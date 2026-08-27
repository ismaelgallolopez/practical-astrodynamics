# Velocity Verlet Integration - Implementation Summary

## Overview

The Velocity Verlet integrator has been implemented with the same structure as the Euler integrator, providing a more accurate second-order integration method for orbit propagation.

## File Structure

### Fortran Source Files
```
src/fortran/
├── gravity.f90                      # Gravitational acceleration (shared)
├── velocity_verlet.f90              # Velocity Verlet integration module
└── propagate_orbit_verlet.f90       # Main propagation program for Verlet
```

### Python Analysis Scripts
```
src/python/
├── compute_position_difference_verlet.py  # Compare SGP4 vs Verlet
└── plot_cgpd_vs_timestep_verlet.py       # CGPD analysis for Verlet
```

### Automation Scripts
```
scripts/
├── run_propagation_verlet.sh        # Run Verlet propagation workflow
└── run_cgpd_analysis_verlet.sh      # Full CGPD sensitivity analysis
```

### Data Organization
```
data/
├── verlet_outputs/                  # Verlet propagation results
│   └── dt<N>s_verlet_output.txt
├── position_differences_verlet/     # Comparison statistics
│   └── dt<N>s_position_differences.npz
└── summary/
    └── cgpd_vs_timestep_verlet.npz  # CGPD analysis results
```

### Plots Organization
```
plots/
├── timestep_comparisons_verlet/     # Per-timestep comparisons
│   └── dt<N>s/
│       ├── position_difference_l2_norm.png
│       ├── keplerian_comparison_semi_major_axis.png
│       ├── keplerian_comparison_eccentricity.png
│       ├── keplerian_comparison_inclination.png
│       ├── keplerian_comparison_raan.png
│       └── keplerian_comparison_true_anomaly_arg_periapsis.png
└── summary/
    └── cgpd_vs_timestep_verlet.png  # Timestep sensitivity plot
```

## Usage

### Single Timestep Propagation
```bash
./scripts/run_propagation_verlet.sh 100
```

### Multiple Timesteps
```bash
./scripts/run_propagation_verlet.sh 10,50,100,500,1000
```

### Full CGPD Analysis
```bash
./scripts/run_cgpd_analysis_verlet.sh
```

## Method Comparison

### Euler Method (First Order)
- **Algorithm**: `y_{n+1} = y_n + h*f(t_n, y_n)`
- **Accuracy**: O(h²) per step, O(h) global
- **Files**: `euler_outputs/`, `timestep_comparisons/`

### Velocity Verlet (Second Order)
- **Algorithm**: 
  ```
  r_{n+1} = r_n + dt*v_n + 0.5*dt²*a_n
  a_{n+1} = a(r_{n+1})
  v_{n+1} = v_n + 0.5*dt*(a_n + a_{n+1})
  ```
- **Accuracy**: O(h⁴) per step, O(h²) global
- **Properties**: Symplectic (preserves phase space structure)
- **Files**: `verlet_outputs/`, `timestep_comparisons_verlet/`

## Key Features

✅ **Same interface as Euler** - Easy to compare methods
✅ **Identical workflow** - Same scripts and structure
✅ **Separate outputs** - No mixing of results
✅ **Parallel analysis** - Can run both methods simultaneously
✅ **Smart computation** - Skips existing timesteps
✅ **Complete automation** - From TLE fetch to CGPD plots

## Workflow

1. **Fetch TLE** → `data/sgp4_reference/tle.txt` (if needed)
2. **Generate SGP4** → `data/sgp4_reference/orbit_propagation.npz` (if needed)
3. **Extract Initial State** → `data/sgp4_reference/initial_state.txt`
4. **Propagate with Verlet** → `data/verlet_outputs/dt<N>s_verlet_output.txt`
5. **Compare with SGP4** → Plots and statistics
6. **CGPD Analysis** → Summary plot showing error vs timestep

## Expected Results

The Velocity Verlet method should show:
- **Better accuracy** than Euler for the same timestep
- **Smaller CGPD** values across all timesteps
- **Better energy conservation** (symplectic property)
- **Steeper error scaling** with timestep (O(h²) vs O(h))

## Comparison Commands

### Run Both Methods
```bash
# Euler
./scripts/run_propagation.sh 10,20,50,100,200,500,1000

# Velocity Verlet
./scripts/run_propagation_verlet.sh 10,20,50,100,200,500,1000
```

### Compare CGPD Plots
The two methods can be compared visually:
- Euler: `plots/summary/cgpd_vs_timestep.png`
- Verlet: `plots/summary/cgpd_vs_timestep_verlet.png`

### File Naming Convention

All Verlet files include "verlet" in the name to distinguish from Euler:
- Data files: `*_verlet_output.txt`, `*_verlet.npz`
- Plot directories: `timestep_comparisons_verlet/`
- Scripts: `*_verlet.sh`, `*_verlet.py`

This clear separation allows easy identification and prevents confusion between methods.
