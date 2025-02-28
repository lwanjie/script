#!/bin/bash
# 用法示例：
#   提取所有O原子的z坐标: ./extract_z.sh O [XDATCAR]
#   仅提取第2和第4个O原子的z坐标: ./extract_z.sh O [XDATCAR] "2,4"
#
# 参数说明：
#   第一个参数：元素符号（如 O）
#   第二个参数（可选）：VASP 输出文件（默认 XDATCAR）
#   第三个参数（可选）：以逗号分隔的索引列表（基于该元素在头文件中的顺序），如 "2,4"

if [ "$#" -lt 1 ]; then
    echo "用法: $0 元素符号 [文件名] [索引, 用逗号分隔]"
    exit 1
fi

ELEMENT=$1
FILE=${2:-XDATCAR}
INDEX_STR=${3:-""}

awk -v element="$ELEMENT" -v indices_str="$INDEX_STR" '
BEGIN {
    frame = 0; 
    inblock = 0;
    # 如果用户提供了索引字符串，则解析并存入 desired 数组
    if (indices_str != "") {
       n_indices = split(indices_str, temp_arr, ",");
       for (i = 1; i <= n_indices; i++) {
          desired[temp_arr[i]] = 1;
       }
    }
}
# 第6行：元素符号列表（VASP5及以上版本标准）
NR==6 {
    n = split($0, elems);
}
# 第7行：各元素的原子数
NR==7 {
    split($0, counts);
    total = 0;
    for (i = 1; i <= n; i++){
       counts[i] = counts[i] + 0;  # 转换为数值
       total += counts[i];
       if(elems[i] == element) {
           target_start = total - counts[i] + 1;
           target_end = total;
       }
    }
    next;
}
# 每一帧起始，通常以 "Direct configuration=" 开头
/^Direct configuration=/ {
    frame++;
    inblock = 1;
    lineInBlock = 0;
    output = frame;  # 初始化输出，第一列为帧编号
    next;
}
# 处理每一帧的坐标数据
inblock {
    lineInBlock++;
    # 如果当前行属于目标元素的范围，则提取第三列（z坐标）
    if (lineInBlock >= target_start && lineInBlock <= target_end) {
        local_index = lineInBlock - target_start + 1;
        # 当未指定索引或当前索引在用户指定的数组中时，输出该值
        if (indices_str == "" || (local_index in desired)) {
            output = output "," $3;
        }
    }
    # 当读取完本帧所有原子后输出结果
    if (lineInBlock == total) {
       print output;
       inblock = 0;
    }
}
' "$FILE"
