#!/usr/bin/env python3
"""
Compute all numerical values reported in the µFlow paper.
Every number in a table or inline claim must come from this script.
"""
import numpy as np

mu0 = 4 * np.pi * 1e-7  # T·m/A
kB = 1.38e-23            # J/K
e_charge = 1.6e-19       # C
T = 300                  # K

# ============================================================
# 1. STRAY FIELD VALIDATION (Table tab:stray)
#    Compute on-axis Bz from point dipole at distance dz
#    Bz = (mu0/4pi) * m * 2 / dz^3
#    m = (4/3) pi rb^3 * phi * chi_eff * B0 / mu0
#    chi_eff = 3*(mu_r - 1)/(mu_r + 2)
# ============================================================
print("=" * 60)
print("STRAY FIELD VALIDATION")
print("=" * 60)

def bead_moment(d_b_um, phi, mu_r, B0_T):
    """Compute bead dipole moment [A·m²]"""
    rb = d_b_um * 1e-6 / 2
    chi_eff = 3 * (mu_r - 1) / (mu_r + 2)
    m = (4/3) * np.pi * rb**3 * phi * chi_eff * B0_T / mu0
    return m

def Bz_on_axis(m, dz_um):
    """On-axis Bz from point dipole at distance dz [T]"""
    dz = dz_um * 1e-6
    return (mu0 / (4 * np.pi)) * m * 2 / dz**3

# Gambini 2013 used B0 ~ 50 mT (typical for their CMOS array experiments)
# We'll compute at B0 = 50 mT as stated in our table caption
B0 = 50e-3  # T

beads_stray = [
    # (name, d_b_um, phi, mu_r, dist_um, measured_uT, ref)
    ("M-450",  4.5,  0.06, 10, 3.0, 80,   "Gambini"),
    ("M-280",  2.83, 0.03, 10, 3.0, 11.2, "Gambini"),
    ("MyOne",  1.05, 0.12, 10, 3.0, 3.75, "Gambini"),
    ("M-280",  2.83, 0.03, 10, 7.0, 6.0,  "Besse (B0=500mT)"),
]

print(f"{'Bead':<10} {'d_b(um)':<8} {'phi':<6} {'dist(um)':<9} {'m(A·m²)':<12} {'Bz_pred(uT)':<12} {'Meas(uT)':<10}")
print("-" * 80)
for name, d_b, phi, mu_r, dist, meas, ref in beads_stray:
    B0_use = B0
    if "500mT" in ref:
        B0_use = 500e-3  # Besse used 500 mT
    m = bead_moment(d_b, phi, mu_r, B0_use)
    Bz = Bz_on_axis(m, dist)
    Bz_uT = Bz * 1e6
    print(f"{name:<10} {d_b:<8.2f} {phi:<6.2f} {dist:<9.1f} {m:<12.3e} {Bz_uT:<12.2f} {meas:<10}")

# Also compute at B0=50mT for Besse to show the scaling
m_280_50 = bead_moment(2.83, 0.03, 10, 50e-3)
Bz_280_7um_50 = Bz_on_axis(m_280_50, 7.0) * 1e6
print(f"\nM-280 at 7um, B0=50mT: {Bz_280_7um_50:.2f} uT")
m_280_500 = bead_moment(2.83, 0.03, 10, 500e-3)
Bz_280_7um_500 = Bz_on_axis(m_280_500, 7.0) * 1e6
print(f"M-280 at 7um, B0=500mT: {Bz_280_7um_500:.2f} uT")

# ============================================================
# 2. VOLUME-AVERAGED HALL VOLTAGE (for Design II validation)
#    ΔV_H = G * R_H * sigma * <Bz> * V_bias
#    Need to compute <Bz> via quadrature
# ============================================================
print("\n" + "=" * 60)
print("DESIGN II VALIDATION - Volume-averaged ΔV_H")
print("=" * 60)

def compute_avg_Bz(m, bead_x, bead_y, bead_z_um, w_um, l_um, t_um, nxy=16, nz=8):
    """
    Compute volume-averaged Bz over sensor.
    Sensor centered at origin, bead at (bead_x, bead_y, bead_z) in um.
    """
    w = w_um * 1e-6
    l = l_um * 1e-6
    t = t_um * 1e-6
    bz = bead_z_um * 1e-6

    total = 0.0
    count = 0
    for i in range(nxy):
        xi = -w/2 + (i + 0.5) * w / nxy
        for j in range(nxy):
            yj = -l/2 + (j + 0.5) * l / nxy
            for k in range(nz):
                zk = -(k + 0.5) * t / nz  # sensor below bead
                dx = xi - bead_x * 1e-6
                dy = yj - bead_y * 1e-6
                dz = zk - bz
                r2 = dx**2 + dy**2 + dz**2
                if r2 > 0:
                    r5 = r2**(5/2)
                    Bz_val = (mu0 / (4*np.pi)) * m * (2*dz**2 - dx**2 - dy**2) / r5
                    total += Bz_val
                count += 1
    return total / count

