"""Render each stage of mechanism-demo.html in Python with the same projection
as the canvas renderer, so layout issues can be checked without a browser.

Usage: python tools/preview_demo_stages.py
Output: assets/demo-stage-previews.png (2x3 grid, one panel per stage)
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_meshes(mesh_dir):
    def parse_mtl(path):
        mats, cur = {}, None
        for ln in open(path, encoding='utf-8'):
            p = ln.split()
            if not p:
                continue
            if p[0] == 'newmtl':
                cur = {'c': '#000000', 'a': 1.0}
                mats[p[1]] = cur
            elif p[0] == 'Kd' and cur:
                cur['c'] = '#%02x%02x%02x' % tuple(round(float(x) * 255) for x in p[1:4])
            elif p[0] == 'd' and cur:
                cur['a'] = float(p[1])
        return mats

    mats = parse_mtl(os.path.join(mesh_dir, 'materials.mtl'))
    out = {}
    for fn in sorted(os.listdir(mesh_dir)):
        if not fn.endswith('.obj'):
            continue
        parts, part, base, nv = [], None, 0, 0
        for ln in open(os.path.join(mesh_dir, fn), encoding='utf-8'):
            p = ln.split()
            if not p:
                continue
            if p[0] == 'o':
                part = {'c': '#ffffff', 'a': 1.0, 'v': [], 't': []}
                parts.append(part)
                base = nv
            elif p[0] == 'usemtl' and part is not None:
                part.update(mats[p[1]])
            elif p[0] == 'v' and part is not None:
                part['v'].append([float(x) for x in p[1:4]])
                nv += 1
            elif p[0] == 'f' and part is not None:
                part['t'].append([int(x) - 1 - base for x in p[1:4]])
        out[fn[:-4]] = parts
    return out

MESHES = load_meshes(os.path.join(ROOT, 'static', 'mechanism-meshes'))
OUT = os.path.join(ROOT, 'assets', 'demo-stage-previews.png')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

W, H = 1200, 640
F = 7.0

def smooth(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)

def rgb(hexs):
    n = int(hexs[1:], 16)
    return np.array([(n >> 16) & 255, (n >> 8) & 255, n & 255]) / 255.0

def rot_v(v, r, sc):
    x, y, z = v[:, 0] * sc, v[:, 1] * sc, v[:, 2] * sc
    if r[0]:
        c, s = np.cos(r[0]), np.sin(r[0])
        y, z = y * c - z * s, y * s + z * c
    if r[1]:
        c, s = np.cos(r[1]), np.sin(r[1])
        x, z = x * c + z * s, -x * s + z * c
    if r[2]:
        c, s = np.cos(r[2]), np.sin(r[2])
        x, y = x * c - y * s, x * s + y * c
    return np.stack([x, y, z], axis=1)

def mk(mesh, **kw):
    d = dict(mesh=mesh, pos=np.zeros(3), rot=[0, 0, 0], scale=1.0,
             show=True, glow=0.0, alpha=1.0)
    d.update(kw)
    return d

PI = np.pi
O = {
    'tcell': mk(MESHES['tcell'], pos=np.array([-2.85, 0, 0.]), scale=2.2),
    'neuron': mk(MESHES['neuron'], pos=np.array([3.3, -.15, 0.]), rot=[-1.22, 0, .3], scale=1.6),
    'ecto': mk(MESHES['ecto'], pos=np.array([-.75, .35, .1]), rot=[0, PI / 2, 0], scale=1.1),
    'core': mk(MESHES['core'], pos=np.array([-.75, .35, .1]), rot=[0, PI / 2, 0], scale=1.1),
    'tf': mk(MESHES['tf'], pos=np.array([-1.47, .35, .1])),
    'bcan': mk(MESHES['bcan'], pos=np.array([1.82, .35, .1])),
    'trkb': mk(MESHES['trkb'], pos=np.array([2.63, -.75, .3]), rot=[0, -PI / 2, 0], scale=.8),
    'dna': mk(MESHES['dna'], pos=np.array([-1.44, -.1, .22]), rot=[-PI / 2, 0, 0], scale=.5),
}
BDNF_S = np.array([.35, .6, .15])
BDNF_E = np.array([2.23, -.7, .3])
DOCK_OFF = np.array([[0, 0, 0], [.13, .09, .05], [-.11, .11, -.05],
                     [.06, -.1, .09], [-.15, -.03, .07], [.11, .03, -.1]])

CAMS = [
    dict(look=[0, .05, 0], zoom=.14, ang=.55, tlt=.30),
    dict(look=[1.0, .35, .1], zoom=.40, ang=.10, tlt=.16),
    dict(follow='tf', zoom=.36, ang=.40, tlt=.28),
    dict(look=[-1.45, -.05, .2], zoom=.40, ang=.50, tlt=.30),
    dict(look=[1.0, .1, .2], zoom=.24, ang=.60, tlt=.30),
    dict(look=[2.55, -.4, .2], zoom=.36, ang=.35, tlt=.26),
]
STAGE_NAMES = ['0 OVERVIEW', '1 RECOGNITION', '2 CLEAVAGE',
               '3 TRANSCRIPTION', '4 SECRETION', '5 REPAIR']

def stage_state(i):
    """Apply the same per-stage positions as mechanism-demo.html applyStage()."""
    for k in O:
        O[k]['glow'] = 0.0
    O['tcell']['alpha'] = .3 if i in (2, 3) else 1.0  # membrane fade for intracellular shots
    if i == 0:
        O['tcell']['pos'] = np.array([-2.85, 0, 0.])
        ecto_p, tf_p = np.array([-.75, .35, .1]), np.array([-1.47, .35, .1])
    else:
        O['tcell']['pos'] = np.array([-1.7, 0, 0.])
        ecto_p, tf_p = np.array([.4, .35, .1]), np.array([-.32, .35, .1])
    bcan_p = np.array([1.82, .35, .1])
    if i == 1:
        O['bcan']['glow'] = 1; O['ecto']['glow'] = .7
    if i == 2:  # end of cleavage micro-timeline (k=1)
        ecto_p = ecto_p + np.array([.4, .35, 0.])
        bcan_p = bcan_p + np.array([.4, .35, 0.])
        tf_p = np.array([-1.55, -.1, .2])
        O['tf']['glow'] = .8
    if i >= 3:
        tf_p = np.array([-1.2, .05, .2])
        ecto_p = np.array([.8, .7, .1])   # ectodomain+BCAN stay shed after S2
        bcan_p = np.array([2.22, .7, .1])
        O['dna']['glow'] = 1; O['tf']['glow'] = .8
    if i >= 5:
        O['neuron']['glow'] = .9
    O['ecto']['pos'] = ecto_p
    O['core']['pos'] = np.array([-.75, .35, .1]) if i == 0 else np.array([.4, .35, .1])
    O['tf']['pos'] = tf_p
    O['bcan']['pos'] = bcan_p

    bdnfs = []
    if i >= 4:
        for j in range(6):
            p = smooth((3.5 - j * .5) / 2.2) if i == 4 else 1.0
            if p <= 0:
                continue
            E = BDNF_E + DOCK_OFF[j]
            pos = BDNF_S + (E - BDNF_S) * p
            pos[1] += np.sin(p * PI) * .5
            pos[2] += np.sin(p * PI * 2 + j * 1.7) * .15
            bdnfs.append(pos)
    labels = [
        (O['tcell']['pos'] + [0, -2.6, 0], 'T cell'),
        (O['neuron']['pos'] + [0, 2.2, 0], 'Neuron'),
        (O['core']['pos'] + [0, -.6, 0], 'SynNotch'),
        (O['bcan']['pos'] + [0, .7, 0], 'BCAN'),
    ]
    if i >= 2:
        labels.append((O['tf']['pos'] + [0, .5, 0], 'VP64-Gal4 (ICD)'))
    if i >= 3:
        labels.append((O['dna']['pos'] + [0, -.6, 0], '5xUAS-BDNF'))
    if i >= 4:
        labels.append((O['trkb']['pos'] + [0, .55, 0], 'TrkB'))
        if bdnfs:
            labels.append((bdnfs[0] + [0, .35, 0], 'BDNF'))
    return bdnfs, labels

def render(ax, stage):
    cm = CAMS[stage]
    look = np.array(cm['look']) if 'look' in cm else O[cm['follow']]['pos'].copy()
    A, T = cm['ang'], cm['tlt']
    cA, sA, cT, sT = np.cos(A), np.sin(A), np.cos(T), np.sin(T)
    S = min(W, H) * cm['zoom']

    def project(P):
        x1 = P[:, 0] * cA + P[:, 2] * sA
        z1 = -P[:, 0] * sA + P[:, 2] * cA
        y1 = P[:, 1] * cT - z1 * sT
        z2 = P[:, 1] * sT + z1 * cT
        p = F / (F - z2)
        return x1 * p * S, y1 * p * S, z2, x1, y1

    lc = project(look[None, :])
    cx, cy = -lc[0][0], -lc[1][0]  # shift so look lands at panel centre

    bdnfs, labels = stage_state(stage)
    draw = [O[k] for k in ('tcell', 'neuron', 'ecto', 'core', 'tf', 'bcan', 'trkb', 'dna')]
    for pos in bdnfs:
        draw.append(mk(MESHES['bdnf'], pos=pos, scale=.5, glow=.6))

    faces = []
    for inst in draw:
        for part in inst['mesh']:
            V = rot_v(np.array(part['v']), inst['rot'], inst['scale']) + inst['pos']
            sx, sy, sz, rx, ry = project(V)
            for tri in part['t']:
                a, b, c = tri[0], tri[1], tri[2]  # JS renderer also uses only the first 3
                faces.append((sz[a] + sz[b] + sz[c], a, b, c, sx, sy, sz, rx, ry,
                              part['c'], part['a'] * inst['alpha'], inst['glow']))
    faces.sort(key=lambda f: f[0])
    for _z, a, b, c, sx, sy, sz, rx, ry, col, al, gl in faces:
        ux, uy, uz = rx[b] - rx[a], ry[b] - ry[a], sz[b] - sz[a]
        vx, vy, vz = rx[c] - rx[a], ry[c] - ry[a], sz[c] - sz[a]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        if nz < 0:
            nx, ny, nz = -nx, -ny, -nz
        il = 1.0 / (np.sqrt(nx * nx + ny * ny + nz * nz) or 1)
        la = min(1.15, (.32 + .68 * max(0, (nx * .3 - ny * .5 + nz * .81) * il)) * (1 + gl * .55))
        ax.add_patch(Polygon([(cx + sx[a], cy + sy[a]), (cx + sx[b], cy + sy[b]),
                              (cx + sx[c], cy + sy[c])],
                             closed=True, facecolor=tuple(np.clip(rgb(col) * la, 0, 1)),
                             edgecolor='#234256', linewidth=.3, alpha=al))
    for wpos, txt in labels:
        lx, ly, _z2, _rx, _ry = project(np.array(wpos, dtype=float)[None, :])
        ax.text(cx + lx[0], cy + ly[0] - 10, txt, ha='center', va='bottom',
                color='#DDF2FF', fontsize=9)
    ax.set_xlim(-W / 2, W / 2)
    ax.set_ylim(-H / 2, H / 2)
    ax.set_aspect('equal')
    ax.invert_yaxis()  # match canvas screen coords (y down)
    ax.set_axis_off()
    ax.set_title(STAGE_NAMES[stage], color='#53DBD3', fontsize=12, pad=4)

import sys

if len(sys.argv) > 1:  # single stage, high res: python tools/preview_demo_stages.py 1 [ang_off] [tlt_off]
    st = int(sys.argv[1])
    if len(sys.argv) > 2:
        CAMS[st]['ang'] += float(sys.argv[2])  # reproduce live drift/drag: ang = base + sin(t)*.18 + dragA
    if len(sys.argv) > 3:
        CAMS[st]['tlt'] += float(sys.argv[3])
    fig = plt.figure(figsize=(12, 6.4), facecolor='#0E2233')
    ax = fig.add_axes([0, 0, 1, 1])  # full-bleed; data aspect 1200:640 == figure aspect
    ax.set_facecolor('#122C44')
    render(ax, st)
    out = os.path.join(ROOT, 'assets', f'demo-stage-{st}.png')
    fig.savefig(out, dpi=150, facecolor=fig.get_facecolor())
    print('stage preview ->', out)
    sys.exit(0)

fig, axes = plt.subplots(2, 3, figsize=(18, 10), facecolor='#0E2233')
for st in range(6):
    ax = axes[st // 3][st % 3]
    ax.set_facecolor('#122C44')
    render(ax, st)
fig.tight_layout()
fig.savefig(OUT, dpi=130, facecolor=fig.get_facecolor())
print('stage previews ->', OUT)
