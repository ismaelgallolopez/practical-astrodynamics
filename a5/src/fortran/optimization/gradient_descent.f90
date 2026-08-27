module gradient_descent_mod
    use gravity, only: dp
    implicit none
    
    ! Optimization parameters
    real(dp), parameter :: DEFAULT_LEARNING_RATE = 1.0e-5_dp
    real(dp), parameter :: DEFAULT_TOLERANCE = 1.0e-10_dp
    integer, parameter :: DEFAULT_MAX_ITERATIONS = 1e5
    real(dp), parameter :: FINITE_DIFF_EPSILON = 1.0e-5_dp  ! For numerical gradient
    
contains

    ! Compute numerical gradient using finite differences
    ! Input:
    !   - obj_func: objective function to differentiate
    !   - x: current point (6D state perturbation)
    ! Output:
    !   - gradient: 6D gradient vector
    subroutine compute_gradient(obj_func, x, gradient)
        interface
            function obj_func(delta_y0) result(f)
                import :: dp
                real(dp), intent(in) :: delta_y0(6)
                real(dp) :: f
            end function obj_func
        end interface
        
        real(dp), intent(in) :: x(6)
        real(dp), intent(out) :: gradient(6)
        
        real(dp) :: x_plus(6), x_minus(6)
        real(dp) :: f_plus, f_minus
        integer :: i
        
        ! Compute gradient using central finite differences
        ! df/dx_i ≈ (f(x + ε*e_i) - f(x - ε*e_i)) / (2*ε)
        do i = 1, 6
            x_plus = x
            x_minus = x
            
            x_plus(i) = x(i) + FINITE_DIFF_EPSILON
            x_minus(i) = x(i) - FINITE_DIFF_EPSILON
            
            f_plus = obj_func(x_plus)
            f_minus = obj_func(x_minus)
            
            gradient(i) = (f_plus - f_minus) / (2.0_dp * FINITE_DIFF_EPSILON)
        end do
        
    end subroutine compute_gradient
    
    ! Gradient descent optimization
    ! Inputs:
    !   - obj_func: objective function to minimize
    !   - x0: initial guess (6D)
    !   - learning_rate: step size for gradient descent
    !   - tolerance: convergence criterion (gradient norm)
    !   - max_iterations: maximum number of iterations
    ! Outputs:
    !   - x_opt: optimized solution
    !   - f_opt: optimal function value
    !   - n_iterations: number of iterations performed
    !   - converged: whether algorithm converged
    !   - history_x: history of x values (6, n_iterations)
    !   - history_f: history of objective function values (n_iterations)
    subroutine gradient_descent(obj_func, x0, x_opt, f_opt, n_iterations, converged, &
                                history_x, history_f, learning_rate_in, tolerance_in, max_iter_in)
        interface
            function obj_func(delta_y0) result(f)
                import :: dp
                real(dp), intent(in) :: delta_y0(6)
                real(dp) :: f
            end function obj_func
        end interface
        
        real(dp), intent(in) :: x0(6)
        real(dp), intent(out) :: x_opt(6)
        real(dp), intent(out) :: f_opt
        integer, intent(out) :: n_iterations
        logical, intent(out) :: converged
        real(dp), allocatable, intent(out) :: history_x(:,:)
        real(dp), allocatable, intent(out) :: history_f(:)
        real(dp), optional, intent(in) :: learning_rate_in
        real(dp), optional, intent(in) :: tolerance_in
        integer, optional, intent(in) :: max_iter_in
        
        real(dp) :: x_current(6), gradient(6)
        real(dp) :: f_current, grad_norm
        real(dp) :: x_best(6), f_best
        real(dp) :: learning_rate, tolerance
        integer :: max_iterations, iter
        
        ! Set parameters
        learning_rate = DEFAULT_LEARNING_RATE
        if (present(learning_rate_in)) learning_rate = learning_rate_in
        
        tolerance = DEFAULT_TOLERANCE
        if (present(tolerance_in)) tolerance = tolerance_in
        
        max_iterations = DEFAULT_MAX_ITERATIONS
        if (present(max_iter_in)) max_iterations = max_iter_in
        
        ! Allocate history arrays
        allocate(history_x(6, max_iterations))
        allocate(history_f(max_iterations))
        
        ! Initialize
        x_current = x0
        converged = .false.
        f_best = huge(1.0_dp)
        x_best = x0
        
        ! Optimization loop
        do iter = 1, max_iterations
            ! Evaluate objective function
            f_current = obj_func(x_current)
            
            ! Keep track of best solution
            if (f_current < f_best) then
                f_best = f_current
                x_best = x_current
            end if
            
            ! Store history
            history_x(:, iter) = x_current
            history_f(iter) = f_current
            
            ! Compute gradient
            call compute_gradient(obj_func, x_current, gradient)
            
            ! Check convergence
            grad_norm = sqrt(sum(gradient**2))
            if (grad_norm < tolerance) then
                converged = .true.
                n_iterations = iter
                exit
            end if
            
            ! Update x using gradient descent: x_new = x_old - α * ∇f
            x_current = x_current - learning_rate * gradient
            
        end do
        
        if (.not. converged) then
            n_iterations = max_iterations
        end if
        
        ! Set outputs to best solution found (not last iteration)
        x_opt = x_best
        f_opt = f_best
        
    end subroutine gradient_descent
    
    ! Gradient descent with adaptive learning rate (Adam-like)
    subroutine gradient_descent_adaptive(obj_func, x0, x_opt, f_opt, n_iterations, converged, &
                                        history_x, history_f, learning_rate_in, tolerance_in, max_iter_in)
        interface
            function obj_func(delta_y0) result(f)
                import :: dp
                real(dp), intent(in) :: delta_y0(6)
                real(dp) :: f
            end function obj_func
        end interface
        
        real(dp), intent(in) :: x0(6)
        real(dp), intent(out) :: x_opt(6)
        real(dp), intent(out) :: f_opt
        integer, intent(out) :: n_iterations
        logical, intent(out) :: converged
        real(dp), allocatable, intent(out) :: history_x(:,:)
        real(dp), allocatable, intent(out) :: history_f(:)
        real(dp), optional, intent(in) :: learning_rate_in
        real(dp), optional, intent(in) :: tolerance_in
        integer, optional, intent(in) :: max_iter_in
        
        real(dp) :: x_current(6), gradient(6)
        real(dp) :: f_current, f_prev, grad_norm
        real(dp) :: x_best(6), f_best
        real(dp) :: learning_rate, tolerance
        real(dp) :: momentum(6), velocity(6)
        real(dp) :: beta1, beta2, epsilon
        integer :: max_iterations, iter
        
        ! Set parameters
        learning_rate = DEFAULT_LEARNING_RATE
        if (present(learning_rate_in)) learning_rate = learning_rate_in
        
        tolerance = DEFAULT_TOLERANCE
        if (present(tolerance_in)) tolerance = tolerance_in
        
        max_iterations = DEFAULT_MAX_ITERATIONS
        if (present(max_iter_in)) max_iterations = max_iter_in
        
        ! Momentum parameters (Adam-like)
        beta1 = 0.9_dp
        beta2 = 0.999_dp
        epsilon = 1.0e-8_dp
        
        ! Allocate history arrays
        allocate(history_x(6, max_iterations))
        allocate(history_f(max_iterations))
        
        ! Initialize
        x_current = x0
        momentum = 0.0_dp
        velocity = 0.0_dp
        converged = .false.
        f_prev = huge(1.0_dp)
        f_best = huge(1.0_dp)
        x_best = x0
        
        ! Optimization loop
        do iter = 1, max_iterations
            ! Evaluate objective function
            f_current = obj_func(x_current)
            
            ! Keep track of best solution
            if (f_current < f_best) then
                f_best = f_current
                x_best = x_current
            end if
            
            ! Store history
            history_x(:, iter) = x_current
            history_f(iter) = f_current
            
            ! Compute gradient
            call compute_gradient(obj_func, x_current, gradient)
            
            ! Check convergence
            grad_norm = sqrt(sum(gradient**2))
            if (grad_norm < tolerance) then
                converged = .true.
                n_iterations = iter
                exit
            end if
            
            ! Check for function value improvement
            if (abs(f_current - f_prev) < tolerance * abs(f_prev)) then
                converged = .true.
                n_iterations = iter
                exit
            end if
            
            ! Update momentum and velocity (Adam-like)
            momentum = beta1 * momentum + (1.0_dp - beta1) * gradient
            velocity = beta2 * velocity + (1.0_dp - beta2) * gradient**2
            
            ! Compute bias-corrected estimates
            ! (simplified version, not exact Adam)
            
            ! Update x
            x_current = x_current - learning_rate * momentum / (sqrt(velocity) + epsilon)
            
            f_prev = f_current
            
        end do
        
        if (.not. converged) then
            n_iterations = max_iterations
        end if
        
        ! Set outputs to best solution found (not last iteration)
        x_opt = x_best
        f_opt = f_best
        
    end subroutine gradient_descent_adaptive
    
end module gradient_descent_mod
