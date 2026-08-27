#!/usr/bin/env python3
"""
Analyze and visualize optimization robustness test results
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_robustness_test(results_file='data/outputs_all/robustness_test.txt',
                            output_file='plots/robustness/analysis.png'):
    """
    Analyze and plot robustness test results
    """
    
    # Read data manually to handle overflow values
    test_id = []
    initial_cgpd = []
    optimized_cgpd = []
    improvement = []
    iterations = []
    converged = []
    optimal_pert_pos = []
    optimal_pert_vel = []
    
    with open(results_file, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            
            parts = line.split()
            if '****' in line:  # Skip overflow lines
                continue
                
            test_id.append(int(parts[0]))
            initial_cgpd.append(float(parts[1]))
            optimized_cgpd.append(float(parts[2]))
            improvement.append(float(parts[3]))
            iterations.append(int(parts[4]))
            converged.append(parts[5] == 'T')
            optimal_pert_pos.append([float(parts[12]), float(parts[13]), float(parts[14])])
            optimal_pert_vel.append([float(parts[15]), float(parts[16]), float(parts[17])])
    
    # Convert to arrays
    test_id = np.array(test_id)
    initial_cgpd = np.array(initial_cgpd)
    optimized_cgpd = np.array(optimized_cgpd)
    improvement = np.array(improvement)
    iterations = np.array(iterations)
    converged = np.array(converged)
    optimal_pert_pos = np.array(optimal_pert_pos)
    optimal_pert_vel = np.array(optimal_pert_vel)
    
    # Calculate magnitudes
    optimal_pert_pos_mag = np.linalg.norm(optimal_pert_pos, axis=1)
    optimal_pert_vel_mag = np.linalg.norm(optimal_pert_vel, axis=1)
    
    print(f"\nProcessed {len(test_id)} tests successfully\n")
    
    # Statistics
    print("\n" + "="*70)
    print("ROBUSTNESS TEST ANALYSIS")
    print("="*70)
    print(f"Total tests: {len(test_id)}")
    print(f"All converged: {np.all(converged)}")
    print(f"Iterations: {iterations[0]} (all tests)")
    print()
    print(f"Initial CGPD:")
    print(f"  Mean:   {np.mean(initial_cgpd):12.3f} m")
    print(f"  Std:    {np.std(initial_cgpd):12.3f} m")
    print(f"  Min:    {np.min(initial_cgpd):12.3f} m")
    print(f"  Max:    {np.max(initial_cgpd):12.3f} m")
    print()
    print(f"Optimized CGPD:")
    print(f"  Mean:   {np.mean(optimized_cgpd):12.3f} m")
    print(f"  Std:    {np.std(optimized_cgpd):12.3f} m")
    print(f"  Min:    {np.min(optimized_cgpd):12.3f} m")
    print(f"  Max:    {np.max(optimized_cgpd):12.3f} m")
    print()
    print(f"Improvement:")
    print(f"  Mean:   {np.mean(improvement):12.6f} m")
    print(f"  Std:    {np.std(improvement):12.6f} m")
    print(f"  Min:    {np.min(improvement):12.6f} m")
    print(f"  Max:    {np.max(improvement):12.6f} m")
    print()
    print(f"Optimal Solution Consistency:")
    print(f"  Position magnitude std: {np.std(optimal_pert_pos_mag):.6e} m")
    print(f"  Velocity magnitude std: {np.std(optimal_pert_vel_mag):.6e} m/s")
    print(f"  Optimized CGPD std:     {np.std(optimized_cgpd):.6e} m")
    print("="*70 + "\n")
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: CGPD comparison
    ax = axes[0, 0]
    x = np.arange(len(test_id))
    width = 0.35
    ax.bar(x - width/2, initial_cgpd, width, label='Initial CGPD', alpha=0.8, color='#E63946')
    ax.bar(x + width/2, optimized_cgpd, width, label='Optimized CGPD', alpha=0.8, color='#2A9D8F')
    ax.set_xlabel('Test ID', fontweight='bold')
    ax.set_ylabel('CGPD [m]', fontweight='bold')
    ax.set_title('Initial vs Optimized CGPD for Each Test', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(test_id)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Improvement
    ax = axes[0, 1]
    ax.bar(test_id, improvement, alpha=0.8, color='#F4A261')
    ax.axhline(y=np.mean(improvement), color='red', linestyle='--', 
               label=f'Mean: {np.mean(improvement):.3f} m', linewidth=2)
    ax.set_xlabel('Test ID', fontweight='bold')
    ax.set_ylabel('Improvement [m]', fontweight='bold')
    ax.set_title('CGPD Improvement per Test', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Optimized CGPD consistency
    ax = axes[1, 0]
    ax.scatter(test_id, optimized_cgpd, s=100, alpha=0.7, color='#2E86AB')
    ax.axhline(y=np.mean(optimized_cgpd), color='red', linestyle='--', 
               label=f'Mean: {np.mean(optimized_cgpd):.3f} m', linewidth=2)
    ax.fill_between(ax.get_xlim(), 
                     np.mean(optimized_cgpd) - np.std(optimized_cgpd),
                     np.mean(optimized_cgpd) + np.std(optimized_cgpd),
                     alpha=0.2, color='red', label=f'±1σ: {np.std(optimized_cgpd):.3e} m')
    ax.set_xlabel('Test ID', fontweight='bold')
    ax.set_ylabel('Optimized CGPD [m]', fontweight='bold')
    ax.set_title('Optimization Consistency', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Convergence to same solution
    ax = axes[1, 1]
    # Show that all tests converge to similar optimal perturbations
    ax.scatter(optimal_pert_pos[:, 0]*1e3, optimal_pert_pos[:, 1]*1e3, s=100, alpha=0.7, 
               label='Optimal δx vs δy', color='#2A9D8F')
    ax.scatter(np.mean(optimal_pert_pos[:, 0])*1e3, np.mean(optimal_pert_pos[:, 1])*1e3, 
               s=300, marker='*', color='red', edgecolor='black', linewidth=2,
               label='Mean', zorder=5)
    ax.set_xlabel('Optimal δx [mm]', fontweight='bold')
    ax.set_ylabel('Optimal δy [mm]', fontweight='bold')
    ax.set_title('Optimal Solution Clustering', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    
    plt.show()

if __name__ == '__main__':
    analyze_robustness_test()
