#!/usr/bin/env python3
"""
Plot total CPU time as a function of CGPD for optimized orbits.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Read the data
data_file = 'data/outputs_all/timestep_study.txt'
data = np.loadtxt(data_file, usecols=(0,1,2,3,4))  # Skip the boolean column

timesteps = data[:, 0]  # seconds
total_times = data[:, 1]  # seconds
cgpd_values = data[:, 4]  # meters

# Create figure
plt.figure(figsize=(10, 6))

# Plot CPU time vs CGPD
plt.plot(cgpd_values / 1000, total_times, 'o-', linewidth=2, markersize=8, 
         color='tab:purple', label='Optimization Performance')

# Annotate some points with timestep values
for i in [0, len(timesteps)//2, -1]:
    plt.annotate(f'dt={timesteps[i]:.2f}s', 
                xy=(cgpd_values[i]/1000, total_times[i]),
                xytext=(10, 10), textcoords='offset points',
                fontsize=9, alpha=0.7,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))

plt.xlabel('CGPD [km]', fontsize=12)
plt.ylabel('Total CPU Time [s]', fontsize=12)
plt.title('Optimization CPU Time vs CGPD\n' + 
          '(LR=5e-4, Tol=0.01m, J2+SRP+TBP enabled)', 
          fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)

plt.tight_layout()

# Save the plot
os.makedirs('plots/timestep_study', exist_ok=True)
output_file = 'plots/timestep_study/cputime_vs_cgpd.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Plot saved to: {output_file}")

# Print summary statistics
print("\n" + "="*60)
print("CPU Time vs CGPD Summary")
print("="*60)
print(f"CGPD range: {cgpd_values.min()/1000:.1f} - {cgpd_values.max()/1000:.1f} km")
print(f"CPU time range: {total_times.min():.3f} - {total_times.max():.3f} s")
print(f"\nTrade-off analysis:")
print(f"  Fastest: {total_times.min():.3f}s @ CGPD={cgpd_values[np.argmin(total_times)]/1000:.1f}km (dt={timesteps[np.argmin(total_times)]:.2f}s)")
print(f"  Best CGPD: {cgpd_values.min()/1000:.1f}km @ {total_times[np.argmin(cgpd_values)]:.3f}s (dt={timesteps[np.argmin(cgpd_values)]:.2f}s)")
print("="*60)

plt.show()
