import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass
from sgp4.earth_gravity import wgs72


@dataclass
class KeplerianElements:
    """Container for classical Keplerian orbital elements."""
    semi_major_axis: np.ndarray  # a [km]
    eccentricity: np.ndarray  # e [-]
    inclination: np.ndarray  # i [rad]
    raan: np.ndarray  # Ω [rad] - Right Ascension of Ascending Node
    argument_of_periapsis: np.ndarray  # ω [rad]
    true_anomaly: np.ndarray  # θ [rad]
    
    def __repr__(self) -> str:
        n_points = len(self.semi_major_axis)
        return (f"KeplerianElements(n_points={n_points}, "
                f"a_mean={np.mean(self.semi_major_axis):.2f} km, "
                f"e_mean={np.mean(self.eccentricity):.6f})")


class OrbitPropagator:
    """
    Orbit propagator for computing Keplerian elements from Cartesian state vectors.
    
    Uses classical orbital mechanics formulations with robust numerical handling
    for edge cases including circular and equatorial orbits.
    """
    
    def __init__(self, mu: float = wgs72.mu, epsilon: float = 1e-10):
        """
        Initialize orbit propagator.
        
        Args:
            mu: Gravitational parameter [km^3/s^2]
            epsilon: Numerical tolerance for singularity handling
        """
        self.mu = mu
        self.epsilon = epsilon
        self.k_vector = np.array([0.0, 0.0, 1.0])  # Unit vector in z-direction
    
    def compute_specific_angular_momentum(
        self, 
        positions: np.ndarray, 
        velocities: np.ndarray
    ) -> np.ndarray:
        """
        Compute specific angular momentum vector: h = r × v
        
        Args:
            positions: Position vectors [N×3] in km
            velocities: Velocity vectors [N×3] in km/s
            
        Returns:
            Angular momentum vectors [N×3] in km^2/s
        """
        return np.cross(positions, velocities)
    
    def compute_eccentricity_vector(
        self,
        positions: np.ndarray,
        velocities: np.ndarray,
        angular_momentum: np.ndarray,
        radius: np.ndarray
    ) -> np.ndarray:
        """
        Compute eccentricity vector: e = (v × h) / μ - r̂
        
        The eccentricity vector points toward periapsis with magnitude equal
        to the orbital eccentricity.
        
        Args:
            positions: Position vectors [N×3] in km
            velocities: Velocity vectors [N×3] in km/s
            angular_momentum: Angular momentum vectors [N×3] in km^2/s
            radius: Position magnitudes [N] in km
            
        Returns:
            Eccentricity vectors [N×3]
        """
        # e = (1/μ)(v × h) - r̂
        velocity_cross_h = np.cross(velocities, angular_momentum)
        unit_position = positions / radius[:, np.newaxis]
        
        eccentricity_vector = (velocity_cross_h / self.mu) - unit_position
        return eccentricity_vector
    
    def compute_semi_major_axis(
        self,
        radius: np.ndarray,
        velocity_magnitude: np.ndarray
    ) -> np.ndarray:
        """
        Compute semi-major axis using vis-viva equation: a = 1 / (2/r - v²/μ)
        
        Args:
            radius: Position magnitudes [N] in km
            velocity_magnitude: Velocity magnitudes [N] in km/s
            
        Returns:
            Semi-major axis [N] in km
        """
        # Vis-viva equation: v² = μ(2/r - 1/a)
        # Rearranged: 1/a = 2/r - v²/μ
        specific_orbital_energy = (velocity_magnitude**2) / 2.0 - self.mu / radius
        
        # a = -μ / (2ε) where ε is specific orbital energy
        semi_major_axis = -self.mu / (2.0 * specific_orbital_energy)
        
        return semi_major_axis
    
    def compute_inclination(self, angular_momentum: np.ndarray) -> np.ndarray:
        """
        Compute orbital inclination: i = arccos(h_z / |h|)
        
        Args:
            angular_momentum: Angular momentum vectors [N×3] in km^2/s
            
        Returns:
            Inclination [N] in radians [0, π]
        """
        h_magnitude = np.linalg.norm(angular_momentum, axis=1)
        h_z = angular_momentum[:, 2]
        
        # Clamp to avoid numerical errors in arccos
        cos_inclination = np.clip(h_z / h_magnitude, -1.0, 1.0)
        inclination = np.arccos(cos_inclination)
        
        return inclination
    
    def compute_node_vector(self, angular_momentum: np.ndarray) -> np.ndarray:
        """
        Compute node vector: n = k̂ × h
        
        The node vector points toward the ascending node.
        
        Args:
            angular_momentum: Angular momentum vectors [N×3] in km^2/s
            
        Returns:
            Node vectors [N×3]
        """
        # For vectorized operation, broadcast k across all rows
        k_broadcast = np.tile(self.k_vector, (len(angular_momentum), 1))
        node_vector = np.cross(k_broadcast, angular_momentum)
        
        return node_vector
    
    def compute_raan(self, node_vector: np.ndarray) -> np.ndarray:
        """
        Compute Right Ascension of Ascending Node: Ω = arctan2(n_y, n_x)
        
        Args:
            node_vector: Node vectors [N×3]
            
        Returns:
            RAAN [N] in radians [0, 2π)
        """
        raan = np.arctan2(node_vector[:, 1], node_vector[:, 0])
        
        # Normalize to [0, 2π)
        raan = np.mod(raan, 2.0 * np.pi)
        
        return raan
    
    def compute_argument_of_periapsis(
        self,
        node_vector: np.ndarray,
        eccentricity_vector: np.ndarray,
        angular_momentum: np.ndarray
    ) -> np.ndarray:
        """
        Compute argument of periapsis: ω = arccos((n · e) / (|n||e|))
        
        Sign determined by (n × e) · h to handle full [0, 2π) range.
        
        Args:
            node_vector: Node vectors [N×3]
            eccentricity_vector: Eccentricity vectors [N×3]
            angular_momentum: Angular momentum vectors [N×3]
            
        Returns:
            Argument of periapsis [N] in radians [0, 2π)
        """
        n_magnitude = np.linalg.norm(node_vector, axis=1)
        e_magnitude = np.linalg.norm(eccentricity_vector, axis=1)
        
        # Dot product: n · e
        dot_product = np.einsum('ij,ij->i', node_vector, eccentricity_vector)
        
        # Avoid division by zero for circular or equatorial orbits
        denominator = n_magnitude * e_magnitude
        safe_denominator = np.where(denominator > self.epsilon, denominator, 1.0)
        
        cos_omega = np.clip(dot_product / safe_denominator, -1.0, 1.0)
        omega = np.arccos(cos_omega)
        
        # Determine sign using triple product: (n × e) · h
        cross_product = np.cross(node_vector, eccentricity_vector)
        sign_indicator = np.sign(np.einsum('ij,ij->i', cross_product, angular_momentum))
        
        # Apply sign and normalize to [0, 2π)
        omega = np.where(sign_indicator >= 0, omega, 2.0 * np.pi - omega)
        
        return omega
    
    def compute_true_anomaly(
        self,
        positions: np.ndarray,
        eccentricity_vector: np.ndarray,
        angular_momentum: np.ndarray,
        radius: np.ndarray
    ) -> np.ndarray:
        """
        Compute true anomaly: θ = arccos((e · r) / (|e||r|))
        
        Sign determined by (e × r) · h to handle full [0, 2π) range.
        
        Args:
            positions: Position vectors [N×3] in km
            eccentricity_vector: Eccentricity vectors [N×3]
            angular_momentum: Angular momentum vectors [N×3]
            radius: Position magnitudes [N] in km
            
        Returns:
            True anomaly [N] in radians [0, 2π)
        """
        e_magnitude = np.linalg.norm(eccentricity_vector, axis=1)
        
        # Dot product: e · r
        dot_product = np.einsum('ij,ij->i', eccentricity_vector, positions)
        
        # Avoid division by zero for circular orbits
        denominator = e_magnitude * radius
        safe_denominator = np.where(denominator > self.epsilon, denominator, 1.0)
        
        cos_theta = np.clip(dot_product / safe_denominator, -1.0, 1.0)
        theta = np.arccos(cos_theta)
        
        # Determine sign using triple product: (e × r) · h
        cross_product = np.cross(eccentricity_vector, positions)
        sign_indicator = np.sign(np.einsum('ij,ij->i', cross_product, angular_momentum))
        
        # Apply sign and normalize to [0, 2π)
        theta = np.where(sign_indicator >= 0, theta, 2.0 * np.pi - theta)
        
        return theta
    
    def cartesian_to_keplerian(
        self,
        positions: np.ndarray,
        velocities: np.ndarray
    ) -> KeplerianElements:
        """
        Convert Cartesian state vectors to Keplerian orbital elements.
        
        Args:
            positions: Position vectors [N×3] in km
            velocities: Velocity vectors [N×3] in km/s
            
        Returns:
            KeplerianElements containing all classical orbital elements
            
        Raises:
            ValueError: If input arrays have incompatible shapes
        """
        if positions.shape != velocities.shape:
            raise ValueError(
                f"Position and velocity arrays must have same shape. "
                f"Got {positions.shape} and {velocities.shape}"
            )
        
        if positions.ndim != 2 or positions.shape[1] != 3:
            raise ValueError(
                f"Expected Nx3 arrays, got shape {positions.shape}"
            )
        
        # Compute magnitudes
        radius = np.linalg.norm(positions, axis=1)
        velocity_magnitude = np.linalg.norm(velocities, axis=1)
        
        # Check for zero radius (collision)
        if np.any(radius < self.epsilon):
            raise ValueError("Detected position at or near origin (collision)")
        
        # Compute intermediate vectors
        angular_momentum = self.compute_specific_angular_momentum(positions, velocities)
        eccentricity_vector = self.compute_eccentricity_vector(
            positions, velocities, angular_momentum, radius
        )
        node_vector = self.compute_node_vector(angular_momentum)
        
        # Compute Keplerian elements
        semi_major_axis = self.compute_semi_major_axis(radius, velocity_magnitude)
        eccentricity = np.linalg.norm(eccentricity_vector, axis=1)
        inclination = self.compute_inclination(angular_momentum)
        raan = self.compute_raan(node_vector)
        argument_of_periapsis = self.compute_argument_of_periapsis(
            node_vector, eccentricity_vector, angular_momentum
        )
        true_anomaly = self.compute_true_anomaly(
            positions, eccentricity_vector, angular_momentum, radius
        )
        
        return KeplerianElements(
            semi_major_axis=semi_major_axis,
            eccentricity=eccentricity,
            inclination=inclination,
            raan=raan,
            argument_of_periapsis=argument_of_periapsis,
            true_anomaly=true_anomaly
        )


