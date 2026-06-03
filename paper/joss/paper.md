---
title: 'uFlow: A Modeling Platform for Microfluidic Hall-Effect Magnetic Bead Detection with Parametric Design Optimization'
tags:
  - microfluidics
  - Hall effect
  - biosensor
  - magnetic beads
  - JavaScript
  - WebGL
  - scientific visualization
authors:
  - name: Harshitha Govindaraju
    orcid: 0000-0000-0000-0000
    corresponding: true
    affiliation: 1
  - name: Umer Hassan
    affiliation: 1
affiliations:
  - name: Department of Electrical and Computer Engineering, Rutgers University, Piscataway, NJ, USA
    index: 1
date: 2 June 2026
bibliography: paper.bib
---

# Summary

Microfluidic Hall-effect biosensors detect superparamagnetic bead labels as the
beads flow past a thin-film Hall element in a microchannel. The detected signal
couples bead magnetization, the bead's stray-field distribution, Hall transport
in the sensor, and channel flow, across a dozen geometric, material, and
operational parameters. `uFlow` is a browser-based tool that implements a coupled
closed-form analytical model of this signal chain and runs it interactively, with
no installation, no build step, and no commercial license. The physics components
are Clausius-Mossotti bead magnetization with a volume-fraction correction for
composite beads, a point-dipole stray field, a volume-averaged Hall voltage with a
geometric correction factor, Poiseuille transport, and a Johnson-Nyquist/Hooge
$1/f$ noise framework. The model is evaluated across a database of 12 sensor
platforms spanning graphene, III-V semiconductors, Si CMOS, bismuth, and
topological insulators. The tool renders the microchannel, Hall chip, Halbach
magnet array, and flowing beads in a real-time 3D scene and plots the live Hall
voltage trace, and it exposes a parametric sweep engine, batch detection
statistics, and a built-in 2D axisymmetric magnetostatic finite-element (FEM)
solver. `uFlow` is open source under AGPL-3.0-or-later. The source is at
<https://github.com/hg293/microfluidic-hall-sensor> and the running application is
at <https://uflow.studio>.

![The `uFlow` Simulator page: parameter controls (left), the 3D scene of a bead crossing the Hall sensor inside the microchannel and Halbach array (center), and the live $\Delta V_H$ signal trace (bottom).](../figures/fig2_screenshot.png){ width=85% }

# Statement of need

Designing a microfluidic Hall-effect bead detector requires exploring a coupled
parameter space that finite-element solvers such as COMSOL Multiphysics handle
only at minutes to hours per configuration and behind a commercial license. The
companion COMSOL FEM-BEM study for this work used over 200 individual simulations
to compare three sensor geometries and four semiconductor platforms
[@govindaraju2025]. Closed-form analytical treatments exist for individual parts
of the chain, including the point-dipole stray field [@griffiths],
the planar Hall voltage [@popovic2004], and the noise-optimal sensor regime
identified by Mihajlović et al. for InAs micro-Hall sensors
[@mihajlovic2007], but no open, interactive tool couples the full signal chain for
a non-specialist.

`uFlow` is built for researchers screening sensor designs before fabrication,
assay developers setting bias and flow conditions, and reviewers or students who
need to check claimed detection limits without a FEM license. It implements the
analytical model from the companion COMSOL FEM-BEM study [@govindaraju2025] and is
benchmarked against it. The model reproduces the COMSOL Hall voltage to within
4.8% at the favorable bead-to-sensor area ratio of Design II (10 µm sensor, 6 µm
bead: 44.86 mV vs. 42.79 mV). At the off-optimum Designs I and III the
point-dipole approximation deviates by 22% (16.63 mV vs. 21.375 mV) and 16%
(2.58 mV vs. 3.056 mV). The point-dipole form is the leading term of a
multipole expansion and loses accuracy when the bead-sensor separation
approaches the bead radius ($h/r_b \sim 1$) [@griffiths]; the built-in FEM
solver quantifies this deviation for each geometry, agreeing with the dipole
model to within a few percent at $h/r_b > 3$ and diverging as $h/r_b \to 1$.
The spread tracks the bead-to-sensor area ratio
$\pi r_b^2/(w l)$: Design II (ratio 0.28) concentrates the stray-field footprint
inside the active area, Design I (ratio 0.13) under-covers the near field, and
Design III (ratio 0.03) over-averages it across a large sensor. This motivates
the built-in FEM solver, which quantifies where the dipole approximation degrades
for users working at $h/r_b \lesssim 1$. A single $\Delta V_H$ evaluation completes in
under 1 ms, so design sweeps that would take hours in COMSOL finish in seconds.

# Functionality

