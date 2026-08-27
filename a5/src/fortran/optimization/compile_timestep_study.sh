#!/bin/bash

echo "========================================"
echo "Compiling Timestep Study"
echo "========================================"
echo ""

# Directories
MODULE_DIR="../modules"
OPTIMIZATION_DIR="../optimization"
BUILD_DIR="../build"

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Compilation flags
FFLAGS="-O3 -march=native -ffast-math -funroll-loops"

echo "Compiling modules..."

# Compile gravity module
echo "  - gravity.f90"
gfortran $FFLAGS -c "$MODULE_DIR/gravity.f90" -o "$BUILD_DIR/gravity.o" -J "$BUILD_DIR"

# Compile objective function module
echo "  - objective_function.f90"
gfortran $FFLAGS -c "$MODULE_DIR/objective_function.f90" -o "$BUILD_DIR/objective_function.o" -J "$BUILD_DIR"

# Compile gradient descent module
echo "  - gradient_descent.f90"
gfortran $FFLAGS -c "$MODULE_DIR/gradient_descent.f90" -o "$BUILD_DIR/gradient_descent.o" -J "$BUILD_DIR"

# Compile timestep control module
echo "  - timestep_control_mod.f90"
gfortran $FFLAGS -c "$MODULE_DIR/timestep_control_mod.f90" -o "$BUILD_DIR/timestep_control_mod.o" -J "$BUILD_DIR"

# Compile perturbation modules
echo "  - j2_perturbation.f90"
gfortran $FFLAGS -c "$MODULE_DIR/j2_perturbation.f90" -o "$BUILD_DIR/j2_perturbation.o" -J "$BUILD_DIR"

echo "  - drag_perturbation.f90"
gfortran $FFLAGS -c "$MODULE_DIR/drag_perturbation.f90" -o "$BUILD_DIR/drag_perturbation.o" -J "$BUILD_DIR"

echo "  - srp_perturbation.f90"
gfortran $FFLAGS -c "$MODULE_DIR/srp_perturbation.f90" -o "$BUILD_DIR/srp_perturbation.o" -J "$BUILD_DIR"

echo "  - third_body_perturbation.f90"
gfortran $FFLAGS -c "$MODULE_DIR/third_body_perturbation.f90" -o "$BUILD_DIR/third_body_perturbation.o" -J "$BUILD_DIR"

# Compile integrator module
echo "  - velocity_verlet.f90"
gfortran $FFLAGS -c "$MODULE_DIR/velocity_verlet.f90" -o "$BUILD_DIR/velocity_verlet.o" -J "$BUILD_DIR"

echo ""
echo "Compiling timestep study program..."
gfortran $FFLAGS -c "$OPTIMIZATION_DIR/timestep_study.f90" -o "$BUILD_DIR/timestep_study.o" -J "$BUILD_DIR"

echo ""
echo "Linking..."
gfortran $FFLAGS -o "$BUILD_DIR/timestep_study" \
    "$BUILD_DIR/gravity.o" \
    "$BUILD_DIR/objective_function.o" \
    "$BUILD_DIR/gradient_descent.o" \
    "$BUILD_DIR/timestep_control_mod.o" \
    "$BUILD_DIR/j2_perturbation.o" \
    "$BUILD_DIR/drag_perturbation.o" \
    "$BUILD_DIR/srp_perturbation.o" \
    "$BUILD_DIR/third_body_perturbation.o" \
    "$BUILD_DIR/velocity_verlet.o" \
    "$BUILD_DIR/timestep_study.o"

echo ""
echo "========================================"
echo "Build successful!"
echo "Executable: $BUILD_DIR/timestep_study"
echo "========================================"
echo ""
echo "To run:"
echo "  cd $BUILD_DIR && ./timestep_study"
