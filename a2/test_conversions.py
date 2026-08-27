#!/usr/bin/env python3
"""
Unit tests for orbital coordinate conversions.

Tests the Cartesian↔Keplerian conversions with various edge cases.
"""

import pytest
import numpy as np
from keplerian import OrbitPropagator
from back_cartesian import KeplerianToCartesianConverter


class TestCartesianToKeplerian:
    """Test suite for Cartesian to Keplerian conversion."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.propagator = OrbitPropagator()
        self.mu = 398600.4418  # km^3/s^2
    
    def test_circular_equatorial_orbit(self):
        """Test conversion for circular equatorial orbit."""
        # Circular orbit at 7000 km radius
        r = np.array([7000.0, 0.0, 0.0])
        v = np.array([0.0, np.sqrt(self.mu / 7000.0), 0.0])
        
        elements = self.propagator.cartesian_to_keplerian(r, v)
        
        assert abs(elements.semi_major_axis - 7000.0) < 1e-6
        assert elements.eccentricity < 1e-10
        assert elements.inclination < 1e-10
    
    def test_circular_polar_orbit(self):
        """Test conversion for circular polar orbit."""
        # Circular polar orbit at 7000 km
        r = np.array([7000.0, 0.0, 0.0])
        v = np.array([0.0, 0.0, np.sqrt(self.mu / 7000.0)])
        
        elements = self.propagator.cartesian_to_keplerian(r, v)
        
        assert abs(elements.semi_major_axis - 7000.0) < 1e-6
        assert elements.eccentricity < 1e-10
        assert abs(elements.inclination - np.pi/2) < 1e-10
    
    def test_highly_eccentric_orbit(self):
        """Test conversion for highly eccentric orbit."""
        # Elliptical orbit: a=10000 km, e=0.5
        a = 10000.0
        e = 0.5
        r_mag = a * (1 - e)  # At periapsis
        v_mag = np.sqrt(self.mu * (2/r_mag - 1/a))
        
        r = np.array([r_mag, 0.0, 0.0])
        v = np.array([0.0, v_mag, 0.0])
        
        elements = self.propagator.cartesian_to_keplerian(r, v)
        
        assert abs(elements.semi_major_axis - a) < 1e-6
        assert abs(elements.eccentricity - e) < 1e-10


class TestKeplerianToCartesian:
    """Test suite for Keplerian to Cartesian conversion."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = KeplerianToCartesianConverter()
        self.mu = 398600.4418  # km^3/s^2
    
    def test_circular_orbit_at_periapsis(self):
        """Test conversion at periapsis for circular orbit."""
        a = 7000.0
        e = 0.0
        i = 0.0
        omega = 0.0
        raan = 0.0
        nu = 0.0
        
        r, v = self.converter.keplerian_to_cartesian(a, e, i, raan, omega, nu)
        
        r_mag = np.linalg.norm(r)
        v_mag = np.linalg.norm(v)
        
        assert abs(r_mag - a) < 1e-6
        assert abs(v_mag - np.sqrt(self.mu / a)) < 1e-6
    
    def test_circular_orbit_at_90deg(self):
        """Test conversion at 90° true anomaly."""
        a = 7000.0
        e = 0.0
        i = 0.0
        omega = 0.0
        raan = 0.0
        nu = np.pi / 2
        
        r, v = self.converter.keplerian_to_cartesian(a, e, i, raan, omega, nu)
        
        r_mag = np.linalg.norm(r)
        assert abs(r_mag - a) < 1e-6


class TestRoundTrip:
    """Test round-trip conversions (Cartesian → Keplerian → Cartesian)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.propagator = OrbitPropagator()
        self.converter = KeplerianToCartesianConverter()
    
    def test_round_trip_circular(self):
        """Test round-trip for circular orbit."""
        r_orig = np.array([7000.0, 0.0, 0.0])
        v_orig = np.array([0.0, 7.546, 0.0])
        
        # Convert to Keplerian
        elements = self.propagator.cartesian_to_keplerian(r_orig, v_orig)
        
        # Convert back to Cartesian
        r_back, v_back = self.converter.keplerian_to_cartesian(
            elements.semi_major_axis,
            elements.eccentricity,
            elements.inclination,
            elements.raan,
            elements.argument_of_periapsis,
            elements.true_anomaly
        )
        
        # Check residuals
        r_diff = np.linalg.norm(r_orig - r_back)
        v_diff = np.linalg.norm(v_orig - v_back)
        
        assert r_diff < 1e-9  # nanometer precision
        assert v_diff < 1e-12  # picometer/s precision
    
    def test_round_trip_elliptical(self):
        """Test round-trip for elliptical orbit."""
        r_orig = np.array([10000.0, 5000.0, 2000.0])
        v_orig = np.array([-3.0, 6.0, 1.0])
        
        # Convert to Keplerian
        elements = self.propagator.cartesian_to_keplerian(r_orig, v_orig)
        
        # Convert back to Cartesian
        r_back, v_back = self.converter.keplerian_to_cartesian(
            elements.semi_major_axis,
            elements.eccentricity,
            elements.inclination,
            elements.raan,
            elements.argument_of_periapsis,
            elements.true_anomaly
        )
        
        # Check residuals
        r_diff = np.linalg.norm(r_orig - r_back)
        v_diff = np.linalg.norm(v_orig - v_back)
        
        assert r_diff < 1e-9
        assert v_diff < 1e-12
    
    def test_round_trip_inclined(self):
        """Test round-trip for inclined orbit."""
        r_orig = np.array([7000.0, 0.0, 3000.0])
        v_orig = np.array([0.0, 7.546, 2.0])
        
        # Convert to Keplerian
        elements = self.propagator.cartesian_to_keplerian(r_orig, v_orig)
        
        # Convert back to Cartesian
        r_back, v_back = self.converter.keplerian_to_cartesian(
            elements.semi_major_axis,
            elements.eccentricity,
            elements.inclination,
            elements.raan,
            elements.argument_of_periapsis,
            elements.true_anomaly
        )
        
        # Check residuals
        r_diff = np.linalg.norm(r_orig - r_back)
        v_diff = np.linalg.norm(v_orig - v_back)
        
        assert r_diff < 1e-9
        assert v_diff < 1e-12


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
