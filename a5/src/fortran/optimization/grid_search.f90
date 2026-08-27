program grid_search_optimization
    use gravity, only: dp, gravitational_acceleration
    use j2_perturbation, only: j2_acceleration
    use drag_perturbation, only: drag_acceleration
    use srp_perturbation, only: srp_acceleration
    use third_body_perturbation, only: third_body_acceleration, load_third_body_positions
    use velocity_verlet_integrator_module
    use objective_function
    implicit none
    
    !============================================================================
    ! Grid Search Optimization - Systematic search approach
    !============================================================================
    
    ! Perturbation toggles
    logical, parameter :: ENABLE_J2 = .true.
    logical, parameter :: ENABLE_DRAG = .false.
    logical, parameter :: ENABLE_SRP = .true.
    logical, parameter :: ENABLE_THIRD_BODY = .true.
    
    ! Grid search parameters
    integer, parameter :: N_GRID_POINTS = 50  ! Number of points per dimension
    real(dp), parameter :: SEARCH_RANGE = 1.0_dp  ! Search range [m or m/s]
    
    ! Variables
    real(dp) :: r0(3), v0(3), dt, t_stop
    real(dp) :: delta_y0(6), delta_y0_best(6)
    real(dp) :: cgpd_value, cgpd_best
    integer :: i, j, k, l, m, n
    integer :: total_evaluations, eval_count
    integer(kind=8) :: total_evals_6d  ! 8-byte integer for large number
    real(dp) :: grid_values(N_GRID_POINTS)
    real(dp) :: start_time, end_time
    integer :: out_unit
    
    print *, ''
    print *, '========================================'
    print *, 'Grid Search Optimization'
    print *, '========================================'
    print *, ''
    print *, 'Grid points per dimension:', N_GRID_POINTS
    print *, 'Search range [m or m/s]:  ', SEARCH_RANGE
    print *, ''
    
    ! Total number of evaluations
    total_evals_6d = int(N_GRID_POINTS, kind=8)**6
    print *, 'WARNING: Full 6D grid would require', total_evals_6d, 'evaluations!'
    print *, 'Using 2D grid search instead (dx and dy only)'
    total_evaluations = N_GRID_POINTS**2
    print *, 'Total evaluations:', total_evaluations
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
    
    ! Create grid of values
    do i = 1, N_GRID_POINTS
        grid_values(i) = -SEARCH_RANGE + (i-1) * (2.0_dp * SEARCH_RANGE) / real(N_GRID_POINTS - 1, dp)
    end do
    
    ! Open output file
    open(newunit=out_unit, file='../../../data/outputs_all/grid_search_results.txt', &
         status='replace', action='write')
    
    write(out_unit, '(A)') '# Grid Search Optimization Results'
    write(out_unit, '(A,I0)') '# Grid points per dimension: ', N_GRID_POINTS
    write(out_unit, '(A,ES12.4)') '# Search range [m or m/s]: ', SEARCH_RANGE
    write(out_unit, '(A)') '# 2D grid search: dx and dy only (other components = 0)'
    write(out_unit, '(A)') '#'
    write(out_unit, '(A)') '# Columns: dx[m], dy[m], CGPD[m]'
    
    print *, '========================================'
    print *, 'Running Grid Search'
    print *, '========================================'
    print *, ''
    
    call cpu_time(start_time)
    
    ! Initialize best solution
    cgpd_best = 1.0e30_dp
    delta_y0_best = 0.0_dp
    delta_y0 = 0.0_dp
    eval_count = 0
    
    ! Grid search over dx and dy
    do i = 1, N_GRID_POINTS
        delta_y0(1) = grid_values(i)  ! dx
        
        do j = 1, N_GRID_POINTS
            delta_y0(2) = grid_values(j)  ! dy
            
            eval_count = eval_count + 1
            
            ! Evaluate objective function
            cgpd_value = objective_wrapper(delta_y0)
            
            ! Write to file
            write(out_unit, '(3(ES14.6,2X))') delta_y0(1), delta_y0(2), cgpd_value
            
            ! Update best solution
            if (cgpd_value < cgpd_best) then
                cgpd_best = cgpd_value
                delta_y0_best = delta_y0
            end if
            
            ! Print progress
            if (mod(eval_count, 50) == 0) then
                print '(A,I5,A,I5,A,F8.2,A)', 'Progress: ', eval_count, ' / ', total_evaluations, &
                       ' (', 100.0_dp * real(eval_count, dp) / real(total_evaluations, dp), '%)'
            end if
            
        end do
    end do
    
    call cpu_time(end_time)
    
    close(out_unit)
    
    ! Evaluate CGPD at zero perturbation for comparison
    delta_y0 = 0.0_dp
    cgpd_value = objective_wrapper(delta_y0)
    
    print *, ''
    print *, '========================================'
    print *, 'Grid Search Complete'
    print *, '========================================'
    print *, ''
    print *, 'Total evaluations:   ', total_evaluations
    print *, 'Total time [s]:      ', end_time - start_time
    print *, 'Time per eval [ms]:  ', (end_time - start_time) / real(total_evaluations, dp) * 1000.0_dp
    print *, ''
    print *, 'CGPD at zero perturbation:', cgpd_value, 'm'
    print *, 'Best CGPD found:          ', cgpd_best, 'm'
    print *, 'Improvement:              ', cgpd_value - cgpd_best, 'm'
    print *, ''
    print *, 'Optimal delta_y0 (grid search):'
    print *, '  dx [m]:    ', delta_y0_best(1)
    print *, '  dy [m]:    ', delta_y0_best(2)
    print *, '  dz [m]:    ', delta_y0_best(3)
    print *, '  dvx [m/s]: ', delta_y0_best(4)
    print *, '  dvy [m/s]: ', delta_y0_best(5)
    print *, '  dvz [m/s]: ', delta_y0_best(6)
    print *, ''
    print *, 'Results saved to: data/outputs_all/grid_search_results.txt'
    print *, ''
    
    ! Save best solution
    open(newunit=out_unit, file='../../../data/outputs_all/grid_search_optimal.txt', &
         status='replace', action='write')
    write(out_unit, '(A)') '# Grid Search Optimal Solution'
    write(out_unit, '(A,ES14.6)') '# Best CGPD [m]: ', cgpd_best
    write(out_unit, '(A)') '# Optimal delta_y0:'
    write(out_unit, '(6(ES20.12,2X))') delta_y0_best
    close(out_unit)
    
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
    
end program grid_search_optimization
