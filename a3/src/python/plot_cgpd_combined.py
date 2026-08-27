#!/usr/bin/env python3
"""
Plot combined CGPD (Cumulative Global Position Difference) for both Euler and Verlet methods.

CGPD is defined as the RMS over time of the GPD (Global Position Difference),
where GPD is the L2 norm of position differences between SGP4 and the numerical method.

CGPD = sqrt(mean(GPD^2))
"""

import numpy as np
import matplotlib.pyplot as plt
from keplerian import OrbitDataLoader
import os
import sys
import glob
import re


def compute_cgpd_at_final_time(sgp4_file: str, method_file: str):
    """
    Compute CGPD at the final integration time.
    
    CGPD = RMS of GPD over time = sqrt(mean(GPD^2))
    where GPD = L2 norm of position difference
    
    Args:
        sgp4_file: Path to SGP4 NPZ file
        method_file: Path to numerical method output file (Euler or Verlet)
        
    Returns:
        cgpd: Cumulative global position difference at final time (km)
    """
    loader = OrbitDataLoader()
    
    # Load both datasets
    times_sgp4, pos_sgp4, vel_sgp4, _ = loader.load_from_file(sgp4_file)
    times_method, pos_method, vel_method, _ = loader.load_from_file(method_file)
    
    # Convert times to seconds if needed
    if times_sgp4.ndim == 2:
        times_sgp4 = (times_sgp4[:, 0] - times_sgp4[0, 0]) * 86400.0 + (times_sgp4[:, 1] - times_sgp4[0, 1])
    if times_method.ndim == 2:
        times_method = (times_method[:, 0] - times_method[0, 0]) * 86400.0 + (times_method[:, 1] - times_method[0, 1])
    
    # Interpolate SGP4 to method time points
    pos_sgp4_interp = np.zeros_like(pos_method)
    for i in range(3):
        pos_sgp4_interp[:, i] = np.interp(times_method, times_sgp4, pos_sgp4[:, i])
    
    # Compute GPD (Global Position Difference) - L2 norm at each time
    gpd = np.linalg.norm(pos_method - pos_sgp4_interp, axis=1)  # km
    
    # Compute CGPD = RMS of GPD
    cgpd = np.sqrt(np.mean(gpd ** 2))  # km
    
    return cgpd


def discover_timesteps(data_dir, pattern_suffix):
    """
    Discover all available timesteps from output files.
    
    Args:
        data_dir: Directory containing output files
        pattern_suffix: Suffix pattern like 'euler_output.txt' or 'verlet_output.txt'
        
    Returns:
        List of timesteps (in seconds) sorted in ascending order
    """
    pattern = os.path.join(data_dir, f'dt*s_{pattern_suffix}')
    files = glob.glob(pattern)
    
    if not files:
        return []
    
    timesteps = []
    for file in files:
        basename = os.path.basename(file)
        match = re.search(r'dt(\d+)s_', basename)
        if match:
            dt = float(match.group(1))
            timesteps.append(dt)
    
    return sorted(timesteps)


