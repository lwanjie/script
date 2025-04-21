#!/bin/bash

# 初始化输出文件（覆盖旧数据）
echo "# Directory Dipole_Sum Energy" > combined_results.dat
> dipole_c.dat
> energy.dat

# 查找所有disp目录并按自然排序处理
find . -maxdepth 1 -type d -name "disp_*" | sort -V | while read dir; do
    dirname=${dir#./}
    
    # 检查OUTCAR是否存在
    if [ ! -f "$dirname/OUTCAR" ]; then
        echo "警告: $dirname 中没有OUTCAR文件，跳过..."
        continue
    fi

    # 提取偶极矩数据（取最后一个匹配项）
    dipole=$(tac "$dirname/OUTCAR" | awk '/dipole moment/{print $(NF-3)+$(NF-2); exit}')
    
    # 提取能量数据（取最后一个匹配项）
    energy=$(tac "$dirname/OUTCAR" | awk '/free  energy   TOTEN/{print $5; exit}')
    
    # 验证数据完整性
    if [ -z "$dipole" ] || [ -z "$energy" ]; then
        echo "错误: $dirname 中的数据不完整，跳过..."
        continue
    fi

    # 写入单独文件
    echo "$dipole" >> dipole_c.dat
    echo "$energy" >> energy.dat
    
    # 写入组合文件（带目录信息）
    printf "%-12s %12.6f %12.6f\n" "$dirname" "$dipole" "$energy" >> combined_results.dat
    
    echo "成功处理: $dirname"
done

echo "数据提取完成！"
echo "结果文件:"
echo "- dipole_c.dat (仅偶极矩和)"
echo "- energy.dat (仅能量)"
echo "- combined_results.dat (组合数据)"
