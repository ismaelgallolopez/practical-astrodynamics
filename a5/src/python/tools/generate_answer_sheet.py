#!/usr/bin/env python3
"""
Generate answer-sheet.yaml for Assignment A5 from computed data.
"""

import numpy as np
import yaml
import os
import sys
from pathlib import Path

# Base paths
base_dir = Path(__file__).parent.parent.parent.parent
data_dir = base_dir / 'data'
src_dir = base_dir / 'src'

def read_tle():
    """Read TLE data from file."""
    tle_file = data_dir / 'sgp4_reference' / 'tle.txt'
    with open(tle_file, 'r') as f:
        lines = f.readlines()
    # Return both TLE lines + the name line
    return [lines[0].strip(), lines[1].strip(), lines[2].strip()]

def read_sgp4_orbit():
    """Read SGP4 orbit data."""
    orbit_file = data_dir / 'sgp4_reference' / 'orbit_propagation.npz'
    data = np.load(orbit_file)
    return data

def read_integrated_orbit():
    """Read integrated orbit data."""
    orbit_file = data_dir / 'outputs_all' / 'integrated_orbit.txt'
    data = np.loadtxt(orbit_file)
    return data

def read_optimized_orbit():
    """Read optimized orbit data."""
    orbit_file = data_dir / 'outputs_all' / 'optimized_orbit.txt'
    data = np.loadtxt(orbit_file)
    return data

def read_optimization_results():
    """Read optimization convergence data."""
    conv_file = data_dir / 'outputs_all' / 'convergence_history.txt'
    data = np.loadtxt(conv_file)
    
    # Extract results from convergence data
    # Columns: iteration, cgpd, time
    iterations = data[:, 0]
    cgpds = data[:, 1]
    times = data[:, 2]
    
    results = {
        'initial_cgpd': cgpds[0],
        'final_cgpd': cgpds[-1],
        'best_cgpd': np.min(cgpds),
        'best_iteration': int(iterations[np.argmin(cgpds)]),
        'iterations': len(iterations),
        'total_time': np.sum(times)
    }
    
    return results

def read_third_body_positions():
    """Read Sun and Moon positions."""
    tb_file = data_dir / 'sgp4_reference' / 'third_body_positions.txt'
    
    with open(tb_file, 'r') as f:
        lines = f.readlines()
    
    # Parse the file - find lines that don't start with #
    data_lines = [line for line in lines if not line.strip().startswith('#') and line.strip()]
    
    # First data line is Sun, second is Moon
    sun_data = data_lines[0].strip().split()
    moon_data = data_lines[1].strip().split()
    
    sun_pos = np.array([float(sun_data[0]), float(sun_data[1]), float(sun_data[2])])
    moon_pos = np.array([float(moon_data[0]), float(moon_data[1]), float(moon_data[2])])
    
    return sun_pos, moon_pos

def read_source_file(filepath):
    """Read source code file content."""
    with open(filepath, 'r') as f:
        return f.read()

def format_vector(vec, decimals=6):
    """Format vector for YAML output."""
    return [float(f"{v:.{decimals}f}") for v in vec]

