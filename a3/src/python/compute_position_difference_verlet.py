#!/usr/bin/env python3
"""
Compute position differences between SGP4 and Verlet propagation methods.
Uses L2 norm to quantify the difference at each time step.
"""

import numpy as np
import matplotlib.pyplot as plt
from keplerian import OrbitDataLoader, OrbitPropagator
import os
import sys


def load_propagation_data(sgp4_file: str, verlet_file: str):
    """
    Load data from both SGP4 and Verlet propagators.
    
    Args:
        sgp4_file: Path to SGP4 NPZ file
        verlet_file: Path to Verlet text file
        
    Returns:
        Tuple of (times_sgp4, pos_sgp4, vel_sgp4, times_verlet, pos_verlet, vel_verlet, name_sgp4)
    """
    loader = OrbitDataLoader()
    
    # Load SGP4 data
    print(f"Loading SGP4 data from: {sgp4_file}")
    times_sgp4, pos_sgp4, vel_sgp4, name_sgp4 = loader.load_from_file(sgp4_file)
    print(f"  Loaded {len(pos_sgp4)} points")
    
    # Load Verlet data
    print(f"Loading Verlet data from: {verlet_file}")
    times_verlet, pos_verlet, vel_verlet, name_euler = loader.load_from_file(verlet_file)
    print(f"  Loaded {len(pos_verlet)} points")
    
    return times_sgp4, pos_sgp4, vel_sgp4, times_verlet, pos_verlet, vel_verlet, name_sgp4


def convert_times_to_seconds(times):
    """
    Convert time array to seconds from epoch.
    
    Args:
        times: Either Julian date array (N, 2) or seconds array (N,)
        
    Returns:
        Time in seconds from epoch
    """
    if times.ndim == 2:
        # Julian date format - convert to seconds
        jd_full = times[:, 0] + times[:, 1]
        # Convert to seconds from first epoch
        time_seconds = (jd_full - jd_full[0]) * 86400.0
    else:
        # Already in seconds format
        time_seconds = times - times[0]
    
    return time_seconds


def compute_position_differences(pos_sgp4, pos_verlet):
    """
    Compute L2 norm of position differences.
    
    Args:
        pos_sgp4: SGP4 positions [N x 3] in km
        pos_verlet: Verlet positions [M x 3] in km
        
    Returns:
        Array of L2 norms [min(N,M)] in km
    """
    # Ensure same number of points (take minimum)
    n_points = min(len(pos_sgp4), len(pos_verlet))
    
    if len(pos_sgp4) != len(pos_verlet):
        print(f"Warning: Different number of points (SGP4: {len(pos_sgp4)}, Verlet: {len(pos_verlet)})")
        print(f"Using first {n_points} points for comparison")
    
    # Compute differences
    pos_diff = pos_sgp4[:n_points] - pos_verlet[:n_points]
    
    # Compute L2 norm for each time step: ||Δr|| = sqrt(Δx² + Δy² + Δz²)
    l2_norm = np.linalg.norm(pos_diff, axis=1)
    
    return l2_norm, pos_diff


