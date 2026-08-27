# Integration Methods Comparison

This project implements two numerical integration methods for orbit propagation, allowing direct comparison of their accuracy and performance.

## Quick Start

### Run Euler Method
```bash
./scripts/run_propagation.sh 10,50,100,500,1000
./scripts/run_cgpd_analysis.sh
```

### Run Velocity Verlet Method
```bash
./scripts/run_propagation_verlet.sh 10,50,100,500,1000
./scripts/run_cgpd_analysis_verlet.sh
```

## File Organization

| Aspect | Euler | Velocity Verlet |
|--------|-------|-----------------|
| **Source** | `src/fortran/euler_method.f90` | `src/fortran/velocity_verlet.f90` |
| **Main Program** | `propagate_orbit.f90` | `propagate_orbit_verlet.f90` |
| **Executable** | `build/propagate_orbit` | `build/propagate_orbit_verlet` |
| **Data Output** | `data/euler_outputs/` | `data/verlet_outputs/` |
| **Comparisons** | `data/position_differences/` | `data/position_differences_verlet/` |
| **Plots** | `plots/timestep_comparisons/` | `plots/timestep_comparisons_verlet/` |
| **CGPD Plot** | `plots/summary/cgpd_vs_timestep.png` | `plots/summary/cgpd_vs_timestep_verlet.png` |
| **Run Script** | `scripts/run_propagation.sh` | `scripts/run_propagation_verlet.sh` |
| **Analysis Script** | `scripts/run_cgpd_analysis.sh` | `scripts/run_cgpd_analysis_verlet.sh` |

## Method Characteristics

### Euler Method
- **Order**: First order (O(h))
- **Accuracy**: Moderate, decreases linearly with timestep
- **Stability**: Can drift in energy
- **Computation**: 1 force evaluation per step
- **Best for**: Quick results, testing, large timesteps acceptable

### Velocity Verlet
- **Order**: Second order (O(h²))
- **Accuracy**: High, decreases quadratically with timestep
- **Stability**: Symplectic, conserves energy better
- **Computation**: 2 force evaluations per step
- **Best for**: Accurate long-term propagation, small timesteps

## Expected Performance

For the same timestep:
- Verlet should have **smaller position errors**
- Verlet should have **better energy conservation**
- Verlet should show **O(h²)** error scaling vs Euler's **O(h)**

## Comparing Results

### Visual Comparison
```bash
# View CGPD plots side by side
xdg-open plots/summary/cgpd_vs_timestep.png
xdg-open plots/summary/cgpd_vs_timestep_verlet.png
```

### Data Comparison
```python
import numpy as np
import matplotlib.pyplot as plt

# Load CGPD data
euler_data = np.load('data/summary/cgpd_vs_timestep.npz')
verlet_data = np.load('data/summary/cgpd_vs_timestep_verlet.npz')

# Plot comparison
plt.figure(figsize=(10, 6))
plt.loglog(euler_data['timesteps'], euler_data['cgpd'], 'o-', label='Euler', linewidth=2)
plt.loglog(verlet_data['timesteps'], verlet_data['cgpd'], 's-', label='Velocity Verlet', linewidth=2)
plt.xlabel('Time Step (s)')
plt.ylabel('CGPD (km)')
plt.title('Integration Method Comparison')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('plots/summary/methods_comparison.png', dpi=300)
```

## Workflow Diagram

```
TLE Data (CelesTrak)
    ↓
SGP4 Reference Orbit
    ↓
Initial Conditions
    ├─→ Euler Integration → euler_outputs/ → Comparison → CGPD Analysis
    └─→ Verlet Integration → verlet_outputs/ → Comparison → CGPD Analysis
```

## Recommendations

- **Learning/Testing**: Start with Euler (faster compilation, simpler)
- **Production/Accuracy**: Use Velocity Verlet (better accuracy, energy conservation)
- **Comparison Studies**: Run both methods with same timesteps
- **Large Timesteps (>100s)**: Velocity Verlet advantage is significant
- **Small Timesteps (<10s)**: Both methods may give similar results (but Verlet slower)

## Notes

- Both methods share the same gravity model (`gravity.f90`)
- Both use the same SGP4 reference for comparison
- Both generate identical plot types for easy comparison
- File naming clearly distinguishes the methods (e.g., `euler_output` vs `verlet_output`)