# Design II: w=10um, t=1um, d_b=6um magnetite (phi=1), r=3um, B0=50mT
# R_H = 1.25e-3 m³/C, sigma = 1040 S/m, V_bias = 5V, G=1
designs = [
    ("Design I",   5,  0.5, 2,  1, 1.25e-3, 1040, 5),
    ("Design II",  10, 1,   6,  3, 1.25e-3, 1040, 5),
    ("Design III", 50, 1,   10, 5, 1.25e-3, 1040, 5),
]

print(f"{'Design':<12} {'w(um)':<7} {'d_b(um)':<8} {'r(um)':<7} {'<Bz>(uT)':<10} {'ΔV_H(mV)':<10} {'COMSOL(mV)':<11}")
print("-" * 70)
comsol_vals = [21.375, 42.79, 3.056]
for idx, (name, w, t, d_b, r, R_H, sigma, Vbias) in enumerate(designs):
    m = bead_moment(d_b, 1.0, 10, 50e-3)  # pure magnetite, phi=1
    # bead centered above sensor at height r
    avg_Bz = compute_avg_Bz(m, 0, 0, r + d_b/2, w, w, t, nxy=16, nz=8)
    # Wait - r is bead-sensor distance, bead center is at r above sensor surface
    # Actually r is distance from sensor surface to bead center
    avg_Bz = compute_avg_Bz(m, 0, 0, r, w, w, t, nxy=16, nz=8)
    dVH = 1.0 * R_H * sigma * avg_Bz * Vbias  # G=1
    dVH_mV = dVH * 1e3
    print(f"{name:<12} {w:<7} {d_b:<8} {r:<7} {avg_Bz*1e6:<10.2f} {dVH_mV:<10.2f} {comsol_vals[idx]:<11}")

# ============================================================
# 3. EXPERIMENTAL VALIDATION - compute ΔV_H for published experiments
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENTAL VALIDATION")
print("=" * 60)

# Aledealat 2009: InAs QW, w~5um (square), M-280 bead (d=2.83um, phi=3%),
# B0=55mT, I_bias~10uA
# InAs/AlSb: mu=22000 cm²/Vs, n_s=1e16 m⁻²
# R_H = 1/(n_s*e) for 2D, sigma = n_s*e*mu for sheet
# For 2D: ΔV_H = G * S_I * I_bias * <Bz>  where S_I = R_H = 1/(n_s*e)
# Actually Eq 5 uses R_H * sigma * <Bz> * V_bias
# For 2D material of thickness t_film:
# R_H_3D_equiv = 1/(n_s * e) / 1 = R_H_2D (treating as per-square)
# sigma_sheet = n_s * e * mu
# R_H * sigma = (1/(n_s*e)) * (n_s*e*mu) = mu
# So ΔV_H = G * mu * <Bz> * V_bias

# But V_bias = I_bias * R_square = I_bias / (n_s * e * mu)
# So ΔV_H = G * mu * <Bz> * I_bias / (n_s * e * mu) = G * <Bz> * I_bias / (n_s * e)
# = G * S_I * I_bias * <Bz>

# Aledealat: InAs QW, w=5um, M-280, r~2um (estimated passivation), B0=55mT
print("\n--- Aledealat 2009 (InAs QW) ---")
m_aledealat = bead_moment(2.83, 0.03, 10, 55e-3)
avg_Bz_aled = compute_avg_Bz(m_aledealat, 0, 0, 2.0, 5, 5, 0.1, nxy=16, nz=4)
# S_I = 625 V/AT, I_bias = 10 uA
S_I_InAs = 625  # V/(A·T)
I_bias = 10e-6  # A
dVH_aled = 1.0 * S_I_InAs * I_bias * avg_Bz_aled
print(f"  m = {m_aledealat:.3e} A·m²")
print(f"  <Bz> = {avg_Bz_aled*1e6:.2f} uT")
print(f"  ΔV_H = {dVH_aled*1e6:.2f} uV")

