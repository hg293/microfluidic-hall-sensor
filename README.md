# µFlow

An interactive browser-based 3D simulator for microfluidic Hall-effect detection of superparamagnetic magnetic beads.

**Live application:** https://microfluidic-hall-sensor.vercel.app

µFlow couples four analytical physics modules (Clausius–Mossotti bead magnetization with volume-fraction correction, point-dipole stray field, volume-averaged Hall voltage with geometric correction, and Poiseuille flow with adaptive sub-stepping) and a thermal / 1/f noise framework across a database of 12 Hall-sensor platforms. The analytical model reproduces COMSOL FEM-BEM benchmarks within 6% for three validated sensor designs. A built-in 2D axisymmetric magnetostatic FEM solver provides an independent volumetric-field check on the dipole approximation.

The entire application is a single HTML file built on React 18 and Three.js r160. It runs in any modern browser with WebGL 2 support, requires no installation, no build environment, and no commercial license.

---

## Features

- **Real-time 3D scene** (Three.js r160): PDMS microchannel, Hall sensor chip, cylindrical Halbach magnet array, animated beads under Poiseuille flow.
- **Live signal trace** of the Hall voltage ΔV_H as each bead crosses the sensor.
- **12 sensor material presets** spanning graphene (CVD, hBN-encapsulated, SiC), III–V (GaAs/AlGaAs, AlGaN/GaN, InAs/AlSb, InSb QW, InSb MBE, InAs film), Si CMOS, bismuth, and Bi₂Se₃ topological insulators. Gate-tunable 2D materials support a custom V_g sweep.
- **8 magnetic bead presets** including Dynabeads MyOne, M-280, M-450 with experimentally measured iron volume fractions, plus pure-magnetite reference beads.
- **Parametric sweep engine** with 1D and 2D sweeps across geometry, material, bead, flow velocity, and applied field. CSV export.
- **Batch mode** for per-bead detection statistics (mean, standard deviation, coefficient of variation, detection rate) over up to 50 beads in Poiseuille flow.
- **Built-in 2D axisymmetric FEM solver** for the magnetostatic Maxwell equation, using linear triangular elements and a preconditioned conjugate gradient solver.
- **Noise model** with Johnson–Nyquist thermal noise and Hooge 1/f noise, reporting SNR and the minimum detectable field B_min.

---

## Quick start

### Option 1: Use the live application

Open https://microfluidic-hall-sensor.vercel.app in any desktop browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+). A mobile notice is shown on small screens, since the 3D simulator requires a desktop or laptop.

### Option 2: Run locally

Clone the repository and serve the `public/` directory over HTTP:

```bash
git clone https://github.com/hg293/microfluidic-hall-sensor.git
cd microfluidic-hall-sensor
node build.mjs                                # copies src/index.html to public/index.html
python3 -m http.server -d public 8766         # serves at http://localhost:8766
```

Then open http://localhost:8766 in a desktop browser.

### Development

Edit `src/index.html` directly (single-file React + Three.js application, approximately 3000 lines). Run `node build.mjs` to copy the source to `public/index.html`. There is no bundler, no transpilation, and no package manager required at build time. Dependencies (React 18 UMD, Three.js r160) are loaded from CDN at runtime.

---

## Architecture

| Layer | Implementation |
|-------|---------------|
| UI framework | React 18 (UMD, loaded from CDN) |
| 3D rendering | Three.js r160 with WebGL 2 |
| 2D charts and FEM mesh | HTML5 Canvas 2D |
| Physics engine | Pure JavaScript functions (`beadMoment`, `dipBz`, `volumeAvgBz`, `flowVelocity`, `computeMatProps`) |
| Material and bead libraries | Static JavaScript objects with peer-reviewed parameter values |
| State management | React `useState` / `useEffect` / `useRef` / `useMemo` |
| Build step | `build.mjs` (single-file copy from `src/` to `public/`) |
| Deploy | Vercel, serving `public/index.html` |

The simulator exposes five pages: an Intro landing page, a 3D Simulator, a Designer page for material and bead parameter definition, an Analysis page for parametric sweeps with CSV export, a Theory page documenting the governing equations, and a built-in 2D axisymmetric FEM Solver page.

