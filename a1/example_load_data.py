#!/usr/bin/env python3
"""Example: How to load and use the propagated orbit data"""

import numpy as np


def main():
    # Load the saved data
    print("Loading orbit propagation data...")
    data = np.load('data/orbit_propagation.npz')
    
    # Access the arrays
    times_jd = data['times_jd']
    positions = data['positions']  # Shape: (N, 3) in km
    velocities = data['velocities']  # Shape: (N, 3) in km/s
    errors = data['errors']
    
    # Access metadata
    sat_name = str(data['satellite_name'])
    tle_line1 = str(data['tle_line1'])
    tle_line2 = str(data['tle_line2'])
    
    print(f"\nSatellite: {sat_name}")
    print(f"Number of time points: {len(positions)}")
    print(f"Time span: JD {times_jd[0, 0] + times_jd[0, 1]:.6f} to {times_jd[-1, 0] + times_jd[-1, 1]:.6f}")
    
    # Example calculations
    print("\n" + "=" * 60)
    print("EXAMPLE CALCULATIONS")
    print("=" * 60)
    
    # 1. Compute orbital radius at each point
    radii = np.linalg.norm(positions, axis=1)
    print(f"\n1. Orbital radii:")
    print(f"   Min: {radii.min():.3f} km")
    print(f"   Max: {radii.max():.3f} km")
    print(f"   Mean: {radii.mean():.3f} km")
    
    # 2. Compute speeds
    speeds = np.linalg.norm(velocities, axis=1)
    print(f"\n2. Orbital speeds:")
    print(f"   Min: {speeds.min():.6f} km/s")
    print(f"   Max: {speeds.max():.6f} km/s")
    print(f"   Mean: {speeds.mean():.6f} km/s")
    
    # 3. Compute specific energy (vis-viva equation check)
    mu = 398600.4418  # Earth's gravitational parameter [km^3/s^2]
    specific_energy = 0.5 * speeds**2 - mu / radii
    print(f"\n3. Specific orbital energy:")
    print(f"   Mean: {specific_energy.mean():.6f} km^2/s^2")
    print(f"   Std:  {specific_energy.std():.6f} km^2/s^2")
    
    # 4. Compute semi-major axis from energy: a = -mu / (2*E)
    semi_major_axis = -mu / (2 * specific_energy.mean())
    print(f"   Semi-major axis: {semi_major_axis:.3f} km")
    
    # 5. Position at specific time point
    idx = 10  # 10th time point
    print(f"\n4. State vector at time point {idx}:")
    print(f"   Position: [{positions[idx, 0]:12.3f}, {positions[idx, 1]:12.3f}, {positions[idx, 2]:12.3f}] km")
    print(f"   Velocity: [{velocities[idx, 0]:9.6f}, {velocities[idx, 1]:9.6f}, {velocities[idx, 2]:9.6f}] km/s")
    
    # 6. Angular momentum vector
    h = np.cross(positions, velocities)  # Specific angular momentum
    h_mag = np.linalg.norm(h, axis=1)
    print(f"\n5. Angular momentum magnitude:")
    print(f"   Mean: {h_mag.mean():.3f} km^2/s")
    print(f"   Std:  {h_mag.std():.6f} km^2/s (should be ~0 for Keplerian orbit)")
    
    # 7. Inclination check
    h_mean = h.mean(axis=0)
    h_mean_mag = np.linalg.norm(h_mean)
    inclination_rad = np.arccos(h_mean[2] / h_mean_mag)
    inclination_deg = np.degrees(inclination_rad)
    print(f"\n6. Orbital inclination (from angular momentum):")
    print(f"   {inclination_deg:.4f} degrees")
    
    print("\n" + "=" * 60)
    print("TIPS FOR USING THE DATA")
    print("=" * 60)
    print("""
    - positions[i] gives position at i-th time point [km]
    - velocities[i] gives velocity at i-th time point [km/s]
    - Use numpy operations for vectorized calculations
    - All coordinates are in TEME (True Equator Mean Equinox) frame
    - Earth's radius: 6378.137 km (for altitude calculations)
    """)


if __name__ == '__main__':
    main()