# Besse 2002: Si CMOS, M-280, B0=500mT, I_bias=500uA
# Si CMOS: R_H = 6.3e-4 m³/C, n=1e22 m⁻³
# sensor size ~2.4x2.4 um (individual element), t~500nm
# distance ~ 1-2 um (passivation)
print("\n--- Besse 2002 (Si CMOS) ---")
m_besse = bead_moment(2.83, 0.03, 10, 500e-3)
avg_Bz_besse = compute_avg_Bz(m_besse, 0, 0, 2.0, 2.4, 2.4, 0.5, nxy=16, nz=4)
# R_H = 6.3e-4 m³/C, sigma = n*e*mu = 1e22 * 1.6e-19 * 0.14 = 224 S/m
# Actually for Si: mu = 1400 cm²/Vs = 0.14 m²/Vs
sigma_Si = 1e22 * e_charge * 0.14  # S/m
R_H_Si = 6.3e-4  # m³/C
I_bias_besse = 500e-6  # A
# V_bias = I_bias * R_sq, R_sq = 1/(n*e*mu*t)
t_Si = 0.5e-6  # 500 nm
R_sq_Si = 1 / (1e22 * e_charge * 0.14 * t_Si)
V_bias_besse = I_bias_besse * R_sq_Si
dVH_besse = 1.0 * R_H_Si * sigma_Si * avg_Bz_besse * V_bias_besse
print(f"  m = {m_besse:.3e} A·m²")
print(f"  <Bz> = {avg_Bz_besse*1e6:.2f} uT")
print(f"  R_sq = {R_sq_Si:.1f} Ω/sq")
print(f"  V_bias = {V_bias_besse*1e3:.2f} mV")
print(f"  ΔV_H = {dVH_besse*1e6:.2f} uV")

# Alternative: use ΔV_H = S_I * I_bias * <Bz> for 3D
# S_I = R_H/t = 6.3e-4 / 0.5e-6 = 1260 V/AT
S_I_Si = R_H_Si / t_Si
dVH_besse_alt = 1.0 * S_I_Si * I_bias_besse * avg_Bz_besse
print(f"  S_I = {S_I_Si:.1f} V/AT")
print(f"  ΔV_H (alt) = {dVH_besse_alt*1e6:.2f} uV")

# Gabureac 2013: nanocomposite, w=0.5um, 1um bead (phi~100% estimate), B0=50mT
# distance ~ 0.5um, very different sensor type
print("\n--- Gabureac 2013 (nanocomposite) ---")
# Using their custom sensor - approximate parameters
# Their sensor has R_H ~ 1e-4 m³/C (estimated from nanocomposite)
m_gab = bead_moment(1.0, 0.10, 10, 50e-3)  # 1um bead, ~10% iron oxide estimate
avg_Bz_gab = compute_avg_Bz(m_gab, 0, 0, 0.5, 0.5, 0.5, 0.05, nxy=16, nz=4)
# Very rough - their sensor parameters aren't fully specified for our model
# They report 100-500 nV signals
# Use approximate S_I ~ 100 V/AT, I_bias ~ 100 uA
S_I_gab = 100
I_bias_gab = 100e-6
dVH_gab = 1.0 * S_I_gab * I_bias_gab * avg_Bz_gab
print(f"  m = {m_gab:.3e} A·m²")
print(f"  <Bz> = {avg_Bz_gab*1e6:.2f} uT")
print(f"  ΔV_H = {dVH_gab*1e9:.1f} nV")

# ============================================================
# 4. NOISE MODEL - compute for each material at Design II
# ============================================================
print("\n" + "=" * 60)
print("NOISE MODEL - Material comparison at Design II")
print("=" * 60)

# Design II: w=10um, d_b=6um magnetite (phi=1), r=3um, B0=50mT
# First compute <Bz> for Design II
m_d2 = bead_moment(6, 1.0, 10, 50e-3)
avg_Bz_d2 = compute_avg_Bz(m_d2, 0, 0, 3, 10, 10, 1, nxy=16, nz=8)
print(f"Design II <Bz> = {avg_Bz_d2*1e6:.2f} uT")

# Materials: (name, mu_cm2Vs, n_s_or_n, is_2D, alpha_H, t_nm_for_3D)
materials = [
    ("Graphene/hBN",  40000, 1.1e15, True,  1e-5,    None),
    ("InSb QW",       42000, 5e15,   True,  5e-4,    None),
    ("CVD graphene",  3000,  5e15,   True,  1.8e-4,  None),
    ("InAs/AlSb",     22000, 1e16,   True,  3.7e-3,  None),
    ("Si CMOS",       1400,  1e22,   False, 5e-3,    500),
]

