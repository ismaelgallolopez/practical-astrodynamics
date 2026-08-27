#!/usr/bin/env python3
"""
Generate combined plots showing multiple timesteps for GPD and position magnitude.
"""

import numpy as np
import matplotlib.pyplot as plt
from keplerian import OrbitDataLoader
import os
import sys


def convert_times_to_seconds(times):
    """Convert time array to seconds from epoch."""
    if times.ndim == 2:
        jd_full = times[:, 0] + times[:, 1]
        time_seconds = (jd_full - jd_full[0]) * 86400.0
    else:
        time_seconds = times - times[0]
    return time_seconds


def compute_position_differences(pos_sgp4, pos_euler):
    """Compute L2 norm of position differences."""
    n_points = min(len(pos_sgp4), len(pos_euler))
    pos_diff = pos_sgp4[:n_points] - pos_euler[:n_points]
    l2_norm = np.linalg.norm(pos_diff, axis=1)
    return l2_norm, n_points


def plot_combined_gpd(timesteps, propagator='euler', satellite_name='ISS'):
    """
    Create combined GPD plot for multiple timesteps.
    
    Args:
        timesteps: List of timesteps in seconds (e.g., [100, 500])
        propagator: 'euler' or 'verlet'
        satellite_name: Satellite name
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, dt in enumerate(timesteps):
        # Load data
        sgp4_file = 'data/sgp4_reference/orbit_propagation.npz'
        if propagator == 'euler':
            prop_file = f'data/euler_outputs/dt{int(dt)}s_euler_output.txt'
        else:
            prop_file = f'data/verlet_outputs/dt{int(dt)}s_verlet_output.txt'
        
        loader = OrbitDataLoader()
        times_sgp4, pos_sgp4, vel_sgp4, name_sgp4 = loader.load_from_file(sgp4_file)
        times_prop, pos_prop, vel_prop, name_prop = loader.load_from_file(prop_file)
        
        # Convert times
        times_sgp4_sec = convert_times_to_seconds(times_sgp4)
        times_prop_sec = convert_times_to_seconds(times_prop)
        
        # Compute differences
        l2_norm, n_points = compute_position_differences(pos_sgp4, pos_prop)
        times = times_prop_sec[:n_points]
        times_hours = times / 3600.0
        
        # Plot
        label = f'Δt = {int(dt)}s'
        ax.plot(times_hours, l2_norm, color=colors[i % len(colors)], 
                linewidth=2.0, label=label, alpha=0.85)
    
    ax.set_xlabel('Time from Epoch [hours]', fontsize=12)
    ax.set_ylabel('Position Difference L2 Norm [km]', fontsize=12)
    title = f'Global Position Difference: SGP4 vs {propagator.capitalize()}'
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best')
    
    plt.tight_layout()
    
    return fig


def plot_combined_position_magnitude(timesteps, propagator='euler', satellite_name='ISS'):
    """
    Create combined position magnitude plot for multiple timesteps.
    
    Args:
        timesteps: List of timesteps in seconds (e.g., [100, 500])
        propagator: 'euler' or 'verlet'
        satellite_name: Satellite name
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Plot SGP4 reference (only once)
    sgp4_file = 'data/sgp4_reference/orbit_propagation.npz'
    loader = OrbitDataLoader()
    times_sgp4, pos_sgp4, vel_sgp4, name_sgp4 = loader.load_from_file(sgp4_file)
    times_sgp4_sec = convert_times_to_seconds(times_sgp4)
    times_sgp4_hours = times_sgp4_sec / 3600.0
    r_sgp4 = np.linalg.norm(pos_sgp4, axis=1)
    
    ax.plot(times_sgp4_hours, r_sgp4, 'k-', linewidth=2.5, label='SGP4', alpha=0.9, zorder=10)
    
    # Plot each timestep
    for i, dt in enumerate(timesteps):
        if propagator == 'euler':
            prop_file = f'data/euler_outputs/dt{int(dt)}s_euler_output.txt'
        else:
            prop_file = f'data/verlet_outputs/dt{int(dt)}s_verlet_output.txt'
        
        times_prop, pos_prop, vel_prop, name_prop = loader.load_from_file(prop_file)
        times_prop_sec = convert_times_to_seconds(times_prop)
        times_prop_hours = times_prop_sec / 3600.0
        r_prop = np.linalg.norm(pos_prop, axis=1)
        
        # Plot
        label = f'{propagator.capitalize()} Δt={int(dt)}s'
        ax.plot(times_prop_hours, r_prop, color=colors[i % len(colors)], 
                linestyle='--', linewidth=2.0, label=label, alpha=0.85)
    
    ax.set_xlabel('Time from Epoch [hours]', fontsize=12)
    ax.set_ylabel('Orbital Radius [km]', fontsize=12)
    title = f'Position Magnitude Comparison - {satellite_name}'
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best')
    
    plt.tight_layout()
    
    return fig


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python plot_combined_timesteps.py <propagator> [timestep1] [timestep2] ...")
        print("Example: python plot_combined_timesteps.py euler 100 500")
        print("Example: python plot_combined_timesteps.py verlet 100 500")
        return
    
    propagator = sys.argv[1].lower()
    if propagator not in ['euler', 'verlet']:
        print("Error: Propagator must be 'euler' or 'verlet'")
        return
    
    if len(sys.argv) < 3:
        print("Error: Please provide at least one timestep")
        return
    
    timesteps = [float(arg) for arg in sys.argv[2:]]
    
    print("=" * 70)
    print(f"COMBINED TIMESTEP PLOTS - {propagator.upper()}")
    print("=" * 70)
    print(f"Timesteps: {timesteps}")
    
    # Create output directory
    output_dir = f'plots/combined_timesteps_{propagator}'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate GPD plot
    print("\nGenerating combined GPD plot...")
    fig_gpd = plot_combined_gpd(timesteps, propagator=propagator)
    output_gpd = f'{output_dir}/gpd_combined.png'
    fig_gpd.savefig(output_gpd, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_gpd}")
    
    # Generate position magnitude plot
    print("\nGenerating combined position magnitude plot...")
    fig_mag = plot_combined_position_magnitude(timesteps, propagator=propagator)
    output_mag = f'{output_dir}/position_magnitude_combined.png'
    fig_mag.savefig(output_mag, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_mag}")
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
