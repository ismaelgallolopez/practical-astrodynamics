#!/bin/bash

echo "========================================"
echo "Compiling Grid Search Optimization"
echo "========================================"
echo ""

MOD_DIR=../modules
BUILD_DIR=../build
OPT_DIR=../optimization

FC=gfortran
FFLAGS="-O2 -Wall -J${BUILD_DIR}"

MODULES=(
    "${MOD_DIR}/gravity.f90"
    "${MOD_DIR}/objective_function.f90"
    "${MOD_DIR}/j2_perturbation.f90"
    "${MOD_DIR}/drag_perturbation.f90"
    "${MOD_DIR}/srp_perturbation.f90"
    "${MOD_DIR}/third_body_perturbation.f90"
    "${MOD_DIR}/velocity_verlet.f90"
)

PROG="${OPT_DIR}/grid_search.f90"

echo "Compiling modules..."
for mod in "${MODULES[@]}"; do
    mod_name=$(basename "$mod")
    echo "  - $mod_name"
    $FC $FFLAGS -c "$mod" -o "${BUILD_DIR}/${mod_name%.f90}.o"
    if [ $? -ne 0 ]; then
        echo "Error compiling $mod_name"
        exit 1
    fi
done

echo ""
echo "Compiling grid search..."
$FC $FFLAGS -c "$PROG" -o "${BUILD_DIR}/grid_search.o"
if [ $? -ne 0 ]; then
    echo "Error compiling grid_search.f90"
    exit 1
fi

echo ""
echo "Linking..."
$FC $FFLAGS \
    "${BUILD_DIR}/gravity.o" \
    "${BUILD_DIR}/objective_function.o" \
    "${BUILD_DIR}/j2_perturbation.o" \
    "${BUILD_DIR}/drag_perturbation.o" \
    "${BUILD_DIR}/srp_perturbation.o" \
    "${BUILD_DIR}/third_body_perturbation.o" \
    "${BUILD_DIR}/velocity_verlet.o" \
    "${BUILD_DIR}/grid_search.o" \
    -o "${BUILD_DIR}/grid_search" -lm

if [ $? -ne 0 ]; then
    echo "Error linking"
    exit 1
fi

echo ""
echo "========================================"
echo "Build successful!"
echo "Executable: ${BUILD_DIR}/grid_search"
echo "========================================"
echo ""
echo "To run:"
echo "  cd ${BUILD_DIR} && ./grid_search"
echo ""
