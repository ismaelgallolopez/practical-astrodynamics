#!/usr/bin/env python3
"""
Compare grid search and gradient descent optimization results
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def compare_optimization_methods():
    """
    Compare grid search vs gradient descent results
    """
    
    # Read grid search results
    grid_data = np.loadtxt('data/outputs_all/grid_search_results.txt', comments='#')
    dx_grid = grid_data[:, 0]
    dy_grid = grid_data[:, 1]
    cgpd_grid = grid_data[:, 2]
    
    # Reshape for contour plot
    n_points = int(np.sqrt(len(dx_grid)))
    DX = dx_grid.reshape(n_points, n_points)
    DY = dy_grid.reshape(n_points, n_points)
    CGPD = cgpd_grid.reshape(n_points, n_points)
    
    # Find grid search optimum
    min_idx = np.argmin(cgpd_grid)
    dx_grid_opt = dx_grid[min_idx]
    dy_grid_opt = dy_grid[min_idx]
    cgpd_grid_opt = cgpd_grid[min_idx]
    
    # Read gradient descent result
    grad_data = np.loadtxt('data/outputs_all/convergence_history.txt', comments='#')
    if grad_data.ndim == 1:
        grad_data = grad_data.reshape(1, -1)
    
    dx_grad_opt = grad_data[-1, 2]
    dy_grad_opt = grad_data[-1, 3]
    cgpd_grad_opt = grad_data[-1, 1]
    
    # Create comparison plot
    fig = plt.figure(figsize=(16, 6))
    
    # Plot 1: 2D contour map with both solutions
    ax1 = plt.subplot(131)
    levels = np.linspace(cgpd_grid.min(), cgpd_grid.min() + 5, 20)
    contour = ax1.contourf(DX, DY, CGPD, levels=levels, cmap='viridis')
    contour_lines = ax1.contour(DX, DY, CGPD, levels=levels, colors='white', 
                                  linewidths=0.5, alpha=0.3)
    
    # Mark optimal solutions
    ax1.plot(dx_grid_opt, dy_grid_opt, 'r*', markersize=20, 
             label=f'Grid Search: {cgpd_grid_opt:.3f} m', zorder=5)
    ax1.plot(dx_grad_opt, dy_grad_opt, 'bo', markersize=12, 
             label=f'Gradient Descent: {cgpd_grad_opt:.3f} m', zorder=5)
    ax1.plot(0, 0, 'gx', markersize=12, markeredgewidth=3,
             label='Initial (δ=0)', zorder=5)
    
    plt.colorbar(contour, ax=ax1, label='CGPD [m]')
    ax1.set_xlabel('δx [m]', fontweight='bold')
    ax1.set_ylabel('δy [m]', fontweight='bold')
    ax1.set_title('CGPD Landscape', fontweight='bold', fontsize=12)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Cross-section along dx
    ax2 = plt.subplot(132)
    center_idx = n_points // 2
    ax2.plot(DX[center_idx, :], CGPD[center_idx, :], 'b-', linewidth=2, 
             label='dy = 0')
    ax2.axvline(dx_grid_opt, color='red', linestyle='--', alpha=0.7,
                label=f'Grid optimum: {dx_grid_opt:.3f} m')
    ax2.axvline(dx_grad_opt, color='blue', linestyle='--', alpha=0.7,
                label=f'Gradient optimum: {dx_grad_opt:.6f} m')
    ax2.set_xlabel('δx [m]', fontweight='bold')
    ax2.set_ylabel('CGPD [m]', fontweight='bold')
    ax2.set_title('Cross-section at δy = 0', fontweight='bold', fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Method comparison table
    ax3 = plt.subplot(133)
    ax3.axis('off')
    
    comparison_text = f'''
    OPTIMIZATION METHOD COMPARISON
    {'='*50}
    
    GRID SEARCH:
      • Evaluations:      441
      • Best CGPD:        {cgpd_grid_opt:.6f} m
      • δx:               {dx_grid_opt:.6f} m
      • δy:               {dy_grid_opt:.6f} m
      • Resolution:       0.1 m
      • Advantage:        Guaranteed global optimum
      • Disadvantage:     Computationally expensive
    
    GRADIENT DESCENT:
      • Iterations:       {len(grad_data)}
      • Best CGPD:        {cgpd_grad_opt:.6f} m
      • δx:               {dx_grad_opt:.6f} m
      • δy:               {dy_grad_opt:.6f} m
      • Convergence:      {len(grad_data)} iterations
      • Advantage:        Very fast
      • Disadvantage:     May find local minimum
    
    COMPARISON:
      • CGPD difference:  {abs(cgpd_grid_opt - cgpd_grad_opt):.6f} m
      • Distance between
        solutions:        {np.sqrt((dx_grid_opt-dx_grad_opt)**2 + (dy_grid_opt-dy_grad_opt)**2):.6f} m
      • Speed ratio:      {441/len(grad_data):.0f}x faster (gradient)
    
    CONCLUSION:
      Both methods find very similar solutions!
      Gradient descent is {441/len(grad_data):.0f}x faster.
    '''
    
    ax3.text(0.1, 0.5, comparison_text, transform=ax3.transAxes,
             fontsize=10, verticalalignment='center', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    # Save figure
    output_file = 'plots/optimization/method_comparison.png'
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("OPTIMIZATION METHOD COMPARISON")
    print("="*70)
    print(f"\nGrid Search:")
    print(f"  Evaluations: 441")
    print(f"  Best CGPD:   {cgpd_grid_opt:.6f} m")
    print(f"  Optimal δx:  {dx_grid_opt:.6f} m")
    print(f"  Optimal δy:  {dy_grid_opt:.6f} m")
    print(f"\nGradient Descent:")
    print(f"  Iterations:  {len(grad_data)}")
    print(f"  Best CGPD:   {cgpd_grad_opt:.6f} m")
    print(f"  Optimal δx:  {dx_grad_opt:.6f} m")
    print(f"  Optimal δy:  {dy_grad_opt:.6f} m")
    print(f"\nDifference:")
    print(f"  CGPD diff:   {abs(cgpd_grid_opt - cgpd_grad_opt):.6f} m ({abs(cgpd_grid_opt - cgpd_grad_opt)/cgpd_grid_opt*100:.4f}%)")
    print(f"  Solution distance: {np.sqrt((dx_grid_opt-dx_grad_opt)**2 + (dy_grid_opt-dy_grad_opt)**2):.6f} m")
    print(f"  Speed advantage: Gradient descent is {441/len(grad_data):.0f}x faster")
    print("="*70 + "\n")
    
    plt.show()

if __name__ == '__main__':
    compare_optimization_methods()
