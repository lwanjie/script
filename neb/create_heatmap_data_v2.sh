#!/bin/bash
# 文件名：extract_data_v2.sh

# 初始化输出文件
echo "# Directory Dipole_Sum Dipole_Component Energy" > combined_results.dat
> dipole_sum.dat
> dipole_component.dat
> energy.dat

# 查找所有disp目录
find . -maxdepth 1 -type d -name "disp_*" | sort -V | while read dir; do
    dirname=${dir#./}
    
    # 检查OUTCAR存在性
    if [ ! -f "$dirname/OUTCAR" ]; then
        echo "警告: $dirname 缺少OUTCAR，跳过..."
        continue
    fi

    # 提取三个数据项（逆向搜索最后出现的结果）
    {
        dipole_sum=$(tac "$dirname/OUTCAR" | awk '/dipole moment/{print $(NF-3)+$(NF-2); exit}')
        dipole_comp=$(tac "$dirname/OUTCAR" | awk '/dipolmoment/{printf "%.6f", $4+1-0.982020; exit}')
        energy=$(tac "$dirname/OUTCAR" | awk '/free  energy   TOTEN/{print $5; exit}')
    } 2>/dev/null  # 忽略可能的错误输出

    # 数据验证
    missing_data=()
    [ -z "$dipole_sum" ] && missing_data+=("Dipole_Sum")
    [ -z "$dipole_comp" ] && missing_data+=("Dipole_Component")
    [ -z "$energy" ] && missing_data+=("Energy")
    
    if [ ${#missing_data[@]} -gt 0 ]; then
        echo "错误: $dirname 缺少 ${missing_data[*]} 数据，跳过..."
        continue
    fi

    # 写入独立文件
    echo "$dipole_sum" >> dipole_sum.dat
    echo "$dipole_comp" >> dipole_component.dat
    echo "$energy" >> energy.dat
    
    # 写入组合文件
    printf "%-12s %12.6f %12.6f %12.6f\n" \
        "$dirname" "$dipole_sum" "$dipole_comp" "$energy" >> combined_results.dat
    
    echo "成功处理: $dirname"
done

echo "数据提取完成！"
echo "生成文件:"
echo "- dipole_sum.dat        (总偶极矩)"
echo "- dipole_component.dat  (分量修正值)"
echo "- energy.dat            (能量)"
echo "- combined_results.dat  (综合数据)"
