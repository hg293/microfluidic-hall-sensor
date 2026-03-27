# µFlow — Microfluidic Hall-Effect Sensor Simulator

## Architecture
- **Source code**: `src/index.html` (development version, human-readable)
- **Built output**: `public/index.html` (obfuscated, auto-generated — DO NOT EDIT)
- **Build script**: `build.mjs` — runs javascript-obfuscator with maximum protection
- **Deploy**: Vercel auto-deploys from `main`, runs `node build.mjs` as build command

## Development Workflow
1. Edit `src/index.html` (the clean source)
2. Run `node build.mjs` to produce obfuscated `public/index.html`
3. Test locally: `python3 -m http.server -d public 8766`
4. Commit both `src/` and `public/` — Vercel runs build on deploy

## Code Protection (added 2026-03-27)
The deployed site has these protections:
- **Password gate**: SHA-256 hashed password check (password: "hassan"), stored in sessionStorage
- **JavaScript obfuscation**: control flow flattening, dead code injection, string encryption (RC4), self-defending
- **Domain lock**: only runs on `microfluidic-hall-sensor.vercel.app` and localhost
- **Anti-debugging**: debugger traps, DevTools detection, console disabled
- **Key blocking**: F12, Ctrl+Shift+I, Ctrl+U, right-click all blocked
- **License**: All Rights Reserved (not open source)

## Key Files
- `src/index.html` — Full app source (~2972 lines, React 18 + Three.js + Canvas)
- `build.mjs` — Obfuscation build script with password gate
- `vercel.json` — Vercel deploy config with build command
- `paper/` — SoftwareX paper (LaTeX, Advances in Engineering Software)
- `papers/` — Literature library (96 catalogued, 50 PDFs)

## 5 Pages
1. Intro — Landing page
2. Simulator — 3D Three.js bead transport + live signal trace
3. Designer — 12 materials, 8 bead presets
4. Analysis — Parametric sweeps, CSV export
5. Theory — Full physics reference with equations
6. FEM Solver — 2D axisymmetric magnetostatic validation
