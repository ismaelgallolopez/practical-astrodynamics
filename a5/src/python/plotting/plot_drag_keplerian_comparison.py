#!/usr/bin/env python3
"""
Plot Keplerian element comparison between undisturbed and drag-perturbed orbits.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from utilities.keplerian import OrbitDataLoader
from plotting.plot_keplerian_residuals import plot_keplerian_elements_and_residuals

def main():
    # Setup paths
    base_dir = Path(__file__).resolve().parents[2]
    output_dir_drag = base_dir / "data" / "outputs_drag"
    output_dir_undisturbed = base_dir / "data" / "outputs_orbit"
    plot_dir = base_dir / "plots" / "drag_keplerian"
    plot_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data using OrbitDataLoader
    loader = OrbitDataLoader()
    
    print("Loading orbit data...")
    print(f"  Drag-perturbed:  {output_dir_drag / 'dt10s_drag_output.txt'}")
    t_drag, r_drag, v_drag, _ = loader.load_from_file(str(output_dir_drag / "dt10s_drag_output.txt"))
    
    print(f"  Undisturbed:     {output_dir_undisturbed / 'dt10s_output.txt'}")
    t_unperturbed, r_unperturbed, v_unperturbed, _ = loader.load_from_file(str(output_dir_undisturbed / "dt10s_output.txt"))
    
    # Convert from meters to kilometers
    r_drag_km = r_drag / 1000.0
    v_drag_km = v_drag / 1000.0
    r_unperturbed_km = r_unperturbed / 1000.0
    v_unperturbed_km = v_unperturbed / 1000.0
    
    # Create plots
    print("\nGenerating Keplerian element comparison plots...")
    figures = plot_keplerian_elements_and_residuals(
        r_unperturbed_km, v_unperturbed_km,
        r_drag_km, v_drag_km,
        times=(t_drag - t_drag[0]),
        disturbance_name="Drag",
        mu=None  # Use WGS72 default
    )
    
    # Save figures
    print(f"\nSaving plots to: {plot_dir}")
    for element_name, fig in figures:
        filename = plot_dir / f'{element_name}_comparison.png'
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  Saved: {filename.name}")
    
    print(f"\nPlots saved to: {plot_dir}")
    print("Done!")

if __name__ == "__main__":
    main()
