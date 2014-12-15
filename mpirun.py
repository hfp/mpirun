#! /usr/bin/env python
###############################################################################
## Copyright (c) 2014-2015, Intel Corporation                                ##
## All rights reserved.                                                      ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions        ##
## are met:                                                                  ##
## 1. Redistributions of source code must retain the above copyright         ##
##    notice, this list of conditions and the following disclaimer.          ##
## 2. Redistributions in binary form must reproduce the above copyright      ##
##    notice, this list of conditions and the following disclaimer in the    ##
##    documentation and/or other materials provided with the distribution.   ##
## 3. Neither the name of the copyright holder nor the names of its          ##
##    contributors may be used to endorse or promote products derived        ##
##    from this software without specific prior written permission.          ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS       ##
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT         ##
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR     ##
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT      ##
## HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,    ##
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED  ##
## TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR    ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ##
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
###############################################################################
## Hans Pabst, Christopher Dahnken, Intel Corporation                        ##
###############################################################################
import platform
import argparse
import sys
import os


def micshift(i, rcores, ncores, nthreads):
    return str(max(ncores + min(0, rcores), nthreads)) + "c," + str(nthreads) + "t," + str(i * ncores) + "o"


nodename = platform.node().split(".")[0]
micenv = "MIC"

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--nodelist", help="list of comma separated node names", default=["localhost", nodename]["" != nodename])
parser.add_argument("-p", "--cpuprocs", help="number of processes per socket (host)", type=int, default=1)
parser.add_argument("-q", "--micprocs", help="number of processes per mic (native)", type=int, default=1)
parser.add_argument("-s", "--nsockets", help="number of sockets per node", type=int, default=1)
parser.add_argument("-d", "--ndevices", help="number of devices per node", type=int, default=0)
parser.add_argument("-e", "--cpucores", help="number of CPU cores per socket", type=int, default=1)
parser.add_argument("-t", "--nthreads", help="number of CPU threads per core", type=int, default=2)
parser.add_argument("-m", "--miccores", help="number of MIC cores per device", type=int, default=57)
parser.add_argument("-r", "--reserved", help="number of MIC cores reserved", type=int, default=sys.maxint)
parser.add_argument("-u", "--mthreads", help="number of MIC threads per core", type=int, default=4)
parser.add_argument("-a", "--cpuaffinity", help="affinity (CPU) e.g., compact", default="compact")
parser.add_argument("-b", "--micaffinity", help="affinity (MIC) e.g., balanced", default="balanced")
parser.add_argument("-c", "--schedule", help="schedule, e.g. dynamic", default="static")
parser.add_argument("-w", "--wrapper", help="wrapper")
parser.add_argument("-g", "--debugger", help="debugger")
parser.add_argument("-i", "--inputfile", help="inputfile (<)")
parser.add_argument("-0", "--hr0", help="executable (rank-0)")
parser.add_argument("-x", "--hri", help="executable (host)")
parser.add_argument("-y", "--mri", help="executable (mic)")
parser.add_argument("-z", "--micpre", help="prefixed mic name", action="store_true")
parser.add_argument("-v", "--dryrun", help="dryrun", action="store_true")
args, unknown = parser.parse_known_args()

if (None != args.inputfile):
    arguments = " ".join(unknown) + " < " + args.inputfile
else:
    arguments = " ".join(unknown)
if ("" != arguments): arguments = " " + arguments

if (None != args.wrapper):
    wrapper = args.wrapper + [" ", " " + str(args.debugger) + " -ex run --args"][None != args.debugger]
else:
    wrapper = ["", str(args.debugger) + " -ex run --args"][None != args.debugger]
if ("" != wrapper): wrapper = wrapper + " "

if (1 < args.nsockets): args.cpuaffinity = args.cpuaffinity + ",1"
if (1 < args.nthreads): args.cpuaffinity = args.cpuaffinity + ",granularity=fine"

if (None == args.mri):
    if (sys.maxint == args.reserved): args.reserved = 1
    cpusockets = min(args.nsockets, args.ndevices)
    nparts = args.cpuprocs
else:
    if (sys.maxint == args.reserved): args.reserved = 0
    cpusockets = args.nsockets
    nparts = args.micprocs

