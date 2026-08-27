program propagate_optimized
    use gravity, only: dp, gravitational_acceleration
    use j2_perturbation, only: j2_acceleration
    use drag_perturbation, only: drag_acceleration
    use srp_perturbation, only: srp_acceleration
    use third_body_perturbation, only: third_body_acceleration, load_third_body_positions
    use velocity_verlet_integrator_module
    implicit none
    
    !============================================================================
    ! Propagate orbit with optimized initial state
    !============================================================================
    
    ! Perturbation toggles (must match optimization settings)
    logical, parameter :: ENABLE_J2 = .true.
    logical, parameter :: ENABLE_DRAG = .false.
    logical, parameter :: ENABLE_SRP = .true.
    logical, parameter :: ENABLE_THIRD_BODY = .true.
    
    ! Variables
    real(dp) :: r0(3), v0(3), dt, t_stop
    real(dp) :: delta_y0(6)
    real(dp) :: r_current(3), v_current(3)
    real(dp) :: t_current
    integer :: step, max_steps, out_unit
    
    print *, ''
    print *, '========================================'
    print *, 'Propagating Optimized Orbit'
    print *, '========================================'
    print *, ''
    
    ! Load third body positions
    call load_third_body_positions()
    
    ! Read initial state
    call read_initial_state('../../../data/sgp4_reference/initial_state.txt', &
                           r0, v0, dt, t_stop)
    
    ! Read optimized state (not delta - the file contains the full optimized state)
    call read_optimized_state('../../../data/outputs_all/optimized_initial_state.txt', &
                             r_current, v_current)
    
    print *, 'Initial state (SGP4):'
    print '(A,3F18.6)', '  Position [m]:   ', r0
    print '(A,3F18.6)', '  Velocity [m/s]: ', v0
    print *, ''
    
    ! Compute delta for display
    delta_y0(1:3) = r_current - r0
    delta_y0(4:6) = v_current - v0
    
    print *, 'Optimized correction:'
    print '(A,3ES15.6)', '  Delta pos [m]:  ', delta_y0(1:3)
    print '(A,3ES15.6)', '  Delta vel [m/s]:', delta_y0(4:6)
    print *, ''
    
    ! Apply correction
    ! r_current and v_current are already set from file
    
    print *, 'Optimized initial state:'
    print '(A,3F18.6)', '  Position [m]:   ', r_current
    print '(A,3F18.6)', '  Velocity [m/s]: ', v_current
    print *, ''
    
    ! Open output file
    open(newunit=out_unit, file='../../../data/outputs_all/optimized_orbit.txt', &
         status='replace', action='write')
    
    write(out_unit, '(A)') '# Optimized orbit propagation'
    write(out_unit, '(A)') '# Columns: time[s] x[m] y[m] z[m] vx[m/s] vy[m/s] vz[m/s]'
    
    ! Propagate
    max_steps = ceiling(t_stop / dt) + 10
    t_current = 0.0_dp
    step = 0
    
    print *, 'Propagating...'
    
    ! Write initial state
    write(out_unit, '(F12.6,6ES24.15)') t_current, r_current, v_current
    step = 1
    
    do while (t_current < t_stop)
        ! Integrate one step
        call velocity_verlet_step(r_current, v_current, min(dt, t_stop - t_current))
        
        t_current = t_current + dt
        step = step + 1
        
        ! Write current state
        write(out_unit, '(F12.6,6ES24.15)') min(t_current, t_stop), r_current, v_current
        
        if (mod(step, 1000) == 0) then
            print '(A,I6,A,F10.2,A)', '  Step ', step, ', time = ', t_current, ' s'
        end if
    end do
    
    close(out_unit)
    
    print *, ''
    print *, 'Propagation complete!'
    print '(A,I0,A)', '  Total steps: ', step
    print *, '  Output saved to: data/outputs_all/optimized_orbit.txt'
    print *, ''
    
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
    ! Read optimized state from file
    !============================================================================
    subroutine read_optimized_state(filename, r0, v0)
        character(len=*), intent(in) :: filename
        real(dp), intent(out) :: r0(3), v0(3)
        real(dp) :: dummy_dt, dummy_tstop
        integer :: unit_num, ios
        
        open(newunit=unit_num, file=filename, status='old', action='read', iostat=ios)
        if (ios /= 0) then
            print *, 'Error: Could not open file:', trim(filename)
            stop 1
        end if
        
        read(unit_num, *) r0(1), r0(2), r0(3)
        read(unit_num, *) v0(1), v0(2), v0(3)
        read(unit_num, *) dummy_dt
        read(unit_num, *) dummy_tstop
        
        close(unit_num)
    end subroutine read_optimized_state
    
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
    
end program propagate_optimized
