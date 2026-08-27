module velocity_verlet_integrator_module
    use gravity
    implicit none

contains

    ! Velocity Verlet integrator subroutine
    ! Inputs:
    !   - state0(6): initial state vector [x, y, z, vx, vy, vz]
    !   - dt: time step [s]
    !   - t_stop: stop time [s]
    !   - accel_func: function that computes acceleration from position
    ! Outputs:
    !   - t_array: array of time values
    !   - state_array: array of state vectors at each time step
    !   - n_steps: number of time steps
    subroutine velocity_verlet_integrate(state0, dt, t_stop, accel_func, t_array, state_array, n_steps)
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
        real(dp) :: r(3), v(3)
        real(dp) :: a_n(3), a_np1(3)
        real(dp) :: r_new(3), v_new(3)
        real(dp) :: dt2

        ! Calculate number of steps
        n_steps = int(t_stop / dt) + 1

        ! Allocate output arrays
        allocate(t_array(n_steps))
        allocate(state_array(6, n_steps))

        ! Precompute dt^2
        dt2 = dt * dt

        ! Initialize first state
        t_array(1)      = 0.0_dp
        state_array(:,1) = state0

        ! Velocity Verlet integration loop
        do i = 1, n_steps - 1
            ! Current time
            t_current = t_array(i)

            ! Extract position and velocity at step i
            r = state_array(1:3, i)
            v = state_array(4:6, i)

            ! Acceleration at current position: a_n = a(r_n)
            a_n = accel_func(r)

            ! --- Position update ---
            ! r_{n+1} = r_n + dt*v_n + 0.5*dt^2*a_n
            r_new = r + dt * v + 0.5_dp * dt2 * a_n

            ! Acceleration at new position: a_{n+1} = a(r_{n+1})
            a_np1 = accel_func(r_new)

            ! --- Velocity update ---
            ! v_{n+1} = v_n + 0.5*dt*(a_n + a_{n+1})
            v_new = v + 0.5_dp * dt * (a_n + a_np1)

            ! Store updated state
            state_array(1:3, i+1) = r_new
            state_array(4:6, i+1) = v_new

            ! Update time
            t_array(i+1) = t_current + dt
        end do

    end subroutine velocity_verlet_integrate

end module velocity_verlet_integrator_module
