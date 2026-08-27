# Makefile for Assignment A3 - Practical Astrodynamics
# Orbit Propagation with Euler and Velocity Verlet Methods

# Configuration
FC = gfortran
FFLAGS = -O2 -Wall -std=f2008 -fall-intrinsics
PYTHON = .venv/bin/python
SRC_FORTRAN = src/fortran
BUILD_DIR = build
DATA_DIR = data
PLOTS_DIR = plots

# Default timesteps for testing
DT_TEST = 100
DT_CGPD = 1 2 5 10 20 30 50 75 100 150 200 300 500 750 1000 1500 2000 5000 10000 20000

# Phony targets (not real files)
.PHONY: all help clean clean-data clean-plots compile euler verlet sgp4 plots analysis answer-sheet test

# Default target
all: help

# Help target - show available commands
help:
	@echo "========================================"
	@echo "Assignment A3 - Build System"
	@echo "========================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make help          - Show this help message"
	@echo "  make compile       - Compile all Fortran programs"
	@echo "  make euler         - Run Euler propagation (dt=$(DT_TEST)s)"
	@echo "  make verlet        - Run Velocity Verlet propagation (dt=$(DT_TEST)s)"
	@echo "  make sgp4          - Generate SGP4 reference orbit"
	@echo "  make plots         - Generate comparison plots"
	@echo "  make analysis      - Run CGPD analysis for multiple timesteps"
	@echo "  make answer-sheet  - Generate answer-sheet.yaml"
	@echo "  make test          - Quick test run (compile + euler + verlet + plots)"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make clean-data    - Remove generated data files"
	@echo "  make clean-plots   - Remove generated plots"
	@echo "  make clean-all     - Remove everything (build + data + plots)"
	@echo ""
	@echo "Examples:"
	@echo "  make euler DT_TEST=300       - Run Euler with 300s timestep"
	@echo "  make analysis DT_CGPD='10 100 1000'  - Custom CGPD timesteps"
	@echo ""

# Compile Fortran programs
compile: $(BUILD_DIR)/propagate_orbit $(BUILD_DIR)/propagate_orbit_verlet

$(BUILD_DIR)/propagate_orbit: $(SRC_FORTRAN)/gravity.f90 $(SRC_FORTRAN)/euler_method.f90 $(SRC_FORTRAN)/propagate_orbit.f90
	@echo "Compiling Euler integrator..."
	@mkdir -p $(BUILD_DIR)
	$(FC) $(FFLAGS) -o $(BUILD_DIR)/propagate_orbit $(SRC_FORTRAN)/gravity.f90 $(SRC_FORTRAN)/euler_method.f90 $(SRC_FORTRAN)/propagate_orbit.f90 -J $(BUILD_DIR)
	@echo "✓ Euler compiled successfully"

$(BUILD_DIR)/propagate_orbit_verlet: $(SRC_FORTRAN)/gravity.f90 $(SRC_FORTRAN)/velocity_verlet.f90 $(SRC_FORTRAN)/propagate_orbit_verlet.f90
	@echo "Compiling Velocity Verlet integrator..."
	@mkdir -p $(BUILD_DIR)
	$(FC) $(FFLAGS) -o $(BUILD_DIR)/propagate_orbit_verlet $(SRC_FORTRAN)/gravity.f90 $(SRC_FORTRAN)/velocity_verlet.f90 $(SRC_FORTRAN)/propagate_orbit_verlet.f90 -J $(BUILD_DIR)
	@echo "✓ Velocity Verlet compiled successfully"

# Fetch TLE and generate SGP4 reference
sgp4:
	@echo "Generating SGP4 reference orbit..."
	@mkdir -p $(DATA_DIR)/sgp4_reference
	@if [ ! -f "$(DATA_DIR)/sgp4_reference/tle.txt" ]; then \
		echo "Fetching TLE data..."; \
		$(PYTHON) src/python/fetch_tle.py; \
	fi
	$(PYTHON) src/python/propagator_sgp4.py $(DT_TEST)
	@echo "✓ SGP4 reference generated"

# Extract initial state
$(DATA_DIR)/sgp4_reference/initial_state_dt$(DT_TEST)s.json: sgp4
	@echo "Extracting initial state for dt=$(DT_TEST)s..."
	$(PYTHON) src/python/extract_initial_state.py $(DT_TEST)

# Run Euler propagation
euler: compile $(DATA_DIR)/sgp4_reference/initial_state_dt$(DT_TEST)s.json
	@echo "Running Euler propagation with dt=$(DT_TEST)s..."
	@mkdir -p $(DATA_DIR)/euler_outputs
	cd $(BUILD_DIR) && ./propagate_orbit $(DATA_DIR)/../$(DATA_DIR)/sgp4_reference/initial_state_dt$(DT_TEST)s.json
	@if [ -f "$(BUILD_DIR)/euler_output.txt" ]; then \
		mv $(BUILD_DIR)/euler_output.txt $(DATA_DIR)/euler_outputs/dt$(DT_TEST)s_euler_output.txt; \
		echo "✓ Euler propagation complete: $(DATA_DIR)/euler_outputs/dt$(DT_TEST)s_euler_output.txt"; \
	fi

