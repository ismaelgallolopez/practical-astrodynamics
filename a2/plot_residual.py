#!/usr/bin/env python3
"""
Residual analysis and visualization for Cartesian coordinate conversion.

Compares original SGP4-propagated Cartesian coordinates with back-converted
coordinates from Keplerian elements, plotting position and velocity residuals.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os


def load_data():
    """
    Load original and back-converted Cartesian coordinates.
    
    Returns:
        Tuple of (positions_og, velocities_og, positions_conv, velocities_conv, times_jd)
    """
    # Load original SGP4 propagation data
    data_og = np.load('data/orbit_propagation.npz')
    positions_og = data_og['positions']
    velocities_og = data_og['velocities']
    times_jd = data_og['times_jd']
    
    # Load back-converted Keplerian to Cartesian data
    data_conv = np.load('data/cartesian_from_keplerian.npz')
    positions_conv = data_conv['positions']
    velocities_conv = data_conv['velocities']
    
    return positions_og, velocities_og, positions_conv, velocities_conv, times_jd


def compute_residuals(positions_og, velocities_og, positions_conv, velocities_conv):
    """
    Compute residuals between original and back-converted coordinates.
    
    Args:
        positions_og: Original positions [N×3] in km
        velocities_og: Original velocities [N×3] in km/s
        positions_conv: Back-converted positions [N×3] in km
        velocities_conv: Back-converted velocities [N×3] in km/s
        
    Returns:
        Tuple of (residuals_pos, residuals_vel)
    """
    residuals_pos = positions_og - positions_conv
    residuals_vel = velocities_og - velocities_conv
    
    return residuals_pos, residuals_vel


def julian_to_time_hours(times_jd, reference_jd=None):
    """
    Convert Julian date array to hours from reference time.
    
    Args:
        times_jd: Array of shape (N, 2) containing [jd, fr] pairs
        reference_jd: Reference Julian date (if None, uses first time point)
        
    Returns:
        Time in hours from reference
    """
    jd_full = times_jd[:, 0] + times_jd[:, 1]
    
    if reference_jd is None:
        reference_jd = jd_full[0]
    
    return (jd_full - reference_jd) * 24.0


def plot_residuals_magnitude(times_hours, residuals_pos, residuals_vel):
    """
    Create plots showing residual magnitudes and individual components in linear scale.
    
    Args:
        times_hours: Time array in hours from epoch
        residuals_pos: Position residuals [N×3] in km
        residuals_vel: Velocity residuals [N×3] in km
        
    Returns:
        Figure object
    """
    # Compute magnitudes
    residuals_pos_mag = np.linalg.norm(residuals_pos, axis=1)
    residuals_vel_mag = np.linalg.norm(residuals_vel, axis=1)
    
    # Replace zeros with NaN to avoid log(0)
    pos_x = np.where(np.abs(residuals_pos[:, 0]) == 0, np.nan, np.abs(residuals_pos[:, 0]))
    pos_y = np.where(np.abs(residuals_pos[:, 1]) == 0, np.nan, np.abs(residuals_pos[:, 1]))
    pos_z = np.where(np.abs(residuals_pos[:, 2]) == 0, np.nan, np.abs(residuals_pos[:, 2]))
    pos_mag = np.where(residuals_pos_mag == 0, np.nan, residuals_pos_mag)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Position residuals with magnitude
    ax1.plot(times_hours, pos_x, 'r--', linewidth=1.2, alpha=0.7, label='|Δx|')
    ax1.plot(times_hours, pos_y, 'g--', linewidth=1.2, alpha=0.7, label='|Δy|')
    ax1.plot(times_hours, pos_z, 'b--', linewidth=1.2, alpha=0.7, label='|Δz|')
    ax1.plot(times_hours, pos_mag, 'k-', linewidth=2, label='|Δr| (magnitude)')
    ax1.set_xlabel('Time from Epoch (hours)', fontsize=12)
    ax1.set_ylabel('Position Residuals (km)', fontsize=12)
    ax1.set_title('Position Residuals: Components and Magnitude (Logarithmic Scale)', 
                  fontsize=13, fontweight='bold')
    ax1.set_yscale('log')
    ax1.grid(True, which='both', alpha=0.3)
    ax1.legend(loc='best', fontsize=10)
    
    # Add statistics box
    pos_stats = (f'Max |Δr|: {np.max(residuals_pos_mag):.3e} km\n'
                 f'Mean |Δr|: {np.mean(residuals_pos_mag):.3e} km\n'
                 f'Min |Δr|: {np.min(residuals_pos_mag):.3e} km')
    ax1.text(0.98, 0.97, pos_stats, transform=ax1.transAxes, fontsize=9,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Velocity residuals with magnitude
    vel_x = np.where(np.abs(residuals_vel[:, 0]) == 0, np.nan, np.abs(residuals_vel[:, 0]))
    vel_y = np.where(np.abs(residuals_vel[:, 1]) == 0, np.nan, np.abs(residuals_vel[:, 1]))
    vel_z = np.where(np.abs(residuals_vel[:, 2]) == 0, np.nan, np.abs(residuals_vel[:, 2]))
    vel_mag = np.where(residuals_vel_mag == 0, np.nan, residuals_vel_mag)
    
    ax2.plot(times_hours, vel_x, 'r--', linewidth=1.2, alpha=0.7, label='|Δvₓ|')
    ax2.plot(times_hours, vel_y, 'g--', linewidth=1.2, alpha=0.7, label='|Δvᵧ|')
    ax2.plot(times_hours, vel_z, 'b--', linewidth=1.2, alpha=0.7, label='|Δvᵤ|')
    ax2.plot(times_hours, vel_mag, 'k-', linewidth=2, label='|Δv| (magnitude)')
    ax2.set_xlabel('Time from Epoch (hours)', fontsize=12)
    ax2.set_ylabel('Velocity Residuals (km/s)', fontsize=12)
    ax2.set_title('Velocity Residuals: Components and Magnitude (Logarithmic Scale)', 
                  fontsize=13, fontweight='bold')
    ax2.set_yscale('log')
    ax2.grid(True, which='both', alpha=0.3)
    ax2.legend(loc='best', fontsize=10)
    
    # Add statistics box
    vel_stats = (f'Max |Δv|: {np.max(residuals_vel_mag):.3e} km/s\n'
                 f'Mean |Δv|: {np.mean(residuals_vel_mag):.3e} km/s\n'
                 f'Min |Δv|: {np.min(residuals_vel_mag):.3e} km/s')
    ax2.text(0.98, 0.97, vel_stats, transform=ax2.transAxes, fontsize=9,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    return fig


def plot_residuals_comparison(times_hours, residuals_pos, residuals_vel):
    """
    Create a 2x3 subplot grid showing each component separately.
    
    Args:
        times_hours: Time array in hours from epoch
        residuals_pos: Position residuals [N×3] in km
        residuals_vel: Velocity residuals [N×3] in km
        
    Returns:
        Figure object
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    components = ['X', 'Y', 'Z']
    colors = ['red', 'green', 'blue']
    
    # Position residuals
    for i in range(3):
        ax = axes[0, i]
        pos_component = np.where(np.abs(residuals_pos[:, i]) == 0, np.nan, np.abs(residuals_pos[:, i]))
        ax.plot(times_hours, pos_component, color=colors[i], 
                linewidth=1.5, label=f'|Δ{components[i].lower()}|')
        ax.set_xlabel('Time from Epoch (hours)', fontsize=11)
        ax.set_ylabel(f'|Δ{components[i].lower()}| (km)', fontsize=11)
        ax.set_title(f'Position Residual: {components[i]}-component', fontsize=12, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, which='both', alpha=0.3)
        ax.legend(loc='best', fontsize=10)
        
        # Add statistics
        max_val = np.max(np.abs(residuals_pos[:, i]))
        mean_val = np.mean(np.abs(residuals_pos[:, i]))
        ax.text(0.95, 0.95, f'Max: {max_val:.2e}\nMean: {mean_val:.2e}',
                transform=ax.transAxes, fontsize=9,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    # Velocity residuals
    for i in range(3):
        ax = axes[1, i]
        vel_component = np.where(np.abs(residuals_vel[:, i]) == 0, np.nan, np.abs(residuals_vel[:, i]))
        ax.plot(times_hours, vel_component, color=colors[i], 
                linewidth=1.5, label=f'|Δv{components[i].lower()}|')
        ax.set_xlabel('Time from Epoch (hours)', fontsize=11)
        ax.set_ylabel(f'|Δv{components[i].lower()}| (km/s)', fontsize=11)
        ax.set_title(f'Velocity Residual: {components[i]}-component', fontsize=12, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, which='both', alpha=0.3)
        ax.legend(loc='best', fontsize=10)
        
        # Add statistics
        max_val = np.max(np.abs(residuals_vel[:, i]))
        mean_val = np.mean(np.abs(residuals_vel[:, i]))
        ax.text(0.95, 0.95, f'Max: {max_val:.2e}\nMean: {mean_val:.2e}',
                transform=ax.transAxes, fontsize=9,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    plt.suptitle('Component-wise Residual Analysis: Original vs Back-converted Cartesian Orbit',
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    return fig


def print_residual_statistics(residuals_pos, residuals_vel):
    """
    Print detailed residual statistics.
    
    Args:
        residuals_pos: Position residuals [N×3] in km
        residuals_vel: Velocity residuals [N×3] in km/s
    """
    residuals_pos_mag = np.linalg.norm(residuals_pos, axis=1)
    residuals_vel_mag = np.linalg.norm(residuals_vel, axis=1)
    
    print("\n" + "=" * 70)
    print("RESIDUAL ANALYSIS: ORIGINAL vs BACK-CONVERTED CARTESIAN ORBIT")
    print("=" * 70)
    
    print("\nPosition Residuals (km):")
    print(f"  X-component:")
    print(f"    Mean: {np.mean(residuals_pos[:, 0]):12.6e} km")
    print(f"    Std:  {np.std(residuals_pos[:, 0]):12.6e} km")
    print(f"    Max:  {np.max(np.abs(residuals_pos[:, 0])):12.6e} km")
    
    print(f"  Y-component:")
    print(f"    Mean: {np.mean(residuals_pos[:, 1]):12.6e} km")
    print(f"    Std:  {np.std(residuals_pos[:, 1]):12.6e} km")
    print(f"    Max:  {np.max(np.abs(residuals_pos[:, 1])):12.6e} km")
    
    print(f"  Z-component:")
    print(f"    Mean: {np.mean(residuals_pos[:, 2]):12.6e} km")
    print(f"    Std:  {np.std(residuals_pos[:, 2]):12.6e} km")
    print(f"    Max:  {np.max(np.abs(residuals_pos[:, 2])):12.6e} km")
    
    print(f"  Magnitude:")
    print(f"    Mean: {np.mean(residuals_pos_mag):12.6e} km")
    print(f"    Std:  {np.std(residuals_pos_mag):12.6e} km")
    print(f"    Max:  {np.max(residuals_pos_mag):12.6e} km")
    print(f"    Min:  {np.min(residuals_pos_mag):12.6e} km")
    
    print("\nVelocity Residuals (km/s):")
    print(f"  X-component:")
    print(f"    Mean: {np.mean(residuals_vel[:, 0]):12.6e} km/s")
    print(f"    Std:  {np.std(residuals_vel[:, 0]):12.6e} km/s")
    print(f"    Max:  {np.max(np.abs(residuals_vel[:, 0])):12.6e} km/s")
    
    print(f"  Y-component:")
    print(f"    Mean: {np.mean(residuals_vel[:, 1]):12.6e} km/s")
    print(f"    Std:  {np.std(residuals_vel[:, 1]):12.6e} km/s")
    print(f"    Max:  {np.max(np.abs(residuals_vel[:, 1])):12.6e} km/s")
    
    print(f"  Z-component:")
    print(f"    Mean: {np.mean(residuals_vel[:, 2]):12.6e} km/s")
    print(f"    Std:  {np.std(residuals_vel[:, 2]):12.6e} km/s")
    print(f"    Max:  {np.max(np.abs(residuals_vel[:, 2])):12.6e} km/s")
    
    print(f"  Magnitude:")
    print(f"    Mean: {np.mean(residuals_vel_mag):12.6e} km/s")
    print(f"    Std:  {np.std(residuals_vel_mag):12.6e} km/s")
    print(f"    Max:  {np.max(residuals_vel_mag):12.6e} km/s")
    print(f"    Min:  {np.min(residuals_vel_mag):12.6e} km/s")
    
    print("\n" + "=" * 70)


def main():
    """Main execution function."""
    print("=" * 70)
    print("RESIDUAL ORBIT ANALYSIS: ORIGINAL vs BACK-CONVERTED CARTESIAN")
    print("=" * 70)
    
    # Load data
    print("\n1. Loading data...")
    positions_og, velocities_og, positions_conv, velocities_conv, times_jd = load_data()
    print(f"   Number of data points: {len(positions_og)}")
    
    # Compute residuals
    print("\n2. Computing residuals...")
    residuals_pos, residuals_vel = compute_residuals(
        positions_og, velocities_og, positions_conv, velocities_conv
    )
    
    # Print statistics
    print_residual_statistics(residuals_pos, residuals_vel)
    
    # Convert times to hours
    times_hours = julian_to_time_hours(times_jd)
    print(f"\n3. Time span: {times_hours[0]:.2f} to {times_hours[-1]:.2f} hours")
    
    # Generate plots
    print("\n4. Generating plots...")
    
    # Ensure plots directory exists
    os.makedirs('plots', exist_ok=True)
    
    # Plot 1: Magnitude and components comparison
    print("   Creating plot: magnitude and components comparison...")
    fig1 = plot_residuals_magnitude(times_hours, residuals_pos, residuals_vel)
    filename1 = 'plots/residual_magnitude.png'
    fig1.savefig(filename1, dpi=300, bbox_inches='tight')
    print(f"   Saved: {filename1}")
    
    # Plot 2: Individual component analysis
    print("   Creating plot: individual component analysis grid...")
    fig2 = plot_residuals_comparison(times_hours, residuals_pos, residuals_vel)
    filename2 = 'plots/residual_grid.png'
    fig2.savefig(filename2, dpi=300, bbox_inches='tight')
    print(f"   Saved: {filename2}")
    
    print("\n" + "=" * 70)
    print("RESIDUAL ORBIT ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nPlot filenames:")
    print(f"  - {filename1}")
    print(f"  - {filename2}")
    print("=" * 70)


if __name__ == "__main__":
    main()
