#!/usr/bin/env python3
"""
Plot CGPD (Cumulative Global Position Difference) at final time vs timestep.

CGPD is defined as the RMS over time of the GPD (Global Position Difference),
where GPD is the L2 norm of position differences between SGP4 and Verlet.

CGPD = sqrt(mean(GPD^2))
"""

import numpy as np
import matplotlib.pyplot as plt
from keplerian import OrbitDataLoader
import os
import sys


def compute_cgpd_at_final_time(sgp4_file: str, euler_file: str):
    """
    Compute CGPD at the final integration time.
    
    CGPD = RMS of GPD over time = sqrt(mean(GPD^2))
    where GPD = L2 norm of position difference
    
    Args:
        sgp4_file: Path to SGP4 NPZ file
        euler_file: Path to Verlet output file
        
    Returns:
        cgpd: Cumulative global position difference at final time (km)
    """
    loader = OrbitDataLoader()
    
    # Load both datasets
    times_sgp4, pos_sgp4, vel_sgp4, _ = loader.load_from_file(sgp4_file)
    times_euler, pos_euler, vel_euler, _ = loader.load_from_file(euler_file)
    
    # Convert times to seconds if needed
    if times_sgp4.ndim == 2:
        times_sgp4 = (times_sgp4[:, 0] - times_sgp4[0, 0]) * 86400.0 + (times_sgp4[:, 1] - times_sgp4[0, 1])
    if times_euler.ndim == 2:
        times_euler = (times_euler[:, 0] - times_euler[0, 0]) * 86400.0 + (times_euler[:, 1] - times_euler[0, 1])
    
    # Interpolate SGP4 to Verlet time points
    pos_sgp4_interp = np.zeros_like(pos_euler)
    for i in range(3):
        pos_sgp4_interp[:, i] = np.interp(times_euler, times_sgp4, pos_sgp4[:, i])
    
    # Compute GPD (Global Position Difference) - L2 norm at each time
    gpd = np.linalg.norm(pos_euler - pos_sgp4_interp, axis=1)  # km
    
    # Compute CGPD - RMS of GPD over time
    cgpd = np.sqrt(np.mean(gpd**2))  # km
    
    return cgpd


