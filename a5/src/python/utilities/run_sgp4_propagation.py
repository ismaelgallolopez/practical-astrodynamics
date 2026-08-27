#!/usr/bin/env python3
"""
Complete SGP4 orbit propagation pipeline.
Fetches TLE, propagates orbit, extracts initial state, and writes outputs for Fortran.

All functionality is self-contained in this script.
"""

import os
import sys
import numpy as np
import urllib.request
import re
from pathlib import Path
from datetime import datetime, timedelta
from sgp4.api import Satrec


# ============================================================================
# TLE Fetching Functions
# ============================================================================

def fetch_tle_from_celestrak(norad_id):
    """Fetch TLE data from Celestrak for a given NORAD ID.
    
    Args:
        norad_id: NORAD catalog number (integer)
        
    Returns:
        Dictionary with keys: 'name', 'line1', 'line2'
    """
    url = f'https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}'
    
    print(f'   Fetching from: {url}')
    with urllib.request.urlopen(url) as resp:
        text = resp.read().decode('utf-8')
    
    # Parse TLE
    lines = [l for l in (ln.strip() for ln in text.splitlines()) if l]
    
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith('1 ') and i + 1 < len(lines) and lines[i+1].startswith('2 '):
            name = lines[i-1] if i >= 1 and not lines[i-1].startswith(('1 ', '2 ')) else 'Unknown'
            return {
                'name': name,
                'line1': lines[i],
                'line2': lines[i+1]
            }
        i += 1
    
    raise ValueError("No valid TLE found in response")


