#!/bin/bash
# Compilation script for propagate_orbit_all

# Navigate to the build directory
cd "$(dirname "$0")/build" || exit 1

# Set compiler
FC=gfortran
FFLAGS="-O2 -Wall"

# Module directory
MOD_DIR="../modules"
PROP_DIR="../propagators"

echo "========================================"
echo "Compiling propagate_orbit_all"
echo "========================================"
echo ""

# Compile modules (in dependency order)
echo "Compiling modules..."

# 1. Gravity module (no dependencies)
echo "  - gravity.f90"
$FC $FFLAGS -c $MOD_DIR/gravity.f90 -J . || exit 1

# 2. J2 perturbation (depends on gravity)
echo "  - j2_perturbation.f90"
$FC $FFLAGS -c $MOD_DIR/j2_perturbation.f90 -J . || exit 1

# 3. Drag perturbation (depends on gravity)
echo "  - drag_perturbation.f90"
$FC $FFLAGS -c $MOD_DIR/drag_perturbation.f90 -J . || exit 1

# 4. SRP perturbation (depends on gravity)
echo "  - srp_perturbation.f90"
$FC $FFLAGS -c $MOD_DIR/srp_perturbation.f90 -J . || exit 1

# 5. Third body perturbation (depends on gravity)
echo "  - third_body_perturbation.f90"
$FC $FFLAGS -c $MOD_DIR/third_body_perturbation.f90 -J . || exit 1

# 6. Velocity Verlet integrator
echo "  - velocity_verlet.f90"
$FC $FFLAGS -c $MOD_DIR/velocity_verlet.f90 -J . || exit 1

echo ""
echo "Compiling main program..."

# Compile main program
echo "  - propagate_orbit_all.f90"
$FC $FFLAGS -c $PROP_DIR/propagate_orbit_all.f90 -J . || exit 1

echo ""
echo "Linking..."

# Link everything together
$FC $FFLAGS -o propagate_orbit_all \
    gravity.o \
    j2_perturbation.o \
    drag_perturbation.o \
    srp_perturbation.o \
    third_body_perturbation.o \
    velocity_verlet.o \
    propagate_orbit_all.o || exit 1

echo ""
echo "========================================"
echo "Build successful!"
echo "Executable: build/propagate_orbit_all"
echo "========================================"
echo ""
echo "To run:"
echo "  cd build && ./propagate_orbit_all"
