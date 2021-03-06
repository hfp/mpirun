#!/bin/bash
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

HERE=$(cd $(dirname $0); pwd -P)

CPUFLAGS=$(sed -n "s/flags\s*:\s\+\(.\+\)/\1/p" /proc/cpuinfo | sort -u)
MICINFO=$(micinfo)

NSOCKETS=$(grep "physical id" /proc/cpuinfo | sort -u | wc -l)
CPUCORES=$(sed -n "0,/cpu cores\s*:\s\+\([0-9]\+\)/s//\1/p" /proc/cpuinfo)
NTHREADS=$(($(echo ${CPUFLAGS} | tr " " "\n" | grep -c ht) * 2))

NDEVICES=$(echo "${MICINFO}" | grep -c "Device No:")
MICCORES=$(echo "${MICINFO}" | sed -n "0,/\s\+Total No of Active Cores :\s\+\([0-9]\+\)/s//\1/p")
MTHREADS=4

if [[ "" != "${NSOCKETS}" ]] ; then
  FLAG_NSOCKETS="-s${NSOCKETS}"
else
  echo "Warning: NSOCKETS unknown!"
fi
if [[ "" != "${CPUCORES}" ]] ; then
  FLAG_CPUCORES="-e${CPUCORES}"
else
  echo "Warning: CPUCORES unknown!"
fi
if [[ "" != "${NTHREADS}" ]] ; then
  FLAG_NTHREADS="-t${NTHREADS}"
else
  echo "Warning: NTHREADS unknown!"
fi
if [[ "" != "${NDEVICES}" ]] ; then
  FLAG_NDEVICES="-d${NDEVICES}"
else
  echo "Warning: NDEVICES unknown!"
fi
if [[ "" != "${MICCORES}" ]] ; then
  FLAG_MICCORES="-m${MICCORES}"
else
  echo "Warning: MICCORES unknown!"
fi
if [[ "" != "${MTHREADS}" ]] ; then
  FLAG_MTHREADS="-u${MTHREADS}"
else
  echo "Warning: MTHREADS unknown!"
fi

echo "NSOCKETS=${NSOCKETS} CPUCORES=${CPUCORES} NTHREADS=${NTHREADS} NDEVICES=${NDEVICES} MICCORES=${MICCORES} MTHREADS=${MTHREADS}"
echo
python ${HERE}/mpirun.py ${FLAG_NSOCKETS} ${FLAG_CPUCORES} ${FLAG_NTHREADS} ${FLAG_NDEVICES} ${FLAG_MICCORES} ${FLAG_MTHREADS} $*
RESULT=$?

exit ${RESULT}

