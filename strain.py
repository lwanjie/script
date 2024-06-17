import os
import shutil
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


def write_optcell(directory, content):
    filepath = os.path.join(directory, 'OPTCELL')
    with open(filepath, 'w') as f:
        f.write(content)


def apply_strain(lines, strain_a, strain_b):
    # Modify the lattice vectors based on strain
    a_vector = list(map(float, lines[2].split()))
    b_vector = list(map(float, lines[3].split()))

    # Apply strain
    a_vector[0] *= strain_a
    b_vector[0] *= strain_b
    b_vector[1] *= strain_b

    # Update the lines with new lattice vectors
    lines[2] = "   {:.10f} {:.10f} {:.10f}\n".format(*a_vector)
    lines[3] = "   {:.10f} {:.10f} {:.10f}\n".format(*b_vector)

    return lines


def copy_and_rename_files(src_files, dest_dir, dest_names):
    os.makedirs(dest_dir, exist_ok=True)
    for src_file, dest_name in zip(src_files, dest_names):
        if os.path.exists(src_file):
            dest_file = os.path.join(dest_dir, dest_name)
            shutil.copy(src_file, dest_file)


# 获取当前目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))
initial_poscar_path = os.path.join(current_dir, 'POSCAR')

# 读取初始的POSCAR文件
initial_poscar = read_poscar(initial_poscar_path)

if initial_poscar:
    strains = np.arange(0.985, 1.0151, 0.005)  # 应变范围从0.985到1.015，步长为0.005

    for strain in strains:
        strain_str = f'{strain:.3f}'

        # 对a轴应用应变
        strained_a_poscar = apply_strain(initial_poscar.copy(), strain, 1.0)
        a_directory = os.path.join(current_dir, 'mobility-x', strain_str)
        write_poscar(strained_a_poscar, a_directory)
        write_optcell(a_directory, '010')

        # 复制文件到mobility-x目录并重命名
        copy_and_rename_files(
            [os.path.join(current_dir, 'INCAR-opt'),
             os.path.join(current_dir, 'KPOINTS'),
             os.path.join(current_dir, 'POTCAR')],
            a_directory,
            ['INCAR', 'KPOINTS', 'POTCAR']
        )

        scf_directory = os.path.join(a_directory, 'scf')
        copy_and_rename_files(
            [os.path.join(current_dir, 'INCAR-scf'),
             os.path.join(current_dir, 'KPOINTS'),
             os.path.join(current_dir, 'POTCAR')],
            scf_directory,
            ['INCAR', 'KPOINTS', 'POTCAR']
        )

        band_directory = os.path.join(scf_directory, 'band')
        copy_and_rename_files(
            [os.path.join(current_dir, 'INCAR-band'),
             os.path.join(current_dir, 'KPOINTS-band'),
             os.path.join(current_dir, 'POTCAR')],
            band_directory,
            ['INCAR', 'KPOINTS', 'POTCAR']
        )

        # 对b轴应用应变
        strained_b_poscar = apply_strain(initial_poscar.copy(), 1.0, strain)
        b_directory = os.path.join(current_dir, 'mobility-y', strain_str)
        write_poscar(strained_b_poscar, b_directory)
        write_optcell(b_directory, '100')

        # 复制文件到mobility-y目录并重命名
        copy_and_rename_files(
            [os.path.join(current_dir, 'INCAR-opt'),
             os.path.join(current_dir, 'KPOINTS'),
             os.path.join(current_dir, 'POTCAR')],
            b_directory,
            ['INCAR', 'KPOINTS', 'POTCAR']
        )

        scf_directory = os.path.join(b_directory, 'scf')
        copy_and_rename_files(
            [os.path.join(current_dir, 'INCAR-scf'),
             os.path.join(current_dir, 'KPOINTS'),
             os.path.join(current_dir, 'POTCAR')],
            scf_directory,
            ['INCAR', 'KPOINTS', 'POTCAR']
        )

        band_directory = os.path.join(scf_directory, 'band')
        copy_and_rename_files(
            [os.path.join(current_dir, 'INCAR-band'),
             os.path.join(current_dir, 'KPOINTS-band'),
             os.path.join(current_dir, 'POTCAR')],
            band_directory,
            ['INCAR', 'KPOINTS', 'POTCAR']
        )

    print(
        "Strained POSCAR and OPTCELL files, along with INCAR, KPOINTS, POTCAR files, generated and organized for a-axis and b-axis strains.")
else:
    print("Failed to read the initial POSCAR file.")
