#!/usr/bin/env python3
"""
Plot Keplerian elements and residuals for SGP4, integrated, and optimized orbits.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Gravitational parameter for Earth (m^3/s^2)
MU = 3.986004418e14

def cart_to_kep(r, v, mu=MU):
    """
    Convert Cartesian state (position, velocity) to Keplerian elements.
    
    Parameters:
    -----------
    r : array_like (3,)
        Position vector [m]
    v : array_like (3,)
        Velocity vector [m/s]
    mu : float
        Gravitational parameter [m^3/s^2]
        
    Returns:
    --------
    kep : dict
        Keplerian elements:
        - a: semi-major axis [km]
        - e: eccentricity [-]
        - i: inclination [deg]
        - raan: right ascension of ascending node [deg]
        - argp: argument of perigee [deg]
        - nu: true anomaly [deg]
    """
    r = np.array(r)
    v = np.array(v)
    
    # Magnitude
    r_mag = np.linalg.norm(r)
    v_mag = np.linalg.norm(v)
    
    # Specific angular momentum
    h = np.cross(r, v)
    h_mag = np.linalg.norm(h)
    
    # Node vector
    k = np.array([0, 0, 1])
    n = np.cross(k, h)
    n_mag = np.linalg.norm(n)
    
    # Eccentricity vector
    e_vec = ((v_mag**2 - mu/r_mag) * r - np.dot(r, v) * v) / mu
    e = np.linalg.norm(e_vec)
    
    # Specific orbital energy
    epsilon = v_mag**2 / 2 - mu / r_mag
    
    # Semi-major axis
    if abs(e - 1.0) > 1e-10:  # Not parabolic
        a = -mu / (2 * epsilon)
    else:
        a = np.inf
    
    # Inclination
    i = np.arccos(h[2] / h_mag)
    
    # RAAN
    if n_mag > 1e-10:
        raan = np.arccos(n[0] / n_mag)
        if n[1] < 0:
            raan = 2 * np.pi - raan
    else:
        raan = 0.0
    
    # Argument of perigee
    if n_mag > 1e-10 and e > 1e-10:
        argp = np.arccos(np.dot(n, e_vec) / (n_mag * e))
        if e_vec[2] < 0:
            argp = 2 * np.pi - argp
    else:
        argp = 0.0
    
    # True anomaly
    if e > 1e-10:
        nu = np.arccos(np.dot(e_vec, r) / (e * r_mag))
        if np.dot(r, v) < 0:
            nu = 2 * np.pi - nu
    else:
        nu = 0.0
    
    return {
        'a': a / 1000.0,  # Convert to km
        'e': e,
        'i': np.degrees(i),
        'raan': np.degrees(raan),
        'argp': np.degrees(argp),
        'nu': np.degrees(nu)
    }

def load_orbit_data(filename):
    """Load orbit data from file."""
    data = np.loadtxt(filename, comments='#')
    times = data[:, 0]
    positions = data[:, 1:4]
    velocities = data[:, 4:7]
    return times, positions, velocities

def compute_keplerian_elements(times, positions, velocities):
    """Compute Keplerian elements for all time steps."""
    n_steps = len(times)
    kep_elements = {
        'a': np.zeros(n_steps),
        'e': np.zeros(n_steps),
        'i': np.zeros(n_steps),
        'raan': np.zeros(n_steps),
        'argp': np.zeros(n_steps),
        'nu': np.zeros(n_steps)
    }
    
    for i in range(n_steps):
        kep = cart_to_kep(positions[i], velocities[i])
        for key in kep_elements:
            kep_elements[key][i] = kep[key]
    
    return kep_elements

def main():
    print("="*60)
    print("Keplerian Elements and Residuals Analysis")
    print("="*60)
    print()
    
    # Load orbit data
    print("Loading orbit data...")
    
    # Load SGP4 orbit
    print("  - Loading SGP4 orbit...")
    sgp4_data = np.load('data/sgp4_reference/orbit_propagation.npz')
    times_jd = sgp4_data['times_jd']
    # Convert Julian date to seconds from start (JD is in two parts: integer and fraction)
    jd_full = times_jd[:, 0] + times_jd[:, 1]
    sgp4_times = (jd_full - jd_full[0]) * 86400.0  # JD to seconds
    sgp4_positions = sgp4_data['positions'] * 1000.0  # km to m
    sgp4_velocities = sgp4_data['velocities'] * 1000.0  # km/s to m/s
    
    # Load integrated orbit
    print("  - Loading integrated orbit...")
    times_int, pos_int, vel_int = load_orbit_data('data/outputs_all/integrated_orbit.txt')
    
    # Load optimized orbit
    print("  - Loading optimized orbit...")
    times_opt, pos_opt, vel_opt = load_orbit_data('data/outputs_all/optimized_orbit.txt')
    
    # Compute Keplerian elements
    print()
    print("Computing Keplerian elements...")
    print("  - SGP4 orbit...")
    kep_sgp4 = compute_keplerian_elements(sgp4_times, sgp4_positions, sgp4_velocities)
    
    print("  - Integrated orbit...")
    kep_int = compute_keplerian_elements(times_int, pos_int, vel_int)
    
    print("  - Optimized orbit...")
    kep_opt = compute_keplerian_elements(times_opt, pos_opt, vel_opt)
    
    # Interpolate integrated and optimized orbits to SGP4 times for fair comparison
    print()
    print("Interpolating orbits to common time domain...")
    kep_int_interp = {}
    kep_opt_interp = {}
    for key in ['a', 'e', 'i', 'raan', 'argp', 'nu']:
        kep_int_interp[key] = np.interp(sgp4_times, times_int, kep_int[key])
        kep_opt_interp[key] = np.interp(sgp4_times, times_opt, kep_opt[key])
    
    # Compute argument of latitude (true anomaly + argument of periapsis)
    u_sgp4 = kep_sgp4['nu'] + kep_sgp4['argp']
    u_int = kep_int_interp['nu'] + kep_int_interp['argp']
    u_opt = kep_opt_interp['nu'] + kep_opt_interp['argp']
    
    # Convert times to hours
    times_sgp4_hr = sgp4_times / 3600.0
    
    # Create plots
    print()
    print("Creating plots...")
    
    # Define the 5 elements to plot
    elements_to_plot = [
        ('i', 'Inclination', '[deg]', kep_sgp4['i'], kep_int_interp['i'], kep_opt_interp['i']),
        ('e', 'Eccentricity', '[-]', kep_sgp4['e'], kep_int_interp['e'], kep_opt_interp['e']),
        ('a', 'Semi-major Axis', '[km]', kep_sgp4['a'], kep_int_interp['a'], kep_opt_interp['a']),
        ('u', 'Argument of Latitude', '[deg]', u_sgp4, u_int, u_opt),
        ('raan', 'RAAN', '[deg]', kep_sgp4['raan'], kep_int_interp['raan'], kep_opt_interp['raan'])
    ]
    
    output_files = []
    
    for key, name, unit, sgp4_vals, int_vals, opt_vals in elements_to_plot:
        print(f"  - Creating plot for {name}...")
        
        fig, ax1 = plt.subplots(figsize=(12, 7))
        
        # Primary y-axis: Plot the three orbits
        ax1.set_xlabel('Time [hours]', fontsize=12, fontweight='bold')
        ax1.set_ylabel(f'{name} {unit}', fontsize=12, fontweight='bold', color='black')
        
        line1 = ax1.plot(times_sgp4_hr, sgp4_vals, 'b-', label='SGP4', 
                        linewidth=2, alpha=0.8)
        line2 = ax1.plot(times_sgp4_hr, int_vals, 'g--', label='Integrated', 
                        linewidth=1.5, alpha=0.7)
        line3 = ax1.plot(times_sgp4_hr, opt_vals, 'r:', label='Optimized', 
                        linewidth=1.5, alpha=0.7)
        
        ax1.tick_params(axis='y', labelcolor='black')
        ax1.grid(True, alpha=0.3)
        
        # Secondary y-axis: Plot the differences
        ax2 = ax1.twinx()
        ax2.set_ylabel(f'{name} Difference {unit}', fontsize=12, fontweight='bold', color='purple')
        
        # Compute residuals
        residual_int = int_vals - sgp4_vals
        residual_opt = opt_vals - sgp4_vals
        
        # Handle angle wrapping for angular elements
        if key in ['i', 'u', 'raan', 'argp', 'nu']:
            residual_int = np.arctan2(np.sin(np.radians(residual_int)), 
                                     np.cos(np.radians(residual_int)))
            residual_int = np.degrees(residual_int)
            
            residual_opt = np.arctan2(np.sin(np.radians(residual_opt)), 
                                     np.cos(np.radians(residual_opt)))
            residual_opt = np.degrees(residual_opt)
        
        line4 = ax2.plot(times_sgp4_hr, residual_int, 'm-', 
                        label='Integrated - SGP4', linewidth=1.5, alpha=0.7)
        line5 = ax2.plot(times_sgp4_hr, residual_opt, 'orange', linestyle='-',
                        label='Optimized - SGP4', linewidth=1.5, alpha=0.7)
        
        ax2.tick_params(axis='y', labelcolor='purple')
        ax2.axhline(0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        # Title
        plt.title(f'{name} Comparison: SGP4 vs Integrated vs Optimized', 
                 fontsize=14, fontweight='bold', pad=20)
        
        # Combined legend
        lines = line1 + line2 + line3 + line4 + line5
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(1.15, 1), 
                  framealpha=0.95, fontsize=9, edgecolor='gray')
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0, 0.88, 0.96])
        
        # Save figure
        output_file = f'plots/keplerian/{key}_comparison.png'
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"    Saved: {output_file}")
        output_files.append(output_file)
        plt.close(fig)
        
        # Print statistics
        rms_int = np.sqrt(np.mean(residual_int**2))
        rms_opt = np.sqrt(np.mean(residual_opt**2))
        print(f"    {key.upper()}: RMS error (Integrated) = {rms_int:.6e}, RMS error (Optimized) = {rms_opt:.6e}")
    
    print()
    print("="*60)
    print("Analysis complete!")
    print(f"Created {len(output_files)} plots")
    print("="*60)

if __name__ == '__main__':
    main()
