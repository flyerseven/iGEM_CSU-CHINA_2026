"""Build low-poly OBJ models for the BRIDGE mechanism diagram + render a preview PNG.

Usage: python tools/build_mechanism_models.py
Outputs: models/mechanism/*.obj, assets/mechanism-meshes.js, assets/mechanism-models-preview.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJ_DIR = os.path.join(ROOT, 'models', 'mechanism')
PREVIEW = os.path.join(ROOT, 'assets', 'mechanism-models-preview.png')
rng = np.random.default_rng(7)

# palette (matches mechanism figures, site-adjacent hues)
PINK = '#F3B9C8'   # T cell membrane
ROSE = '#C26A86'   # T cell nucleus
LAV = '#B9A7E8'    # neuron soma/dendrites
PURP = '#7E6BC4'   # neuron axon / dark accent
BLUE = '#77A0BC'   # receptors (info-blue)
NAVY = '#2D5A7F'   # transcription factor (bridge-navy)
TEAL = '#17B7AE'   # TrkB (deep-teal)
AMBER = '#F4C76B'  # BDNF (research-amber)
CYAN = '#53DBD3'   # DNA strand B (aqua-cyan)
GREY = '#9FB3C8'   # membrane slab


def ico(r=1.0, subdiv=1, noise=0.0, center=(0, 0, 0), squash=(1, 1, 1)):
    t = (1 + 5 ** 0.5) / 2
    v = np.array([[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
                  [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
                  [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]], float)
    f = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
         [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
         [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
         [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    for _ in range(subdiv):
        mid, nf = {}, []
        def midpoint(a, b):
            key = tuple(sorted((a, b)))
            if key not in mid:
                mid[key] = len(v_list)
                v_list.append((v[a] + v[b]) / 2)
            return mid[key]
        v_list = list(v)
        for a, b, c in f:
            ab, bc, ca = midpoint(a, b), midpoint(b, c), midpoint(c, a)
            nf += [[a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]]
        v, f = np.array(v_list), nf
    v /= np.linalg.norm(v, axis=1)[:, None]
    if noise:
        v *= (1 + rng.uniform(-noise, noise, len(v)))[:, None]
    v = v * r * np.array(squash) + np.array(center)
    return v, f


def tube(a, b, r0, r1, sides=6):
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    d /= np.linalg.norm(d)
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    u = np.cross(d, up); u /= np.linalg.norm(u)
    w = np.cross(d, u)
    v, f = [], []
    for i, (p, r) in enumerate(((a, r0), (b, r1))):
        for k in range(sides):
            ang = 2 * np.pi * k / sides
            v.append(p + r * (np.cos(ang) * u + np.sin(ang) * w))
    for k in range(sides):
        k2 = (k + 1) % sides
        f.append([k, k2, sides + k2])
        f.append([k, sides + k2, sides + k])
    f.append(list(range(sides - 1, -1, -1)))
    f.append([sides + k for k in range(sides)])
    return np.array(v), f


def branch(start, direction, length, r, depth, parts, color_parts, color):
    end = np.array(start) + np.array(direction) * length
    v, f = tube(start, end, r, r * 0.55)
    parts.append((v, f)); color_parts.append(color)
    if depth == 0:
        return
    d = np.array(direction, float)
    for s in (-1, 1):
        axis = rng.normal(size=3)
        axis -= axis @ d * d
        axis /= np.linalg.norm(axis)
        ang = s * rng.uniform(0.35, 0.65)
        nd = d * np.cos(ang) + np.cross(axis, d) * np.sin(ang)
        branch(end, nd, length * 0.62, r * 0.6, depth - 1, parts, color_parts, color)


def tcell():
    mem = ico(1.0, subdiv=1, noise=0.06)
    nuc = ico(0.55, subdiv=1, noise=0.05, center=(0.12, -0.08, 0.1))
    # alpha .45: two membrane layers still read as a cell, but the DNA/TF inside stay visible
    return [(mem, PINK, 0.45), (nuc, ROSE, 0.85)]


def neuron():
    parts, cols = [], []
    soma = ico(0.55, subdiv=1, noise=0.08)
    parts.append(soma); cols.append(LAV)
    # dendrites fan over the local +x half only, so after the demo's runtime
    # rotation no branch reaches back across the synaptic cleft into the T cell
    for k in range(5):
        ang = (k - 2) * 0.62
        d = np.array([np.cos(ang), np.sin(ang), 0.35])
        d /= np.linalg.norm(d)
        branch((0, 0, 0.1), d, 0.7, 0.09, 2, parts, cols, LAV)
    axon_pts = [(0, 0, -0.4), (0.15, 0.1, -1.3), (0.5, 0.25, -2.1)]
    for i in range(len(axon_pts) - 1):
        v, f = tube(axon_pts[i], axon_pts[i + 1], 0.07, 0.05)
        parts.append((v, f)); cols.append(PURP)
    for s in (-1, 1):
        branch(axon_pts[-1], (s * 0.6, 0.3, -0.7), 0.45, 0.045, 1, parts, cols, PURP)
    return [(p, c, 1.0) for p, c in zip(parts, cols)]


def synnotch():
    slab_v = np.array([[x, y, z] for x in (-0.75, 0.75) for y in (-0.75, 0.75) for z in (-0.06, 0.06)])
    slab_f = [[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1],
              [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]]
    # scFv as an open socket (bowl) that cradles the BCAN ball — ball-and-socket complementarity
    sv, sf = ico(0.34, subdiv=1, noise=0.04, center=(0, 0, 0.95))
    sf = [t for t in sf if sum(sv[i][2] for i in t) / 3 < 0.93]  # cut the cap -> bowl opens +z
    socket = (sv, sf)
    # NRR: compact globular Notch core that masks the S2 site until ligand pulling
    nrr = ico(0.24, subdiv=1, noise=0.05, center=(0, 0, 0.38), squash=(0.95, 0.95, 1.05))
    core = tube((0, 0, 0.2), (0, 0, -0.35), 0.11, 0.11)
    tf = ico(0.28, subdiv=1, noise=0.05, center=(0, 0, -0.65))
    return [((slab_v, slab_f), GREY, 0.9), (socket, BLUE, 1.0),
            (nrr, BLUE, 1.0), (core, NAVY, 1.0), (tf, NAVY, 1.0)]


def bcan():
    # single small ball — ECM ligand, fits the scFv socket
    return [(ico(0.26, subdiv=1, noise=0.05), BLUE, 1.0)]


def bdnf():
    # subdiv=0: 20-face lobes — the demo spawns 6 of these, keep them cheap
    a = ico(0.3, subdiv=0, noise=0.07, center=(-0.16, 0, 0), squash=(1.3, 0.8, 0.9))
    b = ico(0.3, subdiv=0, noise=0.07, center=(0.16, 0, 0), squash=(1.3, 0.8, 0.9))
    return [(a, AMBER, 1.0), (b, '#E0A94E', 1.0)]


def trkb():
    lobe1 = ico(0.16, subdiv=1, noise=0.08, center=(-0.1, 0, 0.55), squash=(0.8, 0.8, 1.3))
    lobe2 = ico(0.16, subdiv=1, noise=0.08, center=(0.1, 0, 0.55), squash=(0.8, 0.8, 1.3))
    stalk = tube((0, 0, 0.4), (0, 0, -0.5), 0.07, 0.09)
    return [(lobe1, TEAL, 1.0), (lobe2, TEAL, 1.0), (stalk, TEAL, 1.0)]


def dna():
    sa, sb, rungs = [], [], []
    steps, turns, rad, pitch = 13, 1.75, 0.28, 0.16
    pts = [[], []]
    for i in range(steps):
        t = i / (steps - 1) * 2 * np.pi * turns
        z = (i - steps / 2) * pitch
        pts[0].append((rad * np.cos(t), rad * np.sin(t), z))
        pts[1].append((rad * np.cos(t + np.pi), rad * np.sin(t + np.pi), z))
    for s in range(2):
        for i in range(steps - 1):
            (sa if s == 0 else sb).append(tube(pts[s][i], pts[s][i + 1], 0.06, 0.06, 5))
    for i in range(0, steps, 2):
        rungs.append(tube(pts[0][i], pts[1][i], 0.035, 0.035, 5))
    return ([(p, BLUE, 1.0) for p in sa] + [(p, CYAN, 1.0) for p in sb]
            + [(p, GREY, 1.0) for p in rungs])


MODELS = {
    'tcell': ('T Cell', tcell),
    'neuron': ('Neuron', neuron),
    'synnotch': ('SynNotch receptor', synnotch),
    'bcan': ('BCAN ligand', bcan),
    'bdnf': ('BDNF dimer', bdnf),
    'trkb': ('TrkB receptor', trkb),
    'dna': ('5xUAS-BDNF gene', dna),
}


def write_obj(path, parts):
    with open(path, 'w', encoding='utf-8') as fh:
        off = 1
        for (v, f), _c, _a in parts:
            for p in v:
                fh.write(f'v {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}\n')
            for face in f:
                for k in range(1, len(face) - 1):
                    fh.write(f'f {face[0]+off} {face[k]+off} {face[k+1]+off}\n')
            off += len(v)


def export_obj(dir_path):
    """Per-component OBJ + one shared MTL (colors/alpha live in the MTL, the
    standard OBJ way). Browser fetches these directly; vertex coords stay
    relative to each component's origin — the demo applies pos/rot/scale."""
    parts_map = {name: builder() for name, (_label, builder) in MODELS.items()}
    sn = parts_map.pop('synnotch')
    # demo animates these separately: ectodomain scFv+linker+NRR (S2 cut), TM core (S3 cut),
    # TF = the receptor's own intracellular domain (released by S3)
    parts_map['ecto'] = sn[1:3]
    parts_map['core'] = [sn[3]]
    parts_map['tf'] = [sn[4]]

    mats = {}  # (color, alpha) -> material name
    for parts in parts_map.values():
        for _vf, color, alpha in parts:
            key = (color, round(alpha, 2))
            mats.setdefault(key, f"c_{color[1:]}_{int(round(alpha, 2) * 100)}")

    def hex2rgb(h):
        return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))

    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, 'materials.mtl'), 'w', encoding='utf-8') as fh:
        fh.write('# BRIDGE mechanism palette — Kd = face color, d = alpha\n')
        for (color, alpha), name in sorted(mats.items(), key=lambda kv: kv[1]):
            r, g, b = hex2rgb(color)
            fh.write(f'newmtl {name}\nKd {r:.3f} {g:.3f} {b:.3f}\nd {alpha}\n\n')

    header = ('# {name} mesh for mechanism-demo. Coordinates are RELATIVE TO THE\n'
              '# COMPONENT ORIGIN — the demo applies pos/rot/scale at render time.\n'
              '# Regenerate: python tools/build_mechanism_models.py\n')
    for name, parts in parts_map.items():
        lines = [header.format(name=name), 'mtllib materials.mtl\n']
        off = 1
        for i, ((v, f), color, alpha) in enumerate(parts):
            lines.append(f'o part{i}\nusemtl {mats[(color, round(alpha, 2))]}')
            lines += [f'v {p[0]:.3f} {p[1]:.3f} {p[2]:.3f}' for p in v.tolist()]
            for face in f:  # fan-triangulate: tube end caps are N-gons
                for k in range(1, len(face) - 1):
                    lines.append(f'f {face[0] + off} {face[k] + off} {face[k + 1] + off}')
            off += len(v)
        with open(os.path.join(dir_path, f'{name}.obj'), 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines) + '\n')
    print(f'meshes -> {dir_path} ({len(parts_map)} components + materials.mtl)')


