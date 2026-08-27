# Orbit Propagation using SGP4

This program reads TLE data from a file, generates a time domain, and propagates a satellite orbit using the SGP4 algorithm.

## Features

- Read TLE data from file
- Generate time domain with specified start, stop, and time step
- Propagate orbit using SGP4 library
- Store results in NumPy arrays (`.npz` format)
- Compute orbital statistics

## Files

- **`main.py`** - Main orbit propagation program
- **`fetch_tle.py`** - Download TLE data from CelesTrak
- **`example_load_data.py`** - Example showing how to load and analyze saved data
- **`data/tle.txt`** - TLE data file (created by `fetch_tle.py`)
- **`data/orbit_propagation.npz`** - Saved orbit propagation results

## Usage

### 1. Fetch TLE Data

First, download TLE data from CelesTrak:

```bash
python fetch_tle.py
```

This saves the TLE to `data/tle.txt`.

### 2. Run Orbit Propagation

Run the main program to propagate the orbit:

```bash
python main.py
```

**Configuration** (edit in `main.py`):
- `start_datetime` - Start time for propagation
- `stop_datetime` - Stop time for propagation
- `time_step_minutes` - Time step in minutes

### 3. Load and Analyze Results

Use the saved data:

```python
import numpy as np

# Load data
data = np.load('data/orbit_propagation.npz')

# Access arrays
positions = data['positions']     # (N, 3) array [km]
velocities = data['velocities']   # (N, 3) array [km/s]
times_jd = data['times_jd']       # (N, 2) array (Julian date)
errors = data['errors']           # (N,) array (error codes)

# Example: compute orbital radius
radii = np.linalg.norm(positions, axis=1)
```

See `example_load_data.py` for more examples.

## Output Data Structure

The propagation results are saved in `data/orbit_propagation.npz` with:

| Key | Shape | Unit | Description |
|-----|-------|------|-------------|
| `times_jd` | (N, 2) | days | Julian dates (jd, fr) |
| `positions` | (N, 3) | km | Position vectors in TEME frame |
| `velocities` | (N, 3) | km/s | Velocity vectors in TEME frame |
| `errors` | (N,) | - | SGP4 error codes (0 = success) |
| `satellite_name` | string | - | Satellite name from TLE |
| `tle_line1` | string | - | TLE line 1 |
| `tle_line2` | string | - | TLE line 2 |

## Example Output

```
======================================================================
ORBIT PROPAGATION USING SGP4
======================================================================

1. Reading TLE data from: data/tle.txt
   Found 1 TLE set(s)

2. Using TLE for: USA 149 (DSP 20)
   Line 1: 1 26356U 00024A   25316.50001387  .00000091  00000+0  00000+0 0  9997
   Line 2: 2 26356  13.0072  13.3677 0001484 255.2148 157.9867  1.00276180 30740

3. Initializing SGP4 propagator...
   Satellite number: 26356
   Epoch: JD 2460992.000014

4. Generating time domain:
   Start: 2025-11-13 00:00:00
   Stop:  2025-11-14 00:00:00
   Step:  10.0 minutes
   Duration: 24.0 hours
   Expected points: 145

5. Propagating orbit...
   Generated 145 state vectors
   Errors: 0

7. Orbital Statistics:
   Altitude range: 35780.2 to 35789.4 km
   Radius range:   42158.3 to 42167.6 km
   Speed range:    3.074 to 3.075 km/s
   Mean radius:    42162.9 km
   Mean speed:     3.075 km/s
```

## Dependencies

- Python 3.12+
- `numpy` - Array operations
- `sgp4` - SGP4 orbit propagator

Install with:
```bash
pip install numpy sgp4
```

## Coordinate Frame

All position and velocity vectors are in the **TEME** (True Equator Mean Equinox) frame, which is the native output of SGP4.

## Notes

- The program handles TLE files with multiple satellites (uses first one)
- Error codes from SGP4 are stored in the `errors` array
- Earth's equatorial radius: 6378.137 km (WGS84)
- Gravitational parameter μ: 398600.4418 km³/s²