class OrbitDataLoader:
    """Utility class for loading and managing orbit propagation data."""
    
    @staticmethod
    def load_from_npz(filepath: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, str]:
        """
        Load orbit propagation data from NPZ file (SGP4 output).
        
        Args:
            filepath: Path to NPZ file containing orbit data
            
        Returns:
            Tuple of (times_jd, positions, velocities, satellite_name)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            KeyError: If required keys are missing
        """
        data = np.load(filepath)
        
        required_keys = ['times_jd', 'positions', 'velocities', 'satellite_name']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            raise KeyError(f"Missing required keys in data file: {missing_keys}")
        
        times_jd = data['times_jd']
        positions = data['positions']
        velocities = data['velocities']
        satellite_name = str(data['satellite_name'])
        
        return times_jd, positions, velocities, satellite_name
    
    @staticmethod
    def load_from_txt(filepath: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, str]:
        """
        Load orbit propagation data from text file (Euler integrator output).
        
        Expected format:
        # Header line (ignored)
        time[s] x[m] y[m] z[m] vx[m/s] vy[m/s] vz[m/s]
        ...
        
        Args:
            filepath: Path to text file containing orbit data
            
        Returns:
            Tuple of (times_seconds, positions_km, velocities_km_s, satellite_name)
        """
        # Load data, skipping header
        data = np.loadtxt(filepath, skiprows=1)
        
        times_seconds = data[:, 0]  # seconds
        positions_m = data[:, 1:4]  # meters
        velocities_m_s = data[:, 4:7]  # m/s
        
        # Convert to km and km/s for consistency with NPZ format
        positions_km = positions_m / 1000.0
        velocities_km_s = velocities_m_s / 1000.0
        
        satellite_name = "Euler Propagation"
        
        return times_seconds, positions_km, velocities_km_s, satellite_name
    
    @staticmethod
    def load_from_file(filepath: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, str]:
        """
        Load orbit propagation data from file (auto-detect format).
        
        Supports both NPZ (SGP4) and TXT (Euler) formats.
        
        Args:
            filepath: Path to data file
            
        Returns:
            Tuple of (times, positions, velocities, satellite_name)
            - For NPZ: times are Julian dates (N, 2)
            - For TXT: times are seconds from epoch (N,)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not recognized
        """
        if filepath.endswith('.npz'):
            return OrbitDataLoader.load_from_npz(filepath)
        elif filepath.endswith('.txt'):
            return OrbitDataLoader.load_from_txt(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath}. Use .npz or .txt")


