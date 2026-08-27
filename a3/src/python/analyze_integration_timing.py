#!/usr/bin/env python3
"""
Extract and compare integration timing data from Euler and Verlet output files.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path


def extract_timing_from_file(filepath):
    """
    Extract timing information from propagation output file header.
    
    Args:
        filepath: Path to output file
        
    Returns:
        dict with keys: timestep, n_steps, integration_time, time_per_step
    """
    if not os.path.exists(filepath):
        return None
    
    data = {}
    with open(filepath, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                break
            
            if 'Time step (s):' in line:
                data['timestep'] = float(line.split(':')[1].strip())
            elif 'Number of steps:' in line:
                data['n_steps'] = int(line.split(':')[1].strip())
            elif 'Integration time (s):' in line:
                data['integration_time'] = float(line.split(':')[1].strip())
            elif 'Time per step (ms):' in line:
                data['time_per_step'] = float(line.split(':')[1].strip())
    
    return data if len(data) == 4 else None


def discover_timesteps(output_dir, pattern):
    """
    Discover available timesteps from output files.
    
    Args:
        output_dir: Directory containing output files
        pattern: Regex pattern to match filenames
        
    Returns:
        List of timesteps (sorted)
    """
    if not os.path.exists(output_dir):
        return []
    
    timesteps = []
    for file in os.listdir(output_dir):
        match = re.match(pattern, file)
        if match:
            timesteps.append(int(match.group(1)))
    
    return sorted(timesteps)


def collect_timing_data(method='euler'):
    """
    Collect timing data for all available timesteps.
    
    Args:
        method: 'euler' or 'verlet'
        
    Returns:
        Arrays: timesteps, n_steps, integration_times, time_per_step
    """
    if method == 'euler':
        output_dir = 'data/euler_outputs'
        pattern = r'dt(\d+)s_euler_output\.txt'
    else:
        output_dir = 'data/verlet_outputs'
        pattern = r'dt(\d+)s_verlet_output\.txt'
    
    timesteps_available = discover_timesteps(output_dir, pattern)
    
    if not timesteps_available:
        return None, None, None, None
    
    timesteps = []
    n_steps_list = []
    integration_times = []
    time_per_step_list = []
    
    for dt in timesteps_available:
        if method == 'euler':
            filepath = f'{output_dir}/dt{dt}s_euler_output.txt'
        else:
            filepath = f'{output_dir}/dt{dt}s_verlet_output.txt'
        
        timing = extract_timing_from_file(filepath)
        if timing:
            timesteps.append(timing['timestep'])
            n_steps_list.append(timing['n_steps'])
            integration_times.append(timing['integration_time'])
            time_per_step_list.append(timing['time_per_step'])
    
    if not timesteps:
        return None, None, None, None
    
    return (np.array(timesteps), np.array(n_steps_list), 
            np.array(integration_times), np.array(time_per_step_list))


def plot_timing_comparison():
    """Generate timing comparison plots for Euler vs Verlet."""
    
    # Collect data
    euler_data = collect_timing_data('euler')
    verlet_data = collect_timing_data('verlet')
    
    if euler_data[0] is None and verlet_data[0] is None:
        print("Error: No timing data found for either method")
        print("Run propagations first with:")
        print("  ./scripts/run_propagation.sh <timesteps>")
        print("  ./scripts/run_propagation_verlet.sh <timesteps>")
        return
    
    # Create output directory
    os.makedirs('plots/summary', exist_ok=True)
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Total integration time vs timestep
    ax1.set_title('Total Integration Time vs Timestep', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Time Step (s)', fontsize=11)
    ax1.set_ylabel('Integration Time (s)', fontsize=11)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3, which='both')
    
    if euler_data[0] is not None:
        ax1.plot(euler_data[0], euler_data[2], 'o-', label='Euler', 
                linewidth=2, markersize=8, color='blue')
        print(f"Euler: {len(euler_data[0])} timesteps analyzed")
    
    if verlet_data[0] is not None:
        ax1.plot(verlet_data[0], verlet_data[2], 's-', label='Velocity Verlet', 
                linewidth=2, markersize=8, color='red')
        print(f"Verlet: {len(verlet_data[0])} timesteps analyzed")
    
    ax1.legend(fontsize=10)
    
    # Plot 2: Time per step vs timestep
    ax2.set_title('Time per Step vs Timestep', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Time Step (s)', fontsize=11)
    ax2.set_ylabel('Time per Step (ms)', fontsize=11)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3, which='both')
    
    if euler_data[0] is not None:
        ax2.plot(euler_data[0], euler_data[3], 'o-', label='Euler', 
                linewidth=2, markersize=8, color='blue')
    
    if verlet_data[0] is not None:
        ax2.plot(verlet_data[0], verlet_data[3], 's-', label='Velocity Verlet', 
                linewidth=2, markersize=8, color='red')
    
    ax2.legend(fontsize=10)
    
    plt.tight_layout()
    
    # Save plot
    output_file = 'plots/summary/integration_timing_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved: {output_file}")
    
    # Print timing statistics
    print("\n" + "=" * 60)
    print("TIMING COMPARISON STATISTICS")
    print("=" * 60)
    
    if euler_data[0] is not None:
        print("\nEuler Method:")
        print(f"  Timestep range: {euler_data[0].min():.1f} - {euler_data[0].max():.1f} s")
        print(f"  Integration time range: {euler_data[2].min():.6f} - {euler_data[2].max():.6f} s")
        print(f"  Mean time per step: {euler_data[3].mean():.6f} ms")
    
    if verlet_data[0] is not None:
        print("\nVelocity Verlet Method:")
        print(f"  Timestep range: {verlet_data[0].min():.1f} - {verlet_data[0].max():.1f} s")
        print(f"  Integration time range: {verlet_data[2].min():.6f} - {verlet_data[2].max():.6f} s")
        print(f"  Mean time per step: {verlet_data[3].mean():.6f} ms")
    
    # Compare methods if both available
    if euler_data[0] is not None and verlet_data[0] is not None:
        # Find common timesteps
        common_dt = np.intersect1d(euler_data[0], verlet_data[0])
        
        if len(common_dt) > 0:
            print(f"\nComparison at common timesteps ({len(common_dt)} values):")
            
            euler_idx = np.isin(euler_data[0], common_dt)
            verlet_idx = np.isin(verlet_data[0], common_dt)
            
            euler_times = euler_data[3][euler_idx]
            verlet_times = verlet_data[3][verlet_idx]
            
            ratio = verlet_times / euler_times
            print(f"  Mean Verlet/Euler time ratio: {ratio.mean():.2f}x")
            print(f"  Verlet is {'slower' if ratio.mean() > 1 else 'faster'} on average")
    
    # Save data
    os.makedirs('data/summary', exist_ok=True)
    
    save_dict = {}
    if euler_data[0] is not None:
        save_dict['euler_timesteps'] = euler_data[0]
        save_dict['euler_integration_times'] = euler_data[2]
        save_dict['euler_time_per_step'] = euler_data[3]
    
    if verlet_data[0] is not None:
        save_dict['verlet_timesteps'] = verlet_data[0]
        save_dict['verlet_integration_times'] = verlet_data[2]
        save_dict['verlet_time_per_step'] = verlet_data[3]
    
    if save_dict:
        data_file = 'data/summary/integration_timing.npz'
        np.savez(data_file, **save_dict)
        print(f"\nData saved: {data_file}")


def main():
    """Main function."""
    print("=" * 60)
    print("INTEGRATION TIMING ANALYSIS")
    print("=" * 60)
    print()
    
    plot_timing_comparison()


if __name__ == '__main__':
    main()
