#!/usr/bin/env python3
"""Programmatically generate and fill answer-sheet.yaml from scratch.

This script:
1. Runs orbit propagation (main.py)
2. Extracts all results from the output
3. Fills the answer sheet programmatically
4. Validates the result
"""

import os
import sys
import yaml
import numpy as np
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
# import inspect
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


def run_propagation() -> Dict[str, Any]:
    """Run the orbit propagation and return results.
    
    Returns:
        Dictionary containing all propagation results
    """
    print("=" * 70)
    print("STEP 1: RUNNING ORBIT PROPAGATION")
    print("=" * 70)
    
    # Import and run main.py programmatically
    sys.path.insert(0, str(Path(__file__).parent))
    import main
    
    # Run propagation
    result = main.main()
    
    # Load the saved data
    data_file = Path('data/orbit_propagation.npz')
    if not data_file.exists():
        raise FileNotFoundError("Orbit data not found. Propagation may have failed.")
    
    data = np.load(data_file)
    
    return {
        'times_jd': data['times_jd'],
        'positions': data['positions'],
        'velocities': data['velocities'],
        'errors': data['errors'],
        'satellite_name': str(data['satellite_name']),
        'tle_line1': str(data['tle_line1']),
        'tle_line2': str(data['tle_line2'])
    }


def extract_tle_info(tle_line1: str, tle_line2: str) -> Dict[str, Any]:
    """Extract information from TLE lines.
    
    Args:
        tle_line1: First line of TLE
        tle_line2: Second line of TLE
        
    Returns:
        Dictionary with TLE information
    """
    from sgp4.api import Satrec
    
    sat = Satrec.twoline2rv(tle_line1, tle_line2)
    
    return {
        'norad_id': sat.satnum,
        'line1': tle_line1,
        'line2': tle_line2
    }


