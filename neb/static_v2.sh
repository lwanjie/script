#!/bin/bash
# 文件名：create_heatmap_data_v2.sh

# 设置网格参数（根据实际情况修改）
intervals_x=12
intervals_y=12

# 初始化所有数据矩阵
declare -A sum_matrix comp_matrix energy_matrix

# 解析组合数据文件
while read -r dir dsum dcomp energy; do
    [[ "$dir" == *#* ]] && continue  # 跳过注释行
    
    # 提取坐标索引
    IFS=_ read -ra parts <<< "$dir"
    i=${parts[1]#0}
    j=${parts[2]#0}
    
    # 存储数据
    sum_matrix["$i,$j"]=$dsum
    comp_matrix["$i,$j"]=$dcomp
    energy_matrix["$i,$j"]=$energy
done < combined_results.dat

# 生成三列格式数据
echo "x y Dipole_Sum Dipole_Component Energy" > heatmap_data.dat
for i in $(seq 0 $intervals_x); do
    for j in $(seq 0 $intervals_y); do
        x=$(awk "BEGIN {printf \"%.2f\", $i/$intervals_x}")
        y=$(awk "BEGIN {printf \"%.2f\", $j/$intervals_y}")
        dsum=${sum_matrix["$i,$j"]:-NaN}
        dcomp=${comp_matrix["$i,$j"]:-NaN}
        energy=${energy_matrix["$i,$j"]:-NaN}
        printf "%-6.2f %-6.2f %-12.6f %-12.6f %-12.6f\n" \
            $x $y $dsum $dcomp $energy >> heatmap_data.dat
    done
done

# 生成矩阵格式文件
generate_matrix() {
    local param=$1
    echo "生成 ${param}_matrix.dat..."
    
    # Y轴标签
    printf "%6s" "" > ${param}_matrix.dat
    for j in $(seq 0 $intervals_y); do
        y_val=$(awk "BEGIN {printf \"%.2f\", $j/$intervals_y}")
        printf " %10.6f" $y_val >> ${param}_matrix.dat
    done
    printf "\n" >> ${param}_matrix.dat
    
    # 数据行
    for i in $(seq 0 $intervals_x); do
        x_val=$(awk "BEGIN {printf \"%.2f\", $i/$intervals_x}")
        printf "%6.2f" $x_val >> ${param}_matrix.dat
        for j in $(seq 0 $intervals_y); do
            case $param in
                "Dipole_Sum") val=${sum_matrix["$i,$j"]:-NaN} ;;
                "Dipole_Component") val=${comp_matrix["$i,$j"]:-NaN} ;;
                "Energy") val=${energy_matrix["$i,$j"]:-NaN} ;;
            esac
            printf " %10.6f" $val >> ${param}_matrix.dat
        done
        printf "\n" >> ${param}_matrix.dat
    done
}

generate_matrix "Dipole_Sum"
generate_matrix "Dipole_Component"
generate_matrix "Energy"

echo "热图数据已生成："
ls -lh *matrix.dat heatmap_data.dat
