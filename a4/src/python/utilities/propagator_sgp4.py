#!/usr/bin/env python3
"""Main script for Assignment 1 - Practical Astrodynamics
Orbit propagation using SGP4 from TLE data.
"""

import os
import numpy as np
from datetime import datetime, timedelta
from sgp4.api import Satrec


def read_tle_from_file(filepath):
    """Read TLE data from a file.
    
    Args:
        filepath: Path to file containing TLE data
        
    Returns:
        List of dicts with 'name', 'line1', 'line2'
    """
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    tle_sets = []
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith('1 ') and i + 1 < len(lines) and lines[i+1].startswith('2 '):
            name = lines[i-1] if i >= 1 and not lines[i-1].startswith(('1 ', '2 ')) else 'Unknown'
            tle_sets.append({
                'name': name,
                'line1': lines[i],
                'line2': lines[i+1]
            })
            i += 2
        else:
            i += 1
    
    return tle_sets


def sgp4_propagate(tle, ti, tf, dt):
    """Propagate orbit using SGP4 with vectorized array operations.
    
    Args:
        tle: Tuple of (name, line1, line2) TLE data
        ti: Start time in seconds from TLE epoch
        tf: End time in seconds from TLE epoch
        dt: Time step in seconds
    
    Returns:
        Tuple of (errors, positions, velocities, jd_array, fr_array, satellite, times_seconds)
        - errors: (N,) array of error codes
        - positions: (N, 3) array of positions [km] in TEME frame
        - velocities: (N, 3) array of velocities [km/s] in TEME frame
        - jd_array: (N, 1) array of Julian date whole parts
        - fr_array: (N, 1) array of Julian date fractional parts (days from epoch)
        - satellite: Satrec object
        - times_seconds: (N, 1) array of times in seconds from epoch
    """
    sat = Satrec.twoline2rv(tle[1], tle[2])

    # Time vector in seconds from TLE epoch
    times_seconds = np.arange(ti, tf + dt, dt, dtype=float)  # shape (N,)

    # Full Julian date at each step (including fractional epoch!)
    epoch_jd = sat.jdsatepoch + sat.jdsatepochF
    jd_full = epoch_jd + times_seconds / 86400.0             # shape (N,)

    # Split into integer + fractional parts for sgp4_array
    jd_int = np.floor(jd_full).astype(float)
    jd_frac = jd_full - jd_int

    # Propagate
    e, r_km, v_km_s = sat.sgp4_array(jd_int, jd_frac)
    assert np.all(e == 0), f"SGP4 failed at {np.sum(e != 0)} epochs out of {len(e)}"

    return e, r_km, v_km_s, jd_int, jd_frac, sat, times_seconds



def main():
    # Configuration
    tle_file = 'data/sgp4_reference/tle.txt'
    propagation_hours = 72.0  # Propagate for 72 hours from TLE epoch
    time_step_seconds = 10.0 # Time step in seconds
    
    print("=" * 70)
    print("ORBIT PROPAGATION USING SGP4")
    print("=" * 70)
    
    # Read TLE from file
    print(f"\n1. Reading TLE data from: {tle_file}")
    try:
        tle_sets = read_tle_from_file(tle_file)
        print(f"   Found {len(tle_sets)} TLE set(s)")
    except FileNotFoundError:
        print(f"   ERROR: File not found. Run fetch_tle.py first to download TLE data.")
        return
    
    if not tle_sets:
        print("   ERROR: No valid TLE data found in file.")
        return
    
    # Use first TLE set
    tle_data = tle_sets[0]
    print(f"\n2. Using TLE for: {tle_data['name']}")
    print(f"   Line 1: {tle_data['line1']}")
    print(f"   Line 2: {tle_data['line2']}")
    
    # Prepare TLE tuple for sgp4_propagate function
    tle = (tle_data['name'], tle_data['line1'], tle_data['line2'])
    
    # Generate time domain
    ti = 0.0  # Start at TLE epoch
    tf = propagation_hours * 3600.0  # End time in seconds
    dt = time_step_seconds
    
    print(f"\n3. Generating time domain:")
    print(f"   Start: TLE Epoch (ti = {ti} seconds)")
    print(f"   Duration: {propagation_hours} hours ({tf} seconds)")
    print(f"   Step: {time_step_seconds} seconds ({time_step_seconds/60:.1f} minutes)")
    
    n_expected = int((tf - ti) / dt) + 1
    print(f"   Expected points: {n_expected}")
    
    # Propagate orbit using vectorized SGP4
    print(f"\n4. Propagating orbit using vectorized SGP4...")
    errors, positions, velocities, jd, fr, satellite, times_seconds = sgp4_propagate(tle, ti, tf, dt)
    
    print(f"   Satellite number: {satellite.satnum}")
    print(f"   Epoch: JD {satellite.jdsatepoch + satellite.jdsatepochF:.6f}")
    
    # Display results
    print(f"\n5. Results:")
    print(f"   Generated {len(positions)} state vectors")
    print(f"   Errors: {sum(errors != 0)}")
    
    if sum(errors != 0) == 0:
        print("\n   Sample positions (first 5 points) [km]:")
        for i in range(min(5, len(positions))):
            r = positions[i]
            print(f"   [{i}] x={r[0]:12.3f}, y={r[1]:12.3f}, z={r[2]:12.3f}")
        
        print("\n   Sample velocities (first 5 points) [km/s]:")
        for i in range(min(5, len(velocities))):
            v = velocities[i]
            print(f"   [{i}] vx={v[0]:9.6f}, vy={v[1]:9.6f}, vz={v[2]:9.6f}")
        
        # Compute some statistics
        # Orbital radius
        radii = np.linalg.norm(positions, axis=1)
        speeds = np.linalg.norm(velocities, axis=1)
        
        print(f"\n6. Orbital Statistics:")
        print(f"   Altitude range: {radii.min() - 6378.137:.1f} to {radii.max() - 6378.137:.1f} km")
        print(f"   Radius range:   {radii.min():.1f} to {radii.max():.1f} km")
        print(f"   Speed range:    {speeds.min():.3f} to {speeds.max():.3f} km/s")
        print(f"   Mean radius:    {radii.mean():.1f} km")
        print(f"   Mean speed:     {speeds.mean():.3f} km/s")
    
    # Prepare times_jd array in the expected format (N, 2)
    # times_jd = np.column_stack([jd.flatten(), fr.flatten()])
    times_jd = np.column_stack([jd, fr])

    
    # Save results to file
    os.makedirs('data/sgp4_reference', exist_ok=True)
    output_file = 'data/sgp4_reference/orbit_propagation.npz'
    np.savez(output_file,
             times_jd=times_jd,
             positions=positions,
             velocities=velocities,
             errors=errors,
             satellite_name=tle_data['name'],
             tle_line1=tle_data['line1'],
             tle_line2=tle_data['line2'])
    
    print(f"\n7. Data saved to: {output_file}")
    print(f"   Load with: data = np.load('{output_file}')")
    print(f"   Access arrays: data['positions'], data['velocities'], etc.")
    
    print("\n" + "=" * 70)
    print("PROPAGATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
