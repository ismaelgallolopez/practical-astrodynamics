#!/usr/bin/env python3
"""
Generate all missing Keplerian element plots for the answer sheet.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from utilities.keplerian import cart_to_kep

def load_orbit_data(filepath):
    """Load orbit data from file."""
    if filepath.endswith('.npz'):
        data = np.load(filepath)
        times_jd = data['times_jd']
        positions = data['positions'] * 1000  # km to m
        velocities = data['velocities'] * 1000  # km/s to m/s
        # Convert to hours
        times = (times_jd[:, 0] + times_jd[:, 1] - times_jd[0, 0] - times_jd[0, 1]) * 24.0
    else:
        data = np.loadtxt(filepath)
        times = data[:, 0] / 3600.0  # seconds to hours
        positions = data[:, 1:4]
        velocities = data[:, 4:7]
    
    return times, positions, velocities

def compute_elements(positions, velocities):
    """Compute Keplerian elements for all timesteps."""
    n = len(positions)
    elements = {
        'a': np.zeros(n),
        'e': np.zeros(n),
        'i': np.zeros(n),
        'raan': np.zeros(n),
        'omega': np.zeros(n),
        'nu': np.zeros(n)
    }
    
    for i in range(n):
        kep = cart_to_kep(positions[i], velocities[i])
        elements['a'][i] = kep[0]
        elements['e'][i] = kep[1]
        elements['i'][i] = kep[2]
        elements['raan'][i] = kep[3]
        elements['omega'][i] = kep[4]
        elements['nu'][i] = kep[5]
    
    return elements

def plot_integrated_elements(orbit_file, output_prefix):
    """Generate Keplerian element plots for integrated orbit."""
    print(f"Loading orbit data from {orbit_file}...")
    times, positions, velocities = load_orbit_data(orbit_file)
    
    print("Computing Keplerian elements...")
    elements = compute_elements(positions, velocities)
    
    # Argument of latitude (nu + omega)
    arg_lat = np.rad2deg(elements['nu']) + np.rad2deg(elements['omega'])
    
    # Plot 1: a, e, i
    print("Creating Plot 1...")
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    
    color1 = 'tab:blue'
    ax1.set_xlabel('Time [hours]', fontsize=12)
    ax1.set_ylabel('Semi-major Axis [km]', color=color1, fontsize=12)
    ax1.plot(times, elements['a']/1000, color=color1, linewidth=1.5)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)
    
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Eccentricity [-]', color=color2, fontsize=12)
    ax2.plot(times, elements['e'], color=color2, linewidth=1.5)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    color3 = 'tab:green'
    ax3.set_ylabel('Inclination [deg]', color=color3, fontsize=12)
    ax3.plot(times, np.rad2deg(elements['i']), color=color3, linewidth=1.5)
    ax3.tick_params(axis='y', labelcolor=color3)
    
    plt.title('Integrated Orbit: Keplerian Elements (a, e, i)', fontsize=14)
    fig1.tight_layout()
    
    filename1 = f'../../../plots/keplerian/{output_prefix}_elements_1.png'
    fig1.savefig(filename1, dpi=300, bbox_inches='tight')
    print(f"  Saved: {filename1}")
    plt.close(fig1)
    
    # Plot 2: arg_lat, RAAN
    print("Creating Plot 2...")
    fig2, ax1 = plt.subplots(figsize=(12, 7))
    
    color1 = 'tab:purple'
    ax1.set_xlabel('Time [hours]', fontsize=12)
    ax1.set_ylabel('Argument of Latitude [deg]', color=color1, fontsize=12)
    ax1.plot(times, arg_lat, color=color1, linewidth=1.5)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)
    
    ax2 = ax1.twinx()
    color2 = 'tab:orange'
    ax2.set_ylabel('RAAN [deg]', color=color2, fontsize=12)
    ax2.plot(times, np.rad2deg(elements['raan']), color=color2, linewidth=1.5)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    plt.title('Integrated Orbit: Keplerian Elements (Arg. Latitude, RAAN)', fontsize=14)
    fig2.tight_layout()
    
    filename2 = f'../../../plots/keplerian/{output_prefix}_elements_2.png'
    fig2.savefig(filename2, dpi=300, bbox_inches='tight')
    print(f"  Saved: {filename2}")
    plt.close(fig2)

def plot_individual_elements():
    """Generate individual element plots for SGP4, integrated, and optimized orbits."""
    print("\nGenerating individual element comparison plots...")
    
    # Load all three orbits
    print("Loading orbit data...")
    times_sgp4, pos_sgp4, vel_sgp4 = load_orbit_data('../../../data/sgp4_reference/orbit_propagation.npz')
    times_int, pos_int, vel_int = load_orbit_data('../../../data/outputs_all/integrated_orbit.txt')
    times_opt, pos_opt, vel_opt = load_orbit_data('../../../data/outputs_all/optimized_orbit.txt')
    
    # Compute elements
    print("Computing Keplerian elements...")
    elem_sgp4 = compute_elements(pos_sgp4, vel_sgp4)
    elem_int = compute_elements(pos_int, vel_int)
    elem_opt = compute_elements(pos_opt, vel_opt)
    
    # Compute arg latitude
    arg_lat_sgp4 = np.rad2deg(elem_sgp4['nu']) + np.rad2deg(elem_sgp4['omega'])
    arg_lat_int = np.rad2deg(elem_int['nu']) + np.rad2deg(elem_int['omega'])
    arg_lat_opt = np.rad2deg(elem_opt['nu']) + np.rad2deg(elem_opt['omega'])
    
    # Define elements to plot
    elements_to_plot = [
        ('a', 'Semi-major Axis', 'km', 1000),
        ('e', 'Eccentricity', '', 1),
        ('i', 'Inclination', 'deg', 1, np.rad2deg),
        ('arg_lat', 'Argument of Latitude', 'deg', 1, None),
        ('raan', 'RAAN', 'deg', 1, np.rad2deg),
    ]
    
    for elem_info in elements_to_plot:
        if len(elem_info) == 4:
            key, title, unit, scale = elem_info
            convert = None
        else:
            key, title, unit, scale, convert = elem_info
        
        print(f"  Creating {title} plot...")
        
        fig, ax1 = plt.subplots(figsize=(12, 7))
        
        # Get data
        if key == 'arg_lat':
            y_sgp4 = arg_lat_sgp4 / scale
            y_int = arg_lat_int / scale
            y_opt = arg_lat_opt / scale
        else:
            y_sgp4 = elem_sgp4[key] / scale if convert is None else convert(elem_sgp4[key]) / scale
            y_int = elem_int[key] / scale if convert is None else convert(elem_int[key]) / scale
            y_opt = elem_opt[key] / scale if convert is None else convert(elem_opt[key]) / scale
        
        # Plot on main axis
        ax1.plot(times_sgp4, y_sgp4, 'b-', linewidth=1.5, label='SGP4', alpha=0.8)
        ax1.plot(times_int, y_int, 'r--', linewidth=1.5, label='Integrated', alpha=0.8)
        ax1.plot(times_opt, y_opt, 'g:', linewidth=2, label='Optimized', alpha=0.8)
        
        ax1.set_xlabel('Time [hours]', fontsize=12)
        unit_str = f' [{unit}]' if unit else ''
        ax1.set_ylabel(f'{title}{unit_str}', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left', fontsize=10)
        
        # Add difference plot on second y-axis
        ax2 = ax1.twinx()
        diff_int = y_int - y_sgp4
        diff_opt = y_opt - y_sgp4
        
        ax2.plot(times_int, diff_int, 'r-', linewidth=1, label='Int - SGP4', alpha=0.6)
        ax2.plot(times_opt, diff_opt, 'g-', linewidth=1, label='Opt - SGP4', alpha=0.6)
        ax2.set_ylabel(f'Difference{unit_str}', fontsize=12, color='purple')
        ax2.tick_params(axis='y', labelcolor='purple')
        ax2.legend(loc='upper right', fontsize=10)
        ax2.axhline(y=0, color='k', linestyle=':', alpha=0.3)
        
        plt.title(f'{title} Comparison: SGP4, Integrated, and Optimized Orbits', fontsize=14)
        fig.tight_layout()
        
        filename = f'../../../plots/keplerian/{key.replace("_", "_")}.png'
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"    Saved: {filename}")
        plt.close(fig)

if __name__ == '__main__':
    # Generate integrated orbit plots
    plot_integrated_elements('../../../data/outputs_all/integrated_orbit.txt', 'integrated')
    
    # Generate individual element comparison plots
    plot_individual_elements()
    
    print("\n✓ All plots generated successfully!")
