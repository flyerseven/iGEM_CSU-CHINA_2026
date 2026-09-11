import json, re, sys

src = sys.argv[1] if len(sys.argv) > 1 else 'brain-mesh.js'
out = sys.argv[2] if len(sys.argv) > 2 else 'brain-mesh.js'
cell = float(sys.argv[3]) if len(sys.argv) > 3 else 0.06

if src.lower().endswith('.obj'):
    verts, tris = [], []
    for line in open(src, encoding='utf-8', errors='ignore'):
        if line.startswith('v '):
            verts.append([float(v) for v in line[2:].split()[:3]])
        elif line.startswith('f '):
            idx = [int(t.split('/')[0]) - 1 for t in line[2:].split()]
            for i in range(1, len(idx) - 1):
                tris.append([idx[0], idx[i], idx[i + 1]])
    mn = [min(v[i] for v in verts) for i in range(3)]
    mx = [max(v[i] for v in verts) for i in range(3)]
    c = [(mn[i] + mx[i]) / 2 for i in range(3)]
    sc = max(mx[i] - mn[i] for i in range(3)) / 2
    verts = [[(v[0]-c[0])/sc, -(v[1]-c[1])/sc, (v[2]-c[2])/sc] for v in verts]
else:
    text = open(src, encoding='utf-8').read()
    data = json.loads(re.search(r'=\s*(\{.*\})\s*;?\s*$', text, re.S).group(1))
    verts, tris = data['verts'], data['tris']

acc, cell_idx, remap = {}, {}, []
for x, y, z in verts:
    key = (int(x // cell), int(y // cell), int(z // cell))
    if key not in acc:
        acc[key] = [0.0, 0.0, 0.0, 0]
        cell_idx[key] = len(cell_idx)
    a = acc[key]
    a[0] += x; a[1] += y; a[2] += z; a[3] += 1
    remap.append(cell_idx[key])

new_verts = [None] * len(acc)
for key, idx in cell_idx.items():
    a = acc[key]
    new_verts[idx] = [round(a[0]/a[3], 4), round(a[1]/a[3], 4), round(a[2]/a[3], 4)]

seen, new_tris = set(), []
for t in tris:
    a, b, c = remap[t[0]], remap[t[1]], remap[t[2]]
    if len({a, b, c}) == 3:
        k = tuple(sorted((a, b, c)))
        if k not in seen:
            seen.add(k)
            new_tris.append([a, b, c])

# shell filter: drop interior verts (opt-in: pass 'shell'; only safe for solid-scan models —
# on surface-only models it eats fissure/cerebellum surface and opens holes)
if 'shell' in sys.argv[4:]:
    vox = {}
    for i, (x, y, z) in enumerate(new_verts):
        vox.setdefault((int(x // cell), int(y // cell), int(z // cell)), []).append(i)
    shell = []
    for i, (x, y, z) in enumerate(new_verts):
        k = (int(x // cell), int(y // cell), int(z // cell))
        interior = all((k[0]+dx, k[1]+dy, k[2]+dz) in vox
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
                       if (dx, dy, dz) != (0, 0, 0))
        if not interior:
            shell.append(i)
    remap2 = {old: new for new, old in enumerate(shell)}
    new_verts = [new_verts[i] for i in shell]
    new_tris = [[remap2[a], remap2[b], remap2[c]] for a, b, c in new_tris
                if a in remap2 and b in remap2 and c in remap2]

# fill the front-bottom gap: drape a patch under the frontal lobe (opt-in: pass 'patch')
if 'patch' in sys.argv[4:]:
    gx, gz = 8, 6
    xs = [-0.42 + i * (0.84 / (gx - 1)) for i in range(gx)]
    zs = [0.34 + j * (0.50 / (gz - 1)) for j in range(gz)]
    base_verts = list(new_verts)
    def bottom_y(x, z):
        near = [v[1] for v in base_verts if abs(v[0]-x) < 0.3 and abs(v[2]-z) < 0.3]
        return (max(near) if near else 0.45) + 0.05
    ids = {}
    for j, z in enumerate(zs):
        for i, x in enumerate(xs):
            ids[(i, j)] = len(new_verts)
            new_verts.append([round(x, 4), round(bottom_y(x, z), 4), round(z, 4)])
    for j in range(gz - 1):
        for i in range(gx - 1):
            a, b = ids[(i, j)], ids[(i+1, j)]
            c2, d2 = ids[(i, j+1)], ids[(i+1, j+1)]
            new_tris.append([a, c2, b]); new_tris.append([b, c2, d2])

# mark buried points: r=2 voxel neighborhood (124 cells) almost fully occupied.
# index.html hides their dots but keeps them as mesh vertices, so no holes open.
# ponytail: threshold 100/124 tuned for cell~0.24; lower it to hide more dots.
vox2 = set()
for x, y, z in new_verts:
    vox2.add((int(x // cell), int(y // cell), int(z // cell)))
hidden = []
for i, (x, y, z) in enumerate(new_verts):
    k = (int(x // cell), int(y // cell), int(z // cell))
    n = sum(1 for dx in range(-2, 3) for dy in range(-2, 3) for dz in range(-2, 3)
            if (dx, dy, dz) != (0, 0, 0) and (k[0]+dx, k[1]+dy, k[2]+dz) in vox2)
    if n >= 100:
        hidden.append(i)

with open(out, 'w', encoding='utf-8') as f:
    f.write('const BRAIN_MESH=' + json.dumps({'verts': new_verts, 'tris': new_tris, 'hidden': hidden}) + ';\n')

assert all(i < len(new_verts) for t in new_tris for i in t)
assert all(len(set(t)) == 3 for t in new_tris)
print(f'{len(verts)} verts {len(tris)} tris -> {len(new_verts)} verts {len(new_tris)} tris (cell={cell})')
