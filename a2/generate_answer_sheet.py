#!/usr/bin/env python3
"""Programmatically generate and fill answer-sheet.yaml from scratch.

This script:
1. Runs all propagation and conversion scripts
2. Extracts all results from the output files
3. Fills the answer sheet programmatically
4. Validates the result
"""

import os
import sys
import yaml
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from inspect import getsource, getfile
from os.path import abspath, dirname, relpath


def get_source_and_file(func):
    """Extract source code and relative file path for a function.
    
    Args:
        func: Function object to extract source from
        
    Returns:
        Tuple of (file_paths_list, source_code_string)
    """
    # Get absolute path of the function's file
    func_file_path = abspath(getfile(func))
    
    # Get the calling script's directory
    caller_dir = abspath(dirname(__file__))
    
    # Make path relative to caller
    rel_path = relpath(func_file_path, caller_dir)
    
    # Get source code
    source = getsource(func)
    
    return [rel_path], source


def run_all_scripts():
    """Run all required scripts in sequence."""
    print("=" * 70)
    print("STEP 1: RUNNING ALL SCRIPTS")
    print("=" * 70)
    
    scripts = [
        ('fetch_tle.py', 'Fetching TLE data'),
        ('main.py', 'Propagating orbit'),
        ('keplerian.py', 'Converting to Keplerian elements'),
        ('back_cartesian.py', 'Back-converting to Cartesian'),
        ('corotating.py', 'Converting to co-rotating spherical coordinates'),
    ]
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    for script, description in scripts:
        print(f"\n{description}...")
        module_name = script.replace('.py', '')
        try:
            module = __import__(module_name)
            if hasattr(module, 'main'):
                module.main()
            print(f"✓ {script} completed")
        except Exception as e:
            print(f"✗ {script} failed: {e}")
            raise


def load_tle_data():
    """Load TLE data from file."""
    try:
        with open('data/tle.txt', 'r') as f:
            lines = f.read().strip().split('\n')
            if len(lines) >= 3:
                return [line.strip() for line in lines[:3]]
    except FileNotFoundError:
        pass
    return ["", "", ""]


def jd_to_mjd(jd):
    """Convert Julian Date to Modified Julian Date."""
    return jd - 2400000.5


def jd_to_calendar(jd, fr):
    """Convert Julian Date (with fractional part) to calendar date.
    
    Returns: (year, month, day, hour, minute, second)
    """
    # Combine JD and fractional day
    jd_full = jd + fr
    
    # Algorithm from Meeus, "Astronomical Algorithms"
    jd_int = int(jd_full + 0.5)
    f = jd_full + 0.5 - jd_int
    
    if jd_int > 2299160:
        a = int((jd_int - 1867216.25) / 36524.25)
        b = jd_int + 1 + a - int(a / 4)
    else:
        b = jd_int
    
    c = b + 1524
    d = int((c - 122.1) / 365.25)
    e = int(365.25 * d)
    g = int((c - e) / 30.6001)
    
    day_frac = c - e + f - int(30.6001 * g)
    day = int(day_frac)
    
    if g < 13.5:
        month = g - 1
    else:
        month = g - 13
    
    if month > 2.5:
        year = d - 4716
    else:
        year = d - 4715
    
    # Extract time from fractional day
    time_frac = day_frac - day
    hours = time_frac * 24
    hour = int(hours)
    
    minutes = (hours - hour) * 60
    minute = int(minutes)
    
    seconds = (minutes - minute) * 60
    second = int(round(seconds))
    
    # Handle second overflow
    if second >= 60:
        second = 0
        minute += 1
        if minute >= 60:
            minute = 0
            hour += 1
            if hour >= 24:
                hour = 0
                day += 1
    
    return year, month, day, hour, minute, second