---

## Physics summary

Bead magnetic moment from the Clausius–Mossotti effective susceptibility:

```
m = (4/3) π r_b³ · φ · χ_eff · B₀ / μ₀,   χ_eff = 3(μ_r − 1) / (μ_r + 2)
```

with an explicit volume-fraction factor φ for composite beads (computed from iron content reported by Fonnum et al., 2005).

Point-dipole stray field along the channel axis:

```
B_z(Δx, Δy, Δz) = (μ₀ / 4π) · m · (2Δz² − Δx² − Δy²) / r⁵
```

Volume-averaged Hall voltage with geometric correction factor G:

```
ΔV_H = G · R_H · σ · ⟨B_z⟩ · V_bias
```

where ⟨B_z⟩ is computed by numerical quadrature over the sensor active volume.

Bead trajectories under Poiseuille flow in a high-aspect-ratio channel:

```
v(y) = (3/2) · v_mean · [1 − (2y/H − 1)²]
```

with adaptive sub-stepping that caps bead displacement per sub-step at 0.4 × sensor width.

Noise model: total noise V_n = √(V_th² + V_{1/f}²) with Johnson noise V_th = √(4 k_B T R_□ Δf) and Hooge 1/f noise V_{1/f} = V_bias √[(α_H / N) ln(1 + Δf / f_op)]. SNR = |ΔV_H| / V_n; minimum detectable field B_min = V_n / (|S_I| · I_bias).

Full derivations and references are on the in-app Theory page. The SoftwareX manuscript and bibliography live on the `main` branch under `paper/`.

---

## Validation

The analytical model has been validated against:

- **COMSOL FEM-BEM** simulations of three sensor designs (5×5, 10×10, 50×50 µm) from Govindaraju and Hassan, *Sensors and Actuators A: Physical*, vol. 393, 2025. Relative error stays below 6%.
- **Built-in 2D axisymmetric FEM solver** for direct comparison of the dipole approximation with a full volumetric magnetostatic solve. Agreement within 2% for h/R > 3, widening to 5–8% near contact (h/R ≈ 1).
- **Published experimental detections**: Aledealat et al., 2009 (InAs quantum-well µ-Hall + M-280 Dynabeads), Besse et al., 2002 (Si CMOS + M-280), Gabureac et al., 2013 (nanocomposite + 1 µm beads). Signal magnitudes and bipolar waveform shapes match reported values.

---

## Citation

If you use µFlow in your research, please cite:

> Govindaraju, H. and Hassan, U. *µFlow: An interactive browser-based 3D simulator for microfluidic Hall-effect magnetic bead detection.* SoftwareX (in preparation, 2026).

And the companion COMSOL FEM-BEM study that the analytical model is validated against:

> Govindaraju, H. and Hassan, U. *Sensors and Actuators A: Physical*, vol. 393, 2025.

---

## Code metadata

| Nr. | Description | Value |
|-----|-------------|-------|
| C1  | Current code version | v1.0 |
| C2  | Repository | https://github.com/hg293/microfluidic-hall-sensor |
| C3  | Legal Code License | MIT |
| C4  | Code versioning system | git |
| C5  | Languages, tools, services | JavaScript (ES2020), HTML5, CSS3, React 18 (UMD), Three.js r160 (WebGL 2), HTML5 Canvas 2D |
| C6  | Compilation requirements / dependencies | Modern web browser with WebGL 2 (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+). No installation or server required. |
| C7  | Developer documentation | This file (`README.md`) |
| C8  | Support email | harshitha.govindaraju@rutgers.edu |

---

## Authors

- **Harshitha Govindaraju** (corresponding author) — Department of Electrical and Computer Engineering, Rutgers University. `harshitha.govindaraju@rutgers.edu`
- **Umer Hassan** — Department of Electrical and Computer Engineering, Rutgers University. `umer.hassan@rutgers.edu`

## Acknowledgements

This work was supported by the Department of Electrical and Computer Engineering at Rutgers University and by the National Science Foundation under Award Nos. 2053149 and 2329761.

## License

MIT — see [`LICENSE.txt`](LICENSE.txt).
