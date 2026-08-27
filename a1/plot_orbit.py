#!/usr/bin/env python3
"""Plot orbit data from SGP4 propagation results.

This script creates visualizations of the satellite orbit including:
- Position and velocity components vs time
- 3D orbit visualization
- Altitude vs time
- Ground track (optional)
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys, inspect 


def plot_position_velocity_vs_time(times_jd, positions, velocities, sat_name, output_prefix='plots/orbit'):
    """Plot position and velocity components vs time.
    
    Args:
        times_jd: (N, 2) array of Julian dates
        positions: (N, 3) array of positions [km]
        velocities: (N, 3) array of velocities [km/s]
        sat_name: Satellite name for title
        output_prefix: Prefix for output filenames
    """
    # Convert Julian dates to hours from start
    jd_start = times_jd[0, 0] + times_jd[0, 1]
    times_hours = (times_jd[:, 0] + times_jd[:, 1] - jd_start) * 24.0
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot position components
    ax1.plot(times_hours, positions[:, 0], 'r-', label='X', linewidth=1.5)
    ax1.plot(times_hours, positions[:, 1], 'g-', label='Y', linewidth=1.5)
    ax1.plot(times_hours, positions[:, 2], 'b-', label='Z', linewidth=1.5)
    ax1.set_xlabel('Time [hours]', fontsize=12)
    ax1.set_ylabel('Position [km]', fontsize=12)
    ax1.set_title(f'Position Components vs Time - {sat_name}', fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Plot velocity components
    ax2.plot(times_hours, velocities[:, 0], 'r-', label='Vx', linewidth=1.5)
    ax2.plot(times_hours, velocities[:, 1], 'g-', label='Vy', linewidth=1.5)
    ax2.plot(times_hours, velocities[:, 2], 'b-', label='Vz', linewidth=1.5)
    ax2.set_xlabel('Time [hours]', fontsize=12)
    ax2.set_ylabel('Velocity [km/s]', fontsize=12)
    ax2.set_title(f'Velocity Components vs Time - {sat_name}', fontsize=14, fontweight='bold')
    ax2.legend(loc='best', fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename = f'{output_prefix}_pos_vel_vs_time.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f'Saved: {filename}')
    plt.close()


def plot_orbit_3d(positions, sat_name, output_prefix='plots/orbit'):
    """Plot 3D orbit visualization.
    
    Args:
        positions: (N, 3) array of positions [km]
        sat_name: Satellite name for title
        output_prefix: Prefix for output filenames
    """
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot Earth
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    r_earth = 6378.137  # km
    x_earth = r_earth * np.outer(np.cos(u), np.sin(v))
    y_earth = r_earth * np.outer(np.sin(u), np.sin(v))
    z_earth = r_earth * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x_earth, y_earth, z_earth, color='lightblue', alpha=0.6, edgecolor='none')
    
    # Plot orbit
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'r-', linewidth=2, label='Orbit')
    
    # Set labels and title
    ax.set_xlabel('X [km]', fontsize=11)
    ax.set_ylabel('Y [km]', fontsize=11)
    ax.set_zlabel('Z [km]', fontsize=11)
    ax.set_title(f'3D Orbit Visualization - {sat_name}', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    
    # Set equal aspect ratio
    max_range = np.array([positions[:, 0].max()-positions[:, 0].min(),
                          positions[:, 1].max()-positions[:, 1].min(),
                          positions[:, 2].max()-positions[:, 2].min()]).max() / 2.0
    mid_x = (positions[:, 0].max()+positions[:, 0].min()) * 0.5
    mid_y = (positions[:, 1].max()+positions[:, 1].min()) * 0.5
    mid_z = (positions[:, 2].max()+positions[:, 2].min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    filename = f'{output_prefix}_3d.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f'Saved: {filename}')
    plt.close()


def plot_radius_and_speed(times_jd, positions, velocities, sat_name, output_prefix='plots/orbit'):
    """Plot orbital radius and speed vs time.
    
    Args:
        times_jd: (N, 2) array of Julian dates
        positions: (N, 3) array of positions [km]
        velocities: (N, 3) array of velocities [km/s]
        sat_name: Satellite name for title
        output_prefix: Prefix for output filenames
    """
    # Convert Julian dates to hours from start
    jd_start = times_jd[0, 0] + times_jd[0, 1]
    times_hours = (times_jd[:, 0] + times_jd[:, 1] - jd_start) * 24.0
    
    # Calculate radius and speed
    radii = np.linalg.norm(positions, axis=1)
    speeds = np.linalg.norm(velocities, axis=1)
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot orbital radius (absolute values)
    ax1.plot(times_hours, radii, 'b-', linewidth=2)
    ax1.set_xlabel('Time [hours]', fontsize=12)
    ax1.set_ylabel('Orbital Radius [km]', fontsize=12)
    ax1.set_title(f'Orbital Radius vs Time - {sat_name}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=radii.mean(), color='r', linestyle='--', linewidth=1, 
                label=f'Mean: {radii.mean():.1f} km')
    ax1.legend(loc='best', fontsize=11)
    
    # Plot speed
    ax2.plot(times_hours, speeds, 'g-', linewidth=2)
    ax2.set_xlabel('Time [hours]', fontsize=12)
    ax2.set_ylabel('Speed [km/s]', fontsize=12)
    ax2.set_title(f'Speed vs Time - {sat_name}', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=speeds.mean(), color='r', linestyle='--', linewidth=1, 
                label=f'Mean: {speeds.mean():.4f} km/s')
    ax2.legend(loc='best', fontsize=11)
    
    plt.tight_layout()
    filename = f'{output_prefix}_radius_speed.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f'Saved: {filename}')
    plt.close()


def plot_orbital_elements(times_jd, positions, velocities, sat_name, output_prefix='plots/orbit'):
    """Plot classical orbital elements vs time.
    
    Args:
        times_jd: (N, 2) array of Julian dates
        positions: (N, 3) array of positions [km]
        velocities: (N, 3) array of velocities [km/s]
        sat_name: Satellite name for title
        output_prefix: Prefix for output filenames
    """
    # Convert Julian dates to hours from start
    jd_start = times_jd[0, 0] + times_jd[0, 1]
    times_hours = (times_jd[:, 0] + times_jd[:, 1] - jd_start) * 24.0
    
    # Gravitational parameter
    mu = 398600.4418  # km^3/s^2
    
    # Calculate orbital elements
    n = len(positions)
    radii = np.linalg.norm(positions, axis=1)
    speeds = np.linalg.norm(velocities, axis=1)
    
    # Specific angular momentum
    h_vec = np.cross(positions, velocities)
    h_mag = np.linalg.norm(h_vec, axis=1)
    
    # Eccentricity vector
    e_vec = np.zeros_like(positions)
    for i in range(n):
        r_mag = radii[i]
        v_mag = speeds[i]
        e_vec[i] = ((v_mag**2 - mu/r_mag) * positions[i] - 
                    np.dot(positions[i], velocities[i]) * velocities[i]) / mu
    
    eccentricity = np.linalg.norm(e_vec, axis=1)
    
    # Semi-major axis
    specific_energy = 0.5 * speeds**2 - mu / radii
    semi_major_axis = -mu / (2 * specific_energy)
    
    # Inclination
    inclination = np.arccos(h_vec[:, 2] / h_mag) * 180 / np.pi
    
    # Create figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
    
    # Plot semi-major axis
    ax1.plot(times_hours, semi_major_axis, 'b-', linewidth=2)
    ax1.set_xlabel('Time [hours]', fontsize=12)
    ax1.set_ylabel('Semi-major axis [km]', fontsize=12)
    ax1.set_title(f'Semi-major Axis vs Time - {sat_name}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=semi_major_axis.mean(), color='r', linestyle='--', linewidth=1,
                label=f'Mean: {semi_major_axis.mean():.1f} km')
    ax1.legend(loc='best', fontsize=11)
    
    # Plot eccentricity
    ax2.plot(times_hours, eccentricity, 'g-', linewidth=2)
    ax2.set_xlabel('Time [hours]', fontsize=12)
    ax2.set_ylabel('Eccentricity', fontsize=12)
    ax2.set_title(f'Eccentricity vs Time - {sat_name}', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=eccentricity.mean(), color='r', linestyle='--', linewidth=1,
                label=f'Mean: {eccentricity.mean():.6f}')
    ax2.legend(loc='best', fontsize=11)
    
    # Plot inclination
    ax3.plot(times_hours, inclination, 'r-', linewidth=2)
    ax3.set_xlabel('Time [hours]', fontsize=12)
    ax3.set_ylabel('Inclination [degrees]', fontsize=12)
    ax3.set_title(f'Inclination vs Time - {sat_name}', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=inclination.mean(), color='b', linestyle='--', linewidth=1,
                label=f'Mean: {inclination.mean():.4f}°')
    ax3.legend(loc='best', fontsize=11)
    
    plt.tight_layout()
    filename = f'{output_prefix}_orbital_elements.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f'Saved: {filename}')
    plt.close()


def jd_to_datetime(jd_whole, jd_frac):
    """Convert Julian Date to datetime.
    
    Args:
        jd_whole: Whole part of Julian Date
        jd_frac: Fractional part of Julian Date
    
    Returns:
        datetime object
    """
    jd = jd_whole + jd_frac
    # Julian Date to datetime conversion
    # JD 0.0 = January 1, 4713 BC at noon
    # Unix epoch (1970-01-01) = JD 2440587.5
    jd_unix_epoch = 2440587.5
    seconds_since_epoch = (jd - jd_unix_epoch) * 86400.0
    return datetime(1970, 1, 1) + timedelta(seconds=seconds_since_epoch)


def teme_to_ecef(positions_teme, times_jd):
    """Convert TEME positions to ECEF accounting for Earth rotation.
    
    Args:
        positions_teme: (N, 3) array of positions in TEME frame [km]
        times_jd: (N, 2) array of Julian dates [jd_whole, jd_frac]
    
    Returns:
        (N, 3) array of positions in ECEF frame [km]
    """
    # Compute GMST for each time point
    jd_combined = times_jd[:, 0] + times_jd[:, 1]
    
    # GMST calculation (simplified)
    T = (jd_combined - 2451545.0) / 36525.0
    gmst_deg = (280.46061837 
                + 360.98564736629 * (jd_combined - 2451545.0)
                + 0.000387933 * T**2
                - T**3 / 38710000.0)
    gmst_rad = np.deg2rad(gmst_deg % 360.0)
    
    # Rotation matrix R3(GMST) from TEME to ECEF
    cos_gmst = np.cos(gmst_rad)
    sin_gmst = np.sin(gmst_rad)
    
    x_teme = positions_teme[:, 0]
    y_teme = positions_teme[:, 1]
    z_teme = positions_teme[:, 2]
    
    # Apply rotation
    x_ecef = cos_gmst * x_teme + sin_gmst * y_teme
    y_ecef = -sin_gmst * x_teme + cos_gmst * y_teme
    z_ecef = z_teme
    
    return np.column_stack([x_ecef, y_ecef, z_ecef])


def ecef_to_latlon(positions_ecef):
    """Convert ECEF positions to latitude/longitude (geodetic).
    
    Args:
        positions_ecef: (N, 3) array of positions in ECEF frame [km]
    
    Returns:
        latitude [deg], longitude [deg] as (N,) arrays
    """
    x = positions_ecef[:, 0]
    y = positions_ecef[:, 1]
    z = positions_ecef[:, 2]
    
    # Compute geocentric latitude and longitude
    r = np.sqrt(x**2 + y**2 + z**2)
    latitude = np.degrees(np.arcsin(z / r))
    longitude = np.degrees(np.arctan2(y, x))
    
    return latitude, longitude


def plot_groundtrack(positions, times_jd, sat_name, output_prefix='plots/orbit'):
    """Plot satellite groundtrack on Earth map with proper Earth rotation.
    
    Args:
        positions: (N, 3) array of positions in TEME frame [km]
        times_jd: (N, 2) array of Julian dates [jd_whole, jd_frac]
        sat_name: Satellite name for title
        output_prefix: Prefix for output filenames
    """
    # Convert TEME to ECEF (accounting for Earth rotation)
    positions_ecef = teme_to_ecef(positions, times_jd)
    
    # Convert ECEF to lat/lon
    latitude, longitude = ecef_to_latlon(positions_ecef)
    
    # Create figure with PlateCarree projection
    fig = plt.figure(figsize=(16, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Add map features
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.5)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, linestyle='--')
    
    # Plot groundtrack - handle longitude wrapping
    # Split into segments where longitude wraps around
    lon_diff = np.diff(longitude)
    wrap_indices = np.where(np.abs(lon_diff) > 180)[0]
    
    # Plot in segments
    start_idx = 0
    for wrap_idx in wrap_indices:
        ax.plot(longitude[start_idx:wrap_idx+1], latitude[start_idx:wrap_idx+1],
                'r-', linewidth=2, transform=ccrs.Geodetic(), alpha=0.8)
        start_idx = wrap_idx + 1
    
    # Plot final segment
    ax.plot(longitude[start_idx:], latitude[start_idx:],
            'r-', linewidth=2, transform=ccrs.Geodetic(), alpha=0.8, label='Ground Track')
    
    # Get time range for title
    start_time = jd_to_datetime(times_jd[0, 0], times_jd[0, 1])
    end_time = jd_to_datetime(times_jd[-1, 0], times_jd[-1, 1])
    duration_hours = (end_time - start_time).total_seconds() / 3600
    
    ax.set_title(f'Ground Track - {sat_name}\n' +
                f'{start_time.strftime("%Y-%m-%d %H:%M")} to {end_time.strftime("%H:%M UTC")} ' +
                f'({duration_hours:.1f} hours)',
                fontsize=14, fontweight='bold', pad=20)
    
    ax.legend(loc='lower left', fontsize=11, framealpha=0.9)
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
    
    plt.tight_layout()
    filename = f'{output_prefix}_groundtrack.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f'Saved: {filename}')
    plt.close()


def main():
    """Main function to generate all plots."""
    print("=" * 70)
    print("ORBIT PLOTTING")
    print("=" * 70)
    
    # Create plots directory if it doesn't exist
    os.makedirs('plots', exist_ok=True)
    
    # Load propagation data
    print("\nLoading orbit propagation data...")
    data = np.load('data/orbit_propagation.npz')
    
    times_jd = data['times_jd']
    positions = data['positions']
    velocities = data['velocities']
    sat_name = str(data['satellite_name'])
    
    print(f"Satellite: {sat_name}")
    print(f"Number of points: {len(positions)}")
    
    # Create plots
    print("\nGenerating plots...")
    print("-" * 70)
    
    plot_position_velocity_vs_time(times_jd, positions, velocities, sat_name)
    plot_orbit_3d(positions, sat_name)
    plot_radius_and_speed(times_jd, positions, velocities, sat_name)
    plot_orbital_elements(times_jd, positions, velocities, sat_name)
    plot_groundtrack(positions, times_jd, sat_name)
    
    print("-" * 70)
    print("\n" + "=" * 70)
    print("PLOTTING COMPLETE")
    print("=" * 70)
    print("\nGenerated plots in 'plots/' directory:")
    print("  1. plots/orbit_pos_vel_vs_time.png - Position and velocity components")
    print("  2. plots/orbit_3d.png - 3D orbit visualization")
    print("  3. plots/orbit_radius_speed.png - Orbital radius and speed")
    print("  4. plots/orbit_orbital_elements.png - Classical orbital elements")
    print("  5. plots/orbit_groundtrack.png - Satellite ground track")


if __name__ == '__main__':
    main()
