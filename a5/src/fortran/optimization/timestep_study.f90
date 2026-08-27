program timestep_study
    use gravity, only: dp, gravitational_acceleration
    use j2_perturbation, only: j2_acceleration
    use drag_perturbation, only: drag_acceleration
    use srp_perturbation, only: srp_acceleration
    use third_body_perturbation, only: third_body_acceleration, load_third_body_positions
    use velocity_verlet_integrator_module
    use objective_function
    use gradient_descent_mod
    use timestep_control_mod
    implicit none
    
    !============================================================================
    ! Study optimization performance as a function of integration time step
    !============================================================================
    
    ! Perturbation toggles
    logical, parameter :: ENABLE_J2 = .true.
    logical, parameter :: ENABLE_DRAG = .false.
    logical, parameter :: ENABLE_SRP = .true.
    logical, parameter :: ENABLE_THIRD_BODY = .true.
    
    ! Optimization parameters (middle ground convergence criteria)
    real(dp), parameter :: LEARNING_RATE = 5.0e-4_dp
    real(dp), parameter :: TOLERANCE_GRAD = 5.0e-7_dp  ! Gradient norm tolerance (middle ground)
    real(dp), parameter :: TOLERANCE_CGPD = 0.7_dp     ! CGPD improvement tolerance [m] (middle ground)
    integer, parameter :: MAX_ITERATIONS = 50000       ! Maximum iterations
    integer, parameter :: PATIENCE = 100               ! Early stop if no improvement for 100 iterations
    
    ! Time step study parameters
    integer, parameter :: N_TIMESTEPS = 10
    real(dp), parameter :: N_STEPS_MIN = 10.0_dp      ! minimum number of steps
    real(dp), parameter :: N_STEPS_MAX = 400.0_dp   ! maximum number of steps
    
    ! Variables
    real(dp) :: r0(3), v0(3), dt_nominal, t_stop
    real(dp) :: delta_y0_init(6), delta_y0_opt(6)
    real(dp) :: cgpd_opt
    integer :: n_iterations, i, j
    logical :: converged, early_stopped
    real(dp), allocatable :: history_x(:,:), history_f(:)
    real(dp) :: start_time, end_time, total_time, avg_time_per_iter
    real(dp) :: best_cgpd
    integer :: iterations_no_improvement
    integer :: out_unit
    real(dp) :: dt_test, dt_values(N_TIMESTEPS)
    
    print *, ''
    print *, '========================================'
    print *, 'Time Step Sensitivity Study'
    print *, '========================================'
    print *, ''
    print *, 'Testing', N_TIMESTEPS, 'different numbers of steps'
    print *, 'Range:', int(N_STEPS_MIN), 'to', int(N_STEPS_MAX), 'steps'
    print *, ''
    
    ! Load third body positions
    call load_third_body_positions()
    
    ! Load SGP4 reference
    call load_sgp4_reference('../../../data/sgp4_reference/sgp4_orbit.txt')
    
    ! Read initial state
    call read_initial_state('../../../data/sgp4_reference/initial_state.txt', &
                           r0, v0, dt_nominal, t_stop)
    
    print *, 'Nominal time step:', dt_nominal, 's'
    print *, 'Propagation time:', t_stop, 's (', t_stop/3600.0_dp, 'hours)'
    print *, ''
    
    ! Generate logarithmic spacing for number of steps
    ! Then compute time step as dt = t_stop / n_steps
    do i = 1, N_TIMESTEPS
        ! Log spacing for number of steps
        dt_values(i) = t_stop / (N_STEPS_MIN * (N_STEPS_MAX/N_STEPS_MIN)**((i-1.0_dp)/(N_TIMESTEPS-1.0_dp)))
    end do
    
    ! Open output file
    open(newunit=out_unit, file='../../../data/outputs_all/timestep_study.txt', &
         status='replace', action='write')
    
    write(out_unit, '(A)') '# Time step sensitivity study (varying number of steps)'
    write(out_unit, '(A,ES12.4)') '# Propagation time [s]: ', t_stop
    write(out_unit, '(A)') '#'
    write(out_unit, '(A)') '# Columns: TimeStep[s] NumSteps TotalTime[s] Iterations AvgTimePerIter[s] '// &
                           'FinalCGPD[m] Converged'
    
    ! Initialize delta
    delta_y0_init = 0.0_dp
    
    print *, '========================================'
    print *, 'Running Optimizations'
    print *, '========================================'
    print *, ''
    
    ! Test each time step
    do i = 1, N_TIMESTEPS
        dt_test = dt_values(i)
        
        print '(A,I2,A,I2,A,F8.4,A,I6,A)', 'Test ', i, ' of ', N_TIMESTEPS, ': dt = ', dt_test, ' s (', &
              nint(t_stop/dt_test), ' steps)'
        
        ! Set global time step for this test
        call set_global_params(dt_test, t_stop, r0, v0)
        
        ! Run optimization
        call cpu_time(start_time)
        
        call gradient_descent_adaptive(objective_wrapper, delta_y0_init, delta_y0_opt, &
                                       cgpd_opt, n_iterations, converged, &
                                       history_x, history_f, &
                                       LEARNING_RATE, TOLERANCE_GRAD, MAX_ITERATIONS)
        
        call cpu_time(end_time)
        total_time = end_time - start_time
        
        ! Check for early stopping (iterations without improvement)
        best_cgpd = history_f(1)
        iterations_no_improvement = 0
        early_stopped = .false.
        do j = 2, n_iterations
            if (history_f(j) < best_cgpd - TOLERANCE_CGPD) then
                best_cgpd = history_f(j)
                iterations_no_improvement = 0
            else
                iterations_no_improvement = iterations_no_improvement + 1
                if (iterations_no_improvement >= PATIENCE) then
                    early_stopped = .true.
                    exit
                end if
            end if
        end do
        
        avg_time_per_iter = total_time / real(n_iterations, dp)
        
        ! Print results
        print '(A,I4,A,F10.3,A,A,F10.6,A,A,F10.3,A)', &
              '  Iterations: ', n_iterations, &
              ', Total time: ', total_time, ' s', &
              ', Avg per iter: ', avg_time_per_iter, ' s', &
              ', CGPD: ', cgpd_opt, ' m'
        
        ! Write to file
        write(out_unit, '(F12.6,2X,I8,2X,F12.6,2X,I5,2X,F12.6,2X,F15.6,2X,L1)') &
              dt_test, nint(t_stop/dt_test), total_time, n_iterations, avg_time_per_iter, cgpd_opt, converged
        
        ! Clean up
        if (allocated(history_x)) deallocate(history_x)
        if (allocated(history_f)) deallocate(history_f)
        
        print *, ''
    end do
    
    close(out_unit)
    
    print *, '========================================'
    print *, 'Study Complete'
    print *, '========================================'
    print *, ''
    print *, 'Results saved to: data/outputs_all/timestep_study.txt'
    print *, ''
    
    call cleanup_sgp4_reference()
    
