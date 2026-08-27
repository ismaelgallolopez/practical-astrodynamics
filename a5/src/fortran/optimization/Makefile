# Makefile for Gradient Descent Optimizer
# Compiles the optimization program with all required modules

# Compiler and flags
FC = gfortran
FFLAGS = -O2 -Wall -J$(BUILD_DIR)
LDFLAGS = -lm

# Directories
MOD_DIR = ../modules
BUILD_DIR = ../build
OPT_DIR = .

# Source files
MOD_SOURCES = $(MOD_DIR)/gravity.f90 \
              $(MOD_DIR)/objective_function.f90 \
              $(OPT_DIR)/gradient_descent.f90 \
              $(MOD_DIR)/j2_perturbation.f90 \
              $(MOD_DIR)/drag_perturbation.f90 \
              $(MOD_DIR)/srp_perturbation.f90 \
              $(MOD_DIR)/third_body_perturbation.f90 \
              $(MOD_DIR)/velocity_verlet.f90

PROG_SOURCE = $(OPT_DIR)/optimize_gradient_descent.f90

# Object files
MOD_OBJECTS = $(BUILD_DIR)/gravity.o \
              $(BUILD_DIR)/objective_function.o \
              $(BUILD_DIR)/gradient_descent.o \
              $(BUILD_DIR)/j2_perturbation.o \
              $(BUILD_DIR)/drag_perturbation.o \
              $(BUILD_DIR)/srp_perturbation.o \
              $(BUILD_DIR)/third_body_perturbation.o \
              $(BUILD_DIR)/velocity_verlet.o

PROG_OBJECT = $(BUILD_DIR)/optimize_gradient_descent.o

# Executable
EXECUTABLE = $(BUILD_DIR)/optimize_gradient_descent

# Default target
all: $(EXECUTABLE)

# Link executable
$(EXECUTABLE): $(MOD_OBJECTS) $(PROG_OBJECT)
	@echo "Linking..."
	$(FC) $(FFLAGS) -o $@ $^ $(LDFLAGS)
	@echo ""
	@echo "========================================"
	@echo "Build successful!"
	@echo "Executable: $(EXECUTABLE)"
	@echo "========================================"
	@echo ""
	@echo "To run:"
	@echo "  cd $(BUILD_DIR) && ./optimize_gradient_descent"
	@echo ""

# Compile modules (with dependencies)
$(BUILD_DIR)/gravity.o: $(MOD_DIR)/gravity.f90
	@echo "Compiling gravity.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

$(BUILD_DIR)/objective_function.o: $(MOD_DIR)/objective_function.f90 $(BUILD_DIR)/gravity.o
	@echo "Compiling objective_function.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

$(BUILD_DIR)/gradient_descent.o: $(OPT_DIR)/gradient_descent.f90 $(BUILD_DIR)/gravity.o
	@echo "Compiling gradient_descent.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

$(BUILD_DIR)/j2_perturbation.o: $(MOD_DIR)/j2_perturbation.f90 $(BUILD_DIR)/gravity.o
	@echo "Compiling j2_perturbation.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

$(BUILD_DIR)/drag_perturbation.o: $(MOD_DIR)/drag_perturbation.f90 $(BUILD_DIR)/gravity.o
	@echo "Compiling drag_perturbation.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

$(BUILD_DIR)/srp_perturbation.o: $(MOD_DIR)/srp_perturbation.f90 $(BUILD_DIR)/gravity.o
	@echo "Compiling srp_perturbation.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

$(BUILD_DIR)/third_body_perturbation.o: $(MOD_DIR)/third_body_perturbation.f90 $(BUILD_DIR)/gravity.o
	@echo "Compiling third_body_perturbation.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

$(BUILD_DIR)/velocity_verlet.o: $(MOD_DIR)/velocity_verlet.f90 $(BUILD_DIR)/gravity.o
	@echo "Compiling velocity_verlet.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

# Compile main program (depends on all modules)
$(BUILD_DIR)/optimize_gradient_descent.o: $(PROG_SOURCE) $(MOD_OBJECTS)
	@echo "Compiling optimize_gradient_descent.f90..."
	$(FC) $(FFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(BUILD_DIR)/*.o $(BUILD_DIR)/*.mod $(EXECUTABLE)
	@echo "Clean complete."

# Run the program
run: $(EXECUTABLE)
	cd $(BUILD_DIR) && ./optimize_gradient_descent

# Rebuild everything
rebuild: clean all

.PHONY: all clean run rebuild
