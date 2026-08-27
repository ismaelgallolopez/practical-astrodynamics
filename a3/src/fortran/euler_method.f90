module euler_integrator_module
    use gravity
    implicit none
    
contains

    ! Euler integrator subroutine
    ! Inputs:
    !   - state0(6): initial state vector [x, y, z, vx, vy, vz]
    !   - dt: time step [s]
    !   - t_stop: stop time [s]
    !   - accel_func: function that computes acceleration from position
    ! Outputs:
    !   - t_array: array of time values
    !   - state_array: array of state vectors at each time step
    !   - n_steps: number of time steps
    subroutine euler_integrate(state0, dt, t_stop, accel_func, t_array, state_array, n_steps)
        real(dp), intent(in) :: state0(6)
        real(dp), intent(in) :: dt
        real(dp), intent(in) :: t_stop
        integer, intent(out) :: n_steps
        real(dp), allocatable, intent(out) :: t_array(:)
        real(dp), allocatable, intent(out) :: state_array(:,:)
        
        interface
            function accel_func(r) result(a)
                import :: dp
                real(dp), intent(in) :: r(3)
                real(dp) :: a(3)
            end function accel_func
        end interface
        
        integer :: i
        real(dp) :: t_current
        real(dp) :: r(3), v(3), a(3)
        
        ! Calculate number of steps
        n_steps = int(t_stop / dt) + 1
        
        ! Allocate output arrays
        allocate(t_array(n_steps))
        allocate(state_array(6, n_steps))
        
        ! Initialize first state
        t_array(1) = 0.0_dp
        state_array(:, 1) = state0
        
        ! Euler integration loop
        do i = 1, n_steps - 1
            ! Current time
            t_current = t_array(i)
            
            ! Extract position and velocity
            r = state_array(1:3, i)
            v = state_array(4:6, i)
            
            ! Compute acceleration using provided function
            a = accel_func(r)
            
            ! Euler step: state(n+1) = state(n) + dt * derivative
            state_array(1:3, i+1) = r + dt * v        ! position update
            state_array(4:6, i+1) = v + dt * a        ! velocity update
            
            ! Update time
            t_array(i+1) = t_current + dt
        end do
        
    end subroutine euler_integrate

end module euler_integrator_module
