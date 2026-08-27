#!/usr/bin/env python3
"""
Plot co-rotating spherical coordinates (ground track and radial distance).

Creates visualizations of:
1. Ground track (longitude vs latitude)
2. Radial distance evolution over time
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
from PIL import Image


def plot_groundtrack(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    times_hours: np.ndarray,
    satellite_name: str
) -> None:
    """
    Plot satellite ground track on Earth map projection.
    
    Args:
        latitude_deg: Latitude in degrees [N]
        longitude_deg: Longitude in degrees [N]
        times_hours: Time in hours since epoch [N]
        satellite_name: Name of satellite
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Load and display Earth map as background
    try:
        earth_img = Image.open('eo_base_2020_clean_3600x1800.png')
        ax.imshow(earth_img, extent=[-180, 180, -90, 90], aspect='auto', alpha=0.8, zorder=0)
    except FileNotFoundError:
        print("Warning: Earth map image not found, plotting without background")
    
    # Plot ground track as a simple line
    ax.plot(longitude_deg, latitude_deg, 'r-', linewidth=2, alpha=0.9, zorder=2)
    
    # Grid and labels
    ax.grid(True, alpha=0.2, linestyle='--', zorder=1, color='gray', linewidth=0.5)
    ax.set_xlabel('Longitude (degrees)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude (degrees)', fontsize=12, fontweight='bold')
    ax.set_title(f'Ground Track - {satellite_name}', fontsize=14, fontweight='bold')
    
    # Set axis limits to world map
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    
    # Add reference lines
    ax.axhline(y=0, color='k', linewidth=1, alpha=0.4, zorder=1)  # Equator
    ax.axvline(x=0, color='k', linewidth=1, alpha=0.4, zorder=1)  # Prime meridian
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('plots', exist_ok=True)
    plt.savefig('plots/groundtrack.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: plots/groundtrack.png")
    plt.close()


def plot_radial_distance(
    times_hours: np.ndarray,
    radial_distance_km: np.ndarray,
    satellite_name: str
) -> None:
    """
    Plot radial distance evolution over time.
    
    Args:
        times_hours: Time in hours since epoch [N]
        radial_distance_km: Radial distance in km [N]
        satellite_name: Name of satellite
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot radial distance
    ax.plot(times_hours, radial_distance_km, 'b-', linewidth=1.5, alpha=0.7)
    
    # Add mean line
    mean_radius = np.mean(radial_distance_km)
    ax.axhline(y=mean_radius, color='r', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_radius:.2f} km', alpha=0.7)
    
    # Grid and labels
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Radial Distance (km)', fontsize=12, fontweight='bold')
    ax.set_title(f'Radial Distance Evolution - {satellite_name}', fontsize=14, fontweight='bold')
    
    ax.legend(loc='best', fontsize=10)
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('plots', exist_ok=True)
    plt.savefig('plots/radial_distance.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: plots/radial_distance.png")
    plt.close()


def plot_latitude_longitude_time(
    times_hours: np.ndarray,
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    satellite_name: str
) -> None:
    """
    Plot latitude and longitude evolution over time.
    
    Args:
        times_hours: Time in hours since epoch [N]
        latitude_deg: Latitude in degrees [N]
        longitude_deg: Longitude in degrees [N]
        satellite_name: Name of satellite
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot latitude
    ax1.plot(times_hours, latitude_deg, 'b-', linewidth=1.5, alpha=0.7)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_ylabel('Latitude (degrees)', fontsize=12, fontweight='bold')
    ax1.set_title(f'Latitude and Longitude Evolution - {satellite_name}', 
                  fontsize=14, fontweight='bold')
    ax1.axhline(y=0, color='k', linewidth=0.5, alpha=0.3)
    
    # Plot longitude
    ax2.plot(times_hours, longitude_deg, 'r-', linewidth=1.5, alpha=0.7)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Longitude (degrees)', fontsize=12, fontweight='bold')
    ax2.axhline(y=0, color='k', linewidth=0.5, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('plots', exist_ok=True)
    plt.savefig('plots/latitude_longitude_time.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: plots/latitude_longitude_time.png")
    plt.close()


def main():
    """
    Main function to generate all co-rotating coordinate plots.
    """
    print("=" * 70)
    print("GENERATING CO-ROTATING SPHERICAL COORDINATE PLOTS")
    print("=" * 70)
    
    # Load data
    print("\n1. Loading co-rotating spherical coordinate data...")
    data = np.load('data/corotating_spherical.npz', allow_pickle=True)
    
    latitude = data['latitude']  # radians
    longitude = data['longitude']  # radians
    radial_distance = data['radial_distance']  # km
    times_jd = data['times_jd']
    satellite_name = str(data['satellite_name'])
    
    # Convert to degrees
    latitude_deg = np.rad2deg(latitude)
    longitude_deg = np.rad2deg(longitude)
    
    # Calculate time in hours
    time_0 = times_jd[0, 0] + times_jd[0, 1]
    times_full = times_jd[:, 0] + times_jd[:, 1]
    times_hours = (times_full - time_0) * 24.0  # Convert days to hours
    
    print(f"   Satellite: {satellite_name}")
    print(f"   Number of points: {len(latitude)}")
    
    # Generate plots
    print("\n2. Generating plots...")
    
    print("\n   Creating ground track plot...")
    plot_groundtrack(latitude_deg, longitude_deg, times_hours, satellite_name)
    
    print("\n   Creating radial distance plot...")
    plot_radial_distance(times_hours, radial_distance, satellite_name)
    
    print("\n   Creating latitude/longitude time series plot...")
    plot_latitude_longitude_time(times_hours, latitude_deg, longitude_deg, satellite_name)
    
    print("\n" + "=" * 70)
    print("PLOTTING COMPLETE")
    print("=" * 70)
    print("\nGenerated plots:")
    print("  - plots/groundtrack.png")
    print("  - plots/radial_distance.png")
    print("  - plots/latitude_longitude_time.png")


if __name__ == '__main__':
    main()
