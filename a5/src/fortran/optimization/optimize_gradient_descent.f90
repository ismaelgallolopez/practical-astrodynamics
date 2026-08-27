program optimize_initial_state
    use gravity, only: dp, gravitational_acceleration
    use j2_perturbation, only: j2_acceleration
    use drag_perturbation, only: drag_acceleration
    use srp_perturbation, only: srp_acceleration
    use third_body_perturbation, only: third_body_acceleration, load_third_body_positions
    use velocity_verlet_integrator_module
    use objective_function
    use gradient_descent_mod
    implicit none
    
    !============================================================================
    ! PERTURBATION TOGGLES - Set to .true. to enable, .false. to disable
    !============================================================================
    logical, parameter :: ENABLE_J2 = .true.           ! J2 oblateness perturbation
    logical, parameter :: ENABLE_DRAG = .false.        ! Atmospheric drag
    logical, parameter :: ENABLE_SRP = .true.          ! Solar radiation pressure
    logical, parameter :: ENABLE_THIRD_BODY = .true.   ! Third body (Sun + Moon)
    !============================================================================
    
    !============================================================================
    ! OPTIMIZATION PARAMETERS
    !============================================================================
    real(dp), parameter :: LEARNING_RATE = 5.0e-4_dp   ! Gradient descent learning rate (optimized)
    real(dp), parameter :: TOLERANCE_GRAD = 5.0e-7_dp  ! Gradient norm tolerance (middle ground)
    real(dp), parameter :: TOLERANCE_CGPD = 0.7_dp     ! CGPD improvement tolerance [m] (middle ground)
    integer, parameter :: MAX_ITERATIONS = 50000       ! Maximum optimization iterations
    integer, parameter :: PATIENCE = 100               ! Max iterations without improvement before early stop
    real(dp), parameter :: INITIAL_PERTURBATION = 0.0_dp  ! No initial perturbation - start from nominal state
    !============================================================================
    
    real(dp) :: state0(6), dt, t_stop
    real(dp) :: delta_y0_initial(6), delta_y0_optimal(6)
    real(dp) :: cgpd_initial, cgpd_optimal
    integer :: n_iterations, iostat, i
    logical :: converged
    character(len=256) :: input_file, sgp4_file, output_file
    real(dp), allocatable :: history_x(:,:), history_f(:)
    real(dp) :: start_time, end_time, total_time
    integer :: iterations_no_improvement, best_iteration
    real(dp) :: best_cgpd
    logical :: early_stopped
    
    ! File paths
    input_file = '../../../data/sgp4_reference/initial_state.txt'
    sgp4_file = '../../../data/sgp4_reference/sgp4_orbit.txt'
    
    print *, "========================================"
    print *, "Gradient-Based Orbit Optimization"
    print *, "========================================"
    print *, ""
    
    ! Display perturbation configuration
    print *, "Perturbation Configuration:"
    print *, "  Two-body gravity:       ALWAYS ENABLED"
    if (ENABLE_J2) print *, "  J2 oblateness:          ENABLED"
    if (ENABLE_DRAG) print *, "  Atmospheric drag:       ENABLED"
    if (ENABLE_SRP) print *, "  Solar radiation press.: ENABLED"
    if (ENABLE_THIRD_BODY) print *, "  Third body (Sun+Moon):  ENABLED"
    print *, ""
    
    ! Load third body positions if enabled
    if (ENABLE_THIRD_BODY) then
        print *, "Loading third body positions..."
        call load_third_body_positions()
        print *, ""
    end if
    
    ! Load SGP4 reference orbit
    print *, "Loading SGP4 reference orbit from: ", trim(sgp4_file)
    call load_sgp4_reference(sgp4_file)
    print *, ""
    
    ! Read initial conditions
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
    print *, "  t_stop [s]:    ", t_stop, " (", t_stop/3600.0_dp, " hours)"
    print *, ""
    
    ! Optimization parameters
    print *, "Optimization Parameters:"
    print *, "  Algorithm:         Adaptive Gradient Descent (with momentum)"
    print *, "  Learning rate:     ", LEARNING_RATE
    print *, "  Gradient tolerance:", TOLERANCE_GRAD
    print *, "  CGPD tolerance:    ", TOLERANCE_CGPD, " m"
    print *, "  Max iterations:    ", MAX_ITERATIONS
    print *, "  Patience:          ", PATIENCE, " iterations"
    print *, "  Init. perturbation:", INITIAL_PERTURBATION, " m, m/s"
    print *, ""
    
    ! Compute initial CGPD (with delta_y0 = 0)
    print *, "========================================"
    print *, "Computing Initial CGPD"
    print *, "========================================"
    delta_y0_initial = 0.0_dp
    cgpd_initial = objective_function_eval(delta_y0_initial)
    print *, "CGPD (delta_y0 = 0): ", cgpd_initial, " m"
    print *, ""
    
    ! Add small random perturbation to avoid starting at saddle point or local minimum
    ! This helps the optimizer find a direction to improve
    if (INITIAL_PERTURBATION > 0.0_dp) then
        call random_seed()
        call random_number(delta_y0_initial)
        ! Scale to [-INITIAL_PERTURBATION, +INITIAL_PERTURBATION]
        delta_y0_initial = (delta_y0_initial - 0.5_dp) * 2.0_dp * INITIAL_PERTURBATION
        print *, "Starting with random perturbation:"
        print *, "  Position [m]:  ", delta_y0_initial(1:3)
        print *, "  Velocity [m/s]:", delta_y0_initial(4:6)
        print *, ""
    end if
    
    ! Run optimization
    print *, "========================================"
    print *, "Running Optimization"
    print *, "========================================"
    print *, ""
    
    call cpu_time(start_time)
    
    ! Use adaptive gradient descent (momentum-based)
    ! Note: gradient_descent uses gradient norm tolerance, not CGPD tolerance
    ! The CGPD tolerance check is built into the adaptive version
    call gradient_descent_adaptive(objective_function_eval, delta_y0_initial, &
                         delta_y0_optimal, cgpd_optimal, n_iterations, converged, &
                         history_x, history_f, &
                         learning_rate_in=LEARNING_RATE, &
                         tolerance_in=TOLERANCE_GRAD, &
                         max_iter_in=MAX_ITERATIONS)
    
    call cpu_time(end_time)
    total_time = end_time - start_time
    
    ! Check for early stopping (iterations without improvement)
    best_cgpd = history_f(1)
    best_iteration = 1
    iterations_no_improvement = 0
    early_stopped = .false.
    
    do i = 2, n_iterations
        if (history_f(i) < best_cgpd - TOLERANCE_CGPD) then
            ! Significant improvement found
            best_cgpd = history_f(i)
            best_iteration = i
            iterations_no_improvement = 0
        else
            ! No significant improvement
            iterations_no_improvement = iterations_no_improvement + 1
            if (iterations_no_improvement >= PATIENCE) then
                early_stopped = .true.
                exit
            end if
        end if
    end do
    
    print *, "Optimization complete!"
    print *, "  Iterations:          ", n_iterations
    print *, "  Converged:           ", converged
    print *, "  Early stopped:       ", early_stopped
    if (early_stopped) then
        print *, "  Reason:              No improvement for ", PATIENCE, " iterations"
        print *, "  Last improvement at: Iteration ", best_iteration
    end if
    print *, "  Total time [s]:      ", total_time
    print *, "  Time per iter:       ", total_time / real(n_iterations, dp), " s"
    print *, ""
    
    ! Display results
    print *, "========================================"
    print *, "Optimization Results"
    print *, "========================================"
    print *, ""
    print *, "Initial CGPD:       ", cgpd_initial, " m"
    print *, "Optimized CGPD:     ", cgpd_optimal, " m"
    print *, "Improvement:        ", cgpd_initial - cgpd_optimal, " m"
    print *, "Reduction:          ", 100.0_dp * (cgpd_initial - cgpd_optimal) / cgpd_initial, " %"
    print *, ""
    print *, "Optimal delta_y0:"
    print *, "  Position [m]:  ", delta_y0_optimal(1:3)
    print *, "  Velocity [m/s]:", delta_y0_optimal(4:6)
    print *, ""
    
    ! Save convergence history
    output_file = '../../../data/outputs_all/convergence_history.txt'
    call system('mkdir -p ../../../data/outputs_all')
    
    open(unit=20, file=output_file, status='replace', action='write')
    write(20, '(A)') '# Gradient Descent Convergence History'
    write(20, '(A, I0)') '# Total iterations: ', n_iterations
    write(20, '(A, L1)') '# Converged: ', converged
    write(20, '(A, L1)') '# Early stopped: ', early_stopped
    if (early_stopped) then
        write(20, '(A, I0)') '# Best iteration: ', best_iteration
        write(20, '(A, F15.6)') '# Best CGPD [m]: ', best_cgpd
    end if
    write(20, '(A, F15.6)') '# Total time [s]: ', total_time
    write(20, '(A)') '# Columns: iteration CGPD[m] dx[m] dy[m] dz[m] dvx[m/s] dvy[m/s] dvz[m/s]'
    
    do i = 1, n_iterations
        write(20, '(I6, 7(ES20.12))') i, history_f(i), history_x(:, i)
    end do
    close(20)
    
    print *, "Convergence history saved to: ", trim(output_file)
    print *, ""
    
    ! Save optimized initial state
    output_file = '../../../data/outputs_all/optimized_initial_state.txt'
    open(unit=21, file=output_file, status='replace', action='write')
    
    ! Optimized initial state = nominal + delta_y0_optimal
    write(21, '(3(ES23.15))') state0(1:3) + delta_y0_optimal(1:3)
    write(21, '(3(ES23.15))') state0(4:6) + delta_y0_optimal(4:6)
    write(21, '(ES23.15)') dt
    write(21, '(ES23.15)') t_stop
    close(21)
    
    print *, "Optimized initial state saved to: ", trim(output_file)
    print *, ""
    
    ! Display first few iterations
    print *, "Convergence History (first 10 iterations):"
    print *, "  Iter     CGPD [m]    Improvement [m]  No-Improve"
    iterations_no_improvement = 0
    best_cgpd = history_f(1)
    do i = 1, min(10, n_iterations)
        if (i == 1) then
            print '(I6, F15.3, A)', i, history_f(i), "         --              0"
        else
            if (history_f(i) < best_cgpd - TOLERANCE_CGPD) then
                best_cgpd = history_f(i)
                iterations_no_improvement = 0
            else
                iterations_no_improvement = iterations_no_improvement + 1
            end if
            print '(I6, F15.3, F15.3, I11)', i, history_f(i), history_f(i-1) - history_f(i), &
                  iterations_no_improvement
        end if
    end do
    if (n_iterations > 10) then
        print *, "  ..."
        ! Recompute for last iteration
        iterations_no_improvement = 0
        best_cgpd = history_f(1)
        do i = 2, n_iterations
            if (history_f(i) < best_cgpd - TOLERANCE_CGPD) then
                best_cgpd = history_f(i)
                iterations_no_improvement = 0
            else
                iterations_no_improvement = iterations_no_improvement + 1
            end if
        end do
        print '(I6, F15.3, F15.3, I11)', n_iterations, history_f(n_iterations), &
               history_f(n_iterations-1) - history_f(n_iterations), iterations_no_improvement
    end if
    
    ! Find best iteration (minimum CGPD)
    print *, ""
    print *, "Best CGPD achieved at iteration:", minloc(history_f(1:n_iterations))
    print *, "Best CGPD value: ", minval(history_f(1:n_iterations)), " m"
    print *, ""
    
    ! Cleanup
    deallocate(history_x, history_f)
    call cleanup_sgp4_reference()
    
    print *, "========================================"
    print *, "Optimization Complete"
    print *, "========================================"

