#!/bin/bash

# 预复制公共文件（仅需执行一次）
common_files=(pbs.sh POTCAR INCAR KPOINTS)

# 找到所有目标目录
dirs=($(find . -maxdepth 1 -type d -name "disp_*" | sort -V))

# 并行复制文件
printf "%s\0" "${dirs[@]}" | xargs -0 -P 8 -I {} cp "${common_files[@]}" {}

# 顺序提交作业
for dir in "${dirs[@]}"; do
    (cd "$dir" && qsub pbs.sh)
done
