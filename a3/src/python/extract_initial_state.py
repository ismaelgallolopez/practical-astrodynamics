#!/usr/bin/env python3
"""Extract initial state from orbit_propagation.npz and create input file for Fortran."""

import numpy as np
import os
import sys


def extract_initial_state(npz_file='data/sgp4_reference/orbit_propagation.npz', 
                          output_file='data/sgp4_reference/initial_state.txt',
                          custom_dt=None):
    """
    Extract initial conditions from npz file and save in format readable by Fortran.
    
    Args:
        npz_file: Path to the NPZ file containing orbit data
        output_file: Path to output text file for Fortran
    """
    print("=" * 60)
    print("Extracting Initial State from NPZ file")
    print("=" * 60)
    
    # Load the npz file
    print(f"\nLoading data from: {npz_file}")
    try:
        data = np.load(npz_file)
    except FileNotFoundError:
        print(f"Error: File {npz_file} not found!")
        print("Please run main.py first to generate the orbit data.")
        return
    
    # Extract data
    positions = data['positions']  # Shape: (N, 3) in km
    velocities = data['velocities']  # Shape: (N, 3) in km/s
    times_jd = data['times_jd']  # Shape: (N, 2) - Julian date parts
    
    # Get initial state (first point)
    r0_km = positions[0, :]  # km
    v0_km_s = velocities[0, :]  # km/s
    
    # Convert to SI units (meters, m/s)
    r0_m = r0_km * 1000.0
    v0_m_s = v0_km_s * 1000.0
    
    # Calculate time parameters based on the data
    n_points = len(positions)
    
    # Compute time differences (assuming uniform time step)
    if n_points > 1:
        # Calculate dt from Julian dates
        # times_jd contains [jd_int, jd_frac] for each point
        jd_full = times_jd[:, 0] + times_jd[:, 1]
        dt_days = jd_full[1] - jd_full[0]
        dt_seconds = dt_days * 86400.0  # Convert days to seconds
        
        t_stop_seconds = (jd_full[-1] - jd_full[0]) * 86400.0
    else:
        print("Warning: Only one data point found. Using defaults.")
        dt_seconds = 600.0  # 10 minutes
        t_stop_seconds = 72 * 3600.0  # 72 hours
    
    # Override with custom dt if provided
    if custom_dt is not None:
        dt_seconds = custom_dt
        print(f"\nUsing custom time step: {dt_seconds:.2f} seconds ({dt_seconds/60:.2f} minutes)")
    
    # Display information
    print(f"\nData Information:")
    print(f"  Number of points: {n_points}")
    print(f"  Time step: {dt_seconds:.2f} seconds ({dt_seconds/60:.2f} minutes)")
    print(f"  Total duration: {t_stop_seconds:.2f} seconds ({t_stop_seconds/3600:.2f} hours)")
    
    print(f"\nInitial State (SI units):")
    print(f"  Position [m]:  {r0_m}")
    print(f"  Velocity [m/s]: {v0_m_s}")
    
    # print(f"\nInitial State (original units):")
    # print(f"  Position [km]:  {r0_km}")
    # print(f"  Velocity [km/s]: {v0_km_s}")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to output file in Fortran-readable format
    print(f"\nWriting to: {output_file}")
    with open(output_file, 'w') as f:
        # Line 1: Initial position [m]
        f.write(f"{r0_m[0]:.12e} {r0_m[1]:.12e} {r0_m[2]:.12e}\n")
        # Line 2: Initial velocity [m/s]
        f.write(f"{v0_m_s[0]:.12e} {v0_m_s[1]:.12e} {v0_m_s[2]:.12e}\n")
        # Line 3: Time step [s]
        f.write(f"{dt_seconds:.12e}\n")
        # Line 4: Stop time [s]
        f.write(f"{t_stop_seconds:.12e}\n")
    
    print("\n" + "=" * 60)
    print("Extraction Complete!")
    print("=" * 60)
    print(f"\nYou can now run the Fortran program:")
    print(f"  ./propagate_orbit")
    

if __name__ == '__main__':
    # Parse command line arguments
    custom_dt = None
    if len(sys.argv) > 1:
        try:
            custom_dt = float(sys.argv[1])
            print(f"Custom time step requested: {custom_dt} seconds")
        except ValueError:
            print(f"Error: Invalid time step '{sys.argv[1]}'. Using default from file.")
    
    extract_initial_state(custom_dt=custom_dt)
