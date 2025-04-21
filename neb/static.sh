#!/bin/bash
# 文件名：create_heatmap_data.sh

# 读取间隔数（根据实际位移参数设置）
intervals_x=12
intervals_y=12

# 初始化二维数组
declare -A energy_matrix dipole_matrix

# 解析combined_results.dat
while read -r dir dipole energy; do
    # 跳过注释行
    [[ "$dir" == *#* ]] && continue
    
    # 从目录名提取坐标索引
    IFS=_ read -ra parts <<< "$dir"
    i=${parts[1]#0}  # 去除前导零
    j=${parts[2]#0}
    
    # 转换为实际坐标
    x=$(awk "BEGIN {print $i/$intervals_x}")
    y=$(awk "BEGIN {print $j/$intervals_y}")
    
    # 存储数据
    energy_matrix["$i,$j"]=$energy
    dipole_matrix["$i,$j"]=$dipole
done < combined_results.dat

# 生成三列格式数据文件
echo "x y Energy Dipole" > heatmap_data.dat
for i in $(seq 0 $intervals_x); do
    for j in $(seq 0 $intervals_y); do
        x=$(awk "BEGIN {printf \"%.2f\", $i/$intervals_x}")
        y=$(awk "BEGIN {printf \"%.2f\", $j/$intervals_y}")
        energy=${energy_matrix["$i,$j"]:-NaN}
        dipole=${dipole_matrix["$i,$j"]:-NaN}
        printf "%-6.2f %-6.2f %-12.6f %-12.6f\n" $x $y $energy $dipole >> heatmap_data.dat
    done
done

# 生成矩阵格式数据
echo "生成矩阵格式文件..."
for param in Energy Dipole; do
    echo "Processing $param..."
    # Y轴标签
    printf "%6s" "" > ${param}_matrix.dat
    for j in $(seq 0 $intervals_y); do
        y=$(awk "BEGIN {printf \"%.2f\", $j/$intervals_y}")
        printf " %10.6f" $y >> ${param}_matrix.dat
    done
    printf "\n" >> ${param}_matrix.dat
    
    # 数据行
    for i in $(seq 0 $intervals_x); do
        x=$(awk "BEGIN {printf \"%.2f\", $i/$intervals_x}")
        printf "%6.2f" $x >> ${param}_matrix.dat
        for j in $(seq 0 $intervals_y); do
            val=$([ "$param" == "Energy" ] && echo ${energy_matrix["$i,$j"]:-NaN} || echo ${dipole_matrix["$i,$j"]:-NaN})
            printf " %10.6f" $val >> ${param}_matrix.dat
        done
        printf "\n" >> ${param}_matrix.dat
    done
done

echo "数据文件已生成："
echo "- heatmap_data.dat (三列格式)"
echo "- Energy_matrix.dat (能量矩阵)"
echo "- Dipole_matrix.dat (偶极矩阵)"
