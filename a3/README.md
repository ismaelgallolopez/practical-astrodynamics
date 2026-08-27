<script>
  src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
  type="text/javascript">
</script>

# Assignment A3

Please carefully read the [rules](https://gitlab.tudelft.nl/ae4894-practical-astrodynamics/rules/-/blob/main/README.md). Remember that you have to create the `answer-sheet.yaml` file yourself and check that it is formatted correctly with the `answer-sheet-sanity.py` utility. You are also highly encouraged to get feedback with the [Formative Assessment online tool](https://spacegravimetry.tudelft.nl/PA/check.html).

You will find the answer keys in the assignment text below. They are all related uniquely to the task specified directly above the respective answer key. 

Please direct any questions to Brightspace, as it may be of help to your colleagues.

## Contents

[[_TOC_]]

## Objectives

This assignment intends to challenge you to implement numerical integration yourself.

### Use of libraries

You must not use any ODE library, numerical integration routine, or any other implementation of an integrator that you do not author.

### Reporting differences

You will be asked to compute the **global position difference** (GPD) and **cumulative global position difference** (CGPD). Please use the L2 norm to compute the GPD and the RMS over time of these quantities to calculate the CGPD for the entire time domain.

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

### Implement the point-mass gravitational model

Implement a function that computes the 3D gravitational acceleration as a function of position, resulting from a point mass as massive as the Earth.

Report the source code where you implement the 3D gravitational acceleration as a function of position. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_Grav_SRC_0

ss_REG_Grav_CODE_1

### Implement the Euler integrator

Implement an Euler integrator that receives:

- initial state vector: 3D position and velocity,
- time step (scalar),
- stop time (scalar), and
- the function that computes the 3D gravitational acceleration as a function of position.

Report the source code where you implement the Euler integrator. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_Euler_SRC_0

ss_REG_Euler_CODE_1

### Perform the orbit integration

Use this Euler integrator to compute the successive positions and velocities under the influence of the gravitational attraction of a point mass as massive as Earth, so as to reproduce the orbit from *[Update your orbit](#update-your-orbit)*, in the form of the henceforth called *integrated orbit*:

- for initial state vector, use the first data point of the SGP4 orbit (given in Cartesian coordinates);
- use the same start time as in Task [Update your orbit](#update-your-orbit).

Choose your integration step length and the stop time such that a complete orbit integration does not take longer than 10 seconds.

- Final time in seconds: sf_MDT_EulerTimeEnd_NUM_0
- The time step in seconds: sf_MDT_EulerTimeStep_NUM_0

When measuring CPU time, only include the integration process; exclude reading or writing orbital data, as well as any other unrelated operations, such as printing to the screen. Report the total CPU time your integrator takes to produce the orbit, in terms of seconds.

sf_REG_EulerTimeTotal_NUM_0.5

Report the average computational time per integration step, in terms of seconds.

sf_REG_EulerTimeEff_NUM_0.5

Report the initial and final positions (in meters) and velocities (in meters per second) of the S/C.

- Initial 3D position: lf_REG_EulerPosIni_NUM_0
- Initial 3D velocity: lf_REG_EulerVelIni_NUM_0
- Final 3D position: lf_REG_EulerPosEnd_NUM_2
- Final 3D velocity: lf_REG_EulerVelEnd_NUM_2

### Plot the Keplerian elements

Represent the Keplerian elements of the SGP4 orbit in two plots, showing (at least) the following as a function of time:

- The first plot with the inclination, eccentricity and semi-major axis, in 3 different y-axes;
- The second plot with the true anomaly plus argument of pericenter and the right ascension of the ascending node, in 2 different y-axes.

Report the filename(s) of your plot(s).

ls_REG_OrbKepPlotFile_PLOT_1

Represent the Keplerian elements of the integrated orbit, showing the same quantities as above. Report the filename(s) of your plot(s).

ls_REG_EulerKepPlotFile_PLOT_1

### Assess the difference between the integrated and SGP4 orbits

Implement a routine that computes the GPD between two orbits, as a function of time. To do this, calculate the difference between the integrated and SGP4 orbital positions, then compute the magnitude (i.e., the length or L2 norm) of the resulting position residual, **independently for each epoch**. If needed, recompute the SGP4 orbit with the the stop and step times that you used in the integrated orbit. 

Report the source code where you implement the routine requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_GlobErr_SRC_0

ss_REG_GlobErr_CODE_2

Produce 2 plots:

- the GPD between the integrated and SGP4 orbit and 
- the position magnitude of the integrated orbit,

... both as a function of time and for (at least) two different step sizes. For the first plot, you need to regenerate the SGP4 orbit (from the same TLE data, i.e., the initial state vector remains the same in all orbit integrations) with the new time domain resulting from a different step size. Note that if the step sizes are vastly different, one of the lines of the GPD plot may be too small compared to the other and not clearly visible in the plot. You may use a logarithmic scale on the y-axis to make both lines clearly visible. Conversely, if the step size is too close, there may not be enough difference between the two lines.

Report the step sizes you considered above.

lf_MDT_GlobErrSteps_NUM_0.5

You are encouraged to represent the (residual) orbit data in **alternative ways** in additional plots to aid in interpretation and conclusion.

Produce 5 additional plots, with the inclination, eccentricity, semi-major axis, true anomaly plus argument of pericenter and the right ascension of the ascending node. In every plot, show three lines referring to:

- the SGP4 orbit and the integrated orbit in one y-axis, and
- the difference between the SGP4 and integrated orbit in another y-axis.

Note that the time domain of the integrate orbit must be the same as the SGP4 orbit for the 3rd line.

Report the source code where you implement the plots requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_GlobErrPlot_SRC_0

ss_REG_GlobErrPlot_CODE_2

Report the filename(s) of your plot(s).

ls_REG_GlobErr_PLOT_7

Plot the CGPD at the last integration time as a function of different step sizes used in your Euler integrator. Consider at least 10 different values of step size spanning at least 2 orders of magnitude.

Report all step sizes you considered above.

lf_MDT_CumGlobErrSteps_NUM_0.5

Report the source code where you implement the plot(s) requested above, and compute the CGPD. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_CumGlobErrPlot_SRC_0

ss_REG_CumGlobErrPlot_CODE_2

Report the filename(s) of your plot(s).

ls_REG_CumGlobErr_PLOT_7

### Analyse the difference between the integrated and SGP4 orbits

Regarding the plot(s) in the task [above](#assess-the-difference-between–the-integrated-and-sgp4-orbits):

- Make three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_REG_OrbObs_OIC_10

- Make two interpretations about the observations you reported above.

ss_REG_OrbInt_OIC_15

- Make one conclusion based on the observations and interpretations you reported above.

ss_REG_OrbCon_OIC_23

## Assignment excellence

### Implement an alternative integration algorithm

Implement an alternative integration algorithm. If the algorithm you picked is listed below, please use that string to answer this question. Replace `o` with the order or `s` with the steps of that algorithm.

- Runge-Kutta `o`
- Heun
- Ralston
- Runge–Kutta–Fehlberg
- Bogacki–Shampine
- Cash–Karp
- Dormand–Prince
- Closed Newton-Cotes `o`
- Open Newton-Cotes `o`
- Adams-Bashforth `s`
- Adams-Moulton `s`

Report the name of this algorithm.

ss_AEX_AltName_GEN_0.1

Report the source code where you implement the alternative integrator. Ensure that you include only the code relevant to this task.

Source code filename: ls_AEX_Alt_SRC_0.1

ss_AEX_Alt_CODE_2

### Perform the orbit integration with the alternative integration algorithm

Reproduce the orbit from *[Update your orbit](#update-your-orbit)*, similarly to Task *[Assess the difference between the integrated and SGP4 orbits](#assess-the-difference-between-the-integrated-and-sgp4-orbits)*, in the form of the henceforth called *alternative integrated orbit*:

- for initial state vector, use the first data point of the SGP4 orbit (given in Cartesian coordinates);
- use the same start time as in Task [Update your orbit](#update-your-orbit).

Choose your integration step length and the stop time such that a complete orbit integration does not take longer than 10 seconds.

- Final time in seconds: sf_AEX_AltTimeEnd_NUM_0.1
- The time step in seconds: sf_AEX_AltTimeStep_NUM_0.1

When measuring CPU time, only include the integration process; exclude reading or writing orbital data, as well as any other unrelated operations, such as printing to the screen. Report the total CPU time your integrator takes to produce the orbit, in terms of seconds.

sf_AEX_AtlTimeTotal_NUM_0.5

Report the average computational time per integration step, in terms of seconds.

sf_AEX_AltTimeEff_NUM_0.5

Report the initial and final positions (in meters) and velocities (in meters per second) of the S/C.

- Initial 3D position: lf_AEX_AltPosIni_NUM_0
- Initial 3D velocity: lf_AEX_AltVelIni_NUM_0
- Final 3D position: lf_AEX_AltPosEnd_NUM_2
- Final 3D velocity: lf_AEX_AltVelEnd_NUM_2

### Assess the differences in the orbit from the alternative integrator

Plot the GPD as a function of time between:

- the alternative integrated orbit and the integrated orbit, and
- the alternative integrated orbit and the SGP4 orbit.

Do this for two different step sizes, similarly to Task *[Assess the difference between the integrated and SGP4 orbits](#assess-the-difference-between-the-integrated-and-sgp4-orbits)*, but not necessarily the same values of step size you picked there. As always, all lines must be clearly distinguishable, even if they are overlapping. Ensure the same start/stop/step times are used in all three orbits; this may lead to conflict with the [rules](https://gitlab.tudelft.nl/ae4894-practical-astrodynamics/rules/-/blob/main/README.md#reporting-start-and-stop-times-of-the-sgp4-integration), which is acceptable here. The plot(s) must show a total of 4 lines: 2 time steps for SGP4 and integrated orbit differences, relative to the alternative integrated orbit.

[//]: # (No need to request the plot code here, since it is identical to above)

Report the step sizes you considered above.

lf_AEX_AltGlobErrSteps_NUM_0.1

You are encouraged to represent the (residual) orbit data in **alternative ways** in additional plots to aid in interpretation and conclusion.

Produce 5 additional plots, with the inclination, eccentricity, semi-major axis, true anomaly plus argument of pericenter and the right ascension of the ascending node. In every plot, show three lines referring to:

- the alternative integrated orbit orbit and the integrated orbit in one y-axis, and
- the difference between the alternative integrated orbit and integrated orbit in another y-axis.

Note that the time domain of the integrate orbit must be the same as the SGP4 orbit for the 3rd line.

[//]: # (No need to request the plot code here, since it is identical to above)

Report the filename(s) of your plot(s).

ls_AEX_AltGlobErr_PLOT_2.2

Plot the CGPD as a function of different step sizes used in your alternative integrator. Consider at least 10 different values of the step size, spanning two orders of magnitude. As above, the differences are to be computed relative to both the SGP4 and integrated orbits.

Report all step sizes you considered above.

lf_AEX_AltCumGlobErrSteps_NUM_0.1

[//]: # (No need to request the plot code here, since it is identical to above)

Report the filename(s) of your plot(s).

ls_AEX_AltCumGlobErr_PLOT_2.2

### Analyse the differences in your alternative integrator

Regarding the plots in the task [above](#assess-the-differences-in-the-orbit-from-the-alternative-integrator), or the differences between them and the plots from Task *[Analyse the difference between the integrated and SGP4 orbits](#analyse-the-difference-between-the-integrated-and-sgp4-orbits)*:

- Make three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_AEX_AltObs_OIC_1.5

- Make two interpretations about the observations you reported above.

ss_AEX_AltInt_OIC_2.5

- Make one conclusion based on the observations and interpretations you reported above.

ss_AEX_AltCon_OIC_4

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
