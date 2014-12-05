#!/bin/bash
###############################################################################
## Copyright (c) 2013-2015, Intel Corporation                                ##
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

HERE=$(cd $(dirname $0); pwd -P)

CPUFLAGS=$(sed -n "s/flags\s*:\s\+\(.\+\)/\1/p" /proc/cpuinfo | sort -u)
MICINFO=$(micinfo)

NSOCKETS=$(grep "physical id" /proc/cpuinfo | sort -u | wc -l)
CPUCORES=$(sed -n "0,/cpu cores\s*:\s\+\(.\+\)/s//\1/p" /proc/cpuinfo)
NTHREADS=$(($(echo $CPUFLAGS | tr " " "\n" | grep -c ht) * 2))

NDEVICES=$(echo "$MICINFO" | grep -c "Device No:")
MICCORES=$(echo "$MICINFO" | sed -n "0,/\s\+Total No of Active Cores :\s\+\(.\+\)/s//\1/p")
MTHREADS=4

echo "NSOCKETS=$NSOCKETS CPUCORES=$CPUCORES NTHREADS=$NTHREADS NDEVICES=$NDEVICES MICCORES=$MICCORES MTHREADS=$MTHREADS"
echo
python $HERE/mpirun.py -s$NSOCKETS -d$NDEVICES -e$CPUCORES -t$NTHREADS -m$MICCORES -u$MTHREADS $*
RESULT=$?

exit $RESULT