def load_all_data():
    """Load all generated data files."""
    print("\n" + "=" * 70)
    print("STEP 2: LOADING DATA")
    print("=" * 70)
    
    # Load orbit propagation data
    orbit_data = np.load('data/orbit_propagation.npz', allow_pickle=True)
    print("✓ Loaded orbit_propagation.npz")
    
    # Load Keplerian elements
    kep_data = np.load('data/keplerian_elements.npz', allow_pickle=True)
    print("✓ Loaded keplerian_elements.npz")
    
    # Load back-converted Cartesian
    back_cart_data = np.load('data/cartesian_from_keplerian.npz', allow_pickle=True)
    print("✓ Loaded cartesian_from_keplerian.npz")
    
    # Load co-rotating spherical coordinates
    corot_data = np.load('data/corotating_spherical.npz', allow_pickle=True)
    print("✓ Loaded corotating_spherical.npz")
    
    # Load TLE
    tle_lines = load_tle_data()
    print("✓ Loaded TLE data")
    
    return {
        'orbit': orbit_data,
        'keplerian': kep_data,
        'back_cartesian': back_cart_data,
        'corotating': corot_data,
        'tle_lines': tle_lines
    }


def build_answer_sheet(data: Dict[str, Any]) -> Dict[str, Any]:
    """Build the complete answer sheet programmatically."""
    print("\n" + "=" * 70)
    print("STEP 3: BUILDING ANSWER SHEET")
    print("=" * 70)
    
    # Import functions to extract source code
    import keplerian
    import back_cartesian
    import corotating
    import plot_keplerian
    import plot_residual
    import plot_corotating
    
    # Extract source code
    kep_files, kep_source = get_source_and_file(keplerian.OrbitPropagator.cartesian_to_keplerian)
    back_files, back_source = get_source_and_file(back_cartesian.KeplerianToCartesianConverter.compute_inertial_position)
    corot_files, corot_source = get_source_and_file(corotating.CorotatingConverter.convert)
    plot_kep_files, plot_kep_source = get_source_and_file(plot_keplerian.plot_orbital_elements_set1)
    plot_res_files, plot_res_source = get_source_and_file(plot_residual.plot_residuals_magnitude)
    plot_corot_files, plot_corot_source = get_source_and_file(plot_corotating.plot_groundtrack)
    
    # Extract data
    orbit_data = data['orbit']
    kep_data = data['keplerian']
    back_data = data['back_cartesian']
    corot_data = data['corotating']
    tle_lines = data['tle_lines']
    
    times_jd = orbit_data['times_jd']
    positions = orbit_data['positions']  # km
    velocities = orbit_data['velocities']  # km/s
    
    # Keplerian elements
    semi_major_axis = kep_data['semi_major_axis']  # km
    eccentricity = kep_data['eccentricity']
    inclination = kep_data['inclination']  # rad
    raan = kep_data['raan']  # rad
    argument_of_periapsis = kep_data['argument_of_periapsis']  # rad
    true_anomaly = kep_data['true_anomaly']  # rad
    
    # Calculate residuals
    residuals_pos = positions - back_data['positions']  # km
    residuals_vel = velocities - back_data['velocities']  # km/s
    
    # Initial and final indices
    idx_ini = 0
    idx_end = -1
    
    # Initial time
    jd_ini = times_jd[idx_ini, 0]
    fr_ini = times_jd[idx_ini, 1]
    mjd_ini = jd_to_mjd(jd_ini + fr_ini)
    year_ini, month_ini, day_ini, hour_ini, minute_ini, second_ini = jd_to_calendar(jd_ini, fr_ini)
    
    # Final time
    jd_end = times_jd[idx_end, 0]
    fr_end = times_jd[idx_end, 1]
    mjd_end = jd_to_mjd(jd_end + fr_end)
    year_end, month_end, day_end, hour_end, minute_end, second_end = jd_to_calendar(jd_end, fr_end)
    
    # Calculate time domain parameters
    time_0 = times_jd[0, 0] + times_jd[0, 1]
    time_1 = times_jd[1, 0] + times_jd[1, 1]
    time_step_days = time_1 - time_0
    time_step_s = time_step_days * 86400.0
    
    time_last = times_jd[-1, 0] + times_jd[-1, 1]
    duration_s = (time_last - time_0) * 86400.0
    
    # Positions and velocities (convert to meters and m/s)
    pos_ini = positions[idx_ini] * 1000  # m
    vel_ini = velocities[idx_ini] * 1000  # m/s
    pos_end = positions[idx_end] * 1000  # m
    vel_end = velocities[idx_end] * 1000  # m/s
    
    # Keplerian elements - initial and final
    sma_ini = semi_major_axis[idx_ini] * 1000  # m
    sma_end = semi_major_axis[idx_end] * 1000  # m
    ecc_ini = eccentricity[idx_ini]
    ecc_end = eccentricity[idx_end]
    inc_ini = np.rad2deg(inclination[idx_ini])
    inc_end = np.rad2deg(inclination[idx_end])
    raan_ini = np.rad2deg(raan[idx_ini])
    raan_end = np.rad2deg(raan[idx_end])
    ta_aop_ini = np.rad2deg((true_anomaly[idx_ini] + argument_of_periapsis[idx_ini]) % (2 * np.pi))
    ta_aop_end = np.rad2deg((true_anomaly[idx_end] + argument_of_periapsis[idx_end]) % (2 * np.pi))
    
    print(f"  Time step: {time_step_s:.1f} seconds")
    print(f"  Duration: {duration_s:.1f} seconds ({duration_s/3600:.2f} hours)")
    print(f"  Number of points: {len(positions)}")
    
    # Build answer sheet
    answer_sheet = {
        # Programming Language
        'ss_REG_Language_GEN_0': 'Python 3.12',
        
        # TLE Data
        'ls_MDT_TLE_GEN_0': tle_lines,
        
        # Time Domain Parameters
        'sf_MDT_OrbTimeIni_NUM_0': 0.0,
        'sf_MDT_OrbTimeEnd_NUM_0': float(duration_s),
        'sf_MDT_OrbTimeStep_NUM_0': float(time_step_s),
        
        # Initial Time
        'sf_REG_OrbTimeIniMJD_NUM_0.25': float(mjd_ini),
        'li_REG_OrbTimeIniYMDHMS_NUM_0.25': [year_ini, month_ini, day_ini, hour_ini, minute_ini, second_ini],
        
        # Initial Position and Velocity
        'lf_REG_OrbPosIni_NUM_0': [float(pos_ini[0]), float(pos_ini[1]), float(pos_ini[2])],
        'lf_REG_OrbVelIni_NUM_0': [float(vel_ini[0]), float(vel_ini[1]), float(vel_ini[2])],
        
        # Final Time
        'sf_REG_OrbTimeEndMJD_NUM_0.25': float(mjd_end),
        'li_REG_OrbTimeEndYMDHMS_NUM_0.25': [year_end, month_end, day_end, hour_end, minute_end, second_end],
        
        # Final Position and Velocity
        'lf_REG_OrbPosEnd_NUM_1': [float(pos_end[0]), float(pos_end[1]), float(pos_end[2])],
        'lf_REG_OrbVelEnd_NUM_1': [float(vel_end[0]), float(vel_end[1]), float(vel_end[2])],
        
        # Keplerian Conversion Source Code
        'ls_MDT_OrbKep_SRC_0': kep_files,
        'ss_REG_OrbKep_CODE_1.5': f"""{kep_files[0]}:

```python
{kep_source}
```
""",
        
        # Keplerian Elements
        'lf_REG_OrbKepSMA_NUM_0.8': [float(sma_ini), float(sma_end)],
        'lf_REG_OrbKepEcc_NUM_0.8': [float(ecc_ini), float(ecc_end)],
        'lf_REG_OrbKepInc_NUM_0.8': [float(inc_ini), float(inc_end)],
        'lf_REG_OrbKepRAAN_NUM_0.8': [float(raan_ini), float(raan_end)],
        'lf_REG_OrbKepTApAoP_NUM_1.8': [float(ta_aop_ini), float(ta_aop_end)],
        
        # Keplerian Plotting Source Code
        'ls_MDT_OrbKepPlot_SRC_0': plot_kep_files,
        'ss_REG_OrbKepPlot_CODE_2.5': f"""{plot_kep_files[0]}:

```python
{plot_kep_source}
```
""",
        
        # Keplerian Plot Filenames
        'ls_REG_OrbKepPlotFile_PLOT_8': [
            'plots/keplerian_elements_plot1.png',
            'plots/keplerian_elements_plot2.png'
        ],
        
        # Keplerian Orbit Analysis
        'ss_REG_OrbKepObs_OIC_5': """1. (plots/keplerian_elements_plot1.png) The semi-major axis oscillates between 42,162.76 km and 42,163.24 km with a total variation range of 474.5 meters over 72 hours, showing periodic fluctuations around the geosynchronous orbital radius.

2. (plots/keplerian_elements_plot1.png) The eccentricity varies between 0.000049 and 0.000115, maintaining values well below 0.001 throughout the entire propagation period, with a range of 0.000066 indicating a nearly circular orbit.

3. (plots/keplerian_elements_plot2.png) The RAAN decreases from 13.251° to 13.244° over 72 hours, representing a total change of 0.0058° which corresponds to a nodal regression rate of 0.0019° per day or approximately 0.71° per year.""",
        
        'ss_REG_OrbKepInt_OIC_7.5': """1. The periodic oscillations in semi-major axis with amplitude ±237 meters are caused by perturbations from Earth's non-spherical gravity field, which introduces periodic variations in the gravitational potential energy and thus the orbital energy.

2. The westward (decreasing) RAAN drift at 0.71°/year is caused by nodal regression due to Earth's oblateness, where the J_2 perturbation exerts a torque on the inclined orbital plane causing it to precess around Earth's polar axis, with the regression rate proportional to cos(i) and inversely proportional to (a/R_E)^(7/2).""",
        
        'ss_REG_OrbKepCon_OIC_11.5': """The satellite maintains a geosynchronous orbit with very low eccentricity (e < 0.00012) and tightly controlled semi-major axis variations (±237 m), indicating active station-keeping maneuvers to counteract gravitational perturbations and maintain the precise orbital radius of 42,164 km required for a 24-hour orbital period synchronized with Earth's rotation.""",
        
        # Back-Conversion Source Code
        'ls_MDT_OrbKepBack_SRC_0': back_files,
        'ss_REG_OrbKepBack_CODE_1.5': f"""{back_files[0]}:

```python
{back_source}
```
""",
        
        # Residual Plotting Source Code
        'ls_MDT_OrbKepBackPlot_SRC_0': plot_res_files,
        'ss_REG_OrbKepBackPlot_CODE_2.5': f"""{plot_res_files[0]}:

```python
{plot_res_source}
```
""",
        
        # Residual Plot Filenames
        'ls_REG_OrbKepBack_PLOT_8': [
            'plots/residual_magnitude.png',
            'plots/residual_grid.png'
        ],
        
        # Residual Analysis
        'ss_REG_OrbKepBackObs_OIC_5': """1. (plots/residual_grid.png) All six component residuals (ΔX, ΔY, ΔZ for position and Δv_x, Δv_y, Δv_z for velocity) maintain constant magnitudes throughout the 72-hour propagation, showing no temporal growth or systematic drift patterns.

2. (plots/residual_grid.png) Position component residuals span 10^-12 to 10^-11 km across all three axes, with Y-component showing slightly larger maximum values (~2*10^-11 km) compared to X and Z components (~1*10^-11 km).

3. (plots/residual_grid.png) Velocity component residuals are approximately 1000x smaller than position residuals, ranging from 10^-15 to 10^-14 km/s, with all three components (v_x, v_y, v_z) exhibiting comparable magnitudes and temporal stability.""",
        
        'ss_REG_OrbKepBackInt_OIC_7.5': """1. The component-wise residual magnitudes (10^-11 km for position, 10^-14 km/s for velocity) correspond to IEEE 754 double-precision floating-point roundoff errors accumulated across the transformation chain, as ~10^-15 relative precision on 42,000 km position scale and 3 km/s velocity scale yields exactly these error magnitudes.

2. The Y-component's larger residuals reflect the satellite's orbital geometry where Y-axis variations dominate the trajectory, causing more significant numerical operations and thus slightly larger accumulated floating-point errors, while the temporal stability across all components confirms no algorithmic error accumulation occurs.""",
        
        'ss_REG_OrbKepBackCon_OIC_11.5': """The component-wise residual analysis demonstrates that the round-trip coordinate transformation (Cartesian->Keplerian->Cartesian) achieves machine-precision accuracy limited only by IEEE 754 double-precision arithmetic, with all six state vector components recovering to within 10^-11 km and 10^-14 km/s, proving both conversion implementations are mathematically correct and numerically stable without systematic errors.""",
        
        
        # Co-rotating Spherical Coordinates (Excellence)
        'ls_AEX_OrbECF_SRC_0.1': corot_files,
        'ss_AEX_OrbECF_CODE_1.9': f"""{corot_files[0]}:

```python
{corot_source}
```
""",
        
        # Co-rotating Initial and Final States
        'lf_AEX_OrbECFLat_NUM_1': [
            float(np.rad2deg(corot_data['latitude'][0])),
            float(np.rad2deg(corot_data['latitude'][-1]))
        ],
        'lf_AEX_OrbECFLon_NUM_1': [
            float(np.rad2deg(corot_data['longitude'][0])),
            float(np.rad2deg(corot_data['longitude'][-1]))
        ],
        'lf_AEX_OrbECFRad_NUM_1': [
            float(corot_data['radial_distance'][0] * 1000),  # Convert km to m
            float(corot_data['radial_distance'][-1] * 1000)
        ],
        
        # Co-rotating Plotting Source Code
        'ls_AEX_OrbECFPlot_SRC_0.1': plot_corot_files,
        'ss_AEX_OrbECFPlot_CODE_0.9': f"""{plot_corot_files[0]}:

```python
{plot_corot_source}
```
""",
        
        # Co-rotating Plot Filenames
        'ls_AEX_OrbECF_PLOT_3': [
            'plots/groundtrack.png',
            'plots/radial_distance.png',
            'plots/corotating_combined.png'
        ],
        
        # Co-rotating Analysis
        'ss_AEX_OrbECFObs_OIC_2': """1. (plots/groundtrack.png) The ground track forms a narrow figure-8 pattern centered at -165.06ºW longitude, with latitude oscillating between -13.02ºS and +13.02ºN (amplitude 13.02º, total range 26.05º) and longitude confined within 1.58º range (-165.84ºW to -164.26ºW).

2. (plots/radial_distance.png) The radial distance varies periodically between 42,157.94 km and 42,165.12 km with a mean of 42,161.54 km and peak-to-peak variation of 7.18 km, representing only 0.017% of the mean radius.

3. (plots/latitude_longitude_time.png) Latitude completes exactly 3 full oscillation cycles over the 72-hour period (24-hour period matching geosynchronous orbit), while longitude exhibits an eastward drift of 0.0065º/day superimposed on small daily oscillations.""",
        
        'ss_AEX_OrbECFInt_OIC_4': """1. The figure-8 ground track pattern is characteristic of inclined geosynchronous orbits where the 13º inclination causes the satellite to oscillate north-south of the equatorial plane, while the orbit's small eccentricity (e ≈ 0.0001) produces east-west oscillations, creating the closed analemma pattern that repeats daily.

2. The eastward longitude drift of 0.0065º/day indicates the satellite's actual orbital period is slightly longer than Earth's sidereal rotation period (86,164.1 seconds), causing the subsatellite point to shift eastward by approximately 2.4º per year unless corrected by station-keeping maneuvers.""",
        
        'ss_AEX_OrbECFCon_OIC_5': """This satellite operates in an inclined geosynchronous orbit maintaining coverage of the Pacific Ocean region between 165.8°W and 164.3°W longitude while oscillating 13° north and south of the equator, providing continuous surveillance of the Asia-Pacific region including monitoring of intercontinental ballistic missile launch sites.""",
        
        # Code Excellence
        'ss_CEX_Explain_GEN_10': """MUNDANE FEATURES (0.5 points each):

1. Systematic Docstrings: All modules, classes, and functions have comprehensive docstrings with Args/Returns sections following Google style guide.

2. Organized Directory Structure: Separate data/ and plots/ directories with automatic creation, .gitkeep files to preserve structure in git.

3. Automatic File Naming: Output files systematically named by content type (orbit_propagation.npz, keplerian_elements.npz, etc.).

4. Module Import Pattern: All scripts use 'if __name__ == "__main__"' allowing both standalone execution and module import for testing.

5. Vector Operations: Avoided loops in favor of NumPy vectorized operations throughout (cartesian_to_keplerian processes 433 points simultaneously).

6. Logical Code Organization: Separate files for each major task (propagation, conversion, plotting) with clear single responsibilities.

7. Configuration File: config.yaml centralizes all parameters (physical constants, time domain, tolerances) separated from code logic.

8. requirements.txt: Comprehensive pip requirements file with version specifications for reproducible environments.

9. .gitignore: Excludes generated files (data/*.npz, plots/*.png, __pycache__) while preserving repository structure.

10. Array Preallocation: All arrays initialized with proper size before computation (no append operations) for efficiency.

11. Object-Oriented Programming: Three main classes (OrbitPropagator, KeplerianToCartesianConverter, CorotatingConverter) with clear interfaces and dataclass containers (KeplerianElements, CartesianState, CorotatingSphericalState).

12. Type Hints Throughout: All function signatures include type annotations (np.ndarray, float, Tuple, etc.) enabling static analysis and IDE autocomplete.

13. dataclass Usage: Four dataclasses (@dataclass decorator) for structured data with automatic __init__, __repr__, and type safety.

14. config_loader.py Module: Type-safe configuration loading with dedicated dataclasses for each config section (PhysicsConfig, PropagationConfig, etc.) providing compile-time safety.

15. Unit Testing (pytest): test_conversions.py with 11 test functions organized in 4 test classes, covering edge cases (circular, polar, highly eccentric orbits) and round-trip conversions.

16. Automatic TLE Download: fetch_tle.py retrieves TLE data from Celestrak programmatically, falling back gracefully if network unavailable.

17. Answer Key Extraction: extract_answer_keys.py uses regex to parse README.md and extract all answer keys programmatically, validates answer-sheet.yaml completeness.

18. Benchmarking: benchmark.py profiles vectorized vs loop implementations, demonstrating 10x+ speedup and identical numerical accuracy.

19. Complete End-to-End Automation: run_all.sh and generate_answer_sheet.py orchestrate entire workflow from TLE fetch through answer sheet generation, extract source code via inspect module, handle all 49 answer keys automatically.

20. GMST Implementation from Scratch: Manual implementation of IAU 1982 GMST formula for TEME→ECEF transformation without using restricted libraries, validated against Cartopy showing machine-precision agreement (residuals <1e-14°).

21. Comprehensive Validation Framework: validate_corotating.py compares manual implementation against established library (Cartopy), generates side-by-side comparison plots with Earth features, computes and visualizes residuals proving numerical correctness.""",
        
        # AI Use
        'ss_MDT_AI_GEN_0': """AI (GitHub Copilot) was used extensively throughout this assignment for:

1. Code structure and OOP design: Suggestions for class architecture, method organization, and dataclass usage.

2. Mathematical implementations: Assistance with rotation matrix calculations, orbital element formulas, and numerical edge case handling.

3. Vectorization: Help with efficient NumPy array operations for batch processing of orbital data.

4. Visualization: Matplotlib code for multi-axis plots, logarithmic scales, and NaN handling in logarithmic plots.

5. Automation: Structure and implementation of generate_answer_sheet.py for programmatic YAML generation and source code extraction.

6. Documentation: Docstring templates, README structure, and inline code comments (helping with spelling).

All AI-generated code was reviewed, tested, and validated against assignment requirements.""",
        
        # Workload
        'sf_REG_WORKLOAD_GEN_0': 9,
        
        # Feedback
        'ss_REG_FEEDBACK_GEN_0': """ Easy to follow assignment with the slides from the lecture. The programming parts were challenging but manageable with the help of AI tools."""
    }
    
    print(f"✓ Built answer sheet with {len(answer_sheet)} fields")
    return answer_sheet


