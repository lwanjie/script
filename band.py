import matplotlib.pyplot as plt

# 文件路径
file_path = 'BAND.dat'  # 数据文件路径
band_gap_file_path = 'BAND_GAP'  # Band Gap 文件路径
klabels_file_path = 'KLABELS'  # KLABELS 文件路径

# 初始化存储多条线的数据
all_lines = []
x = []
y = []

# 读取 BAND.dat 文件数据
with open(file_path, 'r') as file:
    lines = file.readlines()
    # 从第三行开始处理数据
    for line in lines[2:]:
        line = line.strip()

        # 检查是否是空行
        if line == "":
            # 如果遇到空行且x和y有数据，将数据存储为一条线并重置
            if x and y:
                all_lines.append((x, y))
                x = []
                y = []
            continue

        # 检查是否是以# Band-Index开头的行
        if line.startswith("# Band-Index"):
            # 如果当前有数据未保存，先保存数据
            if x and y:
                all_lines.append((x, y))
                x = []
                y = []
            continue

        # 处理数据行
        try:
            # 分割数据行并转换为浮点数
            x_value, y_value = map(float, line.split())
            x.append(x_value)
            y.append(y_value)
        except ValueError:
            # 如果转换失败，跳过该行
            continue

# 确保最后一组数据也被添加
if x and y:
    all_lines.append((x, y))

# 计算 x 轴的最大值
x_max = max(max(line[0]) for line in all_lines)

# 读取 BAND_GAP 文件并提取 Band Gap 值
band_gap_value = None
with open(band_gap_file_path, 'r') as file:
    for line in file:
        if "Band Gap" in line:
            # 提取 Band Gap 行的最后一个数据
            band_gap_value = float(line.strip().split()[-1])
            break

# 读取 KLABELS 文件并提取刻度标签位置
klabels_positions = []
with open(klabels_file_path, 'r') as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) > 1:
            try:
                klabels_positions.append(float(parts[1]))
            except ValueError:
                continue

# 假设你的刻度标签为 ['G', 'M', 'K', 'G']
klabels_labels = ['G', 'M', 'K', 'G']

# 创建图形并设置大小和分辨率
plt.figure(figsize=(6, 5), dpi=400)

# 绘制所有线条，统一使用蓝色折线
for line in all_lines:
    plt.plot(line[0], line[1], color='blue')

# 设置纵轴范围
plt.ylim(-4, 4)

# 设置横轴范围从0到数据中的最大值
plt.xlim(0, x_max)

# 设置 x 轴刻度位置和标签
if klabels_positions and len(klabels_positions) == len(klabels_labels):
    plt.xticks(ticks=klabels_positions, labels=klabels_labels)

# 在 y=0 处添加虚线
plt.axhline(y=0, color='red', linestyle='--')

# 设置刻度线朝内
plt.tick_params(axis='both', direction='in')

# 绘制纵向网格线（虚线）
plt.grid(which='major', axis='x', linestyle='--')

# 隐藏横向网格线
plt.grid(which='major', axis='y', linestyle='none')

# 设置标题
plt.title(f'Band Gap  = {band_gap_value:.2f} eV')
# 添加上标题
#if band_gap_value is not None:
#    plt.suptitle(f'Band Gap (Eg) = {band_gap_value}', x=0.5, y=1.02, ha='center')

# 保存图像为文件
plt.savefig('output_plot.png', bbox_inches='tight')  # 可以更改为需要的文件名和格式

# 显示图像
plt.show()
