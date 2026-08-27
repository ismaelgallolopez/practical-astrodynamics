#!/usr/bin/env python3
"""
Plot timestep sensitivity study results with three y-axes.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Read the data
data_file = 'data/outputs_all/timestep_study.txt'
# Use converters to handle overflow values shown as '**********'
def convert_float(s):
    try:
        return float(s)
    except ValueError:
        return np.nan

converters = {i: convert_float for i in range(6)}
data = np.loadtxt(data_file, usecols=(0,1,2,3,4,5), converters=converters)

timesteps = data[:, 0]  # seconds
num_steps = data[:, 1]  # number of integration steps
total_times = data[:, 2]  # seconds
iterations = data[:, 3]  # count
avg_times = data[:, 4]  # seconds per iteration
cgpd_values = data[:, 5]  # meters

# Create figure with three y-axes
fig, ax1 = plt.subplots(figsize=(15, 7))

# First y-axis: Total CPU time (left) - LOG SCALE
color1 = 'tab:blue'
ax1.set_xlabel('Integration Time Step [s]', fontsize=12)
ax1.set_ylabel('Total CPU Time [s]', color=color1, fontsize=12)
line1 = ax1.plot(timesteps, total_times, 'o-', color=color1, linewidth=2, 
                 markersize=8, label='Total CPU Time')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, alpha=0.3)
ax1.set_xscale('log')
ax1.set_yscale('log')  # Set y-axis to log scale

# Second y-axis: Number of iterations (right) - LOG SCALE
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.set_ylabel('Number of Iterations', color=color2, fontsize=12)
line2 = ax2.plot(timesteps, iterations, 's-', color=color2, linewidth=2, 
                 markersize=8, label='Iterations')
ax2.tick_params(axis='y', labelcolor=color2)
ax2.set_yscale('log')  # Set y-axis to log scale

# Third y-axis: Average time per iteration (far right)
ax3 = ax1.twinx()
# Offset the third axis
ax3.spines['right'].set_position(('outward', 60))
color3 = 'tab:green'
ax3.set_ylabel('Avg Time per Iteration [s]', color=color3, fontsize=12)
line3 = ax3.plot(timesteps, avg_times, '^-', color=color3, linewidth=2, 
                 markersize=8, label='Avg Time/Iter')
ax3.tick_params(axis='y', labelcolor=color3)

# Create legend
lines = line1 + line2 + line3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.25, 1), 
           framealpha=0.95, fontsize=9, edgecolor='gray')

plt.title('Optimization Performance vs Integration Time Step\n' + 
          f'(LR=5e-4, Tol=0.01m, J2+SRP+TBP enabled)', 
          fontsize=14, pad=20)

# Adjust layout to prevent label clipping
plt.tight_layout(rect=[0, 0, 0.78, 0.96])

# Save the plot
os.makedirs('plots/timestep_study', exist_ok=True)
output_file = 'plots/timestep_study/performance_vs_timestep.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Plot saved to: {output_file}")

# Print summary statistics
print("\n" + "="*60)
print("Timestep Study Summary")
print("="*60)
print(f"Number of steps range: {int(num_steps.min())} - {int(num_steps.max())}")
print(f"Time step range: {timesteps.min():.3f} - {timesteps.max():.3f} s")
print(f"Total time range: {total_times.min():.3f} - {total_times.max():.3f} s")
print(f"Iterations range: {int(iterations.min())} - {int(iterations.max())}")
print(f"Avg time/iter range: {avg_times.min():.6f} - {avg_times.max():.6f} s")
print(f"CGPD range: {cgpd_values.min():.1f} - {cgpd_values.max():.1f} m")
print("="*60)

# Find optimal configuration (minimize total time while maintaining low CGPD)
optimal_idx = np.argmin(total_times)
print(f"\nFastest configuration:")
print(f"  Number of steps: {int(num_steps[optimal_idx])}")
print(f"  Time step: {timesteps[optimal_idx]:.3f} s")
print(f"  Total time: {total_times[optimal_idx]:.3f} s")
print(f"  Iterations: {int(iterations[optimal_idx])}")
print(f"  CGPD: {cgpd_values[optimal_idx]:.1f} m")

plt.show()
