# uenv squashfs performance

What is the overhead of multiple processes on different nodes reading from a uenv squashfs image?

Feedback from HPE is that slow start times for large MPI jobs could be caused by many ranks trying to read shared libaries and causing disk contention.

## requirements

The benchmark requires [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

## generate

The `generate.py` script generates the job scripts required to run an experiment.

It takes as its inputs the uenv to use, the number of nodes/ranks-per-node

* `-n/--nodes`: number of nodes to run on
* `-r/--ranks-per-node`: number of ranks per node
* `-u/--uenv`: the name of the uenv to use (e.g. recommended `-uprgenv-gnu/24.11:v2`)
* `-j/--jobname`: the name of the job: this will be the name of the job script, and also used for the output file
* `-d/--dir`: the directory to store the generated job and artifacts in 
* `-p/--partition`: the partition to run on (optional)

Generate a single benchmark that tests one rank on one node:
```console
$ ./generate.py -uprgenv-gnu/24.11:v2 --nodes=1 --ranks-per-node=1 -jjob -pdebug -dtest
# note that fd and hyperfine are installed by generate.py
$ fd ./test
test/fd
test/hyperfine
test/job
test/job.script
$ sbatch ./test/job
# ... wait for it to complete
$ cat ./test/job.out
```

Generate and submit 
```

## submit

```
sbatch job_64x4
```

## evaluate

```
cat job_64x4.out
```
