#!/usr/bin/env python3
"""
Generate comparison plots for Verlet showing differences relative to both Euler and SGP4.
This addresses the assignment requirement to show 4 lines (2 timesteps × 2 comparisons).
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


def compute_position_differences(pos_ref, pos_test):
    """Compute L2 norm of position differences."""
    n_points = min(len(pos_ref), len(pos_test))
    pos_diff = pos_ref[:n_points] - pos_test[:n_points]
    l2_norm = np.linalg.norm(pos_diff, axis=1)
    return l2_norm, n_points


def plot_verlet_gpd_4lines(timesteps, output_dir='plots/verlet_analysis'):
    """
    Create single GPD plot with 4 lines showing:
    - Verlet vs Euler (2 timesteps)
    - Verlet vs SGP4 (2 timesteps)
    
    Args:
        timesteps: List of 2 timesteps in seconds (e.g., [100, 500])
        output_dir: Output directory for plots
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Use distinct colors and line styles for clarity
    colors = ['#1f77b4', '#ff7f0e']  # Blue and orange for the two timesteps
    
    for i, dt in enumerate(timesteps):
        # Load data
        sgp4_file = 'data/sgp4_reference/orbit_propagation.npz'
        euler_file = f'data/euler_outputs/dt{int(dt)}s_euler_output.txt'
        verlet_file = f'data/verlet_outputs/dt{int(dt)}s_verlet_output.txt'
        
        loader = OrbitDataLoader()
        times_sgp4, pos_sgp4, vel_sgp4, _ = loader.load_from_file(sgp4_file)
        times_euler, pos_euler, vel_euler, _ = loader.load_from_file(euler_file)
        times_verlet, pos_verlet, vel_verlet, _ = loader.load_from_file(verlet_file)
        
        # Convert times
        times_sgp4_sec = convert_times_to_seconds(times_sgp4)
        times_euler_sec = convert_times_to_seconds(times_euler)
        times_verlet_sec = convert_times_to_seconds(times_verlet)
        
        # Compute Verlet vs Euler
        l2_norm_euler, n_points_euler = compute_position_differences(pos_verlet, pos_euler)
        times_euler_hours = times_verlet_sec[:n_points_euler] / 3600.0
        
        # Compute Verlet vs SGP4
        l2_norm_sgp4, n_points_sgp4 = compute_position_differences(pos_verlet, pos_sgp4)
        times_sgp4_hours = times_verlet_sec[:n_points_sgp4] / 3600.0
        
        # Plot Verlet vs Euler (solid lines)
        label_euler = f'Verlet-Euler Δt={int(dt)}s'
        ax.plot(times_euler_hours, l2_norm_euler, color=colors[i], 
                linestyle='-', linewidth=2.5, label=label_euler, alpha=0.9)
        
        # Plot Verlet vs SGP4 (dashed lines)
        label_sgp4 = f'Verlet-SGP4 Δt={int(dt)}s'
        ax.plot(times_sgp4_hours, l2_norm_sgp4, color=colors[i], 
                linestyle='--', linewidth=2.5, label=label_sgp4, alpha=0.9)
    
    ax.set_xlabel('Time from Epoch [hours]', fontsize=12)
    ax.set_ylabel('Position Difference L2 Norm [km]', fontsize=12)
    ax.set_title('GPD: Velocity Verlet vs Euler and SGP4', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best', framealpha=0.95)
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/verlet_gpd_4lines.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    
    return fig


def plot_verlet_vs_euler_gpd(timesteps, output_dir='plots/verlet_analysis'):
    """
    Create GPD plot showing Verlet vs Euler for multiple timesteps.
    
    Args:
        timesteps: List of timesteps in seconds (e.g., [100, 500])
        output_dir: Output directory for plots
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, dt in enumerate(timesteps):
        # Load data
        euler_file = f'data/euler_outputs/dt{int(dt)}s_euler_output.txt'
        verlet_file = f'data/verlet_outputs/dt{int(dt)}s_verlet_output.txt'
        
        loader = OrbitDataLoader()
        times_euler, pos_euler, vel_euler, _ = loader.load_from_file(euler_file)
        times_verlet, pos_verlet, vel_verlet, _ = loader.load_from_file(verlet_file)
        
        # Convert times
        times_euler_sec = convert_times_to_seconds(times_euler)
        times_verlet_sec = convert_times_to_seconds(times_verlet)
        
        # Compute Verlet vs Euler
        l2_norm, n_points = compute_position_differences(pos_verlet, pos_euler)
        times_hours = times_verlet_sec[:n_points] / 3600.0
        
        # Plot
        label = f'Δt = {int(dt)}s'
        ax.plot(times_hours, l2_norm, color=colors[i % len(colors)], 
                linewidth=2.5, label=label, alpha=0.9)
    
    ax.set_xlabel('Time from Epoch [hours]', fontsize=12)
    ax.set_ylabel('Position Difference L2 Norm [km]', fontsize=12)
    ax.set_title('GPD: Velocity Verlet vs Euler', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best')
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/verlet_euler_gpd.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    
    return fig


def plot_verlet_vs_sgp4_gpd(timesteps, output_dir='plots/verlet_analysis'):
    """
    Create GPD plot showing Verlet vs SGP4 for multiple timesteps.
    
    Args:
        timesteps: List of timesteps in seconds (e.g., [100, 500])
        output_dir: Output directory for plots
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, dt in enumerate(timesteps):
        # Load data
        sgp4_file = 'data/sgp4_reference/orbit_propagation.npz'
        verlet_file = f'data/verlet_outputs/dt{int(dt)}s_verlet_output.txt'
        
        loader = OrbitDataLoader()
        times_sgp4, pos_sgp4, vel_sgp4, _ = loader.load_from_file(sgp4_file)
        times_verlet, pos_verlet, vel_verlet, _ = loader.load_from_file(verlet_file)
        
        # Convert times
        times_sgp4_sec = convert_times_to_seconds(times_sgp4)
        times_verlet_sec = convert_times_to_seconds(times_verlet)
        
        # Compute Verlet vs SGP4
        l2_norm, n_points = compute_position_differences(pos_verlet, pos_sgp4)
        times_hours = times_verlet_sec[:n_points] / 3600.0
        
        # Plot
        label = f'Δt = {int(dt)}s'
        ax.plot(times_hours, l2_norm, color=colors[i % len(colors)], 
                linewidth=2.5, label=label, alpha=0.9)
    
    ax.set_xlabel('Time from Epoch [hours]', fontsize=12)
    ax.set_ylabel('Position Difference L2 Norm [km]', fontsize=12)
    ax.set_title('GPD: Velocity Verlet vs SGP4', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best')
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/verlet_sgp4_gpd.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    
    return fig


def plot_verlet_position_magnitude(timesteps, output_dir='plots/verlet_analysis'):
    """
    Create position magnitude plot showing Verlet, Euler, and SGP4 for multiple timesteps.
    Uses varied colors, line styles and widths to ensure all lines are clearly distinguishable.
    
    Args:
        timesteps: List of timesteps in seconds
        output_dir: Output directory for plots
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Use very distinct colors for each line
    color_euler_100 = '#e74c3c'    # Red
    color_euler_500 = '#f39c12'    # Orange
    color_verlet_100 = '#3498db'   # Blue
    color_verlet_500 = '#2ecc71'   # Green
    
    # Plot SGP4 reference (only once) - very thick gray in background
    sgp4_file = 'data/sgp4_reference/orbit_propagation.npz'
    loader = OrbitDataLoader()
    times_sgp4, pos_sgp4, vel_sgp4, _ = loader.load_from_file(sgp4_file)
    times_sgp4_sec = convert_times_to_seconds(times_sgp4)
    times_sgp4_hours = times_sgp4_sec / 3600.0
    r_sgp4 = np.linalg.norm(pos_sgp4, axis=1)
    
    ax.plot(times_sgp4_hours, r_sgp4, color='gray', linewidth=6.0, 
            label='SGP4', alpha=0.4, zorder=1, solid_capstyle='round')
    
    # Define colors for each timestep
    colors_euler = [color_euler_100, color_euler_500]
    colors_verlet = [color_verlet_100, color_verlet_500]
    
    # Plot each timestep with very distinct styles
    for i, dt in enumerate(timesteps):
        euler_file = f'data/euler_outputs/dt{int(dt)}s_euler_output.txt'
        verlet_file = f'data/verlet_outputs/dt{int(dt)}s_verlet_output.txt'
        
        times_euler, pos_euler, vel_euler, _ = loader.load_from_file(euler_file)
        times_verlet, pos_verlet, vel_verlet, _ = loader.load_from_file(verlet_file)
        
        times_euler_sec = convert_times_to_seconds(times_euler)
        times_verlet_sec = convert_times_to_seconds(times_verlet)
        
        times_euler_hours = times_euler_sec / 3600.0
        times_verlet_hours = times_verlet_sec / 3600.0
        
        r_euler = np.linalg.norm(pos_euler, axis=1)
        r_verlet = np.linalg.norm(pos_verlet, axis=1)
        
        # Plot Euler with dotted line - distinct colors
        label_euler = f'Euler Δt={int(dt)}s'
        ax.plot(times_euler_hours, r_euler, color=colors_euler[i], 
                linestyle=':', linewidth=3.5, label=label_euler, alpha=1.0, zorder=3+i)
        
        # Plot Verlet with dashed line - distinct colors
        # Make 100s (i=0) thicker for background visibility
        label_verlet = f'Verlet Δt={int(dt)}s'
        linewidth_verlet = 5.0 if i == 0 else 3.0
        ax.plot(times_verlet_hours, r_verlet, color=colors_verlet[i], 
                linestyle='--', linewidth=linewidth_verlet, label=label_verlet, alpha=1.0, zorder=5+i)
    
    ax.set_xlabel('Time from Epoch [hours]', fontsize=13)
    ax.set_ylabel('Orbital Radius [km]', fontsize=13)
    ax.set_title('Position Magnitude Comparison: Verlet, Euler, and SGP4', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, zorder=0)
    ax.legend(fontsize=11, loc='best', framealpha=0.95, ncol=2)
    
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/verlet_position_magnitude.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_file}")
    
    return fig


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python plot_verlet_comparison.py [timestep1] [timestep2] ...")
        print("Example: python plot_verlet_comparison.py 100 500")
        return
    
    timesteps = [float(arg) for arg in sys.argv[1:]]
    
    print("=" * 70)
    print("VERLET COMPARISON PLOTS")
    print("=" * 70)
    print(f"Timesteps: {timesteps}")
    
    output_dir = 'plots/verlet_analysis'
    
    # Generate main GPD plot with 4 lines (Verlet-Euler and Verlet-SGP4 for 2 timesteps)
    print("\nGenerating Verlet GPD plot (4 lines: Verlet-Euler and Verlet-SGP4)...")
    plot_verlet_gpd_4lines(timesteps, output_dir)
    
    # Generate individual comparison plots for additional analysis
    print("\nGenerating Verlet vs Euler GPD plot...")
    plot_verlet_vs_euler_gpd(timesteps, output_dir)
    
    print("\nGenerating Verlet vs SGP4 GPD plot...")
    plot_verlet_vs_sgp4_gpd(timesteps, output_dir)
    
    # Generate position magnitude comparison plot
    print("\nGenerating Verlet position magnitude comparison plot...")
    plot_verlet_position_magnitude(timesteps, output_dir)
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
