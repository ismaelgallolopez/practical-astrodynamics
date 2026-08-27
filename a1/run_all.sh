#!/bin/bash
# Quick Start Script for Assignment A1
# This script runs all components of the assignment in sequence

set -e  # Exit on error

echo "=========================================="
echo "Assignment A1 - Quick Start"
echo "=========================================="
echo ""

# Get the Python interpreter
PYTHON="/home/ismag/workspace/tud/practical_astrodynamics/pa_env/bin/python"

# Navigate to assignment directory
cd /home/ismag/workspace/tud/practical_astrodynamics/a1

echo "Step 1: Fetch TLE data"
echo "-------------------------------------------"
$PYTHON fetch_tle.py
echo ""

echo "Step 2: Propagate orbit"
echo "-------------------------------------------"
$PYTHON main.py
echo ""

echo "Step 3: Generate plots"
echo "-------------------------------------------"
$PYTHON plot_orbit.py
echo ""

echo "Step 4: Validate answer sheet"
echo "-------------------------------------------"
$PYTHON answer-sheet-sanity.py
echo ""

echo "Step 5: Example data analysis"
echo "-------------------------------------------"
$PYTHON example_load_data.py
echo ""

echo "=========================================="
echo "✓ All tasks completed successfully!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  - data/tle.txt (TLE data)"
echo "  - data/orbit_propagation.npz (propagated orbit)"
echo "  - orbit_pos_vel_vs_time.png (position/velocity plot)"
echo "  - orbit_3d.png (3D visualization)"
echo "  - orbit_altitude_speed.png (altitude/speed plot)"
echo "  - orbit_orbital_elements.png (orbital elements plot)"
echo "  - answer-sheet.yaml (assignment answers)"
echo ""
echo "Ready for submission!"
