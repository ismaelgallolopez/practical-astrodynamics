#!/bin/bash
# Quick Start Script for Assignment A2
# This script runs all components of the assignment in sequence

set -e  # Exit on error

echo "=========================================="
echo "Assignment A2 - Quick Start"
echo "=========================================="
echo ""

# Get the Python interpreter
PYTHON="/home/ismag/workspace/tud/practical_astrodynamics/pa_env/bin/python"

# Navigate to assignment directory
cd /home/ismag/workspace/tud/practical_astrodynamics/a2

echo "Step 1: Fetch TLE data"
echo "-------------------------------------------"
$PYTHON fetch_tle.py
echo ""

echo "Step 2: Propagate orbit"
echo "-------------------------------------------"
$PYTHON main.py
echo ""

echo "Step 3: Convert to Keplerian elements"
echo "-------------------------------------------"
$PYTHON keplerian.py
echo ""

echo "Step 4: Generate Keplerian plots"
echo "-------------------------------------------"
$PYTHON plot_keplerian.py
echo ""

echo "Step 5: Back-convert to Cartesian"
echo "-------------------------------------------"
$PYTHON back_cartesian.py
echo ""

echo "Step 6: Generate residual plots"
echo "-------------------------------------------"
$PYTHON plot_residual.py
echo ""

echo "Step 7: Convert to co-rotating coordinates"
echo "-------------------------------------------"
$PYTHON corotating.py
echo ""

echo "Step 8: Generate co-rotating plots"
echo "-------------------------------------------"
$PYTHON plot_corotating.py
echo ""

echo "Step 9: Generate answer sheet"
echo "-------------------------------------------"
$PYTHON generate_answer_sheet.py
echo ""

echo "Step 10: Validate answer sheet"
echo "-------------------------------------------"
$PYTHON answer-sheet-sanity.py
echo ""

echo "=========================================="
echo "✓ All tasks completed successfully!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  - data/tle.txt (TLE data)"
echo "  - data/orbit_propagation.npz (propagated orbit)"
echo "  - data/keplerian_elements.npz (Keplerian elements)"
echo "  - data/cartesian_from_keplerian.npz (back-converted Cartesian)"
echo "  - data/corotating_spherical.npz (co-rotating spherical coordinates)"
echo "  - plots/keplerian_elements_plot1.png (Keplerian plot 1)"
echo "  - plots/keplerian_elements_plot2.png (Keplerian plot 2)"
echo "  - plots/residual_magnitude.png (residual magnitude)"
echo "  - plots/residual_grid.png (residual components grid)"
echo "  - plots/groundtrack.png (satellite ground track)"
echo "  - plots/radial_distance.png (radial distance evolution)"
echo "  - plots/latitude_longitude_time.png (lat/lon time series)"
echo "  - plots/corotating_combined.png (combined co-rotating plot)"
echo "  - answer-sheet.yaml (assignment answers)"
echo ""
echo "Ready for submission!"