# Run Velocity Verlet propagation
verlet: compile $(DATA_DIR)/sgp4_reference/initial_state_dt$(DT_TEST)s.json
	@echo "Running Velocity Verlet propagation with dt=$(DT_TEST)s..."
	@mkdir -p $(DATA_DIR)/verlet_outputs
	cd $(BUILD_DIR) && ./propagate_orbit_verlet $(DATA_DIR)/../$(DATA_DIR)/sgp4_reference/initial_state_dt$(DT_TEST)s.json
	@if [ -f "$(BUILD_DIR)/verlet_output.txt" ]; then \
		mv $(BUILD_DIR)/verlet_output.txt $(DATA_DIR)/verlet_outputs/dt$(DT_TEST)s_verlet_output.txt; \
		echo "✓ Velocity Verlet propagation complete: $(DATA_DIR)/verlet_outputs/dt$(DT_TEST)s_verlet_output.txt"; \
	fi

# Generate comparison plots
plots:
	@echo "Generating comparison plots..."
	@mkdir -p $(PLOTS_DIR)/timestep_comparisons/dt$(DT_TEST)s
	@mkdir -p $(PLOTS_DIR)/timestep_comparisons_verlet/dt$(DT_TEST)s
	$(PYTHON) src/python/compute_position_difference.py $(DT_TEST)
	$(PYTHON) src/python/compute_position_difference_verlet.py $(DT_TEST)
	@echo "✓ Plots generated in $(PLOTS_DIR)/"

# Run comprehensive CGPD analysis
analysis:
	@echo "Running CGPD analysis for multiple timesteps..."
	@echo "Timesteps: $(DT_CGPD)"
	@for dt in $(DT_CGPD); do \
		echo "Processing dt=$${dt}s..."; \
		$(MAKE) sgp4 DT_TEST=$$dt -s; \
		$(MAKE) euler DT_TEST=$$dt -s; \
		$(MAKE) verlet DT_TEST=$$dt -s; \
		$(PYTHON) src/python/compute_position_difference.py $$dt 2>/dev/null || true; \
		$(PYTHON) src/python/compute_position_difference_verlet.py $$dt 2>/dev/null || true; \
	done
	@echo "Generating summary plots..."
	$(PYTHON) src/python/plot_cgpd_vs_timestep.py
	$(PYTHON) src/python/plot_cgpd_vs_timestep_verlet.py
	$(PYTHON) src/python/analyze_integration_timing.py
	@echo "✓ CGPD analysis complete"

# Generate answer sheet
answer-sheet:
	@echo "Generating answer-sheet.yaml..."
	$(PYTHON) generate_answer_sheet.py
	@echo "Validating answer sheet..."
	$(PYTHON) answer-sheet-sanity.py answer-sheet.yaml || true
	@echo "✓ Answer sheet generated"

# Quick test - compile and run with single timestep
test: compile
	@echo "Running quick test (dt=$(DT_TEST)s)..."
	$(MAKE) sgp4 DT_TEST=$(DT_TEST)
	$(MAKE) euler DT_TEST=$(DT_TEST)
	$(MAKE) verlet DT_TEST=$(DT_TEST)
	$(MAKE) plots DT_TEST=$(DT_TEST)
	@echo "✓ Test complete"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)/*.o $(BUILD_DIR)/*.mod
	rm -f $(BUILD_DIR)/propagate_orbit $(BUILD_DIR)/propagate_orbit_verlet
	@echo "✓ Build artifacts cleaned"

# Clean generated data files
clean-data:
	@echo "Cleaning generated data..."
	rm -rf $(DATA_DIR)/euler_outputs/*
	rm -rf $(DATA_DIR)/verlet_outputs/*
	rm -rf $(DATA_DIR)/position_differences/*
	rm -rf $(DATA_DIR)/position_differences_verlet/*
	rm -rf $(DATA_DIR)/summary/*
	@echo "✓ Data files cleaned (TLE and SGP4 reference preserved)"

# Clean generated plots
clean-plots:
	@echo "Cleaning generated plots..."
	rm -rf $(PLOTS_DIR)/timestep_comparisons/*
	rm -rf $(PLOTS_DIR)/timestep_comparisons_verlet/*
	rm -rf $(PLOTS_DIR)/combined_timesteps_euler/*
	rm -rf $(PLOTS_DIR)/combined_timesteps_verlet/*
	rm -rf $(PLOTS_DIR)/summary/*
	@echo "✓ Plots cleaned"

# Clean everything
clean-all: clean clean-data clean-plots
	@echo "✓ All generated files removed"

# Install Python dependencies
install-deps:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Run sanity check on answer sheet
validate:
	@echo "Validating answer-sheet.yaml..."
	$(PYTHON) answer-sheet-sanity.py answer-sheet.yaml
