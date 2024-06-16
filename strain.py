import os
import numpy as np


def read_poscar(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        return lines
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return None


def write_poscar(lines, directory, filename='POSCAR'):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        f.writelines(lines)


def apply_strain(lines, strain_a, strain_b):
    # Convert the strain values to float
    strain_a = float(strain_a)
    strain_b = float(strain_b)

    # Modify the lattice vectors based on strain
    a_vector = list(map(float, lines[2].split()))
    b_vector = list(map(float, lines[3].split()))

    # Apply strain
    a_vector[0] *= (1 + strain_a)
    b_vector[0] *= (1 + strain_b)
    b_vector[1] *= (1 + strain_b)

    # Update the lines with new lattice vectors
    lines[2] = "   {:.10f} {:.10f} {:.10f}\n".format(*a_vector)
    lines[3] = "   {:.10f} {:.10f} {:.10f}\n".format(*b_vector)

    return lines


# 获取当前目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))
initial_poscar_path = os.path.join(current_dir, 'POSCAR')

# 读取初始的POSCAR文件
initial_poscar = read_poscar(initial_poscar_path)

if initial_poscar:
    strains = np.arange(-0.02, 0.025, 0.005)  # 应变范围从-0.02到0.02，步长为0.005

    for strain in strains:
        # 对a轴应用应变
        strained_a_poscar = apply_strain(initial_poscar.copy(), strain, 0)
        a_directory = os.path.join(current_dir, 'mobility-x', f'{strain:+.3f}')
        write_poscar(strained_a_poscar, a_directory)

        # 对b轴应用应变
        strained_b_poscar = apply_strain(initial_poscar.copy(), 0, strain)
        b_directory = os.path.join(current_dir, 'mobility-y', f'{strain:+.3f}')
        write_poscar(strained_b_poscar, b_directory)

    print("Strained POSCAR files generated for a-axis and b-axis strains.")
else:
    print("Failed to read the initial POSCAR file.")
