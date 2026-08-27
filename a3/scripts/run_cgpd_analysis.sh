#!/bin/bash

# Run CGPD analysis: propagate with different timesteps and plot CGPD vs timestep
# Requires at least 10 timesteps spanning at least 2 orders of magnitude

echo "=================================================="
echo "CGPD Analysis: Euler Integrator Timestep Sensitivity"
echo "=================================================="

# Define timesteps spanning 2+ orders of magnitude (1s to 20000s = 20000x range)
TIMESTEPS="1,2,5,10,20,30,50,75,100,150,200,300,500,750,1000,1500,2000,5000,10000,20000"

echo ""
echo "Timesteps to analyze: $TIMESTEPS"
echo ""
echo "Step 1: Running orbit propagations..."
echo "--------------------------------------------------"

# Run all propagations
./scripts/run_propagation.sh "$TIMESTEPS"

if [ $? -ne 0 ]; then
    echo "Error: Propagation failed"
    exit 1
fi

echo ""
echo "Step 2: Computing CGPD vs timestep..."
echo "--------------------------------------------------"

# Make script executable
chmod +x src/python/plot_cgpd_vs_timestep.py

# Run CGPD analysis
python3 src/python/plot_cgpd_vs_timestep.py "$TIMESTEPS"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================="
    echo "CGPD analysis complete!"
    echo "================================================="
    echo "Output files:"
    echo "  - plots/summary/cgpd_vs_timestep.png"
    echo "  - data/summary/cgpd_vs_timestep.npz"
else
    echo "Error: CGPD analysis failed"
    exit 1
fi
