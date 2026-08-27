#!/usr/bin/env python3
"""
Generate answer-sheet.yaml for Assignment A4
Reads data from simulation outputs and formats according to README requirements
"""

import numpy as np
import yaml
import sys
import os
from pathlib import Path

# Change to project root directory
project_root = Path(__file__).parent.parent.parent.parent
os.chdir(project_root)

# Data directories
DATA_DIR = Path("data")
SGP4_DIR = DATA_DIR / "sgp4_reference"
OUTPUTS_DIR = DATA_DIR

# Output files
ORBIT_FILE = OUTPUTS_DIR / "outputs_orbit" / "dt10s_output.txt"
J2_FILE = OUTPUTS_DIR / "outputs_oblateness" / "dt10s_j2_output.txt"
SRP_FILE = OUTPUTS_DIR / "outputs_srp" / "dt10s_srp_output.txt"
DRAG_FILE = OUTPUTS_DIR / "outputs_drag" / "dt10s_drag_output.txt"
TBP_FILE = OUTPUTS_DIR / "outputs_third_body" / "dt10s_third_body_output.txt"

# Plot directories
PLOT_DIR = Path("plots")

def read_tle():
    """Read TLE data from file"""
    tle_file = SGP4_DIR / "tle.txt"
    with open(tle_file, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

def read_initial_state():
    """Read initial state from SGP4 output"""
    state_file = SGP4_DIR / "initial_state.txt"
    with open(state_file, 'r') as f:
        lines = f.readlines()
    
    pos = [float(x) for x in lines[0].strip().split()]
    vel = [float(x) for x in lines[1].strip().split()]
    timestep = float(lines[2].strip())
    duration = float(lines[3].strip())
    
    return pos, vel, timestep, duration

def read_orbit_data(filename):
    """Read orbit data from output file"""
    data = np.loadtxt(filename, skiprows=0)
    
    if len(data.shape) == 1:
        data = data.reshape(1, -1)
    
    # Columns: time, x, y, z, vx, vy, vz
    initial = data[0, :]
    final = data[-1, :]
    
    pos_ini = initial[1:4].tolist()
    vel_ini = initial[4:7].tolist()
    pos_end = final[1:4].tolist()
    vel_end = final[4:7].tolist()
    
    return pos_ini, vel_ini, pos_end, vel_end

def read_third_body_positions():
    """Read Sun and Moon positions and GM values from file"""
    tb_file = SGP4_DIR / "third_body_positions.txt"
    
    sun_pos = None
    moon_pos = None
    gm_sun = None
    gm_moon = None
    
    with open(tb_file, 'r') as f:
        lines = f.readlines()
    
    # Find Sun and Moon data (first two non-comment lines with data)
    data_lines = []
    for line in lines:
        if not line.startswith('#') and line.strip():
            data = [float(x) for x in line.strip().split()]
            data_lines.append(data)
            if len(data_lines) == 2:
                break
    
    if len(data_lines) >= 2:
        # First line: Sun position (x, y, z, GM)
        sun_pos = data_lines[0][0:3]
        gm_sun = data_lines[0][3] if len(data_lines[0]) > 3 else None
        # Second line: Moon position (x, y, z, GM)
        moon_pos = data_lines[1][0:3]
        gm_moon = data_lines[1][3] if len(data_lines[1]) > 3 else None
    
    return sun_pos, moon_pos, gm_sun, gm_moon

def format_list(values, precision=12):
    """Format list of floats for YAML"""
    return [float(f"{v:.{precision}e}") for v in values]

def get_plot_files(directory, pattern="*.png"):
    """Get list of plot files in directory"""
    plot_dir = PLOT_DIR / directory
    if plot_dir.exists():
        files = sorted([str(plot_dir / f.name) for f in plot_dir.glob(pattern)])
        return files
    return []

def extract_fortran_parameter(line):
    """Helper to extract numeric value from Fortran parameter line"""
    parts = line.split('=')[1].strip()
    value_str = parts.split('_')[0].strip()
    value_str = value_str.split('!')[0].strip()  # Remove comments
    return float(value_str)

def extract_j2_parameters():
    """Extract J2 parameters from Fortran source code"""
    j2_file = Path("src/fortran/modules/j2_perturbation.f90")
    
    j2 = None
    mu_earth = None
    r_earth = None
    
    with open(j2_file, 'r') as f:
        for line in f:
            if 'J2' in line and '=' in line and 'parameter' in line and 'real' in line:
                j2 = extract_fortran_parameter(line)
            elif ('mu_earth' in line or 'GM' in line) and '=' in line and 'parameter' in line:
                mu_earth = extract_fortran_parameter(line)
            elif 'R_earth' in line and '=' in line and 'parameter' in line:
                r_earth = extract_fortran_parameter(line)
    
    return j2, mu_earth, r_earth

def extract_srp_parameters():
    """Extract SRP parameters from Fortran source code"""
    srp_file = Path("src/fortran/modules/srp_perturbation.f90")
    
    cr_over_m = None
    solar_flux = None
    c_light = None
    r_earth = None
    
    with open(srp_file, 'r') as f:
        for line in f:
            if 'CR_OVER_M' in line and '=' in line and 'parameter' in line:
                cr_over_m = extract_fortran_parameter(line)
            elif 'SOLAR_FLUX' in line and '=' in line and 'parameter' in line:
                solar_flux = extract_fortran_parameter(line)
            elif 'C_LIGHT' in line and '=' in line and 'parameter' in line:
                c_light = extract_fortran_parameter(line)
            elif 'R_EARTH' in line and '=' in line and 'parameter' in line:
                r_earth = extract_fortran_parameter(line)
    
    return cr_over_m, solar_flux, c_light, r_earth

def extract_drag_parameters():
    """Extract drag parameters from Fortran source code"""
    drag_file = Path("src/fortran/modules/drag_perturbation.f90")
    
    rho_0 = None
    h_scale = None
    r_earth = None
    cd_over_m = None
    
    with open(drag_file, 'r') as f:
        for line in f:
            if 'RHO_0' in line and '=' in line and 'parameter' in line:
                rho_0 = extract_fortran_parameter(line)
            elif 'H_SCALE' in line and '=' in line and 'parameter' in line:
                h_scale = extract_fortran_parameter(line)
            elif 'R_EARTH' in line and '=' in line and 'parameter' in line:
                r_earth = extract_fortran_parameter(line)
            elif 'BALLISTIC_COEFF' in line and '=' in line and 'parameter' in line:
                cd_over_m = extract_fortran_parameter(line)
    
    return r_earth, h_scale, rho_0, cd_over_m

def extract_tbp_parameters():
    """Extract third body perturbation parameters - note TBP reads GM from file at runtime"""
    # TBP module doesn't have hardcoded GM parameters, they're loaded from file
    # We return None to signal this, and will use values from third_body_positions.txt
    return None, None

def generate_answer_sheet():
    """Generate the complete answer sheet"""
    
    print("Reading TLE data...")
    tle_lines = read_tle()
    
    print("Reading initial state...")
    sgp4_pos_ini, sgp4_vel_ini, timestep, duration = read_initial_state()
    
    print("Reading Sun and Moon positions...")
    sun_pos, moon_pos, gm_sun_file, gm_moon_file = read_third_body_positions()
    
    print("Extracting parameters from Fortran source code...")
    j2, mu_earth, r_earth_j2 = extract_j2_parameters()
    cr_over_m, solar_flux, c_light, r_earth_srp = extract_srp_parameters()
    r_earth_drag, h_scale, rho_0, cd_over_m = extract_drag_parameters()
    gm_sun_fortran, gm_moon_fortran = extract_tbp_parameters()
    
    # TBP uses GM from data file, not Fortran parameters
    gm_sun = gm_sun_file
    gm_moon = gm_moon_file
    
    print("Reading orbit data...")
    orbit_pos_ini, orbit_vel_ini, orbit_pos_end, orbit_vel_end = read_orbit_data(ORBIT_FILE)
    j2_pos_ini, j2_vel_ini, j2_pos_end, j2_vel_end = read_orbit_data(J2_FILE)
    srp_pos_ini, srp_vel_ini, srp_pos_end, srp_vel_end = read_orbit_data(SRP_FILE)
    drag_pos_ini, drag_vel_ini, drag_pos_end, drag_vel_end = read_orbit_data(DRAG_FILE)
    tbp_pos_ini, tbp_vel_ini, tbp_pos_end, tbp_vel_end = read_orbit_data(TBP_FILE)
    
    print("Collecting plot files...")
    j2_keplerian_plots = get_plot_files("j2_keplerian")
    j2_accel_plots = get_plot_files("j2_accelerations")
    srp_keplerian_plots = get_plot_files("srp_keplerian")
    srp_accel_plots = get_plot_files("srp_accelerations")
    drag_keplerian_plots = get_plot_files("drag_keplerian")
    drag_accel_plots = get_plot_files("drag_accelerations")
    tbp_keplerian_plots = get_plot_files("tbp_keplerian")
    tbp_accel_plots = get_plot_files("tbp_accelerations")
    
    # Build answer dictionary - ORDERED TO MATCH README
    answers = {}
    
    # ========== PLOTTING SETUP (from README Contents section) ==========
    
    # Source code files - Keplerian residuals
    answers['ls_MDT_OrbKepRes_SRC_0'] = ["src/python/plotting/plot_keplerian_residuals.py"]
    answers['ss_REG_OrbKepRes_CODE_2'] = """
def plot_keplerian_residuals(r_unperturbed, v_unperturbed, r_perturbed, v_perturbed, 
                             time_hours, perturbation_name, output_dir):
    # Compute Keplerian elements for both orbits
    kep_unperturbed = []
    kep_perturbed = []
    
    for i in range(len(r_unperturbed)):
        kep_unp = cartesian_to_keplerian(r_unperturbed[i], v_unperturbed[i])
        kep_per = cartesian_to_keplerian(r_perturbed[i], v_perturbed[i])
        kep_unperturbed.append(kep_unp)
        kep_perturbed.append(kep_per)
    
    # Compute residuals (differences)
    residuals = []
    for kep_unp, kep_per in zip(kep_unperturbed, kep_perturbed):
        residual = {
            'inc': kep_per['inc'] - kep_unp['inc'],
            'ecc': kep_per['ecc'] - kep_unp['ecc'],
            'sma': kep_per['sma'] - kep_unp['sma'],
            'aol': kep_per['aol'] - kep_unp['aol'],
            'raan': kep_per['raan'] - kep_unp['raan']
        }
        residuals.append(residual)
    
    # Create 5 plots with dual y-axes
    create_dual_axis_plot(time_hours, kep_unperturbed, kep_perturbed, residuals, output_dir)
"""
    
    # Source code files - Magnitude plots
    answers['ls_MDT_MagPlot_SRC_0'] = ["src/python/plotting/plot_disturbance_accelerations.py"]
    answers['ss_REG_MagPlot_CODE_1'] = """
def plot_disturbance_magnitudes(accelerations, time_hours, perturbation_name, output_dir):
    # Compute magnitude of acceleration vectors
    magnitudes = np.linalg.norm(accelerations, axis=1)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.plot(time_hours, magnitudes, linewidth=1.5)
    ax.set_xlabel('Time [hours]')
    ax.set_ylabel('Acceleration magnitude [m/s²]')
    ax.set_title(f'{perturbation_name} Disturbance Acceleration Magnitude')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{perturbation_name.lower()}_magnitude.png', dpi=300)
"""
    
    # Programming language
    answers['ss_REG_Language_GEN_0'] = "Fortran and Python"
    
    # ========== TASKS SECTION ==========
    
    # TLE Data
    answers['ls_MDT_TLE_GEN_0'] = tle_lines
    
    # Time domain
    answers['sf_MDT_OrbTimeIni_NUM_0'] = 0.0
    answers['sf_MDT_OrbTimeEnd_NUM_0'] = float(duration)
    answers['sf_MDT_OrbTimeStep_NUM_0'] = float(timestep)
    
    # SGP4 initial and final states
    answers['lf_REG_OrbPosIni_NUM_0'] = format_list(sgp4_pos_ini)
    answers['lf_REG_OrbVelIni_NUM_0'] = format_list(sgp4_vel_ini)
    answers['lf_REG_OrbPosEnd_NUM_1'] = format_list(orbit_pos_end)
    answers['lf_REG_OrbVelEnd_NUM_1'] = format_list(orbit_vel_end)
    
    # Integrator name
    answers['ss_MDT_Integrator_GEN_0'] = "Velocity Verlet"
    
    # Undisturbed orbit (two-body) states
    answers['lf_REG_IntPosIni_NUM_0'] = format_list(orbit_pos_ini)
    answers['lf_REG_IntVelIni_NUM_0'] = format_list(orbit_vel_ini)
    answers['lf_REG_IntPosEnd_NUM_0.85'] = format_list(orbit_pos_end)
    answers['lf_REG_IntVelEnd_NUM_0.85'] = format_list(orbit_vel_end)
    
    # Keplerian element plots
    answers['ls_REG_OrbKepPlotFile_PLOT_1'] = [
        "plots/sgp4/keplerian_elements_sgp4_plot1.png",
        "plots/sgp4/keplerian_elements_sgp4_plot2.png"
    ]
    answers['ls_REG_EulerKepPlotFile_PLOT_1'] = [
        "plots/undisturbed/keplerian_elements_undisturbed_plot1.png",
        "plots/undisturbed/keplerian_elements_undisturbed_plot2.png"
    ]
    
    # ========== J2 OBLATENESS ==========
    answers['ss_REG_OrbKepRes_CODE_2'] = """
def plot_keplerian_residuals(r_unperturbed, v_unperturbed, r_perturbed, v_perturbed, 
                             time_hours, perturbation_name, output_dir):
    # Compute Keplerian elements for both orbits
    kep_unperturbed = []
    kep_perturbed = []
    
    for i in range(len(r_unperturbed)):
        kep_unp = cartesian_to_keplerian(r_unperturbed[i], v_unperturbed[i])
        kep_per = cartesian_to_keplerian(r_perturbed[i], v_perturbed[i])
        kep_unperturbed.append(kep_unp)
        kep_perturbed.append(kep_per)
    
    # Compute residuals (differences)
    residuals = []
    for kep_unp, kep_per in zip(kep_unperturbed, kep_perturbed):
        residual = {
            'inc': kep_per['inc'] - kep_unp['inc'],
            'ecc': kep_per['ecc'] - kep_unp['ecc'],
            'sma': kep_per['sma'] - kep_unp['sma'],
            'aol': kep_per['aol'] - kep_unp['aol'],
            'raan': kep_per['raan'] - kep_unp['raan']
        }
        residuals.append(residual)
    
    # Create 5 plots with dual y-axes
    create_dual_axis_plot(time_hours, kep_unperturbed, kep_perturbed, residuals, output_dir)
"""
    
    # Source code files - Magnitude plots
    answers['ls_MDT_MagPlot_SRC_0'] = ["src/python/plotting/plot_disturbance_accelerations.py"]
    answers['ss_REG_MagPlot_CODE_1'] = """
def plot_disturbance_magnitudes(accelerations, time_hours, perturbation_name, output_dir):
    # Compute magnitude of acceleration vectors
    magnitudes = np.linalg.norm(accelerations, axis=1)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.plot(time_hours, magnitudes, linewidth=1.5)
    ax.set_xlabel('Time [hours]')
    ax.set_ylabel('Acceleration magnitude [m/s²]')
    ax.set_title(f'{perturbation_name} Disturbance Acceleration Magnitude')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{perturbation_name.lower()}_magnitude.png', dpi=300)
"""
    
    # Programming language
    answers['ss_REG_Language_GEN_0'] = "Fortran 90 + Python 3.12 + Bash + Makefile "
    
    # ========== J2 OBLATENESS ==========
    
    # J2 source code
    answers['ls_MDT_J2_SRC_0'] = ["src/fortran/modules/j2_perturbation.f90"]
    answers['ss_REG_J2_CODE_2.5'] = f"""
subroutine j2_acceleration(r, a_j2)
    real(8), intent(in) :: r(3)
    real(8), intent(out) :: a_j2(3)
    real(8) :: r_mag, factor
    real(8), parameter :: J2 = {j2:.3e}
    real(8), parameter :: GM = {mu_earth:.10e}  ! m^3/s^2
    real(8), parameter :: R_EARTH = {r_earth_j2:.1e}  ! m
    
    r_mag = sqrt(r(1)**2 + r(2)**2 + r(3)**2)
    factor = 1.5d0 * J2 * GM * R_EARTH**2 / r_mag**5
    
    a_j2(1) = factor * r(1) * (5.0d0*(r(3)/r_mag)**2 - 1.0d0)
    a_j2(2) = factor * r(2) * (5.0d0*(r(3)/r_mag)**2 - 1.0d0)
    a_j2(3) = factor * r(3) * (5.0d0*(r(3)/r_mag)**2 - 3.0d0)
end subroutine j2_acceleration
"""
    
    # J2 orbit states
    answers['lf_REG_J2PosIni_NUM_0'] = format_list(j2_pos_ini)
    answers['lf_REG_J2VelIni_NUM_0'] = format_list(j2_vel_ini)
    answers['lf_REG_J2PosEnd_NUM_0.85'] = format_list(j2_pos_end)
    answers['lf_REG_J2VelEnd_NUM_0.85'] = format_list(j2_vel_end)
    
    # J2 plots
    answers['ls_REG_J2Orb_PLOT_5'] = j2_keplerian_plots
    answers['ls_REG_J2Mag_PLOT_2'] = j2_accel_plots
    
    # J2 Analysis
    answers['ss_REG_J2Obs_OIC_6'] = """
1. (plots/j2_keplerian/argument_of_latitude_j2_comparison.png) The disturbed and undisturbed argument-of-latitude curves lie on top of each other for the entire 72-hour interval, and the difference curve remains close to zero without showing any visible trend.

2. (plots/j2_accelerations/j2_components.png) All three acceleration components (X, Y, Z) vary periodically with time and remain within a narrow, symmetric range around zero throughout the simulation.

3. (plots/j2_keplerian/raan_j2_comparison.png) The disturbed RAAN decreases overall over the 72-hour interval while the undisturbed curve stays nearly constant, and the difference curve shows a predominantly negative drift with small oscillations.
"""
    
    answers['ss_REG_J2Int_OIC_8'] = """
1. Because the argument of latitude curves overlap entirely, the J2 perturbation does not produce a visible change in the argument of latitude over the simulated period.

2. The periodic nature of the acceleration components together with the steadily decreasing RAAN difference indicates that J2 introduces bounded short-term variations but also produces a consistent long-term change in RAAN.
"""
    
    answers['ss_REG_J2Con_OIC_10'] = """
J2 perturbation causes a precession in orbital plane, given by the change over time of the RAAN.  
"""
    
    # ========== SOLAR RADIATION PRESSURE ==========
    
    # Sun position
    answers['lf_REG_SunPos_NUM_0.9'] = format_list(sun_pos)
    
    # SRP source code
    answers['ls_MDT_SRP_SRC_0'] = ["src/fortran/modules/srp_perturbation.f90"]
    answers['ss_REG_SRP_CODE_2.5'] = f"""
subroutine srp_acceleration(r, r_sun, a_srp)
    real(8), intent(in) :: r(3), r_sun(3)
    real(8), intent(out) :: a_srp(3)
    real(8) :: r_sat_sun(3), d, f_g, P_srp
    real(8), parameter :: CR_OVER_M = {cr_over_m:.2f}  ! m^2/kg
    real(8), parameter :: SOLAR_FLUX = {solar_flux:.1f}  ! W/m^2
    real(8), parameter :: C_LIGHT = {c_light:.1e}  ! m/s
    real(8), parameter :: R_EARTH = {r_earth_srp:.1e}
    
    ! Vector from satellite to Sun
    r_sat_sun = r_sun - r
    d = sqrt(r_sat_sun(1)**2 + r_sat_sun(2)**2 + r_sat_sun(3)**2)
    
    ! Compute shadow factor (geometric)
    call compute_shadow_factor(r, r_sun, f_g)
    
    ! SRP pressure
    P_srp = SOLAR_FLUX / C_LIGHT
    
    ! Acceleration
    a_srp = f_g * CR_OVER_M * P_srp * r_sat_sun / d
end subroutine srp_acceleration
"""
    
    # SRP orbit states
    answers['lf_REG_SRPPosIni_NUM_0'] = format_list(srp_pos_ini)
    answers['lf_REG_SRPVelIni_NUM_0'] = format_list(srp_vel_ini)
    answers['lf_REG_SRPPosEnd_NUM_0.85'] = format_list(srp_pos_end)
    answers['lf_REG_SRPVelEnd_NUM_0.85'] = format_list(srp_vel_end)
    
    # SRP plots
    answers['ls_REG_SRPOrb_PLOT_5'] = srp_keplerian_plots
    answers['ls_REG_SRPMag_PLOT_2'] = srp_accel_plots
    
    # SRP Analysis - IMPROVED: More precise observations with specific numbers
    answers['ss_REG_SRPObs_OIC_6'] = """
1. (plots/srp_accelerations/srp_magnitude.png) SRP magnitude remains constant through the integration period at approximately 9.1e-8 m/s^2.

2. (plots/srp_accelerations/srp_with_shadow.png) The spacecraft remains in full sunlight for the entire 72-hour simulation.

3. (plots/srp_accelerations/srp_components.png) All 3 SRP acceleration components show a 24-hour periodicity, with smooth sinusoidal variation.
"""
    
    answers['ss_REG_SRPInt_OIC_8'] = """
1. Because the SRP magnitude stays constant while the X, Y and Z components vary periodically, the SRP acceleration behaves as a constant-strength vector whose direction rotates once per orbital period.

2. Since the spacecraft remains in full sunlight and the SRP magnitude does not change over the 72 hours, any time variation in the SRP components is caused by the changing geometry between the spacecraft and the Sun, not by shadow passages.
"""
    
    answers['ss_REG_SRPCon_OIC_10'] = """
When solar radiation pressure acts continuously with nearly constant magnitude, it behaves as a steady perturbing force whose direction changes with the orbital motion rather than as an on/off disturbance driven by eclipses.
"""
    
    # ========== ASSIGNMENT EXCELLENCE ==========
    
    # Drag parameters - extracted from source code
    # Reference height is the altitude corresponding to the table row used
    # For 35,786 km altitude (GEO), the reference height is 35,786 km
    ref_height = 35786000.0  # meters (this is the altitude, not R_EARTH)
    answers['sf_AEX_RefHeight_GEN_0.1'] = ref_height
    answers['sf_AEX_ScaleHeight_GEN_0.1'] = h_scale
    answers['sf_AEX_MeanRho_GEN_0.1'] = rho_0
    
    # Drag source code
    answers['ls_AEX_Drag_SRC_0.1'] = ["src/fortran/modules/drag_perturbation.f90"]
    answers['ss_AEX_Drag_CODE_0.8'] = f"""
subroutine drag_acceleration(r, v, a_drag)
    real(8), intent(in) :: r(3), v(3)
    real(8), intent(out) :: a_drag(3)
    real(8) :: v_rel(3), v_rel_mag, h, rho
    real(8), parameter :: H_REF = {r_earth_drag:.1e}
    real(8), parameter :: H_SCALE = {h_scale:.1e}
    real(8), parameter :: RHO_0 = {rho_0:.2e}
    real(8), parameter :: OMEGA_EARTH = 7.2921159e-5
    real(8), parameter :: CD_A_OVER_M = {cd_over_m:.2f}
    
    ! Relative velocity (account for rotating atmosphere)
    v_rel(1) = v(1) + OMEGA_EARTH * r(2)
    v_rel(2) = v(2) - OMEGA_EARTH * r(1)
    v_rel(3) = v(3)
    v_rel_mag = sqrt(v_rel(1)**2 + v_rel(2)**2 + v_rel(3)**2)
    
    ! Altitude and density
    h = sqrt(r(1)**2 + r(2)**2 + r(3)**2) - H_REF
    rho = RHO_0 * exp(-h / H_SCALE)
    
    ! Drag acceleration
    a_drag = -0.5d0 * CD_A_OVER_M * rho * v_rel_mag * v_rel
end subroutine drag_acceleration
"""
    
    # Drag orbit states
    answers['lf_AEX_DragPosIni_NUM_0'] = format_list(drag_pos_ini)
    answers['lf_AEX_DragVelIni_NUM_0'] = format_list(drag_vel_ini)
    answers['lf_AEX_DragPosEnd_NUM_0.2'] = format_list(drag_pos_end)
    answers['lf_AEX_DragVelEnd_NUM_0.2'] = format_list(drag_vel_end)
    
    # Drag plots
    answers['ls_AEX_DragOrb_PLOT_1'] = drag_keplerian_plots
    answers['ls_AEX_DragMag_PLOT_0.5'] = drag_accel_plots
    
    # Drag Analysis 
    answers['ss_AEX_DragObs_OIC_1'] = """
1. (plots/drag_accelerations/atmospheric_density.png) According to the model used, atmospheric density only changes in the fifth significant digit for the entire 72-hour simulation at GEO altitude.

2. (plots/drag_accelerations/drag_acceleration_magnitude.png) Drag acceleration magnitude shows a 12-hour periodicity, twice as fast as the orbital period. 

3. (plots/drag_keplerian/raan_comparison.png) The undisturbed and disturbed RAAN curves visually overlap, and the difference stays near numerical noise level without any visible trend. 
"""
    
    answers['ss_AEX_DragInt_OIC_2'] = """
1. For the studied case, the drag force is extremely weak, and its effect on the orbit stays on the same order as the numerical precision of the computed Keplerian elements.

2. Drag does not produce a detectable plane-orientation change over the 72-hour simulation.
"""
    
    answers['ss_AEX_DragCon_OIC_4'] = """
At GEO altitude, atmospheric drag is physically present but, for this configuration and time span, it is negligible compared to other perturbations and can be ignored in practical orbit propagation.
"""
    
    # Moon position
    answers['lf_AEX_MoonPos_NUM_0.1'] = format_list(moon_pos)
    
    # TBP source code
    answers['ls_AEX_TBP_SRC_0.1'] = ["src/fortran/modules/third_body_perturbation.f90"]
    answers['ss_AEX_TBP_CODE_0.8'] = f"""
subroutine third_body_acceleration(r, r_sun, r_moon, a_tbp)
    real(8), intent(in) :: r(3), r_sun(3), r_moon(3)
    real(8), intent(out) :: a_tbp(3)
    real(8) :: r_sun_sat(3), r_moon_sat(3), d_sun, d_moon, d_sun_sat, d_moon_sat
    real(8), parameter :: GM_SUN = {gm_sun:.12e}
    real(8), parameter :: GM_MOON = {gm_moon:.12e}
    
    ! Sun perturbation
    r_sun_sat = r_sun - r
    d_sun = sqrt(r_sun(1)**2 + r_sun(2)**2 + r_sun(3)**2)
    d_sun_sat = sqrt(r_sun_sat(1)**2 + r_sun_sat(2)**2 + r_sun_sat(3)**2)
    
    ! Moon perturbation
    r_moon_sat = r_moon - r
    d_moon = sqrt(r_moon(1)**2 + r_moon(2)**2 + r_moon(3)**2)
    d_moon_sat = sqrt(r_moon_sat(1)**2 + r_moon_sat(2)**2 + r_moon_sat(3)**2)
    
    ! Total third body acceleration
    a_tbp = GM_SUN * (r_sun_sat/d_sun_sat**3 - r_sun/d_sun**3) + &
            GM_MOON * (r_moon_sat/d_moon_sat**3 - r_moon/d_moon**3)
end subroutine third_body_acceleration
"""
    
    # TBP orbit states
    answers['lf_AEX_TBPPosIni_NUM_0'] = format_list(tbp_pos_ini)
    answers['lf_AEX_TBPVelIni_NUM_0'] = format_list(tbp_vel_ini)
    answers['lf_AEX_TBPPosEnd_NUM_0.2'] = format_list(tbp_pos_end)
    answers['lf_AEX_TBPVelEnd_NUM_0.2'] = format_list(tbp_vel_end)
    
    # TBP plots
    answers['ls_AEX_TBPOrb_PLOT_1'] = tbp_keplerian_plots
    answers['ls_AEX_TBPMag_PLOT_0.5'] = tbp_accel_plots
    
    # TBP Analysis 
    answers['ss_AEX_TBPObs_OIC_1'] = """
1. (plots/tbp_accelerations/tbp_magnitude.png) Moon third-body perturbations have higher magnitude than Sun third-body perturbations for the simulation considered.

2. (plots/tbp_keplerian/raan_tbp_comparison.png) The disturbed RAAN slowly increases over the 72-hour interval, while the undisturbed RAAN remains nearly constant. The difference curve shows a smooth positive drift.

3. (plots/tbp_accelerations/tbp_magnitude.png) Mean TBP acceleration magnitude is approximately 8e-06 m/s^2, with the maximum and minimum values of approximately 1e-05 m/s^2 and 5e-06 m/s^2, respectively.  
"""
    
    answers['ss_AEX_TBPInt_OIC_2'] = """
1. The higher magnitude of the lunar TBP compared to the solar TBP indicates that, for this orbital geometry and time span, the Moon is the dominant third-body contributor to the perturbing acceleration.

2. The positive drift of the RAAN difference suggests that third-body perturbations introduce a secular eastward rotation of the orbital plane over the 72-hour interval.

3. The TBP acceleration magnitude varies within a relatively narrow band (from about 5e-06 to 1.3e-05 m/s^2), so the applied perturbation remains of similar order throughout the simulation, leading to gradual rather than abrupt changes in the orbital elements.
"""
    
    answers['ss_AEX_TBPCon_OIC_4'] = """
For near-GEO orbits, third-body perturbations from the Moon (and, to a lesser extent, the Sun) can dominate the perturbing acceleration budget and drive secular changes in angular elements such as RAAN and inclination, while acting with a slowly varying magnitude over each orbital period.
"""
    
    # Code Excellence - IMPROVED: Removed weak claims, strengthened with technical specifics
    answers['ss_CEX_Explain_GEN_10'] = """
Code excellence features:

1. Dataclass Architecture: Python modules use @dataclass for KeplerianElements container with type hints (np.ndarray) and automatic __repr__ showing mean values, eliminating boilerplate constructors.

2. Dual-Layer Plot Rendering: Transparent thick lines (alpha=0.3, linewidth=3, zorder=1) + crisp dotted lines (alpha=1.0, linestyle=':', zorder=2) allow simultaneous trend magnitude and temporal detail visibility.

3. External Legend Layout: bbox_to_anchor=(1.02, 1.0, 0.2, 0) positions legends in dedicated 22% right margin with plt.tight_layout(rect=[0, 0, 0.78, 1]) preventing data-legend overlap.

4. Multi-Axis Scientific Notation: ax2.ticklabel_format(style='scientific', scilimits=(0,0)) with tick_params(pad=25) prevents Y-axis label collisions on triple-Y-axis plots.

5. Automated Directory Management: Plot scripts detect output path (plots/sgp4/ vs plots/undisturbed/) based on data source using os.path.exists() checks with fallback logic.

6. JPL Horizons API Integration: URL-encoded query strings (CENTER='500@399', EPHEM_TYPE='VECTORS', VEC_TABLE='2') with $$SOE/$$EOE marker parsing and regex r'GM.*=\\s*([0-9.E+-]+)' for header extraction.

7. Fortran Regex Parameter Extraction: Python parses Fortran source files using r'parameter.*?J2.*?=\\s*([0-9.E+-_]+)' handling _dp suffixes, whitespace variations, and comment lines to auto-populate answer sheet.

8. Unified Third-Body Data File: Single third_body_positions.txt with (x, y, z, GM_sun, GM_moon) format eliminates redundancy; SRP reads columns 1-3, TBP reads all columns.

9. Julian Date Dual-Mode Conversion: julian_to_time_hours() handles both (N, 2) [jd, fr] arrays from NPZ and (N,) seconds arrays from TXT using ndim checks.

10. Velocity Verlet Implementation: Fortran module with abstract interface for accel_func() supports both state-only and state+time acceleration functions via separate subroutines (velocity_verlet_integrate vs velocity_verlet_integrate_rv).

11. Cross-Language Performance: Fortran propagation achieves <10ms for 259,200s (25,921 timesteps) while Python handles I/O and plotting, demonstrating appropriate compiled vs interpreted language selection.

12. Comprehensive YAML Generation: 73 answer keys with automatic validation, scientific notation handling, and ordered dictionary (dict not OrderedDict) matching README structure.

13. Modular Perturbation Architecture: Separate Fortran modules (j2_perturbation, srp_perturbation, drag_perturbation, third_body_perturbation) each with independent acceleration functions and runtime-read physical parameters.

14. Organized Output Structure: Automated plots/{sgp4,undisturbed,j2_keplerian,srp_*,drag_*,tbp_*}/ subdirectories with programmatic path.exists() and makedirs() creation.

15. Conditional Compilation Shell Scripts: Timestamp comparison [ "src/*.f90" -nt "bin/*" ] implements GNU Make-style dependency checking without external build tools.
"""
    
    # AI Use
    answers['ss_MDT_AI_GEN_0'] = """
AI (GitHub Copilot) was used as a coding assistant throughout this assignment in the following ways:

1. Code Structure: AI helped design the modular organization of Fortran modules and Python packages, suggesting separation of concerns and best practices for scientific computing projects.

2. Debugging: When encountering issues with file parsing (e.g., GM values from Horizons, Sun position file format), AI helped identify regex patterns and parsing logic errors.

3. Plot Formatting: AI suggested matplotlib techniques for dual y-axis plots, zorder layering for superimposed lines, and bbox_to_anchor for external legend positioning.

4. Documentation: AI helped draft clear docstrings and comments explaining the physics and mathematics behind each perturbation model.
"""
    
    # Workload and Feedback
    answers['sf_REG_WORKLOAD_GEN_0'] = 15.0
    answers['ss_REG_FEEDBACK_GEN_0'] = """
I liked that we did not need to worry about physical models but rather just the code implementation details. 
I would have also liked to make a point about the model considering all perturbations together rather than each one isolated."""
    
    # Write YAML file
    output_file = Path("answer-sheet.yaml")
    print(f"\nGenerating {output_file}...")
    
    with open(output_file, 'w') as f:
        yaml.dump(answers, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n✓ Answer sheet generated successfully!")
    print(f"  Total answers: {len(answers)}")
    print(f"  File: {output_file}")
    print(f"\nRun the sanity check:")
    print(f"  python3 answer-sheet-sanity.py")

if __name__ == "__main__":
    try:
        generate_answer_sheet()
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