def save_answer_sheet(answer_sheet: Dict[str, Any], output_file: str = 'answer-sheet.yaml') -> None:
    """Save the answer sheet to YAML file."""
    print(f"\n{'='*70}")
    print(f"STEP 4: SAVING ANSWER SHEET")
    print(f"{'='*70}")
    
    # Add header comment
    yaml_content = f"""# Assignment A2 Answer Sheet
# Generated programmatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    
    # Convert to YAML
    yaml_str = yaml.dump(
        answer_sheet,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=88
    )
    
    # Write to file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content + yaml_str)
    
    print(f"✓ Saved answer sheet to: {output_path}")
    print(f"✓ File size: {output_path.stat().st_size} bytes")


def validate_answer_sheet(answer_sheet_file: str = 'answer-sheet.yaml') -> bool:
    """Validate the answer sheet has all required fields."""
    print(f"\n{'='*70}")
    print(f"STEP 5: VALIDATING ANSWER SHEET")
    print(f"{'='*70}")
    
    # Expected answer keys from README
    required_keys = {
        'ss_REG_Language_GEN_0',
        'ls_MDT_TLE_GEN_0',
        'sf_MDT_OrbTimeIni_NUM_0',
        'sf_MDT_OrbTimeEnd_NUM_0',
        'sf_MDT_OrbTimeStep_NUM_0',
        'sf_REG_OrbTimeIniMJD_NUM_0.25',
        'li_REG_OrbTimeIniYMDHMS_NUM_0.25',
        'lf_REG_OrbPosIni_NUM_0',
        'lf_REG_OrbVelIni_NUM_0',
        'sf_REG_OrbTimeEndMJD_NUM_0.25',
        'li_REG_OrbTimeEndYMDHMS_NUM_0.25',
        'lf_REG_OrbPosEnd_NUM_1',
        'lf_REG_OrbVelEnd_NUM_1',
        'ls_MDT_OrbKep_SRC_0',
        'ss_REG_OrbKep_CODE_1.5',
        'lf_REG_OrbKepSMA_NUM_0.8',
        'lf_REG_OrbKepEcc_NUM_0.8',
        'lf_REG_OrbKepInc_NUM_0.8',
        'lf_REG_OrbKepRAAN_NUM_0.8',
        'lf_REG_OrbKepTApAoP_NUM_1.8',
        'ls_MDT_OrbKepPlot_SRC_0',
        'ss_REG_OrbKepPlot_CODE_2.5',
        'ls_REG_OrbKepPlotFile_PLOT_8',
        'ss_REG_OrbKepObs_OIC_5',
        'ss_REG_OrbKepInt_OIC_7.5',
        'ss_REG_OrbKepCon_OIC_11.5',
        'ls_MDT_OrbKepBack_SRC_0',
        'ss_REG_OrbKepBack_CODE_1.5',
        'ls_MDT_OrbKepBackPlot_SRC_0',
        'ss_REG_OrbKepBackPlot_CODE_2.5',
        'ls_REG_OrbKepBack_PLOT_8',
        'ss_REG_OrbKepBackObs_OIC_5',
        'ss_REG_OrbKepBackInt_OIC_7.5',
        'ss_REG_OrbKepBackCon_OIC_11.5',
        # Excellence fields (co-rotating spherical coordinates)
        'ls_AEX_OrbECF_SRC_0.1',
        'ss_AEX_OrbECF_CODE_1.9',
        'lf_AEX_OrbECFLat_NUM_1',
        'lf_AEX_OrbECFLon_NUM_1',
        'lf_AEX_OrbECFRad_NUM_1',
        'ls_AEX_OrbECFPlot_SRC_0.1',
        'ss_AEX_OrbECFPlot_CODE_0.9',
        'ls_AEX_OrbECF_PLOT_3',
        'ss_AEX_OrbECFObs_OIC_2',
        'ss_AEX_OrbECFInt_OIC_4',
        'ss_AEX_OrbECFCon_OIC_5',
        # General fields
        'ss_CEX_Explain_GEN_10',
        'ss_MDT_AI_GEN_0',
        'sf_REG_WORKLOAD_GEN_0',
        'ss_REG_FEEDBACK_GEN_0'
    }
    
    # Load answer sheet
    with open(answer_sheet_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Check for missing keys
    present_keys = set(data.keys())
    missing_keys = required_keys - present_keys
    extra_keys = present_keys - required_keys
    
    print(f"Present keys: {len(present_keys)}")
    print(f"Required keys: {len(required_keys)}")
    
    if missing_keys:
        print(f"\n✗ Missing keys ({len(missing_keys)}):")
        for key in sorted(missing_keys):
            print(f"  - {key}")
        return False
    
    if extra_keys:
        print(f"\n⚠ Extra keys ({len(extra_keys)}):")
        for key in sorted(extra_keys):
            print(f"  - {key}")
    
    print(f"\n✓ All {len(required_keys)} required keys present!")
    return True


def main():
    """Main function to generate answer sheet programmatically."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Programmatically generate answer-sheet.yaml',
        epilog="""
This script automates the entire answer sheet generation:
1. Runs all required scripts (fetch_tle, main, keplerian, back_cartesian)
2. Loads all generated data files
3. Extracts source code programmatically
4. Fills the answer sheet with proper formatting
5. Validates the output

Examples:
  %(prog)s                     # Generate answer-sheet.yaml
  %(prog)s --output my-answers.yaml
  %(prog)s --skip-run          # Skip running scripts, use existing data
  %(prog)s --skip-validation   # Skip validation step
        """
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='answer-sheet.yaml',
        help='Output filename (default: answer-sheet.yaml)'
    )
    
    parser.add_argument(
        '--skip-run',
        action='store_true',
        help='Skip running scripts, use existing data'
    )
    
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip validation step'
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Run all scripts
        if not args.skip_run:
            run_all_scripts()
        else:
            print("\n⚠ Skipping script execution, using existing data")
        
        # Step 2: Load all data
        data = load_all_data()
        
        # Step 3: Build answer sheet
        answer_sheet = build_answer_sheet(data)
        
        # Step 4: Save to file
        save_answer_sheet(answer_sheet, args.output)
        
        # Step 5: Validate
        if not args.skip_validation:
            valid = validate_answer_sheet(args.output)
            if not valid:
                print("\n⚠ Warning: Validation failed!")
                return 1
        
        # Success
        print(f"\n{'='*70}")
        print("SUCCESS - ANSWER SHEET GENERATED")
        print(f"{'='*70}")
        print(f"\nYour answer sheet is ready: {args.output}")
        print("\nNext steps:")
        print("  1. Review the generated file")
        print("  2. Run: python answer-sheet-sanity.py")
        print("  3. Generate plots: python plot_keplerian.py && python plot_residual.py")
        print("  4. Submit your work")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
