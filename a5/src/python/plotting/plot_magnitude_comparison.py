#!/usr/bin/env python3
"""
Plot position and velocity magnitudes for SGP4, integrated, and optimized orbits.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_orbit_data(filename):
    """Load orbit data from file."""
    data = np.loadtxt(filename, comments='#')
    times = data[:, 0]
    positions = data[:, 1:4]
    velocities = data[:, 4:7]
    return times, positions, velocities

def main():
    print("="*60)
    print("Position and Velocity Magnitudes Analysis")
    print("="*60)
    print()
    
    # Load orbit data
    print("Loading orbit data...")
    
    # SGP4 orbit
    print("  - Loading SGP4 orbit...")
    sgp4_data = np.load('data/sgp4_reference/orbit_propagation.npz')
    times_jd = sgp4_data['times_jd']
    jd_full = times_jd[:, 0] + times_jd[:, 1]
    times_sgp4 = (jd_full - jd_full[0]) * 86400.0  # seconds
    pos_sgp4 = sgp4_data['positions'] * 1000.0  # km to m
    vel_sgp4 = sgp4_data['velocities'] * 1000.0  # km/s to m/s
    
    # Integrated orbit
    print("  - Loading integrated orbit...")
    times_int, pos_int, vel_int = load_orbit_data('data/outputs_all/integrated_orbit.txt')
    
    # Optimized orbit
    print("  - Loading optimized orbit...")
    times_opt, pos_opt, vel_opt = load_orbit_data('data/outputs_all/optimized_orbit.txt')
    
    # Convert times to hours
    times_sgp4_hr = times_sgp4 / 3600.0
    times_int_hr = times_int / 3600.0
    times_opt_hr = times_opt / 3600.0
    
    # Compute magnitudes
    print()
    print("Computing magnitudes...")
    r_mag_sgp4 = np.linalg.norm(pos_sgp4, axis=1) / 1000.0  # km
    v_mag_sgp4 = np.linalg.norm(vel_sgp4, axis=1)  # m/s
    
    r_mag_int = np.linalg.norm(pos_int, axis=1) / 1000.0  # km
    v_mag_int = np.linalg.norm(vel_int, axis=1)  # m/s
    
    r_mag_opt = np.linalg.norm(pos_opt, axis=1) / 1000.0  # km
    v_mag_opt = np.linalg.norm(vel_opt, axis=1)  # m/s
    
    # Find common time range to avoid extrapolation issues
    t_max_common = min(times_sgp4[-1], times_int[-1], times_opt[-1])
    sgp4_mask = times_sgp4 <= t_max_common
    times_sgp4_common = times_sgp4[sgp4_mask]
    pos_sgp4_common = pos_sgp4[sgp4_mask]
    vel_sgp4_common = vel_sgp4[sgp4_mask]
    
    print(f"  Using common time range: 0 to {t_max_common:.1f} s ({len(times_sgp4_common)} points)")
    
    # Interpolate integrated and optimized to common SGP4 times for difference calculation
    pos_int_interp = np.array([np.interp(times_sgp4_common, times_int, pos_int[:, i]) for i in range(3)]).T
    vel_int_interp = np.array([np.interp(times_sgp4_common, times_int, vel_int[:, i]) for i in range(3)]).T
    
    pos_opt_interp = np.array([np.interp(times_sgp4_common, times_opt, pos_opt[:, i]) for i in range(3)]).T
    vel_opt_interp = np.array([np.interp(times_sgp4_common, times_opt, vel_opt[:, i]) for i in range(3)]).T
    
    # Compute difference vectors, then their magnitudes
    pos_diff_int = pos_int_interp - pos_sgp4_common
    pos_diff_opt = pos_opt_interp - pos_sgp4_common
    vel_diff_int = vel_int_interp - vel_sgp4_common
    vel_diff_opt = vel_opt_interp - vel_sgp4_common
    
    r_diff_mag_int = np.linalg.norm(pos_diff_int, axis=1) / 1000.0  # km
    r_diff_mag_opt = np.linalg.norm(pos_diff_opt, axis=1) / 1000.0  # km
    v_diff_mag_int = np.linalg.norm(vel_diff_int, axis=1)  # m/s
    v_diff_mag_opt = np.linalg.norm(vel_diff_opt, axis=1)  # m/s
    
    print()
    print("Creating plots...")
    
    # Plot 1: Position magnitude
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # Primary y-axis: position magnitudes
    ax1.plot(times_sgp4_hr, r_mag_sgp4, 'b-', label='SGP4', linewidth=2, alpha=0.8)
    ax1.plot(times_int_hr, r_mag_int, 'g--', label='Integrated', linewidth=1.5, alpha=0.7)
    ax1.plot(times_opt_hr, r_mag_opt, 'r:', label='Optimized', linewidth=1.5, alpha=0.7)
    ax1.set_xlabel('Time [hours]', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Position Magnitude [km]', fontsize=12, fontweight='bold', color='k')
    ax1.tick_params(axis='y', labelcolor='k')
    ax1.grid(True, alpha=0.3)
    
    # Secondary y-axis: difference magnitudes
    ax2 = ax1.twinx()
    times_sgp4_hr_common = times_sgp4_common / 3600.0
    ax2.plot(times_sgp4_hr_common, r_diff_mag_int, 'm-', label='Integrated - SGP4', linewidth=1.5, alpha=0.7)
    ax2.plot(times_sgp4_hr_common, r_diff_mag_opt, 'orange', linestyle='-', label='Optimized - SGP4', linewidth=1.5, alpha=0.7)
    ax2.set_ylabel('Position Difference Magnitude [km]', fontsize=12, fontweight='bold', color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')
    
    # Title
    plt.title('Position Magnitude Evolution', fontsize=14, fontweight='bold', pad=20)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
               bbox_to_anchor=(1.15, 1), framealpha=0.95, fontsize=9, 
               edgecolor='gray')
    
    # Adjust layout to prevent label clipping
    plt.tight_layout(rect=[0, 0, 0.85, 0.96])
    
    output_file = 'plots/magnitudes/position_magnitude.png'
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    
    # Print statistics
    print(f"    Position RMS difference (Integrated): {np.sqrt(np.mean(r_diff_mag_int**2)):.6f} km")
    print(f"    Position RMS difference (Optimized):  {np.sqrt(np.mean(r_diff_mag_opt**2)):.6f} km")
    
    # Plot 2: Velocity magnitude
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # Primary y-axis: velocity magnitudes
    ax1.plot(times_sgp4_hr, v_mag_sgp4, 'b-', label='SGP4', linewidth=2, alpha=0.8)
    ax1.plot(times_int_hr, v_mag_int, 'g--', label='Integrated', linewidth=1.5, alpha=0.7)
    ax1.plot(times_opt_hr, v_mag_opt, 'r:', label='Optimized', linewidth=1.5, alpha=0.7)
    ax1.set_xlabel('Time [hours]', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Velocity Magnitude [m/s]', fontsize=12, fontweight='bold', color='k')
    ax1.tick_params(axis='y', labelcolor='k')
    ax1.grid(True, alpha=0.3)
    
    # Secondary y-axis: difference magnitudes
    ax2 = ax1.twinx()
    ax2.plot(times_sgp4_hr_common, v_diff_mag_int, 'm-', label='Integrated - SGP4', linewidth=1.5, alpha=0.7)
    ax2.plot(times_sgp4_hr_common, v_diff_mag_opt, 'orange', linestyle='-', label='Optimized - SGP4', linewidth=1.5, alpha=0.7)
    ax2.set_ylabel('Velocity Difference Magnitude [m/s]', fontsize=12, fontweight='bold', color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')
    
    # Title
    plt.title('Velocity Magnitude Evolution', fontsize=14, fontweight='bold', pad=20)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
               bbox_to_anchor=(1.15, 1), framealpha=0.95, fontsize=9, 
               edgecolor='gray')
    
    # Adjust layout to prevent label clipping
    plt.tight_layout(rect=[0, 0, 0.85, 0.96])
    
    output_file = 'plots/magnitudes/velocity_magnitude.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    
    # Print statistics
    print(f"    Velocity RMS difference (Integrated): {np.sqrt(np.mean(v_diff_mag_int**2)):.6f} m/s")
    print(f"    Velocity RMS difference (Optimized):  {np.sqrt(np.mean(v_diff_mag_opt**2)):.6f} m/s")
    
    print()
    print("="*60)
    print("Analysis complete!")
    print("="*60)

if __name__ == '__main__':
    main()
