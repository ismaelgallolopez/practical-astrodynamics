#!/usr/bin/env python3
"""
Fetch Sun and Moon positions from JPL Horizons for TLE epoch date.
Reads TLE epoch from tle.txt and queries Horizons for positions at start of that day.
"""

import numpy as np
import urllib.request
from datetime import datetime, timedelta

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
    
    print(f"\nQuerying {body_name} position at: {date_str} 00:00 UTC")
    
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
    
    print(f"  X = {x_m:20.6f} m ({x_km:15.6f} km)")
    print(f"  Y = {y_m:20.6f} m ({y_km:15.6f} km)")
    print(f"  Z = {z_m:20.6f} m ({z_km:15.6f} km)")
    print(f"  Distance = {np.sqrt(x_m**2 + y_m**2 + z_m**2)/1e9:.6f} × 10⁹ m")
    
    # Extract GM (gravitational parameter) from object data section
    gm_km3s2 = None
    for line in lines:
        # Look for "GM, km^3/s^2" or "GM (km^3/s^2)"
        if ('GM,' in line or 'GM (' in line) and 'km^3' in line and 's^2' in line:
            import re
            # Extract the number after "GM" specifically
            # Format: "Radius (IAU), km      = 1737.4           GM, km^3/s^2          = 4902.800066"
            # Need to find the "=" that comes AFTER "GM"
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
        print(f"  GM = {gm_m3s2:.12e} m³/s² ({gm_km3s2} km³/s²)")
    else:
        print(f"  Warning: Could not extract {body_name} GM from Horizons data")
        gm_m3s2 = None
    
    # Extract radius from object data section
    radius_km = None
    for line in lines:
        if 'Radius' in line or 'Mean radius' in line:
            # Look for patterns like "696000" or "1737.4" or "6.965(10^5)"
            import re
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
        print(f"  Radius = {radius_m:.6e} m ({radius_km:.6f} km)")
    else:
        print(f"  Warning: Could not extract {body_name} radius from Horizons data")
        radius_m = None
    
    return x_m, y_m, z_m, radius_m, gm_m3s2

# Read TLE file
tle_file = "data/sgp4_reference/tle.txt"
print("=" * 70)
print("FETCHING THIRD BODY POSITIONS FROM JPL HORIZONS")
print("=" * 70)
print(f"\nReading TLE from: {tle_file}")

with open(tle_file, 'r') as f:
    lines = f.readlines()
    tle_line1 = lines[1].strip()  # Line 1 contains epoch

epoch_date = parse_tle_epoch(tle_line1)
date_str = epoch_date.strftime('%Y-%m-%d')

print(f"TLE epoch extracted: {tle_line1[18:32]} (day of year)")
print(f"Epoch date: {date_str}")
print(f"Reference frame: ICRF (inertial frame)")
print(f"Center: Geocenter (Earth center)")

# Fetch Sun position
sun_x, sun_y, sun_z, sun_radius, sun_gm = fetch_body_position('10', 'Sun', date_str)

# Fetch Moon position
moon_x, moon_y, moon_z, moon_radius, moon_gm = fetch_body_position('301', 'Moon', date_str)

# Use default Moon radius if not found
if moon_radius is None:
    moon_radius = 1737.4e3  # Moon mean radius in meters
    print(f"  Using default Moon radius: {moon_radius:.6e} m")

# Use default GM values if not found
if sun_gm is None:
    sun_gm = 1.32712440018e20  # IAU 2015 value in m^3/s^2
    print(f"  Using default Sun GM: {sun_gm:.12e} m³/s²")

if moon_gm is None:
    moon_gm = 4.9028e12  # IAU value in m^3/s^2
    print(f"  Using default Moon GM: {moon_gm:.12e} m³/s²")

# Save to file
output_file = "data/sgp4_reference/third_body_positions.txt"
print(f"\nSaving positions to: {output_file}")

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

print("\nPositions saved successfully!")
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"\nSun position (geocentric):")
print(f"  [{sun_x:.6e}, {sun_y:.6e}, {sun_z:.6e}] m")
print(f"  Radius: {sun_radius:.6e} m")
print(f"  GM: {sun_gm:.12e} m³/s²")
print(f"\nMoon position (geocentric):")
print(f"  [{moon_x:.6e}, {moon_y:.6e}, {moon_z:.6e}] m")
print(f"  Radius: {moon_radius:.6e} m")
print(f"  GM: {moon_gm:.12e} m³/s²")
print("\n" + "=" * 70)
