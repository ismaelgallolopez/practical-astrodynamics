program perturbation_study
    
    use gravity, only: dp, gravitational_acceleration
    use j2_perturbation, only: j2_acceleration
    use drag_perturbation, only: drag_acceleration
    use srp_perturbation, only: srp_acceleration
    use third_body_perturbation, only: third_body_acceleration, load_third_body_positions
    use velocity_verlet_integrator_module
    use objective_function
    implicit none
    
    !============================================================================
    ! Perturbation Study - Systematically test all combinations
    !============================================================================
    
    ! Initial state variables
    real(dp) :: r0(3), v0(3), dt, t_stop
    real(dp) :: delta_y0(6)
    
    ! Study variables
    integer :: i, n_combinations
    logical :: enable_j2, enable_drag, enable_srp, enable_tbp
    logical :: tbp_available
    real(dp) :: cgpd_value, elapsed_time
    character(len=100) :: config_name
    integer :: count_start, count_end, count_rate
    
    ! Output file
    integer :: out_unit
    
    print *, ''
    print *, '========================================'
    print *, 'Perturbation Effects Study'
    print *, '========================================'
    print *, ''
    
    ! Check if third-body data is available
    tbp_available = file_exists('../../../data/sgp4_reference/third_body_positions.txt')
    if (.not. tbp_available) then
        print *, 'Warning: Third-body positions file not found.'
        print *, 'SRP and third-body perturbations will be skipped.'
        print *, 'To include them: python src/python/utilities/fetch_third_body_positions.py'
        print *, ''
    end if
    
    ! Load SGP4 reference orbit
    call load_sgp4_reference('../../../data/sgp4_reference/sgp4_orbit.txt')
    
    ! Read initial state
    call read_initial_state('../../../data/sgp4_reference/initial_state.txt', &
                           r0, v0, dt, t_stop)
    
    print *, 'Initial state loaded:'
    print *, '  Position [m]:  ', r0
    print *, '  Velocity [m/s]:', v0
    print *, '  dt [s]:        ', dt
    print *, '  t_stop [s]:    ', t_stop
    print *, ''
    
    ! Initialize delta_y0 to zero (no perturbation to initial state)
    delta_y0 = 0.0_dp
    
    ! Open output file
    open(newunit=out_unit, file='../../../data/outputs_all/perturbation_study.txt', &
         status='replace', action='write')
    
    ! Write header
    write(out_unit, '(A)') '# Perturbation Effects Study'
    write(out_unit, '(A)') '# Columns: Config_ID, J2, Drag, SRP, ThirdBody, CGPD[m], Time[s], Config_Name'
    write(out_unit, '(A)') '#'
    
    print *, '========================================'
    print *, 'Testing Perturbation Combinations'
    print *, '========================================'
    print *, ''
    
    n_combinations = 0
    
    ! Test all 16 combinations (2^4)
    do i = 0, 15
        n_combinations = n_combinations + 1
        
        ! Decode binary representation to get perturbation flags
        enable_j2   = btest(i, 0)  ! Bit 0
        enable_drag = btest(i, 1)  ! Bit 1
        enable_srp  = btest(i, 2)  ! Bit 2
        enable_tbp  = btest(i, 3)  ! Bit 3
        
        ! Skip SRP and third-body if data not available
        if ((enable_tbp .or. enable_srp) .and. .not. tbp_available) cycle
        
        ! Build configuration name
        call build_config_name(enable_j2, enable_drag, enable_srp, enable_tbp, config_name)
        
        ! Time the propagation
        call system_clock(count_start, count_rate)
        
        ! Compute CGPD for this configuration
        cgpd_value = compute_perturbation_cgpd(r0, v0, dt, t_stop, delta_y0, &
                                               enable_j2, enable_drag, enable_srp, enable_tbp)
        
        call system_clock(count_end)
        elapsed_time = real(count_end - count_start, dp) / real(count_rate, dp)
        
        ! Print progress
        print '(A,I2,A,F10.3,A,F8.5,A,A)', '  Config ', n_combinations, ': CGPD = ', &
              cgpd_value, ' m, Time = ', elapsed_time, ' s  (', trim(config_name), ')'
        
        ! Write to file
        write(out_unit, '(I3,4(2X,L1),2X,F12.6,2X,F10.6,2X,A)') n_combinations, &
              enable_j2, enable_drag, enable_srp, enable_tbp, cgpd_value, elapsed_time, trim(config_name)
    end do
    
    close(out_unit)
    
    print *, ''
    print *, '========================================'
    print *, 'Study Complete'
    print *, '========================================'
    print *, ''
    print *, 'Total combinations tested:', n_combinations
    print *, 'Results saved to: data/outputs_all/perturbation_study.txt'
    print *, ''
    
    ! Cleanup
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
    ! Build configuration name string
    !============================================================================
    subroutine build_config_name(j2, drag, srp, tbp, name)
        logical, intent(in) :: j2, drag, srp, tbp
        character(len=*), intent(out) :: name
        integer :: count
        
        name = ''
        count = 0
        
        if (.not. j2 .and. .not. drag .and. .not. srp .and. .not. tbp) then
            name = 'Two-Body Only'
            return
        end if
        
        if (j2) then
            name = trim(name) // 'J2'
            count = count + 1
        end if
        
        if (drag) then
            if (count > 0) name = trim(name) // '+'
            name = trim(name) // 'Drag'
            count = count + 1
        end if
        
        if (srp) then
            if (count > 0) name = trim(name) // '+'
            name = trim(name) // 'SRP'
            count = count + 1
        end if
        
        if (tbp) then
            if (count > 0) name = trim(name) // '+'
            name = trim(name) // 'TBP'
            count = count + 1
        end if
    end subroutine build_config_name
    
    !============================================================================
    ! Compute CGPD for a specific perturbation configuration
    !============================================================================
    function compute_perturbation_cgpd(r0, v0, dt, t_stop, delta_y0, &
                                       enable_j2, enable_drag, enable_srp, enable_tbp) result(cgpd)
        real(dp), intent(in) :: r0(3), v0(3), dt, t_stop, delta_y0(6)
        logical, intent(in) :: enable_j2, enable_drag, enable_srp, enable_tbp
        real(dp) :: cgpd
        
        ! Modified initial state
        real(dp) :: r_current(3), v_current(3)
        real(dp) :: t_current, t_next
        real(dp) :: dt_current
        integer :: step, max_steps
        
        ! Storage for positions
        real(dp), allocatable :: positions(:,:)
        
        ! Estimate maximum number of steps
        max_steps = ceiling(t_stop / dt) + 10
        allocate(positions(3, max_steps))
        
        ! Apply perturbation to initial state
        r_current = r0 + delta_y0(1:3)
        v_current = v0 + delta_y0(4:6)
        
        t_current = 0.0_dp
        step = 0
        
        ! Propagate orbit
        do while (t_current < t_stop)
            step = step + 1
            
            ! Store position
            positions(:, step) = r_current
            
            dt_current = min(dt, t_stop - t_current)
            t_next = t_current + dt_current
            
            ! Velocity Verlet integration with selected perturbations
            call velocity_verlet_step(r_current, v_current, dt_current, &
                                     enable_j2, enable_drag, enable_srp, enable_tbp)
            
            t_current = t_next
        end do
        
        ! Compute CGPD
        cgpd = compute_cgpd(positions, step)
        
        deallocate(positions)
        
    end function compute_perturbation_cgpd
    
    !============================================================================
    ! Velocity Verlet integration step with configurable perturbations
    !============================================================================
    subroutine velocity_verlet_step(r, v, dt, enable_j2, enable_drag, enable_srp, enable_tbp)
        real(dp), intent(inout) :: r(3), v(3)
        real(dp), intent(in) :: dt
        logical, intent(in) :: enable_j2, enable_drag, enable_srp, enable_tbp
        
        real(dp) :: a1(3), a2(3), r_mid(3), v_mid(3)
        
        ! Compute acceleration at current state
        a1 = total_acceleration(r, v, enable_j2, enable_drag, enable_srp, enable_tbp)
        
        ! Update position: r(t + dt) = r(t) + v(t)*dt + 0.5*a(t)*dt^2
        r = r + v * dt + 0.5_dp * a1 * dt**2
        
        ! Compute acceleration at new position (with current velocity)
        a2 = total_acceleration(r, v, enable_j2, enable_drag, enable_srp, enable_tbp)
        
        ! Update velocity: v(t + dt) = v(t) + 0.5*(a(t) + a(t+dt))*dt
        v = v + 0.5_dp * (a1 + a2) * dt
        
    end subroutine velocity_verlet_step
    
    !============================================================================
    ! Compute total acceleration with configurable perturbations
    !============================================================================
    function total_acceleration(r, v, enable_j2, enable_drag, enable_srp, enable_tbp) result(a)
        real(dp), intent(in) :: r(3), v(3)
        logical, intent(in) :: enable_j2, enable_drag, enable_srp, enable_tbp
        real(dp) :: a(3)
        
        ! Two-body gravitational acceleration (always included)
        a = gravitational_acceleration(r)
        
        ! Add perturbations based on flags
        if (enable_j2) then
            a = a + j2_acceleration(r)
        end if
        
        if (enable_drag) then
            a = a + drag_acceleration(r, v)
        end if
        
        if (enable_srp) then
            a = a + srp_acceleration(r)
        end if
        
        if (enable_tbp) then
            a = a + third_body_acceleration(r)
        end if
        
    end function total_acceleration
    
    !============================================================================
    ! Check if file exists
    !============================================================================
    function file_exists(filename) result(exists)
        character(len=*), intent(in) :: filename
        logical :: exists
        inquire(file=filename, exist=exists)
    end function file_exists
    
end program perturbation_study
