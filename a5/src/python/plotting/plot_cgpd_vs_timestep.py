#!/usr/bin/env python3
"""
Plot CGPD of optimized orbits as a function of integration time step.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Read the data
data_file = 'data/outputs_all/timestep_study.txt'
data = np.loadtxt(data_file, usecols=(0,1,2,3,4))  # Skip the boolean column

timesteps = data[:, 0]  # seconds
cgpd_values = data[:, 4]  # meters

# Create figure
plt.figure(figsize=(10, 6))

# Plot CGPD vs timestep
plt.plot(timesteps, cgpd_values / 1000, 'o-', linewidth=2, markersize=8, 
         color='tab:blue', label='Optimized CGPD')

plt.xlabel('Integration Time Step [s]', fontsize=12)
plt.ylabel('CGPD [km]', fontsize=12)
plt.title('CGPD of Optimized Orbits vs Integration Time Step\n' + 
          '(LR=5e-4, Tol=0.01m, J2+SRP+TBP enabled)', 
          fontsize=14)
plt.grid(True, alpha=0.3)
plt.xscale('log')
plt.legend(fontsize=11)

plt.tight_layout()

# Save the plot
os.makedirs('plots/timestep_study', exist_ok=True)
output_file = 'plots/timestep_study/cgpd_vs_timestep.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Plot saved to: {output_file}")

# Print summary statistics
print("\n" + "="*60)
print("CGPD vs Time Step Summary")
print("="*60)
print(f"Time step range: {timesteps.min():.3f} - {timesteps.max():.3f} s")
print(f"CGPD range: {cgpd_values.min()/1000:.1f} - {cgpd_values.max()/1000:.1f} km")
print(f"Best CGPD: {cgpd_values.min()/1000:.1f} km at dt = {timesteps[np.argmin(cgpd_values)]:.3f} s")
print("="*60)

plt.show()
