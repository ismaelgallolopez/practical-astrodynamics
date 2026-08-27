#!/usr/bin/env python3
"""
Plot Keplerian elements and residuals comparing undisturbed (two-body) 
and J2-disturbed orbits.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from utilities.keplerian import OrbitDataLoader
from plotting.plot_keplerian_residuals import plot_keplerian_elements_and_residuals


def main():
    """Compare undisturbed and J2-disturbed orbits."""
    
    print("=" * 70)
    print("J2 KEPLERIAN ELEMENTS COMPARISON")
    print("=" * 70)
    
    # File paths
    undisturbed_file = "data/outputs_orbit/dt10s_output.txt"
    disturbed_file = "data/outputs_oblateness/dt10s_j2_output.txt"
    output_dir = "plots/j2_keplerian"
    
    # Check if files exist
    if not os.path.exists(undisturbed_file):
        print(f"\nError: Undisturbed orbit file not found: {undisturbed_file}")
        print("Please run: ./src/fortran/build/propagate_orbit")
        return 1
    
    if not os.path.exists(disturbed_file):
        print(f"\nError: J2 orbit file not found: {disturbed_file}")
        print("Please run: ./src/fortran/build/propagate_orbit_oblateness")
        return 1
    
    # Load data
    loader = OrbitDataLoader()
    
    print(f"\nLoading undisturbed orbit from: {undisturbed_file}")
    times_undist, pos_undist, vel_undist, _ = loader.load_from_file(undisturbed_file)
    print(f"  Loaded {len(times_undist)} data points")
    
    print(f"\nLoading J2-disturbed orbit from: {disturbed_file}")
    times_dist, pos_dist, vel_dist, _ = loader.load_from_file(disturbed_file)
    print(f"  Loaded {len(times_dist)} data points")
    
    # Convert times to seconds from start
    times_undist_sec = times_undist - times_undist[0]
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
    
    # Convert from meters to kilometers for OrbitPropagator
    pos_undist_km = pos_undist / 1000.0
    vel_undist_km = vel_undist / 1000.0
    pos_dist_km = pos_dist / 1000.0
    vel_dist_km = vel_dist / 1000.0
    
    print(f"\nTime span: {times_undist_sec[0]:.2f} to {times_undist_sec[-1]:.2f} seconds")
    print(f"           ({times_undist_sec[-1]/3600:.2f} hours)")
    
    # Create plots
    print("\nGenerating Keplerian element comparison plots...")
    figures = plot_keplerian_elements_and_residuals(
        pos_undist_km, vel_undist_km,
        pos_dist_km, vel_dist_km,
        times_undist_sec,
        disturbance_name="J2 Oblateness"
    )
    
    # Save figures
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nSaving plots to: {output_dir}/")
    
    for element_name, fig in figures:
        filename = os.path.join(output_dir, f'{element_name}_j2_comparison.png')
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  Saved: {filename}")
    
    print("\n" + "=" * 70)
    print("PLOTTING COMPLETE")
    print("=" * 70)
    print("\nPlots saved. Close the plot windows to exit.")
    
    # Show plots
    plt.show()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