def plot_combined_cgpd(timesteps_list=None):
    """
    Plot CGPD vs timestep for both Euler and Verlet methods on the same plot.
    
    Args:
        timesteps_list: List of timesteps to analyze. If None, auto-discover from files.
    """
    sgp4_file = 'data/sgp4_reference/orbit_propagation.npz'
    
    if not os.path.exists(sgp4_file):
        print(f"Error: SGP4 file not found: {sgp4_file}")
        return
    
    # Discover timesteps if not provided
    if timesteps_list is None or timesteps_list == ['all']:
        euler_timesteps = discover_timesteps('data/euler_outputs', 'euler_output.txt')
        verlet_timesteps = discover_timesteps('data/verlet_outputs', 'verlet_output.txt')
        
        if not euler_timesteps and not verlet_timesteps:
            print("Error: No Euler or Verlet output files found.")
            return
        
        print(f"Discovered Euler timesteps: {euler_timesteps}")
        print(f"Discovered Verlet timesteps: {verlet_timesteps}")
        
        # Use union of both timestep sets
        all_timesteps = sorted(set(euler_timesteps + verlet_timesteps))
    else:
        all_timesteps = [float(dt) for dt in timesteps_list]
    
    # Compute CGPD for Euler
    euler_cgpd = []
    euler_valid_timesteps = []
    
    print("\nComputing CGPD for Euler:")
    print("-" * 50)
    
    for dt in all_timesteps:
        euler_file = f'data/euler_outputs/dt{int(dt)}s_euler_output.txt'
        
        if not os.path.exists(euler_file):
            print(f"  dt={dt:6.1f}s: Euler file not found, skipping")
            continue
        
        try:
            cgpd = compute_cgpd_at_final_time(sgp4_file, euler_file)
            euler_cgpd.append(cgpd)
            euler_valid_timesteps.append(dt)
            print(f"  dt={dt:6.1f}s: CGPD = {cgpd:10.3f} km")
        except Exception as e:
            print(f"  dt={dt:6.1f}s: Error - {e}")
    
    # Compute CGPD for Verlet
    verlet_cgpd = []
    verlet_valid_timesteps = []
    
    print("\nComputing CGPD for Verlet:")
    print("-" * 50)
    
    for dt in all_timesteps:
        verlet_file = f'data/verlet_outputs/dt{int(dt)}s_verlet_output.txt'
        
        if not os.path.exists(verlet_file):
            print(f"  dt={dt:6.1f}s: Verlet file not found, skipping")
            continue
        
        try:
            cgpd = compute_cgpd_at_final_time(sgp4_file, verlet_file)
            verlet_cgpd.append(cgpd)
            verlet_valid_timesteps.append(dt)
            print(f"  dt={dt:6.1f}s: CGPD = {cgpd:10.3f} km")
        except Exception as e:
            print(f"  dt={dt:6.1f}s: Error - {e}")
    
    if len(euler_valid_timesteps) == 0 and len(verlet_valid_timesteps) == 0:
        print("\nNo valid data found. Please run propagations first.")
        return
    
    # Convert to numpy arrays
    euler_valid_timesteps = np.array(euler_valid_timesteps)
    euler_cgpd = np.array(euler_cgpd)
    verlet_valid_timesteps = np.array(verlet_valid_timesteps)
    verlet_cgpd = np.array(verlet_cgpd)
    
    # Create combined plot
    plt.figure(figsize=(12, 7))
    
    # Plot Euler
    if len(euler_valid_timesteps) > 0:
        plt.loglog(euler_valid_timesteps, euler_cgpd, 'o-', linewidth=2.5, markersize=8, 
                   color='#e74c3c', markerfacecolor='#fadbd8', markeredgewidth=2,
                   label='Euler', zorder=3)
    
    # Plot Verlet
    if len(verlet_valid_timesteps) > 0:
        plt.loglog(verlet_valid_timesteps, verlet_cgpd, 's-', linewidth=2.5, markersize=8,
                   color='#3498db', markerfacecolor='#d6eaf8', markeredgewidth=2,
                   label='Verlet', zorder=3)
    
    plt.xlabel('Time Step (s)', fontsize=12, fontweight='bold')
    plt.ylabel('CGPD at Final Time (km)', fontsize=12, fontweight='bold')
    plt.title('Cumulative Global Position Difference vs Time Step\n(Euler and Verlet vs SGP4)', 
              fontsize=13, fontweight='bold')
    plt.grid(True, which='both', alpha=0.3, linestyle='--')
    plt.legend(fontsize=11, loc='best', framealpha=0.9)
    
    plt.tight_layout()
    
    # Save plot
    os.makedirs('plots/summary', exist_ok=True)
    output_file = 'plots/summary/cgpd_vs_timestep_combined.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nCombined plot saved: {output_file}")
    
    # Save data
    os.makedirs('data/summary', exist_ok=True)
    data_file = 'data/summary/cgpd_vs_timestep_combined.npz'
    np.savez(data_file, 
             euler_timesteps=euler_valid_timesteps, euler_cgpd=euler_cgpd,
             verlet_timesteps=verlet_valid_timesteps, verlet_cgpd=verlet_cgpd)
    print(f"Data saved: {data_file}")
    
    # Print summary statistics
    print("\n" + "=" * 50)
    print("EULER SUMMARY")
    print("=" * 50)
    if len(euler_valid_timesteps) > 0:
        min_idx = np.argmin(euler_cgpd)
        max_idx = np.argmax(euler_cgpd)
        print(f"Number of timesteps: {len(euler_valid_timesteps)}")
        print(f"Timestep range: {euler_valid_timesteps.min():.1f} - {euler_valid_timesteps.max():.1f} s")
        print(f"CGPD range: {euler_cgpd.min():.3f} - {euler_cgpd.max():.3f} km")
        print(f"Best timestep: {euler_valid_timesteps[min_idx]:.1f} s (CGPD = {euler_cgpd[min_idx]:.3f} km)")
        print(f"Worst timestep: {euler_valid_timesteps[max_idx]:.1f} s (CGPD = {euler_cgpd[max_idx]:.3f} km)")
    
    print("\n" + "=" * 50)
    print("VERLET SUMMARY")
    print("=" * 50)
    if len(verlet_valid_timesteps) > 0:
        min_idx = np.argmin(verlet_cgpd)
        max_idx = np.argmax(verlet_cgpd)
        print(f"Number of timesteps: {len(verlet_valid_timesteps)}")
        print(f"Timestep range: {verlet_valid_timesteps.min():.1f} - {verlet_valid_timesteps.max():.1f} s")
        print(f"CGPD range: {verlet_cgpd.min():.3f} - {verlet_cgpd.max():.3f} km")
        print(f"Best timestep: {verlet_valid_timesteps[min_idx]:.1f} s (CGPD = {verlet_cgpd[min_idx]:.3f} km)")
        print(f"Worst timestep: {verlet_valid_timesteps[max_idx]:.1f} s (CGPD = {verlet_cgpd[max_idx]:.3f} km)")


def main():
    if len(sys.argv) == 1:
        print("Usage: python plot_cgpd_combined.py <timesteps>")
        print("  timesteps: Space-separated list of timesteps in seconds")
        print("             or 'all' to analyze all available timesteps")
        print("\nExample: python plot_cgpd_combined.py all")
        print("Example: python plot_cgpd_combined.py 100 500 1000")
        return
    
    timesteps = sys.argv[1:]
    plot_combined_cgpd(timesteps)


if __name__ == "__main__":
    main()
