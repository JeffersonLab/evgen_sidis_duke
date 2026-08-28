#!/bin/bash

module use /group/halla/modulefiles
module load root/6.40.02

export LHAPDFSYS=/group/solid/apps/evgen/LHAPDF/LHAPDF-6.5.6
export PATH=${PATH}:${LHAPDFSYS}/bin
export LD_LIBRARY_PATH=${LHAPDFSYS}/lib:${LD_LIBRARY_PATH}
export LHAPATH=${LHAPDFSYS}/share/LHAPDF

# lhapdf-config --pydir is broken (returns empty), so point PYTHONPATH at the
# LHAPDF python bindings directly; needed by tmdlib/tmd.py's `import lhapdf`
export PYTHONPATH=${LHAPDFSYS}/lib64/python3.9/site-packages:${PYTHONPATH}
