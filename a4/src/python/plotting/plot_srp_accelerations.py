#!/usr/bin/env python3
"""
Compute and plot SRP disturbance acceleration magnitudes along the orbit.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from utilities.keplerian import OrbitDataLoader
from plotting.plot_disturbance_accelerations import plot_disturbance_magnitudes, plot_disturbance_components


# SRP parameters
SOLAR_FLUX = 1361.0        # W/m^2
C_LIGHT = 299792458.0      # m/s
CR_OVER_M = 0.02           # m^2/kg
R_EARTH = 6371000.0        # m (mean)
R_SUN = 696500000.0        # m (from Horizons)

# Sun position (will be loaded from file)
SUN_POSITION = None


def load_sun_position():
    """Load Sun position from file."""
    global SUN_POSITION, R_SUN
    
    sun_file = "data/sgp4_reference/third_body_positions.txt"
    
    if not os.path.exists(sun_file):
        print(f"\nError: Third body position file not found: {sun_file}")
        print("Please run: python src/python/fetch_third_body_positions.py")
        return False
    
    in_sun_section = False
    with open(sun_file, 'r') as f:
        for line in f:
            if line.startswith('# Sun radius:'):
                R_SUN = float(line.split(':')[1].strip().split()[0])
            elif line.startswith('# Sun position'):
                in_sun_section = True
            elif in_sun_section and not line.startswith('#') and line.strip():
                data = line.strip().split()
                SUN_POSITION = np.array([float(data[0]), float(data[1]), float(data[2])])
                break
    
    if SUN_POSITION is None:
        print("\nError: Could not parse Sun position from file")
        return False
    
    print(f"\nSun position loaded:")
    print(f"  X = {SUN_POSITION[0]:.6e} m")
    print(f"  Y = {SUN_POSITION[1]:.6e} m")
    print(f"  Z = {SUN_POSITION[2]:.6e} m")
    print(f"  R_sun = {R_SUN:.6e} m")
    return True


def geometric_shadow_factor(r_sat):
    """
    Compute geometric shadowing factor using Doornbos (2012) Eq. 27-34.
    
    Args:
        r_sat: Satellite position vector [3] in meters
        
    Returns:
        f_g: Geometric shadowing factor [0, 1]
    """
    # Sun position vector (geocentric, from Earth to Sun)
    r_sun_vec = SUN_POSITION
    r_sun_mag = np.linalg.norm(r_sun_vec)
    
    # Unit vector from Earth to Sun
    e_sun = r_sun_vec / r_sun_mag
    
    # r_ps = (e_⊙s · r_⊕s)e_⊙s (Eq. 28) - projection onto Sun-Earth axis
    # Note: e_⊙s points from Sun to Earth, so use -e_sun
    r_ps_scalar = -np.dot(e_sun, r_sat)
    r_ps = -r_ps_scalar * e_sun
    
    # r_⊕p = r_⊕s - r_ps (Eq. 29) - perpendicular component
    r_circle_p = r_sat - r_ps
    
    # h_g = r_⊕p - R_⊕ (Eq. 30) - altitude above Earth surface in perpendicular plane
    h_g = np.linalg.norm(r_circle_p) - R_EARTH
    
    # R_p = (||r_ps|| / r_⊙s) * R_⊙ (Eq. 31) - shadow cone radius at satellite distance
    r_ps_mag = np.linalg.norm(r_ps)
    R_p = (r_ps_mag / r_sun_mag) * R_SUN
    
    # η = h_g / R_p (Eq. 32)
    eta = h_g / R_p
    
    # Apply shadow conditions (Eq. 33-34)
    # eta = h_g / R_p measures how far satellite is from shadow boundary
    # eta >> 1: satellite far outside shadow cone (sunlight)
    # |eta| < 1: satellite near shadow boundary (penumbra/umbra)
    # eta << -1: satellite inside Earth cylinder (umbra)
    if eta < -1.0:
        # Umbra (satellite inside Earth cylinder)
        return 0.0
    elif -1.0 <= eta <= 1.0:
        # Penumbra - calculate fractional area blocked (Eq. 34)
        return 1.0 - (1.0/np.pi) * np.arccos(eta) - (eta/np.pi) * np.sqrt(1.0 - eta**2)
    else:  # eta > 1
        # Full sunlight (satellite outside shadow cone)
        return 1.0


def compute_srp_acceleration(positions_m):
    """
    Compute SRP perturbation acceleration for given positions.
    
    Args:
        positions_m: Position vectors [N x 3] in meters
        
    Returns:
        accelerations: Acceleration vectors [N x 3] in m/s²
        shadow_factors: Shadow factors [N] (0 = umbra, 1 = sunlight)
    """
    n_points = len(positions_m)
    accelerations = np.zeros((n_points, 3))
    shadow_factors = np.zeros(n_points)
    
    r_sun_vec = SUN_POSITION
    
    for i in range(n_points):
        r_sat = positions_m[i]
        r_sun_to_sat = r_sat - r_sun_vec
        r_sun_to_sat_mag = np.linalg.norm(r_sun_to_sat)
        unit_sun_to_sat = r_sun_to_sat / r_sun_to_sat_mag
        
        f_g = geometric_shadow_factor(r_sat)
        shadow_factors[i] = f_g
        
        f_a = 1.0
        P_srp = (SOLAR_FLUX / C_LIGHT) * f_a * f_g
        accelerations[i] = CR_OVER_M * P_srp * unit_sun_to_sat
    
    return accelerations, shadow_factors


def main():
    """Compute and plot SRP acceleration magnitudes."""
    
    print("=" * 70)
    print("SRP DISTURBANCE ACCELERATION MAGNITUDES")
    print("=" * 70)
    
    # Load Sun position
    if not load_sun_position():
        return 1
    
    # File path
    orbit_file = "data/outputs_orbit/dt10s_output.txt"
    output_dir = "plots/srp_accelerations"
    
    # Check if file exists
    if not os.path.exists(orbit_file):
        print(f"\nError: Orbit file not found: {orbit_file}")
        print("Please run: ./src/fortran/build/propagate_orbit")
        return 1
    
    # Load orbit data
    loader = OrbitDataLoader()
    
    print(f"\nLoading orbit from: {orbit_file}")
    times, positions_km, velocities_km, _ = loader.load_from_file(orbit_file)
    print(f"  Loaded {len(times)} data points")
    
    # Convert to meters for acceleration calculation
    positions_m = positions_km * 1000.0
    
    # Convert times to seconds from start
    times_sec = times - times[0]
    
    print(f"\nTime span: {times_sec[0]:.2f} to {times_sec[-1]:.2f} seconds")
    print(f"           ({times_sec[-1]/3600:.2f} hours)")
    
    # Compute SRP accelerations
    print("\nComputing SRP acceleration at each point...")
    acc_srp, shadow_factors = compute_srp_acceleration(positions_m)
    
    # Compute statistics
    acc_srp_mag = np.linalg.norm(acc_srp, axis=1)
    
    # Statistics for sunlight periods
    sunlight_mask = shadow_factors > 0.99
    if np.any(sunlight_mask):
        print(f"\nSRP Acceleration Statistics (sunlight only):")
        print(f"  Mean:   {np.mean(acc_srp_mag[sunlight_mask]):.6e} m/s²")
        print(f"  Median: {np.median(acc_srp_mag[sunlight_mask]):.6e} m/s²")
        print(f"  Min:    {np.min(acc_srp_mag[sunlight_mask]):.6e} m/s²")
        print(f"  Max:    {np.max(acc_srp_mag[sunlight_mask]):.6e} m/s²")
        print(f"  Std:    {np.std(acc_srp_mag[sunlight_mask]):.6e} m/s²")
    
    print(f"\nSRP Acceleration Statistics (all points):")
    print(f"  Mean:   {np.mean(acc_srp_mag):.6e} m/s²")
    print(f"  Median: {np.median(acc_srp_mag):.6e} m/s²")
    print(f"  Min:    {np.min(acc_srp_mag):.6e} m/s²")
    print(f"  Max:    {np.max(acc_srp_mag):.6e} m/s²")
    print(f"  Std:    {np.std(acc_srp_mag):.6e} m/s²")
    
    # Shadow statistics
    eclipse_mask = shadow_factors < 0.01
    penumbra_mask = (shadow_factors >= 0.01) & (shadow_factors <= 0.99)
    print(f"\nShadow Statistics:")
    print(f"  Umbra (f_g < 0.01):      {np.sum(eclipse_mask)} points ({np.sum(eclipse_mask)/len(shadow_factors)*100:.2f}%)")
    print(f"  Penumbra (0.01 ≤ f_g ≤ 0.99): {np.sum(penumbra_mask)} points ({np.sum(penumbra_mask)/len(shadow_factors)*100:.2f}%)")
    print(f"  Sunlight (f_g > 0.99):   {np.sum(sunlight_mask)} points ({np.sum(sunlight_mask)/len(shadow_factors)*100:.2f}%)")
    
    # Compute two-body acceleration for comparison
    print("\nComputing two-body acceleration for comparison...")
    r_mag = np.linalg.norm(positions_m, axis=1)
    MU_EARTH = 3.986004418e14  # m^3/s^2
    acc_twobody_mag = MU_EARTH / r_mag**2
    
    # Compute ratio
    if np.any(sunlight_mask):
        ratio = acc_srp_mag[sunlight_mask] / acc_twobody_mag[sunlight_mask] * 100
        print(f"\nSRP / Two-body ratio (sunlight only):")
        print(f"  Mean:   {np.mean(ratio):.6f}%")
        print(f"  Max:    {np.max(ratio):.6f}%")
    
    # Create plots
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nGenerating plots...")
    
    # Plot 1: SRP magnitude only
    print("  Plot 1: SRP acceleration magnitude...")
    fig1 = plot_disturbance_magnitudes(
        times_sec,
        {'SRP': acc_srp},
        time_unit='hours',
        acc_unit='m/s²',
        title='SRP Disturbance Acceleration Magnitude',
        use_log_scale=False
    )
    filename1 = os.path.join(output_dir, 'srp_magnitude.png')
    fig1.savefig(filename1, dpi=300, bbox_inches='tight')
    print(f"    Saved: {filename1}")
    
    # Plot 2: SRP components breakdown
    print("  Plot 2: SRP acceleration components...")
    fig2 = plot_disturbance_components(
        times_sec,
        acc_srp,
        'SRP',
        time_unit='hours',
        acc_unit='m/s²'
    )
    filename2 = os.path.join(output_dir, 'srp_components.png')
    fig2.savefig(filename2, dpi=300, bbox_inches='tight')
    print(f"    Saved: {filename2}")
    
    # Plot 3: Shadow factor along orbit
    print("  Plot 3: Shadow factor...")
    
    fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Top: Acceleration magnitude
    ax1.plot(times_sec/3600, acc_srp_mag, 'r-', linewidth=1.0)
    ax1.set_ylabel('SRP Acceleration [m/s²]', fontsize=13)
    ax1.set_title('SRP Acceleration with Shadow Periods', fontsize=15, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    if np.max(acc_srp_mag) > 0:
        ax1.set_yscale('log')
    
    # Bottom: Shadow factor
    ax2.plot(times_sec/3600, shadow_factors, 'k-', linewidth=1.0)
    ax2.fill_between(times_sec/3600, 0, shadow_factors, alpha=0.3, color='orange')
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=1, alpha=0.5, label='Umbra')
    ax2.axhline(y=1, color='g', linestyle='--', linewidth=1, alpha=0.5, label='Sunlight')
    ax2.set_xlabel('Time [hours]', fontsize=13)
    ax2.set_ylabel('Shadow Factor $f_g$ [-]', fontsize=13)
    ax2.set_ylim([-0.05, 1.05])
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    
    plt.tight_layout()
    filename3 = os.path.join(output_dir, 'srp_with_shadow.png')
    fig3.savefig(filename3, dpi=300, bbox_inches='tight')
    print(f"    Saved: {filename3}")
    
    print("\n" + "=" * 70)
    print("PLOTTING COMPLETE")
    print("=" * 70)
    print(f"\nPlots saved to: {output_dir}/")
    print("Close the plot windows to exit.")
    
    # Show plots
    plt.show()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
