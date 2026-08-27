#!/usr/bin/env python3
"""
Plot atmospheric drag accelerations over the propagation period.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Constants
R_EARTH = 6371.0e3  # Earth's mean radius [m]
OMEGA_EARTH = 2 * np.pi / 86164.0905  # Earth's angular velocity [rad/s] (sidereal day)
BALLISTIC_COEFF = 0.01  # B = C_D * A / m [m^2/kg]

# Atmospheric parameters (from table, altitude >= 35786 km)
RHO_0 = 4.04e-19  # Mean density [kg/m^3]
H_SCALE = 37300.0e3  # Scale height [m]

def atmospheric_density(r_sat):
    """Compute atmospheric density using exponential model."""
    r_mag = np.linalg.norm(r_sat, axis=1)
    h = r_mag - R_EARTH
    rho = RHO_0 * np.exp(-h / H_SCALE)
    return rho

def drag_acceleration(r_sat, v_sat):
    """Compute drag acceleration."""
    # Earth's angular velocity vector (aligned with z-axis)
    omega_vec = np.array([0, 0, OMEGA_EARTH])
    
    # Relative velocity: v_rel = v_sat - ω_⊕ × r_sat
    # Cross product for each position
    v_rel = v_sat - np.cross(omega_vec, r_sat)
    
    # Magnitude of relative velocity
    v_rel_mag = np.linalg.norm(v_rel, axis=1)
    
    # Get atmospheric density
    rho = atmospheric_density(r_sat)
    
    # Drag acceleration: a_drag = -1/2 * ρ * B * |v_rel| * v_rel
    a_drag = -0.5 * rho[:, np.newaxis] * BALLISTIC_COEFF * v_rel_mag[:, np.newaxis] * v_rel
    
    return a_drag, rho

def load_orbit_data(filepath):
    """Load orbit data from file."""
    data = np.loadtxt(filepath)
    return data[:, 0], data[:, 1:4], data[:, 4:7]  # time, position, velocity

def main():
    # Setup paths
    base_dir = Path(__file__).resolve().parents[2]
    output_dir = base_dir / "data" / "outputs_drag"
    plot_dir = base_dir / "plots" / "drag_accelerations"
    plot_dir.mkdir(parents=True, exist_ok=True)
    
    # Load drag-perturbed orbit data
    print("Loading orbit data...")
    filepath = output_dir / "dt10s_drag_output.txt"
    print(f"  File: {filepath}")
    
    t, r, v = load_orbit_data(filepath)
    t_hrs = t / 3600.0  # Convert to hours
    
    # Compute drag accelerations
    print("\nComputing drag accelerations...")
    a_drag, rho = drag_acceleration(r, v)
    a_drag_mag = np.linalg.norm(a_drag, axis=1)
    
    # Statistics
    print(f"\nDrag Acceleration Statistics:")
    print(f"  Mean:   {np.mean(a_drag_mag):.6e} m/s²")
    print(f"  Median: {np.median(a_drag_mag):.6e} m/s²")
    print(f"  Min:    {np.min(a_drag_mag):.6e} m/s²")
    print(f"  Max:    {np.max(a_drag_mag):.6e} m/s²")
    print(f"  Std:    {np.std(a_drag_mag):.6e} m/s²")
    
    print(f"\nAtmospheric Density Statistics:")
    print(f"  Mean:   {np.mean(rho):.6e} kg/m³")
    print(f"  Median: {np.median(rho):.6e} kg/m³")
    print(f"  Min:    {np.min(rho):.6e} kg/m³")
    print(f"  Max:    {np.max(rho):.6e} kg/m³")
    
    # Compute altitude
    r_mag = np.linalg.norm(r, axis=1)
    h = (r_mag - R_EARTH) / 1000.0  # Convert to km
    
    print(f"\nAltitude Statistics:")
    print(f"  Mean:   {np.mean(h):.2f} km")
    print(f"  Min:    {np.min(h):.2f} km")
    print(f"  Max:    {np.max(h):.2f} km")
    
    # Plot 1: Drag acceleration magnitude over time
    print("\nGenerating Plot 1: Drag acceleration magnitude...")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(t_hrs, a_drag_mag * 1e15, 'b-', linewidth=1.5, label='Drag acceleration')
    ax.set_xlabel('Time [hours]', fontsize=12)
    ax.set_ylabel('Drag Acceleration [10⁻¹⁵ m/s²]', fontsize=12)
    ax.set_title('Atmospheric Drag Acceleration Magnitude', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(plot_dir / 'drag_acceleration_magnitude.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 2: Drag acceleration components
    print("Generating Plot 2: Drag acceleration components...")
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    components = ['X', 'Y', 'Z']
    colors = ['r', 'g', 'b']
    
    for i, (ax, comp, color) in enumerate(zip(axes, components, colors)):
        ax.plot(t_hrs, a_drag[:, i] * 1e15, color=color, linewidth=1.5, label=f'{comp}-component')
        ax.set_ylabel(f'$a_{{{comp}}}$ [10⁻¹⁵ m/s²]', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
    
    axes[-1].set_xlabel('Time [hours]', fontsize=12)
    axes[0].set_title('Atmospheric Drag Acceleration Components', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(plot_dir / 'drag_acceleration_components.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 3: Atmospheric density over time
    print("Generating Plot 3: Atmospheric density...")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(t_hrs, rho * 1e19, 'purple', linewidth=1.5, label='Atmospheric density')
    ax.set_xlabel('Time [hours]', fontsize=12)
    ax.set_ylabel('Density [10⁻¹⁹ kg/m³]', fontsize=12)
    ax.set_title('Atmospheric Density at Satellite Position', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(plot_dir / 'atmospheric_density.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 4: Combined plot - acceleration magnitude and altitude
    print("Generating Plot 4: Combined acceleration and altitude...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Drag acceleration magnitude
    ax1.plot(t_hrs, a_drag_mag * 1e15, 'b-', linewidth=1.5, label='Drag acceleration')
    ax1.set_ylabel('Drag Acceleration [10⁻¹⁵ m/s²]', fontsize=12)
    ax1.set_title('Atmospheric Drag Acceleration and Altitude', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11)
    
    # Altitude
    ax2.plot(t_hrs, h, 'orange', linewidth=1.5, label='Altitude')
    ax2.set_xlabel('Time [hours]', fontsize=12)
    ax2.set_ylabel('Altitude [km]', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig(plot_dir / 'drag_acceleration_and_altitude.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nPlots saved to: {plot_dir}")
    print("  - drag_acceleration_magnitude.png")
    print("  - drag_acceleration_components.png")
    print("  - atmospheric_density.png")
    print("  - drag_acceleration_and_altitude.png")
    print("\nDone!")

if __name__ == "__main__":
    main()
