#!/bin/bash
source /opt/pflotran-ptscotch/pflotran_config
rm *.vtk
rm *.h5
$PETSC_DIR/$PETSC_ARCH/bin/mpirun -np $1 pflotran -pflotranin ./input.in
myarray=(`find ./ -maxdepth 1 -name "*.vtk"`)
if [ ${#myarray[@]} -gt 0 ]; then
  rm -r ./output-vtk
  mkdir output-vtk
  mv *.vtk ./output-vtk
fi
myarray=(`find ./ -maxdepth 1 -name "*.h5"`)
if [ ${#myarray[@]} -gt 0 ]; then
  rm -r ./output-hdf5
  mkdir output-hdf5
  mv *.h5 ./output-hdf5
fi
myarray=(`find ./ -maxdepth 1 -name "*.xmf"`)
if [ ${#myarray[@]} -gt 0 ]; then
  mv *.xmf ./output-hdf5
fi
python3 postprocessing_script.py