contains
    
    !============================================================================
    ! Read initial state from file
    !============================================================================
    subroutine read_initial_state(filename, r0, v0, dt, t_stop)
        character(len=*), intent(in) :: filename
        real(dp), intent(out) :: r0(3), v0(3), dt, t_stop
        integer :: unit_num, ios
        
        open(newunit=unit_num, file=filename, status='old', action='read', iostat=ios)
        if (ios /= 0) then
            print *, 'Error: Could not open file:', trim(filename)
            stop 1
        end if
        
        read(unit_num, *) r0(1), r0(2), r0(3)
        read(unit_num, *) v0(1), v0(2), v0(3)
        read(unit_num, *) dt
        read(unit_num, *) t_stop
        
        close(unit_num)
    end subroutine read_initial_state
    
    !============================================================================
    ! Objective function wrapper
    !============================================================================
    function objective_wrapper(delta_y0) result(cgpd)
        use timestep_control_mod
        real(dp), intent(in) :: delta_y0(6)
        real(dp) :: cgpd
        real(dp) :: r_current(3), v_current(3)
        real(dp) :: t_current, dt_current
        integer :: step, max_steps
        real(dp), allocatable :: positions(:,:)
        
        max_steps = ceiling(global_tstop / global_dt) + 10
        allocate(positions(3, max_steps))
        
        r_current = global_r0 + delta_y0(1:3)
        v_current = global_v0 + delta_y0(4:6)
        
        t_current = 0.0_dp
        step = 0
        
        do while (t_current < global_tstop)
            step = step + 1
            positions(:, step) = r_current
            
            dt_current = min(global_dt, global_tstop - t_current)
            
            call velocity_verlet_step(r_current, v_current, dt_current)
            
            t_current = t_current + global_dt
        end do
        
        cgpd = compute_cgpd(positions, step)
        
        deallocate(positions)
        
    end function objective_wrapper
    
    !============================================================================
    ! Velocity Verlet integration step
    !============================================================================
    subroutine velocity_verlet_step(r, v, dt)
        real(dp), intent(inout) :: r(3), v(3)
        real(dp), intent(in) :: dt
        real(dp) :: a1(3), a2(3)
        
        a1 = total_acceleration(r, v)
        r = r + v * dt + 0.5_dp * a1 * dt**2
        a2 = total_acceleration(r, v)
        v = v + 0.5_dp * (a1 + a2) * dt
        
    end subroutine velocity_verlet_step
    
    !============================================================================
    ! Total acceleration
    !============================================================================
    function total_acceleration(r, v) result(a)
        real(dp), intent(in) :: r(3), v(3)
        real(dp) :: a(3)
        
        a = gravitational_acceleration(r)
        
        if (ENABLE_J2) a = a + j2_acceleration(r)
        if (ENABLE_DRAG) a = a + drag_acceleration(r, v)
        if (ENABLE_SRP) a = a + srp_acceleration(r)
        if (ENABLE_THIRD_BODY) a = a + third_body_acceleration(r)
        
    end function total_acceleration
    
end program timestep_study