w_um = 10  # sensor width
A = (w_um * 1e-6)**2  # sensor area
I_bias = 10e-6  # 10 uA
delta_f = 1000  # Hz
f_op = 1000     # Hz
G = 1.0

print(f"\n{'Material':<16} {'mu(m²/Vs)':<12} {'R_sq(Ω)':<10} {'V_bias(mV)':<11} {'ΔV_H(mV)':<10} {'V_th(nV)':<9} {'V_1f(nV)':<9} {'V_n(nV)':<8} {'SNR':<10} {'B_min(nT/√Hz)':<14}")
print("-" * 130)

for name, mu_cgs, n, is_2D, alpha_H, t_nm in materials:
    mu_si = mu_cgs * 1e-4  # cm²/Vs -> m²/Vs

    if is_2D:
        n_s = n  # sheet carrier density, m⁻²
        R_H = 1 / (n_s * e_charge)  # m²/C (2D)
        S_I = R_H  # V/(A·T) for 2D
        R_sq = 1 / (n_s * e_charge * mu_si)  # Ω/sq
        N = n_s * A  # total carriers
        sigma_eff = n_s * e_charge * mu_si  # sheet conductance (S)
        # ΔV_H = G * mu * <Bz> * V_bias (since R_H*sigma = mu for 2D per square)
        V_bias = I_bias * R_sq
        dVH = G * mu_si * avg_Bz_d2 * V_bias
    else:
        n_vol = n  # bulk carrier density, m⁻³
        t = t_nm * 1e-9  # film thickness
        R_H_3D = 1 / (n_vol * e_charge)  # m³/C
        S_I = R_H_3D / t  # V/(A·T)
        R_sq = 1 / (n_vol * e_charge * mu_si * t)
        N = n_vol * A * t  # total carriers
        V_bias = I_bias * R_sq
        dVH = G * mu_si * avg_Bz_d2 * V_bias

    # Thermal noise
    V_th = np.sqrt(4 * kB * T * R_sq * delta_f)

    # 1/f noise
    V_1f = V_bias * np.sqrt(alpha_H / N * np.log(1 + delta_f / f_op))

    # Total noise
    V_n = np.sqrt(V_th**2 + V_1f**2)

    # SNR
    SNR = abs(dVH) / V_n

    # B_min
    B_min = V_n / (abs(S_I) * I_bias)  # T/√Hz
    B_min_nT = B_min * 1e9 / np.sqrt(delta_f)  # nT/√Hz
    # Actually B_min = V_n / (S_I * I_bias) has units of T (for bandwidth Δf)
    # B_min per √Hz = V_n/√Δf / (S_I * I_bias)
    V_n_per_sqrtHz = V_n / np.sqrt(delta_f)
    B_min_per_sqrtHz = V_n_per_sqrtHz / (abs(S_I) * I_bias)
    B_min_nT_sqrtHz = B_min_per_sqrtHz * 1e9

    print(f"{name:<16} {mu_si:<12.4f} {R_sq:<10.1f} {V_bias*1e3:<11.2f} {dVH*1e3:<10.4f} {V_th*1e9:<9.1f} {V_1f*1e9:<9.1f} {V_n*1e9:<8.1f} {SNR:<10.0f} {B_min_nT_sqrtHz:<14.1f}")

# ============================================================
# 5. CONVERGENCE STUDY
# ============================================================
print("\n" + "=" * 60)
print("CONVERGENCE STUDY - Design II")
print("=" * 60)

grids = [(4,2), (8,4), (16,8), (32,16), (64,32)]
m_conv = bead_moment(6, 1.0, 10, 50e-3)

for nxy, nz in grids:
    avg = compute_avg_Bz(m_conv, 0, 0, 3, 10, 10, 1, nxy=nxy, nz=nz)
    dVH = 1.0 * 1.25e-3 * 1040 * avg * 5
    print(f"  Grid {nxy:>3}x{nxy:>3}x{nz:>2}: <Bz> = {avg*1e6:.4f} uT, ΔV_H = {dVH*1e3:.4f} mV")

# Reference (finest grid)
avg_ref = compute_avg_Bz(m_conv, 0, 0, 3, 10, 10, 1, nxy=64, nz=32)
print(f"\n  Relative errors vs 64x64x32:")
for nxy, nz in grids[:-1]:
    avg = compute_avg_Bz(m_conv, 0, 0, 3, 10, 10, 1, nxy=nxy, nz=nz)
    err = abs(avg - avg_ref) / abs(avg_ref) * 100
    print(f"    {nxy:>3}x{nxy:>3}x{nz:>2}: {err:.3f}%")

print("\n\nDONE. Use these values to update the paper.")
