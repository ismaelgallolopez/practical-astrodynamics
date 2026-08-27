module objective_function
    use gravity, only: dp
    implicit none
    
    ! SGP4 reference orbit data (will be loaded from file)
    integer :: n_sgp4_steps
    real(dp), allocatable :: sgp4_times(:)        ! Time array [s]
    real(dp), allocatable :: sgp4_positions(:,:)  ! Positions [m], shape (3, n_steps)
    real(dp), allocatable :: sgp4_velocities(:,:) ! Velocities [m/s], shape (3, n_steps)
    
contains

    ! Load SGP4 reference orbit from file
    subroutine load_sgp4_reference(filename)
        character(len=*), intent(in) :: filename
        integer :: iostat, i, unit_num
        real(dp) :: dummy_jd, dummy_fr
        
        ! Open file
        unit_num = 15
        open(unit=unit_num, file=filename, status='old', action='read', iostat=iostat)
        if (iostat /= 0) then
            print *, "Error: Could not open SGP4 reference file: ", trim(filename)
            stop
        end if
        
        ! Count number of data lines (skip header comments)
        n_sgp4_steps = 0
        do
            read(unit_num, *, iostat=iostat)
            if (iostat /= 0) exit
            n_sgp4_steps = n_sgp4_steps + 1
        end do
        
        ! Allocate arrays
        allocate(sgp4_times(n_sgp4_steps))
        allocate(sgp4_positions(3, n_sgp4_steps))
        allocate(sgp4_velocities(3, n_sgp4_steps))
        
        ! Rewind and read data
        rewind(unit_num)
        do i = 1, n_sgp4_steps
            ! Format: time(s) x(m) y(m) z(m) vx(m/s) vy(m/s) vz(m/s)
            read(unit_num, *) sgp4_times(i), &
                              sgp4_positions(1, i), sgp4_positions(2, i), sgp4_positions(3, i), &
                              sgp4_velocities(1, i), sgp4_velocities(2, i), sgp4_velocities(3, i)
        end do
        
        close(unit_num)
        
        print *, "Loaded SGP4 reference orbit:"
        print *, "  Number of time steps: ", n_sgp4_steps
        print *, "  Time range [s]: ", sgp4_times(1), " to ", sgp4_times(n_sgp4_steps)
        
    end subroutine load_sgp4_reference
    
    ! Compute CGPD (Cumulative Global Position Difference) as RMS of position differences
    ! Inputs:
    !   - integrated_positions: (3, n_steps) array of integrated orbit positions [m]
    ! Output:
    !   - cgpd: RMS of position difference magnitudes [m]
    function compute_cgpd(integrated_positions, n_steps) result(cgpd)
        integer, intent(in) :: n_steps
        real(dp), intent(in) :: integrated_positions(3, n_steps)
        real(dp) :: cgpd
        
        real(dp) :: pos_diff(3)
        real(dp) :: pos_diff_mag
        real(dp) :: sum_squared_diff
        integer :: i, n_common
        
        ! Use the minimum of the two sizes to avoid out-of-bounds
        n_common = min(n_steps, n_sgp4_steps)
        
        if (abs(n_steps - n_sgp4_steps) > 1) then
            print *, "Warning: Significant mismatch in step count"
            print *, "  Integrated steps: ", n_steps
            print *, "  SGP4 steps: ", n_sgp4_steps
            print *, "  Using first ", n_common, " steps for comparison"
        end if
        
        sum_squared_diff = 0.0_dp
        
        do i = 1, n_common
            ! Compute position difference vector
            pos_diff = integrated_positions(:, i) - sgp4_positions(:, i)
            
            ! Compute magnitude of position difference
            pos_diff_mag = sqrt(pos_diff(1)**2 + pos_diff(2)**2 + pos_diff(3)**2)
            
            ! Accumulate squared differences
            sum_squared_diff = sum_squared_diff + pos_diff_mag**2
        end do
        
        ! Compute RMS
        cgpd = sqrt(sum_squared_diff / real(n_common, dp))
        
    end function compute_cgpd
    
    ! Cleanup memory
    subroutine cleanup_sgp4_reference()
        if (allocated(sgp4_times)) deallocate(sgp4_times)
        if (allocated(sgp4_positions)) deallocate(sgp4_positions)
        if (allocated(sgp4_velocities)) deallocate(sgp4_velocities)
    end subroutine cleanup_sgp4_reference

end module objective_function