def generate_answer_sheet():
    """Generate the complete answer sheet."""
    
    # Initialize answer dictionary
    answers = {}
    
    print("Reading data files...")
    # Read data
    tle_lines = read_tle()
    sgp4_data = read_sgp4_orbit()
    integrated_data = read_integrated_orbit()
    optimized_data = read_optimized_orbit()
    opt_results = read_optimization_results()
    sun_pos, moon_pos = read_third_body_positions()
    
    # Extract SGP4 orbit parameters
    times = sgp4_data['times_jd']
    positions = sgp4_data['positions']  # shape: (n, 3)
    velocities = sgp4_data['velocities']  # shape: (n, 3)
    
    # Time parameters
    t_start = times[0, 0] + times[0, 1]  # JD integer + fraction
    t_end = times[-1, 0] + times[-1, 1]
    dt = (times[1, 0] + times[1, 1]) - (times[0, 0] + times[0, 1])
    
    # Convert to seconds from epoch
    t_start_sec = 0.0  # Start is at epoch
    t_end_sec = (t_end - t_start) * 86400.0  # Convert days to seconds
    dt_sec = dt * 86400.0
    
    print("\nGenerating answer keys...")
    
    # Following the order from README.md
    
    # ====================
    # PLOTTING - Listed first in README
    # ====================
    # Keplerian plot source code
    answers['ls_MDT_OrbKepResPlot_SRC_0'] = ["src/python/plotting/plot_keplerian_comparison.py"]
    kep_plot_code = read_source_file(src_dir / 'python' / 'plotting' / 'plot_keplerian_comparison.py')
    answers['ss_REG_OrbKepResPlot_CODE_1'] = kep_plot_code
    
    # Additional plots
    answers['ls_MDT_AltPlot_SRC_0'] = [
        "src/python/plotting/plot_magnitude_comparison.py",
        "src/python/plotting/plot_optimization_convergence.py"
    ]
    alt_plot_code = read_source_file(src_dir / 'python' / 'plotting' / 'plot_magnitude_comparison.py')
    answers['ss_REG_AltPlot_CODE_0'] = alt_plot_code
    
    # ====================
    # PROGRAMMING LANGUAGE
    # ====================
    answers['ss_REG_Language_GEN_0'] = "Fortran and Python"
    
    # ====================
    # TLE DATA
    # ====================
    answers['ls_MDT_TLE_GEN_0'] = tle_lines
    
    # ====================
    # SGP4 ORBIT - Update your orbit
    # ====================
    answers['sf_MDT_OrbTimeIni_NUM_0'] = float(f"{t_start_sec:.6f}")
    answers['sf_MDT_OrbTimeEnd_NUM_0'] = float(f"{t_end_sec:.6f}")
    answers['sf_MDT_OrbTimeStep_NUM_0'] = float(f"{dt_sec:.6f}")
    
    answers['lf_REG_OrbPosIni_NUM_0'] = format_vector(positions[0] * 1000, 6)  # km to m
    answers['lf_REG_OrbVelIni_NUM_0'] = format_vector(velocities[0] * 1000, 6)  # km/s to m/s
    answers['lf_REG_OrbPosEnd_NUM_1'] = format_vector(positions[-1] * 1000, 6)
    answers['lf_REG_OrbVelEnd_NUM_1'] = format_vector(velocities[-1] * 1000, 6)
    
    # ====================
    # PERFORM ORBIT INTEGRATION
    # ====================
    answers['ss_MDT_Integrator_GEN_0'] = "Velocity Verlet"
    answers['ls_MDT_ForceModelComponents_GEN_0'] = ["J2", "SRP", "SUN", "MOON"]
    
    # Sun and Moon positions (already in meters from JPL)
    answers['lf_REG_SunPos_GEN_0'] = format_vector(sun_pos, 6)
    answers['lf_REG_MoonPos_GEN_0'] = format_vector(moon_pos, 6)
    
    # Integrated orbit timing
    answers['sf_REG_EulerTimeTotal_NUM_0.5'] = 0.033  # Approximate from timestep study
    answers['sf_REG_EulerTimeEff_NUM_0.5'] = 0.033 / len(integrated_data)  # Per step
    
    # Integrated orbit state vectors
    answers['lf_REG_IntPosIni_NUM_0'] = format_vector(integrated_data[0, 1:4], 6)
    answers['lf_REG_IntVelIni_NUM_0'] = format_vector(integrated_data[0, 4:7], 6)
    answers['lf_REG_IntPosEnd_NUM_1'] = format_vector(integrated_data[-1, 1:4], 6)
    answers['lf_REG_IntVelEnd_NUM_1'] = format_vector(integrated_data[-1, 4:7], 6)
    
    # ====================
    # PLOT KEPLERIAN ELEMENTS
    # ====================
    answers['ls_REG_OrbKep_PLOT_1'] = [
        "plots/sgp4/keplerian_elements_sgp4_plot1.png",
        "plots/sgp4/keplerian_elements_sgp4_plot2.png"
    ]
    answers['ls_REG_EulerKep_PLOT_1'] = [
        "plots/integrated/keplerian_elements_custom_plot1.png",
        "plots/integrated/keplerian_elements_custom_plot2.png"
    ]
    
    # ====================
    # BUILD OBJECTIVE FUNCTION
    # ====================
    answers['ls_MDT_ObjFun_SRC_0'] = ["src/fortran/modules/objective_function.f90"]
    obj_fun_code = read_source_file(src_dir / 'fortran' / 'modules' / 'objective_function.f90')
    answers['ss_REG_ObjFun_CODE_1'] = obj_fun_code
    
    # CGPD of integrated orbit (nominal, without optimization)
    answers['sf_REG_CGPDInt_NUM_1'] = float(f"{opt_results['initial_cgpd']:.6f}")
    
    # ====================
    # OPTIMISE INITIAL STATE VECTOR
    # ====================
    answers['ss_MDT_OptName_GEN_0'] = "Gradient"
    answers['ls_MDT_Opt_SRC_0'] = ["src/fortran/optimization/gradient_descent.f90"]
    opt_code = read_source_file(src_dir / 'fortran' / 'optimization' / 'gradient_descent.f90')
    answers['ss_REG_Opt_CODE_6'] = opt_code
    
    # Optimization timing and results
    answers['sf_REG_OptTotal_NUM_0.5'] = float(f"{opt_results['total_time']:.6f}")
    answers['sf_REG_OptEff_NUM_0.5'] = float(f"{opt_results['total_time'] / opt_results['iterations']:.6f}")
    
    # Optimized orbit state vectors
    answers['lf_REG_OptPosIni_NUM_0'] = format_vector(optimized_data[0, 1:4], 6)
    answers['lf_REG_OptVelIni_NUM_0'] = format_vector(optimized_data[0, 4:7], 6)
    answers['lf_REG_OptPosEnd_NUM_0'] = format_vector(optimized_data[-1, 1:4], 6)
    answers['lf_REG_OptVelEnd_NUM_0'] = format_vector(optimized_data[-1, 4:7], 6)
    
    # Final CGPD
    answers['sf_REG_CGPDOpt_NUM_1'] = float(f"{opt_results['final_cgpd']:.6f}")
    
    # ====================
    # PLOT CONVERGENCE
    # ====================
    answers['ls_REG_Conv_PLOT_2'] = ["plots/optimization/convergence.png"]
    
    # ====================
    # REPORT THE DIFFERENCES
    # ====================
    answers['ls_REG_OrbKepRes_PLOT_7'] = [
        "plots/keplerian/i_comparison.png",
        "plots/keplerian/e_comparison.png",
        "plots/keplerian/a_comparison.png",
        "plots/keplerian/u_comparison.png",
        "plots/keplerian/raan_comparison.png"
    ]
    
    # Additional magnitude plots
    answers['ls_REG_MagDiff_PLOT_5'] = [
        "plots/magnitudes/position_magnitude.png",
        "plots/magnitudes/velocity_magnitude.png"
    ]
    
    # ====================
    # OBSERVATIONS, INTERPRETATIONS, CONCLUSIONS
    # ====================
    answers['ss_REG_OrbObs_OIC_10'] = """
1. (plots/optimization/convergence.png) The CGPD decreases more rapidly per iteration (on average) in the initial ~30 iterations than in the rest of the optimization. 

2. (plots/magnitudes/position_magnitude.png) The absolute value of the position magnitude error is always lower for the optimized orbit compared to the integrated orbit for the period studied.

3. (plots/magnitudes/position_magnitude.png & plots/magnitudes/velocity_magnitude.png) Position initial difference is equal to 0 for both integrated and optimized orbits but velocity initial difference is only zero for the integrated orbit.
"""
    
    answers['ss_REG_OrbInt_OIC_15'] = """
    
1. A lower position difference magnitude through the entire time span implies a lower CGPD value, as per CGPD definition.

2. The stalling in CGPD reduction suggests the optimizer may have reached a local minimum. 
"""
    
    answers['ss_REG_OrbCon_OIC_23'] = """
The optimized orbit will always have a greater or equal difference (in position and/or velocity) than the integrated orbit at the initial time, since the change of the initial state vector is the only way to reduce the CGPD in this assignment.    
"""
    
    # ====================
    # ASSIGNMENT EXCELLENCE - TIMESTEP STUDY
    # ====================
    answers['ls_AEX_OptTotalStep_PLOT_2'] = ["plots/timestep_study/performance_vs_timestep.png"]
    answers['ls_AEX_CGPDStep_PLOT_2'] = ["plots/timestep_study/cgpd_vs_timestep.png"]
    answers['ls_AEX_OptTotalCGPD_PLOT_2'] = ["plots/timestep_study/cputime_vs_cgpd.png"]
    
    answers['ss_AEX_OptStep_OIC_3'] = """
1. (plots/timestep_study/performance_vs_timestep.png) The optimization with time step #3 & #4 reached the maximum iterations before converging into a solution.

2. (plots/timestep_study/cputime_vs_cgpd.png) For the values studied, a reduction of time step leads to a higher CPU time.

3. (plots/timestep_study/performance_vs_timestep.png) The CPU time and the number of iterations both show a similar trend (increasing and decreasing in the same points).
"""
    
    answers['ss_AEX_OptStep_OIC_5'] = """
1. The number of iterations is a driving factor in the CPU time.

2. Current hyperparameters (learning rate, tolerance, max. iterations, etc.) of the optimizer cannot guarantee an optimum for all time steps studied.
"""
    
    answers['ss_AEX_OptStep_OIC_6'] = """
Implementing a robust optimizer requires hyperparameter tuning to guarantee convergence to a local optimum. 
"""
    
    # ====================
    # CODE EXCELLENCE
    # ====================
    answers['ss_CEX_Explain_GEN_10'] = """Advanced features implemented using Fortran and Python:
1. Modular Fortran architecture: 7 separate modules (gravity, j2_perturbation, srp_perturbation, third_body_perturbation, drag_perturbation, velocity_verlet, objective_function) for independent development and reusability
2. Dual-path file access: Fallback logic (../../ vs ../../../) enabling execution from build/ or root directories
3. Numerical gradient computation: Central finite differences (epsilon=1e-5) for derivative-based optimization without analytical jacobians
4. Best-solution tracking: Returns minimum CGPD from iteration history, preventing momentum overshoot artifacts
5. Systematic sensitivity studies: 16 force model combinations, 20 hyperparameter pairs, 10 perturbed initial states, 10 integration timesteps
6. Multi-axis plotting: Dual/triple y-axes (twinx()) for overlaying residuals, differences, and multi-variable trends
7. Efficient Velocity Verlet: Pre-allocated arrays, dt^2 pre-computation, achieving 0.5s runtime target
8. Automated compilation: Individual shell scripts per program plus centralized Makefile for correct dependency order
9. Early stopping: Patience-based convergence (100 iterations) prevents wasted computation at optimization plateau
10. Answer sheet auto-generation: Python script extracts values from data files, eliminating manual transcription errors
11. Configurable perturbations: Boolean toggles (ENABLE_J2, ENABLE_DRAG, ENABLE_SRP, ENABLE_THIRD_BODY) allow runtime force model selection
12. SGP4 reference integration: NPZ file loading with Julian date conversion for high-precision orbit comparison
13. Angle wrapping: Proper modulo arithmetic for angular elements (RAAN, inclination, argument of latitude) in residual plots
14. Shadow modeling: Eclipse detection for SRP using dot product between Sun-satellite and Sun-Earth vectors
15. Comprehensive data output: Time-stamped state vectors, acceleration components, Keplerian elements, convergence metrics
16. Cross-platform compatibility: Works on Linux/macOS with gfortran, numpy, matplotlib dependencies only
17. Using Fortran (I bet nobody else did)."""
    
    # ====================
    # AI USE AND WORKLOAD
    # ====================
    answers['ss_MDT_AI_GEN_0'] = """GitHub Copilot was used extensively throughout this assignment as an AI pair-programming assistant. Specific usage included:
1. Code generation: Initial Fortran module templates, Python plotting scripts
2. Debugging: Identifying format string errors, module compilation order issues, Julian date conversion bugs
3. Optimization: Suggesting algorithm improvements (best-solution tracking, hyperparameter tuning)
4. Documentation: Generating code comments and README sections
All AI-generated code was thoroughly reviewed, tested, and modified to ensure correctness and meet assignment requirements. The optimization algorithm design, force model selection, and analysis were done independently."""
    
    answers['sf_REG_WORKLOAD_GEN_0'] = 11.0  
    
    # ====================
    # FEEDBACK
    # ====================
    answers['ss_REG_FEEDBACK_GEN_0'] = """I do not see the point in implementing a optimizer when all (of most) of us do it with AI just to pass the assignment and really take no learning from it. It is impossible to get a good perspective (in my opinion) on numerical optimization with just a lecture on that plus an assignment and never touching it again. Some of us already did optimization courses and have some experience but otherwise it is just an artifact of this assignment."""
    
    # ====================
    # WRITE YAML FILE
    # ====================
    output_file = base_dir / 'answer-sheet.yaml'
    
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w') as f:
        yaml.dump(answers, f, default_flow_style=False, sort_keys=False, width=120)
    
    print(f"\n{'='*60}")
    print(f"✓ Answer sheet generated: {output_file}")
    print(f"✓ Total answer keys filled: {len(answers)}")
    print(f"{'='*60}")
    print("\nIMPORTANT: Review and adjust before submission:")
    print("  - Observations, interpretations, and conclusions (OIC fields)")
    print("  - Code excellence explanation (ss_CEX_Explain_GEN_10)")
    print("  - AI use statement (ss_MDT_AI_GEN_0)")
    print("  - Workload hours (sf_REG_WORKLOAD_GEN_0)")
    print("  - Feedback (ss_REG_FEEDBACK_GEN_0)")
    print("\nValidate with: python answer-sheet-sanity.py")
    
    return answers

if __name__ == '__main__':
    try:
        generate_answer_sheet()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
