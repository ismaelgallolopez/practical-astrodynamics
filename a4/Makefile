# Fortran compiler and flags
FC = gfortran
FFLAGS = -O2
MODDIR = src/fortran/build
BUILDDIR = src/fortran/build

# Compiler flags for module directory
MODFLAGS = -J$(MODDIR) -I$(MODDIR)

# Source files
SRC_DIR = src/fortran
COMMON_SOURCES = $(SRC_DIR)/gravity.f90 $(SRC_DIR)/velocity_verlet.f90
J2_SOURCE = $(SRC_DIR)/j2_perturbation.f90
SRP_SOURCE = $(SRC_DIR)/srp_perturbation.f90
DRAG_SOURCE = $(SRC_DIR)/drag_perturbation.f90

# Executables
EXEC_TWOBODY = $(BUILDDIR)/propagate_orbit
EXEC_J2 = $(BUILDDIR)/propagate_orbit_oblateness
EXEC_SRP = $(BUILDDIR)/propagate_orbit_srp
EXEC_DRAG = $(BUILDDIR)/propagate_orbit_drag

# Default target
all: $(EXEC_TWOBODY) $(EXEC_J2) $(EXEC_SRP) $(EXEC_DRAG)

# Two-body orbit propagation
$(EXEC_TWOBODY): $(COMMON_SOURCES) $(SRC_DIR)/propagate_orbit.f90
	@mkdir -p $(BUILDDIR)
	$(FC) $(FFLAGS) $(MODFLAGS) -o $@ $^

# J2 oblateness propagation
$(EXEC_J2): $(COMMON_SOURCES) $(J2_SOURCE) $(SRC_DIR)/propagate_orbit_oblateness.f90
	@mkdir -p $(BUILDDIR)
	$(FC) $(FFLAGS) $(MODFLAGS) -o $@ $^

# SRP propagation
$(EXEC_SRP): $(COMMON_SOURCES) $(SRP_SOURCE) $(SRC_DIR)/propagate_orbit_srp.f90
	@mkdir -p $(BUILDDIR)
	$(FC) $(FFLAGS) $(MODFLAGS) -o $@ $^

# Drag propagation
$(EXEC_DRAG): $(COMMON_SOURCES) $(DRAG_SOURCE) $(SRC_DIR)/propagate_orbit_drag.f90
	@mkdir -p $(BUILDDIR)
	$(FC) $(FFLAGS) $(MODFLAGS) -o $@ $^

# Clean build artifacts
clean:
	rm -f $(BUILDDIR)/*.mod $(BUILDDIR)/*.o $(EXEC_TWOBODY) $(EXEC_J2) $(EXEC_SRP) $(EXEC_DRAG)

# Phony targets
.PHONY: all clean
