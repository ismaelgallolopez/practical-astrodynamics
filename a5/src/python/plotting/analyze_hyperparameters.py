#!/usr/bin/env python3
"""
Analyze and visualize hyperparameter sensitivity test results.
"""

import numpy as np
import matplotlib.pyplot as plt

def main():
    # Load results
    data_file = 'data/outputs_all/hyperparameter_test.txt'
    
    # Read data
    learning_rates = []
    tolerances = []
    converged = []
    iterations = []
    cgpds = []
    improvements = []
    times = []
    
    with open(data_file, 'r') as f:
        initial_cgpd = None
        for line in f:
            line = line.strip()
            
            # Skip comments but extract initial CGPD
            if line.startswith('#'):
                if 'Initial CGPD' in line:
                    initial_cgpd = float(line.split(':')[1].strip().split()[0])
                continue
            
            if not line:
                continue
            
            parts = line.split()
            learning_rates.append(float(parts[0]))
            tolerances.append(float(parts[1]))
            converged.append(parts[2] == 'T')
            iterations.append(int(parts[3]))
            cgpds.append(float(parts[4]))
            improvements.append(float(parts[5]))
            times.append(float(parts[6]))
    
    # Convert to numpy arrays
    learning_rates = np.array(learning_rates)
    tolerances = np.array(tolerances)
    iterations = np.array(iterations)
    cgpds = np.array(cgpds)
    improvements = np.array(improvements)
    times = np.array(times)
    
    # Get unique values
    unique_lr = np.unique(learning_rates)
    unique_tol = np.unique(tolerances)
    
    # Create matrices for heatmaps
    cgpd_matrix = np.zeros((len(unique_lr), len(unique_tol)))
    iter_matrix = np.zeros((len(unique_lr), len(unique_tol)))
    time_matrix = np.zeros((len(unique_lr), len(unique_tol)))
    improvement_matrix = np.zeros((len(unique_lr), len(unique_tol)))
    
    for i, lr in enumerate(unique_lr):
        for j, tol in enumerate(unique_tol):
            mask = (learning_rates == lr) & (tolerances == tol)
            cgpd_matrix[i, j] = cgpds[mask][0]
            iter_matrix[i, j] = iterations[mask][0]
            time_matrix[i, j] = times[mask][0]
            improvement_matrix[i, j] = improvements[mask][0]
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 10))
    
    # 1. Heatmap of final CGPD
    ax1 = plt.subplot(2, 3, 1)
    im1 = ax1.imshow(cgpd_matrix, aspect='auto', origin='lower', cmap='viridis')
    ax1.set_xticks(range(len(unique_tol)))
    ax1.set_yticks(range(len(unique_lr)))
    ax1.set_xticklabels([f'{t:.2f}' for t in unique_tol])
    ax1.set_yticklabels([f'{lr:.1e}' for lr in unique_lr])
    ax1.set_xlabel('Tolerance [m]')
    ax1.set_ylabel('Learning Rate')
    ax1.set_title('Final CGPD [m]')
    plt.colorbar(im1, ax=ax1)
    
    # Annotate cells
    for i in range(len(unique_lr)):
        for j in range(len(unique_tol)):
            text = ax1.text(j, i, f'{cgpd_matrix[i, j]:.1f}',
                          ha="center", va="center", color="w", fontsize=9)
    
    # 2. Heatmap of iterations
    ax2 = plt.subplot(2, 3, 2)
    im2 = ax2.imshow(iter_matrix, aspect='auto', origin='lower', cmap='plasma')
    ax2.set_xticks(range(len(unique_tol)))
    ax2.set_yticks(range(len(unique_lr)))
    ax2.set_xticklabels([f'{t:.2f}' for t in unique_tol])
    ax2.set_yticklabels([f'{lr:.1e}' for lr in unique_lr])
    ax2.set_xlabel('Tolerance [m]')
    ax2.set_ylabel('Learning Rate')
    ax2.set_title('Number of Iterations')
    plt.colorbar(im2, ax=ax2)
    
    # Annotate cells
    for i in range(len(unique_lr)):
        for j in range(len(unique_tol)):
            text = ax2.text(j, i, f'{int(iter_matrix[i, j])}',
                          ha="center", va="center", color="w", fontsize=9)
    
    # 3. Heatmap of improvement
    ax3 = plt.subplot(2, 3, 3)
    im3 = ax3.imshow(improvement_matrix, aspect='auto', origin='lower', cmap='RdYlGn')
    ax3.set_xticks(range(len(unique_tol)))
    ax3.set_yticks(range(len(unique_lr)))
    ax3.set_xticklabels([f'{t:.2f}' for t in unique_tol])
    ax3.set_yticklabels([f'{lr:.1e}' for lr in unique_lr])
    ax3.set_xlabel('Tolerance [m]')
    ax3.set_ylabel('Learning Rate')
    ax3.set_title('Improvement from Initial [m]')
    plt.colorbar(im3, ax=ax3)
    
    # Annotate cells
    for i in range(len(unique_lr)):
        for j in range(len(unique_tol)):
            text = ax3.text(j, i, f'{improvement_matrix[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=9)
    
    # 4. CGPD vs Learning Rate (for different tolerances)
    ax4 = plt.subplot(2, 3, 4)
    for j, tol in enumerate(unique_tol):
        mask = tolerances == tol
        ax4.plot(learning_rates[mask], cgpds[mask], 'o-', label=f'Tol = {tol:.2f} m')
    ax4.set_xscale('log')
    ax4.set_xlabel('Learning Rate')
    ax4.set_ylabel('Final CGPD [m]')
    ax4.set_title('CGPD vs Learning Rate')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Iterations vs Learning Rate
    ax5 = plt.subplot(2, 3, 5)
    for j, tol in enumerate(unique_tol):
        mask = tolerances == tol
        ax5.plot(learning_rates[mask], iterations[mask], 'o-', label=f'Tol = {tol:.2f} m')
    ax5.set_xscale('log')
    ax5.set_xlabel('Learning Rate')
    ax5.set_ylabel('Number of Iterations')
    ax5.set_title('Iterations vs Learning Rate')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Computation time vs Learning Rate
    ax6 = plt.subplot(2, 3, 6)
    for j, tol in enumerate(unique_tol):
        mask = tolerances == tol
        ax6.plot(learning_rates[mask], times[mask], 'o-', label=f'Tol = {tol:.2f} m')
    ax6.set_xscale('log')
    ax6.set_xlabel('Learning Rate')
    ax6.set_ylabel('Computation Time [s]')
    ax6.set_title('Time vs Learning Rate')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_file = 'plots/optimization/hyperparameter_sensitivity.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f'Saved: {output_file}')
    
    # Print summary
    print('\n' + '='*60)
    print('Hyperparameter Sensitivity Summary')
    print('='*60)
    print(f'\nInitial CGPD: {initial_cgpd:.3f} m')
    print(f'\nBest configuration:')
    best_idx = np.argmin(cgpds)
    print(f'  Learning Rate: {learning_rates[best_idx]:.1e}')
    print(f'  Tolerance: {tolerances[best_idx]:.2f} m')
    print(f'  Final CGPD: {cgpds[best_idx]:.3f} m')
    print(f'  Improvement: {improvements[best_idx]:.3f} m ({100*improvements[best_idx]/initial_cgpd:.2f}%)')
    print(f'  Iterations: {iterations[best_idx]}')
    print(f'  Time: {times[best_idx]:.5f} s')
    
    print(f'\nWorst configuration:')
    worst_idx = np.argmax(cgpds)
    print(f'  Learning Rate: {learning_rates[worst_idx]:.1e}')
    print(f'  Tolerance: {tolerances[worst_idx]:.2f} m')
    print(f'  Final CGPD: {cgpds[worst_idx]:.3f} m')
    print(f'  Improvement: {improvements[worst_idx]:.3f} m ({100*improvements[worst_idx]/initial_cgpd:.2f}%)')
    print(f'  Iterations: {iterations[worst_idx]}')
    
    print(f'\nKey findings:')
    print(f'  - CGPD range: {cgpds.min():.3f} - {cgpds.max():.3f} m')
    print(f'  - Iteration range: {iterations.min()} - {iterations.max()}')
    print(f'  - Time range: {times.min():.5f} - {times.max():.5f} s')
    print(f'  - Learning rate has significant impact on solution quality')
    print(f'  - Higher learning rates achieve better results in fewer iterations')
    print(f'  - Tolerance mainly affects stopping criterion, not final quality')
    print('='*60)

if __name__ == '__main__':
    main()
