program test_objective_function
    use gravity, only: dp, gravitational_acceleration
    use j2_perturbation, only: j2_acceleration
    use drag_perturbation, only: drag_acceleration
    use srp_perturbation, only: srp_acceleration
    use third_body_perturbation, only: third_body_acceleration, load_third_body_positions
    use velocity_verlet_integrator_module
    use objective_function
    implicit none
    
    !============================================================================
    ! PERTURBATION TOGGLES - Set to .true. to enable, .false. to disable
    !============================================================================
    logical, parameter :: ENABLE_J2 = .true.           ! J2 oblateness perturbation
    logical, parameter :: ENABLE_DRAG = .false.        ! Atmospheric drag
    logical, parameter :: ENABLE_SRP = .false.         ! Solar radiation pressure
    logical, parameter :: ENABLE_THIRD_BODY = .false.  ! Third body (Sun + Moon)
    !============================================================================
    
    real(dp) :: state0(6), dt, t_stop
    real(dp) :: delta_state(6)  ! Perturbation to initial state
    real(dp) :: perturbed_state(6)
    real(dp), allocatable :: t_array(:), state_array(:,:)
    integer :: n_steps, i, iostat
    character(len=256) :: input_file, sgp4_file
    real(dp) :: cgpd_value
    real(dp) :: start_time, end_time
    
    ! File paths (relative to workspace root when run from build/)
    input_file = '../../../data/sgp4_reference/initial_state.txt'
    sgp4_file = '../../../data/sgp4_reference/sgp4_orbit.txt'
    
    print *, "========================================"
    print *, "Objective Function Test"
    print *, "========================================"
    print *, ""
    
    ! Load third body positions if enabled
    if (ENABLE_THIRD_BODY) then
        print *, "Loading third body positions..."
        call load_third_body_positions()
        print *, "  Third body data loaded"
        print *, ""
    end if
    
    ! Load SGP4 reference orbit
    print *, "Loading SGP4 reference orbit from: ", trim(sgp4_file)
    call load_sgp4_reference(sgp4_file)
    print *, ""
    
    ! Read initial conditions from file
    print *, "Reading initial conditions from: ", trim(input_file)
    open(unit=10, file=input_file, status='old', action='read', iostat=iostat)
    
    if (iostat /= 0) then
        print *, "Error: Could not open file ", trim(input_file)
        stop
    end if
    
    read(10, *) state0(1), state0(2), state0(3)
    read(10, *) state0(4), state0(5), state0(6)
    read(10, *) dt
    read(10, *) t_stop
    close(10)
    
    print *, "Initial state:"
    print *, "  Position [m]:  ", state0(1:3)
    print *, "  Velocity [m/s]:", state0(4:6)
    print *, "  dt [s]:        ", dt
    print *, "  t_stop [s]:    ", t_stop
    print *, ""
    
    ! Test 1: Compute CGPD with zero perturbation (delta_y0 = 0)
    print *, "========================================"
    print *, "Test 1: CGPD with delta_y0 = 0"
    print *, "========================================"
    delta_state = 0.0_dp
    
    call cpu_time(start_time)
    cgpd_value = objective_function_eval(delta_state)
    call cpu_time(end_time)
    
    print *, "CGPD (delta_y0 = 0): ", cgpd_value, " m"
    print *, "Computation time: ", end_time - start_time, " s"
    print *, ""
    
    ! Test 2: Compute CGPD with small position perturbation
    print *, "========================================"
    print *, "Test 2: CGPD with delta_r = [10, 0, 0] m"
    print *, "========================================"
    delta_state = 0.0_dp
    delta_state(1) = 10.0_dp  ! 10 m perturbation in x
    
    call cpu_time(start_time)
    cgpd_value = objective_function_eval(delta_state)
    call cpu_time(end_time)
    
    print *, "CGPD: ", cgpd_value, " m"
    print *, "Computation time: ", end_time - start_time, " s"
    print *, ""
    
    ! Test 3: Compute CGPD with small velocity perturbation
    print *, "========================================"
    print *, "Test 3: CGPD with delta_v = [0, 0, 0.1] m/s"
    print *, "========================================"
    delta_state = 0.0_dp
    delta_state(6) = 0.1_dp  ! 0.1 m/s perturbation in z
    
    call cpu_time(start_time)
    cgpd_value = objective_function_eval(delta_state)
    call cpu_time(end_time)
    
    print *, "CGPD: ", cgpd_value, " m"
    print *, "Computation time: ", end_time - start_time, " s"
    print *, ""
    
    ! Cleanup
    call cleanup_sgp4_reference()
    
    print *, "========================================"
    print *, "Tests Complete"
    print *, "========================================"

contains

    !========================================================================
    ! Objective function: Evaluates CGPD for a given perturbation
    ! Input: delta_y0(6) - perturbation to initial state vector
    ! Output: CGPD value in meters
    !========================================================================
    function objective_function_eval(delta_y0) result(cgpd)
        real(dp), intent(in) :: delta_y0(6)
        real(dp) :: cgpd
        
        real(dp) :: perturbed_state0(6)
        real(dp), allocatable :: t_arr(:), state_arr(:,:)
        integer :: n_steps_local
        
        ! Apply perturbation to initial state
        perturbed_state0 = state0 + delta_y0
        
        ! Propagate orbit with perturbed initial state
        if (ENABLE_DRAG) then
            call velocity_verlet_integrate_rv(perturbed_state0, dt, t_stop, &
                                              total_acceleration_rv, t_arr, state_arr, n_steps_local)
        else
            call velocity_verlet_integrate(perturbed_state0, dt, t_stop, &
                                           total_acceleration, t_arr, state_arr, n_steps_local)
        end if
        
        ! Compute CGPD between integrated and SGP4 orbits
        cgpd = compute_cgpd(state_arr(1:3, :), n_steps_local)
        
        ! Cleanup
        deallocate(t_arr)
        deallocate(state_arr)
        
    end function objective_function_eval
    
    !========================================================================
    ! Acceleration function combining selected perturbations (position-only)
    !========================================================================
    function total_acceleration(r) result(a)
        real(dp), intent(in) :: r(3)
        real(dp) :: a(3)
        
        a = gravitational_acceleration(r)
        
        if (ENABLE_J2) then
            a = a + j2_acceleration(r)
        end if
        
        if (ENABLE_SRP) then
            a = a + srp_acceleration(r)
        end if
        
        if (ENABLE_THIRD_BODY) then
            a = a + third_body_acceleration(r)
        end if
        
    end function total_acceleration
    
    !========================================================================
    ! Acceleration function with drag (position and velocity)
    !========================================================================
    function total_acceleration_rv(r, v) result(a)
        real(dp), intent(in) :: r(3), v(3)
        real(dp) :: a(3)
        
        a = gravitational_acceleration(r)
        
        if (ENABLE_J2) then
            a = a + j2_acceleration(r)
        end if
        
        if (ENABLE_DRAG) then
            a = a + drag_acceleration(r, v)
        end if
        
        if (ENABLE_SRP) then
            a = a + srp_acceleration(r)
        end if
        
        if (ENABLE_THIRD_BODY) then
            a = a + third_body_acceleration(r)
        end if
        
    end function total_acceleration_rv
    
end program test_objective_function
