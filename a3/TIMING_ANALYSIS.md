# Integration Timing Analysis

## Implementation

Both Euler and Velocity Verlet propagators now measure and report integration timing using Fortran's `cpu_time()` function.

### Measured Metrics

1. **Total Integration Time** - CPU time for complete orbit propagation (seconds)
2. **Time per Step** - Average time per integration step (milliseconds)

### Output Format

Timing information is included in output file headers:

```
# Orbit Propagation Results - [Method Name]
# Time step (s): 100.00
# Stop time (s): 259200.00
# Number of steps: 2593
# Integration time (s): 0.000242
# Time per step (ms): 0.000093328
# Columns: time(s) x(m) y(m) z(m) vx(m/s) vy(m/s) vz(m/s)
```

## Usage

### Run Analysis

```bash
# After running propagations
python3 src/python/analyze_integration_timing.py
```

### Output Files

- **Plot**: `plots/summary/integration_timing_comparison.png`
- **Data**: `data/summary/integration_timing.npz`

## Expected Results

### Computational Cost

- **Euler**: 1 force evaluation per step → faster
- **Velocity Verlet**: 2 force evaluations per step → ~2x slower

Typical ratio: **Verlet/Euler ≈ 1.5-2.0x**

### Scaling with Timestep

For fixed propagation duration (e.g., 72 hours):
- **Larger timestep** → fewer steps → less total time
- **Smaller timestep** → more steps → more total time

Both methods scale linearly with number of steps.

## Performance vs Accuracy Trade-off

| Method | Time Cost | Accuracy | Best Use Case |
|--------|-----------|----------|---------------|
| **Euler** | Low (1x) | O(h) | Quick results, testing |
| **Velocity Verlet** | Medium (1.5-2x) | O(h²) | Accurate propagation |

### Efficiency Comparison

For the same **accuracy** target:
- Verlet can use **larger timesteps** (due to O(h²) convergence)
- This often makes Verlet **more efficient overall**
- Despite being slower per step, fewer steps needed

Example:
- Euler at dt=10s: 25,920 steps, high accuracy
- Verlet at dt=30s: 8,640 steps, same accuracy
- Verlet total time may be **less** despite being slower per step!

## Timing Statistics

From test run with dt = 50, 100, 500 seconds:

```
Euler Method:
  Integration time range: 0.000058 - 0.000578 s
  Mean time per step: 0.000106 ms

Velocity Verlet Method:
  Integration time range: 0.000077 - 0.000979 s
  Mean time per step: 0.000159 ms

Verlet/Euler ratio: 1.50x (Verlet is slower)
```

## Interpretation

### What timing tells us:

1. **Per-step cost** - How expensive each integration step is
2. **Total runtime** - Practical wall-clock time for propagation
3. **Method comparison** - Relative computational efficiency

### Factors affecting timing:

- **Problem size** (number of steps)
- **Force evaluation complexity** (simple gravity vs perturbations)
- **Compiler optimizations** (`-O3` flag can help)
- **System load** (CPU usage by other processes)

## Optimization Tips

### For faster propagation:

1. **Use larger timesteps** (if accuracy allows)
2. **Compile with optimizations**: `gfortran -O3 ...`
3. **Choose appropriate method**:
   - Quick study → Euler
   - Accurate results → Verlet

### For timing comparisons:

1. **Run multiple times** - CPU timing has variance
2. **Clear system load** - Close other programs
3. **Use same timesteps** - Fair comparison

## Automated Analysis

The timing analysis script (`analyze_integration_timing.py`) automatically:

✅ Extracts timing from all propagation files
✅ Compares Euler vs Verlet performance
✅ Generates comparison plots
✅ Computes performance ratios
✅ Saves timing data for further analysis

## Integration with Workflows

Timing is automatically measured when running:
- `./scripts/run_propagation.sh`
- `./scripts/run_propagation_verlet.sh`
- `./scripts/run_cgpd_analysis.sh`
- `./scripts/run_cgpd_analysis_verlet.sh`

No additional steps needed - timing data is always available!
