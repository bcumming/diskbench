benchmark the time it takes to build a reasonable complicated software stack using Spack.

We use a make server with 64 processes, which can build multiple packages in parallel.

## running the tests

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

## results

The time for setup:

```
-------------------
filesystem  time(s)
-------------------
ritom           188
capstor          99
iopsstor        104
memory           12
```

The time taken to `rm -rf store` the directory with all the built software
```
-------------------
filesystem  time(s)
-------------------
ritom           119
capstor          20
```


use the following to time the runs
```
time env --ignore-environment PATH=/usr/bin:/bin:`pwd`/spack/bin HOME=$HOME make store.squashfs -j64
```

Timings for the three file systems building the environment:

total wall time

```
                mem  capstor    ritom
----------  -------  -------  -------
real           1652     5235     7640
user          13675    14032    13711
sys            2688     4460     1466
```

package times for compiler env

```
package               mem  capstor    ritom
----------------  -------  -------  -------
gcc                 794.4   2930.3   4896.5
gettext             192.1    508.4    427.9
perl                 67.6    181.9    169.7
ncurses              52.8    178.6    115.9
texinfo              28.3    137.5     86.4
libxml2               7.5    130.7     56.2
m4                   32.7    108.7     87.8
findutils            30.8     97.7     87.5
diffutils            39.5     90.2     78.2
tar                  25.1     86.9     72.6
berkeley-db          15.7     86.7     60.6
autoconf-archive      1.6     75.6     10.6
zstd                 51.8     68.0     55.8
libiconv             21.5     52.9     41.0
gmp                  17.3     47.3     49.6
gawk                 13.6     49.3     36.0
xz                    9.8     38.7     24.6
mpfr                 14.5     32.8     30.7
automake              1.4     27.6      9.3
gmake                 8.5     19.1     18.2
gdbm                  7.2     18.8     15.1
libtool               7.0     17.7     13.9
readline              5.4     17.4     13.7
pkgconf               3.3     16.2      8.7
libsigsegv            7.0     14.6     12.6
mpc                   3.4     11.6     11.4
autoconf              1.7     10.9      3.4
zlib-ng               2.4      8.1      7.8
bzip2                 1.7      4.0      2.5
pigz                  1.4      1.7      1.8
gnuconfig             1.0      1.2      1.1
compiler-wrapper      0.2      0.3      0.4
gcc-runtime           0.1      0.2      0.4
```

package times for main env

```
package                      mem  capstor    ritom
-----------------------  -------  -------  -------
gettext                    194.3    416.7    473.0
cmake                       62.9    184.7    305.3
perl                        67.3    149.0    171.5
python                      37.5    102.4    141.7
ncurses                     36.4    127.0    122.3
openssl                     16.7     51.8     83.1
diffutils                   30.2     81.2     80.5
hdf5                        23.4     49.2     77.4
berkeley-db                 12.8     76.0     64.4
tar                         25.4     69.2     74.6
zstd                        54.2     65.8     63.7
util-linux-uuid             13.6     62.3     55.4
curl                        17.1     44.9     61.8
libxml2                      7.7     61.5     57.7
libiconv                    20.0     56.9     46.2
sqlite                      44.1     50.3     49.6
xz                           9.2     27.4     26.3
nghttp2                      9.6     25.0     26.0
libbsd                       6.3     24.2     20.7
gmake                        8.7     17.4     19.9
expat                        8.3     17.4     16.7
readline                     4.8     17.3     15.0
libffi                       4.5     14.4     15.5
gdbm                         4.9     13.2     14.7
libmd                        3.3     11.7     11.3
pkgconf                      3.2      9.4      9.0
zlib-ng                      2.4      7.4      8.5
libaec                       1.2      3.2      6.2
squashfs                     1.8      3.3      2.5
bzip2                        1.6      2.8      2.5
pigz                         1.4      2.1      1.9
ca-certificates-mozilla      0.1      0.3      0.4
gcc-runtime                  0.1      0.2      0.4
```

Some queries on the nodes

```
$ mount | grep ritom
172.28.55.1:/scratch on /ritom/scratch type nfs (rw,nosuid,relatime,vers=3,rsize=1048576,wsize=1048576,namlen=255,hard,forcerdirplus,proto=tcp,nconnect=64,timeo=600,retrans=2,sec=sys,mountaddr=172.28.55.1,mountvers=3,mountport=20048,mountproto=udp,local_lock=none,localports=172.28.16.44-172.28.16.47,localports_failover,remoteports=172.28.55.1-172.28.55.96,addr=172.28.55.8)
```

```
$ stat -f /ritom/scratch
  File: "/ritom/scratch"
    ID: 0        Namelen: 255     Type: nfs
Block size: 1048576    Fundamental block size: 1048576
Blocks: Total: 9723683840 Free: 9587221309 Available: 9587221309
Inodes: Total: 87003340800 Free: 86997535922
```

The following don't show anything
```
$ lsmod | grep vast
$ ps aux | grep vast
```
```
