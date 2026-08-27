<script>
  src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
  type="text/javascript">
</script>

# Assignment A1

Please carefully read the [rules](https://gitlab.tudelft.nl/ae4894-practical-astrodynamics/rules/-/blob/main/README.md). Remember that you have to create the `answer-sheet.yaml` file yourself and check that it is formatted correctly with the `answer-sheet-sanity.py` utility. You are also highly encouraged to get feedback with the [Formative Assessment online tool](https://spacegravimetry.tudelft.nl/PA/check.html).

You will find the answer keys in the assignment text below. They are all related uniquely to the task specified directly above the respective answer key. 

Please direct any questions to Brightspace, as it may be of help to your colleagues.

## Contents

[[_TOC_]]

## Objectives

This assignment aims to help you set up the basic tools that will be needed for later assignments in the course.  It will lay the foundations for you to solve other assignments. It is also the perfect way for you to get acquainted with Git, GitLab, the submission process, and the general idea of solving tasks. You will receive general feedback on the lectures, and you will have the opportunity to ask questions to address any difficulties you encounter.

We will grade this assignment only in terms of pass/fail. It is, therefore, mandatory, like any other assignment, and you must achieve a pass grade. Like all other assignments, you are given two chances to solve the assignment with a pass grade. The difference with other assignments is that it will not influence your final grade.

### Use of libraries

You may use any library for this assignment.

### Programming language

Report the name of the programming language you used to solve this assignment:

ss_REG_Language_GEN_0

## Tasks

### Pick a satellite

Go to [CelesTrak](https://celestrak.org/satcat/search.php) and pick an Earth-orbiting object of your choice under the following conditions:

- The last 3 digits of the NORAD ID must be the same as the **last** 3 digits of your student number
- the satellite must be active (there's a check box with this criterion when you search for satellites on the CelesTrak website)
- must not be part of a *mega constellation*, i.e., those mentioned in [this article](https://spj.science.org/doi/10.34133/2022/9865174):
    - StarLink
    - OneWeb
    - Iridium Next
    - Globalstar
    - PlanetLabs' Flock
    - Samsung
    - Boeing
    - Telesat
    - Kuper

If there are no satellites that meet these criteria, you may pick a satellite with a NORAD ID that **starts** with the last 3 digits of your student number. If that doesn't work either, then select a satellite with a NORAD ID that **contains** the last 3 digits of your student number. If that still doesn't work, please post a request in Brightspace to have a NORAD ID assigned to you. 

NORAD ID:

si_REG_NORADID_GEN_0

In your own words, provide a brief description of this satellite, its purpose and how this is connected to the orbit configuration:

ss_REG_SatDesc_OIC_5

### Retrieve the TLE data 

Retrieve the TLE data, which should look something like this:

```
DELFI-N3XT              
1 39428U 13066N   22278.36746881  .00006067  00000+0  92841-3 0  9991
2 39428  97.8159 208.0372 0114906 286.7293  72.1329 14.69680532474673
```

TLE data:

ls_MDT_TLE_GEN_0

### Implement the SGP4 propagator 

There are several implementations of the SGP4 orbit propagator:

- [Python](https://pypi.org/project/sgp4/)
- [Matlab](https://www.mathworks.com/matlabcentral/fileexchange/62013-sgp4)
- [C, C++, C#, FORTRAN 90, Java, JavaScript, LibreOffice Basic, Matlab/Octave, Python 2/3, R, Ruby, Rust, Swift from GitHub user *aholinch*](https://github.com/aholinch/sgp4)
- [C++, C#, Excel, FORTRAN, Java, MATLAB and Pascal from Vallado et al. (2006)](http://celestrak.org/publications/AIAA/2006-6753/)

Download/clone one SGP4 implementation, not necessarily from the choices above. Generally, the implementations of the SGP4 are in the form of a library, which means you will have to implement a program that:

- reads one file with TLE data
- generate a time domain, from specified start, stop and time step
- integrates the orbit over this time domain (i.e., call the relevant routine in the SGP4 library)
- stored the resulting time series of position and velocity in a suitable data structure, e.g. a NumPy array.

Optionally, write these data to a file.

For this to happen, you need to tell your program 5 parameters:

- input TLE data file
- start time
- time step
- end time

Report the URL or GitHub repository of the SGP4 implementation you have used in your code. 

ss_REG_SGP4IMPL_GEN_0

Report the source code where you call the SGP4 implementation. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_SGP4_SRC_0

ss_REG_SGP4_CODE_4

### Generate an orbit

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

### Plot your orbit 

Represent the orbit data you generated in Task *[Generate an orbit](#generate-an-orbit)* in a plot, showing how each position and velocity coordinate is changing with time. You are encouraged to represent the orbit data in **alternative ways** in additional plots to aid in interpretation and conclusion.

Report the source code where you implement the plots requested above. Ensure that you include only the code relevant to this task.

Source code filename: ls_MDT_OrbPlot_SRC_0

ss_REG_OrbPlot_CODE_7

Report the filename(s) of your plot(s).

ls_REG_Orb_PLOT_22

### Analyse the results

Regarding the plot(s) in the task [above](#plot-your-orbit):

- Make three observations about what the plots show. Don't forget to specify which plot(s) you refer to in each observation.

ss_REG_OrbObs_OIC_14

- Make two interpretations about the observations you reported above.

ss_REG_OrbInt_OIC_19

- Make one conclusion based on the observations and interpretations you reported above.

ss_REG_OrbCon_OIC_27

## Assignment excellence

Since this assignment is only pass/fail, there is no opportunity for excellence.

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
