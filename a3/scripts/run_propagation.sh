#!/bin/bash
# run_propagation.sh - Run orbit propagation with specified timestep(s)

# Check if timestep argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_propagation.sh <timestep_in_seconds>"
    echo "       ./run_propagation.sh <dt1>,<dt2>,<dt3>,..."
    echo ""
    echo "Examples:"
    echo "  ./run_propagation.sh 300"
    echo "  ./run_propagation.sh 60,300,600,1200"
    echo ""
    echo "This will:"
    echo "  0. Fetch TLE and generate SGP4 reference (if needed)"
    echo "  1. Extract initial state with custom timestep"
    echo "  2. Compile Fortran code (if needed)"
    echo "  3. Run Euler propagator"
    echo "  4. Generate comparison plots"
    exit 1
fi

# Parse comma-separated timesteps
IFS=',' read -ra TIMESTEPS <<< "$1"

echo "========================================"
echo "Orbit Propagation Workflow"
echo "========================================"
echo "Timesteps: ${TIMESTEPS[*]} (${#TIMESTEPS[@]} total)"
echo ""

# Step 0: Fetch TLE (if needed)
echo "Step 0: Checking for TLE data..."
echo "----------------------------------------"

if [ ! -f "data/sgp4_reference/tle.txt" ]; then
    echo "TLE not found. Attempting to fetch..."
    
    # Try to fetch TLE
    python3 src/python/fetch_tle.py
    if [ $? -eq 0 ]; then
        echo "✓ TLE fetched successfully"
    else
        echo "✗ Error: Could not fetch TLE (no internet connection?)"
        echo "  Please ensure internet connection or provide tle.txt"
        exit 1
    fi
else
    echo "✓ TLE data found: data/sgp4_reference/tle.txt"
fi

echo ""
echo "========================================"
echo "Running propagations for ${#TIMESTEPS[@]} timestep(s)"
echo "========================================"

# Compile Fortran once (if needed)
echo ""
echo "Compiling Fortran code..."
if [ ! -f "build/propagate_orbit" ] || [ "src/fortran/gravity.f90" -nt "build/propagate_orbit" ] || [ "src/fortran/euler_method.f90" -nt "build/propagate_orbit" ] || [ "src/fortran/propagate_orbit.f90" -nt "build/propagate_orbit" ]; then
    gfortran src/fortran/gravity.f90 src/fortran/euler_method.f90 src/fortran/propagate_orbit.f90 -o build/propagate_orbit -J build
    if [ $? -ne 0 ]; then
        echo "Error: Compilation failed"
        exit 1
    fi
    echo "Compilation successful"
else
    echo "Executable is up to date"
fi

# Check which timesteps already exist
EXISTING_COUNT=0
MISSING_TIMESTEPS=()

for DT in "${TIMESTEPS[@]}"; do
    if [ -f "data/euler_outputs/dt${DT}s_euler_output.txt" ]; then
        EXISTING_COUNT=$((EXISTING_COUNT + 1))
    else
        MISSING_TIMESTEPS+=("$DT")
    fi
done

echo ""
if [ ${#MISSING_TIMESTEPS[@]} -eq 0 ]; then
    echo "✓ All ${#TIMESTEPS[@]} timestep propagations already exist"
    echo "  To regenerate, delete files in data/euler_outputs/"
else
    echo "Status: ${EXISTING_COUNT}/${#TIMESTEPS[@]} timesteps already exist"
    echo "Will compute ${#MISSING_TIMESTEPS[@]} missing timestep(s): ${MISSING_TIMESTEPS[*]}"
fi

# Loop through each timestep that needs computation
for DT in "${MISSING_TIMESTEPS[@]}"; do
    echo ""
    echo "========================================"
    echo "Processing dt = ${DT} seconds"
    echo "========================================"

    # Step 0.5: Generate timestep-specific SGP4 reference
    echo ""
    echo "Step 0.5: Generating SGP4 reference orbit with dt=${DT}s..."
    python3 src/python/propagator_sgp4.py ${DT}
    if [ $? -ne 0 ]; then
        echo "Error: SGP4 propagation failed for dt=${DT}s"
        exit 1
    fi

    # Step 1: Extract initial state with custom timestep
    echo ""
    echo "Step 1: Extracting initial state with dt=${DT}s..."
    python3 src/python/extract_initial_state.py ${DT}

    if [ $? -ne 0 ]; then
        echo "Error: Failed to extract initial state for dt=${DT}s"
        continue
    fi

    # Step 2: Run propagator
    echo ""
    echo "Step 2: Running Euler propagator..."
    ./build/propagate_orbit

    if [ $? -ne 0 ]; then
        echo "Error: Propagation failed for dt=${DT}s"
        continue
    fi

    # Step 3: Generate comparison plots
    echo ""
    echo "Step 3: Generating comparison plots..."
    python3 src/python/compute_position_difference.py ${DT}

    if [ $? -ne 0 ]; then
        echo "Error: Plotting failed for dt=${DT}s"
        continue
    fi

    # Step 4: Generate Keplerian element plots
    echo ""
    echo "Step 4: Generating Keplerian element plots..."
    echo "  - SGP4 Keplerian plots..."
    # Use timestep-specific SGP4 file if available
    if [ -f "data/sgp4_reference/orbit_propagation_dt${DT}s.npz" ]; then
        python3 src/python/plot_keplerian.py data/sgp4_reference/orbit_propagation_dt${DT}s.npz plots/timestep_comparisons/dt${DT}s
    else
        python3 src/python/plot_keplerian.py data/sgp4_reference/orbit_propagation.npz plots/timestep_comparisons/dt${DT}s
    fi
    
    if [ $? -ne 0 ]; then
        echo "Warning: SGP4 Keplerian plotting failed for dt=${DT}s"
    fi
    
    echo "  - Euler Keplerian plots..."
    python3 src/python/plot_keplerian.py data/euler_outputs/dt${DT}s_euler_output.txt plots/timestep_comparisons/dt${DT}s
    
    if [ $? -ne 0 ]; then
        echo "Warning: Euler Keplerian plotting failed for dt=${DT}s"
    fi

    echo ""
    echo "Complete for dt=${DT}s! Results saved with label: dt${DT}s"
done

echo ""
echo "========================================"
echo "ALL PROPAGATIONS COMPLETE"
echo "========================================"
echo ""
if [ ${#MISSING_TIMESTEPS[@]} -eq 0 ]; then
    echo "No new propagations computed (all existed)"
else
    echo "Computed ${#MISSING_TIMESTEPS[@]} new timestep(s): ${MISSING_TIMESTEPS[*]}"
fi
echo "Total timesteps available: ${#TIMESTEPS[@]}"
echo ""
echo "Output files pattern:"
echo "  - data/euler_outputs/dt<DT>s_euler_output.txt"
echo "  - data/position_differences/dt<DT>s_position_differences.npz"
echo "  - plots/timestep_comparisons/dt<DT>s/position_difference_l2_norm.png"
echo "  - plots/timestep_comparisons/dt<DT>s/keplerian_comparison_*.png"
echo "  - plots/timestep_comparisons/dt<DT>s/sgp4_keplerian_plot1.png"
echo "  - plots/timestep_comparisons/dt<DT>s/sgp4_keplerian_plot2.png"
echo "  - plots/timestep_comparisons/dt<DT>s/euler_keplerian_plot1.png"
echo "  - plots/timestep_comparisons/dt<DT>s/euler_keplerian_plot2.png"
