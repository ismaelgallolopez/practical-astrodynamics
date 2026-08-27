#!/usr/bin/env python3
"""
Convert TEME Cartesian coordinates to Co-rotating Spherical Coordinates.

This module implements the transformation from True Equator Mean Equinox (TEME)
Cartesian coordinates (output from SGP4) to Earth-Centered Earth-Fixed (ECEF) 
spherical coordinates (latitude, longitude, radial distance) using GMST rotation.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class CorotatingSphericalState:
    """
    Container for co-rotating spherical coordinates.
    
    Attributes:
        latitude: Latitude in radians [N]
        longitude: Longitude in radians [N]
        radial_distance: Radial distance in km [N]
        n_points: Number of state vectors
    """
    latitude: np.ndarray
    longitude: np.ndarray
    radial_distance: np.ndarray
    
    @property
    def n_points(self) -> int:
        return len(self.latitude)
    
    def __repr__(self):
        lat_mean = np.rad2deg(np.mean(self.latitude))
        lon_mean = np.rad2deg(np.mean(self.longitude))
        r_mean = np.mean(self.radial_distance)
        return f"CorotatingSphericalState(n_points={self.n_points}, lat_mean={lat_mean:.2f}°, lon_mean={lon_mean:.2f}°, r_mean={r_mean:.2f} km)"


class CorotatingConverter:
    """
    Converter for transforming TEME Cartesian coordinates to Co-rotating Spherical Coordinates.
    
    The transformation involves:
    1. Convert TEME to ECEF (Earth-Centered Earth-Fixed) using GMST rotation
    2. Convert ECEF Cartesian to Spherical coordinates (lat, lon, radius)
    
    TEME (True Equator Mean Equinox) is the reference frame used by SGP4.
    """
    
    def __init__(self):
        """
        Initialize converter.
        """
        pass
    
    def eci_to_ecef(
        self,
        positions_eci: np.ndarray,
        times_jd: np.ndarray,
        epoch_jd: float
    ) -> np.ndarray:
        """
        Convert TEME (True Equator Mean Equinox) to ECEF (Earth-Centered Earth-Fixed).
        
        ECEF rotates with the Earth. The transformation is a rotation about the Z-axis
        by the Greenwich Mean Sidereal Time (GMST), which accounts for Earth's rotation
        and precession.
        
        Args:
            positions_eci: Position vectors in TEME frame [N, 3] in km
            times_jd: Julian dates [N, 2] where each row is [jd_whole, jd_frac]
            epoch_jd: Epoch Julian Date (reference time) - not used in GMST calculation
            
        Returns:
            Position vectors in ECEF frame [N, 3] in km
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
        
        # Build rotation matrices for each time point
        # R_z(GMST) to rotate from TEME to ECEF
        cos_gmst = np.cos(gmst_rad)
        sin_gmst = np.sin(gmst_rad)
        
        # Apply rotation: ECEF = R_z(GMST) @ TEME
        # [x_ecef]   [ cos(θ)  sin(θ)  0] [x_teme]
        # [y_ecef] = [-sin(θ)  cos(θ)  0] [y_teme]
        # [z_ecef]   [   0       0     1] [z_teme]
        
        x_teme = positions_eci[:, 0]
        y_teme = positions_eci[:, 1]
        z_teme = positions_eci[:, 2]
        
        x_ecef = cos_gmst * x_teme + sin_gmst * y_teme
        y_ecef = -sin_gmst * x_teme + cos_gmst * y_teme
        z_ecef = z_teme
        
        positions_ecef = np.column_stack([x_ecef, y_ecef, z_ecef])
        
        return positions_ecef
    
    def ecef_to_spherical(
        self,
        positions_ecef: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert ECEF Cartesian to Spherical coordinates.
        
        Spherical coordinates:
        - Latitude (φ): angle from equatorial plane, range [-90°, +90°]
        - Longitude (λ): angle from prime meridian, range [-180°, +180°]
        - Radial distance (r): distance from Earth center
        
        Args:
            positions_ecef: Position vectors in ECEF frame [N, 3] in km
            
        Returns:
            Tuple of (latitude, longitude, radial_distance)
            - latitude in radians [N]
            - longitude in radians [N]
            - radial_distance in km [N]
        """
        x = positions_ecef[:, 0]
        y = positions_ecef[:, 1]
        z = positions_ecef[:, 2]
        
        # Radial distance: r = sqrt(x² + y² + z²)
        radial_distance = np.sqrt(x**2 + y**2 + z**2)
        
        # Latitude: φ = arcsin(z / r)
        # Using arcsin for better numerical stability near poles
        latitude = np.arcsin(z / radial_distance)
        
        # Longitude: λ = arctan2(y, x)
        # arctan2 handles all quadrants correctly and returns [-π, π]
        longitude = np.arctan2(y, x)
        
        return latitude, longitude, radial_distance
    
    def convert(
        self,
        positions_eci: np.ndarray,
        times_jd: np.ndarray,
        epoch_jd: float
    ) -> CorotatingSphericalState:
        """
        Convert ECI Cartesian coordinates to Co-rotating Spherical coordinates.
        
        Complete transformation pipeline:
        1. ECI → ECEF (account for Earth rotation)
        2. ECEF Cartesian → Spherical (latitude, longitude, radius)
        
        Args:
            positions_eci: Position vectors in ECI frame [N, 3] in km
            times_jd: Julian dates [N, 2] where each row is [jd_whole, jd_frac]
            epoch_jd: Epoch Julian Date (reference time)
            
        Returns:
            CorotatingSphericalState with latitude, longitude, and radial distance
        """
        # Step 1: ECI to ECEF
        positions_ecef = self.eci_to_ecef(positions_eci, times_jd, epoch_jd)
        
        # Step 2: ECEF Cartesian to Spherical
        latitude, longitude, radial_distance = self.ecef_to_spherical(positions_ecef)
        
        return CorotatingSphericalState(
            latitude=latitude,
            longitude=longitude,
            radial_distance=radial_distance
        )


def main():
    """
    Main function to convert orbit to co-rotating spherical coordinates.
    """
    print("=" * 70)
    print("CARTESIAN TO CO-ROTATING SPHERICAL COORDINATE TRANSFORMATION")
    print("=" * 70)
    
    # Load orbit data
    print("\n1. Loading orbit propagation data...")
    data = np.load('data/orbit_propagation.npz', allow_pickle=True)
    
    positions = data['positions']  # km
    times_jd = data['times_jd']  # [N, 2] array of [jd_whole, jd_frac]
    satellite_name = str(data['satellite_name'])
    
    # Get epoch (first time point)
    epoch_jd = times_jd[0, 0] + times_jd[0, 1]
    
    print(f"   Satellite: {satellite_name}")
    print(f"   Number of points: {len(positions)}")
    print(f"   Epoch JD: {epoch_jd:.6f}")
    
    # Create converter
    print("\n2. Converting to co-rotating spherical coordinates...")
    converter = CorotatingConverter()
    corotating_state = converter.convert(positions, times_jd, epoch_jd)
    
    print(f"   {corotating_state}")
    
    # Convert to degrees for display
    lat_deg = np.rad2deg(corotating_state.latitude)
    lon_deg = np.rad2deg(corotating_state.longitude)
    
    # Display initial and final states
    print("\n3. Initial and final co-rotating states:")
    print(f"   Initial latitude:  {lat_deg[0]:>12.8f} deg")
    print(f"   Initial longitude: {lon_deg[0]:>12.8f} deg")
    print(f"   Initial radius:    {corotating_state.radial_distance[0]:>12.8f} km")
    print(f"   Final latitude:    {lat_deg[-1]:>12.8f} deg")
    print(f"   Final longitude:   {lon_deg[-1]:>12.8f} deg")
    print(f"   Final radius:      {corotating_state.radial_distance[-1]:>12.8f} km")
    
    # Statistics
    print("\n4. Statistics:")
    print(f"   Latitude range:  {lat_deg.min():.4f} to {lat_deg.max():.4f} deg")
    print(f"   Longitude range: {lon_deg.min():.4f} to {lon_deg.max():.4f} deg")
    print(f"   Radius range:    {corotating_state.radial_distance.min():.4f} to {corotating_state.radial_distance.max():.4f} km")
    
    # Save results
    output_file = 'data/corotating_spherical.npz'
    np.savez(
        output_file,
        latitude=corotating_state.latitude,
        longitude=corotating_state.longitude,
        radial_distance=corotating_state.radial_distance,
        times_jd=times_jd,
        satellite_name=satellite_name,
        epoch_jd=epoch_jd
    )
    
    print(f"\n5. Results saved to: {output_file}")
    print("   Load with: data = np.load('data/corotating_spherical.npz')")
    
    print("\n" + "=" * 70)
    print("TRANSFORMATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
