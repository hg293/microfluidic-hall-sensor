#!/usr/bin/env python3
"""
Generate all publication figures for the uFlow AIES paper.
Reproduces the exact physics engine from the simulator.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib import patheffects
import os

# ── Output directory ──
OUTDIR = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(OUTDIR, exist_ok=True)

# ── Constants ──
MU0 = 4 * np.pi * 1e-7   # T·m/A
EC  = 1.6e-19             # C

# ── Physics functions (exact port from index.html) ──

def bead_moment(r_b, mu_r, B0):
    chi = 3.0 * (mu_r - 1.0) / (mu_r + 2.0)
    return (4.0/3.0) * np.pi * r_b**3 * chi * B0 / MU0

def dip_bz(m, dx, dy, dz):
    r2 = dx**2 + dy**2 + dz**2
    if r2 < 1e-30:
        return 0.0
    return (MU0 / (4*np.pi)) * m * (2*dz**2 - dx**2 - dy**2) / r2**2.5

def volume_avg_bz(m, bx, by, r, sW, t, nxy=10, nz=3):
    hw = sW / 2.0
    stxy = sW / nxy
    stz = t / nz
    total = 0.0
    for iz in range(nz):
        dz = r + (iz + 0.5) * stz
        for ix in range(nxy):
            sx = -hw + (ix + 0.5) * stxy
            for iy in range(nxy):
                sy = -hw + (iy + 0.5) * stxy
                total += dip_bz(m, bx - sx, by - sy, dz)
    return total / (nxy * nxy * nz)

def compute_delta_vh(RH, sigma, Vbias, m, bx, by, r, sW, t, nxy=10, nz=3):
    avg_bz = volume_avg_bz(m, bx, by, r, sW, t, nxy, nz)
    return RH * sigma * avg_bz * Vbias

# ── Material database (exact from simulator) ──
MATERIALS = [
    {'id':'graphene',     'name':'Graphene (CVD)',      'mu':3000,  'n':5e15,   'dim':'2D', 'color':'#06b6d4', 'family':'Graphene'},
    {'id':'graphene-hbn', 'name':'Graphene/hBN',        'mu':40000, 'n':1.1e15, 'dim':'2D', 'color':'#22d3ee', 'family':'Graphene'},
    {'id':'graphene-sic', 'name':'Graphene/SiC',        'mu':3000,  'n':7.5e16, 'dim':'2D', 'color':'#2dd4bf', 'family':'Graphene'},
    {'id':'gaas',         'name':'GaAs/AlGaAs 2DEG',    'mu':7000,  'n':5e15,   'dim':'2D', 'color':'#a78bfa', 'family':'III-V 2D'},
    {'id':'algangan',     'name':'AlGaN/GaN 2DEG',      'mu':1500,  'n':1e17,   'dim':'2D', 'color':'#34d399', 'family':'III-V 2D'},
    {'id':'insb',         'name':'InSb (MBE)',           'mu':35000, 'n':2e22,   'dim':'3D', 'color':'#f59e0b', 'family':'III-V 3D'},
    {'id':'inas',         'name':'InAs (thin film)',     'mu':22000, 'n':1.5e23, 'dim':'3D', 'color':'#fb923c', 'family':'III-V 3D'},
    {'id':'inas-alsb',    'name':'InAs/AlSb 2DEG',      'mu':22000, 'n':1e16,   'dim':'2D', 'color':'#fdba74', 'family':'III-V 2D'},
    {'id':'insb-qw',      'name':'InSb QW',             'mu':42000, 'n':5e15,   'dim':'2D', 'color':'#fbbf24', 'family':'III-V 2D'},
    {'id':'si',           'name':'Si CMOS',              'mu':1400,  'n':1e22,   'dim':'3D', 'color':'#94a3b8', 'family':'Other'},
    {'id':'bismuth',      'name':'Bismuth',              'mu':15000, 'n':3e23,   'dim':'3D', 'color':'#c084fc', 'family':'Other'},
    {'id':'bise',         'name':'Bi2Se3 (TI)',          'mu':3000,  'n':2e16,   'dim':'2D', 'color':'#e879f9', 'family':'Other'},
]

# ── Design configurations from companion paper ──
DESIGNS = {
    'I':   {'w':5e-6,  't':0.5e-6, 'db':2e-6,  'r':1e-6,  'label':'Design I\n(5 \u00d7 5 \u03bcm)'},
    'II':  {'w':10e-6, 't':1e-6,   'db':6e-6,  'r':3e-6,  'label':'Design II\n(10 \u00d7 10 \u03bcm)'},
    'III': {'w':50e-6, 't':1e-6,   'db':10e-6, 'r':5e-6,  'label':'Design III\n(50 \u00d7 50 \u03bcm)'},
}
RH_VAL    = 1.25e-3   # m^3/C
SIGMA_VAL = 1040.0    # S/m
VBIAS     = 5.0       # V
B0        = 50e-3     # T
MU_R      = 10        # magnetite

# ── Matplotlib style: publication quality, no AI look ──
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'mathtext.fontset': 'stix',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'legend.fontsize': 8,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.minor.width': 0.3,
    'ytick.minor.width': 0.3,
    'lines.linewidth': 1.0,
    'axes.grid': False,
})

COL_WIDTH = 3.5   # inches (single column Elsevier)
DBL_WIDTH = 7.0   # double column

# ═══════════════════════════════════════════════════════════════════════
# FIGURE 1: Architecture diagram
# ═══════════════════════════════════════════════════════════════════════

def fig1_architecture():
    fig, ax = plt.subplots(figsize=(DBL_WIDTH, 2.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    box_style = dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0', edgecolor='#333333', linewidth=0.8)
    box_hl    = dict(boxstyle='round,pad=0.3', facecolor='#e8f4fd', edgecolor='#1a73e8', linewidth=0.8)
    box_out   = dict(boxstyle='round,pad=0.3', facecolor='#fef3e2', edgecolor='#e8871a', linewidth=0.8)

    # User input
    ax.text(0.8, 3.2, 'User\ninteraction', ha='center', va='center', fontsize=8, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#e8e8e8', edgecolor='#555555', linewidth=0.8))

    # React state
    ax.text(2.8, 3.2, 'React 18\nstate', ha='center', va='center', fontsize=8, fontweight='bold', bbox=box_style)

    # Physics engine (central, highlighted)
    ax.text(5.0, 3.2, 'Physics engine\n(Eqs. 1\u20139)', ha='center', va='center', fontsize=8,
            fontweight='bold', bbox=box_hl)

    # Submodules
    sub_y = 1.6
    subs = [
        (1.5, sub_y, 'Clausius\u2013Mossotti\nbead moment'),
        (3.5, sub_y, 'Point-dipole\nstray field'),
        (5.5, sub_y, 'Volume-averaged\nHall voltage'),
        (7.5, sub_y, 'Poiseuille\ntransport'),
    ]
    for (sx, sy, label) in subs:
        ax.text(sx, sy, label, ha='center', va='center', fontsize=7,
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#f7f7f7', edgecolor='#888888', linewidth=0.5))

    # Outputs
    ax.text(7.5, 3.2, 'Three.js r160\n3D scene', ha='center', va='center', fontsize=8, fontweight='bold', bbox=box_out)
    ax.text(9.3, 3.2, 'Canvas 2D\nsignal trace', ha='center', va='center', fontsize=8, fontweight='bold', bbox=box_out)

    # Material DB
    ax.text(9.3, 1.6, 'Material DB\n(12 presets)', ha='center', va='center', fontsize=7,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#f0f7f0', edgecolor='#4a8c4a', linewidth=0.5))

    # Bead library
    ax.text(9.3, 0.5, 'Bead library\n(8 presets)', ha='center', va='center', fontsize=7,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#f0f7f0', edgecolor='#4a8c4a', linewidth=0.5))

    # Arrows: User -> React -> Physics -> Outputs
    arrow_kw = dict(arrowstyle='->', color='#333333', lw=0.8, mutation_scale=10)
    ax.annotate('', xy=(2.0, 3.2), xytext=(1.45, 3.2), arrowprops=arrow_kw)
    ax.annotate('', xy=(4.1, 3.2), xytext=(3.55, 3.2), arrowprops=arrow_kw)
    ax.annotate('', xy=(6.7, 3.2), xytext=(5.9, 3.2), arrowprops=arrow_kw)
    ax.annotate('', xy=(8.5, 3.2), xytext=(8.2, 3.2), arrowprops=arrow_kw)

    # Physics -> submodules
    for (sx, sy, _) in subs:
        ax.annotate('', xy=(sx, sy+0.42), xytext=(5.0, 3.2-0.42),
                     arrowprops=dict(arrowstyle='->', color='#1a73e8', lw=0.5, mutation_scale=8))

    # Material/Bead DB -> Physics
    ax.annotate('', xy=(5.9, 3.0), xytext=(8.6, 1.6),
                arrowprops=dict(arrowstyle='->', color='#4a8c4a', lw=0.5, mutation_scale=8, ls='dashed'))
    ax.annotate('', xy=(5.9, 2.9), xytext=(8.6, 0.5),
                arrowprops=dict(arrowstyle='->', color='#4a8c4a', lw=0.5, mutation_scale=8, ls='dashed'))

    # Labels on arrows
    ax.text(1.7, 3.5, 'sliders,\ndropdowns', ha='center', va='bottom', fontsize=6, color='#555555', style='italic')
    ax.text(3.3, 3.5, 'setState', ha='center', va='bottom', fontsize=6, color='#555555', style='italic')
    ax.text(6.3, 3.5, 'useMemo', ha='center', va='bottom', fontsize=6, color='#555555', style='italic')

    # Bottom label
    ax.text(5.0, 0.3, 'Single HTML file (~1000 lines) --- React 18 + Three.js r160 via CDN, no build tools',
            ha='center', va='center', fontsize=7, color='#666666', style='italic')

    fig.savefig(os.path.join(OUTDIR, 'fig1_architecture.pdf'))
    fig.savefig(os.path.join(OUTDIR, 'fig1_architecture.png'))
    plt.close(fig)
    print('  Fig 1: architecture diagram')


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 3: Validation bar chart
# ═══════════════════════════════════════════════════════════════════════

def fig3_validation():
    labels = ['Design I\n(5 \u00d7 5 \u03bcm)', 'Design II\n(10 \u00d7 10 \u03bcm)', 'Design III\n(50 \u00d7 50 \u03bcm)']
    comsol = [21.375, 42.79, 3.056]
    uflow  = [20.2,   42.4,  3.03]
    errors = [5.5,    0.9,   0.9]

    x = np.arange(len(labels))
    width = 0.32

    fig, ax = plt.subplots(figsize=(COL_WIDTH, 2.6))
    bars1 = ax.bar(x - width/2, comsol, width, label='COMSOL FEM-BEM', color='#4a90c4', edgecolor='#2d5f8a', linewidth=0.5)
    bars2 = ax.bar(x + width/2, uflow,  width, label='\u03bcFlow',     color='#e8934a', edgecolor='#b06a2d', linewidth=0.5)

    ax.set_yscale('log')
    ax.set_ylabel('$\\Delta V_H$ (mV)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(frameon=True, edgecolor='#cccccc', fancybox=False)
    ax.set_ylim(1, 100)
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.get_major_formatter().set_scientific(False)
    ax.set_yticks([1, 2, 5, 10, 20, 50])
    ax.set_yticklabels(['1', '2', '5', '10', '20', '50'])

    # Error annotations
    for i, (c, u, e) in enumerate(zip(comsol, uflow, errors)):
        ymax = max(c, u)
        ax.annotate('{:.1f}%'.format(e), xy=(x[i], ymax*1.12), ha='center', va='bottom',
                    fontsize=7, color='#666666')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(os.path.join(OUTDIR, 'fig3_validation.pdf'))
    fig.savefig(os.path.join(OUTDIR, 'fig3_validation.png'))
    plt.close(fig)
    print('  Fig 3: validation bar chart')


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 4: Delta_VH vs distance (log-log) for 3 designs
# ═══════════════════════════════════════════════════════════════════════

def fig4_distance():
    distances = np.logspace(np.log10(0.5e-6), np.log10(20e-6), 60)  # 0.5 to 20 um

    fig, ax = plt.subplots(figsize=(COL_WIDTH, 2.8))

    design_colors = {'I': '#2d5f8a', 'II': '#c44a4a', 'III': '#4a8c4a'}
    design_lines  = {'I': '-', 'II': '--', 'III': '-.'}

    for dname, d in DESIGNS.items():
        rb = d['db'] / 2.0
        m = bead_moment(rb, MU_R, B0)
        dvh_vals = []
        for r in distances:
            dvh = compute_delta_vh(RH_VAL, SIGMA_VAL, VBIAS, m, 0, 0, r, d['w'], d['t'], nxy=12, nz=3)
            dvh_vals.append(abs(dvh) * 1e3)  # mV
        ax.plot(distances * 1e6, dvh_vals, design_lines[dname], color=design_colors[dname],
                label=d['label'].replace('\n', ' '), linewidth=1.2)

    # 1/r^3 reference line
    r_ref = np.logspace(np.log10(2), np.log10(15), 20)
    ref_vals = 500 * (r_ref[0] / r_ref)**3
    ax.plot(r_ref, ref_vals, ':', color='#999999', linewidth=0.7, label='$1/r^3$ decay')

    # Shaded operating range
    ax.axvspan(1, 5, alpha=0.08, color='#4a90c4', zorder=0)
    ax.text(2.5, 0.015, 'Typical\noperating\nrange', ha='center', va='center', fontsize=6,
            color='#4a90c4', style='italic')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Bead\u2013sensor distance $r$ (\u03bcm)')
    ax.set_ylabel('$|\\Delta V_H|$ (mV)')
    ax.legend(frameon=True, edgecolor='#cccccc', fancybox=False, fontsize=7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(os.path.join(OUTDIR, 'fig4_distance.pdf'))
    fig.savefig(os.path.join(OUTDIR, 'fig4_distance.png'))
    plt.close(fig)
    print('  Fig 4: distance decay')


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 5: Cross-material comparison (horizontal bar chart)
# ═══════════════════════════════════════════════════════════════════════

def fig5_materials():
    # Design II geometry, bead centered at (0,0), r=3um
    d = DESIGNS['II']
    rb = d['db'] / 2.0
    m = bead_moment(rb, MU_R, B0)

    results = []
    for mat in MATERIALS:
        mu_SI = mat['mu'] * 1e-4
        n = mat['n']
        RH = 1.0 / (n * EC)
        sigma = n * EC * mu_SI
        dvh = compute_delta_vh(RH, sigma, VBIAS, m, 0, 0, d['r'], d['w'], d['t'], nxy=12, nz=3)
        results.append((mat['name'], abs(dvh)*1e3, mat['color'], mat['family']))

    # Sort by magnitude
    results.sort(key=lambda x: x[1])

    names  = [r[0] for r in results]
    values = [r[1] for r in results]
    colors = [r[2] for r in results]

    # Family-based colors for a cleaner look
    fam_colors = {
        'Graphene': '#2d8c8c',
        'III-V 2D': '#4a6fc4',
        'III-V 3D': '#c47a4a',
        'Other':    '#888888',
    }
    bar_colors = [fam_colors[r[3]] for r in results]

    fig, ax = plt.subplots(figsize=(COL_WIDTH, 3.2))
    y = np.arange(len(names))
    bars = ax.barh(y, values, height=0.6, color=bar_colors, edgecolor='white', linewidth=0.3)

    # Value labels
    for i, (v, name) in enumerate(zip(values, names)):
        if v > 0.1:
            ax.text(v * 1.08, i, '{:.1f}'.format(v), va='center', fontsize=6.5, color='#333333')
        else:
            ax.text(v * 1.15, i, '{:.3f}'.format(v), va='center', fontsize=6.5, color='#333333')

    ax.set_xscale('log')
    ax.set_xlabel('$|\\Delta V_H|$ (mV)')
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Legend for families
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=fam_colors[f], label=f) for f in ['Graphene', 'III-V 2D', 'III-V 3D', 'Other']]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, edgecolor='#cccccc',
              fancybox=False, fontsize=7)

    fig.savefig(os.path.join(OUTDIR, 'fig5_materials.pdf'))
    fig.savefig(os.path.join(OUTDIR, 'fig5_materials.png'))
    plt.close(fig)
    print('  Fig 5: material comparison')


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 6: Flow velocity sensitivity (dual-axis)
# ═══════════════════════════════════════════════════════════════════════

def fig6_flowrate():
    """
    Detection rate and mean peak DVH vs mean flow velocity.
    Simulate N=20 beads at Design II geometry in range mode.
    Heights uniformly distributed across a 25 um channel (typical for
    single-bead detection experiments).
    Detection: bead is "detected" if its peak |DVH| > threshold AND
    the transit is slow enough for the adaptive sub-stepping to resolve the peak.
    """
    d = DESIGNS['II']
    rb = d['db'] / 2.0
    m = bead_moment(rb, MU_R, B0)
    channel_H = 25e-6  # 25 um channel — realistic for bead detection

    # For material: use the companion paper params
    RH = RH_VAL
    sigma = SIGMA_VAL

    velocities = np.logspace(np.log10(0.1), np.log10(50), 40)  # mm/s
    N_beads = 20
    np.random.seed(42)

    # Bead heights: from just above sensor to near channel ceiling
    min_h = rb + 0.1e-6
    max_h = channel_H - rb
    bead_heights = np.random.uniform(min_h, max_h, N_beads)

    # Peak DVH for each bead (depends only on height, bead at center x=0)
    bead_peak_dvh = []
    for h in bead_heights:
        dvh = compute_delta_vh(RH, sigma, VBIAS, m, 0, 0, h, d['w'], d['t'], nxy=10, nz=3)
        bead_peak_dvh.append(abs(dvh) * 1e3)
    bead_peak_dvh = np.array(bead_peak_dvh)

    # Detection threshold: 0.01 mV (10 uV) — achievable with lock-in readout
    threshold = 0.01  # mV

    # Adaptive sub-stepping parameters (from simulator)
    frame_dt = 1.0/60.0  # 60 fps browser animation
    max_substeps = 20

    detection_rates = []
    mean_dvhs = []

    for v_avg_mm in velocities:
        v_avg = v_avg_mm * 1e-3  # m/s
        detected_count = 0
        dvh_detected = []
        for i in range(N_beads):
            h = bead_heights[i]
            eta = 2*h / channel_H - 1.0
            v_local = 1.5 * v_avg * (1 - eta**2)
            transit_time = d['w'] / max(v_local, 1e-12)
            # Sub-step resolves peak if transit > minimum sampling interval
            substep_dt = frame_dt / max_substeps
            peak_resolved = transit_time > substep_dt
            if bead_peak_dvh[i] > threshold and peak_resolved:
                detected_count += 1
                dvh_detected.append(bead_peak_dvh[i])

        detection_rates.append(100.0 * detected_count / N_beads)
        # Mean peak DVH of ALL beads (height-dependent, velocity-independent)
        mean_dvhs.append(np.mean(bead_peak_dvh))

    fig, ax1 = plt.subplots(figsize=(COL_WIDTH, 2.6))
    color1 = '#2d5f8a'
    color2 = '#c44a4a'

    ax1.plot(velocities, detection_rates, '-', color=color1, linewidth=1.2, label='Detection rate')
    ax1.set_xlabel('Mean flow velocity $\\bar{v}$ (mm/s)')
    ax1.set_ylabel('Detection rate (%)', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xscale('log')
    ax1.set_ylim(0, 110)

    # Shaded optimal window
    ax1.axvspan(0.5, 5, alpha=0.08, color='#4a8c4a', zorder=0)
    ax1.text(1.6, 105, 'Optimal window', ha='center', fontsize=6, color='#4a8c4a', style='italic')

    ax2 = ax1.twinx()
    ax2.plot(velocities, mean_dvhs, '--', color=color2, linewidth=1.0, label='Mean $|\\Delta V_H|$')
    ax2.set_ylabel('Mean peak $|\\Delta V_H|$ (mV)', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='center left', frameon=True,
               edgecolor='#cccccc', fancybox=False, fontsize=7)

    ax1.spines['top'].set_visible(False)

    fig.savefig(os.path.join(OUTDIR, 'fig6_flowrate.pdf'))
    fig.savefig(os.path.join(OUTDIR, 'fig6_flowrate.png'))
    plt.close(fig)
    print('  Fig 6: flow velocity sensitivity')


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 7: Sensitivity contour map (bead diameter vs sensor width)
# ═══════════════════════════════════════════════════════════════════════

def fig7_sensitivity():
    """
    Contour heatmap: DVH(mV) as function of bead diameter and sensor width.
    Bead centered at (0,0), distance r = d_b/2 + 0.1 um (bead sitting just above sensor).
    """
    bead_diams = np.linspace(1e-6, 15e-6, 40)    # 1 to 15 um
    sensor_widths = np.linspace(5e-6, 100e-6, 40) # 5 to 100 um
    t_sensor = 1e-6  # 1 um thickness

    RH = RH_VAL
    sigma = SIGMA_VAL

    DVH = np.zeros((len(bead_diams), len(sensor_widths)))

    for i, db in enumerate(bead_diams):
        rb = db / 2.0
        m = bead_moment(rb, MU_R, B0)
        r_dist = rb + 0.1e-6  # bead sitting just above sensor
        for j, sw in enumerate(sensor_widths):
            dvh = compute_delta_vh(RH, sigma, VBIAS, m, 0, 0, r_dist, sw, t_sensor, nxy=10, nz=3)
            DVH[i, j] = abs(dvh) * 1e3  # mV

    SW, DB = np.meshgrid(sensor_widths * 1e6, bead_diams * 1e6)

    fig, ax = plt.subplots(figsize=(COL_WIDTH, 3.0))

    # Use log scale for color
    from matplotlib.colors import LogNorm
    vmin = max(DVH[DVH > 0].min(), 0.001)
    vmax = DVH.max()
    im = ax.pcolormesh(SW, DB, DVH, cmap='viridis', norm=LogNorm(vmin=vmin, vmax=vmax),
                       shading='gouraud')
    cb = fig.colorbar(im, ax=ax, label='$|\\Delta V_H|$ (mV)', pad=0.02)

    # Contour lines at 1, 10, 100 mV
    contour_levels = [0.1, 1, 10, 100]
    CS = ax.contour(SW, DB, DVH, levels=contour_levels, colors='white', linewidths=0.6)
    ax.clabel(CS, inline=True, fontsize=6, fmt='%g mV')

    # Mark the three validated designs
    design_marks = [
        (5,  2,  'I'),
        (10, 6,  'II'),
        (50, 10, 'III'),
    ]
    for sw, db, label in design_marks:
        ax.plot(sw, db, '*', color='white', markersize=8, markeredgecolor='black', markeredgewidth=0.3)
        ax.annotate(label, xy=(sw, db), xytext=(sw+3, db+0.5), fontsize=7, color='white',
                    fontweight='bold',
                    arrowprops=dict(arrowstyle='-', color='white', lw=0.5))

    ax.set_xlabel('Sensor width (\u03bcm)')
    ax.set_ylabel('Bead diameter (\u03bcm)')

    fig.savefig(os.path.join(OUTDIR, 'fig7_sensitivity.pdf'))
    fig.savefig(os.path.join(OUTDIR, 'fig7_sensitivity.png'))
    plt.close(fig)
    print('  Fig 7: sensitivity contour map')


# ═══════════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('Generating AIES paper figures...')
    fig1_architecture()
    fig3_validation()
    fig4_distance()
    fig5_materials()
    fig6_flowrate()
    fig7_sensitivity()
    print('Done. Figures saved to:', OUTDIR)