def plot_position_magnitude(times, pos_sgp4, pos_verlet, satellite_name):
    """
    Create standalone plot showing position magnitudes (orbital radius) comparison.
    
    Args:
        times: Time array in seconds
        pos_sgp4: SGP4 positions [N x 3] in km
        pos_verlet: Verlet positions [N x 3] in km
        satellite_name: Name for plot title
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Convert times to hours for plotting
    times_hours = times / 3600.0
    
    # Compute position magnitudes
    r_sgp4 = np.linalg.norm(pos_sgp4, axis=1)
    r_verlet = np.linalg.norm(pos_verlet, axis=1)
    
    ax.plot(times_hours, r_sgp4, 'b-', linewidth=1.5, label='SGP4', alpha=0.8)
    ax.plot(times_hours, r_verlet, 'r--', linewidth=1.5, label='Verlet', alpha=0.8)
    ax.set_xlabel('Time from Epoch [hours]', fontsize=12)
    ax.set_ylabel('Orbital Radius [km]', fontsize=12)
    ax.set_title(f'Position Magnitude Comparison - {satellite_name}', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    
    # Add statistics text for orbital radius
    stats_text = f'SGP4:\n'
    stats_text += f'  Mean: {np.mean(r_sgp4):.1f} km\n'
    stats_text += f'  Std:  {np.std(r_sgp4):.1f} km\n'
    stats_text += f'  Min:  {np.min(r_sgp4):.1f} km\n'
    stats_text += f'  Max:  {np.max(r_sgp4):.1f} km\n\n'
    stats_text += f'Verlet:\n'
    stats_text += f'  Mean: {np.mean(r_verlet):.1f} km\n'
    stats_text += f'  Std:  {np.std(r_verlet):.1f} km\n'
    stats_text += f'  Min:  {np.min(r_verlet):.1f} km\n'
    stats_text += f'  Max:  {np.max(r_verlet):.1f} km'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5),
            fontsize=9, family='monospace')
    
    plt.tight_layout()
    
    return fig


def plot_position_differences(times, l2_norm, pos_diff, pos_sgp4, pos_verlet, satellite_name):
    """
    Create plots showing position differences and orbital radii.
    
    Args:
        times: Time array in seconds
        l2_norm: L2 norm of position differences [km]
        pos_diff: Position difference vectors [N x 3] in km
        pos_sgp4: SGP4 positions [N x 3] in km
        pos_verlet: Verlet positions [N x 3] in km
        satellite_name: Name for plot title
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 14))
    
    # Convert times to hours for plotting
    times_hours = times / 3600.0
    
    # Plot 1: L2 norm over time
    ax1 = axes[0]
    ax1.plot(times_hours, l2_norm, 'b-', linewidth=1.5, label='L2 Norm')
    ax1.set_xlabel('Time [hours]', fontsize=12)
    ax1.set_ylabel('Position Difference L2 Norm [km]', fontsize=12)
    ax1.set_title(f'Position Difference: SGP4 vs Verlet - {satellite_name}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    
    # Add statistics text
    stats_text = f'Mean: {np.mean(l2_norm):.3f} km\n'
    stats_text += f'Max: {np.max(l2_norm):.3f} km\n'
    stats_text += f'Min: {np.min(l2_norm):.3f} km\n'
    stats_text += f'Std: {np.std(l2_norm):.3f} km\n'
    stats_text += f'Final: {l2_norm[-1]:.3f} km'
    
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             fontsize=10, family='monospace')
    
    # Plot 2: Position magnitudes (orbital radius)
    ax2 = axes[1]
    
    # Compute position magnitudes
    r_sgp4 = np.linalg.norm(pos_sgp4, axis=1)
    r_euler = np.linalg.norm(pos_verlet, axis=1)
    
    ax2.plot(times_hours, r_sgp4, 'b-', linewidth=1.5, label='SGP4', alpha=0.8)
    ax2.plot(times_hours, r_euler, 'r--', linewidth=1.5, label='Verlet', alpha=0.8)
    ax2.set_xlabel('Time [hours]', fontsize=12)
    ax2.set_ylabel('Orbital Radius [km]', fontsize=12)
    ax2.set_title('Orbital Radius Comparison', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    
    # Add statistics text for orbital radius
    stats_text2 = f'SGP4:\n'
    stats_text2 += f'  Mean: {np.mean(r_sgp4):.1f} km\n'
    stats_text2 += f'  Std:  {np.std(r_sgp4):.1f} km\n'
    stats_text2 += f'Verlet:\n'
    stats_text2 += f'  Mean: {np.mean(r_euler):.1f} km\n'
    stats_text2 += f'  Std:  {np.std(r_euler):.1f} km'
    
    ax2.text(0.02, 0.98, stats_text2, transform=ax2.transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5),
             fontsize=9, family='monospace')
    
    # Plot 3: Component-wise differences
    ax3 = axes[2]
    ax3.plot(times_hours, pos_diff[:, 0], 'r-', linewidth=1.0, label='Δx', alpha=0.7)
    ax3.plot(times_hours, pos_diff[:, 1], 'g-', linewidth=1.0, label='Δy', alpha=0.7)
    ax3.plot(times_hours, pos_diff[:, 2], 'b-', linewidth=1.0, label='Δz', alpha=0.7)
    ax3.set_xlabel('Time [hours]', fontsize=12)
    ax3.set_ylabel('Position Difference Components [km]', fontsize=12)
    ax3.set_title('Component-wise Position Differences', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    ax3.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
    
    plt.tight_layout()
    
    return fig


def print_statistics(times, l2_norm, pos_diff):
    """
    Print detailed statistics about position differences.
    
    Args:
        times: Time array in seconds
        l2_norm: L2 norm array [km]
        pos_diff: Position difference vectors [N x 3] in km
    """
    print("\n" + "=" * 70)
    print("POSITION DIFFERENCE STATISTICS")
    print("=" * 70)
    
    print("\nL2 Norm Statistics:")
    print(f"  Mean:     {np.mean(l2_norm):12.6f} km")
    print(f"  Std Dev:  {np.std(l2_norm):12.6f} km")
    print(f"  Min:      {np.min(l2_norm):12.6f} km (at t={times[np.argmin(l2_norm)]/3600:.2f} hrs)")
    print(f"  Max:      {np.max(l2_norm):12.6f} km (at t={times[np.argmax(l2_norm)]/3600:.2f} hrs)")
    print(f"  Initial:  {l2_norm[0]:12.6f} km")
    print(f"  Final:    {l2_norm[-1]:12.6f} km")
    
    print("\nComponent-wise Difference Statistics (Mean ± Std):")
    print(f"  Δx: {np.mean(pos_diff[:, 0]):10.6f} ± {np.std(pos_diff[:, 0]):10.6f} km")
    print(f"  Δy: {np.mean(pos_diff[:, 1]):10.6f} ± {np.std(pos_diff[:, 1]):10.6f} km")
    print(f"  Δz: {np.mean(pos_diff[:, 2]):10.6f} ± {np.std(pos_diff[:, 2]):10.6f} km")
    
    print("\nComponent-wise RMS:")
    print(f"  RMS(Δx): {np.sqrt(np.mean(pos_diff[:, 0]**2)):10.6f} km")
    print(f"  RMS(Δy): {np.sqrt(np.mean(pos_diff[:, 1]**2)):10.6f} km")
    print(f"  RMS(Δz): {np.sqrt(np.mean(pos_diff[:, 2]**2)):10.6f} km")
    
    # Compute growth rate
    time_hours = times / 3600.0
    duration = time_hours[-1] - time_hours[0]
    growth = l2_norm[-1] - l2_norm[0]
    growth_rate = growth / duration if duration > 0 else 0
    
    print(f"\nDifference Growth:")
    print(f"  Duration:     {duration:.2f} hours")
    print(f"  Growth:       {growth:.6f} km")
    print(f"  Growth rate:  {growth_rate:.6f} km/hour")
    print(f"  Growth rate:  {growth_rate*1000:.6f} m/hour")
    
    print("\n" + "=" * 70)


def plot_keplerian_element_comparison(times_hours, elem_euler, elem_verlet, residual, 
                                     element_name, unit, satellite_name):
    """
    Create a single plot with Euler and Verlet values on left axis, Verlet-Euler residual on right axis.
    
    Args:
        times_hours: Time array in hours
        elem_euler: Element values for Euler
        elem_verlet: Element values for Verlet
        residual: Residual (Verlet - Euler) showing improvement
        element_name: Name of the element
        unit: Unit string
        satellite_name: Satellite name for title
    
    Returns:
        Figure object
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Left y-axis: Euler and Verlet values
    ax1.set_xlabel('Time [hours]', fontsize=12)
    ax1.set_ylabel(f'{element_name} [{unit}]', fontsize=12, color='black')
    
    # Euler: Solid line
    line1 = ax1.plot(times_hours, elem_euler, color='crimson', linestyle='-', linewidth=2.5, 
                     label='Euler', alpha=0.9, zorder=2)
    # Verlet: Dashed line
    line2 = ax1.plot(times_hours, elem_verlet, color='orangered', linestyle='--', linewidth=2.5, 
                     label='Velocity Verlet', alpha=0.9, zorder=3)
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.grid(True, alpha=0.3, zorder=0)
    
    # Right y-axis: Verlet - Euler Residual (shows improvement)
    ax2 = ax1.twinx()
    ax2.set_ylabel(f'Residual (Verlet - Euler) [{unit}]', fontsize=12, color='darkgreen')
    line3 = ax2.plot(times_hours, residual, color='darkgreen', linestyle='-', linewidth=2.0, 
                     label='Residual', alpha=0.9, zorder=4)
    ax2.tick_params(axis='y', labelcolor='darkgreen')
    ax2.axhline(y=0, color='dimgray', linestyle='--', linewidth=1.0, alpha=0.5)
    
    # Ensure ax1 is rendered above ax2 so legend and text stay on top
    ax1.set_zorder(ax2.get_zorder() + 1)
    ax1.patch.set_visible(False)  # Make ax1 background transparent
    
    # Title
    ax1.set_title(f'{element_name} Comparison: Euler vs Velocity Verlet - {satellite_name}', 
                  fontsize=14, fontweight='bold')
    
    # Combined legend
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    legend = ax1.legend(lines, labels, loc='best', fontsize=10, framealpha=0.9)
    legend.set_zorder(100)
    
    # Add statistics text
    stats_text = f'Euler:\n'
    stats_text += f'  Mean: {np.mean(elem_euler):.6g} {unit}\n'
    stats_text += f'  Std:  {np.std(elem_euler):.6g} {unit}\n'
    stats_text += f'Verlet:\n'
    stats_text += f'  Mean: {np.mean(elem_verlet):.6g} {unit}\n'
    stats_text += f'  Std:  {np.std(elem_verlet):.6g} {unit}\n'
    stats_text += f'Residual:\n'
    stats_text += f'  Mean: {np.mean(residual):.6g} {unit}\n'
    stats_text += f'  RMS:  {np.sqrt(np.mean(residual**2)):.6g} {unit}'
    
    text_box = ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.95),
             fontsize=9, family='monospace')
    text_box.set_zorder(100)
    
    plt.tight_layout()
    
    return fig


def plot_keplerian_comparisons(times, pos_euler, vel_euler, pos_verlet, vel_verlet, satellite_name):
    """
    Create 5 plots comparing Keplerian elements between Euler and Verlet.
    
    Args:
        times: Time array in seconds
        pos_euler: Euler positions [N x 3] in km
        vel_euler: Euler velocities [N x 3] in km/s
        pos_verlet: Verlet positions [N x 3] in km
        vel_verlet: Verlet velocities [N x 3] in km/s
        satellite_name: Name for plot titles
    
    Returns:
        List of figure objects
    """
    print("\nComputing Keplerian elements...")
    propagator = OrbitPropagator()
    
    # Compute Keplerian elements for both
    elements_euler = propagator.cartesian_to_keplerian(pos_euler, vel_euler)
    elements_verlet = propagator.cartesian_to_keplerian(pos_verlet, vel_verlet)
    
    times_hours = times / 3600.0
    
    figures = []
    
    # 1. Semi-major axis [m]
    sma_euler = elements_euler.semi_major_axis * 1000  # km to m
    sma_verlet = elements_verlet.semi_major_axis * 1000
    sma_residual = sma_verlet - sma_euler
    
    fig1 = plot_keplerian_element_comparison(times_hours, sma_euler, sma_verlet, sma_residual,
                                            'Semi-major Axis', 'm', satellite_name)
    figures.append(('semi_major_axis', fig1))
    
    # 2. Eccentricity [dimensionless]
    ecc_euler = elements_euler.eccentricity
    ecc_verlet = elements_verlet.eccentricity
    ecc_residual = ecc_verlet - ecc_euler
    
    fig2 = plot_keplerian_element_comparison(times_hours, ecc_euler, ecc_verlet, ecc_residual,
                                            'Eccentricity', '-', satellite_name)
    figures.append(('eccentricity', fig2))
    
    # 3. Inclination [deg]
    inc_euler = np.rad2deg(elements_euler.inclination)
    inc_verlet = np.rad2deg(elements_verlet.inclination)
    inc_residual = inc_verlet - inc_euler
    
    fig3 = plot_keplerian_element_comparison(times_hours, inc_euler, inc_verlet, inc_residual,
                                            'Inclination', 'deg', satellite_name)
    figures.append(('inclination', fig3))
    
    # 4. RAAN [deg]
    raan_euler = np.rad2deg(elements_euler.raan)
    raan_verlet = np.rad2deg(elements_verlet.raan)
    raan_residual = raan_verlet - raan_euler
    
    fig4 = plot_keplerian_element_comparison(times_hours, raan_euler, raan_verlet, raan_residual,
                                            'RAAN', 'deg', satellite_name)
    figures.append(('raan', fig4))
    
    # 5. Argument of Latitude (True Anomaly + Argument of Periapsis) [deg]
    # Unwrap first to handle discontinuities, compute residual on unwrapped values, then wrap for display
    ta_aop_euler_unwrapped = np.rad2deg(np.unwrap(elements_euler.true_anomaly + elements_euler.argument_of_periapsis))
    ta_aop_verlet_unwrapped = np.rad2deg(np.unwrap(elements_verlet.true_anomaly + elements_verlet.argument_of_periapsis))
    ta_aop_residual = ta_aop_verlet_unwrapped - ta_aop_euler_unwrapped  # Compute on unwrapped values
    
    # Wrap for display
    ta_aop_euler = ta_aop_euler_unwrapped % 360.0
    ta_aop_verlet = ta_aop_verlet_unwrapped % 360.0
    
    fig5 = plot_keplerian_element_comparison(times_hours, ta_aop_euler, ta_aop_verlet, ta_aop_residual,
                                            'Argument of Latitude (u = θ + ω)', 'deg', satellite_name)
    figures.append(('true_anomaly_arg_periapsis', fig5))
    
    return figures


def save_difference_data(times, l2_norm, pos_diff, output_file='data/position_differences.npz'):
    """
    Save computed differences to file.
    
    Args:
        times: Time array in seconds
        l2_norm: L2 norm array
        pos_diff: Position difference vectors
        output_file: Output file path
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    np.savez(output_file,
             times_seconds=times,
             l2_norm=l2_norm,
             position_differences=pos_diff)
    
    print(f"\nDifference data saved to: {output_file}")


def main():
    """Main execution function."""
    # Parse command line arguments for timestep
    dt_label = ""
    dt_seconds = None
    
    if len(sys.argv) < 2:
        print("Usage: python compute_position_difference_verlet.py <timestep_seconds>")
        print("Example: python compute_position_difference_verlet.py 100")
        sys.exit(1)
    
    try:
        dt_seconds = float(sys.argv[1])
        dt_label = f"_dt{int(dt_seconds)}s"
        print(f"Using timestep label: {dt_label}")
    except ValueError:
        print(f"Error: Invalid timestep '{sys.argv[1]}'")
        sys.exit(1)
    
    print("=" * 70)
    print("POSITION DIFFERENCE ANALYSIS: SGP4 vs VELOCITY VERLET")
    print("=" * 70)
    
    # File paths - use timestep-specific SGP4 file if available, otherwise use default
    sgp4_file_dt = f'data/sgp4_reference/orbit_propagation_dt{int(dt_seconds)}s.npz'
    sgp4_file_default = 'data/sgp4_reference/orbit_propagation.npz'
    
    if os.path.exists(sgp4_file_dt):
        sgp4_file = sgp4_file_dt
        print(f"Using timestep-specific SGP4 file: {sgp4_file}")
    else:
        sgp4_file = sgp4_file_default
        print(f"Using default SGP4 file: {sgp4_file}")
        print(f"Note: Generate timestep-specific file with: python src/python/propagator_sgp4.py {int(dt_seconds)}")
    
    verlet_file = f'data/verlet_outputs/dt{int(dt_seconds)}s_verlet_output.txt' if dt_label else 'data/verlet_outputs/verlet_output.txt'
    euler_file = f'data/euler_outputs/dt{int(dt_seconds)}s_euler_output.txt' if dt_label else 'data/euler_outputs/euler_output.txt'
    
    # Check if files exist
    if not os.path.exists(verlet_file):
        print(f"\nError: Verlet output file not found: {verlet_file}")
        print("Please run the propagator first with the appropriate timestep.")
        return
    
    if not os.path.exists(euler_file):
        print(f"\nError: Euler output file not found: {euler_file}")
        print("Please run the Euler propagator first with the appropriate timestep.")
        return
    
    # Load data
    loader = OrbitDataLoader()
    times_sgp4, pos_sgp4, vel_sgp4, sat_name = loader.load_from_file(sgp4_file)
    times_verlet, pos_verlet, vel_verlet, _ = loader.load_from_file(verlet_file)
    times_euler, pos_euler, vel_euler, _ = loader.load_from_file(euler_file)
    
    # Convert times to seconds
    times_sgp4_sec = convert_times_to_seconds(times_sgp4)
    times_verlet_sec = convert_times_to_seconds(times_verlet)
    times_euler_sec = convert_times_to_seconds(times_euler)
    
    # Use the shorter time array for comparison
    n_points = min(len(times_sgp4_sec), len(times_verlet_sec), len(times_euler_sec))
    times = times_sgp4_sec[:n_points]
    
    print(f"\nComputing position differences...")
    print(f"Comparing {n_points} time points")
    
    # Compute L2 norm of differences
    l2_norm, pos_diff = compute_position_differences(pos_sgp4, pos_verlet)
    
    # Print statistics
    print_statistics(times, l2_norm, pos_diff)
    
    # Create plots
    print("\nGenerating plots...")
    os.makedirs('plots', exist_ok=True)
    
    # Use the trimmed position arrays for plotting
    fig = plot_position_differences(times, l2_norm, pos_diff, 
                                    pos_sgp4[:n_points], pos_verlet[:n_points], sat_name)
    
    # Create output directory for this timestep
    plot_dir = f'plots/timestep_comparisons_verlet/dt{int(dt_seconds)}s' if dt_label else 'plots'
    os.makedirs(plot_dir, exist_ok=True)
    
    output_plot = f'{plot_dir}/position_difference_l2_norm.png'
    fig.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_plot}")
    
    # Create and save separate position magnitude plot
    print("\nGenerating separate position magnitude plot...")
    fig_mag = plot_position_magnitude(times, pos_sgp4[:n_points], pos_verlet[:n_points], sat_name)
    output_mag = f'{plot_dir}/position_magnitude.png'
    fig_mag.savefig(output_mag, dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_mag}")
    
    # Save data
    save_difference_data(times, l2_norm, pos_diff, 
                        output_file=f'data/position_differences_verlet/dt{int(dt_seconds)}s_position_differences.npz' if dt_label else 'data/position_differences_verlet/position_differences.npz')
    
    # Create Keplerian element comparison plots
    print("\nGenerating Keplerian element comparison plots...")
    kep_figures = plot_keplerian_comparisons(times, 
                                            pos_euler[:n_points], vel_euler[:n_points],
                                            pos_verlet[:n_points], vel_verlet[:n_points],
                                            sat_name)
    
    for name, fig in kep_figures:
        filename = f'{plot_dir}/keplerian_comparison_{name}.png'
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  Saved: {filename}")
    
    # Show plot
    print("\nDisplaying plots...")
    plt.show()
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nUsage: python compute_position_difference.py [timestep_in_seconds]")
    print(f"Example: python compute_position_difference.py 300")


if __name__ == '__main__':
    main()
