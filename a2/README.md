<script>
  src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
  type="text/javascript">
</script>

# Assignment A2

Please carefully read the [rules](https://gitlab.tudelft.nl/ae4894-practical-astrodynamics/rules/-/blob/main/README.md). Remember that you have to create the `answer-sheet.yaml` file yourself and check that it is formatted correctly with the `answer-sheet-sanity.py` utility. You are also highly encouraged to get feedback with the [Formative Assessment online tool](https://spacegravimetry.tudelft.nl/PA/check.html).

You will find the answer keys in the assignment text below. They are all related uniquely to the task specified directly above the respective answer key. 

Please direct any questions to Brightspace, as it may be of help to your colleagues.

## Contents

[[_TOC_]]

## Objectives

This assignment intends to show you how to represent orbital data under different time and representations, notably orbital elements. For the opportunity for excellence, you are tasked with representing the ground track of your satellite, which is useful for predicting when it will pass overhead.

### Use of libraries

You must not use any library that does time or coordinate transformations (e.g., to convert between time units) or help you represent these quantities in different ways. This includes, but is not limited to `sgp4.api.jday` (you may still use this function to check your results). 

If you use Python, the `datetime` and `time` libraries are allowed as long as they are not in conflict with the first statement. You may use the following (if needed):

```python
import time
GMT_offset=time.localtime().tm_gmtoff
```
Or:
```python
import datetime
datetime.datetime.now(datetime.UTC)
```

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

Report the initial and final times, positions (in meters) and velocities (in meters per second) of the S/C as represented by the SGP4 orbit.

- Initial time in MJD (with fractional part), in days: sf_REG_OrbTimeIniMJD_NUM_0.25
- Initial time in year, month, day, hour, minute, second (all integers, round the seconds if needed): li_REG_OrbTimeIniYMDHMS_NUM_0.25
- Initial 3D position: lf_REG_OrbPosIni_NUM_0
- Initial 3D velocity: lf_REG_OrbVelIni_NUM_0
- Final time in MJD (with fractional part), in days: sf_REG_OrbTimeEndMJD_NUM_0.25
- Final time in year, month, day, hour, minute, second (all integers, round the seconds if needed): li_REG_OrbTimeEndYMDHMS_NUM_0.25
- Final 3D position: lf_REG_OrbPosEnd_NUM_1
- Final 3D velocity: lf_REG_OrbVelEnd_NUM_1

### Implement the conversion to Keplerian elements

Implement a program that converts the orbit data represented in Cartesian coordinates (henceforth *Cartesian orbit*), produced in Task *[Update your orbit](#update-your-orbit)* to a time series of Keplerian elements (henceforth *Keplerian orbit*). 

Report the source code where you implement the conversion to Keplerian elements. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_OrbKep_SRC_0

ss_REG_OrbKep_CODE_1.5

### Compute the Keplerian orbit

Report the Keplerian elements of the initial and final state vector.

- Initial and final semi-major axis in meters: lf_REG_OrbKepSMA_NUM_0.8
- Initial and final eccentricity (dimensionless):lf_REG_OrbKepEcc_NUM_0.8
- Initial and final inclination in degrees: lf_REG_OrbKepInc_NUM_0.8
- Initial and final right ascension of the ascending node in degrees: lf_REG_OrbKepRAAN_NUM_0.8
- Initial and final true anomaly plus argument of pericenter in degrees: lf_REG_OrbKepTApAoP_NUM_1.8

### Plot the Keplerian orbit

Represent the Keplerian orbit you produced in Task *[Compute the Keplerian orbit](#compute-the-keplerian-orbit)* in **two plots**, showing (at least) all 5 quantities mentioned in the previous task as a function of time:

- The first plot with the inclination, eccentricity and semi-major axis, in 3 different y-axes;
- The second plot with the true anomaly plus argument of pericenter and the right ascension of the ascending node, in 2 different y-axes.

There are numerous online tutorials on how to plot with multiple axes with Python, e.g.:

- [matplotlib.axes.Axes.twinx](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.twinx.html)
- [Plots with different scales](https://matplotlib.org/stable/gallery/subplots_axes_and_figures/two_scales.html)

Additionally, you must choose a y-axis scale that allow all lines to be clearly visible in the same plot.

Report the source code where you implement the plots requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_OrbKepPlot_SRC_0

ss_REG_OrbKepPlot_CODE_2.5

Report the filename(s) of your plot(s).

ls_REG_OrbKepPlotFile_PLOT_8

### Analyse the Keplerian orbit

Regarding the plot(s) in the task [above](#plot-the-keplerian-orbit):

- Make three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_REG_OrbKepObs_OIC_5

- Make two interpretations about the observations you reported above.

ss_REG_OrbKepInt_OIC_7.5

- Make one conclusion based on the observations and interpretations you reported above.

ss_REG_OrbKepCon_OIC_11.5

### Implement the conversion from Keplerian elements

Implement a program that converts the Keplerian orbit, produced in Task *[Compute the Keplerian orbit](#compute-the-keplerian-orbit)* to a time series of Cartesian coordinates (henceforth *back-converted Cartesian orbit*). 

Report the source code where you implement the conversion from Keplerian elements. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_OrbKepBack_SRC_0

ss_REG_OrbKepBack_CODE_1.5

### Plot the residual between the original and back-converted Cartesian orbits

Compute the back-converted Cartesian orbit from the Keplerian orbit you produced in Task *[Compute the Keplerian orbit](#compute-the-keplerian-orbit)*. Compute the difference between the Cartesian orbit and back-converted Cartesian (henceforth *residual Cartesian orbit*) for each position and velocity component as a function of time. Represent the 3 position and velocity components of the residual Cartesian orbit in one or more plots as a function of time. If you use the logarithmic scale for the y-axes, don't forget to compute the absolute value of the difference.

You are encouraged to represent the residual orbit data in **alternative ways** in additional plots to aid in interpretation and conclusion.

Report the source code where you implement the plots requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_OrbKepBackPlot_SRC_0

ss_REG_OrbKepBackPlot_CODE_2.5

Report the filename(s) of your plot(s).

ls_REG_OrbKepBack_PLOT_8

### Analyse the back-converted Cartesian orbit

Regarding the plot(s) in the task [above](#plot-the-residual-between-the-original-and-back-converted-cartesian-orbits):

- Make three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_REG_OrbKepBackObs_OIC_5

- Make two interpretations about the observations you reported above.

ss_REG_OrbKepBackInt_OIC_7.5

- Make one conclusion based on the observations and interpretations you reported above.

ss_REG_OrbKepBackCon_OIC_11.5

## Assignment excellence

### Implement the conversion to Co-rotating Spherical Coordinates

Implement a program that converts the Cartesian orbit, produced in Task *[Update your orbit](#update-your-orbit)* to a time series of (geographic) latitude, longitude and radial distance (henceforth *Co-rotating orbit*). 

Report the source code where you implement the conversion to Co-rotating Spherical Coordinates. Ensure that you include only the code relevant to this task.

Source code filename: ls_AEX_OrbECF_SRC_0.1

ss_AEX_OrbECF_CODE_1.9

### Compute the Co-rotating Spherical Coordinates

Report the initial and final states of the Co-rotating orbit.

- Initial and final latitude in degrees: lf_AEX_OrbECFLat_NUM_1
- Initial and final longitude in degrees: lf_AEX_OrbECFLon_NUM_1
- Initial and final radial distance in meters: lf_AEX_OrbECFRad_NUM_1

### Plot the Co-rotating Spherical Coordinates

Represent the latitude, longitude and radial distance you produced in Task *[Compute the Co-rotating Spherical Coordinates](#compute-the-co-rotating-spherical-coordinates)* in one or more plots, showing the [ground tracks](https://en.wikipedia.org/wiki/Ground_track) and the evolution of radial distance with time. 

Report the source code where you implement the plots requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_AEX_OrbECFPlot_SRC_0.1

ss_AEX_OrbECFPlot_CODE_0.9

Report the filename(s) of your plot(s).

ls_AEX_OrbECF_PLOT_3

### Analyse the Co-rotating orbit

Regarding the plot(s) in the task [above](#plot-the-co-rotating-spherical-coordinates):

- Make three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_AEX_OrbECFObs_OIC_2

- Make two interpretations about the observations you reported above.

ss_AEX_OrbECFInt_OIC_4

- Make one conclusion based on the observations and interpretations you reported above.

ss_AEX_OrbECFCon_OIC_5

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