def main():
    """Main execution function."""
    # Load data
    loader = OrbitDataLoader()
    times_jd, positions, velocities, sat_name = loader.load_from_file('data/orbit_propagation.npz')
    
    print(f"Satellite: {sat_name}")
    print(f"Number of points: {len(positions)}")
    
    # Initialize propagator and compute Keplerian elements
    propagator = OrbitPropagator()
    elements = propagator.cartesian_to_keplerian(positions, velocities)
    
    print(f"\n{elements}")
    
    # Get initial (first) and final (last) elements
    idx_initial = 0
    idx_final = -1
    
    # Extract initial and final values
    sma_initial_m = elements.semi_major_axis[idx_initial] * 1000  # Convert km to m
    sma_final_m = elements.semi_major_axis[idx_final] * 1000
    
    ecc_initial = elements.eccentricity[idx_initial]
    ecc_final = elements.eccentricity[idx_final]
    
    inc_initial_deg = np.rad2deg(elements.inclination[idx_initial])
    inc_final_deg = np.rad2deg(elements.inclination[idx_final])
    
    raan_initial_deg = np.rad2deg(elements.raan[idx_initial])
    raan_final_deg = np.rad2deg(elements.raan[idx_final])
    
    # True anomaly + argument of periapsis
    ta_aop_initial_deg = np.rad2deg(
        (elements.true_anomaly[idx_initial] + elements.argument_of_periapsis[idx_initial]) % (2 * np.pi)
    )
    ta_aop_final_deg = np.rad2deg(
        (elements.true_anomaly[idx_final] + elements.argument_of_periapsis[idx_final]) % (2 * np.pi)
    )
    
    # Print results in required format
    print("\n" + "=" * 70)
    print("INITIAL AND FINAL KEPLERIAN ELEMENTS")
    print("=" * 70)
    
    print(f"\nInitial and final semi-major axis in meters: lf_REG_OrbKepSMA_NUM_0.8")
    print(f"  Initial: {sma_initial_m:.8e} m")
    print(f"  Final:   {sma_final_m:.8e} m")
    
    print(f"\nInitial and final eccentricity (dimensionless): lf_REG_OrbKepEcc_NUM_0.8")
    print(f"  Initial: {ecc_initial:.8f}")
    print(f"  Final:   {ecc_final:.8f}")
    
    print(f"\nInitial and final inclination in degrees: lf_REG_OrbKepInc_NUM_0.8")
    print(f"  Initial: {inc_initial_deg:.8f} deg")
    print(f"  Final:   {inc_final_deg:.8f} deg")
    
    print(f"\nInitial and final right ascension of the ascending node in degrees: lf_REG_OrbKepRAAN_NUM_0.8")
    print(f"  Initial: {raan_initial_deg:.8f} deg")
    print(f"  Final:   {raan_final_deg:.8f} deg")
    
    print(f"\nInitial and final true anomaly plus argument of pericenter in degrees: lf_REG_OrbKepTApAoP_NUM_1.8")
    print(f"  Initial: {ta_aop_initial_deg:.8f} deg")
    print(f"  Final:   {ta_aop_final_deg:.8f} deg")
    
    print("\n" + "=" * 70)
    
    # Also print mean statistics for reference
    print(f"\nOrbital parameters (mean ± std):")
    print(f"  Semi-major axis: {np.mean(elements.semi_major_axis):.2f} ± {np.std(elements.semi_major_axis):.2f} km")
    print(f"  Eccentricity: {np.mean(elements.eccentricity):.6f} ± {np.std(elements.eccentricity):.6f}")
    print(f"  Inclination: {np.rad2deg(np.mean(elements.inclination)):.2f} ± {np.rad2deg(np.std(elements.inclination)):.2f} deg")
    print(f"  RAAN: {np.rad2deg(np.mean(elements.raan)):.2f} ± {np.rad2deg(np.std(elements.raan)):.2f} deg")
    print(f"  Arg. of periapsis: {np.rad2deg(np.mean(elements.argument_of_periapsis)):.2f} ± {np.rad2deg(np.std(elements.argument_of_periapsis)):.2f} deg")
    
    # Save Keplerian elements to file
    output_file = 'data/keplerian_elements.npz'
    np.savez(output_file,
             times_jd=times_jd,
             semi_major_axis=elements.semi_major_axis,
             eccentricity=elements.eccentricity,
             inclination=elements.inclination,
             raan=elements.raan,
             argument_of_periapsis=elements.argument_of_periapsis,
             true_anomaly=elements.true_anomaly,
             satellite_name=sat_name)
    
    print(f"\n8. Keplerian elements saved to: {output_file}")
    print(f"   Load with: data = np.load('{output_file}')")
    print(f"   Access arrays: data['semi_major_axis'], data['eccentricity'], etc.")


if __name__ == "__main__":
    main()