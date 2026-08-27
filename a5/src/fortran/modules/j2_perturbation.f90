module j2_perturbation
    implicit none
    
    ! Parameters
    integer, parameter :: dp = selected_real_kind(15, 307)
    real(dp), parameter :: mu_earth = 3.986004418e14_dp  ! Earth's gravitational parameter [m^3/s^2]
    real(dp), parameter :: R_earth = 6371.0e3_dp         ! Earth's mean radius [m]
    real(dp), parameter :: J2 = 1.083e-3_dp              ! Earth's J2 coefficient (dimensionless)
    
contains

    ! Compute J2 perturbation acceleration
    ! Input: position vector r [m] in inertial frame (z-axis aligned with Earth's rotation axis)
    ! Output: acceleration vector a_j2 [m/s^2]
    function j2_acceleration(r) result(a_j2)
        real(dp), intent(in) :: r(3)
        real(dp) :: a_j2(3)
        real(dp) :: r_mag, z2_r2, factor
        
        ! Compute distance from Earth center
        r_mag = sqrt(r(1)**2 + r(2)**2 + r(3)**2)
        
        ! Compute z^2 / r^2
        z2_r2 = (r(3) / r_mag)**2
        
        ! Common factor: (3/2) * J2 * mu * R_earth^2 / r^5
        factor = 1.5_dp * J2 * mu_earth * (R_earth / r_mag)**2 / r_mag**3
        
        ! Compute J2 acceleration components
        ! a_x = factor * x * (5*z^2/r^2 - 1)
        ! a_y = factor * y * (5*z^2/r^2 - 1)
        ! a_z = factor * z * (5*z^2/r^2 - 3)
        a_j2(1) = factor * r(1) * (5.0_dp * z2_r2 - 1.0_dp)
        a_j2(2) = factor * r(2) * (5.0_dp * z2_r2 - 1.0_dp)
        a_j2(3) = factor * r(3) * (5.0_dp * z2_r2 - 3.0_dp)
        
        
    end function j2_acceleration

end module j2_perturbation