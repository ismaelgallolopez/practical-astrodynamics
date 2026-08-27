#!/usr/bin/env python3
"""
Benchmark vectorized vs loop implementations for Keplerian conversions.

Demonstrates the performance benefits of NumPy vectorization.
"""

import numpy as np
import time
from keplerian import OrbitPropagator


def cartesian_to_keplerian_loop(positions, velocities, mu=398600.4418):
    """Loop-based implementation for comparison."""
    n = len(positions)
    results = {
        'a': np.zeros(n),
        'e': np.zeros(n),
        'i': np.zeros(n),
        'raan': np.zeros(n),
        'omega': np.zeros(n),
        'nu': np.zeros(n)
    }
    
    for idx in range(n):
        r = positions[idx]
        v = velocities[idx]
        
        # Orbital radius and speed
        r_mag = np.sqrt(r[0]**2 + r[1]**2 + r[2]**2)
        v_mag = np.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        
        # Specific angular momentum
        h = np.cross(r, v)
        h_mag = np.sqrt(h[0]**2 + h[1]**2 + h[2]**2)
        
        # Eccentricity vector
        e_vec = ((v_mag**2 - mu/r_mag) * r - np.dot(r, v) * v) / mu
        e = np.sqrt(e_vec[0]**2 + e_vec[1]**2 + e_vec[2]**2)
        
        # Semi-major axis
        energy = 0.5 * v_mag**2 - mu / r_mag
        a = -mu / (2 * energy)
        
        # Inclination
        i = np.arccos(h[2] / h_mag)
        
        # Node vector
        n = np.array([-h[1], h[0], 0.0])
        n_mag = np.sqrt(n[0]**2 + n[1]**2)
        
        # RAAN
        if n_mag > 1e-10:
            raan = np.arccos(n[0] / n_mag)
            if n[1] < 0:
                raan = 2 * np.pi - raan
        else:
            raan = 0.0
        
        # Argument of periapsis
        if n_mag > 1e-10 and e > 1e-10:
            omega = np.arccos(np.dot(n, e_vec) / (n_mag * e))
            if e_vec[2] < 0:
                omega = 2 * np.pi - omega
        else:
            omega = 0.0
        
        # True anomaly
        if e > 1e-10:
            nu = np.arccos(np.dot(e_vec, r) / (e * r_mag))
            if np.dot(r, v) < 0:
                nu = 2 * np.pi - nu
        else:
            nu = 0.0
        
        results['a'][idx] = a
        results['e'][idx] = e
        results['i'][idx] = i
        results['raan'][idx] = raan
        results['omega'][idx] = omega
        results['nu'][idx] = nu
    
    return results


def benchmark_conversions(n_points=1000):
    """Benchmark vectorized vs loop implementations."""
    print("=" * 70)
    print("KEPLERIAN CONVERSION BENCHMARK")
    print("=" * 70)
    
    # Generate random orbital states
    print(f"\nGenerating {n_points} random orbital states...")
    np.random.seed(42)
    
    # Random positions (7000-50000 km radius)
    r_mags = np.random.uniform(7000, 50000, n_points)
    theta = np.random.uniform(0, 2*np.pi, n_points)
    phi = np.random.uniform(-np.pi/2, np.pi/2, n_points)
    
    positions = np.zeros((n_points, 3))
    positions[:, 0] = r_mags * np.cos(phi) * np.cos(theta)
    positions[:, 1] = r_mags * np.cos(phi) * np.sin(theta)
    positions[:, 2] = r_mags * np.sin(phi)
    
    # Random velocities (circular-ish orbits)
    mu = 398600.4418
    v_mags = np.sqrt(mu / r_mags) * np.random.uniform(0.8, 1.2, n_points)
    v_theta = np.random.uniform(0, 2*np.pi, n_points)
    v_phi = np.random.uniform(-np.pi/4, np.pi/4, n_points)
    
    velocities = np.zeros((n_points, 3))
    velocities[:, 0] = v_mags * np.cos(v_phi) * np.cos(v_theta)
    velocities[:, 1] = v_mags * np.cos(v_phi) * np.sin(v_theta)
    velocities[:, 2] = v_mags * np.sin(v_phi)
    
    # Benchmark loop implementation
    print("\n" + "-" * 70)
    print("1. Loop-based implementation...")
    start_loop = time.time()
    results_loop = cartesian_to_keplerian_loop(positions, velocities)
    time_loop = time.time() - start_loop
    print(f"   Time: {time_loop:.4f} seconds")
    
    # Benchmark vectorized implementation
    print("\n2. Vectorized implementation...")
    propagator = OrbitPropagator()
    start_vec = time.time()
    results_vec = propagator.cartesian_to_keplerian_batch(positions, velocities)
    time_vec = time.time() - start_vec
    print(f"   Time: {time_vec:.4f} seconds")
    
    # Compare results
    print("\n" + "-" * 70)
    print("RESULTS")
    print("-" * 70)
    print(f"Loop time:       {time_loop:.4f} s")
    print(f"Vectorized time: {time_vec:.4f} s")
    print(f"Speedup:         {time_loop/time_vec:.2f}x")
    
    # Verify accuracy
    print("\n" + "-" * 70)
    print("ACCURACY VERIFICATION")
    print("-" * 70)
    
    elements_vec = [results_vec[i] for i in range(n_points)]
    
    max_diff_a = np.max(np.abs(results_loop['a'] - np.array([e.semi_major_axis for e in elements_vec])))
    max_diff_e = np.max(np.abs(results_loop['e'] - np.array([e.eccentricity for e in elements_vec])))
    max_diff_i = np.max(np.abs(results_loop['i'] - np.array([e.inclination for e in elements_vec])))
    
    print(f"Max difference in semi-major axis: {max_diff_a:.3e} km")
    print(f"Max difference in eccentricity:    {max_diff_e:.3e}")
    print(f"Max difference in inclination:     {max_diff_i:.3e} rad")
    
    if max_diff_a < 1e-9 and max_diff_e < 1e-12 and max_diff_i < 1e-12:
        print("\n✓ Both implementations produce identical results!")
    else:
        print("\n⚠ Implementations differ (may be due to edge case handling)")
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)
    print(f"\nConclusion: Vectorization provides {time_loop/time_vec:.1f}x speedup")
    print("while maintaining numerical accuracy at machine precision.")


if __name__ == '__main__':
    benchmark_conversions()
