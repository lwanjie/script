#!/bin/bash

exec > run.out 2>&1
cd "mobility-x"
for i in 0.985  0.990  0.995  1.000  1.005  1.010  1.015
do
cd $i/scf/
echo -e "426\n3\n" | vaspkit
cd band/
echo -e "911\n" | vaspkit
cd ../../../
done
cd ..
cd "mobility-y"
for i in 0.985  0.990  0.995  1.000  1.005  1.010  1.015
do
cd $i/scf/
echo -e "426\n3\n" | vaspkit
cd band/
echo -e "911\n" | vaspkit
cd ../../../
done