# ============================================================================
# SGP4 Propagation Functions
# ============================================================================

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
        - jd_array: (N,) array of Julian date whole parts
        - fr_array: (N,) array of Julian date fractional parts (days from epoch)
        - satellite: Satrec object
        - times_seconds: (N,) array of times in seconds from epoch
    """
    sat = Satrec.twoline2rv(tle[1], tle[2])

    # Time vector in seconds from TLE epoch
    times_seconds = np.arange(ti, tf + dt, dt, dtype=float)

    # Full Julian date at each step (including fractional epoch!)
    epoch_jd = sat.jdsatepoch + sat.jdsatepochF
    jd_full = epoch_jd + times_seconds / 86400.0

    # Split into integer + fractional parts for sgp4_array
    jd_int = np.floor(jd_full).astype(float)
    jd_frac = jd_full - jd_int

    # Propagate
    e, r_km, v_km_s = sat.sgp4_array(jd_int, jd_frac)
    assert np.all(e == 0), f"SGP4 failed at {np.sum(e != 0)} epochs out of {len(e)}"

    return e, r_km, v_km_s, jd_int, jd_frac, sat, times_seconds


# ============================================================================
# Output Writing Functions
# ============================================================================



def write_sgp4_orbit_fortran(times_seconds, positions, velocities, output_file):
    """Write SGP4 orbit data in format readable by Fortran.
    
    Format: time[s] x[m] y[m] z[m] vx[m/s] vy[m/s] vz[m/s]
    
    Args:
        times_seconds: (N,) array of times in seconds from epoch
        positions: (N, 3) array of positions in km
        velocities: (N, 3) array of velocities in km/s
        output_file: Path to output file
    """
    # Convert to meters and m/s
    pos_m = positions * 1000.0  # km -> m
    vel_ms = velocities * 1000.0  # km/s -> m/s
    
    # Write data
    with open(output_file, 'w') as f:
        for i in range(len(times_seconds)):
            f.write(f"{times_seconds[i]:15.6f}  ")
            f.write(f"{pos_m[i,0]:23.15e}  {pos_m[i,1]:23.15e}  {pos_m[i,2]:23.15e}  ")
            f.write(f"{vel_ms[i,0]:23.15e}  {vel_ms[i,1]:23.15e}  {vel_ms[i,2]:23.15e}\n")
    
    print(f"   Fortran-readable orbit saved to: {output_file}")


# ============================================================================
# Third Body Position Functions
# ============================================================================

def parse_tle_epoch(tle_line1):
    """
    Parse TLE epoch from line 1.
    Format: YYDDDddddd where YY is year (00-99), DDD is day of year, ddddd is fractional day.
    Returns datetime object for start of that calendar day.
    """
    # Extract epoch field (columns 19-32 in line 1)
    epoch_str = tle_line1[18:32].strip()
    
    # Parse year and day
    year_2digit = int(epoch_str[0:2])
    day_of_year = int(epoch_str[2:5])
    
    # Convert 2-digit year to 4-digit (assume 1957-2056 range per TLE convention)
    if year_2digit >= 57:
        year = 1900 + year_2digit
    else:
        year = 2000 + year_2digit
    
    # Create datetime for January 1st of that year, then add days
    epoch_date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    
    return epoch_date


def fetch_body_position(body_id, body_name, date_str):
    """Fetch position, radius, and GM for a celestial body from JPL Horizons."""
    
    # Query parameters
    obj_data = 'YES'  # Get summary data including radius and GM
    ephem_type = 'VECTORS'  # Cartesian state vectors
    center = '500@399'  # Geocenter (Earth center)
    ref_plane = 'FRAME'  # Use ICRF x-y plane
    start_time = f'{date_str}%2000:00'  # Start of TLE epoch day (URL encoded)
    stop_time = f'{date_str}%2000:01'  # One minute later (URL encoded)
    step_size = '1m'  # Single epoch
    vec_table = '2'  # Position and velocity vectors
    vec_labels = 'NO'  # No labels needed
    csv_format = 'YES'  # CSV format
    vec_delta_t = 'NO'  # Don't need TDB-UT
    
    print(f"   Querying {body_name} from JPL Horizons...")
    
    # Build URL
    url = ('https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND=%27' + body_id + '%27&OBJ_DATA=%27' + obj_data
           + '%27&EPHEM_TYPE=%27' + ephem_type + '%27&CENTER=%27' + center + '%27&REF_PLANE=%27' + ref_plane
           + '%27&START_TIME=%27' + start_time + '%27&STOP_TIME=%27' + stop_time + '%27&STEP_SIZE=%27' + step_size
           + '%27&VEC_TABLE=%27' + vec_table + '%27&VEC_LABELS=%27' + vec_labels + '%27&CSV_FORMAT=%27' + csv_format
           + '%27&VEC_DELTA_T=%27' + vec_delta_t + '%27')
    
    # Make request
    response = urllib.request.urlopen(url).read().decode('utf-8')
    
    # Parse response to extract position
    lines = response.split('\n')
    
    # Extract data between $$SOE and $$EOE markers
    data_lines = []
    start = False
    for line in lines:
        if line == '$$SOE':
            start = True
            continue
        if not start:
            continue
        if line == '$$EOE':
            break
        else:
            data_lines.append(line.split(','))
    
    if not data_lines:
        raise ValueError(f"Could not find {body_name} position data in Horizons response")
    
    # Parse the data
    # Format: JDTDB, Calendar_Date, X, Y, Z, VX, VY, VZ
    arr = np.array(data_lines, dtype=object)
    
    # Extract position (columns 2, 3, 4)
    # Positions are in km
    x_km = float(arr[0, 2])
    y_km = float(arr[0, 3])
    z_km = float(arr[0, 4])
    
    # Convert to meters
    x_m = x_km * 1000
    y_m = y_km * 1000
    z_m = z_km * 1000
    
    # Extract GM (gravitational parameter) from object data section
    gm_km3s2 = None
    for line in lines:
        # Look for "GM, km^3/s^2" or "GM (km^3/s^2)"
        if ('GM,' in line or 'GM (' in line) and 'km^3' in line and 's^2' in line:
            # Extract the number after "GM" specifically
            gm_index = line.find('GM')
            if gm_index != -1:
                line_after_gm = line[gm_index:]
                match = re.search(r'=\s*([\d.]+)(?:[Ee]([-+]?\d+))?', line_after_gm)
                if match:
                    mantissa = float(match.group(1))
                    if match.group(2):
                        exponent = int(match.group(2))
                        gm_km3s2 = mantissa * (10 ** exponent)
                    else:
                        gm_km3s2 = mantissa
                    break
    
    if gm_km3s2:
        gm_m3s2 = gm_km3s2 * 1e9  # Convert km^3/s^2 to m^3/s^2
    else:
        gm_m3s2 = None
    
    # Extract radius from object data section
    radius_km = None
    for line in lines:
        if 'Radius' in line or 'Mean radius' in line:
            # Handle scientific notation like "6.965(10^5)"
            match = re.search(r'([\d.]+)\(10\^(\d+)\)', line)
            if match:
                mantissa = float(match.group(1))
                exponent = int(match.group(2))
                radius_km = mantissa * (10 ** exponent)
            else:
                # Try to find a number followed by "km"
                match = re.search(r'([\d.]+)\s*km', line, re.IGNORECASE)
                if match:
                    radius_km = float(match.group(1))
    
    if radius_km:
        radius_m = radius_km * 1000
    else:
        radius_m = None
    
    return x_m, y_m, z_m, radius_m, gm_m3s2


def fetch_third_body_positions(tle_line1, output_dir):
    """Fetch Sun and Moon positions from JPL Horizons for TLE epoch date."""
    
    epoch_date = parse_tle_epoch(tle_line1)
    date_str = epoch_date.strftime('%Y-%m-%d')
    
    print(f"   TLE epoch date: {date_str}")
    
    # Fetch Sun position
    sun_x, sun_y, sun_z, sun_radius, sun_gm = fetch_body_position('10', 'Sun', date_str)
    
    # Fetch Moon position
    moon_x, moon_y, moon_z, moon_radius, moon_gm = fetch_body_position('301', 'Moon', date_str)
    
    # Use default values if not found
    if moon_radius is None:
        moon_radius = 1737.4e3  # Moon mean radius in meters
    
    if sun_gm is None:
        sun_gm = 1.32712440018e20  # IAU 2015 value in m^3/s^2
    
    if moon_gm is None:
        moon_gm = 4.9028e12  # IAU value in m^3/s^2
    
    # Save to file
    output_file = output_dir / "third_body_positions.txt"
    
    with open(output_file, 'w') as f:
        f.write("# Third body positions for orbital perturbation calculations\n")
        f.write(f"# TLE epoch: {date_str} 00:00 UTC\n")
        f.write(f"# Reference frame: ICRF (inertial frame)\n")
        f.write(f"# Center: Geocenter (Earth center)\n")
        f.write(f"#\n")
        f.write(f"# Sun radius: {sun_radius:.6e} m\n")
        f.write(f"# Sun GM: {sun_gm:.12e} m³/s²\n")
        f.write(f"# Moon radius: {moon_radius:.6e} m\n")
        f.write(f"# Moon GM: {moon_gm:.12e} m³/s²\n")
        f.write(f"#\n")
        f.write(f"# Format: X [m], Y [m], Z [m], GM [m³/s²]\n")
        f.write(f"#\n")
        f.write(f"# Sun position (geocentric ICRF)\n")
        f.write(f"{sun_x:.15e} {sun_y:.15e} {sun_z:.15e} {sun_gm:.15e}\n")
        f.write(f"#\n")
        f.write(f"# Moon position (geocentric ICRF)\n")
        f.write(f"{moon_x:.15e} {moon_y:.15e} {moon_z:.15e} {moon_gm:.15e}\n")
    
    print(f"   Third body positions saved to: {output_file}")
    
    return output_file


def main():
    """Main SGP4 propagation pipeline."""
    
    # ============================================================================
    # Configuration
    # ============================================================================
    
    # Satellite to track
    NORAD_ID = 26356  # student number: 6541356
    
    # Time domain parameters
    N_TIMESTEPS = 150  # Number of timesteps
    T_STOP_HOURS = 24.0*0.2    # Total propagation time in hours
    
    # Output directory
    OUTPUT_DIR = Path('data/sgp4_reference')
    
    print("=" * 80)
    print("SGP4 ORBIT PROPAGATION PIPELINE")
    print("=" * 80)
    
    # ============================================================================
    # Step 1: Fetch TLE data
    # ============================================================================
    
    print("\n[1/5] Fetching TLE data from Celestrak...")
    
    tle_file = OUTPUT_DIR / 'tle.txt'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        tle_data = fetch_tle_from_celestrak(NORAD_ID)
        
        # Save TLE to file
        with open(tle_file, 'w') as f:
            f.write(f"{tle_data['name']}\n")
            f.write(f"{tle_data['line1']}\n")
            f.write(f"{tle_data['line2']}\n")
        
        print(f"   Satellite: {tle_data['name']}")
        print(f"   NORAD ID: {NORAD_ID}")
        print(f"   TLE saved to: {tle_file}")
        
    except Exception as e:
        print(f"   Error fetching TLE: {e}")
        print(f"   Trying to read from existing file: {tle_file}")
        
        if not tle_file.exists():
            print("   ERROR: No TLE file found. Cannot proceed.")
            return
        
        # Read existing TLE
        with open(tle_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        tle_data = {
            'name': lines[0],
            'line1': lines[1],
            'line2': lines[2]
        }
        
        print(f"   Using existing TLE for: {tle_data['name']}")
    
    # ============================================================================
    # Step 2: Fetch third body positions
    # ============================================================================
    
    print("\n[2/6] Fetching third body positions from JPL Horizons...")
    
    try:
        third_body_file = fetch_third_body_positions(tle_data['line1'], OUTPUT_DIR)
    except Exception as e:
        print(f"   Error fetching third body positions: {e}")
        print(f"   Continuing without third body positions...")
    
    # ============================================================================
    # Step 3: Setup time domain
    # ============================================================================
    
    print("\n[3/6] Setting up time domain...")
    
    ti = 0.0  # Start at TLE epoch
    tf = T_STOP_HOURS * 3600.0  # Convert hours to seconds
    
    # Calculate dt from number of timesteps
    dt = tf / (N_TIMESTEPS - 1)  # -1 to include both endpoints
    
    print(f"   Number of timesteps: {N_TIMESTEPS}")
    print(f"   Total time: {T_STOP_HOURS} hours ({tf} seconds)")
    print(f"   Time step (calculated): {dt:.6f} seconds")
    print(f"   Start: ti = {ti} s (TLE epoch)")
    print(f"   End: tf = {tf} s")
    
    # ============================================================================
    # Step 4: Propagate orbit using SGP4
    # ============================================================================
    
    print("\n[4/6] Propagating orbit with SGP4...")
    
    tle = (tle_data['name'], tle_data['line1'], tle_data['line2'])
    
    errors, positions, velocities, jd, fr, satellite, times_seconds = sgp4_propagate(
        tle, ti, tf, dt
    )
    
    n_actual = len(positions)
    print(f"   Generated {n_actual} state vectors")
    print(f"   Errors: {sum(errors != 0)}")
    
    if sum(errors != 0) > 0:
        print("   WARNING: SGP4 encountered errors!")
        return
    
    # Statistics
    radii = np.linalg.norm(positions, axis=1)
    speeds = np.linalg.norm(velocities, axis=1)
    
    print(f"\n   Orbital statistics:")
    print(f"   - Radius: {radii.min():.1f} to {radii.max():.1f} km")
    print(f"   - Altitude: {radii.min()-6378.137:.1f} to {radii.max()-6378.137:.1f} km")
    print(f"   - Speed: {speeds.min():.3f} to {speeds.max():.3f} km/s")
    
    # ============================================================================
    # Step 5: Extract and save initial state
    # ============================================================================
    
    print("\n[5/6] Extracting initial state...")
    
    initial_state_file = OUTPUT_DIR / 'initial_state.txt'
    
    # Initial state from SGP4
    r0 = positions[0] * 1000.0  # km -> m
    v0 = velocities[0] * 1000.0  # km/s -> m/s
    
    # Save initial state (without comments for Fortran compatibility)
    with open(initial_state_file, 'w') as f:
        f.write(f"{r0[0]:23.15e}  {r0[1]:23.15e}  {r0[2]:23.15e}\n")
        f.write(f"{v0[0]:23.15e}  {v0[1]:23.15e}  {v0[2]:23.15e}\n")
        f.write(f"{dt:23.15e}\n")
        f.write(f"{tf:23.15e}\n")
    
    print(f"   Initial position [m]: [{r0[0]:.6e}, {r0[1]:.6e}, {r0[2]:.6e}]")
    print(f"   Initial velocity [m/s]: [{v0[0]:.6e}, {v0[1]:.6e}, {v0[2]:.6e}]")
    print(f"   Saved to: {initial_state_file}")
    
    # ============================================================================
    # Step 6: Save outputs
    # ============================================================================
    
    print("\n[6/6] Saving outputs...")
    
    # Save NumPy binary format (for Python)
    times_jd = np.column_stack([jd, fr])
    npz_file = OUTPUT_DIR / 'orbit_propagation.npz'
    
    np.savez(
        npz_file,
        times_jd=times_jd,
        positions=positions,
        velocities=velocities,
        errors=errors,
        satellite_name=tle_data['name'],
        tle_line1=tle_data['line1'],
        tle_line2=tle_data['line2']
    )
    
    print(f"   NumPy binary saved to: {npz_file}")
    
    # Save Fortran-readable ASCII format
    fortran_file = OUTPUT_DIR / 'sgp4_orbit.txt'
    write_sgp4_orbit_fortran(times_seconds, positions, velocities, fortran_file)
    
    # Summary
    print("\n" + "=" * 80)
    print("PROPAGATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  1. TLE data:         {tle_file}")
    print(f"  2. Third bodies:     {OUTPUT_DIR / 'third_body_positions.txt'}")
    print(f"  3. Initial state:    {initial_state_file}")
    print(f"  4. Orbit (NumPy):    {npz_file}")
    print(f"  5. Orbit (Fortran):  {fortran_file}")
    print(f"\nConfiguration:")
    print(f"  - Satellite: {tle_data['name']} (NORAD {NORAD_ID})")
    print(f"  - Timesteps: {N_TIMESTEPS}")
    print(f"  - Time step: {dt:.6f} s")
    print(f"  - Duration: {T_STOP_HOURS} hours")
    print(f"  - Data points: {n_actual}")
    print("=" * 80)


if __name__ == '__main__':
    main()
