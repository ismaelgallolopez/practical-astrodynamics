<script>
  src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
  type="text/javascript">
</script>

# Assignment A5

Please carefully read the [rules](https://gitlab.tudelft.nl/ae4894-practical-astrodynamics/rules/-/blob/main/README.md). Remember that you have to create the `answer-sheet.yaml` file yourself and check that it is formatted correctly with the `answer-sheet-sanity.py` utility. You are also highly encouraged to get feedback with the [Formative Assessment online tool](https://spacegravimetry.tudelft.nl/PA/check.html).

You will find the answer keys in the assignment text below. They are all related uniquely to the task specified directly above the respective answer key. 

Please direct any questions to Brightspace, as it may be of help to your colleagues.

## Contents

[[_TOC_]]

## Objectives

This assignment intends to challenge you to get a better orbit prediction by optimising the initial state vector, using one of the optimisation algorithms discussed in the lecture, so that you get a better orbit fit to the SGP4 orbit. If you wish to use any other optimisation algorithm, please say so in Brightspace and state the reasons for your choice. In any case, the algorithm has to be fully developed by you.

### Use of libraries

You must not use any library that performs any optimisation or estimation. You must use the coordinate transformation routines, the integrator and the disturbance models you implemented in the previous assignments.

### Plotting for this assignment

#### Keplerian elements and their residuals

You are asked to compute the differences between the [SGP4](#update-your-orbit), [integrated](#perform-the-orbit-integration) and [optimised](#optimise-the-initial-state-vector-of-your-orbit) orbits. 

This task means that you need to plot the inclination, eccentricity, semi-major axis, argument of latitude (i.e., true anomaly plus argument of pericenter) and the right ascension of the ascending node in five separate figures, each containing three lines referring to:
  1. SGP4 orbit, 
  1. integrated orbit, 
  1. optimised orbit, 
  1. difference between the SGP4 and integrated orbits (connected to a second y-axis), and
  1. difference between the SGP4 and optimised orbits (connected to the same second y-axis).

Note that all orbits must have the same time domain to calculate their differences correctly.

Implement this plotting capability as a **function** that receives three orbits in Cartesian coordinates, performs their conversion to Keplerian elements, computes their difference and produces the requested 5 plots. We'll refer to these plots as *Keplerian elements and their residuals*.

Report the source code where you implement the plots requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_OrbKepResPlot_SRC_0

ss_REG_OrbKepResPlot_CODE_1

#### Additional plots

Irrespective of the mandatory plots requested in this assignment, you are encouraged to represent the residual orbit data in **alternative ways** in additional plots to aid in interpretation and conclusion.

If you use additional plots, report the source code where you implement them. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_AltPlot_SRC_0

ss_REG_AltPlot_CODE_0

### Special considerations for this assignment

This assignment will require that you perform **numerous orbit integrations**. The speed with which you can do this is crucial. With this in mind, choose the parameters that define the time domain, i.e., start `ti`, step `dt` and stop times `tf`, such that (differences w.r.t. the [rules](https://gitlab.tudelft.nl/ae4894-practical-astrodynamics/rules/-/blob/main/README.md#reporting-start-and-stop-times-of-the-sgp4-integration) are in bold):

- `ti` must be within 24 hours of the TLE epoch;
- `tf` must be between **0.1** to 7 orbital periods from `ti` **(lower values lead to a faster integration time, which is preferable)**;
- `dt` must be such that:
    - the *length of the time domain* (i.e., the number of data points in your list, vector or array that defines the *time domain*) is no more than 1e5 for the Euler integrator and 1e4 for the alternate integrator; for SGP4, it should not be larger than 1e4 unless you need to compare it with the Euler integrator, in which case it can be as large as 1e5;
    - the *length of the time domain* is no less than 1e2 for the Euler integrator and 1e2 for the alternate integrator and SPG4;
    - There are no visible effects of integration errors that make it difficult to interpret the results in the context of the assignment;
- **you can demonstrate the correct dependency of the cumulative global position difference (CGPD) with increasing value of the time step `dt`**;
- **one orbit integration does not take longer than half a second of [wall-clock time](https://pythonspeed.com/articles/blocking-cpu-or-io/), with smaller execution times preferable**; and
- **produces an integrated orbit with a CGPD relative to the SGP4 orbit that is larger than 1 km**.

As suggested in the requirements above, you are free to make the stop time less than one orbital revolution. Even if that's OK, try to complete one orbit revolution. This is necessary to avoid the search space of the optimisation being too flat, i.e., you have something substantial to optimise.

If you are not able to make the 0.5-second benchmark, there may be **unnecessary code in the integration kernel**, i.e., the part of the code that computes $`y_{i+1}`$. Unnecessary code is `if`, `print`, `assert` and other non-mathematical statements. Avoid saving your new states by appending them to a growing matrix (using `np.append` or `np.column_stack`), but find a way to directly assign them to a pre-sized matrix (possibly using other techniques). Also, critically assess which perturbations make sense to include; refer to the last assignment, where you quantified their magnitude and effect on the orbit. There are no bonus points for using all (or most) perturbations, and you are essentially wasting your time. You may address the increased computational effort by reducing the time domain unnecessarily, which overall undermines the objective of this assignment. Please spend some time streamlining your integration function; it will pay back later.

To give you an idea of the number of orbit integrations you will be performing, let's consider the example of a grid search optimisation. With 3 values (which is not a lot) for each one of the 6 unknowns (3 positions and 3 velocities), your search space has a size of $`3^6=729`$ and each optimisation run will take roughly 6 minutes (assuming half a second per orbit integration). If you build your grid with 5 values for each unknown, your optimisation may take over two hours to finish. It is not a bad idea to manually adapt the grid values after each optimisation run, or to implement a more advanced optimisation algorithm.

If you are using the **Euler integrator**, make sure your orbit is not "spiralling outwards". Reduce the step size and end times to avoid this.

You have the option to use **any perturbations** in your orbit integration; even none, if you think this is a good idea (is it?). Any additional  perturbation will slow down your orbit integration. However, the more perturbations you add, the closer your force model is to SGP4's, and you will be able to get a much lower orbit difference. Try experimenting with different perturbations to find the best balance between speed and accuracy.

You will be asked to compute the CGPD. Recall that the global position difference $`\Upsilon_i^{({\rm pos})}`$ is the epoch-wise (subscript "i") magnitude of the position difference vector (superscript "pos"). Please use the RMS over time of these quantities to compute the CGPD $`\Upsilon^{({\rm RMS, pos})}`$, as was done for the previous assignments.

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

### Perform the orbit integration 

Use the Euler or another integrator **you implemented in assignment A3**, to reproduce the orbit from *[Update your orbit](#update-your-orbit)*, with the same start/stop/step times and initial state vector as the SGP4 orbit. We'll refer to this as the *integrated orbit*.

Report the name of the integration algorithm you used, e.g., "Euler" or "RK4" (amongst any other you implemented):

ss_MDT_Integrator_GEN_0

You may include any perturbation you implemented in assignment A4. Please refer to them as follows:

- Earth's oblateness: `J2`
- Atmospheric drag: `Drag`
- Solar Radiation Pressure: `SRP`
- Third-body perturbation from the Sun: `SUN`
- Third-body perturbation from the Moon: `MOON`
- No disturbance: `None`

Report which of the perturbations above you included in the force model used to compute the integrated orbit.

ls_MDT_ForceModelComponents_GEN_0

Please complete the details of your force model:

- If you specified "Drag", consider the same assumptions as in assignment A4, and report:
  
    - Reference height, in meters: sf_REG_RefHeight_GEN_0
    - Scale height, in meters: sf_REG_ScaleHeight_GEN_0
    - Mean density, in $`kg/m^3`$: sf_REG_MeanRho_GEN_0

- If you specified "SRP" or "SUN", consider the same assumptions as in assignment A4, and report the 3D position of the Sun relative to the centre of the Earth, at the start of the calendar day of the TLE epoch, in meters:

lf_REG_SunPos_GEN_0

- If you specified "MOON", consider the same assumptions as in assignment A4, and report the 3D position of the Moon relative to the centre of the Earth, at the start of the calendar day of the TLE epoch, in meters:

lf_REG_MoonPos_GEN_0

Report the total CPU time your integrator takes to produce the orbit, in terms of seconds. 

sf_REG_EulerTimeTotal_NUM_0.5

Report the average computational time per integration step, in terms of seconds.

sf_REG_EulerTimeEff_NUM_0.5

Report the initial and final positions (in meters) and velocities (in meters per second) of the integrated orbit.

- Initial 3D position: lf_REG_IntPosIni_NUM_0
- Initial 3D velocity: lf_REG_IntVelIni_NUM_0
- Final 3D position: lf_REG_IntPosEnd_NUM_1
- Final 3D velocity: lf_REG_IntVelEnd_NUM_1

### Plot the Keplerian elements

Represent the Keplerian elements of the SGP4 orbit in two plots, showing (at least) the following as a function of time:

- The first plot with the inclination, eccentricity and semi-major axis, in 3 different y-axes;
- The second plot with the argument of latitude (i.e., the true anomaly plus argument of pericenter) and the right ascension of the ascending node, on 2 different y-axes.

Report the filename(s) of your plot(s).

ls_REG_OrbKep_PLOT_1

Represent the Keplerian elements of the integrated orbit, showing the same quantities as above. Report the filename(s) of your plot(s).

ls_REG_EulerKep_PLOT_1

### Objective function

Build an objective function $`f(\vec x)`$ that computes the CGPD between:
  
- the **integrated orbit** produced from a set of initial state vector differences $`\vec x = \delta \vec y_0`$ that change the original one $`y_0`$ by the small amount $`\delta \vec y_0`$; we'll call this the *iterated orbit*, and
- the original **SGP4 orbit**, without changing its initial state vector.

In other words, the input for this objective function is $`\delta \vec y_0`$ and the output is the CGPD, represented by $`\Upsilon^{({\rm RMS, pos})}`$ (a scalar value):

$`\Upsilon^{({\rm RMS,pos})}=f(\delta \vec y_0)`$

Recall that $`\Upsilon^{({\rm RMS, pos})}`$ is computed as the RMS of the magnitude of the vector difference between the positions of the iterated and SGP4 orbits.

Report the code that computes the objective function $`f(\vec x)`$, including the routine that computes the CGPD (if implemented separately).

Source code filename: ls_MDT_ObjFun_SRC_0

ss_REG_ObjFun_CODE_1

Report the CGPD that your cost function returns when $`\delta \vec y_0=0`$, in meters.

sf_REG_CGPDInt_NUM_1

### Implement an optimisation algorithm

Implement any of the optimisation algorithms discussed during the lectures, to minimise the objective function $`f`$, which must be the same as that you reported in *[Objective function](#objective-function)*.

From the following list:

- "Grid search"
- "Random sampling"
- "Gradient"
- "Evolutionary"
- "Other"

... report the name of the optimisation algorithm that you used.

ss_MDT_OptName_GEN_0

Report the code that implements the optimisation.

Source code filename: ls_MDT_Opt_SRC_0

ss_REG_Opt_CODE_6

### Optimise the initial state vector of your orbit

Use the optimisation algorithm you implemented in the previous task to minimise the differences with respect to the SGP4 orbit by optimising the initial state vector, thereby producing the *optimised orbit*. 

Report the total CPU time your algorithm takes to optimise the initial state vector orbit, in terms of seconds.

sf_REG_OptTotal_NUM_0.5

Report the average computational time per optimisation iteration or objective function calls, whichever you prefer, in terms of seconds.

sf_REG_OptEff_NUM_0.5

Report the initial and final positions (in meters) and velocities (in meters per second) of the optimised orbit.

- Initial 3D position: lf_REG_OptPosIni_NUM_0
- Initial 3D velocity: lf_REG_OptVelIni_NUM_0
- Final 3D position: lf_REG_OptPosEnd_NUM_0
- Final 3D velocity: lf_REG_OptVelEnd_NUM_0

Report the CGPD of the optimised orbit relative to the SGP4 orbit, in meters.

sf_REG_CGPDOpt_NUM_1

### Convergence plot

Plot the CGPD as a function of the optimisation iteration (or objective function calls). This requires that you store the **lowest** CGPD for every optimisation iteration (or objective function call).

Report the filename(s) of your plot(s).

ls_REG_Conv_PLOT_2

### Keplerian elements plots

Plot the [Keplerian elements and their residuals](#keplerian-elements-and-their-residuals) for the SGP4, integrated and optimised orbits. 

Report the filename(s) of your plot(s).

ls_REG_OrbKepRes_PLOT_7

### Position and velocity magnitude plots

Plot the position and velocity magnitudes of the SGP4, integrated and optimised orbits over time, along with the difference of the latter two relative to the first on a second y-axis. When computing the magnitude difference, first compute the difference vector, then calculate its magnitude. You should have 2 plots, one for position and another for velocity, with the same 5 lines as in the Keplerian elements and their residuals plot.

Report the filename(s) of your plot(s).

ls_REG_MagDiff_PLOT_5


### Analyse the optimisation results

Regarding the plot(s) in the tasks above ([Plot the convergence of the optimisation](#plot-the-convergence-of-the-optimisation) and [Plot the SGP4, integrated and optimised orbits](#plot-the-SGP4-integrated-and-optimised-orbits)):

- Make (at least) three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_REG_OrbObs_OIC_10

- Make (at least) two interpretations about the observations you reported above.

ss_REG_OrbInt_OIC_15

- Make (at least) one conclusion based on the observations and interpretations you reported above.

ss_REG_OrbCon_OIC_23

## Assignment excellence

### Assess the effect of the integration time step

Repeat the optimisation you did above for (at least) 10 different values of the integration time step, while keeping the start and stop times unchanged.

As a function of the different integration time steps, plot:

- the total CPU time your algorithm takes to optimise the initial state vector orbit,
- the total number of optimisation iterations (or objective function) calls, and
- the average computational time per optimisation iteration (or objective function) call.

Do this in the **same plot**, using three y-axes (one plot with three lines).

Report the filename(s) of your plot(s).

ls_AEX_OptTotalStep_PLOT_2

Plot the CGPD of the optimised orbits as a function of the integration time step (one plot with one line).

Report the filename(s) of your plot(s).

ls_AEX_CGPDStep_PLOT_2

Plot the total CPU time your algorithm takes to optimise the initial state vector orbit as a function of the CGPD of the optimised orbits (one plot with one line).

Report the filename(s) of your plot(s).

ls_AEX_OptTotalCGPD_PLOT_2

### Analyse the results

Regarding the plots in the task [above](#assess-the-effect-of-the-integration-time-step):

- Make (at least) three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_AEX_OptStep_OIC_3

- Make (at least) two interpretations about the observations you reported above.

ss_AEX_OptStep_OIC_5

- Make (at least) one conclusion based on the observations and interpretations you reported above.

ss_AEX_OptStep_OIC_6

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