def analyze_cgpd_vs_timestep_verlet(timesteps: list):
    """
    Compute CGPD for multiple timesteps and create plot.
    
    Args:
        timesteps: List of timestep values in seconds
    """
    sgp4_file = 'data/sgp4_reference/orbit_propagation.npz'
    
    # Check if SGP4 file exists
    if not os.path.exists(sgp4_file):
        print(f"Error: SGP4 file not found: {sgp4_file}")
        return
    
    cgpd_values = []
    valid_timesteps = []
    
    print("\nComputing CGPD for different timesteps:")
    print("-" * 50)
    
    for dt in timesteps:
        verlet_file = f'data/verlet_outputs/dt{int(dt)}s_verlet_output.txt'
        
        if not os.path.exists(verlet_file):
            print(f"  dt={dt:6.1f}s: File not found, skipping")
            continue
        
        try:
            cgpd = compute_cgpd_at_final_time(sgp4_file, verlet_file)
            cgpd_values.append(cgpd)
            valid_timesteps.append(dt)
            print(f"  dt={dt:6.1f}s: CGPD = {cgpd:10.3f} km")
        except Exception as e:
            print(f"  dt={dt:6.1f}s: Error - {e}")
    
    if len(valid_timesteps) == 0:
        print("\nNo valid data found. Please run propagations first.")
        return
    
    # Convert to numpy arrays
    valid_timesteps = np.array(valid_timesteps)
    cgpd_values = np.array(cgpd_values)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.loglog(valid_timesteps, cgpd_values, 'o-', linewidth=2, markersize=8, 
               color='darkblue', markerfacecolor='lightblue', markeredgewidth=2)
    
    plt.xlabel('Time Step (s)', fontsize=12, fontweight='bold')
    plt.ylabel('CGPD at Final Time (km)', fontsize=12, fontweight='bold')
    plt.title('Cumulative Global Position Difference vs Time Step\n(Verlet vs SGP4)', 
              fontsize=13, fontweight='bold')
    plt.grid(True, which='both', alpha=0.3, linestyle='--')
    
    # Add annotations for min and max CGPD
    min_idx = np.argmin(cgpd_values)
    max_idx = np.argmax(cgpd_values)
    
    plt.annotate(f'Min: {cgpd_values[min_idx]:.1f} km\n@ dt={valid_timesteps[min_idx]:.0f}s',
                xy=(valid_timesteps[min_idx], cgpd_values[min_idx]),
                xytext=(20, 20), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.annotate(f'Max: {cgpd_values[max_idx]:.1f} km\n@ dt={valid_timesteps[max_idx]:.0f}s',
                xy=(valid_timesteps[max_idx], cgpd_values[max_idx]),
                xytext=(20, -40), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    
    # Save plot
    os.makedirs('plots/summary', exist_ok=True)
    output_file = 'plots/summary/cgpd_vs_timestep_verlet.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved: {output_file}")
    
    # Save data
    os.makedirs('data/summary', exist_ok=True)
    data_file = 'data/summary/cgpd_vs_timestep_verlet.npz'
    np.savez(data_file, timesteps=valid_timesteps, cgpd=cgpd_values)
    print(f"Data saved: {data_file}")
    
    # Print summary statistics
    print("\n" + "=" * 50)
    print("SUMMARY STATISTICS")
    print("=" * 50)
    print(f"Number of timesteps analyzed: {len(valid_timesteps)}")
    print(f"Timestep range: {valid_timesteps.min():.1f} - {valid_timesteps.max():.1f} s")
    print(f"Orders of magnitude span: {np.log10(valid_timesteps.max() / valid_timesteps.min()):.2f}")
    print(f"CGPD range: {cgpd_values.min():.3f} - {cgpd_values.max():.3f} km")
    print(f"Best timestep: {valid_timesteps[min_idx]:.1f} s (CGPD = {cgpd_values[min_idx]:.3f} km)")
    print(f"Worst timestep: {valid_timesteps[max_idx]:.1f} s (CGPD = {cgpd_values[max_idx]:.3f} km)")


def discover_timesteps_from_folder(data_dir='data'):
    """
    Discover all available timesteps from Verlet output files in the data folder.
    
    Args:
        data_dir: Directory containing Verlet output files
        
    Returns:
        List of timesteps (in seconds) sorted in ascending order
    """
    import glob
    import re
    
    # Pattern: dt<N>s_verlet_output.txt
    pattern = os.path.join(data_dir, 'verlet_outputs', 'dt*s_verlet_output.txt')
    files = glob.glob(pattern)
    
    timesteps = []
    for file in files:
        # Extract timestep from filename using regex
        match = re.search(r'dt(\d+)s_verlet_output\.txt', os.path.basename(file))
        if match:
            timesteps.append(int(match.group(1)))
    
    return sorted(timesteps)


def main():
    """Main function."""
    # Check command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        # Option 1: "all" - discover all available timesteps
        if arg.lower() == 'all':
            timesteps = discover_timesteps_from_folder()
            if len(timesteps) == 0:
                print("Error: No Verlet output files found in data/ folder.")
                print("Please run propagations first using run_propagation.sh")
                return
            print(f"Discovered {len(timesteps)} timesteps from data folder: {timesteps}")
        
        # Option 2: Comma-separated list of specific timesteps
        else:
            try:
                timesteps = [float(dt) for dt in arg.split(',')]
                print(f"Using specified timesteps: {timesteps}")
            except ValueError:
                print("Error: Invalid timestep format. Use comma-separated values or 'all'.")
                print("Examples:")
                print("  python3 plot_cgpd_vs_timestep_verlet.py all")
                print("  python3 plot_cgpd_vs_timestep_verlet.py 10,20,50,100,200,500,1000")
                return
    else:
        # Default: discover all available timesteps
        timesteps = discover_timesteps_from_folder()
        if len(timesteps) == 0:
            print("No Verlet output files found in data/ folder.")
            print("Using default timestep set...")
            timesteps = [10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000]
            print(f"Default timesteps: {timesteps}")
            print("\nNote: Run propagations first or specify timesteps:")
            print("  python3 plot_cgpd_vs_timestep_verlet.py all")
            print("  python3 plot_cgpd_vs_timestep_verlet.py 10,20,50,100")
        else:
            print(f"Discovered {len(timesteps)} timesteps from data folder: {timesteps}")
    
    analyze_cgpd_vs_timestep_verlet(timesteps)


if __name__ == '__main__':
    main()
