#!/usr/bin/env python3
"""
Plotting script for Keplerian orbital elements.

Creates two visualizations:
1. Plot with inclination, eccentricity, and semi-major axis (3 y-axes)
2. Plot with true anomaly + argument of periapsis and RAAN (2 y-axes)
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from utilities.keplerian import OrbitPropagator, OrbitDataLoader
from sgp4.api import jday


def julian_to_time_hours(times_jd: np.ndarray, reference_jd: float = None) -> np.ndarray:
    """
    Convert Julian date array to hours from reference time.
    
    Args:
        times_jd: Array of shape (N, 2) containing [jd, fr] pairs or (N,) for seconds
        reference_jd: Reference Julian date (if None, uses first time point)
        
    Returns:
        Time in hours from reference
    """
    # Check if times are in Julian date format (N, 2) or seconds (N,)
    if times_jd.ndim == 2:
        # Julian date format from NPZ
        jd_full = times_jd[:, 0] + times_jd[:, 1]
        
        if reference_jd is None:
            reference_jd = jd_full[0]
        
        # Convert days to hours
        time_hours = (jd_full - reference_jd) * 24.0
    else:
        # Seconds format from TXT
        # Convert seconds to hours
        time_hours = times_jd / 3600.0
        # Shift to start at zero
        time_hours = time_hours - time_hours[0]
    
    return time_hours


def plot_orbital_elements_set1(times_hours: np.ndarray, elements, satellite_name: str):
    """
    Create first plot: Inclination, Eccentricity, and Semi-major axis vs time.
    Each quantity plotted on separate y-axis.
    """
    fig, ax1 = plt.subplots(figsize=(15, 6))
    
    # Color scheme
    color_i = 'tab:blue'
    color_e = 'tab:orange'
    color_a = 'tab:green'
    
    # First y-axis: Inclination (degrees)
    ax1.set_xlabel('Time from Epoch (hours)', fontsize=12)
    ax1.set_ylabel('Inclination (deg)', color=color_i, fontsize=12)
    line1 = ax1.plot(times_hours, np.rad2deg(elements.inclination), 
                     color=color_i, linewidth=1.5, label='Inclination')
    ax1.tick_params(axis='y', labelcolor=color_i)
    ax1.grid(True, alpha=0.3)
    
    # Second y-axis: Eccentricity
    ax2 = ax1.twinx()
    ax2.set_ylabel('Eccentricity (-)', color=color_e, fontsize=12)
    line2 = ax2.plot(times_hours, elements.eccentricity, 
                     color=color_e, linewidth=3.5, label='Eccentricity')
    ax2.tick_params(axis='y', labelcolor=color_e, pad=25)
    ax2.ticklabel_format(style='scientific', scilimits=(0,0), axis='y')
    
    # Third y-axis: Semi-major axis (km) - CHANGED FROM METERS
    ax3 = ax1.twinx()
    # Offset the third axis to the right
    ax3.spines['right'].set_position(('outward', 80))
    
    # FIX: Plot in km instead of meters to avoid the huge e7 offset obstruction
    # Note: removed the * 1000 multiplier assuming elements.semi_major_axis is in km
    ax3.set_ylabel('Semi-major Axis (km)', color=color_a, fontsize=12)
    line3 = ax3.plot(times_hours, elements.semi_major_axis, 
                     color=color_a, linewidth=1.5, label='Semi-major Axis')
    
    ax3.tick_params(axis='y', labelcolor=color_a, pad=5)
    
    # Optional: Force scientific notation off if you want plain numbers (e.g. 42168)
    ax3.ticklabel_format(useOffset=False, style='plain', axis='y')

    # Title and legend
    fig.suptitle(f'Keplerian Orbital Elements - {satellite_name}', 
                 fontsize=14, fontweight='bold')
    ax1.set_title('Inclination, Eccentricity, and Semi-major Axis vs Time', 
                  fontsize=11, pad=10)
    
    # Combine legends from all axes
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.35, 1), 
               framealpha=0.95, fontsize=9, edgecolor='gray')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 0.82, 0.96])
    
    return fig


def plot_orbital_elements_set2(times_hours: np.ndarray, elements, satellite_name: str):
    """
    Create second plot: (True Anomaly + Argument of Periapsis) and RAAN vs time.
    Two quantities plotted on separate y-axes.
    
    Args:
        times_hours: Time array in hours
        elements: KeplerianElements object
        satellite_name: Name of satellite for title
    """
    fig, ax1 = plt.subplots(figsize=(15, 6))
    
    # Color scheme
    color_theta_omega = 'tab:red'
    color_raan = 'tab:purple'
    
    # Compute true anomaly + argument of periapsis (in degrees)
    theta_plus_omega = np.rad2deg(
        (elements.true_anomaly + elements.argument_of_periapsis) % (2 * np.pi)
    )
    raan_deg = np.rad2deg(elements.raan)
    
    # First y-axis: True Anomaly + Argument of Periapsis
    ax1.set_xlabel('Time from Epoch (hours)', fontsize=12)
    ax1.set_ylabel('True Anomaly + Arg. of Periapsis (deg)', 
                   color=color_theta_omega, fontsize=12)
    line1 = ax1.plot(times_hours, theta_plus_omega, 
                     color=color_theta_omega, linewidth=1.5, 
                     label='θ + ω')
    ax1.tick_params(axis='y', labelcolor=color_theta_omega)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 360])
    ax1.yaxis.set_major_locator(MultipleLocator(60))
    
    # Second y-axis: RAAN
    ax2 = ax1.twinx()
    ax2.set_ylabel('Right Ascension of Ascending Node (deg)', 
                   color=color_raan, fontsize=12)
    line2 = ax2.plot(times_hours, raan_deg, 
                     color=color_raan, linewidth=1.5, 
                     label='RAAN (Ω)')
    ax2.tick_params(axis='y', labelcolor=color_raan)
    
    # Title and legend
    fig.suptitle(f'Keplerian Orbital Elements - {satellite_name}', 
                 fontsize=14, fontweight='bold')
    ax1.set_title('Argument of Latitude and RAAN vs Time', 
                  fontsize=11, pad=10)
    
    # Combine legends from both axes
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.1, 1), 
               framealpha=0.95, fontsize=9, edgecolor='gray')
    
    # Adjust layout to prevent label clipping
    plt.tight_layout(rect=[0, 0, 0.90, 0.96])
    
    return fig


def print_statistics(elements, satellite_name: str):
    """
    Print summary statistics for orbital elements.
    
    Args:
        elements: KeplerianElements object
        satellite_name: Name of satellite
    """
    print("\n" + "=" * 70)
    print(f"KEPLERIAN ELEMENTS STATISTICS - {satellite_name}")
    print("=" * 70)
    
    print(f"\nSemi-major Axis (a):")
    print(f"  Mean:   {np.mean(elements.semi_major_axis) * 1000:12.3f} m")
    print(f"  Std:    {np.std(elements.semi_major_axis) * 1000:12.3f} m")
    print(f"  Min:    {np.min(elements.semi_major_axis) * 1000:12.3f} m")
    print(f"  Max:    {np.max(elements.semi_major_axis) * 1000:12.3f} m")
    
    print(f"\nEccentricity (e):")
    print(f"  Mean:   {np.mean(elements.eccentricity):12.8f}")
    print(f"  Std:    {np.std(elements.eccentricity):12.8f}")
    print(f"  Min:    {np.min(elements.eccentricity):12.8f}")
    print(f"  Max:    {np.max(elements.eccentricity):12.8f}")
    
    print(f"\nInclination (i):")
    print(f"  Mean:   {np.rad2deg(np.mean(elements.inclination)):12.6f} deg")
    print(f"  Std:    {np.rad2deg(np.std(elements.inclination)):12.6f} deg")
    print(f"  Min:    {np.rad2deg(np.min(elements.inclination)):12.6f} deg")
    print(f"  Max:    {np.rad2deg(np.max(elements.inclination)):12.6f} deg")
    
    print(f"\nRAAN (Ω):")
    print(f"  Mean:   {np.rad2deg(np.mean(elements.raan)):12.6f} deg")
    print(f"  Std:    {np.rad2deg(np.std(elements.raan)):12.6f} deg")
    print(f"  Min:    {np.rad2deg(np.min(elements.raan)):12.6f} deg")
    print(f"  Max:    {np.rad2deg(np.max(elements.raan)):12.6f} deg")
    
    print(f"\nArgument of Periapsis (ω):")
    print(f"  Mean:   {np.rad2deg(np.mean(elements.argument_of_periapsis)):12.6f} deg")
    print(f"  Std:    {np.rad2deg(np.std(elements.argument_of_periapsis)):12.6f} deg")
    print(f"  Min:    {np.rad2deg(np.min(elements.argument_of_periapsis)):12.6f} deg")
    print(f"  Max:    {np.rad2deg(np.max(elements.argument_of_periapsis)):12.6f} deg")
    
    print(f"\nTrue Anomaly (θ):")
    print(f"  Mean:   {np.rad2deg(np.mean(elements.true_anomaly)):12.6f} deg")
    print(f"  Std:    {np.rad2deg(np.std(elements.true_anomaly)):12.6f} deg")
    print(f"  Min:    {np.rad2deg(np.min(elements.true_anomaly)):12.6f} deg")
    print(f"  Max:    {np.rad2deg(np.max(elements.true_anomaly)):12.6f} deg")
    
    # Compute θ + ω
    theta_plus_omega = np.rad2deg((elements.true_anomaly + elements.argument_of_periapsis) % (2 * np.pi))
    print(f"\nTrue Anomaly + Arg. of Periapsis (θ + ω):")
    print(f"  Mean:   {np.mean(theta_plus_omega):12.6f} deg")
    print(f"  Std:    {np.std(theta_plus_omega):12.6f} deg")
    print(f"  Min:    {np.min(theta_plus_omega):12.6f} deg")
    print(f"  Max:    {np.max(theta_plus_omega):12.6f} deg")
    
    print("\n" + "=" * 70)


def main():
    """Main execution function."""
    import sys
    
    # Change to project root directory
    project_root = os.path.join(os.path.dirname(__file__), '../../..')
    os.chdir(project_root)
    
    # Parse arguments
    data_source = sys.argv[1] if len(sys.argv) > 1 else 'both'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'plots'
    
    sources = []
    if data_source == 'both':
        sources = [
            ('data/sgp4_reference/orbit_propagation.npz', 'SGP4'),
            ('data/outputs_orbit/dt10s_output.txt', 'Undisturbed')
        ]
    elif data_source == 'sgp4':
        sources = [('data/sgp4_reference/orbit_propagation.npz', 'SGP4')]
    elif data_source == 'euler':
        sources = [('data/outputs_orbit/dt10s_output.txt', 'Undisturbed')]
    else:
        # Try to use the provided path
        sources = [(data_source, 'Custom')]
    
    print("=" * 70)
    print("KEPLERIAN ELEMENTS PLOTTING")
    print("=" * 70)
    
    # Process each data source
    all_figures = []
    loader = OrbitDataLoader()
    
    for filepath, label in sources:
        try:
            print(f"\nProcessing {label} data from: {filepath}")
            print("-" * 70)
            
            # Load data
            times, positions, velocities, sat_name = loader.load_from_file(filepath)
            
            # Add label to satellite name
            sat_name_full = f"{sat_name} ({label})"
            
            print(f"Satellite: {sat_name_full}")
            print(f"Number of data points: {len(positions)}")
            
            # Initialize propagator and compute Keplerian elements
            print("Computing Keplerian elements...")
            propagator = OrbitPropagator()
            elements = propagator.cartesian_to_keplerian(positions, velocities)
            
            # Convert times to hours from epoch
            times_hours = julian_to_time_hours(times)
            print(f"Time span: {times_hours[0]:.2f} to {times_hours[-1]:.2f} hours")
            
            # Print statistics
            print_statistics(elements, sat_name_full)
            
            # Create plots
            print("\nGenerating plots...")
            
            # Generate file suffix and output directory for saving
            # Detect data source from filepath
            if 'sgp4' in filepath.lower():
                suffix = 'sgp4'
                plot_output_dir = os.path.join(output_dir, 'sgp4')
            elif 'undisturbed' in label.lower() or 'outputs_orbit' in filepath.lower():
                suffix = 'undisturbed'
                plot_output_dir = os.path.join(output_dir, 'undisturbed')
            elif 'euler' in filepath.lower():
                suffix = 'euler'
                plot_output_dir = os.path.join(output_dir, 'undisturbed')
            elif 'verlet' in filepath.lower():
                suffix = 'verlet'
                plot_output_dir = os.path.join(output_dir, 'undisturbed')
            else:
                suffix = label.lower().replace(' ', '_')
                plot_output_dir = output_dir
            
            # Create output directory if it doesn't exist
            os.makedirs(plot_output_dir, exist_ok=True)
            
            print(f"  Creating Plot 1: Inclination, Eccentricity, Semi-major Axis...")
            fig1 = plot_orbital_elements_set1(times_hours, elements, sat_name_full)
            filename1 = os.path.join(plot_output_dir, f'keplerian_elements_{suffix}_plot1.png')
            fig1.savefig(filename1, dpi=300, bbox_inches='tight')
            print(f"    Saved: {filename1}")
            all_figures.append(fig1)
            
            print(f"  Creating Plot 2: Argument of Latitude, RAAN...")
            fig2 = plot_orbital_elements_set2(times_hours, elements, sat_name_full)
            filename2 = os.path.join(plot_output_dir, f'keplerian_elements_{suffix}_plot2.png')
            fig2.savefig(filename2, dpi=300, bbox_inches='tight')
            print(f"    Saved: {filename2}")
            all_figures.append(fig2)
            
        except FileNotFoundError:
            print(f"  Warning: File not found: {filepath}")
            print(f"  Skipping {label} data...")
        except Exception as e:
            print(f"  Error processing {label} data: {e}")
            print(f"  Skipping...")
    
    if not all_figures:
        print("\nNo data could be processed!")
        return
    
    # Show plots
    print("\n" + "=" * 70)
    print("Displaying plots...")
    plt.show()
    
    print("\n" + "=" * 70)
    print("PLOTTING COMPLETE")
    print("=" * 70)
    print("\nUsage: python plot_keplerian.py [data_source] [output_dir]")
    print("  data_source: sgp4|euler|both (default: both) or file path")
    print("  output_dir: output directory (default: plots)")
    print("\nExamples:")
    print("  python plot_keplerian.py sgp4 plots/timestep_comparisons/dt100s")
    print("  python plot_keplerian.py data/sgp4_reference/orbit_propagation.npz plots")


if __name__ == "__main__":
    main()
