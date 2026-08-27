#!/usr/bin/env python3
"""
Reusable plotting function for Keplerian elements and their residuals.

This module provides a function to compare two orbits (disturbed vs undisturbed)
by plotting their Keplerian elements on one axis and the differences on another axis.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional
from utilities.keplerian import OrbitPropagator


def plot_keplerian_element_with_residual(
    times_hours: np.ndarray,
    elem_undisturbed: np.ndarray,
    elem_disturbed: np.ndarray,
    elem_diff: np.ndarray,
    element_name: str,
    unit: str,
    title: str
) -> plt.Figure:
    """
    Create a single plot with undisturbed and disturbed values on left axis, 
    difference on right axis.
    
    Args:
        times_hours: Time array in hours
        elem_undisturbed: Element values for undisturbed orbit
        elem_disturbed: Element values for disturbed orbit
        elem_diff: Difference (disturbed - undisturbed)
        element_name: Name of the element (e.g., "Inclination")
        unit: Unit string (e.g., "deg", "m", "-")
        title: Plot title
        
    Returns:
        Figure object
    """
    fig, ax1 = plt.subplots(figsize=(16, 6))
    
    # Left y-axis: Undisturbed and Disturbed values
    ax1.set_xlabel('Time [hours]', fontsize=12)
    ax1.set_ylabel(f'{element_name} [{unit}]', fontsize=12, color='black')
    
    # Undisturbed: Thick solid line in background
    line1 = ax1.plot(times_hours, elem_undisturbed, color='navy', linestyle='-', 
                     linewidth=4.5, label='Undisturbed', alpha=0.6, zorder=2)
    # Disturbed: Dashed line in foreground
    line2 = ax1.plot(times_hours, elem_disturbed, color='orangered', linestyle='--', 
                     linewidth=3.0, label='Disturbed', alpha=1.0, zorder=4)
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.grid(True, alpha=0.3, zorder=0)
    
    # Right y-axis: Difference (with two representations superimposed)
    ax2 = ax1.twinx()
    ax2.set_ylabel(f'Difference [{unit}]', fontsize=12, color='darkgreen')
    
    # Difference representation 1: Thin, transparent line at bottom layer
    line3a = ax2.plot(times_hours, elem_diff, color='darkgreen', linestyle='-', 
                      linewidth=0.8, alpha=0.15, zorder=1)
    # Difference representation 2: Normal line on top layer
    line3b = ax2.plot(times_hours, elem_diff, color='darkgreen', linestyle=':', 
                      linewidth=2.0, label='Difference (Disturbed - Undisturbed)', 
                      alpha=0.8, zorder=3)
    
    ax2.tick_params(axis='y', labelcolor='darkgreen')
    ax2.axhline(y=0, color='dimgray', linestyle=':', linewidth=1.0, alpha=0.5)
    
    # Title
    ax1.set_title(title, fontsize=14, fontweight='bold')
    
    # Combined legend (only show the main difference line, not the transparent one)
    # Place legend outside plot area to the right
    lines = line1 + line2 + line3b
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.15, 1.0), 
               fontsize=11, framealpha=0.9)
    
    # Add statistics text outside plot area below the legend
    stats_text = f'Undisturbed:\n'
    stats_text += f'  Mean: {np.mean(elem_undisturbed):.6g} {unit}\n'
    stats_text += f'  Std:  {np.std(elem_undisturbed):.6g} {unit}\n'
    stats_text += f'Disturbed:\n'
    stats_text += f'  Mean: {np.mean(elem_disturbed):.6g} {unit}\n'
    stats_text += f'  Std:  {np.std(elem_disturbed):.6g} {unit}\n'
    stats_text += f'Difference:\n'
    stats_text += f'  Mean: {np.mean(elem_diff):.6g} {unit}\n'
    stats_text += f'  Final: {elem_diff[-1]:.6g} {unit}'
    
    # Place text box outside to the right, below the legend
    fig.text(1.15, 0.35, stats_text, transform=ax1.transAxes,
             verticalalignment='center', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=9, family='monospace')
    
    plt.tight_layout(rect=[0, 0, 0.78, 1])  # Leave more space on the right for legend and text
    
    return fig


def plot_keplerian_elements_and_residuals(
    pos_undisturbed: np.ndarray,
    vel_undisturbed: np.ndarray,
    pos_disturbed: np.ndarray,
    vel_disturbed: np.ndarray,
    times: np.ndarray,
    disturbance_name: str = "Disturbed",
    mu: float = None
) -> List[Tuple[str, plt.Figure]]:
    """
    Create 5 plots comparing Keplerian elements between undisturbed and disturbed orbits.
    
    Each plot shows:
    - Undisturbed orbit (thick solid navy line, left y-axis)
    - Disturbed orbit (dashed orange-red line, left y-axis)
    - Difference (dotted green line, right y-axis)
    
    The five plots are:
    1. Inclination [deg]
    2. Eccentricity [-]
    3. Semi-major axis [m]
    4. Argument of latitude (True Anomaly + Arg. of Periapsis) [deg]
    5. RAAN (Right Ascension of Ascending Node) [deg]
    
    Args:
        pos_undisturbed: Undisturbed orbit positions [N x 3] in km
        vel_undisturbed: Undisturbed orbit velocities [N x 3] in km/s
        pos_disturbed: Disturbed orbit positions [N x 3] in km
        vel_disturbed: Disturbed orbit velocities [N x 3] in km/s
        times: Time array in seconds from epoch
        disturbance_name: Name of the disturbance for plot titles (e.g., "J2", "SRP", "Drag")
        mu: Gravitational parameter [km^3/s^2] (if None, uses WGS72 value)
        
    Returns:
        List of tuples (element_name, figure) for the 5 plots
        
    Raises:
        ValueError: If input arrays have incompatible shapes
    """
    # Validate input shapes
    if pos_undisturbed.shape != pos_disturbed.shape:
        raise ValueError(
            f"Position arrays must have same shape. "
            f"Got undisturbed: {pos_undisturbed.shape}, disturbed: {pos_disturbed.shape}"
        )
    
    if vel_undisturbed.shape != vel_disturbed.shape:
        raise ValueError(
            f"Velocity arrays must have same shape. "
            f"Got undisturbed: {vel_undisturbed.shape}, disturbed: {vel_disturbed.shape}"
        )
    
    if len(times) != len(pos_undisturbed):
        raise ValueError(
            f"Time array length ({len(times)}) must match position array length ({len(pos_undisturbed)})"
        )
    
    print("\n" + "=" * 70)
    print(f"COMPUTING KEPLERIAN ELEMENTS AND RESIDUALS - {disturbance_name}")
    print("=" * 70)
    
    # Initialize propagator
    if mu is not None:
        propagator = OrbitPropagator(mu=mu)
    else:
        propagator = OrbitPropagator()
    
    # Compute Keplerian elements for both orbits
    print("Computing Keplerian elements for undisturbed orbit...")
    elements_undisturbed = propagator.cartesian_to_keplerian(pos_undisturbed, vel_undisturbed)
    
    print("Computing Keplerian elements for disturbed orbit...")
    elements_disturbed = propagator.cartesian_to_keplerian(pos_disturbed, vel_disturbed)
    
    # Convert times to hours
    times_hours = times / 3600.0
    
    print(f"Time span: {times_hours[0]:.2f} to {times_hours[-1]:.2f} hours")
    print(f"Number of data points: {len(times)}")
    
    figures = []
    
    # 1. Inclination [deg]
    print("\nPlot 1: Inclination")
    inc_undisturbed = np.rad2deg(elements_undisturbed.inclination)
    inc_disturbed = np.rad2deg(elements_disturbed.inclination)
    inc_diff = inc_disturbed - inc_undisturbed
    
    fig1 = plot_keplerian_element_with_residual(
        times_hours, inc_undisturbed, inc_disturbed, inc_diff,
        'Inclination', 'deg', 
        f'Inclination Comparison: {disturbance_name} vs Undisturbed'
    )
    figures.append(('inclination', fig1))
    print(f"  Difference range: [{np.min(inc_diff):.6g}, {np.max(inc_diff):.6g}] deg")
    
    # 2. Eccentricity [dimensionless]
    print("\nPlot 2: Eccentricity")
    ecc_undisturbed = elements_undisturbed.eccentricity
    ecc_disturbed = elements_disturbed.eccentricity
    ecc_diff = ecc_disturbed - ecc_undisturbed
    
    fig2 = plot_keplerian_element_with_residual(
        times_hours, ecc_undisturbed, ecc_disturbed, ecc_diff,
        'Eccentricity', '-', 
        f'Eccentricity Comparison: {disturbance_name} vs Undisturbed'
    )
    figures.append(('eccentricity', fig2))
    print(f"  Difference range: [{np.min(ecc_diff):.6g}, {np.max(ecc_diff):.6g}]")
    
    # 3. Semi-major axis [m]
    print("\nPlot 3: Semi-major Axis")
    sma_undisturbed = elements_undisturbed.semi_major_axis * 1000  # km to m
    sma_disturbed = elements_disturbed.semi_major_axis * 1000
    sma_diff = sma_disturbed - sma_undisturbed
    
    fig3 = plot_keplerian_element_with_residual(
        times_hours, sma_undisturbed, sma_disturbed, sma_diff,
        'Semi-major Axis', 'm', 
        f'Semi-major Axis Comparison: {disturbance_name} vs Undisturbed'
    )
    figures.append(('semi_major_axis', fig3))
    print(f"  Difference range: [{np.min(sma_diff):.6g}, {np.max(sma_diff):.6g}] m")
    
    # 4. Argument of Latitude (True Anomaly + Argument of Periapsis) [deg]
    print("\nPlot 4: Argument of Latitude")
    arg_lat_undisturbed = np.rad2deg(
        (elements_undisturbed.true_anomaly + elements_undisturbed.argument_of_periapsis) % (2 * np.pi)
    )
    arg_lat_disturbed = np.rad2deg(
        (elements_disturbed.true_anomaly + elements_disturbed.argument_of_periapsis) % (2 * np.pi)
    )
    arg_lat_diff = arg_lat_disturbed - arg_lat_undisturbed
    
    fig4 = plot_keplerian_element_with_residual(
        times_hours, arg_lat_undisturbed, arg_lat_disturbed, arg_lat_diff,
        'Argument of Latitude', 'deg', 
        f'Argument of Latitude Comparison: {disturbance_name} vs Undisturbed'
    )
    figures.append(('argument_of_latitude', fig4))
    print(f"  Difference range: [{np.min(arg_lat_diff):.6g}, {np.max(arg_lat_diff):.6g}] deg")
    
    # 5. RAAN (Right Ascension of Ascending Node) [deg]
    print("\nPlot 5: RAAN")
    raan_undisturbed = np.rad2deg(elements_undisturbed.raan)
    raan_disturbed = np.rad2deg(elements_disturbed.raan)
    raan_diff = raan_disturbed - raan_undisturbed
    
    fig5 = plot_keplerian_element_with_residual(
        times_hours, raan_undisturbed, raan_disturbed, raan_diff,
        'RAAN', 'deg', 
        f'RAAN Comparison: {disturbance_name} vs Undisturbed'
    )
    figures.append(('raan', fig5))
    print(f"  Difference range: [{np.min(raan_diff):.6g}, {np.max(raan_diff):.6g}] deg")
    
    print("\n" + "=" * 70)
    print("KEPLERIAN ELEMENTS AND RESIDUALS COMPUTATION COMPLETE")
    print("=" * 70)
    
    return figures


def main():
    """
    Example usage of the plotting function.
    
    This demonstrates how to use the plot_keplerian_elements_and_residuals function
    with sample data.
    """
    import sys
    import os
    from keplerian import OrbitDataLoader
    
    print("=" * 70)
    print("KEPLERIAN ELEMENTS AND RESIDUALS PLOTTING")
    print("=" * 70)
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("\nUsage: python plot_keplerian_residuals.py <undisturbed_file> <disturbed_file> [disturbance_name] [output_dir]")
        print("\nExample:")
        print("  python plot_keplerian_residuals.py data/sgp4_output.npz data/j2_output.txt J2 plots/j2")
        print("\nSupported file formats: .npz, .txt")
        return
    
    undisturbed_file = sys.argv[1]
    disturbed_file = sys.argv[2]
    disturbance_name = sys.argv[3] if len(sys.argv) > 3 else "Disturbed"
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "plots"
    
    # Load data
    loader = OrbitDataLoader()
    
    print(f"\nLoading undisturbed orbit from: {undisturbed_file}")
    times_undist, pos_undist, vel_undist, sat_name_undist = loader.load_from_file(undisturbed_file)
    
    print(f"Loading disturbed orbit from: {disturbed_file}")
    times_dist, pos_dist, vel_dist, sat_name_dist = loader.load_from_file(disturbed_file)
    
    # Convert times to seconds if needed (handle both formats)
    if times_undist.ndim == 2:  # Julian date format
        times_undist_sec = (times_undist[:, 0] + times_undist[:, 1] - times_undist[0, 0] - times_undist[0, 1]) * 86400
    else:
        times_undist_sec = times_undist - times_undist[0]
    
    if times_dist.ndim == 2:
        times_dist_sec = (times_dist[:, 0] + times_dist[:, 1] - times_dist[0, 0] - times_dist[0, 1]) * 86400
    else:
        times_dist_sec = times_dist - times_dist[0]
    
    # Check that time domains match
    if len(times_undist_sec) != len(times_dist_sec):
        print("\nWarning: Time domains have different lengths!")
        print(f"  Undisturbed: {len(times_undist_sec)} points")
        print(f"  Disturbed: {len(times_dist_sec)} points")
        print("  Using minimum length for comparison...")
        min_len = min(len(times_undist_sec), len(times_dist_sec))
        times_undist_sec = times_undist_sec[:min_len]
        times_dist_sec = times_dist_sec[:min_len]
        pos_undist = pos_undist[:min_len]
        vel_undist = vel_undist[:min_len]
        pos_dist = pos_dist[:min_len]
        vel_dist = vel_dist[:min_len]
    
    # Create plots
    print("\nGenerating Keplerian element comparison plots...")
    figures = plot_keplerian_elements_and_residuals(
        pos_undist, vel_undist,
        pos_dist, vel_dist,
        times_undist_sec,
        disturbance_name
    )
    
    # Save figures
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nSaving plots to: {output_dir}")
    
    for element_name, fig in figures:
        filename = os.path.join(output_dir, f'{element_name}_comparison.png')
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  Saved: {filename}")
    
    print("\n" + "=" * 70)
    print("PLOTTING COMPLETE")
    print("=" * 70)
    
    # Show plots
    plt.show()


if __name__ == "__main__":
    main()
