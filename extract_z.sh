#!/bin/bash
# 用法示例: ./extract_z.sh O [XDATCAR]  > extract_z.dat
# 若不指定文件名，默认处理当前目录下的 XDATCAR 文件

if [ "$#" -lt 1 ]; then
    echo "用法: $0 元素符号 [文件名]"
    exit 1
fi

ELEMENT=$1
FILE=${2:-XDATCAR}

awk -v element="$ELEMENT" '
BEGIN {
    frame = 0; 
    inblock = 0;
}
# 第6行：一般为元素符号列表（VASP5及以上版本）
NR==6 {
    n = split($0, elems);
}
# 第7行：各元素的原子数
NR==7 {
    split($0, counts);
    total = 0;
    for(i = 1; i <= n; i++){
       counts[i] = counts[i] + 0;  # 转换为数值
       total += counts[i];
       if(elems[i] == element) {
           target_start = total - counts[i] + 1;
           target_end = total;
       }
    }
    next;
}
# 每一帧的起始标志（通常为 "Direct configuration="）
/^Direct configuration=/ {
    frame++;
    inblock = 1;
    lineInBlock = 0;
    output = frame;  # 初始化输出内容，第一列为帧编号
    next;
}
# 处理一帧内的坐标数据
inblock {
    lineInBlock++;
    # 如果当前行号在目标元素的范围内，则提取第三列（z坐标）
    if(lineInBlock >= target_start && lineInBlock <= target_end) {
        output = output "," $3;
    }
    # 当读完一帧所有原子后输出该帧数据
    if(lineInBlock == total) {
       print output;
       inblock = 0;
    }
}
' "$FILE"

