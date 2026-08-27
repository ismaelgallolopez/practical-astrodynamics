#!/usr/bin/env python3
"""
Plot optimization convergence history showing CGPD vs iteration
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_optimization_convergence(history_file='data/outputs_all/convergence_history.txt', 
                                   output_file='plots/optimization/convergence.png'):
    """
    Plot CGPD as a function of optimization iteration
    
    Parameters:
    -----------
    history_file : str
        Path to convergence history file
    output_file : str
        Path to save the plot
    """
    
    # Read convergence history
    data = np.loadtxt(history_file, comments='#')
    
    # Extract iteration and CGPD columns
    if data.ndim == 1:  # Single iteration case
        data = data.reshape(1, -1)
    
    iterations = data[:, 0].astype(int)
    cgpd = data[:, 1]  # CGPD in meters
    
    # Calculate reduction
    initial_cgpd = cgpd[0]
    final_cgpd = cgpd[-1]
    best_cgpd = cgpd.min()
    best_iter = iterations[np.argmin(cgpd)]
    improvement = initial_cgpd - best_cgpd
    percent_reduction = (improvement / initial_cgpd) * 100
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Plot CGPD vs iteration
    plt.plot(iterations, cgpd, 'o-', linewidth=2, markersize=6, 
             color='#2E86AB', alpha=0.7, label='CGPD trajectory')
    
    # Mark initial point
    plt.plot(iterations[0], cgpd[0], 'go', markersize=12, 
             label=f'Initial: {cgpd[0]:.2f} m', zorder=5)
    
    # Mark best point (this is what the algorithm returns)
    plt.plot(best_iter, best_cgpd, 'r*', markersize=18, 
             label=f'Best: {best_cgpd:.2f} m (iter {best_iter})', zorder=6)
    
    # If last iteration is not the best, mark it differently
    if best_iter != iterations[-1]:
        plt.plot(iterations[-1], cgpd[-1], 'x', markersize=12, 
                 color='orange', label=f'Last iter: {cgpd[-1]:.2f} m', zorder=5)
    
    # Add horizontal line at initial value for reference
    plt.axhline(y=initial_cgpd, color='gray', linestyle='--', 
                alpha=0.5, linewidth=1)
    
    # Labels and title
    plt.xlabel('Iteration', fontsize=12, fontweight='bold')
    plt.ylabel('CGPD [m]', fontsize=12, fontweight='bold')
    plt.title(f'Optimization Convergence\nBest improvement: {improvement:.3f} m ({percent_reduction:.2f}%)', 
              fontsize=14, fontweight='bold')
    
    # Grid
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Legend
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), 
               fontsize=10, framealpha=0.95, edgecolor='gray')
    
    # Tight layout
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    # Save figure
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    
    # Display summary
    print("\n" + "="*60)
    print("Optimization Summary")
    print("="*60)
    print(f"Total iterations:     {len(iterations)}")
    print(f"Initial CGPD:         {initial_cgpd:.6f} m")
    print(f"Best CGPD:            {best_cgpd:.6f} m (iteration {best_iter})")
    print(f"Last CGPD:            {final_cgpd:.6f} m (iteration {iterations[-1]})")
    print(f"Improvement:          {improvement:.6f} m")
    print(f"Percent reduction:    {percent_reduction:.6f} %")
    print("="*60)
    
    # Show plot
    plt.show()


if __name__ == '__main__':
    import sys
    
    # Allow custom file paths from command line
    if len(sys.argv) > 1:
        history_file = sys.argv[1]
    else:
        history_file = 'data/outputs_all/convergence_history.txt'
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = 'plots/optimization/convergence.png'
    
    plot_optimization_convergence(history_file, output_file)
