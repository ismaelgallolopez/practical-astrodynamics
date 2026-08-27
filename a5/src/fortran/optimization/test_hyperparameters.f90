program test_hyperparameters
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
    ! Test different hyperparameters for gradient descent
    !============================================================================
    
    ! Perturbation toggles
    logical, parameter :: ENABLE_J2 = .true.
    logical, parameter :: ENABLE_DRAG = .false.
    logical, parameter :: ENABLE_SRP = .true.
    logical, parameter :: ENABLE_THIRD_BODY = .true.
    
    ! Test parameters
    integer, parameter :: N_LEARNING_RATES = 5
    integer, parameter :: N_TOLERANCES = 4
    real(dp), parameter :: LEARNING_RATES(N_LEARNING_RATES) = &
        [1.0e-6_dp, 1.0e-5_dp, 5.0e-5_dp, 1.0e-4_dp, 5.0e-4_dp]
    real(dp), parameter :: TOLERANCES(N_TOLERANCES) = &
        [0.01_dp, 0.1_dp, 1.0_dp, 10.0_dp]  ! meters
    integer, parameter :: MAX_ITERATIONS = 1000
    
    ! Variables
    real(dp) :: r0(3), v0(3), dt, t_stop
    real(dp) :: delta_y0_init(6), delta_y0_opt(6)
    real(dp) :: cgpd_initial, cgpd_opt
    integer :: n_iterations, i, j
    logical :: converged
    real(dp), allocatable :: history_x(:,:), history_f(:)
    real(dp) :: lr, tol
    real(dp) :: start_time, end_time, elapsed_time
    integer :: out_unit
    
    print *, ''
    print *, '========================================'
    print *, 'Hyperparameter Sensitivity Test'
    print *, '========================================'
    print *, ''
    print *, 'Testing', N_LEARNING_RATES, 'learning rates x', N_TOLERANCES, 'tolerances'
    print *, 'Total configurations:', N_LEARNING_RATES * N_TOLERANCES
    print *, ''
    
    ! Load third body positions
    call load_third_body_positions()
    
    ! Load SGP4 reference
    call load_sgp4_reference('../../../data/sgp4_reference/sgp4_orbit.txt')
    
    ! Read initial state
    call read_initial_state('../../../data/sgp4_reference/initial_state.txt', &
                           r0, v0, dt, t_stop)
    
    ! Compute initial CGPD
    delta_y0_init = 0.0_dp
    cgpd_initial = objective_wrapper(delta_y0_init)
    
    print *, 'Initial CGPD (no perturbation):', cgpd_initial, 'm'
    print *, ''
    
    ! Open output file
    open(newunit=out_unit, file='../../../data/outputs_all/hyperparameter_test.txt', &
         status='replace', action='write')
    
    write(out_unit, '(A)') '# Hyperparameter Sensitivity Test'
    write(out_unit, '(A,ES12.4)') '# Initial CGPD [m]: ', cgpd_initial
    write(out_unit, '(A)') '#'
    write(out_unit, '(A)') '# Columns: LearningRate, Tolerance[m], Converged, Iterations, '// &
                           'FinalCGPD[m], Improvement[m], Time[s]'
    
    print *, '========================================'
    print *, 'Running Tests'
    print *, '========================================'
    print *, ''
    
    ! Test all combinations
    do i = 1, N_LEARNING_RATES
        lr = LEARNING_RATES(i)
        
        do j = 1, N_TOLERANCES
            tol = TOLERANCES(j)
            
            ! Run optimization
            call cpu_time(start_time)
            
            call gradient_descent_adaptive(objective_wrapper, delta_y0_init, delta_y0_opt, &
                                           cgpd_opt, n_iterations, converged, &
                                           history_x, history_f, &
                                           lr, tol, MAX_ITERATIONS)
            
            call cpu_time(end_time)
            elapsed_time = end_time - start_time
            
            ! Print progress
            print '(A,ES9.2,A,F6.2,A,L1,A,I4,A,F10.3,A,F8.5,A)', &
                  'LR=', lr, ', Tol=', tol, ' m: Conv=', converged, &
                  ', Iters=', n_iterations, ', CGPD=', cgpd_opt, ' m, Time=', elapsed_time, ' s'
            
            ! Write to file
            write(out_unit, '(ES12.4,2X,F8.4,2X,L1,2X,I5,2X,F12.6,2X,F10.6,2X,F10.6)') &
                  lr, tol, converged, n_iterations, cgpd_opt, cgpd_initial - cgpd_opt, elapsed_time
            
            ! Clean up allocations
            if (allocated(history_x)) deallocate(history_x)
            if (allocated(history_f)) deallocate(history_f)
            
        end do
        print *, ''
    end do
    
    close(out_unit)
    
    print *, '========================================'
    print *, 'Test Complete'
    print *, '========================================'
    print *, ''
    print *, 'Results saved to: data/outputs_all/hyperparameter_test.txt'
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
    
end program test_hyperparameters
