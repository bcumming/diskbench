i/o benchmarks based on icon aquaplanet runs

installation:

```
./install.sh
```

copy all files from directory

```
runscripts/*
```

to

```
icon-exclaim/run
```

in the latter directory the two script are started with sbatch

* `exp.exclaim_ape_R2B07__aquaplanet.run`: 10 nodes
* `exp.exclaim_ape_R2B10__aquaplanet.run`: 16 nodes

the number of nodes can be changed by modifying the two lines

```
#SBATCH --nodes=10

: ${no_of_nodes:=10} ${mpi_procs_pernode:=4}
```

just a differnt number than 10 has to be inserted