The physics engine exposes pure functions for the bead moment
$m = \tfrac{4}{3}\pi r_b^3 \phi \chi_{\text{eff}} B_0/\mu_0$ with
$\chi_{\text{eff}} = 3(\mu_r-1)/(\mu_r+2)$ and an explicit volume-fraction factor
$\phi$ for composite Dynabeads computed from the iron content reported by Fonnum
et al. [@fonnum2005]; the point-dipole stray field
$B_z = (\mu_0/4\pi)\,m\,(2\Delta z^2 - \Delta x^2 - \Delta y^2)/r^5$
[@griffiths]; the volume-averaged Hall voltage
$\Delta V_H = G\,R_H\,\sigma\,\langle B_z\rangle\,V_{\text{bias}}$ with
$\langle B_z\rangle$ from midpoint quadrature over the sensor volume and a
user-adjustable geometric correction $G$ for non-square Hall crosses
[@popovic2004]; Poiseuille transport with adaptive sub-stepping that caps bead
displacement at $0.4\,w_{\text{sensor}}$ per sub-step so narrow signal peaks are
sampled correctly; and a Johnson-Nyquist plus Hooge $1/f$ noise model that reports
$\Delta V_H$, the noise floor, the signal-to-noise ratio, and the minimum
detectable field. The default $16\times16\times8$ quadrature grid is converged:
for Design II it gives 44.86 mV, within 0.044% of a $64\times64\times32$
reference.

A material database holds peer-reviewed parameters for 12 sensor platforms
including CVD graphene, graphene/hBN [@dauber2015], GaAs/AlGaAs, AlGaN/GaN,
InAs/AlSb, InSb quantum wells, Si CMOS [@besse2002], bismuth, and a Bi$_2$Se$_3$
topological insulator [@saeed2024], with gate-tunable carrier density for 2D
materials. A parametric sweep engine evaluates geometry, material, bead, flow
velocity, and applied field over user-set ranges with CSV export and a multi-
material overlay of all 12 presets. Batch mode injects up to 50 beads under
Poiseuille flow and returns per-bead peak $\Delta V_H$, detection status, detection
rate, mean, and coefficient of variation. The built-in 2D axisymmetric FEM solver
solves the magnetostatic scalar-potential problem on a structured triangular mesh
with a preconditioned conjugate-gradient method, giving an independent volumetric
check on the dipole model inside the browser.

Across the 12 platforms, the signals track carrier mobility: InSb quantum wells
and graphene/hBN produce the strongest intrinsic $\Delta V_H$, while Si CMOS and
AlGaN/GaN are among the weakest. At Design II geometry the noise-model comparison
gives graphene/hBN $\Delta V_H = 0.39$ mV against Si CMOS 0.086 mV, about a factor
of 4.5. The sweep engine recovers a bead-to-sensor area-ratio optimum of 0.1-0.5;
the optimum coincides with the regime, identified by Mihajlović et al. as
noise-optimal, in which the sensor active area is comparable to the bead
footprint [@mihajlovic2007], and a flow-velocity detection window. The predicted signals are order-of-magnitude consistent with the
low-microvolt Hall transients reported by Aledealat et al., who detected
superparamagnetic beads (2.6 µm, Bangs Laboratories) flowing
through a PDMS microchannel in real time with an InAs quantum-well micro-Hall
sensor, recording a bipolar Hall transient as beads entered, covered, and left
the cross [@aledealat2009], and with the magnetic-induction changes of order
tens of microtesla measured by Besse et al. for a Si CMOS Hall sensor
[@besse2002].

# State of the field

Commercial finite-element packages reproduce the coupled physics accurately but
are slow per configuration and require a license; the companion COMSOL FEM-BEM
study [@govindaraju2025] is the validation reference here, and `uFlow` is the
open, interactive analytical counterpart that targets the regime where the
dipole model is valid and defers near-contact geometries to its own FEM check.
Prior analytical work in this field either targets a single platform, such as the
InAs noise analysis of Mihajlović et al. [@mihajlovic2007], or remains as
unreleased MATLAB [@tu2009]. Browser-based scientific simulators have shown that
WebGL and modern JavaScript engines support physics workloads previously confined
to desktop applications [@gurvich2022; @stein2023]. `uFlow` couples the analytical
modules into one interactive package, adds a cross-material noise framework and a
12-platform database, and provides the in-browser FEM solver as a reproducibility
and verification artifact.

# Acknowledgements

This work was supported by the National Science Foundation
<!-- TODO: insert NSF award number(s) before submission -->
and by the Department of Electrical and Computer Engineering at Rutgers
University.

An archived snapshot of the version described here is deposited at Zenodo
(DOI: <!-- TODO: insert Zenodo DOI once minted -->).

# References