def main():
    os.makedirs(OBJ_DIR, exist_ok=True)
    export_obj(os.path.join(ROOT, 'static', 'mechanism-meshes'))
    fig = plt.figure(figsize=(12, 6.5), facecolor='#0E2233')
    for i, (name, (label, builder)) in enumerate(MODELS.items()):
        parts = builder()
        obj_path = os.path.join(OBJ_DIR, f'{name}.obj')
        write_obj(obj_path, parts)
        nv = sum(len(p[0][0]) for p in parts)
        nf = sum(len(p[0][1]) for p in parts)
        assert nv > 0 and nf > 0, name
        print(f'{name}: {nv} verts, {nf} tris -> {obj_path}')

        ax = fig.add_subplot(2, 4, i + 1, projection='3d')
        for (v, f), color, alpha in parts:
            polys = [[v[idx] for idx in tri] for tri in f]
            pc = Poly3DCollection(polys, facecolors=[color] * len(polys),
                                  edgecolors=['#234256'] * len(polys), linewidths=0.4,
                                  alpha=alpha, shade=True)
            ax.add_collection3d(pc)
        allv = np.vstack([p[0][0] for p in parts])
        lo, hi = allv.min(0), allv.max(0)
        c = (lo + hi) / 2
        r = (hi - lo).max() / 2 * 1.1
        ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=16, azim=-55)
        ax.set_axis_off()
        ax.set_title(label, color='#DDF2FF', fontsize=11, pad=2)
    ax_note = fig.add_subplot(2, 4, 8); ax_note.set_axis_off()
    ax_note.text(0.5, 0.5, 'BRIDGE mechanism\nlow-poly kit', ha='center', va='center',
                 color='#53DBD3', fontsize=12, weight='bold')
    fig.tight_layout()
    fig.savefig(PREVIEW, dpi=170, facecolor=fig.get_facecolor())
    print(f'preview -> {PREVIEW}')


if __name__ == '__main__':
    main()
