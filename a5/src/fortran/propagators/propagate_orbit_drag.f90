program propagate_orbit_drag
    use gravity, only: dp, gravitational_acceleration
    use drag_perturbation
    use velocity_verlet_integrator_module
    implicit none
    
    real(dp) :: state0(6), dt, t_stop
    real(dp), allocatable :: t_array(:), state_array(:,:)
    integer :: n_steps, i, iostat
    character(len=256) :: input_file, output_file
    character(len=50) :: dt_str
    real(dp) :: start_time, end_time, integration_time
    
    ! Default parameters (can be modified)
    input_file = 'data/sgp4_reference/initial_state.txt'
    
    print *, "========================================"
    print *, "Orbit Propagation with Atmospheric Drag"
    print *, "========================================"
    print *, ""
    
    ! Read initial conditions and parameters from file
    print *, "Reading initial conditions from: ", trim(input_file)
    open(unit=10, file=input_file, status='old', action='read', iostat=iostat)
    
    if (iostat /= 0) then
        print *, "Error: Could not open file ", trim(input_file)
        print *, "Please create the file or run the Python script to generate it."
        stop
    end if
    
    ! Read parameters from file
    ! Expected format:
    ! Line 1: x y z (position in meters)
    ! Line 2: vx vy vz (velocity in m/s)
    ! Line 3: dt (time step in seconds)
    ! Line 4: t_stop (stop time in seconds)
    
    read(10, *, iostat=iostat) state0(1), state0(2), state0(3)
    if (iostat /= 0) then
        print *, "Error reading initial position"
        close(10)
        stop
    end if
    
    read(10, *, iostat=iostat) state0(4), state0(5), state0(6)
    if (iostat /= 0) then
        print *, "Error reading initial velocity"
        close(10)
        stop
    end if
    
    read(10, *, iostat=iostat) dt
    if (iostat /= 0) then
        print *, "Error reading time step"
        close(10)
        stop
    end if
    
    read(10, *, iostat=iostat) t_stop
    if (iostat /= 0) then
        print *, "Error reading stop time"
        close(10)
        stop
    end if
    
    close(10)
    
    print *, "Initial Conditions:"
    print *, "  Position [m]:  ", state0(1:3)
    print *, "  Velocity [m/s]:", state0(4:6)
    print *, ""
    print *, "Integration Parameters:"
    print *, "  Time step [s]:  ", dt
    print *, "  Stop time [s]:  ", t_stop
    print *, "  Duration [hrs]: ", t_stop / 3600.0_dp
    print *, ""
    print *, "Perturbations: Two-body + Atmospheric Drag only"
    print *, ""
    
    ! Atmospheric parameters
    print *, "Atmospheric Model:"
    print *, "  rho_0 = ", RHO_0, " kg/m^3"
    print *, "  H     = ", H_SCALE/1000.0_dp, " km"
    print *, "  B     = ", BALLISTIC_COEFF, " m^2/kg"
    print *, ""
    
    ! Call Velocity Verlet integrator with combined acceleration function
    print *, "Propagating orbit with atmospheric drag..."
    
    ! Start timing
    call cpu_time(start_time)
    call velocity_verlet_integrate_rv(state0, dt, t_stop, total_acceleration_drag, t_array, state_array, n_steps)
    call cpu_time(end_time)
    
    ! Calculate integration time
    integration_time = end_time - start_time
    
    print *, "Integration complete!"
    print *, "  Total steps: ", n_steps
    print *, "  Integration time: ", integration_time, " seconds"
    print *, "  Time per step: ", integration_time / real(n_steps, dp) * 1000.0_dp, " ms"
    print *, ""
    
    ! Create data directory if it doesn't exist
    call system('mkdir -p data/outputs_drag')
    
    ! Create filename with timestep at the beginning
    write(dt_str, '(I0)') nint(dt)
    output_file = 'data/outputs_drag/dt' // trim(adjustl(dt_str)) // 's_drag_output.txt'
    
    ! Save results to output file
    open(unit=20, file=trim(output_file), status='replace', action='write', iostat=iostat)
    if (iostat /= 0) then
        print *, "Warning: Could not create output file in data/outputs_drag/ directory"
        print *, "Attempting to write to current directory..."
        output_file = 'dt' // trim(adjustl(dt_str)) // 's_drag_output.txt'
        open(unit=20, file=trim(output_file), status='replace', action='write')
    end if
    
    print *, "Saving results to: ", trim(output_file)
    
    ! Write header
    write(20, '(A)') '# Orbit Propagation Results - Atmospheric Drag Perturbation'
    write(20, '(A, F15.2)') '# Time step (s): ', dt
    write(20, '(A, F15.2)') '# Stop time (s): ', t_stop
    write(20, '(A, I0)') '# Number of steps: ', n_steps
    write(20, '(A, F15.6)') '# Integration time (s): ', integration_time
    write(20, '(A, F15.9)') '# Time per step (ms): ', integration_time / real(n_steps, dp) * 1000.0_dp
    write(20, '(A)') '# Columns: time(s) x(m) y(m) z(m) vx(m/s) vy(m/s) vz(m/s)'
    
    ! Write data
    do i = 1, n_steps
        write(20, '(F15.2, 6(ES25.16E3))') t_array(i), state_array(:, i)
    end do
    
    close(20)
    
    print *, "Results saved successfully!"
    print *, ""
    
    ! Clean up
    deallocate(t_array)
    deallocate(state_array)

contains

    ! Acceleration function combining two-body gravity and atmospheric drag
    function total_acceleration_drag(r, v) result(a)
        real(dp), intent(in) :: r(3), v(3)
        real(dp) :: a(3)
        
        ! Combine two-body gravity and atmospheric drag
        a = gravitational_acceleration(r) + drag_acceleration(r, v)
    end function total_acceleration_drag

end program propagate_orbit_drag

