# Project Structure

This document describes the organized structure of the orbit propagation analysis project.

## Directory Layout

```
a3/
├── src/                          # Source code
│   ├── fortran/                  # Fortran numerical integration
│   │   ├── gravity.f90          # Gravitational acceleration function
│   │   ├── euler_method.f90     # Euler integration module
│   │   └── propagate_orbit.f90  # Main orbit propagation program
│   │
│   └── python/                   # Python analysis and utilities
│       ├── fetch_tle.py         # Download TLE data from CelesTrak
│       ├── propagator_sgp4.py   # SGP4 orbit propagator
│       ├── extract_initial_state.py  # Extract initial conditions
│       ├── compute_position_difference.py  # Compare propagators
│       ├── plot_cgpd_vs_timestep.py  # CGPD analysis
│       ├── plot_keplerian.py    # Keplerian element plotting
│       ├── keplerian.py         # Orbital mechanics utilities
│       └── answer-sheet-sanity.py  # Validation script
│
├── scripts/                      # Automation scripts
│   ├── run_propagation.sh       # Run full propagation workflow
│   └── run_cgpd_analysis.sh     # Run CGPD sensitivity analysis
│
├── build/                        # Compiled binaries and intermediate files
│   ├── propagate_orbit          # Main executable
│   ├── *.o                      # Object files
│   └── *.mod                    # Fortran module files
│
├── data/                         # Data storage
│   ├── sgp4_reference/          # SGP4 reference data
│   │   ├── tle.txt              # TLE orbital elements
│   │   ├── orbit_propagation.npz  # SGP4 propagated orbit
│   │   └── initial_state.txt    # Initial conditions for Fortran
│   │
│   ├── euler_outputs/           # Euler propagation results
│   │   └── dt<N>s_euler_output.txt  # Orbit for each timestep
│   │
│   ├── position_differences/    # Comparison statistics
│   │   └── dt<N>s_position_differences.npz
│   │
│   └── summary/                 # Analysis summaries
│       └── cgpd_vs_timestep.npz # CGPD sensitivity data
│
├── plots/                        # Visualization outputs
│   ├── timestep_comparisons/    # Per-timestep comparisons
│   │   └── dt<N>s/              # Results for specific timestep
│   │       ├── position_difference_l2_norm.png
│   │       ├── keplerian_comparison_semi_major_axis.png
│   │       ├── keplerian_comparison_eccentricity.png
│   │       ├── keplerian_comparison_inclination.png
│   │       ├── keplerian_comparison_raan.png
│   │       └── keplerian_comparison_true_anomaly_arg_periapsis.png
│   │
│   └── summary/                 # Summary analysis plots
│       └── cgpd_vs_timestep.png # Timestep sensitivity plot
│
├── README.md                     # Main project documentation
├── PROPAGATION_README.md         # Detailed propagation guide
├── PROJECT_STRUCTURE.md          # This file
├── requirements.txt              # Python dependencies
└── .gitignore                   # Git ignore patterns
```

## Quick Start

### 1. Setup
```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Run SGP4 Propagator (if needed)
```bash
cd src/python
python3 fetch_tle.py              # Download TLE
python3 propagator_sgp4.py        # Generate reference orbit
cd ../..
```

### 3. Run Euler Propagation
```bash
# Single timestep
./scripts/run_propagation.sh 100

# Multiple timesteps
./scripts/run_propagation.sh 10,50,100,500,1000
```

### 4. Run CGPD Analysis
```bash
# Full sensitivity analysis with 14 timesteps
./scripts/run_cgpd_analysis.sh
```

## Output Organization

### Per-Timestep Results
Each timestep value creates its own directory structure:
- **Data**: `data/euler_outputs/dt<N>s_euler_output.txt`
- **Stats**: `data/position_differences/dt<N>s_position_differences.npz`
- **Plots**: `plots/timestep_comparisons/dt<N>s/*.png`

### Summary Results
- **CGPD Plot**: `plots/summary/cgpd_vs_timestep.png`
- **CGPD Data**: `data/summary/cgpd_vs_timestep.npz`

## Workflow

1. **SGP4 Reference** → `data/sgp4_reference/orbit_propagation.npz`
2. **Extract Initial** → `data/sgp4_reference/initial_state.txt`
3. **Euler Propagate** → `data/euler_outputs/dt<N>s_euler_output.txt`
4. **Compare** → `data/position_differences/dt<N>s_*.npz` + plots
5. **Analyze** → `plots/summary/cgpd_vs_timestep.png`

## Key Features

- **Organized by function**: Source, scripts, data, and plots separated
- **Timestep isolation**: Each timestep has dedicated subdirectory
- **Clean build**: Compiled files isolated in `build/`
- **Summary analysis**: High-level results in `summary/` folders
- **Easy navigation**: Clear naming conventions, sorted by timestep

## File Naming Conventions

- **Euler outputs**: `dt<timestep>s_euler_output.txt`
- **Comparisons**: `dt<timestep>s_position_differences.npz`
- **Plot folders**: `dt<timestep>s/` (contains all plots for that timestep)
- **Plot files**: Descriptive names without timestep prefix (within timestep folder)

This structure ensures:
✓ Easy comparison between different timesteps
✓ Clear separation of concerns
✓ Reproducible workflow
✓ Scalable to many timestep values
