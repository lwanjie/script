#!/bin/bash
grep "VBM (" run.out >> out.dat
grep "CBM (" run.out >> out.dat
grep "Vacuum-Level (" run.out >> out.dat
grep "energy  without entropy" mobility-x/*/scf/OUTCAR >> out.dat
#grep "entropy=" mobility-y/*/scf/OUTCAR >> out.dat
