#!/bin/bash

set -e

basepath=$1
jobrun=$((SLURM_PROCID+1))

jobpath=$basepath/run$jobrun

cd $jobpath
logfile=$jobpath/log

echo "==== running $jobrun in $jobpath"

/usr/bin/time -f $'real\t%Em\nuser\t%Um\nsys\t%Sm' \
    env --ignore-environment \
    PATH=/usr/bin:/bin:`pwd`/spack/bin \
    HOME=$HOME \
    make store.squashfs -j64 \
    >$logfile 2>&1
