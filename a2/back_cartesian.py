#!/usr/bin/env python3
"""
Keplerian to Cartesian Coordinate Transformation.

Converts orbital elements (Keplerian coordinates) back to Cartesian state vectors
(position and velocity) using classical orbital mechanics transformations.
"""

import numpy as np
from typing import Tuple
from dataclasses import dataclass
from sgp4.earth_gravity import wgs72


@dataclass
class CartesianState:
    """Container for Cartesian state vectors."""
    positions: np.ndarray  # [N×3] in km
    velocities: np.ndarray  # [N×3] in km/s
    times_jd: np.ndarray  # [N×2] Julian dates
    
    def __repr__(self) -> str:
        n_points = len(self.positions)
        return (f"CartesianState(n_points={n_points}, "
                f"r_mean={np.mean(np.linalg.norm(self.positions, axis=1)):.2f} km, "
                f"v_mean={np.mean(np.linalg.norm(self.velocities, axis=1)):.6f} km/s)")


class KeplerianToCartesianConverter:
    """
    Converter for transforming Keplerian orbital elements to Cartesian coordinates.
    
    Uses classical orbital mechanics formulations with perifocal coordinate system
    and rotation matrices for the transformation.
    """
    
    def __init__(self, mu: float = wgs72.mu):
        """
        Initialize converter.
        
        Args:
            mu: Gravitational parameter [km^3/s^2]
        """
        self.mu = mu
    
    def compute_orbital_radius(
        self,
        semi_major_axis: np.ndarray,
        eccentricity: np.ndarray,
        true_anomaly: np.ndarray
    ) -> np.ndarray:
        """
        Compute orbital radius using the orbit equation.
        
        r = a(1 - e²) / (1 + e·cos(θ))
        
        Args:
            semi_major_axis: Semi-major axis [N] in km
            eccentricity: Eccentricity [N] dimensionless
            true_anomaly: True anomaly [N] in radians
            
        Returns:
            Orbital radius [N] in km
        """
        numerator = semi_major_axis * (1.0 - eccentricity**2)
        denominator = 1.0 + eccentricity * np.cos(true_anomaly)
        
        return numerator / denominator
    
    def compute_perifocal_coordinates(
        self,
        radius: np.ndarray,
        true_anomaly: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute position in perifocal coordinate system.
        
        Perifocal frame: x-axis points to periapsis, z-axis along angular momentum
        
        Args:
            radius: Orbital radius [N] in km
            true_anomaly: True anomaly [N] in radians
            
        Returns:
            Tuple of (xi, eta) coordinates in perifocal frame [N]
        """
        xi = radius * np.cos(true_anomaly)
        eta = radius * np.sin(true_anomaly)
        
        return xi, eta
    
    def compute_rotation_matrix(
        self,
        raan: np.ndarray,
        argument_of_periapsis: np.ndarray,
        inclination: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute rotation matrix elements from perifocal to inertial frame.
        
        Rotation sequence: Rz(Ω) · Rx(i) · Rz(ω)
        
        Matrix structure:
        [l1  l2  0] [x_perifocal]   [x_inertial]
        [m1  m2  0] [y_perifocal] = [y_inertial]
        [n1  n2  0] [z_perifocal]   [z_inertial]
        
        Args:
            raan: Right Ascension of Ascending Node [N] in radians
            argument_of_periapsis: Argument of periapsis [N] in radians
            inclination: Inclination [N] in radians
            
        Returns:
            Tuple of (l1, l2, m1, m2, n1, n2) rotation matrix elements
        """
        # Precompute trigonometric functions
        cos_omega = np.cos(argument_of_periapsis)
        sin_omega = np.sin(argument_of_periapsis)
        cos_raan = np.cos(raan)
        sin_raan = np.sin(raan)
        cos_inc = np.cos(inclination)
        sin_inc = np.sin(inclination)
        
        # First row of rotation matrix
        l1 = cos_raan * cos_omega - sin_raan * sin_omega * cos_inc
        l2 = -cos_raan * sin_omega - sin_raan * cos_omega * cos_inc
        
        # Second row of rotation matrix
        m1 = sin_raan * cos_omega + cos_raan * sin_omega * cos_inc
        m2 = -sin_raan * sin_omega + cos_raan * cos_omega * cos_inc
        
        # Third row of rotation matrix
        n1 = sin_omega * sin_inc
        n2 = cos_omega * sin_inc
        
        return l1, l2, m1, m2, n1, n2
    
    def compute_specific_angular_momentum_magnitude(
        self,
        semi_major_axis: np.ndarray,
        eccentricity: np.ndarray
    ) -> np.ndarray:
        """
        Compute magnitude of specific angular momentum.
        
        H = √[μ·a·(1 - e²)]
        
        Args:
            semi_major_axis: Semi-major axis [N] in km
            eccentricity: Eccentricity [N] dimensionless
            
        Returns:
            Specific angular momentum magnitude [N] in km²/s
        """
        return np.sqrt(self.mu * semi_major_axis * (1.0 - eccentricity**2))
    
    def compute_inertial_position(
        self,
        xi: np.ndarray,
        eta: np.ndarray,
        l1: np.ndarray,
        l2: np.ndarray,
        m1: np.ndarray,
        m2: np.ndarray,
        n1: np.ndarray,
        n2: np.ndarray
    ) -> np.ndarray:
        """
        Transform perifocal coordinates to inertial frame position.
        
        Args:
            xi: Perifocal x-coordinate [N] in km
            eta: Perifocal y-coordinate [N] in km
            l1, l2, m1, m2, n1, n2: Rotation matrix elements [N]
            
        Returns:
            Position vectors [N×3] in inertial frame in km
        """
        x = l1 * xi + l2 * eta
        y = m1 * xi + m2 * eta
        z = n1 * xi + n2 * eta
        
        return np.column_stack([x, y, z])
    
    def compute_inertial_velocity(
        self,
        true_anomaly: np.ndarray,
        eccentricity: np.ndarray,
        H: np.ndarray,
        l1: np.ndarray,
        l2: np.ndarray,
        m1: np.ndarray,
        m2: np.ndarray,
        n1: np.ndarray,
        n2: np.ndarray
    ) -> np.ndarray:
        """
        Compute velocity in inertial frame using angular momentum.
        
        v = (μ/H) · [-sin(θ)·r̂_perifocal + (e + cos(θ))·t̂_perifocal]
        
        Args:
            true_anomaly: True anomaly [N] in radians
            eccentricity: Eccentricity [N] dimensionless
            H: Specific angular momentum magnitude [N] in km²/s
            l1, l2, m1, m2, n1, n2: Rotation matrix elements [N]
            
        Returns:
            Velocity vectors [N×3] in inertial frame in km/s
        """
        sin_theta = np.sin(true_anomaly)
        cos_theta = np.cos(true_anomaly)
        
        # Velocity components in perifocal frame transformed to inertial
        mu_over_H = self.mu / H
        
        x_dot = mu_over_H * (-l1 * sin_theta + l2 * (eccentricity + cos_theta))
        y_dot = mu_over_H * (-m1 * sin_theta + m2 * (eccentricity + cos_theta))
        z_dot = mu_over_H * (-n1 * sin_theta + n2 * (eccentricity + cos_theta))
        
        return np.column_stack([x_dot, y_dot, z_dot])
    
    def keplerian_to_cartesian(
        self,
        times_jd: np.ndarray,
        semi_major_axis: np.ndarray,
        eccentricity: np.ndarray,
        inclination: np.ndarray,
        raan: np.ndarray,
        argument_of_periapsis: np.ndarray,
        true_anomaly: np.ndarray
    ) -> CartesianState:
        """
        Convert Keplerian orbital elements to Cartesian state vectors.
        
        Args:
            times_jd: Julian dates [N×2]
            semi_major_axis: Semi-major axis [N] in km
            eccentricity: Eccentricity [N] dimensionless
            inclination: Inclination [N] in radians
            raan: Right Ascension of Ascending Node [N] in radians
            argument_of_periapsis: Argument of periapsis [N] in radians
            true_anomaly: True anomaly [N] in radians
            
        Returns:
            CartesianState containing positions and velocities
        """
        # Step 1: Compute orbital radius
        radius = self.compute_orbital_radius(semi_major_axis, eccentricity, true_anomaly)
        
        # Step 2: Compute perifocal coordinates
        xi, eta = self.compute_perifocal_coordinates(radius, true_anomaly)
        
        # Step 3: Compute rotation matrix
        l1, l2, m1, m2, n1, n2 = self.compute_rotation_matrix(
            raan, argument_of_periapsis, inclination
        )
        
        # Step 4: Transform position to inertial frame
        positions = self.compute_inertial_position(xi, eta, l1, l2, m1, m2, n1, n2)
        
        # Step 5: Compute specific angular momentum magnitude
        H = self.compute_specific_angular_momentum_magnitude(semi_major_axis, eccentricity)
        
        # Step 6: Compute velocity in inertial frame
        velocities = self.compute_inertial_velocity(
            true_anomaly, eccentricity, H, l1, l2, m1, m2, n1, n2
        )
        
        return CartesianState(
            positions=positions,
            velocities=velocities,
            times_jd=times_jd
        )


def load_keplerian_elements(filepath: str = 'data/keplerian_elements.npz') -> Tuple:
    """
    Load Keplerian elements from NPZ file.
    
    Args:
        filepath: Path to NPZ file
        
    Returns:
        Tuple of all Keplerian elements and metadata
    """
    data = np.load(filepath)
    
    return (
        data['times_jd'],
        data['semi_major_axis'],
        data['eccentricity'],
        data['inclination'],
        data['raan'],
        data['argument_of_periapsis'],
        data['true_anomaly'],
        str(data['satellite_name'])
    )


def main():
    """Main execution function."""
    print("=" * 70)
    print("KEPLERIAN TO CARTESIAN COORDINATE TRANSFORMATION")
    print("=" * 70)
    
    # Load Keplerian elements
    print("\n1. Loading Keplerian elements...")
    (times_jd, semi_major_axis, eccentricity, inclination,
     raan, argument_of_periapsis, true_anomaly, sat_name) = load_keplerian_elements()
    
    print(f"   Satellite: {sat_name}")
    print(f"   Number of points: {len(semi_major_axis)}")
    
    # Initialize converter
    converter = KeplerianToCartesianConverter()
    
    # Convert to Cartesian coordinates
    print("\n2. Converting to Cartesian coordinates...")
    cartesian_state = converter.keplerian_to_cartesian(
        times_jd=times_jd,
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=inclination,
        raan=raan,
        argument_of_periapsis=argument_of_periapsis,
        true_anomaly=true_anomaly
    )
    
    print(f"   {cartesian_state}")
    
    # Display sample results
    print("\n3. Sample Cartesian state vectors (first 3 points):")
    for i in range(min(3, len(cartesian_state.positions))):
        r = cartesian_state.positions[i]
        v = cartesian_state.velocities[i]
        print(f"   [{i}] Position: [{r[0]:12.6f}, {r[1]:12.6f}, {r[2]:12.6f}] km")
        print(f"       Velocity: [{v[0]:12.6f}, {v[1]:12.6f}, {v[2]:12.6f}] km/s")
    
    # Compute statistics
    radii = np.linalg.norm(cartesian_state.positions, axis=1)
    speeds = np.linalg.norm(cartesian_state.velocities, axis=1)
    
    print("\n4. Statistics:")
    print(f"   Radius range:  {radii.min():.3f} to {radii.max():.3f} km")
    print(f"   Speed range:   {speeds.min():.6f} to {speeds.max():.6f} km/s")
    print(f"   Mean radius:   {radii.mean():.3f} km")
    print(f"   Mean speed:    {speeds.mean():.6f} km/s")
    
    # Save results
    output_file = 'data/cartesian_from_keplerian.npz'
    np.savez(output_file,
             times_jd=times_jd,
             positions=cartesian_state.positions,
             velocities=cartesian_state.velocities,
             satellite_name=sat_name)
    
    print(f"\n5. Results saved to: {output_file}")
    print(f"   Load with: data = np.load('{output_file}')")
    
    print("\n" + "=" * 70)
    print("TRANSFORMATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
