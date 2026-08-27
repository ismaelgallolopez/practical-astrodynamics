# Orbit Propagation with Variable Timesteps

This system allows you to propagate orbits using the Euler method with different timesteps and automatically compare results with SGP4.

## Quick Start

Run a complete propagation and analysis with one or more timesteps:

```bash
# Single timestep
./run_propagation.sh <timestep_in_seconds>

# Multiple timesteps (comma-separated, no spaces)
./run_propagation.sh <dt1>,<dt2>,<dt3>,...
```

### Examples:

```bash
# Single: 5 minute timestep
./run_propagation.sh 300

# Multiple: Run 1min, 5min, and 10min consecutively
./run_propagation.sh 60,300,600

# Multiple: Compare several timesteps at once
./run_propagation.sh 30,60,120,300,600,1200
```

## What It Does

The script automatically:
1. Compiles Fortran code once (if needed)
2. For each timestep:
   - Extracts initial state from SGP4 data
   - Runs Euler integrator
   - Generates comparison plots and saves data

## Output Files

All outputs are labeled with the timestep for easy comparison:

### Data Files:
- `data/dt<timestep>s_euler_output.txt` - Propagated trajectory
- `data/dt<timestep>s_position_differences.npz` - Difference statistics

### Plot Files:
- `plots/dt<timestep>s_position_difference_l2_norm.png` - Position error plot
- `plots/dt<timestep>s_keplerian_comparison_semi_major_axis.png`
- `plots/dt<timestep>s_keplerian_comparison_eccentricity.png`
- `plots/dt<timestep>s_keplerian_comparison_inclination.png`
- `plots/dt<timestep>s_keplerian_comparison_raan.png`
- `plots/dt<timestep>s_keplerian_comparison_true_anomaly_arg_periapsis.png`

## Comparing Different Timesteps

### Option 1: Run all at once (recommended)
```bash
./run_propagation.sh 30,60,300,600,1200
```

### Option 2: Run individually
```bash
./run_propagation.sh 30
./run_propagation.sh 60
./run_propagation.sh 300
```

Then compare the plots side-by-side to see how timestep affects accuracy!

## Manual Steps (if needed)

If you want to run steps individually:

```bash
# 1. Extract initial state with custom timestep
python extract_initial_state.py <timestep>

# 2. Compile (if needed)
gfortran gravity.f90 euler_method.f90 propagate_orbit.f90 -o propagate_orbit

# 3. Run propagator
./propagate_orbit

# 4. Generate comparison plots
python compute_position_difference.py <timestep>
```

## Files Overview

- `run_propagation.sh` - Main automation script
- `extract_initial_state.py` - Extracts initial conditions from SGP4 data
- `gravity.f90` - Gravitational acceleration function
- `euler_method.f90` - Euler integrator module
- `propagate_orbit.f90` - Main propagation program
- `compute_position_difference.py` - Comparison and plotting script
