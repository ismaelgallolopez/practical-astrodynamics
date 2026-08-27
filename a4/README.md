<script>
  src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
  type="text/javascript">
</script>

# Assignment A4

Please carefully read the [rules](https://gitlab.tudelft.nl/ae4894-practical-astrodynamics/rules/-/blob/main/README.md). Remember that you have to create the `answer-sheet.yaml` file yourself and check that it is formatted correctly with the `answer-sheet-sanity.py` utility. You are also highly encouraged to get feedback with the [Formative Assessment online tool](https://spacegravimetry.tudelft.nl/PA/check.html).

You will find the answer keys in the assignment text below. They are all related uniquely to the task specified directly above the respective answer key. 

Please direct any questions to Brightspace, as it may be of help to your colleagues.

## Contents

[[_TOC_]]

## Objectives

This assignment intends to challenge you to implement disturbing forces in your orbit integrator and analyses their effect on the orbit.

### Use of libraries

You must not use any library that computes forces, orbital disturbances or celestial body locations. 

### Plotting for this assignment

Irrespective of the mandatory plots described below, you are encouraged to represent the residual orbit data in **alternative ways** in additional plots to aid in interpretation and conclusion.

#### Keplerian elements and their residuals

You are asked to compute the effect of different **disturbances**. This means that you must calculate the differences between the various *disturbed orbits* (under the effect of [J2](#Earths-oblateness), [SRP](#solar-radiation-pressure), and optionally [drag](#atmospheric-drag) and [TBP](#third-body-perturbations)) and the [*undisturbed orbit*](#perform-the-orbit-integration).

As was the case in assignment A3, all tasks ask you to produce 5 plots of the inclination, eccentricity, semi-major axis, argument of latitude and the right ascension of the ascending node in a single plot, each containing three lines referring to:

- the disturbed and undisturbed orbits in one y-axis, and
- the difference between the disturbed and undisturbed orbits in another y-axis.

Note that the disturbed and undisturbed orbits must have the same time domain to correctly calculated the 3rd line.

Implement this plotting capability as a **function** that receives two orbits in Cartesian coordinates, performs their conversion to Keplerian elements, computes their difference and produces the requested 5 plots. We'll refer to these plots as *Keplerian elements and their residuals*.

Report the source code where you compute the Keplerian elements and their residuals. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_OrbKepRes_SRC_0

ss_REG_OrbKepRes_CODE_2

#### Disturbance magnitudes

You are also asked to plot the magnitude of the acceleration caused by the various disturbances, as a function of time, along your undisturbed orbit. Implement this plotting capability as a **function** that receives a time series of acceleration vectors, computes their magnitude and produces the requested plot. We'll refer to this plot as *disturbance magnitudes*.

Report the source code where you implement the plot(s) requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_MagPlot_SRC_0

ss_REG_MagPlot_CODE_1


### Reference frames

The intention in all tasks of this assignment is for the integration to be done in the inertial frame. Therefore, all forces need to be converted back to the inertial frame, so that the integration can take place without having to account for the Coriolis, Euler or Centrifugal acceleration terms.

Unlike Earth's gravity, Solar Radiation Pressure (SRP) and third-body perturbations (TBP) depend only on the state of the satellite and another body, which can be expressed in an inertial frame of reference. The rotation of Earth's atmosphere complicates drag, but that's a velocity vector that can be easily expressed in the inertial frame.

With Earth's gravity, there is a need to calculate these disturbances in an Earth-co-rotating frame, because the origin of those disturbances is also rotating with the Earth. The $J_2$ coefficient and all zonal coefficients are a particular case in Earth's gravity because the effect of longitude is homogeneous. This happens to make it possible for us to immediately express this disturbance in the inertial frame, as was done for $J_2$ in the slide entitled "Disturbance caused by Earth’s oblateness" of lecture 4. 

For $J_{2,2}$, and all non-zonal coefficients, longitude matters as much as latitude. For this assignment, you are not tasked to consider non-zonal coefficients, and this issue is irrelevant.

### Programming language

Report the name of the programming language you used to solve this assignment:

ss_REG_Language_GEN_0

## Tasks

### Retrieve the TLE data

Go to [celestrak](https://celestrak.org/satcat/search.php) and report the updated TLE data of the Earth-orbiting objects you chose in assignment A1.

TLE data:

ls_MDT_TLE_GEN_0

### Update your orbit

Use the SGP4 propagator to generate the position and velocity of your satellite. We'll refer to this as the *SGP4 orbit*.

Report the parameters that define your time domain. The initial and final times are relative to the TLE epoch. You may select the start/stop times, as well as the integration time step, provided that they comply with the stated [rules](https://gitlab.tudelft.nl/ae4894-practical-astrodynamics/rules/-/blob/main/README.md#reporting-start-and-stop-times-of-the-sgp4-integration).

- Initial time in seconds: sf_MDT_OrbTimeIni_NUM_0
- Final time in seconds: sf_MDT_OrbTimeEnd_NUM_0
- The time step in seconds: sf_MDT_OrbTimeStep_NUM_0

Report the initial and final positions (in meters) and velocities (in meters per second) of the S/C as represented by the SGP4 orbit.

- Initial 3D position: lf_REG_OrbPosIni_NUM_0
- Initial 3D velocity: lf_REG_OrbVelIni_NUM_0
- Final 3D position: lf_REG_OrbPosEnd_NUM_1
- Final 3D velocity: lf_REG_OrbVelEnd_NUM_1

For this assignment, the SGP4 orbit is not longer relevant.

### Perform the orbit integration 

Use the Euler or another integrator **you implemented in assignment A3**, to reproduce the orbit from *[Update your orbit](#update-your-orbit)*, with the same start/stop/step times and initial state vector as the SGP4 orbit. We'll refer to this as the *undisturbed orbit*.

Report the name of the integration algorithm you used, e.g., "Euler" or "RK4" (amongst any other you implemented).

ss_MDT_Integrator_GEN_0

Report the initial and final positions (in meters) and velocities (in meters per second) of the S/C as represented by the undisturbed orbit.

- Initial 3D position: lf_REG_IntPosIni_NUM_0
- Initial 3D velocity: lf_REG_IntVelIni_NUM_0
- Final 3D position: lf_REG_IntPosEnd_NUM_0.85
- Final 3D velocity: lf_REG_IntVelEnd_NUM_0.85

### Plot the Keplerian elements

Represent the Keplerian elements of the SGP4 orbit in two plots, showing (at least) the following as a function of time:

- The first plot with the inclination, eccentricity and semi-major axis, in 3 different y-axes;
- The second plot with the argument of latitude (i.e., the true anomaly plus argument of pericenter) and the right ascension of the ascending node, in 2 different y-axes.

Report the filename(s) of your plot(s).

ls_REG_OrbKepPlotFile_PLOT_1

Represent the Keplerian elements of the undisturbed orbit, showing the same quantities as above. Report the filename(s) of your plot(s).

ls_REG_EulerKepPlotFile_PLOT_1

For this assignment, the SGP4 orbit will not be relevant any more.

### Earth's oblateness

#### Implement the gravitational disturbance resulting from Earth's oblateness

Implement a **function** that computes the gravity disturbance from $`J_2`$ as a function of the Cartesian coordinates of the orbital position in the inertial frame. Assume the $`J_2`$ geopotential coefficient is equal to $`1.083\times 10^{-3}`$, Earth's gravitational parameter equal to $`GM=398600.4418 km^3/s^2`$ and Earth's mean radius is $`R = 6371 km`$. 

Report the source code where you implement the function requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_J2_SRC_0

ss_REG_J2_CODE_2.5

#### Perform the orbit integration under the effect of Earth's oblateness

Add the routine you implemented in the previous task to your propagator. Assume that the only gravitational disturbance affecting the orbit of your satellite is due to Earth's oblateness, and compute the resulting orbit, considering the state given by the first epoch of the undisturbed orbit as initial conditions.

Report the initial and final positions (in meters) and velocities (in meters per second) of the S/C under the influence of $`J_2`$.

- Initial 3D position: lf_REG_J2PosIni_NUM_0
- Initial 3D velocity: lf_REG_J2VelIni_NUM_0
- Final 3D position: lf_REG_J2PosEnd_NUM_0.85
- Final 3D velocity: lf_REG_J2VelEnd_NUM_0.85

#### Plot the effect of Earth's oblateness in your orbit

Plot the [Keplerian elements and their residuals](#keplerian-elements-and-their-residuals) between the undisturbed orbit and the orbit disturbed by $`J_2`$. 

Report the filename(s) of your plot(s).

ls_REG_J2Orb_PLOT_5

#### Plot the magnitude of the accelerations from Earth's oblateness along your orbital positions

Plot the $`J_2`$ [disturbance magnitudes](#disturbance-magnitudes).

Report the filename(s) of your plot(s).

ls_REG_J2Mag_PLOT_2

#### Analyse the results related to the effect of Earth's oblateness

Regarding the plot(s) in the two tasks above:

- Make (at least) three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_REG_J2Obs_OIC_6

- Make (at least) two interpretations about the observations you reported above.

ss_REG_J2Int_OIC_8

- Make (at least) one conclusion based on the observations and interpretations you reported above.

ss_REG_J2Con_OIC_10

### Solar Radiation Pressure

#### Determine the position of the Sun

Using the example script [horizons_script.py](./horizon-tool/horizons_script.py), report the 3D position of the Sun relative to the centre of the Earth, as provided by the [Horizons System](https://ssd.jpl.nasa.gov/horizons/), in meters, at the start of the calendar day of the TLE epoch.

lf_REG_SunPos_NUM_0.9

#### Implement the SRP disturbance

Consider the following assumptions:

- Your satellite is a perfect sphere,
- Its radiation pressure ballistic coefficient is $`0.02 m^2/kg`$, 
- The Sun is assumed to remain at the same position relative to Earth during the orbit integration and equal to the value you reported in the section [above](#determine-the-position-of-the-sun),
- The solar radiation flux is $`1361 W/m^2`$, and
- The solar illumination of the satellite follows the shadow function proposed by Doornbos (2012)[Thermospheric Density and Wind Determination from Satellite Dynamics](https://resolver.tudelft.nl/uuid:08e4faa1-a38b-43a8-989a-a70b78d59e58), pp. 58 to 61, including the effect of penumbra given by the geometric shadowing factor $`f_g`$ given by Eq. 3.32 of Doornbos (2012), with no absorption of solar flux by Earth's atmosphere (the factor $`f_a`$ in Eq. 3.31 of Doornbos (2012) is 1).

Implement a **function** that computes the SRP acceleration as a function of the Cartesian coordinates of the orbital position in the inertial frame.

Report the source code where you implement the function requested above. Make sure you include the code relevant only to this task.

Source code filename: ls_MDT_SRP_SRC_0

ss_REG_SRP_CODE_2.5

#### Perform the orbit integration under the effect of SRP

Add the routine you implemented in the previous task to your propagator. Assume that the only gravitational disturbance affecting the orbit of your satellite is due to SRP and compute the resulting orbit, considering the state given by the first epoch of the undisturbed orbit as initial conditions. This means you will have to turn off the effect of $`J_2`$ that you implemented earlier in this assignment.

Report the initial and final positions (in meters) and velocities (in meters per second) of the S/C under the influence of SRP.

- Initial 3D position: lf_REG_SRPPosIni_NUM_0
- Initial 3D velocity: lf_REG_SRPVelIni_NUM_0
- Final 3D position: lf_REG_SRPPosEnd_NUM_0.85
- Final 3D velocity: lf_REG_SRPVelEnd_NUM_0.85

#### Plot the effect of SRP in your orbit

Plot the [Keplerian elements and their residuals](#keplerian-elements-and-their-residuals) between the undisturbed orbit and the orbit disturbed by SRP. 

Report the filename(s) of your plot(s).

ls_REG_SRPOrb_PLOT_5

#### Plot the magnitude of the acceleration from SRP along your orbital positions

Plot the SRP [disturbance magnitudes](#disturbance-magnitudes).

Report the filename(s) of your plot(s).

ls_REG_SRPMag_PLOT_2

#### Analyse the results related to the effect of SRP

Regarding the plot(s) in the two tasks above:

- Make (at least) three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_REG_SRPObs_OIC_6

- Make (at least) two interpretations about the observations you reported above.

ss_REG_SRPInt_OIC_8

- Make (at least) one conclusion based on the observations and interpretations you reported above.

ss_REG_SRPCon_OIC_10


## Assignment excellence

### Atmospheric drag

#### Implement the disturbance resulting from atmospheric drag

Consider the following assumptions:

- Your satellite is a perfect sphere,
- Its ballistic coefficient is $`0.01 m^2/kg`$, and 
- Earth's atmosphere is spherical and its density follows the exponential density distribution $`\rho(h)=\rho_0 e^{-h/H}`$, with the mean density $`\rho_0`$ and scale height $` H`$ retrieved from the table in [Appendix](#scale-heights-and-mean-densities).

Report the reference height you consider in your implementation of drag, in meters.

sf_AEX_RefHeight_GEN_0.1

Report the scale height you consider in your implementation of drag, in meters.

sf_AEX_ScaleHeight_GEN_0.1

Report the mean density you consider in your implementation of drag, in $`kg/m^3`$.

sf_AEX_MeanRho_GEN_0.1

Implement a **function** that computes the drag acceleration as a function of the Cartesian coordinates of the orbital position and velocity in the inertial frame. Don't forget to include the effect of the rotating atmosphere.

Report the source code where you implement the function requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_AEX_Drag_SRC_0.1

ss_AEX_Drag_CODE_0.8

#### Perform the orbit integration under the effect of drag

Add the routine you implemented in the previous task to your propagator. Assume that the only gravitational disturbance affecting the orbit of your satellite is due to drag, and compute the resulting orbit, considering the state given by the first epoch of the undisturbed orbit as initial conditions. This means you will have to turn off the effect of $`J_2`$ and SRP that you implemented earlier in this assignment.

Report the initial and final positions (in meters) and velocities (in meters per second) of the S/C under the influence of drag.

- Initial 3D position: lf_AEX_DragPosIni_NUM_0
- Initial 3D velocity: lf_AEX_DragVelIni_NUM_0
- Final 3D position: lf_AEX_DragPosEnd_NUM_0.2
- Final 3D velocity: lf_AEX_DragVelEnd_NUM_0.2

#### Plot the effect of drag in your orbit

Plot the [Keplerian elements and their residuals](#keplerian-elements-and-their-residuals) between the undisturbed orbit and the orbit disturbed by drag. 

Report the filename(s) of your plot(s).

ls_AEX_DragOrb_PLOT_1

#### Plot the magnitude of drag along your orbital positions

Plot the drag [disturbance magnitudes](#disturbance-magnitudes).

Report the filename(s) of your plot(s).

ls_AEX_DragMag_PLOT_0.5

#### Analyse the results related to the effect of drag

Regarding the plot(s) in the two task above:

- Make (at least) three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_AEX_DragObs_OIC_1

- Make (at least) two interpretations about the observations you reported above.

ss_AEX_DragInt_OIC_2

- Make (at least) one conclusion based on the observations and interpretations you reported above.

ss_AEX_DragCon_OIC_4

### Third body perturbations (TBP)

#### Determine the position of the Moon

Using the example script [horizons_script.py](./horizon-tool/horizons_script.py), report the 3D position of the Moon relative to the centre of the Earth, as provided by the [Horizons System](https://ssd.jpl.nasa.gov/horizons/), in meters, at the start of the calendar day of the TLE epoch.

lf_AEX_MoonPos_NUM_0.1

Consider the position of the Sun the same as in the Task ["Determine the position of the Sun"](#determine-the-position-of-the-sun).

#### Implement the disturbance resulting from TBP

Implement a **function** that computes the gravitational attraction of the Sun and Moon as a function of the Cartesian coordinates of the orbital position in the inertial frame. 

Report the source code where you implement the function requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_AEX_TBP_SRC_0.1

ss_AEX_TBP_CODE_0.8

#### Perform the orbit integration under the effect of TBP

Add the routine you implemented in the previous task to your propagator. Assume that the only gravitational disturbance affecting the orbit of your satellite is due to TBP and compute the resulting orbit, considering the state given by the first epoch of the undisturbed orbit as initial conditions. This means you will have to turn off the effect of $`J_2`$, SRP and drag that you implemented earlier in this assignment.

Report the initial and final positions (in meters) and velocities (in meters per second) of the S/C under the influence of TBP.

- Initial 3D position: lf_AEX_TBPPosIni_NUM_0
- Initial 3D velocity: lf_AEX_TBPVelIni_NUM_0
- Final 3D position: lf_AEX_TBPPosEnd_NUM_0.2
- Final 3D velocity: lf_AEX_TBPVelEnd_NUM_0.2

#### Plot the effect of TBP in your orbit

Plot the [Keplerian elements and their residuals](#keplerian-elements-and-their-residuals) between the undisturbed orbit and the orbit disturbed by TBPs. 

Report the filename(s) of your plot(s).

ls_AEX_TBPOrb_PLOT_1

#### Plot the magnitude of the accelerations from TBP along your orbital positions

Plot the TBP [disturbance magnitudes](#disturbance-magnitudes).

Report the filename(s) of your plot(s).

ls_AEX_TBPMag_PLOT_0.5

#### Analyse the results related to the effect of TBP

Regarding the plot(s) in the task [above](#plot-the-magnitude-of-tbp-along-your-orbital-positions):

- Make (at least) three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_AEX_TBPObs_OIC_1

- Make (at least) two interpretations about the observations you reported above.

ss_AEX_TBPInt_OIC_2

- Make (at least) one conclusion based on the observations and interpretations you reported above.

ss_AEX_TBPCon_OIC_4


## Code excellence

Report below any advanced coding features you have implemented in your code.

ss_CEX_Explain_GEN_10

## AI use

Irrespective of the use of AI, you are responsible for the code, plots, answers and statements you submit.

If you use AI:
- You must vet and guarantee your results, i.e., be critical of AI output and verify it against non-AI sources. 
- AI must augment, not replace, your efforts. Do not use AI output directly.

Explain, motivate and substantiate how you used AI. If you leave this answer empty (it still needs to be in your answer sheet since it is an `MDT` answer), it means you are implicitly declaring you did not use AI in any way.

ss_MDT_AI_GEN_0

## Final remarks

Report the time, in hours, that it took you to solve the assignment.

sf_REG_WORKLOAD_GEN_0

Please provide feedback on the assignment, namely how interesting you found it and how challenging it was to answer. Suggestions are welcome.

ss_REG_FEEDBACK_GEN_0

## Appendix

### Scale heights and mean densities

This table has been retrieved from [here](http://www.braeunig.us/space/atmos.htm). 

Do not interpolate these values. Find the highest altitude that is below your orbital altitude (assume the mean Earth radius to compute this) in the first column, and retrieve the Scale Height in the second column and the Mean Density in the third column.

The maximum density only applies during solar maximum; please assume mean density in your calculations.

|Altitude (km)|Scale Height (km)|Mean Density (kg/m3)|Maximum Density (kg/m3)|
|---|---|---|---|
| 0 | 8.4 | 1.225 | 1.225 |
| 100 | 5.9 | 5.25E-7 | 5.75E-7 |
| 150 | 25.5 | 1.73E-9 | 1.99E-9 |
| 200 | 37.5 | 2.41E-10 | 3.65E-10 |
| 250 | 44.8 | 5.97E-11 | 1.20E-10 |
| 300 | 50.3 | 1.87E-11 | 4.84E-11 |
| 350 | 54.8 | 6.66E-12 | 2.18E-11 |
| 400 | 58.2 | 2.62E-12 | 1.05E-11 |
| 450 | 61.3 | 1.09E-12 | 5.35E-12 |
| 500 | 64.5 | 4.76E-13 | 2.82E-12 |
| 550 | 68.7 | 2.14E-13 | 1.53E-12 |
| 600 | 74.8 | 9.89E-14 | 8.46E-13 |
| 650 | 84.4 | 4.73E-14 | 4.77E-13 |
| 700 | 99.3 | 2.36E-14 | 2.73E-13 |
| 750 | 121 | 1.24E-14 | 1.59E-13 |
| 800 | 151 | 6.95E-15 | 9.41E-14 |
| 850 | 188 | 4.22E-15 | 5.67E-14 |
| 900 | 226 | 2.78E-15 | 3.49E-14 |
| 950 | 263 | 1.98E-15 | 2.21E-14 |
| 1,000 | 296 | 1.49E-15 | 1.43E-14 |
| 1,250 | 408 | 5.70E-16 | 2.82E-15 |
| 1,500 | 516 | 2.79E-16 | 1.16E-15 |
| 2,000 | 829 | 9.09E-17 | 3.80E-16 |
| 2,500 | 1220 | 4.23E-17 | 1.54E-16 |
| 3,000 | 1590 | 2.54E-17 | 7.09E-17 |
| 3,500 | 1900 | 1.77E-17 | 3.67E-17 |
| 4,000 | 2180 | 1.34E-17 | 2.11E-17 |
| 4,500 | 2430 | 1.06E-17 | 1.34E-17 |
| 5,000 | 2690 | 8.62E-18 | 9.30E-18 |
| 6,000 | 3200 | 6.09E-18 | 5.41E-18 |
| 7,000 | 3750 | 4.56E-18 | 3.74E-18 |
| 8,000 | 4340 | 3.56E-18 | 2.87E-18 |
| 9,000 | 4970 | 2.87E-18 | 2.34E-18 |
| 10,000 | 5630 | 2.37E-18 | 1.98E-18 |
| 15,000 | 9600 | 1.21E-18 | 1.16E-18 |
| 20,000 | 14600 | 7.92E-19 | 8.42E-19 |
| 25,000 | 20700 | 5.95E-19 | 6.81E-19 |
| 30,000 | 27800 | 4.83E-19 | 5.84E-19 |
| 35,000 | 36000 | 4.13E-19 | 5.21E-19 |
| 35,786 | 37300 | 4.04E-19 | 5.12E-19 |
