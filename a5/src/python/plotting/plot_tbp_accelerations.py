#!/usr/bin/env python3
"""
Compute and plot third body perturbation (TBP) acceleration magnitudes along the orbit.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from utilities.keplerian import OrbitDataLoader
from plotting.plot_disturbance_accelerations import plot_disturbance_magnitudes, plot_disturbance_components


# Gravitational parameters
MU_SUN = 1.32712440042e20   # m^3/s^2
MU_MOON = 4.9028000660e12   # m^3/s^2
R_EARTH = 6378137.0         # m

# Load third body positions from file
def load_third_body_positions():
    """Load Sun and Moon positions from file."""
    with open('data/sgp4_reference/third_body_positions.txt', 'r') as f:
        lines = f.readlines()
    
    # Parse data lines (skip comments)
    data_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        data_lines.append(line)
    
    # First data line is Sun position and GM
    sun_data = list(map(float, data_lines[0].split()))
    sun_pos = np.array(sun_data[:3])  # X, Y, Z in meters
    
    # Second data line is Moon position and GM
    moon_data = list(map(float, data_lines[1].split()))
    moon_pos = np.array(moon_data[:3])  # X, Y, Z in meters
    
    return sun_pos, moon_pos


def compute_third_body_acceleration(positions_m, body_pos, mu_body):
    """
    Compute third body perturbation acceleration for a single body.
    
    Formula: a = μ * [(r_body - r_sat)/|r_body - r_sat|³ - r_body/|r_body|³]
    
    Args:
        positions_m: Satellite position vectors [N x 3] in meters
        body_pos: Third body position [3] in meters (geocentric)
        mu_body: Third body gravitational parameter [m³/s²]
        
    Returns:
        Acceleration vectors [N x 3] in m/s²
    """
    n_points = len(positions_m)
    accelerations = np.zeros((n_points, 3))
    
    r_body_mag = np.linalg.norm(body_pos)
    
    for i in range(n_points):
        r_sat = positions_m[i]
        r_body_sat = body_pos - r_sat
        r_body_sat_mag = np.linalg.norm(r_body_sat)
        
        # Third body acceleration formula
        term1 = r_body_sat / r_body_sat_mag**3
        term2 = body_pos / r_body_mag**3
        accelerations[i] = mu_body * (term1 - term2)
    
    return accelerations


def main():
    """Compute and plot TBP acceleration magnitudes."""
    
    print("=" * 70)
    print("THIRD BODY PERTURBATION ACCELERATION MAGNITUDES")
    print("=" * 70)
    
    # File path
    orbit_file = "data/outputs_orbit/dt10s_output.txt"
    output_dir = "plots/tbp_accelerations"
    
    # Check if file exists
    if not os.path.exists(orbit_file):
        print(f"\nError: Orbit file not found: {orbit_file}")
        print("Please run: ./src/fortran/propagate_orbit")
        return 1
    
    # Load third body positions
    print("\nLoading third body positions...")
    sun_pos, moon_pos = load_third_body_positions()
    print(f"  Sun position: [{sun_pos[0]:.6e}, {sun_pos[1]:.6e}, {sun_pos[2]:.6e}] m")
    print(f"  Sun distance: {np.linalg.norm(sun_pos)/1e9:.3f} × 10⁹ m")
    print(f"  Moon position: [{moon_pos[0]:.6e}, {moon_pos[1]:.6e}, {moon_pos[2]:.6e}] m")
    print(f"  Moon distance: {np.linalg.norm(moon_pos)/1e6:.3f} × 10⁶ m")
    
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
    
    # Compute TBP accelerations
    print("\nComputing Sun perturbation acceleration at each point...")
    acc_sun = compute_third_body_acceleration(positions_m, sun_pos, MU_SUN)
    
    print("Computing Moon perturbation acceleration at each point...")
    acc_moon = compute_third_body_acceleration(positions_m, moon_pos, MU_MOON)
    
    print("Computing total TBP acceleration...")
    acc_tbp = acc_sun + acc_moon
    
    # Compute magnitudes
    acc_sun_mag = np.linalg.norm(acc_sun, axis=1)
    acc_moon_mag = np.linalg.norm(acc_moon, axis=1)
    acc_tbp_mag = np.linalg.norm(acc_tbp, axis=1)
    
    # Compute statistics
    print(f"\nSun Acceleration Statistics:")
    print(f"  Mean:   {np.mean(acc_sun_mag):.6e} m/s²")
    print(f"  Median: {np.median(acc_sun_mag):.6e} m/s²")
    print(f"  Min:    {np.min(acc_sun_mag):.6e} m/s²")
    print(f"  Max:    {np.max(acc_sun_mag):.6e} m/s²")
    print(f"  Std:    {np.std(acc_sun_mag):.6e} m/s²")
    
    print(f"\nMoon Acceleration Statistics:")
    print(f"  Mean:   {np.mean(acc_moon_mag):.6e} m/s²")
    print(f"  Median: {np.median(acc_moon_mag):.6e} m/s²")
    print(f"  Min:    {np.min(acc_moon_mag):.6e} m/s²")
    print(f"  Max:    {np.max(acc_moon_mag):.6e} m/s²")
    print(f"  Std:    {np.std(acc_moon_mag):.6e} m/s²")
    
    print(f"\nTotal TBP Acceleration Statistics:")
    print(f"  Mean:   {np.mean(acc_tbp_mag):.6e} m/s²")
    print(f"  Median: {np.median(acc_tbp_mag):.6e} m/s²")
    print(f"  Min:    {np.min(acc_tbp_mag):.6e} m/s²")
    print(f"  Max:    {np.max(acc_tbp_mag):.6e} m/s²")
    print(f"  Std:    {np.std(acc_tbp_mag):.6e} m/s²")
    
    # Compute two-body acceleration for comparison
    print("\nComputing two-body acceleration for comparison...")
    r_mag = np.linalg.norm(positions_m, axis=1)
    MU_EARTH = 3.986004418e14  # m^3/s^2
    acc_twobody_mag = MU_EARTH / r_mag**2
    
    # Compute ratios
    ratio_sun = acc_sun_mag / acc_twobody_mag * 100
    ratio_moon = acc_moon_mag / acc_twobody_mag * 100
    ratio_tbp = acc_tbp_mag / acc_twobody_mag * 100
    
    print(f"\nSun / Two-body ratio:")
    print(f"  Mean:   {np.mean(ratio_sun):.6f}%")
    print(f"  Min:    {np.min(ratio_sun):.6f}%")
    print(f"  Max:    {np.max(ratio_sun):.6f}%")
    
    print(f"\nMoon / Two-body ratio:")
    print(f"  Mean:   {np.mean(ratio_moon):.6f}%")
    print(f"  Min:    {np.min(ratio_moon):.6f}%")
    print(f"  Max:    {np.max(ratio_moon):.6f}%")
    
    print(f"\nTotal TBP / Two-body ratio:")
    print(f"  Mean:   {np.mean(ratio_tbp):.6f}%")
    print(f"  Min:    {np.min(ratio_tbp):.6f}%")
    print(f"  Max:    {np.max(ratio_tbp):.6f}%")
    
    # Create plots
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nGenerating plots...")
    
    # Plot 1: TBP magnitude (Sun + Moon + Total)
    print("  Plot 1: TBP acceleration magnitudes...")
    fig1 = plot_disturbance_magnitudes(
        times_sec,
        {
            'Sun': acc_sun,
            'Moon': acc_moon,
            'Total TBP': acc_tbp
        },
        time_unit='hours',
        acc_unit='m/s²',
        title='Third Body Perturbation Acceleration Magnitudes',
        use_log_scale=False
    )
    filename1 = os.path.join(output_dir, 'tbp_magnitude.png')
    fig1.savefig(filename1, dpi=300, bbox_inches='tight')
    print(f"    Saved: {filename1}")
    
    # Plot 2: Total TBP components breakdown
    print("  Plot 2: Total TBP acceleration components...")
    fig2 = plot_disturbance_components(
        times_sec,
        acc_tbp,
        'Total TBP (Sun + Moon)',
        time_unit='hours',
        acc_unit='m/s²'
    )
    filename2 = os.path.join(output_dir, 'tbp_components.png')
    fig2.savefig(filename2, dpi=300, bbox_inches='tight')
    print(f"    Saved: {filename2}")
    
    # Plot 3: TBP vs altitude
    print("  Plot 3: TBP acceleration vs altitude...")
    altitudes_km = (np.linalg.norm(positions_m, axis=1) - R_EARTH) / 1000
    
    fig3, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(altitudes_km, acc_tbp_mag, c=times_sec/3600, 
                        cmap='viridis', s=10, alpha=0.6)
    ax.set_xlabel('Altitude [km]', fontsize=13)
    ax.set_ylabel('TBP Acceleration Magnitude [m/s²]', fontsize=13)
    ax.set_title('Third Body Perturbation Acceleration vs Altitude', fontsize=15, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Time [hours]', fontsize=11)
    
    # Add statistics box
    stats_text = f'Altitude Range:\n'
    stats_text += f'  Min: {np.min(altitudes_km):.2f} km\n'
    stats_text += f'  Max: {np.max(altitudes_km):.2f} km\n'
    stats_text += f'  Mean: {np.mean(altitudes_km):.2f} km\n'
    stats_text += f'\nTBP Acceleration:\n'
    stats_text += f'  Sun Mean: {np.mean(acc_sun_mag):.6e} m/s²\n'
    stats_text += f'  Moon Mean: {np.mean(acc_moon_mag):.6e} m/s²\n'
    stats_text += f'  Total Mean: {np.mean(acc_tbp_mag):.6e} m/s²'
    
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
            fontsize=9, family='monospace')
    
    plt.tight_layout()
    filename3 = os.path.join(output_dir, 'tbp_vs_altitude.png')
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
