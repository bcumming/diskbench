#!/bin/bash

base=$1
for i in $(seq 8);
do
    target=$base/run$i;
    "=== creating $target";
    ./create_job.sh --system daint --path $target;
done
