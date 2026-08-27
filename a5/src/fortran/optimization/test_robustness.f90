program test_optimization_robustness
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
    ! Test optimization robustness with different initial states
    !============================================================================
    
    ! Perturbation toggles
    logical, parameter :: ENABLE_J2 = .true.
    logical, parameter :: ENABLE_DRAG = .false.
    logical, parameter :: ENABLE_SRP = .true.
    logical, parameter :: ENABLE_THIRD_BODY = .true.
    
    ! Optimization parameters
    real(dp), parameter :: LEARNING_RATE = 5.0e-5_dp
    real(dp), parameter :: TOLERANCE = 0.1_dp
    integer, parameter :: MAX_ITERATIONS = 300
    
    ! Test parameters
    integer, parameter :: N_TESTS = 10
    real(dp), parameter :: PERTURBATION_SCALE = 100.0_dp  ! Scale for random perturbations [m or m/s]
    
    ! Variables
    real(dp) :: r0(3), v0(3), dt, t_stop
    real(dp) :: delta_y0_init(6), delta_y0_opt(6)
    real(dp) :: cgpd_initial, cgpd_opt
    integer :: n_iterations, i, seed_val
    logical :: converged
    real(dp), allocatable :: history_x(:,:), history_f(:)
    real(dp) :: total_time_start, total_time_end
    integer :: out_unit
    
    ! Random number generator
    integer :: seed_size
    integer, allocatable :: seed(:)
    
    print *, ''
    print *, '========================================'
    print *, 'Optimization Robustness Test'
    print *, '========================================'
    print *, ''
    print *, 'Testing optimization with', N_TESTS, 'different initial states'
    print *, 'Perturbation scale:', PERTURBATION_SCALE, 'm or m/s'
    print *, ''
    
    ! Load third body positions if needed
    if (ENABLE_THIRD_BODY) then
        call load_third_body_positions()
    end if
    
    ! Load SGP4 reference
    call load_sgp4_reference('../../../data/sgp4_reference/sgp4_orbit.txt')
    
    ! Read initial state
    call read_initial_state('../../../data/sgp4_reference/initial_state.txt', &
                           r0, v0, dt, t_stop)
    
    ! Initialize random seed
    call random_seed(size=seed_size)
    allocate(seed(seed_size))
    seed = 12345  ! Fixed seed for reproducibility
    call random_seed(put=seed)
    
    ! Open output file
    open(newunit=out_unit, file='../../../data/outputs_all/robustness_test.txt', &
         status='replace', action='write')
    
    write(out_unit, '(A)') '# Optimization Robustness Test'
    write(out_unit, '(A)') '# Testing with different initial perturbations'
    write(out_unit, '(A,I0)') '# Number of tests: ', N_TESTS
    write(out_unit, '(A,ES12.4)') '# Perturbation scale [m or m/s]: ', PERTURBATION_SCALE
    write(out_unit, '(A)') '#'
    write(out_unit, '(A)') '# Columns: Test_ID, Initial_CGPD[m], Optimized_CGPD[m], Improvement[m], '// &
                           'Iterations, Converged, dx0[m], dy0[m], dz0[m], dvx0[m/s], dvy0[m/s], dvz0[m/s], '// &
                           'dx_opt[m], dy_opt[m], dz_opt[m], dvx_opt[m/s], dvy_opt[m/s], dvz_opt[m/s]'
    
    print *, '========================================'
    print *, 'Running Tests'
    print *, '========================================'
    print *, ''
    
    call cpu_time(total_time_start)
    
    ! Run multiple tests with different initial perturbations
    do i = 1, N_TESTS
        
        ! Generate random initial perturbation
        if (i == 1) then
            ! First test: zero perturbation (baseline)
            delta_y0_init = 0.0_dp
        else
            ! Random perturbations
            call random_number(delta_y0_init)
            delta_y0_init = (delta_y0_init - 0.5_dp) * 2.0_dp * PERTURBATION_SCALE
        end if
        
        ! Compute initial CGPD
        cgpd_initial = objective_wrapper(delta_y0_init)
        
        ! Run optimization
        call gradient_descent_adaptive(objective_wrapper, delta_y0_init, delta_y0_opt, &
                                       cgpd_opt, n_iterations, converged, &
                                       history_x, history_f, &
                                       LEARNING_RATE, TOLERANCE, MAX_ITERATIONS)
        
        ! Print progress
        print '(A,I2,A,F10.3,A,F10.3,A,I3,A,L1)', &
              'Test ', i, ': Initial CGPD = ', cgpd_initial, ' m, Optimized = ', cgpd_opt, &
              ' m, Iters = ', n_iterations, ', Converged = ', converged
        
        ! Write to file
        write(out_unit, '(I3,2(2X,F12.6),2X,F10.6,2X,I4,2X,L1,12(2X,ES14.6))') &
              i, cgpd_initial, cgpd_opt, cgpd_initial - cgpd_opt, n_iterations, converged, &
              delta_y0_init, delta_y0_opt
        
        ! Clean up allocations
        if (allocated(history_x)) deallocate(history_x)
        if (allocated(history_f)) deallocate(history_f)
        
    end do
    
    call cpu_time(total_time_end)
    
    close(out_unit)
    
    print *, ''
    print *, '========================================'
    print *, 'Robustness Test Complete'
    print *, '========================================'
    print *, ''
    print *, 'Total time:', total_time_end - total_time_start, 's'
    print *, 'Results saved to: data/outputs_all/robustness_test.txt'
    print *, ''
    
    call cleanup_sgp4_reference()
    deallocate(seed)
    
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
        real(dp), intent(in) :: delta_y0(6)
        real(dp) :: cgpd
        real(dp) :: r_current(3), v_current(3)
        real(dp) :: t_current, dt_current
        integer :: step, max_steps
        real(dp), allocatable :: positions(:,:)
        
        max_steps = ceiling(t_stop / dt) + 10
        allocate(positions(3, max_steps))
        
        r_current = r0 + delta_y0(1:3)
        v_current = v0 + delta_y0(4:6)
        
        t_current = 0.0_dp
        step = 0
        
        do while (t_current < t_stop)
            step = step + 1
            positions(:, step) = r_current
            
            dt_current = min(dt, t_stop - t_current)
            
            call velocity_verlet_step(r_current, v_current, dt_current)
            
            t_current = t_current + dt_current
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
    
end program test_optimization_robustness
