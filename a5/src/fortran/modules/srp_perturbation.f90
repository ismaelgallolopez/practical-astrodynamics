module srp_perturbation
    implicit none
    
    ! Parameters
    integer, parameter :: dp = selected_real_kind(15, 307)
    real(dp), parameter :: PI = acos(-1.0_dp)
    real(dp), parameter :: R_EARTH = 6371.0e3_dp           ! Earth's mean radius [m]
    real(dp), parameter :: SOLAR_FLUX = 1361.0_dp          ! Solar radiation flux [W/m^2]
    real(dp), parameter :: C_LIGHT = 299792458.0_dp        ! Speed of light [m/s]
    real(dp), parameter :: CR_OVER_M = 0.02_dp             ! Radiation pressure ballistic coefficient [m^2/kg]
    
    ! Sun position (geocentric, ICRF frame) [m] - will be read from file
    real(dp), save :: SUN_X, SUN_Y, SUN_Z
    real(dp), save :: R_SUN  ! Sun radius [m] - will be read from file
    logical, save :: sun_position_loaded = .false.
    
contains

    ! Load Sun position from file
    subroutine load_sun_position()
        integer :: iostat, unit_num
        character(len=256) :: line
        character(len=256) :: sun_file
        real(dp) :: gm_sun  ! GM value (not used in SRP but need to read)
        
        ! Only load once
        if (sun_position_loaded) return
        
        unit_num = 15
        
        ! Try path from workspace root first
        sun_file = 'data/sgp4_reference/third_body_positions.txt'
        open(unit=unit_num, file=trim(sun_file), status='old', action='read', iostat=iostat)
        
        ! If that fails, try path from build directory
        if (iostat /= 0) then
            sun_file = '../../../data/sgp4_reference/third_body_positions.txt'
            open(unit=unit_num, file=trim(sun_file), status='old', action='read', iostat=iostat)
        end if
        
        if (iostat /= 0) then
            print *, "Error: Could not open third body positions file: ", trim(sun_file)
            print *, "Please run: python src/python/fetch_third_body_positions.py"
            stop
        end if
        
        ! Read comment lines to extract Sun radius
        R_SUN = 6.96e8_dp  ! Default value
        do
            read(unit_num, '(A)', iostat=iostat) line
            if (iostat /= 0) then
                print *, "Error reading third body positions file"
                close(unit_num)
                stop
            end if
            
            ! Check for Sun radius line
            if (index(line, '# Sun radius:') > 0) then
                read(line(15:), *, iostat=iostat) R_SUN
            end if
            
            ! Skip empty lines and comments to find first data line
            if (len_trim(line) == 0 .or. line(1:1) == '#') cycle
            
            ! First data line is Sun position and GM
            read(line, *, iostat=iostat) SUN_X, SUN_Y, SUN_Z, gm_sun
            exit
        end do
        
        if (iostat /= 0) then
            print *, "Error parsing Sun position data"
            close(unit_num)
            stop
        end if
        
        close(unit_num)
        
        sun_position_loaded = .true.
        
        print *, "Sun position loaded from file:"
        print *, "  X = ", SUN_X, " m"
        print *, "  Y = ", SUN_Y, " m"
        print *, "  Z = ", SUN_Z, " m"
        print *, "  R_sun = ", R_SUN, " m"
        print *, ""
        
    end subroutine load_sun_position

    ! Compute geometric shadowing factor following Doornbos (2012) Eq. 3.27-3.34
    ! This implements the penumbra model with proper geometric calculation
    function geometric_shadow_factor(r_sat) result(f_g)
        real(dp), intent(in) :: r_sat(3)  ! Satellite position [m]
        real(dp) :: f_g                    ! Geometric shadowing factor [0, 1]
        real(dp) :: r_sun_vec(3), e_sun(3), e_i(3)
        real(dp) :: r_i, r_earth_sun_vec(3), r_circle_s(3)
        real(dp) :: r_ps(3), r_circle_p(3), h_g, R_p, eta
        real(dp) :: r_ps_mag, r_circle_s_mag
        
        ! Load Sun position if not already loaded
        if (.not. sun_position_loaded) then
            call load_sun_position()
        end if
        
        ! Following equations 27-32 from the slide:
        ! r_i = ||r_sat||, e_i = r_sat/r_i, r_circle_s = r_sat (Eq. 27)
        r_i = sqrt(r_sat(1)**2 + r_sat(2)**2 + r_sat(3)**2)
        e_i(1) = r_sat(1) / r_i
        e_i(2) = r_sat(2) / r_i
        e_i(3) = r_sat(3) / r_i
        r_circle_s = r_sat  ! Position of satellite
        
        ! Sun position vector (geocentric, from Earth to Sun)
        r_sun_vec(1) = SUN_X
        r_sun_vec(2) = SUN_Y
        r_sun_vec(3) = SUN_Z
        r_circle_s_mag = sqrt(r_sun_vec(1)**2 + r_sun_vec(2)**2 + r_sun_vec(3)**2)
        
        ! Unit vector from Earth to Sun
        e_sun(1) = r_sun_vec(1) / r_circle_s_mag
        e_sun(2) = r_sun_vec(2) / r_circle_s_mag
        e_sun(3) = r_sun_vec(3) / r_circle_s_mag
        
        ! r_⊙s = r_⊕s - r_⊕⊙ (Eq. 27) - vector from Sun to Earth center
        r_earth_sun_vec(1) = -r_sun_vec(1)
        r_earth_sun_vec(2) = -r_sun_vec(2)
        r_earth_sun_vec(3) = -r_sun_vec(3)
        
        ! r_ps = (e_⊙s · r_⊕s)e_⊙s (Eq. 28) - projection onto Sun-Earth axis
        ! Note: e_⊙s points from Sun to Earth, so use -e_sun
        r_ps_mag = -(e_sun(1)*r_sat(1) + e_sun(2)*r_sat(2) + e_sun(3)*r_sat(3))
        r_ps(1) = -r_ps_mag * e_sun(1)
        r_ps(2) = -r_ps_mag * e_sun(2)
        r_ps(3) = -r_ps_mag * e_sun(3)
        
        ! r_⊕p = r_⊕s - r_ps (Eq. 29) - perpendicular component
        r_circle_p(1) = r_sat(1) - r_ps(1)
        r_circle_p(2) = r_sat(2) - r_ps(2)
        r_circle_p(3) = r_sat(3) - r_ps(3)
        
        ! h_g = r_⊕p - R_⊕ (Eq. 30) - altitude above Earth surface in perpendicular plane
        h_g = sqrt(r_circle_p(1)**2 + r_circle_p(2)**2 + r_circle_p(3)**2) - R_EARTH
        
        ! R_p = (r_ps / r_⊙s) * R_⊙ (Eq. 31) - shadow cone radius at satellite distance
        R_p = (sqrt(r_ps(1)**2 + r_ps(2)**2 + r_ps(3)**2) / r_circle_s_mag) * R_SUN
        
        ! η = h_g / R_p (Eq. 32)
        eta = h_g / R_p
        
        ! Apply shadow conditions based on eta (Eq. 33)
        ! eta = h_g / R_p measures how far satellite is from shadow boundary
        ! eta >> 1: satellite far outside shadow cone (sunlight)
        ! |eta| < 1: satellite near shadow boundary (penumbra/umbra)  
        ! eta << -1: satellite inside Earth cylinder (impossible for orbits)
        if (eta < -1.0_dp) then
            ! Umbra (satellite inside Earth cylinder relative to shadow cone)
            f_g = 0.0_dp
        else if (eta >= -1.0_dp .and. eta <= 1.0_dp) then
            ! Penumbra - calculate fractional area blocked (Eq. 34)
            f_g = 1.0_dp - (1.0_dp/PI) * acos(eta) - (eta/PI) * sqrt(1.0_dp - eta**2)
        else  ! eta > 1
            ! Full sunlight (satellite outside shadow cone)
            f_g = 1.0_dp
        end if
        
    end function geometric_shadow_factor
    
    ! Compute SRP acceleration
    ! Input: position vector r [m] in inertial frame (ICRF)
    ! Output: acceleration vector a_srp [m/s^2]
    function srp_acceleration(r_sat) result(a_srp)
        real(dp), intent(in) :: r_sat(3)
        real(dp) :: a_srp(3)
        real(dp) :: r_sun(3), r_sun_to_sat(3), r_sun_to_sat_mag
        real(dp) :: f_g, f_a, P_srp
        real(dp) :: unit_sun_to_sat(3)
        
        ! Load Sun position if not already loaded
        if (.not. sun_position_loaded) then
            call load_sun_position()
        end if
        
        ! Sun position vector (geocentric, ICRF)
        r_sun(1) = SUN_X
        r_sun(2) = SUN_Y
        r_sun(3) = SUN_Z
        
        ! Vector from Sun to satellite
        r_sun_to_sat = r_sat - r_sun
        r_sun_to_sat_mag = sqrt(r_sun_to_sat(1)**2 + r_sun_to_sat(2)**2 + r_sun_to_sat(3)**2)
        
        ! Unit vector from Sun to satellite
        unit_sun_to_sat = r_sun_to_sat / r_sun_to_sat_mag
        
        ! Geometric shadowing factor (penumbra model)
        f_g = geometric_shadow_factor(r_sat)
        
        ! Atmospheric absorption factor (set to 1.0 as per problem statement)
        f_a = 1.0_dp
        
        ! Solar radiation pressure at satellite distance
        ! P = (Φ / c) * f_a * f_g
        P_srp = (SOLAR_FLUX / C_LIGHT) * f_a * f_g
        
        ! SRP acceleration: a = (C_R * A / m) * P * ê_sun
        ! where ê_sun is unit vector from Sun to satellite
        a_srp = CR_OVER_M * P_srp * unit_sun_to_sat
        
    end function srp_acceleration

end module srp_perturbation
