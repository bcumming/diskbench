#!/bin/bash

# the git clone refers to
# commit b498bad59ae17b0c0778e7914434ee1a4f2488f7
git clone --recursive https://github.com/C2SM/icon-exclaim.git
uenv start icon/25.2:v3 --view=default
cd icon-exclaim
./config/cscs/santis.gpu.nvhpc
./make_runscripts
