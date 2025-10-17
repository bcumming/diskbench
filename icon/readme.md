## status of work

The benchmark has been built and tested.

**note**: both benchmarks generated the same amount of output, and I suspect that the R2B10 script is actually runnin R2B07, but I am not expert enough to tell.

We need to find a way to increase the duration, and possibly increase output frequency, to generate large regular amounts of data.

## building ICON

The process is to build ICON in `/dev/shm`, so that it can be built as quickly as possible.

The `bin/icon` executable that is generated is "self-contained", in the sense that no dynamic libraries or other runtime artifacts are generated.

So we then copy the executable, and other files from the repositry into a a `$runpath` location that can be kept while the build path is thrown away.

```
# the location of the icon path where diskbench was cloned
export diskbench=/users/bcumming/software/diskbench/icon
# where the build will be performed
export buildpath=/dev/shm/bcumming/icon
# where we will install icon
export runpath=/capstor/scratch/cscs/bcumming/icon

mkdir -p $buildpath
cd $buildpath
export icon_path=$(realpath $buildpath/icon-exclaim)

# TODO: which branch/tag/commit to use? this is just using the main/master branch
git clone --recursive git@github.com:C2SM/icon-exclaim.git $icon_path

# build ICON inside the uenv
cd $icon_path
uenv run icon/25.2:v3 --view=default -- ./config/cscs/santis.gpu.nvhpc

# install ICON
mkdir -p $runpath
cd $runpath
cp -R $icon_path/bin $runpath
cp -R $icon_path/run $runpath
cp -R $icon_path/data $runpath
cp -R $icon_path/externals $runpath
cp -v $diskbench/runscripts/*  $runpath/run
sed -i "s|@@ICONPATH@@|$runpath|g" $runpath/run/job.r2b07.sh
sed -i "s|@@ICONPATH@@|$runpath|g" $runpath/run/job.r2b10.sh
chmod +x $runpath/run/job.*.sh
```

## running ICON

Move to the `runpath/run` directory, and launch the job script:

```
cd $runpath/run
sbatch ./job.r2b07.sh
```

This will generate log output in `$runpath/log`.

Results are stored in `$runpath/experiments`.

There were about 12G generated for the r2b7 model.

## testing different filesystems

The simulation outputs are stored in the `experiments` sub-direcotry of `$runpath`.
To test a different filesystem, copy the `bin`, `run`, `data`, `externals` paths on the new file system, regenerate the `job.r2bXX.sh` scripts to set ICONPATH to the new location.

To test the effect of lustre striping, create the `$runpath/experiments` path beforehand and set the striping with `lfs setstripe`.