contains

    !========================================================================
    ! Objective function wrapper for optimization
    !========================================================================
    function objective_function_eval(delta_y0) result(cgpd)
        real(dp), intent(in) :: delta_y0(6)
        real(dp) :: cgpd
        
        real(dp) :: perturbed_state0(6)
        real(dp), allocatable :: t_arr(:), state_arr(:,:)
        integer :: n_steps_local
        real(dp) :: delta_magnitude_pos, delta_magnitude_vel
        
        ! Check magnitude of perturbation (for diagnostics/bounds checking)
        delta_magnitude_pos = sqrt(delta_y0(1)**2 + delta_y0(2)**2 + delta_y0(3)**2)
        delta_magnitude_vel = sqrt(delta_y0(4)**2 + delta_y0(5)**2 + delta_y0(6)**2)
        
        ! Optional: Warn if perturbation is very large (sanity check)
        ! Uncomment for debugging:
        ! if (delta_magnitude_pos > 1000.0_dp .or. delta_magnitude_vel > 10.0_dp) then
        !     print *, "WARNING: Large perturbation - pos:", delta_magnitude_pos, " m, vel:", delta_magnitude_vel, " m/s"
        ! end if
        
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
        
        ! Compute CGPD
        cgpd = compute_cgpd(state_arr(1:3, :), n_steps_local)
        
        ! Cleanup
        deallocate(t_arr, state_arr)
        
    end function objective_function_eval
    
    !========================================================================
    ! Acceleration functions
    !========================================================================
    function total_acceleration(r) result(a)
        real(dp), intent(in) :: r(3)
        real(dp) :: a(3)
        
        a = gravitational_acceleration(r)
        if (ENABLE_J2) a = a + j2_acceleration(r)
        if (ENABLE_SRP) a = a + srp_acceleration(r)
        if (ENABLE_THIRD_BODY) a = a + third_body_acceleration(r)
    end function total_acceleration
    
    function total_acceleration_rv(r, v) result(a)
        real(dp), intent(in) :: r(3), v(3)
        real(dp) :: a(3)
        
        a = gravitational_acceleration(r)
        if (ENABLE_J2) a = a + j2_acceleration(r)
        if (ENABLE_DRAG) a = a + drag_acceleration(r, v)
        if (ENABLE_SRP) a = a + srp_acceleration(r)
        if (ENABLE_THIRD_BODY) a = a + third_body_acceleration(r)
    end function total_acceleration_rv
    
end program optimize_initial_state