def build_answer_sheet(results: Dict[str, Any]) -> Dict[str, Any]:
    """Build the complete answer sheet programmatically.
    
    Args:
        results: Dictionary containing propagation results
        
    Returns:
        Complete answer sheet dictionary
    """
    print("\n" + "=" * 70)
    print("STEP 2: BUILDING ANSWER SHEET")
    print("=" * 70)
    
    # Import functions to extract source code
    import main
    from plot_orbit import plot_groundtrack
    
    # Extract source code for SGP4 and plotting functions
    sgp4_src_files, sgp4_source = get_source_and_file(main.sgp4_propagate)
    plot_src_files, plot_source = get_source_and_file(plot_groundtrack)
    
    # Extract TLE info
    tle_info = extract_tle_info(results['tle_line1'], results['tle_line2'])
    
    # Get positions and velocities (convert km to m)
    positions_m = results['positions'] * 1000  # km to m
    velocities_m = results['velocities'] * 1000  # km/s to m/s
    
    # Calculate time domain parameters from actual data
    times_jd = results['times_jd']
    n_points = len(positions_m)
    
    # Calculate time step from the data
    # times_jd has shape (N, 2) where each row is [jd_whole, jd_frac]
    time_0 = times_jd[0, 0] + times_jd[0, 1]  # First time point (days)
    time_1 = times_jd[1, 0] + times_jd[1, 1]  # Second time point (days)
    time_step_days = time_1 - time_0
    time_step_s = time_step_days * 86400.0  # Convert days to seconds
    
    # Calculate total duration
    time_last = times_jd[-1, 0] + times_jd[-1, 1]
    duration_days = time_last - time_0
    duration_s = duration_days * 86400.0
    
    print(f"  Time step: {time_step_s:.1f} seconds ({time_step_s/60:.2f} minutes)")
    print(f"  Duration: {duration_s:.1f} seconds ({duration_s/3600:.2f} hours)")
    print(f"  Number of points: {n_points}")
    
    # Build answer sheet
    answer_sheet = {
        # Programming Language
        'ss_REG_Language_GEN_0': 'Python 3.12',
        
        # NORAD ID
        'si_REG_NORADID_GEN_0': int(tle_info['norad_id']),
        
        # Satellite Description
        'ss_REG_SatDesc_OIC_5': f"""{results['satellite_name']} is a missile detection satellite launched in 
        2000-05-08 in a geosyncronous orbit avobe the Pacific Ocean. Its orbit is verly likely designed for 
        continuous surveillance of possible tactical missile attacks from Asia towards the US. It is equipped 
        with infrarred sensors for that mission.""",

        # is a Defense Support Program satellite in a geosynchronous orbit. 
        # The DSP satellites are designed for early warning of missile launches using infrared 
        # sensors. The geosynchronous orbit (altitude ~35,786 km, inclination ~13°) provides 
        # continuous coverage of specific regions of Earth, which is ideal for persistent 
        # surveillance and early warning missions. The low eccentricity (~0.00015) maintains 
        # a nearly circular orbit for stable positioning.
        
        # TLE Data
        'ls_MDT_TLE_GEN_0': [
            results['satellite_name'],
            tle_info['line1'],
            tle_info['line2']
        ],
        
        # SGP4 Implementation URL
        'ss_REG_SGP4IMPL_GEN_0': 'https://github.com/brandon-rhodes/python-sgp4',
        
        # SGP4 Source Code Files
        'ls_MDT_SGP4_SRC_0': sgp4_src_files,
        
        # SGP4 Code Implementation
        'ss_REG_SGP4_CODE_4': f"""{sgp4_src_files[0]}:

```python
{sgp4_source}
```
""",
        
        # Time Domain Parameters
        'sf_MDT_OrbTimeIni_NUM_0': 0.0,
        'sf_MDT_OrbTimeEnd_NUM_0': float(duration_s),
        'sf_MDT_OrbTimeStep_NUM_0': float(time_step_s),
        
        # Initial Position (meters)
        'lf_REG_OrbPosIni_NUM_0': [
            float(positions_m[0, 0]),
            float(positions_m[0, 1]),
            float(positions_m[0, 2])
        ],
        
        # Initial Velocity (m/s)
        'lf_REG_OrbVelIni_NUM_0': [
            float(velocities_m[0, 0]),
            float(velocities_m[0, 1]),
            float(velocities_m[0, 2])
        ],
        
        # Final Position (meters)
        'lf_REG_OrbPosEnd_NUM_1': [
            float(positions_m[-1, 0]),
            float(positions_m[-1, 1]),
            float(positions_m[-1, 2])
        ],
        
        # Final Velocity (m/s)
        'lf_REG_OrbVelEnd_NUM_1': [
            float(velocities_m[-1, 0]),
            float(velocities_m[-1, 1]),
            float(velocities_m[-1, 2])
        ],
        
        # Plot Source Code Files
        'ls_MDT_OrbPlot_SRC_0': plot_src_files,
        
        # Plot Code Implementation  
        'ss_REG_OrbPlot_CODE_7': f"""{plot_src_files[0]}:

```python
{plot_source}
```
""",
        
        # Plot Filenames
        'ls_REG_Orb_PLOT_22': [
            'plots/orbit_pos_vel_vs_time.png',
            'plots/orbit_3d.png',
            'plots/orbit_radius_speed.png',
            'plots/orbit_orbital_elements.png',
            'plots/orbit_groundtrack.png'
        ],
        
        # Observations
        'ss_REG_OrbObs_OIC_14': """1. (orbit_pos_vel_vs_time.png) Position and velocity of the satellite show sinusodial
        variations with a day period between them. Z-axis variations are much smaller than X and Y-axis ones.
        
        2. (orbit_radius_speed.png) Radius and speed remain nearly constant. 

        3. (orbit_groundtrack.png) Ground track representation shows a repeating ground track orbit over the Pacific Ocean.""",
        
        # Interpretations
        'ss_REG_OrbInt_OIC_19': """1. Low inclination values are typical for geosynchronous satellites, helping pointing from ground.
        
        2. Low changes in radius and speed indicate a very low eccentricity orbit.""",
        
        # Conclusion
        'ss_REG_OrbCon_OIC_27': f"""Geopolitical considerations influence the design of surveillance 
        satellite orbits, which exploit orbital mechanics to serve military interests.""",
        
        # Code Excellence
        'ss_CEX_Explain_GEN_10': """Advanced coding features implemented:

1. Modular design: Separate modules for TLE fetching (fetch_tle.py), propagation 
   (main.py), and visualization (plot_orbit.py) following separation of concerns.

2. Vectorized NumPy operations: Arrays used throughout for fast computation of 
   orbital parameters (radii, speeds, angular momentum, eccentricity).

3. Data persistence: Results saved in compressed .npz format with metadata.

4. Comprehensive visualization: Four plot types with professional formatting, 
   including 3D orbit with Earth sphere and computed orbital elements.

5. Error handling: SGP4 error codes tracked; file existence checks with informative 
   error messages.

6. Documentation: Docstrings for all functions with parameter and return types; 
   README files with usage examples.

7. Preallocated arrays: Using np.zeros() instead of append operations for efficiency.

8. Reusable functions: fetch_tle() returns structured data for use in other scripts.""",
        
        # AI Use
        'ss_MDT_AI_GEN_0': """AI (GitHub Copilot) was used to assist with:

1. Code structure and organization: suggestions for modular design and function signatures, 
code excellence features' implementation and implementation of new libraries with low 
familiarity by the student (e.g., cartopy).

2. NumPy vectorization: assistance with efficient array operations for orbital element 
   calculations.

3. Matplotlib formatting.

4. Documentation: template for docstrings and README structure.

5. Generating the answer sheet programatically (generate_answer_sheet.py)""",
        
        # Workload
        'sf_REG_WORKLOAD_GEN_0': 8,
        
        # Feedback
        'ss_REG_FEEDBACK_GEN_0': """Assignment 1 good introduction to gitlab and SGP4.

        Suggestions:
        - Organize a tutorial session or similar to go through most of the steps in person together."""
    }
    
    print(f"✓ Built answer sheet with {len(answer_sheet)} fields")
    return answer_sheet


