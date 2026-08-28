#!/bin/csh

module use /group/halla/modulefiles
module load root/6.40.02

setenv LHAPDFSYS /group/solid/apps/evgen/LHAPDF/LHAPDF-6.5.6
setenv PATH ${PATH}:${LHAPDFSYS}/bin
setenv LD_LIBRARY_PATH $LHAPDFSYS/lib:$LD_LIBRARY_PATH
setenv LHAPATH $LHAPDFSYS/share/LHAPDF

# lhapdf-config --pydir is broken (returns empty), so point PYTHONPATH at the
# LHAPDF python bindings directly; needed by tmdlib/tmd.py's `import lhapdf`
if ($?PYTHONPATH) then
  setenv PYTHONPATH ${LHAPDFSYS}/lib64/python3.9/site-packages:$PYTHONPATH
else
  setenv PYTHONPATH ${LHAPDFSYS}/lib64/python3.9/site-packages
endif


