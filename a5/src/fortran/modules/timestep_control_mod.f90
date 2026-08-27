!==============================================================================
! Module for time step control
!==============================================================================
module timestep_control_mod
    use gravity, only: dp
    implicit none
    
    real(dp) :: global_dt, global_tstop, global_r0(3), global_v0(3)
    
contains
    
    subroutine set_global_params(dt, tstop, r0, v0)
        real(dp), intent(in) :: dt, tstop, r0(3), v0(3)
        global_dt = dt
        global_tstop = tstop
        global_r0 = r0
        global_v0 = v0
    end subroutine set_global_params
    
end module timestep_control_mod
