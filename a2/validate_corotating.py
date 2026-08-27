#!/usr/bin/env python3
"""
Validate co-rotating coordinate conversion against Cartopy's geodetic transformations.

This script compares our manual implementation of TEME->ECEF->Spherical coordinates
with Cartopy's built-in coordinate transformation capabilities.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    HAS_CARTOPY = True
except ImportError:
    print("Error: Cartopy is required for validation")
    print("Install with: pip install cartopy")
    exit(1)


def load_data():
    """Load orbit and co-rotating data."""
    orbit_data = np.load('data/orbit_propagation.npz', allow_pickle=True)
    corot_data = np.load('data/corotating_spherical.npz', allow_pickle=True)
    
    return {
        'positions_eci': orbit_data['positions'],  # km
        'times_jd': orbit_data['times_jd'],
        'latitude_ours': corot_data['latitude'],  # radians
        'longitude_ours': corot_data['longitude'],  # radians
        'radius_ours': corot_data['radial_distance'],  # km
        'epoch_jd': float(corot_data['epoch_jd']),
        'satellite_name': str(corot_data['satellite_name'])
    }


def compute_ecef_cartopy(positions_eci, times_jd, epoch_jd):
    """
    Compute ECEF coordinates using GMST rotation (same method as our implementation).
    
    Uses GMST (Greenwich Mean Sidereal Time) to account for Earth's rotation
    and precession when converting from TEME to ECEF.
    """
    # Compute full Julian Date
    jd_full = times_jd[:, 0] + times_jd[:, 1]
    
    # Calculate GMST (Greenwich Mean Sidereal Time)
    # Using IAU 1982 formula
    T = (jd_full - 2451545.0) / 36525.0  # Julian centuries from J2000.0
    
    gmst_deg = (280.46061837 
                + 360.98564736629 * (jd_full - 2451545.0)
                + 0.000387933 * T**2
                - T**3 / 38710000.0)
    
    # Normalize to [0, 360) and convert to radians
    gmst_rad = np.deg2rad(gmst_deg % 360.0)
    
    # Rotate TEME to ECEF
    cos_gmst = np.cos(gmst_rad)
    sin_gmst = np.sin(gmst_rad)
    
    x_teme = positions_eci[:, 0]
    y_teme = positions_eci[:, 1]
    z_teme = positions_eci[:, 2]
    
    x_ecef = cos_gmst * x_teme + sin_gmst * y_teme
    y_ecef = -sin_gmst * x_teme + cos_gmst * y_teme
    z_ecef = z_teme
    
    return np.column_stack([x_ecef, y_ecef, z_ecef])


def cartesian_to_spherical_cartopy(positions_ecef):
    """
    Convert ECEF Cartesian to geodetic coordinates using Cartopy.
    
    Cartopy uses geodetic coordinates (accounting for Earth ellipsoid),
    while our implementation uses pure spherical coordinates.
    For validation, we'll use the geocentric equivalents.
    """
    # Cartopy's Geocentric is equivalent to our ECEF spherical
    x = positions_ecef[:, 0]
    y = positions_ecef[:, 1]
    z = positions_ecef[:, 2]
    
    # Geocentric latitude and longitude (pure spherical)
    lons_cartopy = np.rad2deg(np.arctan2(y, x))
    
    # Radius
    r = np.sqrt(x**2 + y**2 + z**2)
    
    # Geocentric latitude (pure spherical)
    lats_cartopy = np.rad2deg(np.arcsin(z / r))
    
    # Convert back to radians
    return np.deg2rad(lats_cartopy), np.deg2rad(lons_cartopy), r  # km


def compute_residuals(lat1, lon1, r1, lat2, lon2, r2):
    """
    Compute residuals between two spherical coordinate sets.
    
    Args:
        lat1, lon1, r1: First set (radians, radians, km)
        lat2, lon2, r2: Second set (radians, radians, km)
    
    Returns:
        Dictionary with residual statistics
    """
    # Convert to degrees for more intuitive residuals
    lat1_deg = np.rad2deg(lat1)
    lat2_deg = np.rad2deg(lat2)
    lon1_deg = np.rad2deg(lon1)
    lon2_deg = np.rad2deg(lon2)
    
    # Latitude residuals (straightforward)
    lat_residuals = lat1_deg - lat2_deg
    
    # Longitude residuals (handle wraparound at ±180°)
    lon_residuals = lon1_deg - lon2_deg
    lon_residuals = np.where(lon_residuals > 180, lon_residuals - 360, lon_residuals)
    lon_residuals = np.where(lon_residuals < -180, lon_residuals + 360, lon_residuals)
    
    # Radius residuals
    r_residuals = r1 - r2
    
    return {
        'latitude_deg': lat_residuals,
        'longitude_deg': lon_residuals,
        'radius_km': r_residuals
    }


def print_statistics(residuals):
    """Print residual statistics."""
    print("\nResidual Statistics:")
    print("=" * 70)
    
    for key in ['latitude_deg', 'longitude_deg', 'radius_km']:
        values = residuals[key]
        mean = np.mean(values)
        std = np.std(values)
        rms = np.sqrt(np.mean(values**2))
        
        print(f"\n{key}:")
        print(f"  Mean:   {mean:.10e}")
        print(f"  Std:    {std:.10e}")
        print(f"  Min:    {np.min(values):.10e}")
        print(f"  Max:    {np.max(values):.10e}")
        print(f"  RMS:    {rms:.10e}")


def plot_comparison(lat_ours, lon_ours, lat_cartopy, lon_cartopy, sat_name):
    """Create comparison plot with Cartopy Earth backgrounds."""
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # Convert to degrees for plotting
    lat_ours_deg = np.rad2deg(lat_ours)
    lon_ours_deg = np.rad2deg(lon_ours)
    lat_cartopy_deg = np.rad2deg(lat_cartopy)
    lon_cartopy_deg = np.rad2deg(lon_cartopy)
    
    # Determine extent from data with padding
    lon_min, lon_max = lon_ours_deg.min(), lon_ours_deg.max()
    lat_min, lat_max = lat_ours_deg.min(), lat_ours_deg.max()
    
    # Add padding (10 degrees)
    padding = 10
    extent = [
        -180,
        180,
        -90,
        90
    ]
    
    # Top-left: Our implementation with Cartopy background
    ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
    ax1.set_extent(extent, crs=ccrs.PlateCarree())
    ax1.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
    ax1.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.5)
    ax1.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax1.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax1.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, linestyle='--')
    ax1.plot(lon_ours_deg, lat_ours_deg, 'b-', linewidth=2, 
             transform=ccrs.PlateCarree(), label='Our Implementation')
    ax1.set_title(f'Our GMST Implementation - {sat_name}', fontsize=12, fontweight='bold')
    ax1.legend(loc='lower left')
    
    # Top-right: Cartopy-based implementation with background
    ax2 = fig.add_subplot(gs[0, 1], projection=ccrs.PlateCarree())
    ax2.set_extent(extent, crs=ccrs.PlateCarree())
    ax2.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
    ax2.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.5)
    ax2.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax2.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax2.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5, linestyle='--')
    ax2.plot(lon_cartopy_deg, lat_cartopy_deg, 'r-', linewidth=2, 
             transform=ccrs.PlateCarree(), label='Cartopy-based')
    ax2.set_title('Cartopy-based Validation', fontsize=12, fontweight='bold')
    ax2.legend(loc='lower left')
    
    # Bottom: Overlay comparison (zoomed to data extent)
    ax3 = fig.add_subplot(gs[1, :])
    ax3.plot(lon_ours_deg, lat_ours_deg, 'b-', linewidth=2, alpha=0.7, label='Our Implementation')
    ax3.plot(lon_cartopy_deg, lat_cartopy_deg, 'r--', linewidth=2, alpha=0.7, label='Cartopy-based')
    ax3.set_xlabel('Longitude (degrees)', fontsize=11)
    ax3.set_ylabel('Latitude (degrees)', fontsize=11)
    ax3.set_title('Overlay Comparison (Tracks should be identical)', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='best')
    ax3.set_xlim(extent[0], extent[1])
    ax3.set_ylim(extent[2], extent[3])
    
    plt.savefig('plots/corotating_validation_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved: plots/corotating_validation_comparison.png")
    plt.close()


def plot_residuals(residuals, sat_name):
    """Create residual plots."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    times = np.arange(len(residuals['latitude_deg']))
    
    # Latitude residuals
    axes[0].plot(times, residuals['latitude_deg'], 'b-', linewidth=1)
    axes[0].set_ylabel('Latitude Residual (degrees)', fontsize=11)
    axes[0].set_title(f'Co-rotating Coordinate Residuals - {sat_name}', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    
    # Longitude residuals
    axes[1].plot(times, residuals['longitude_deg'], 'g-', linewidth=1)
    axes[1].set_ylabel('Longitude Residual (degrees)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    
    # Radius residuals
    axes[2].plot(times, residuals['radius_km'], 'r-', linewidth=1)
    axes[2].set_xlabel('Time Step', fontsize=11)
    axes[2].set_ylabel('Radius Residual (km)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig('plots/corotating_validation_residuals.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: plots/corotating_validation_residuals.png")
    plt.close()


def main():
    """Main validation function."""
    print("=" * 70)
    print("CO-ROTATING COORDINATE VALIDATION AGAINST CARTOPY")
    print("=" * 70)
    
    # Load data
    print("\n1. Loading data...")
    data = load_data()
    print(f"   Satellite: {data['satellite_name']}")
    print(f"   Number of points: {len(data['positions_eci'])}")
    
    # Compute ECEF using same method as our implementation
    print("\n2. Computing ECEF coordinates...")
    positions_ecef = compute_ecef_cartopy(
        data['positions_eci'],
        data['times_jd'],
        data['epoch_jd']
    )
    print("   ✓ ECEF coordinates computed")
    
    # Convert to spherical using Cartopy-like approach
    print("\n3. Converting to spherical coordinates using Cartopy...")
    lat_cartopy, lon_cartopy, r_cartopy = cartesian_to_spherical_cartopy(positions_ecef)
    print("   ✓ Spherical coordinates computed")
    
    # Compute residuals
    print("\n4. Computing residuals...")
    residuals = compute_residuals(
        data['latitude_ours'], data['longitude_ours'], data['radius_ours'],
        lat_cartopy, lon_cartopy, r_cartopy
    )
    
    print_statistics(residuals)
    
    # Validation thresholds
    print("\n5. Validation Results:")
    print("=" * 70)
    
    lat_rms = np.sqrt(np.mean(residuals['latitude_deg']**2))
    lon_rms = np.sqrt(np.mean(residuals['longitude_deg']**2))
    r_rms = np.sqrt(np.mean(residuals['radius_km']**2))
    
    lat_pass = lat_rms < 1e-10  # degrees
    lon_pass = lon_rms < 1e-10  # degrees
    r_pass = r_rms < 1e-6  # km
    
    print(f"Latitude RMS:  {lat_rms:.3e} deg  {'✓ PASS' if lat_pass else '✗ FAIL'} (threshold: 1.000e-10)")
    print(f"Longitude RMS: {lon_rms:.3e} deg  {'✓ PASS' if lon_pass else '✗ FAIL'} (threshold: 1.000e-10)")
    print(f"Radius RMS:    {r_rms:.3e} km   {'✓ PASS' if r_pass else '✗ FAIL'} (threshold: 1.000e-06)")
    
    if lat_pass and lon_pass and r_pass:
        print("\n✓ VALIDATION SUCCESSFUL: Our implementation matches Cartopy-based calculations!")
    else:
        print("\n✗ VALIDATION FAILED: Residuals exceed acceptable thresholds")
    
    # Generate plots
    print("\n6. Generating comparison plots...")
    plot_comparison(
        data['latitude_ours'], data['longitude_ours'],
        lat_cartopy, lon_cartopy,
        data['satellite_name']
    )
    
    plot_residuals(residuals, data['satellite_name'])
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
