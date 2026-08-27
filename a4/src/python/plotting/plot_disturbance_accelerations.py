#!/usr/bin/env python3
"""
Plotting function for disturbance acceleration magnitudes.

This module provides a function to plot the magnitude of accelerations
caused by various orbital perturbations (J2, SRP, drag, third-body, etc.)
as a function of time.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional


def compute_acceleration_magnitude(accelerations: np.ndarray) -> np.ndarray:
    """
    Compute the magnitude of acceleration vectors.
    
    Args:
        accelerations: Acceleration vectors [N x 3] in m/s² or km/s²
        
    Returns:
        Acceleration magnitudes [N] in same units as input
        
    Raises:
        ValueError: If input array has invalid shape
    """
    if accelerations.ndim != 2 or accelerations.shape[1] != 3:
        raise ValueError(
            f"Expected array of shape (N, 3), got {accelerations.shape}"
        )
    
    # Compute L2 norm along axis 1
    magnitudes = np.linalg.norm(accelerations, axis=1)
    
    return magnitudes


def plot_disturbance_magnitudes(
    times: np.ndarray,
    accelerations_dict: Dict[str, np.ndarray],
    time_unit: str = 'hours',
    acc_unit: str = 'm/s²',
    title: Optional[str] = None,
    use_log_scale: bool = False,
    show_statistics: bool = True
) -> plt.Figure:
    """
    Plot magnitude of disturbance accelerations as a function of time.
    
    Creates a single plot showing the acceleration magnitude for multiple
    disturbances on the same axes for easy comparison.
    
    Args:
        times: Time array [N] in seconds from epoch
        accelerations_dict: Dictionary mapping disturbance names to acceleration
                          arrays [N x 3]. Keys are disturbance names (e.g., 'J2', 'SRP'),
                          values are acceleration vectors in m/s² or km/s²
        time_unit: Unit for time axis ('seconds', 'hours', 'days')
        acc_unit: Unit for acceleration ('m/s²', 'km/s²', 'mm/s²')
        title: Optional custom title (default: auto-generated)
        use_log_scale: If True, use logarithmic scale for y-axis
        show_statistics: If True, display statistics box
        
    Returns:
        Figure object
        
    Raises:
        ValueError: If inputs have incompatible shapes or invalid parameters
        
    Example:
        >>> times = np.linspace(0, 86400, 1000)  # 1 day
        >>> acc_j2 = np.random.randn(1000, 3) * 1e-5
        >>> acc_srp = np.random.randn(1000, 3) * 1e-7
        >>> 
        >>> fig = plot_disturbance_magnitudes(
        ...     times,
        ...     {'J2': acc_j2, 'SRP': acc_srp},
        ...     time_unit='hours',
        ...     acc_unit='m/s²'
        ... )
        >>> fig.savefig('disturbance_magnitudes.png')
    """
    # Validate inputs
    if not accelerations_dict:
        raise ValueError("accelerations_dict cannot be empty")
    
    # Convert time to requested units
    time_conversion = {
        'seconds': 1.0,
        'hours': 1.0 / 3600.0,
        'days': 1.0 / 86400.0
    }
    
    if time_unit.lower() not in time_conversion:
        raise ValueError(
            f"Invalid time_unit '{time_unit}'. "
            f"Must be one of {list(time_conversion.keys())}"
        )
    
    times_converted = times * time_conversion[time_unit.lower()]
    
    # Validate all acceleration arrays
    n_points = len(times)
    for name, acc in accelerations_dict.items():
        if len(acc) != n_points:
            raise ValueError(
                f"Acceleration array for '{name}' has {len(acc)} points, "
                f"but time array has {n_points} points"
            )
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 6))
    
    # Color scheme for different disturbances
    colors = [
        'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
        'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan'
    ]
    
    # Line styles for variety
    linestyles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
    
    # Plot each disturbance
    lines = []
    labels = []
    statistics = {}
    
    for idx, (name, accelerations) in enumerate(accelerations_dict.items()):
        # Compute magnitude
        magnitudes = compute_acceleration_magnitude(accelerations)
        
        # Store statistics
        statistics[name] = {
            'mean': np.mean(magnitudes),
            'std': np.std(magnitudes),
            'min': np.min(magnitudes),
            'max': np.max(magnitudes),
            'median': np.median(magnitudes)
        }
        
        # Plot
        color = colors[idx % len(colors)]
        linestyle = linestyles[idx % len(linestyles)]
        
        line = ax.plot(
            times_converted, magnitudes,
            color=color,
            linestyle=linestyle,
            linewidth=2.0,
            label=name,
            alpha=0.85
        )
        
        lines.extend(line)
        labels.append(name)
    
    # Axis labels
    time_labels = {
        'seconds': 'Time [s]',
        'hours': 'Time [hours]',
        'days': 'Time [days]'
    }
    ax.set_xlabel(time_labels.get(time_unit.lower(), f'Time [{time_unit}]'), 
                  fontsize=13)
    ax.set_ylabel(f'Acceleration Magnitude [{acc_unit}]', fontsize=13)
    
    # Title
    if title is None:
        title = 'Disturbance Acceleration Magnitudes vs Time'
    ax.set_title(title, fontsize=15, fontweight='bold', pad=15)
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    
    # Log scale if requested
    if use_log_scale:
        ax.set_yscale('log')
        ax.yaxis.set_minor_locator(plt.LogLocator(subs='auto'))
    
    # Legend - place outside to the right
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), fontsize=11, 
              framealpha=0.95, edgecolor='gray')
    
    # Statistics box
    if show_statistics and len(statistics) <= 5:
        stats_text = "Statistics:\n" + "─" * 35 + "\n"
        
        for name, stats in statistics.items():
            stats_text += f"{name}:\n"
            stats_text += f"  Mean: {stats['mean']:.6g} {acc_unit}\n"
            stats_text += f"  Max:  {stats['max']:.6g} {acc_unit}\n"
            stats_text += f"  Min:  {stats['min']:.6g} {acc_unit}\n"
        
        # Position statistics box outside plot area, aligned with legend
        fig.text(
            1.02, 0.35, stats_text,
            transform=ax.transAxes,
            verticalalignment='center',
            horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85, edgecolor='gray'),
            fontsize=9,
            family='monospace'
        )
    
    plt.tight_layout(rect=[0, 0, 0.78, 1])  # Leave more space on the right for legend and text
    
    # Print statistics to console
    print("\n" + "=" * 70)
    print("DISTURBANCE ACCELERATION STATISTICS")
    print("=" * 70)
    
    for name, stats in statistics.items():
        print(f"\n{name}:")
        print(f"  Mean:      {stats['mean']:.6e} {acc_unit}")
        print(f"  Std Dev:   {stats['std']:.6e} {acc_unit}")
        print(f"  Median:    {stats['median']:.6e} {acc_unit}")
        print(f"  Min:       {stats['min']:.6e} {acc_unit}")
        print(f"  Max:       {stats['max']:.6e} {acc_unit}")
        print(f"  Range:     {stats['max'] - stats['min']:.6e} {acc_unit}")
    
    print("\n" + "=" * 70)
    
    return fig


def plot_single_disturbance_magnitude(
    times: np.ndarray,
    accelerations: np.ndarray,
    disturbance_name: str,
    time_unit: str = 'hours',
    acc_unit: str = 'm/s²',
    use_log_scale: bool = False
) -> plt.Figure:
    """
    Plot magnitude of a single disturbance acceleration.
    
    Convenience function for plotting a single disturbance.
    
    Args:
        times: Time array [N] in seconds from epoch
        accelerations: Acceleration vectors [N x 3]
        disturbance_name: Name of the disturbance
        time_unit: Unit for time axis
        acc_unit: Unit for acceleration
        use_log_scale: If True, use logarithmic scale
        
    Returns:
        Figure object
    """
    return plot_disturbance_magnitudes(
        times,
        {disturbance_name: accelerations},
        time_unit=time_unit,
        acc_unit=acc_unit,
        title=f'{disturbance_name} Acceleration Magnitude vs Time',
        use_log_scale=use_log_scale
    )


def plot_disturbance_components(
    times: np.ndarray,
    accelerations: np.ndarray,
    disturbance_name: str,
    time_unit: str = 'hours',
    acc_unit: str = 'm/s²'
) -> plt.Figure:
    """
    Plot individual components (x, y, z) and magnitude of acceleration.
    
    Creates a plot with 4 subplots showing x, y, z components and the
    total magnitude.
    
    Args:
        times: Time array [N] in seconds from epoch
        accelerations: Acceleration vectors [N x 3]
        disturbance_name: Name of the disturbance
        time_unit: Unit for time axis
        acc_unit: Unit for acceleration
        
    Returns:
        Figure object with 4 subplots
    """
    # Convert time
    time_conversion = {'seconds': 1.0, 'hours': 1.0/3600.0, 'days': 1.0/86400.0}
    times_converted = times * time_conversion.get(time_unit.lower(), 1.0)
    
    # Compute magnitude
    magnitude = compute_acceleration_magnitude(accelerations)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(f'{disturbance_name} Acceleration Components and Magnitude',
                 fontsize=16, fontweight='bold')
    
    time_label = {'seconds': 'Time [s]', 'hours': 'Time [hours]', 
                  'days': 'Time [days]'}.get(time_unit.lower(), f'Time [{time_unit}]')
    
    # X component
    axes[0, 0].plot(times_converted, accelerations[:, 0], 
                    color='tab:red', linewidth=1.5)
    axes[0, 0].set_ylabel(f'X Acceleration [{acc_unit}]', fontsize=11)
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_title('X Component', fontsize=12)
    
    # Y component
    axes[0, 1].plot(times_converted, accelerations[:, 1], 
                    color='tab:green', linewidth=1.5)
    axes[0, 1].set_ylabel(f'Y Acceleration [{acc_unit}]', fontsize=11)
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_title('Y Component', fontsize=12)
    
    # Z component
    axes[1, 0].plot(times_converted, accelerations[:, 2], 
                    color='tab:blue', linewidth=1.5)
    axes[1, 0].set_xlabel(time_label, fontsize=11)
    axes[1, 0].set_ylabel(f'Z Acceleration [{acc_unit}]', fontsize=11)
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_title('Z Component', fontsize=12)
    
    # Magnitude
    axes[1, 1].plot(times_converted, magnitude, 
                    color='tab:purple', linewidth=2.0)
    axes[1, 1].set_xlabel(time_label, fontsize=11)
    axes[1, 1].set_ylabel(f'Magnitude [{acc_unit}]', fontsize=11)
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_title('Total Magnitude', fontsize=12, fontweight='bold')
    
    # Add statistics to magnitude plot
    stats_text = f'Mean: {np.mean(magnitude):.6g} {acc_unit}\n'
    stats_text += f'Max:  {np.max(magnitude):.6g} {acc_unit}\n'
    stats_text += f'Min:  {np.min(magnitude):.6g} {acc_unit}'
    
    axes[1, 1].text(0.98, 0.98, stats_text, transform=axes[1, 1].transAxes,
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                    fontsize=9, family='monospace')
    
    plt.tight_layout()
    
    return fig


def main():
    """
    Example usage of disturbance acceleration plotting functions.
    """
    import sys
    
    print("=" * 70)
    print("DISTURBANCE ACCELERATION MAGNITUDE PLOTTING")
    print("=" * 70)
    
    # Example: Generate synthetic acceleration data
    print("\nGenerating synthetic disturbance acceleration data...")
    
    n_points = 1000
    times = np.linspace(0, 86400, n_points)  # 1 day in seconds
    
    # Simulate different disturbances with different magnitudes
    # J2: ~1e-5 m/s²
    acc_j2 = np.random.randn(n_points, 3) * 5e-6 + np.array([1e-5, 0, 0])
    
    # SRP: ~1e-7 m/s²
    acc_srp = np.random.randn(n_points, 3) * 1e-8 + np.array([0, 5e-8, 0])
    
    # Drag: ~1e-6 m/s² (decaying)
    acc_drag = np.random.randn(n_points, 3) * 1e-7
    acc_drag[:, 0] -= np.linspace(5e-7, 1e-6, n_points)
    
    # Third-body (Moon): ~1e-6 m/s²
    acc_tbp = np.sin(2 * np.pi * times / 86400)[:, np.newaxis] * np.array([1e-6, 1e-6, 5e-7])
    acc_tbp += np.random.randn(n_points, 3) * 1e-7
    
    print(f"Generated {n_points} data points over 1 day")
    
    # Create plots
    print("\nCreating plots...")
    
    # Plot 1: All disturbances together
    print("  Plot 1: Combined disturbances (linear scale)...")
    accelerations = {
        'J2': acc_j2,
        'SRP': acc_srp,
        'Drag': acc_drag,
        'Third-Body': acc_tbp
    }
    
    fig1 = plot_disturbance_magnitudes(
        times, accelerations,
        time_unit='hours',
        acc_unit='m/s²',
        use_log_scale=False
    )
    
    # Plot 2: All disturbances with log scale
    print("  Plot 2: Combined disturbances (log scale)...")
    fig2 = plot_disturbance_magnitudes(
        times, accelerations,
        time_unit='hours',
        acc_unit='m/s²',
        use_log_scale=True,
        title='Disturbance Acceleration Magnitudes (Log Scale)'
    )
    
    # Plot 3: Single disturbance (J2)
    print("  Plot 3: J2 disturbance only...")
    fig3 = plot_single_disturbance_magnitude(
        times, acc_j2,
        'J2 Perturbation',
        time_unit='hours',
        acc_unit='m/s²'
    )
    
    # Plot 4: Components breakdown
    print("  Plot 4: J2 components breakdown...")
    fig4 = plot_disturbance_components(
        times, acc_j2,
        'J2 Perturbation',
        time_unit='hours',
        acc_unit='m/s²'
    )
    
    # Save figures
    import os
    output_dir = 'plots/disturbance_accelerations'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nSaving plots to: {output_dir}")
    
    fig1.savefig(f'{output_dir}/combined_linear.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_dir}/combined_linear.png")
    
    fig2.savefig(f'{output_dir}/combined_log.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_dir}/combined_log.png")
    
    fig3.savefig(f'{output_dir}/j2_magnitude.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_dir}/j2_magnitude.png")
    
    fig4.savefig(f'{output_dir}/j2_components.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: {output_dir}/j2_components.png")
    
    print("\n" + "=" * 70)
    print("PLOTTING COMPLETE")
    print("=" * 70)
    print("\nTo use in your scripts:")
    print("  from plot_disturbance_accelerations import plot_disturbance_magnitudes")
    print("\nExample:")
    print("  fig = plot_disturbance_magnitudes(times, {'J2': acc_j2}, 'hours', 'm/s²')")
    
    # Show plots
    plt.show()


if __name__ == "__main__":
    main()
