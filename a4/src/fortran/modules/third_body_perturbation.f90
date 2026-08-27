module third_body_perturbation
    use gravity, only: dp
    implicit none
    
    ! Gravitational parameters [m^3/s^2]
    ! These will be loaded from file (Horizons data)
    real(dp) :: MU_SUN
    real(dp) :: MU_MOON
    
    ! Third body positions (geocentric, ICRF frame) [m]
    ! These will be loaded from file
    real(dp) :: SUN_X, SUN_Y, SUN_Z
    real(dp) :: MOON_X, MOON_Y, MOON_Z
    
contains

    ! Load third body positions from file
    subroutine load_third_body_positions()
        integer :: iostat, unit_num
        character(len=256) :: line
        
        unit_num = 15
        open(unit=unit_num, file='data/sgp4_reference/third_body_positions.txt', &
             status='old', action='read', iostat=iostat)
        
        if (iostat /= 0) then
            print *, "Error: Could not open third_body_positions.txt"
            print *, "Please run fetch_third_body_positions.py first"
            stop
        end if
        
        ! Read file line by line, skipping comments
        do
            read(unit_num, '(A)', iostat=iostat) line
            if (iostat /= 0) exit
            
            ! Skip empty lines and comments
            if (len_trim(line) == 0) cycle
            if (line(1:1) == '#') cycle
            
            ! First data line is Sun position and GM
            read(line, *) SUN_X, SUN_Y, SUN_Z, MU_SUN
            exit
        end do
        
        ! Read Moon position and GM (next non-comment line)
        do
            read(unit_num, '(A)', iostat=iostat) line
            if (iostat /= 0) exit
            
            ! Skip empty lines and comments
            if (len_trim(line) == 0) cycle
            if (line(1:1) == '#') cycle
            
            ! This is Moon position and GM
            read(line, *) MOON_X, MOON_Y, MOON_Z, MU_MOON
            exit
        end do
        
        close(unit_num)
        
    end subroutine load_third_body_positions
    
    ! Compute third body perturbation acceleration
    ! Uses the formula: a_3body = μ_body * [(r_body - r_sat)/|r_body - r_sat|^3 - r_body/|r_body|^3]
    ! 
    ! Input: r_sat - satellite position vector [m] in inertial frame
    ! Output: a_3body - third body acceleration vector [m/s^2]
    function third_body_acceleration(r_sat) result(a_3body)
        real(dp), intent(in) :: r_sat(3)
        real(dp) :: a_3body(3)
        real(dp) :: r_sun(3), r_moon(3)
        real(dp) :: r_sun_sat(3), r_moon_sat(3)
        real(dp) :: r_sun_mag, r_moon_mag
        real(dp) :: r_sun_sat_mag, r_moon_sat_mag
        real(dp) :: a_sun(3), a_moon(3)
        
        ! Sun position vector
        r_sun(1) = SUN_X
        r_sun(2) = SUN_Y
        r_sun(3) = SUN_Z
        
        ! Moon position vector
        r_moon(1) = MOON_X
        r_moon(2) = MOON_Y
        r_moon(3) = MOON_Z
        
        ! Relative position vectors: body - satellite
        r_sun_sat = r_sun - r_sat
        r_moon_sat = r_moon - r_sat
        
        ! Magnitudes
        r_sun_mag = sqrt(r_sun(1)**2 + r_sun(2)**2 + r_sun(3)**2)
        r_moon_mag = sqrt(r_moon(1)**2 + r_moon(2)**2 + r_moon(3)**2)
        r_sun_sat_mag = sqrt(r_sun_sat(1)**2 + r_sun_sat(2)**2 + r_sun_sat(3)**2)
        r_moon_sat_mag = sqrt(r_moon_sat(1)**2 + r_moon_sat(2)**2 + r_moon_sat(3)**2)
        
        ! Third body acceleration from Sun
        ! a_sun = μ_sun * [(r_sun - r_sat)/|r_sun - r_sat|^3 - r_sun/|r_sun|^3]
        a_sun = MU_SUN * (r_sun_sat / r_sun_sat_mag**3 - r_sun / r_sun_mag**3)
        
        ! Third body acceleration from Moon
        ! a_moon = μ_moon * [(r_moon - r_sat)/|r_moon - r_sat|^3 - r_moon/|r_moon|^3]
        a_moon = MU_MOON * (r_moon_sat / r_moon_sat_mag**3 - r_moon / r_moon_mag**3)
        
        ! Total third body acceleration
        a_3body = a_sun + a_moon
        
    end function third_body_acceleration

end module third_body_perturbation
