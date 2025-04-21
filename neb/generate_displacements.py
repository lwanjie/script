import os
import argparse

def read_poscar(poscar_path):
    with open(poscar_path, 'r') as f:
        lines = f.readlines()
    
    title = lines[0].strip()
    scale = float(lines[1])
    a = list(map(float, lines[2].split()))
    b = list(map(float, lines[3].split()))
    c = list(map(float, lines[4].split()))
    species = lines[5].split()
    nums = list(map(int, lines[6].split()))
    total_atoms = sum(nums)
    coord_type = lines[7].strip().lower()[0]
    
    coords = []
    for line in lines[8:8+total_atoms]:
        parts = line.split()
        coords.append([float(parts[0]), float(parts[1]), float(parts[2])])
    
    return {
        'title': title,
        'scale': scale,
        'lattice': [a, b, c],
        'species': species,
        'nums': nums,
        'coord_type': coord_type,
        'coords': coords
    }

def write_poscar(data, new_coords, folder, coord_type):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, 'POSCAR'), 'w') as f:
        f.write(data['title'] + '\n')
        f.write(f"{data['scale']}\n")
        for vec in data['lattice']:
            f.write(' '.join(map(str, vec)) + '\n')
        f.write(' '.join(data['species']) + '\n')
        f.write(' '.join(map(str, data['nums'])) + '\n')
        f.write('Direct\n' if coord_type == 'd' else 'Cartesian\n')
        for coord in new_coords:
            f.write(' '.join(f"{x:.10f}" for x in coord) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Generate displacement POSCARs.")
    parser.add_argument('--atoms', nargs='+', type=int, required=True,
                        help='1-based indices of atoms to displace')
    parser.add_argument('--grid', nargs=2, type=int, default=[12, 12],
                        help='Number of intervals in x and y directions (default: 12 12)')
    args = parser.parse_args()
    
    poscar_data = read_poscar('POSCAR')
    coord_type = poscar_data['coord_type']
    coords = poscar_data['coords']
    selected_atoms = [i-1 for i in args.atoms]
    
    max_index = len(coords) - 1
    for idx in selected_atoms:
        if idx < 0 or idx > max_index:
            raise ValueError(f"原子索引 {idx+1} 超出范围（总原子数：{max_index+1}）")
    
    intervals_x, intervals_y = args.grid
    grid_x = intervals_x
    grid_y = intervals_y
    width_x = len(str(intervals_x))  # 最大索引=间隔数
    width_y = len(str(intervals_y))

    scale = poscar_data['scale']
    a = [scale * x for x in poscar_data['lattice'][0]]
    b = [scale * x for x in poscar_data['lattice'][1]]

    # 修改循环范围为 0 到间隔数（包含）
    for i in range(intervals_x + 1):
        for j in range(intervals_y + 1):
            dx = i / intervals_x
            dy = j / intervals_y
            
            if coord_type == 'd':
                displacement = [dx, dy, 0.0]
            else:
                displacement = [
                    dx * a[0] + dy * b[0],
                    dx * a[1] + dy * b[1],
                    dx * a[2] + dy * b[2]
                ]
            
            new_coords = []
            for idx, coord in enumerate(coords):
                if idx in selected_atoms:
                    new_coord = [c + disp for c, disp in zip(coord, displacement)]
                    new_coords.append(new_coord)
                else:
                    new_coords.append(coord.copy())
            
            folder = f"disp_{i:0{width_x}d}_{j:0{width_y}d}"
            write_poscar(poscar_data, new_coords, folder, coord_type)

if __name__ == "__main__":
    main()
