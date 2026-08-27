module gravity
    implicit none
    
    ! Parameters
    integer, parameter :: dp = selected_real_kind(15, 307)
    real(dp), parameter :: mu_earth = 3.986004418e14_dp  ! Earth's gravitational parameter [m^3/s^2]
    
contains

    ! Compute 3D gravitational acceleration from point mass
    ! Input: position vector r [m]
    ! Output: acceleration vector a [m/s^2]
    function gravitational_acceleration(r) result(a)
        real(dp), intent(in) :: r(3)
        real(dp) :: a(3)
        real(dp) :: r_mag
        
        ! Compute distance from Earth center
        r_mag = sqrt(r(1)**2 + r(2)**2 + r(3)**2)
        
        ! Compute gravitational acceleration: a = -mu * r / |r|^3
        a = -mu_earth * r / r_mag**3
        
    end function gravitational_acceleration

end module gravity
