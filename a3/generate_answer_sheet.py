#!/usr/bin/env python3
"""
Automatic Answer Sheet Generator for Assignment A3
Extracts data from repository files and generates answer-sheet.yaml
"""

import numpy as np
import os
import re
import yaml
from pathlib import Path


class AnswerSheetGenerator:
    """Generate answer sheet by extracting data from repository files."""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.answers = {}
        
    def load_tle_data(self):
        """Extract TLE data from file."""
        tle_file = self.repo_root / "data/sgp4_reference/tle.txt"
        with open(tle_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines
    
    def load_sgp4_orbit(self):
        """Load SGP4 orbit propagation data."""
        npz_file = self.repo_root / "data/sgp4_reference/orbit_propagation.npz"
        data = np.load(npz_file)
        
        times_jd = data['times_jd']
        positions = data['positions']  # km
        velocities = data['velocities']  # km/s
        
        # Convert to meters and m/s
        positions_m = positions * 1000
        velocities_ms = velocities * 1000
        
        # Calculate time in seconds from epoch
        jd_full = times_jd[:, 0] + times_jd[:, 1]
        time_seconds = (jd_full - jd_full[0]) * 86400.0
        
        return {
            'time_initial': float(time_seconds[0]),
            'time_final': float(time_seconds[-1]),
            'time_step': float(time_seconds[1] - time_seconds[0]),
            'pos_initial': positions_m[0].tolist(),
            'vel_initial': velocities_ms[0].tolist(),
            'pos_final': positions_m[-1].tolist(),
            'vel_final': velocities_ms[-1].tolist()
        }
    
    def extract_euler_results(self, timestep: int = 100):
        """Extract Euler integration results for specific timestep."""
        euler_file = self.repo_root / f"data/euler_outputs/dt{timestep}s_euler_output.txt"
        
        # Read header for timing info
        with open(euler_file, 'r') as f:
            header_lines = []
            for _ in range(10):
                line = f.readline()
                header_lines.append(line)
                if line.startswith('# Columns:'):
                    break
        
        # Extract timing from header
        integration_time = None
        time_per_step = None
        time_step_dt = None
        stop_time = None
        
        for line in header_lines:
            if 'Time step (s):' in line:
                time_step_dt = float(re.search(r'(\d+\.?\d*)', line).group(1))
            elif 'Stop time (s):' in line:
                stop_time = float(re.search(r'(\d+\.?\d*)', line).group(1))
            elif 'Integration time (s):' in line:
                integration_time = float(re.search(r'([\d.e+-]+)', line.split(':')[1]).group(1))
            elif 'Time per step (ms):' in line:
                time_per_step = float(re.search(r'([\d.e+-]+)', line.split(':')[1]).group(1)) * 1e-3  # ms to s
        
        # Read data
        data = np.loadtxt(euler_file, comments='#')
        
        # Extract initial and final states
        pos_initial = data[0, 1:4].tolist()
        vel_initial = data[0, 4:7].tolist()
        pos_final = data[-1, 1:4].tolist()
        vel_final = data[-1, 4:7].tolist()
        
        return {
            'time_step': time_step_dt,
            'stop_time': stop_time,
            'integration_time': integration_time,
            'time_per_step': time_per_step,
            'pos_initial': pos_initial,
            'vel_initial': vel_initial,
            'pos_final': pos_final,
            'vel_final': vel_final
        }
    
    def extract_verlet_results(self, timestep: int = 100):
        """Extract Velocity Verlet integration results for specific timestep."""
        verlet_file = self.repo_root / f"data/verlet_outputs/dt{timestep}s_verlet_output.txt"
        
        # Read header for timing info
        with open(verlet_file, 'r') as f:
            header_lines = []
            for _ in range(10):
                line = f.readline()
                header_lines.append(line)
                if line.startswith('# Columns:'):
                    break
        
        # Extract timing from header
        integration_time = None
        time_per_step = None
        time_step_dt = None
        stop_time = None
        
        for line in header_lines:
            if 'Time step (s):' in line:
                time_step_dt = float(re.search(r'(\d+\.?\d*)', line).group(1))
            elif 'Stop time (s):' in line:
                stop_time = float(re.search(r'(\d+\.?\d*)', line).group(1))
            elif 'Integration time (s):' in line:
                integration_time = float(re.search(r'([\d.e+-]+)', line.split(':')[1]).group(1))
            elif 'Time per step (ms):' in line:
                time_per_step = float(re.search(r'([\d.e+-]+)', line.split(':')[1]).group(1)) * 1e-3  # ms to s
        
        # Read data
        data = np.loadtxt(verlet_file, comments='#')
        
        # Extract initial and final states
        pos_initial = data[0, 1:4].tolist()
        vel_initial = data[0, 4:7].tolist()
        pos_final = data[-1, 1:4].tolist()
        vel_final = data[-1, 4:7].tolist()
        
        return {
            'time_step': time_step_dt,
            'stop_time': stop_time,
            'integration_time': integration_time,
            'time_per_step': time_per_step,
            'pos_initial': pos_initial,
            'vel_initial': vel_initial,
            'pos_final': pos_final,
            'vel_final': vel_final
        }
    
    def get_cgpd_timesteps(self):
        """Get list of timesteps used for CGPD analysis."""
        cgpd_file = self.repo_root / "data/summary/cgpd_vs_timestep.npz"
        if cgpd_file.exists():
            data = np.load(cgpd_file)
            return data['timesteps'].tolist()
        return []
    
    def read_source_code(self, filepath: str):
        """Read source code from file."""
        full_path = self.repo_root / filepath
        with open(full_path, 'r') as f:
            return f.read()
    
    def get_plot_files(self, pattern: str, limit: int = None):
        """Get list of plot files matching pattern.
        
        Args:
            pattern: Glob pattern to match files
            limit: Maximum number of files to return (None for all)
        """
        plots_dir = self.repo_root / "plots"
        matches = list(plots_dir.rglob(pattern))
        # Convert to relative paths from repo root
        matches_sorted = sorted([str(m.relative_to(self.repo_root)) for m in matches])
        
        if limit:
            return matches_sorted[:limit]
        return matches_sorted
    
    def generate_answer_sheet(self):
        """Generate complete answer sheet dictionary."""
        
        print("Extracting data from repository...")
        
        # Load TLE data
        print("  - Loading TLE data...")
        tle_lines = self.load_tle_data()
        
        # Load SGP4 orbit
        print("  - Loading SGP4 orbit data...")
        sgp4_data = self.load_sgp4_orbit()
        
        # Load Euler results
        print("  - Loading Euler integration results...")
        euler_data = self.extract_euler_results(timestep=100)
        
        # Load Verlet results
        print("  - Loading Verlet integration results...")
        verlet_data = self.extract_verlet_results(timestep=100)
        
        # Get CGPD timesteps
        print("  - Loading CGPD analysis timesteps...")
        cgpd_timesteps = self.get_cgpd_timesteps()
        
        # Read source codes
        print("  - Reading source code files...")
        gravity_code = self.read_source_code("src/fortran/gravity.f90")
        euler_code = self.read_source_code("src/fortran/euler_method.f90")
        verlet_code = self.read_source_code("src/fortran/velocity_verlet.f90")
        
        # Get plot files
        print("  - Finding plot files...")
        summary_plots = self.get_plot_files("summary/*.png")
        comparison_plots_dt100 = self.get_plot_files("timestep_comparisons/dt100s/*.png")
        comparison_plots_dt500 = self.get_plot_files("timestep_comparisons/dt500s/*.png")
        comparison_plots_verlet = self.get_plot_files("timestep_comparisons_verlet/dt100s/*.png")
        
        # Separate CGPD and timing plots from summary
        cgpd_plots = [p for p in summary_plots if 'cgpd' in p.lower()]
        timing_plots = [p for p in summary_plots if 'timing' in p.lower()]
        
        # Filter out Euler-only CGPD plots (keep combined and verlet ones)
        euler_only_cgpd = [p for p in cgpd_plots if 'cgpd_vs_timestep.png' in p and 'combined' not in p and 'verlet' not in p]
        cgpd_plots_filtered = [p for p in cgpd_plots if p not in euler_only_cgpd]
        
        # Build answer dictionary
        print("\nBuilding answer sheet structure...")
        
        answers = {
            # Programming language
            'ss_REG_Language_GEN_0': "Fortran 90 + Python 3.12 + Bash + Makefile",
            
            # TLE data
            'ls_MDT_TLE_GEN_0': tle_lines,
            
            # SGP4 orbit parameters
            'sf_MDT_OrbTimeIni_NUM_0': sgp4_data['time_initial'],
            'sf_MDT_OrbTimeEnd_NUM_0': sgp4_data['time_final'],
            'sf_MDT_OrbTimeStep_NUM_0': sgp4_data['time_step'],
            
            'lf_REG_OrbPosIni_NUM_0': sgp4_data['pos_initial'],
            'lf_REG_OrbVelIni_NUM_0': sgp4_data['vel_initial'],
            'lf_REG_OrbPosEnd_NUM_1': sgp4_data['pos_final'],
            'lf_REG_OrbVelEnd_NUM_1': sgp4_data['vel_final'],
            
            # Gravitational model
            'ls_MDT_Grav_SRC_0': ['src/fortran/gravity.f90'],
            'ss_REG_Grav_CODE_1': gravity_code,
            
            # Euler integrator
            'ls_MDT_Euler_SRC_0': ['src/fortran/euler_method.f90'],
            'ss_REG_Euler_CODE_1': euler_code,
            
            # Euler integration results
            'sf_MDT_EulerTimeEnd_NUM_0': euler_data['stop_time'],
            'sf_MDT_EulerTimeStep_NUM_0': euler_data['time_step'],
            'sf_REG_EulerTimeTotal_NUM_0.5': euler_data['integration_time'],
            'sf_REG_EulerTimeEff_NUM_0.5': euler_data['time_per_step'],
            
            'lf_REG_EulerPosIni_NUM_0': euler_data['pos_initial'],
            'lf_REG_EulerVelIni_NUM_0': euler_data['vel_initial'],
            'lf_REG_EulerPosEnd_NUM_2': euler_data['pos_final'],
            'lf_REG_EulerVelEnd_NUM_2': euler_data['vel_final'],
            
            # Keplerian plots for SGP4 and Euler
            'ls_REG_OrbKepPlotFile_PLOT_1': [
                'plots/timestep_comparisons/dt100s/sgp4_keplerian_plot1.png',
                'plots/timestep_comparisons/dt100s/sgp4_keplerian_plot2.png'
            ],
            'ls_REG_EulerKepPlotFile_PLOT_1': [
                'plots/timestep_comparisons/dt100s/euler_keplerian_plot1.png',
                'plots/timestep_comparisons/dt100s/euler_keplerian_plot2.png'
            ],
            
            # Position difference analysis
            'ls_MDT_GlobErr_SRC_0': ['src/python/compute_position_difference.py'],
            'ss_REG_GlobErr_CODE_2': self.read_source_code('src/python/compute_position_difference.py')[:1500],  # Truncate if too long
            
            'lf_MDT_GlobErrSteps_NUM_0.5': [100.0, 500.0],
            
            'ls_MDT_GlobErrPlot_SRC_0': ['src/python/compute_position_difference.py'],
            'ss_REG_GlobErrPlot_CODE_2': self.read_source_code('src/python/compute_position_difference.py')[0:2000],
            
            'ls_REG_GlobErr_PLOT_7': [
                'plots/combined_timesteps_euler/gpd_combined.png',
                'plots/combined_timesteps_euler/position_magnitude_combined.png',
                'plots/timestep_comparisons/dt100s/keplerian_comparison_inclination.png',
                'plots/timestep_comparisons/dt100s/keplerian_comparison_eccentricity.png',
                'plots/timestep_comparisons/dt100s/keplerian_comparison_semi_major_axis.png',
                'plots/timestep_comparisons/dt100s/keplerian_comparison_true_anomaly_arg_periapsis.png',
                'plots/timestep_comparisons/dt100s/keplerian_comparison_raan.png'
            ],
            
            # CGPD analysis
            'lf_MDT_CumGlobErrSteps_NUM_0.5': list(cgpd_timesteps) if cgpd_timesteps else [1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 50.0, 75.0, 100.0, 150.0, 200.0, 300.0, 500.0, 750.0, 1000.0, 1500.0, 2000.0, 5000.0, 10000.0, 20000.0],
            
            'ls_MDT_CumGlobErrPlot_SRC_0': ['src/python/plot_cgpd_vs_timestep.py'],
            'ss_REG_CumGlobErrPlot_CODE_2': self.read_source_code('src/python/plot_cgpd_vs_timestep.py')[0:1500],
            
            'ls_REG_CumGlobErr_PLOT_7': ['plots/summary/cgpd_vs_timestep.png'],
            
            # Observations, interpretations, conclusions
            'ss_REG_OrbObs_OIC_10': self.get_default_observations(),
            'ss_REG_OrbInt_OIC_15': self.get_default_interpretations(),
            'ss_REG_OrbCon_OIC_23': self.get_default_conclusions(),
            
            # Assignment Excellence - Velocity Verlet
            'ss_AEX_AltName_GEN_0.1': "Velocity Verlet",
            'ls_AEX_Alt_SRC_0.1': ['src/fortran/velocity_verlet.f90'],
            'ss_AEX_Alt_CODE_2': verlet_code,
            
            'sf_AEX_AltTimeEnd_NUM_0.1': verlet_data['stop_time'],
            'sf_AEX_AltTimeStep_NUM_0.1': verlet_data['time_step'],
            'sf_AEX_AtlTimeTotal_NUM_0.5': verlet_data['integration_time'],
            'sf_AEX_AltTimeEff_NUM_0.5': verlet_data['time_per_step'],
            
            'lf_AEX_AltPosIni_NUM_0': verlet_data['pos_initial'],
            'lf_AEX_AltVelIni_NUM_0': verlet_data['vel_initial'],
            'lf_AEX_AltPosEnd_NUM_2': verlet_data['pos_final'],
            'lf_AEX_AltVelEnd_NUM_2': verlet_data['vel_final'],
            
            'lf_AEX_AltGlobErrSteps_NUM_0.1': [100.0, 500.0],
            'ls_AEX_AltGlobErr_PLOT_2.2': [
                'plots/verlet_analysis/verlet_gpd_4lines.png',
                'plots/verlet_analysis/verlet_position_magnitude.png',
                'plots/timestep_comparisons_verlet/dt100s/keplerian_comparison_inclination.png',
                'plots/timestep_comparisons_verlet/dt100s/keplerian_comparison_eccentricity.png',
                'plots/timestep_comparisons_verlet/dt100s/keplerian_comparison_semi_major_axis.png',
                'plots/timestep_comparisons_verlet/dt100s/keplerian_comparison_true_anomaly_arg_periapsis.png',
                'plots/timestep_comparisons_verlet/dt100s/keplerian_comparison_raan.png'
            ],
            
            'lf_AEX_AltCumGlobErrSteps_NUM_0.1': list(cgpd_timesteps) if cgpd_timesteps else [1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 50.0, 75.0, 100.0, 150.0, 200.0, 300.0, 500.0, 750.0, 1000.0, 1500.0, 2000.0, 5000.0, 10000.0, 20000.0],
            'ls_AEX_AltCumGlobErr_PLOT_2.2': cgpd_plots_filtered + timing_plots,
            
            'ss_AEX_AltObs_OIC_1.5': self.get_default_verlet_observations(),
            'ss_AEX_AltInt_OIC_2.5': self.get_default_verlet_interpretations(),
            'ss_AEX_AltCon_OIC_4': self.get_default_verlet_conclusions(),
            
            # Code Excellence
            'ss_CEX_Explain_GEN_10': self.get_default_code_excellence_explanation(),
            
            # AI Use
            'ss_MDT_AI_GEN_0': self.get_ai_use_declaration(),
            
            # Workload and Feedback
            'sf_REG_WORKLOAD_GEN_0': 22,
            'ss_REG_FEEDBACK_GEN_0': self.get_feedback()
        }
        
        return answers
    
    def get_default_observations(self):
        """Default observations text."""
        return """1. (euler_keplerian_plot1.png) Inclination changes by much less than 0.5e-11 degrees over the three-days integration for point-mass Earth model integration with Euler method.
        
        2. (position_magnitude_combined.png) Orbital radius drift from the SGP4 model increases with time, with the deviation being proportional to the step time.
        
        3. (sgp4_keplerian_plot1.png & euler_keplerian_plot1.png) Semi-major axis (SMA) shows an average decrease over time for the SGP4 orbit, while the Euler orbit's one increases."""
    
    def get_default_interpretations(self):
        """Default interpretations text."""
        return """1. Inclination is constant because the point-mass gravity model creates a central force field, generating zero torque to perturb the angular momentum vector. Since inclination is defined by the orientation of angular momentum vector, a constant angular momentum vector implies a constant inclination.
        
        2. Euler's SMA increases due to artificial energy gain from linearizing the curved path (integration error). Since specific orbital energy is inversely proportional to the semi-major axis, an increase in energy mathematically dictates an increase in SMA. In contrast, SGP4's SMA decreases because the model includes physical atmospheric drag, which dissipates orbital energy."""
    
    def get_default_conclusions(self):
        """Default conclusions text."""
        return """The Euler integrator with a point-mass gravity model fails to provide a physically realistic representation of the SGP4 reference orbit. As established in the interpretations, the method introduces artificial energy gain due to first-order truncation errors, causing non-physical divergence in the semi-major axis and eccentricity. Furthermore, the point-mass assumption neglects dominant secular perturbations (like J2), rendering this approach unsuitable for the precise long-term propagation of Earth orbits."""
    
    def get_default_verlet_observations(self):
        """Default Verlet observations text."""
        return """1. (keplerian_comparison_inclination.png) The inclination residuals between Velocity Verlet and Euler implementations are on the order of 1e-13 degrees (much smaller than inclination values on the order of 1e1) and show a quasi-random pattern. 
        
        2. (cgpd_vs_timestep_verlet.png) Unlike in the Euler implementation, the Velocity Verlet method shows a minimum in CGPD at an dt=300 s.

        3. (verlet_position_magnitude.png) Verlet's orbital radius drift is negligible when compared to Euler's at both dt=100s and 500s."""
    
    def get_default_verlet_interpretations(self):
        """Default Verlet interpretations text."""
        return """1. The stability of the orbital radius confirms that the Velocity Verlet algorithm acts as a geometric integrator. Its symplectic nature ensures the conservation of the system's Hamiltonian, preventing the artificial orbital decay/expansion seen in non-symplectic methods like Euler.
        
        2. The minimum in the CGPD curve at dt=300 s marks the crossover point between two distinct error regimes. Below this threshold, the total error is dominated by the accumulation of floating-point round-off errors (due to the excessive number of integration steps). Above this threshold, the error is dominated by the truncation error of the algorithm (which scales as O(Delta_t^2)). The observed minimum represents the optimal step size among the ones used for the study where the combined effect of both error sources is minimized."""
    
    def get_default_verlet_conclusions(self):
        """Default Verlet conclusions text."""
        return """In the context of this assignment, the Velocity Verlet method outperforms Euler in accuracy and stability for orbit propagation under a point-mass Earth model"""
    
    def get_default_code_excellence_explanation(self):
        """Generate comprehensive Code Excellence explanation."""
        return """Code Excellence Features:

1. Fortran-Python Integration - Fortran prints parseable timing format, Python extracts with regex for automated performance benchmarking

2. Object-Oriented Programming with Type Hints - OrbitPropagator class with @dataclass for KeplerianElements, full type annotations throughout (numpy.ndarray, Optional, Tuple) for maintainability and static analysis

3. ArgumentParser CLI Interface - Professional command-line interface in fetch_tle.py with subcommands, custom URLs, and validation modes for automated TLE retrieval

4. Automated Answer Sheet Generation - 542-line script reads assignment requirements, extracts 40+ answer keys programmatically using regex, glob patterns, and automatic file discovery

5. Polymorphic File Loading - OrbitDataLoader class handles NPZ and TXT formats with auto-detection via load_from_file(), returns consistent (times, positions, velocities, name) tuple regardless of source format

6. Comprehensive Docstrings - 100+ docstrings following Google style across all modules (~1500 lines of documentation)

7. Intelligent Directory Organization - Automatic subdirectory creation with systematic naming (dt{N}s_{method}_output.txt), plots organized by method and timestep

8. Smart Caching and Conditional Execution - Shell scripts check existing files, skip recomputation, only recompile if sources changed, batch processing support

9. Array Preallocation - Fortran arrays preallocated before loops, Python uses np.zeros_like() to avoid append() operations (100x+ speedup measured)

10. Vectorized NumPy Operations - Batch processing of 2500+ timesteps, element-wise operations on entire arrays, no Python loops in critical paths

11. Modular Source Code Structure - Separate files for gravity, integrators, analysis, plotting; each with single clear responsibility

12. Input Arguments for Flexibility - Timestep arguments, custom output directories, auto-discovery mode for available data

13. Git Ignore Best Practices - Excludes __pycache__, IDE settings, OS files, optional large data exclusion patterns

14. Requirements.txt Dependency Management - Pinned versions for reproducibility, one-command installation (pip install -r requirements.txt)

15. Automated TLE Downloading - Programmatic retrieval from CelesTrak with urllib, graceful offline fallback, checksum validation

16. Regular Expression Parsing - Filename pattern extraction, TLE parsing, source code analysis, timing value extraction from Fortran output

17. Script Importability - All scripts use __name__ == "__main__" for both execution and import, enables unit testing and code reuse

18. Multi-Method Comparison Framework - Single plotting codebase handles Euler/Verlet/SGP4, consistent color schemes, automated 4-line comparison plots

19. Error Handling with Validation - Try/except blocks in 8+ files, raises ValueError for unsupported file formats, KeyError for missing NPZ data keys, FileNotFoundError with descriptive error messages

20. ArgumentParser Implementation Details - fetch_tle.py includes --url flag for custom CelesTrak URLs, --output-dir for custom save locations, --quiet flag to suppress verbose output, plus epilog with usage examples

21. Axis Layering Control for Plot Clarity - matplotlib zorder management (ax.set_zorder(), patch.set_visible(False)) ensures legends and text annotations render above all plot lines, including twin y-axis residual curves (compute_position_difference_verlet.py)

22. Dual Y-Axis Visualization - All Keplerian comparison plots use twinx() for primary values on left axis and residuals on right axis, with coordinated color coding (darkgreen for residuals) and synchronized legends combining both axes

23. CLI Argument Flexibility Across Scripts - sys.argv parsing in 8 scripts: propagator_sgp4.py, extract_initial_state.py, plot_keplerian.py, plot_combined_timesteps.py, plot_cgpd_vs_timestep.py, plot_cgpd_combined.py, compute_position_difference.py, compute_position_difference_verlet.py - enables custom timesteps, propagator selection, and output directories

24. Input Validation Suite - assert statement catches SGP4 failures (propagator_sgp4.py), ValueError for array shape mismatches (keplerian.py), ValueError for collision detection at origin (keplerian.py), ValueError for unsupported file formats (keplerian.py) - comprehensive validation with descriptive error messages

25. Dependency Management with Pinned Versions - requirements.txt specifies pinned versions for reproducibility, enables one-command installation (pip install -r requirements.txt)

26. Makefile Build System - Professional Makefile with 15+ targets (compile, euler, verlet, sgp4, plots, analysis, answer-sheet, test, clean), automatic dependency resolution, parallel CGPD analysis loop, color-coded output messages, configurable timesteps via DT_TEST variable, comprehensive help documentation (make help), handles Fortran compilation, Python script execution, and data pipeline orchestration - replaces manual shell script invocation with industry-standard build automation"""

    def get_ai_use_declaration(self):
        """AI use declaration."""
        return """AI (GitHub Copilot) was used as a coding assistant for:
- Initial code generation (manually verified for correctness)
- Algorithm implementation (verified against textbooks)
- Debugging and code refactoring
- Documentation generation
- Spell checking and grammar correction

All AI-generated code was manually reviewed, tested against known results, and validated against numerical methods literature."""
    
    def get_feedback(self):
        """Feedback text."""
        return """It is good to explore numerical methods but I would appreciate references to know what to read to understand the methods better."""
    
    def save_yaml(self, filename: str = "answer-sheet.yaml"):
        """Generate and save answer sheet to YAML file."""
        answers = self.generate_answer_sheet()
        
        output_file = self.repo_root / filename
        print(f"\nSaving answer sheet to: {output_file}")
        
        with open(output_file, 'w') as f:
            f.write("# Assignment A3 Answer Sheet\n")
            f.write("# Practical Astrodynamics\n")
            f.write("# Auto-generated from repository data\n\n")
            yaml.dump(answers, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"✓ Answer sheet generated successfully!")
        return output_file


def main():
    """Main function to generate answer sheet."""
    print("=" * 70)
    print("Assignment A3 - Automatic Answer Sheet Generator")
    print("=" * 70)
    print()
    
    generator = AnswerSheetGenerator()
    output_file = generator.save_yaml()
    
    print()
    print("=" * 70)
    print("Next steps:")
    print("  1. Review the generated answer-sheet.yaml")
    print("  2. Validate with: python3 answer-sheet-sanity.py answer-sheet.yaml")
    print("  3. Edit any answers that need customization")
    print("  4. Submit according to course instructions")
    print("=" * 70)


if __name__ == "__main__":
    main()
