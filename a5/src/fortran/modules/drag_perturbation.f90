module drag_perturbation
    use gravity, only: dp, omega_earth
    implicit none
    
    ! Parameters
    real(dp), parameter :: PI = acos(-1.0_dp)
    real(dp), parameter :: R_EARTH = 6371.0e3_dp           ! Earth's mean radius [m]
    real(dp), parameter :: BALLISTIC_COEFF = 0.01_dp       ! B = C_D * A / m [m^2/kg]
    
    ! Atmospheric parameters for altitude 35786 km (from table)
    real(dp), parameter :: RHO_0 = 4.04e-19_dp             ! Mean density [kg/m^3]
    real(dp), parameter :: H_SCALE = 37300.0e3_dp          ! Scale height [m]
    
contains

    ! Compute atmospheric density using exponential model
    ! ρ(h) = ρ₀ * exp(-h/H)
    function atmospheric_density(r_sat) result(rho)
        real(dp), intent(in) :: r_sat(3)  ! Satellite position [m]
        real(dp) :: rho                    ! Atmospheric density [kg/m^3]
        real(dp) :: r_mag, h
        
        ! Compute altitude (spherical height)
        r_mag = sqrt(r_sat(1)**2 + r_sat(2)**2 + r_sat(3)**2)
        h = r_mag - R_EARTH
        
        ! Exponential density model
        rho = RHO_0 * exp(-h / H_SCALE)
        
    end function atmospheric_density
    
    ! Compute atmospheric drag acceleration
    ! Input: position vector r [m] and velocity vector v [m/s] in inertial frame
    ! Output: acceleration vector a_drag [m/s^2]
    function drag_acceleration(r_sat, v_sat) result(a_drag)
        real(dp), intent(in) :: r_sat(3), v_sat(3)
        real(dp) :: a_drag(3)
        real(dp) :: omega_vec(3), v_rel(3), v_rel_mag
        real(dp) :: rho
        
        ! Earth's angular velocity vector (aligned with z-axis)
        omega_vec(1) = 0.0_dp
        omega_vec(2) = 0.0_dp
        omega_vec(3) = omega_earth
        
        ! Relative velocity: v_rel = v_sat - ω_⊕ × r_sat
        ! Computing cross product: ω × r
        v_rel(1) = v_sat(1) - (omega_vec(2)*r_sat(3) - omega_vec(3)*r_sat(2))
        v_rel(2) = v_sat(2) - (omega_vec(3)*r_sat(1) - omega_vec(1)*r_sat(3))
        v_rel(3) = v_sat(3) - (omega_vec(1)*r_sat(2) - omega_vec(2)*r_sat(1))
        
        v_rel_mag = sqrt(v_rel(1)**2 + v_rel(2)**2 + v_rel(3)**2)
        
        ! Get atmospheric density
        rho = atmospheric_density(r_sat)
        
        ! Drag acceleration: a_drag = -1/2 * ρ * B * |v_rel| * v_rel
        a_drag = -0.5_dp * rho * BALLISTIC_COEFF * v_rel_mag * v_rel
        
    end function drag_acceleration

end module drag_perturbation
