import pyprocar
import numpy as np
import matplotlib.pyplot as plt

def read_fermi_level(outcar_path):
    with open(outcar_path, 'r') as f:
        for line in f:
            if "E-fermi" in line:
                efermi = float(line.split()[2])
                break
    return efermi

# 设置文件路径
outcar_path = 'OUTCAR'
dirname = '.'

# 从 OUTCAR 文件中读取费米能级
efermi = read_fermi_level(outcar_path)
#efermi = pyprocar.get_efermi
# 绘制能带结构
fig, ax = pyprocar.bandsplot(
    code='vasp',          # 使用VASP格式的输出文件
    dirname='.',          # 当前目录
    elimit=[-6, 6],       # 能量范围（相对于费米能级）
    mode='plain',         # 绘图模式
    color='blue',
    fermi_linestyle='--',
    fermi_color='black',
    fermi_linewidth=2,
    fermi=efermi,
    knames=['G','M','K','G'],
    linewidth=[2,2],
    title="Band Structure",
    figure_size=[4,6],
    dpi=1000,
    show=False,
)

Gap=pyprocar.scripts.bandgap(
     dirname ='.',
     code='vasp',
     fermi=efermi,
)

gap_text = f"Eg = {Gap:.2f} eV"
ax.text(0.27, 0.52, gap_text, transform=ax.transAxes, fontsize=14, verticalalignment='bottom')
ax.set_title('Band Structure',fontsize=20)
ax.set_xlabel('',fontsize=20)
ax.set_ylabel('Energy (eV)',fontsize=20)
ax.set_yticks([-6, -3, 0, 3, 6])
ax.set_yticklabels([-6, -3, 0, 3, 6], fontsize=14)
ax.set_xticklabels(['G','M','K','G'], fontsize=14)

plt.savefig("1.png", dpi=1000,bbox_inches='tight')