cputhreads = cpusockets * args.cpucores * args.nthreads
mcores = int(0 < nparts) * max((args.miccores - max(args.reserved, 0)), nparts) / max(nparts, 1)
pthreads = int(0 < (args.cpuprocs * cpusockets)) * cputhreads / max(args.cpuprocs * cpusockets, 1)
remainder = cputhreads - pthreads * args.cpuprocs * cpusockets


runstring = "mpirun -bootstrap ssh"
if (None == args.mri): runstring = runstring \
                    + " -genv I_MPI_PIN_DOMAIN=auto" \
                    + " -genv OFFLOAD_INIT=on_start" \
                    + " -genv MIC_USE_2MB_BUFFERS=2m" \
                    + " -genv MIC_ENV_PREFIX=" + micenv \
                    + " -genv " + micenv + "_KMP_AFFINITY=" + args.micaffinity \
                    + " -genv " + micenv + "_OMP_SCHEDULE=" + args.schedule \
                    + " -genv " + micenv + "_OMP_NUM_THREADS=" + str(max((mcores + min(0, args.reserved)) * 4, args.mthreads))
else: runstring = runstring \
                    + " -genv I_MPI_MIC=1"
if (None != args.hr0): runstring = runstring \
                    + " -host " + args.nodelist.split(",")[0] + " -np 1" \
                    + " -env I_MPI_PIN_DOMAIN=auto" \
                    + " -env KMP_AFFINITY=" + args.cpuaffinity \
                    + " -env OMP_NUM_THREADS=" + str(args.nthreads) \
                    + " " + wrapper + args.hr0 + arguments \
                    + " :"
for n in args.nodelist.split(","):
    for s in range(0, cpusockets):
        for p in range(0, args.cpuprocs):
            runstring = runstring \
                    + " -host " + n + " -np 1" \
                    + " -env KMP_AFFINITY=" + args.cpuaffinity \
                    + " -env OMP_SCHEDULE=" + args.schedule \
                    + " -env OMP_NUM_THREADS=" + str(pthreads - [0, args.nthreads][None != args.hr0 and 0 == s and 0 == p])
            if (None == args.mri): runstring = runstring \
                    + " -env OFFLOAD_DEVICES=" + str(s) \
                    + " -env " + micenv + "_KMP_PLACE_THREADS=" + micshift(p, args.reserved, mcores, args.mthreads) \
                    + " -env " + micenv + "_OMP_SCHEDULE=" + args.schedule
            else: runstring = runstring \
                    + " -env I_MPI_PIN_DOMAIN=auto"
            runstring = runstring \
                    + " " + wrapper + args.hri + arguments \
                    + " :"
    if (None != args.mri):
        for d in range(0, args.ndevices):
            for m in range(0, args.micprocs):
                runstring = runstring \
                    + " -host " + ["", n + "-"][int(args.micpre)] + "mic" + str(d) + " -np 1" \
                    + " -env LD_LIBRARY_PATH=$MIC_LD_LIBRARY_PATH" \
                    + " -env I_MPI_PIN=off" \
                    + " -env KMP_PLACE_THREADS=" + micshift(m, args.reserved, mcores, args.mthreads) \
                    + " -env KMP_AFFINITY=" + args.micaffinity \
                    + " -env OMP_SCHEDULE=" + args.schedule \
                    + " -env OMP_NUM_THREADS=" + str(max(mcores + min(0, args.reserved), args.mthreads) * 4) \
                    + " " + args.mri + arguments \
                    + " :"
        if (0 < remainder and 0 < cputhreads and 0 < args.cpuprocs): runstring = runstring \
                    + " -host " + n + " -np 1" \
                    + " -env I_MPI_PIN_DOMAIN=auto" \
                    + " -env KMP_AFFINITY=" + args.cpuaffinity \
                    + " -env OMP_SCHEDULE=" + args.schedule \
                    + " -env OMP_NUM_THREADS=" + str(remainder) \
                    + " " + wrapper + args.hri + arguments \
                    + " :"

runstring = runstring[0:len(runstring)-2]
print runstring
print

result = 0
if (False == args.dryrun):
    result = os.system(runstring)

sys.exit([0, 1][0 != result])

