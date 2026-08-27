#!/bin/bash
# Compilation script for gradient descent optimization

# Navigate to the build directory
cd "$(dirname "$0")/../build" || exit 1

# Set compiler
FC=gfortran
FFLAGS="-O2 -Wall"

# Module directories
MOD_DIR="../modules"
OPT_DIR="../optimization"

echo "========================================"
echo "Compiling Gradient Descent Optimizer"
echo "========================================"
echo ""

# Compile modules (in dependency order)
echo "Compiling modules..."

# 1. Gravity module (no dependencies)
echo "  - gravity.f90"
$FC $FFLAGS -c $MOD_DIR/gravity.f90 -J . || exit 1

# 2. Objective function module (depends on gravity)
echo "  - objective_function.f90"
$FC $FFLAGS -c $MOD_DIR/objective_function.f90 -J . || exit 1

# 3. Gradient descent module (depends on gravity)
echo "  - gradient_descent.f90"
$FC $FFLAGS -c $OPT_DIR/gradient_descent.f90 -J . || exit 1

# 4. J2 perturbation (depends on gravity)
echo "  - j2_perturbation.f90"
$FC $FFLAGS -c $MOD_DIR/j2_perturbation.f90 -J . || exit 1

# 5. Drag perturbation (depends on gravity)
echo "  - drag_perturbation.f90"
$FC $FFLAGS -c $MOD_DIR/drag_perturbation.f90 -J . || exit 1

# 6. SRP perturbation (depends on gravity)
echo "  - srp_perturbation.f90"
$FC $FFLAGS -c $MOD_DIR/srp_perturbation.f90 -J . || exit 1

# 7. Third body perturbation (depends on gravity)
echo "  - third_body_perturbation.f90"
$FC $FFLAGS -c $MOD_DIR/third_body_perturbation.f90 -J . || exit 1

# 8. Velocity Verlet integrator
echo "  - velocity_verlet.f90"
$FC $FFLAGS -c $MOD_DIR/velocity_verlet.f90 -J . || exit 1

echo ""
echo "Compiling optimization program..."

# Compile main program
echo "  - optimize_gradient_descent.f90"
$FC $FFLAGS -c $OPT_DIR/optimize_gradient_descent.f90 -J . || exit 1

echo ""
echo "Linking..."

# Link everything together
$FC $FFLAGS -o optimize_gradient_descent \
    gravity.o \
    objective_function.o \
    gradient_descent.o \
    j2_perturbation.o \
    drag_perturbation.o \
    srp_perturbation.o \
    third_body_perturbation.o \
    velocity_verlet.o \
    optimize_gradient_descent.o || exit 1

echo ""
echo "========================================"
echo "Build successful!"
echo "Executable: build/optimize_gradient_descent"
echo "========================================"
echo ""
echo "To run:"
echo "  cd build && ./optimize_gradient_descent"
