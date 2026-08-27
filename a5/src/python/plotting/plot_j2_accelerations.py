#!/usr/bin/env python3
"""
Compute and plot J2 disturbance acceleration magnitudes along the orbit.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from utilities.keplerian import OrbitDataLoader
from plotting.plot_disturbance_accelerations import plot_disturbance_magnitudes, plot_disturbance_components


# Earth parameters
MU_EARTH = 3.986004418e14  # m^3/s^2
R_EARTH = 6378137.0        # m
J2 = 1.08262668e-3         # dimensionless


def compute_j2_acceleration(positions_m):
    """
    Compute J2 perturbation acceleration for given positions.
    
    Args:
        positions_m: Position vectors [N x 3] in meters
        
    Returns:
        Acceleration vectors [N x 3] in m/s²
    """
    n_points = len(positions_m)
    accelerations = np.zeros((n_points, 3))
    
    for i in range(n_points):
        r = positions_m[i]
        r_mag = np.linalg.norm(r)
        z2_r2 = (r[2] / r_mag)**2
        factor = 1.5 * J2 * MU_EARTH * (R_EARTH / r_mag)**2 / r_mag**3
        
        accelerations[i, 0] = factor * r[0] * (5.0 * z2_r2 - 1.0)
        accelerations[i, 1] = factor * r[1] * (5.0 * z2_r2 - 1.0)
        accelerations[i, 2] = factor * r[2] * (5.0 * z2_r2 - 3.0)
    
    return accelerations


def main():
    """Compute and plot J2 acceleration magnitudes."""
    
    print("=" * 70)
    print("J2 DISTURBANCE ACCELERATION MAGNITUDES")
    print("=" * 70)
    
    # File path
    orbit_file = "data/outputs_orbit/dt10s_output.txt"
    output_dir = "plots/j2_accelerations"
    
    # Check if file exists
    if not os.path.exists(orbit_file):
        print(f"\nError: Orbit file not found: {orbit_file}")
        print("Please run: ./src/fortran/build/propagate_orbit")
        return 1
    
    # Load orbit data
    loader = OrbitDataLoader()
    
    print(f"\nLoading orbit from: {orbit_file}")
    times, positions_km, velocities_km, _ = loader.load_from_file(orbit_file)
    print(f"  Loaded {len(times)} data points")
    
    # Convert to meters for acceleration calculation
    positions_m = positions_km * 1000.0
    
    # Convert times to seconds from start
    times_sec = times - times[0]
    
    print(f"\nTime span: {times_sec[0]:.2f} to {times_sec[-1]:.2f} seconds")
    print(f"           ({times_sec[-1]/3600:.2f} hours)")
    
    # Compute J2 accelerations
    print("\nComputing J2 acceleration at each point...")
    acc_j2 = compute_j2_acceleration(positions_m)
    
    # Compute statistics
    acc_j2_mag = np.linalg.norm(acc_j2, axis=1)
    print(f"\nJ2 Acceleration Statistics:")
    print(f"  Mean:   {np.mean(acc_j2_mag):.6e} m/s²")
    print(f"  Median: {np.median(acc_j2_mag):.6e} m/s²")
    print(f"  Min:    {np.min(acc_j2_mag):.6e} m/s²")
    print(f"  Max:    {np.max(acc_j2_mag):.6e} m/s²")
    print(f"  Std:    {np.std(acc_j2_mag):.6e} m/s²")
    
    # Compute two-body acceleration for comparison
    print("\nComputing two-body acceleration for comparison...")
    r_mag = np.linalg.norm(positions_m, axis=1)
    acc_twobody_mag = MU_EARTH / r_mag**2
    
    # Compute ratio
    ratio = acc_j2_mag / acc_twobody_mag * 100
    print(f"\nJ2 / Two-body ratio:")
    print(f"  Mean:   {np.mean(ratio):.4f}%")
    print(f"  Min:    {np.min(ratio):.4f}%")
    print(f"  Max:    {np.max(ratio):.4f}%")
    
    # Create plots
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nGenerating plots...")
    
    # Plot 1: J2 magnitude only
    print("  Plot 1: J2 acceleration magnitude...")
    fig1 = plot_disturbance_magnitudes(
        times_sec,
        {'J2 Oblateness': acc_j2},
        time_unit='hours',
        acc_unit='m/s²',
        title='J2 Disturbance Acceleration Magnitude',
        use_log_scale=False
    )
    filename1 = os.path.join(output_dir, 'j2_magnitude.png')
    fig1.savefig(filename1, dpi=300, bbox_inches='tight')
    print(f"    Saved: {filename1}")
    
    # Plot 2: J2 components breakdown
    print("  Plot 2: J2 acceleration components...")
    fig2 = plot_disturbance_components(
        times_sec,
        acc_j2,
        'J2 Oblateness',
        time_unit='hours',
        acc_unit='m/s²'
    )
    filename2 = os.path.join(output_dir, 'j2_components.png')
    fig2.savefig(filename2, dpi=300, bbox_inches='tight')
    print(f"    Saved: {filename2}")
    
    # Plot 3: J2 vs altitude (if orbit altitude varies)
    print("  Plot 3: J2 acceleration vs altitude...")
    altitudes_km = (np.linalg.norm(positions_m, axis=1) - R_EARTH) / 1000
    
    fig3, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(altitudes_km, acc_j2_mag, c=times_sec/3600, 
                        cmap='viridis', s=10, alpha=0.6)
    ax.set_xlabel('Altitude [km]', fontsize=13)
    ax.set_ylabel('J2 Acceleration Magnitude [m/s²]', fontsize=13)
    ax.set_title('J2 Acceleration vs Altitude', fontsize=15, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Time [hours]', fontsize=11)
    
    # Add statistics box
    stats_text = f'Altitude Range:\n'
    stats_text += f'  Min: {np.min(altitudes_km):.2f} km\n'
    stats_text += f'  Max: {np.max(altitudes_km):.2f} km\n'
    stats_text += f'  Mean: {np.mean(altitudes_km):.2f} km\n'
    stats_text += f'\nJ2 Acceleration:\n'
    stats_text += f'  Mean: {np.mean(acc_j2_mag):.6e} m/s²\n'
    stats_text += f'  Max: {np.max(acc_j2_mag):.6e} m/s²'
    
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
            fontsize=9, family='monospace')
    
    plt.tight_layout()
    filename3 = os.path.join(output_dir, 'j2_vs_altitude.png')
    fig3.savefig(filename3, dpi=300, bbox_inches='tight')
    print(f"    Saved: {filename3}")
    
    print("\n" + "=" * 70)
    print("PLOTTING COMPLETE")
    print("=" * 70)
    print(f"\nPlots saved to: {output_dir}/")
    print("Close the plot windows to exit.")
    
    # Show plots
    plt.show()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