def save_answer_sheet(answer_sheet: Dict[str, Any], output_file: str = 'answer-sheet.yaml') -> None:
    """Save the answer sheet to YAML file.
    
    Args:
        answer_sheet: Answer sheet dictionary
        output_file: Output filename
    """
    print(f"\n{'='*70}")
    print(f"STEP 3: SAVING ANSWER SHEET")
    print(f"{'='*70}")
    
    # Add header comment
    yaml_content = f"""# Assignment A1 Answer Sheet
# Generated programmatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Student Number: 6541356
# NORAD ID: {answer_sheet['si_REG_NORADID_GEN_0']}

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
    """Validate the answer sheet has all required fields.
    
    Args:
        answer_sheet_file: Path to answer sheet
        
    Returns:
        True if valid, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"STEP 4: VALIDATING ANSWER SHEET")
    print(f"{'='*70}")
    
    # Expected answer keys (from assignment)
    required_keys = {
        'ss_REG_Language_GEN_0',
        'si_REG_NORADID_GEN_0',
        'ss_REG_SatDesc_OIC_5',
        'ls_MDT_TLE_GEN_0',
        'ss_REG_SGP4IMPL_GEN_0',
        'ls_MDT_SGP4_SRC_0',
        'ss_REG_SGP4_CODE_4',
        'sf_MDT_OrbTimeIni_NUM_0',
        'sf_MDT_OrbTimeEnd_NUM_0',
        'sf_MDT_OrbTimeStep_NUM_0',
        'lf_REG_OrbPosIni_NUM_0',
        'lf_REG_OrbVelIni_NUM_0',
        'lf_REG_OrbPosEnd_NUM_1',
        'lf_REG_OrbVelEnd_NUM_1',
        'ls_MDT_OrbPlot_SRC_0',
        'ss_REG_OrbPlot_CODE_7',
        'ls_REG_Orb_PLOT_22',
        'ss_REG_OrbObs_OIC_14',
        'ss_REG_OrbInt_OIC_19',
        'ss_REG_OrbCon_OIC_27',
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
        description='Programmatically generate answer-sheet.yaml from orbit propagation',
        epilog="""
This script automates the entire answer sheet generation:
1. Runs orbit propagation (main.py)
2. Extracts all numerical results
3. Fills the answer sheet with proper formatting
4. Validates the output

Examples:
  %(prog)s                     # Generate answer-sheet.yaml
  %(prog)s --output my-answers.yaml
  %(prog)s --skip-validation
        """
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='answer-sheet.yaml',
        help='Output filename (default: answer-sheet.yaml)'
    )
    
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip validation step'
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Run propagation
        results = run_propagation()
        
        # Step 2: Build answer sheet
        answer_sheet = build_answer_sheet(results)
        
        # Step 3: Save to file
        save_answer_sheet(answer_sheet, args.output)
        
        # Step 4: Validate
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
        print("  3. Generate plots: python plot_orbit.py")
        print("  4. Submit your work")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
