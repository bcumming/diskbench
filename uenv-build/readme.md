run this once after cloning this rep
```
./setup.sh
```

Here we set up the experiment on ritom, capstor, iopstor and /dev/shm
```
time ./create_job.sh --system daint --path /ritom/scratch/cscs/$USER/disktest/job-64
time ./create_job.sh --system daint --path /capstor/scratch/cscs/$USER/disktest/job-64
time ./create_job.sh --system daint --path /iopsstor/scratch/cscs/$USER/disktest/job-64
time ./create_job.sh --system daint --path /dev/shm/$USER/disktest/job-64
```

The time for setup

```
-------------------
filesystem  time(s)
-------------------
ritom           188
capstor          99
iopsstor        104
memory           12
```

use the following to time the runs
```
time env --ignore-environment PATH=/usr/bin:/bin:`pwd`/spack/bin HOME=$HOME make store.squashfs -j64
```

build results in seconds.
real is the wall time: what the user ultimately experiences

```
        memory      capstor     ritom
real    1652        3689         7640
user   13675       14076        13711
sys     2688        4387         1466
```
