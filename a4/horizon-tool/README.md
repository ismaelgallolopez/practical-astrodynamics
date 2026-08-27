# horizon-tool

## Scope
The objective of this script is to provide a minimal working example of how to retrieve ephemerides data from the Horizons System of NASA.

## Inputs
The input variables whose values need to be modified to alter the retrieved ephemerides can be found in the INPUTS block. A brief description of the meaning of each variable, together with their possible and recommended values (where applicable), can be found in the in-line comments to the right of the variable declaration. Useful links to explore the complete range of options available are also provided in said comments. Feel free to play with these values until you understand how they affect the retrieved output. Beware that, for the script to work as it is now, even numeric values given to these input variables need to be of type string!!!

## Body
As you can see, the body of the script is short. The objective of each performed operation is explained in a comment above its corresponding block of code. The intention is that you need to make little to no modification to this section of the code. Beware of the hard-coded delimiter in the `else` block:

```Python
    else:
        lines_mod.append(line.split(','))
```
and the hard-coded column indexes for deletion:

```Python
arr=np.delete(arr, [1, 6, 7, 8, 9], 1)
```

Their presence is not a matter of lazyness (at least not solely), but of making you interact to some extent with the output of the URL request so that you get to undestand what each thing does.

## Outputs
The intended output of the script is an array holding the retrieved ephemerides. The explanation on how they are stored can be found in a comment at the end of this section of the code. Remember that this may not be exactly what you need and that you may require to perform further modifications for the usage of the ephemerides.

## Example
The following should be the output you see when running this script as it is:

```
$ python3 horizons_script.py
  1 : API VERSION: 1.2
  2 : API SOURCE: NASA/JPL Horizons API
  3 :
  4 :
  5 :
  6 : *******************************************************************************
  7 : Ephemeris / API_USER Thu Oct 12 02:29:34 2023 Pasadena, USA      / Horizons
  8 : *******************************************************************************
  9 : Target body name: Sun (10)                        {source: DE441}
 10 : Center body name: Earth (399)                     {source: DE441}
 11 : Center-site name: BODY CENTER
 12 : *******************************************************************************
 13 : Start time      : A.D. 2023-Nov-25 00:00:00.0000 TDB
 14 : Stop  time      : A.D. 2023-Nov-29 00:00:00.0000 TDB
 15 : Step-size       : 720 minutes
 16 : *******************************************************************************
 17 : Center geodetic : 0.0, 0.0, 0.0                   {E-lon(deg),Lat(deg),Alt(km)}
 18 : Center cylindric: 0.0, 0.0, 0.0                   {E-lon(deg),Dxy(km),Dz(km)}
 19 : Center radii    : 6378.137, 6378.137, 6356.752 km {Equator_a, b, pole_c}
 20 : Output units    : KM-S
 21 : Calendar mode   : Mixed Julian/Gregorian
 22 : Output type     : GEOMETRIC cartesian states
 23 : Output format   : 1x (position w/uncertainties: XYZ)
 24 : EOP file        : eop.231010.p240103
 25 : EOP coverage    : DATA-BASED 1962-JAN-20 TO 2023-OCT-10. PREDICTS-> 2024-JAN-02
 26 : Reference frame : ICRF
 27 : *******************************************************************************
 28 :             JDTDB             Calendar Date (TDB),        delta-T,                      X,                      Y,                      Z,             X_s,             Y_s,             Z_s,
 29 : *********************************************************************************************************************************************************************************************
 30 : $$SOE
 31 : 2460273.500000000, A.D. 2023-Nov-25 00:00:00.0000,      69.182918, -6.907813730189458E+07, -1.197693917281251E+08, -5.191795012180165E+07,            n.a.,            n.a.,            n.a.,
 32 : 2460274.000000000, A.D. 2023-Nov-25 12:00:00.0000,      69.182929, -6.791743048766552E+07, -1.203122132748499E+08, -5.215321060669691E+07,            n.a.,            n.a.,            n.a.,
 33 : 2460274.500000000, A.D. 2023-Nov-26 00:00:00.0000,      69.182940, -6.675155153177705E+07, -1.208458189183307E+08, -5.238447776709128E+07,            n.a.,            n.a.,            n.a.,
 34 : 2460275.000000000, A.D. 2023-Nov-26 12:00:00.0000,      69.182951, -6.558058300242192E+07, -1.213701697315464E+08, -5.261173545278894E+07,            n.a.,            n.a.,            n.a.,
 35 : 2460275.500000000, A.D. 2023-Nov-27 00:00:00.0000,      69.182962, -6.440460735955125E+07, -1.218852267613939E+08, -5.283496744860365E+07,            n.a.,            n.a.,            n.a.,
 36 : 2460276.000000000, A.D. 2023-Nov-27 12:00:00.0000,      69.182973, -6.322370708678949E+07, -1.223909509907225E+08, -5.305415744772734E+07,            n.a.,            n.a.,            n.a.,
 37 : 2460276.500000000, A.D. 2023-Nov-28 00:00:00.0000,      69.182984, -6.203796482499160E+07, -1.228873033235693E+08, -5.326928903749281E+07,            n.a.,            n.a.,            n.a.,
 38 : 2460277.000000000, A.D. 2023-Nov-28 12:00:00.0000,      69.182995, -6.084746350158770E+07, -1.233742445923978E+08, -5.348034569713160E+07,            n.a.,            n.a.,            n.a.,
 39 : 2460277.500000000, A.D. 2023-Nov-29 00:00:00.0000,      69.183006, -5.965228645059840E+07, -1.238517355848631E+08, -5.368731080640987E+07,            n.a.,            n.a.,            n.a.,
 40 : $$EOE
 41 : *********************************************************************************************************************************************************************************************
 42 :
 43 : TIME
 44 :
 45 :   Barycentric Dynamical Time ("TDB" or T_eph) output was requested. This
 46 : continuous coordinate time is equivalent to the relativistic proper time
 47 : of a clock at rest in a reference frame co-moving with the solar system
 48 : barycenter but outside the system's gravity well. It is the independent
 49 : variable in the solar system relativistic equations of motion.
 50 :
 51 :   TDB runs at a uniform rate of one SI second per second and is independent
 52 : of irregularities in Earth's rotation.
 53 :
 54 : CALENDAR SYSTEM
 55 :
 56 :   Mixed calendar mode was active such that calendar dates after AD 1582-Oct-15
 57 : (if any) are in the modern Gregorian system. Dates prior to 1582-Oct-5 (if any)
 58 : are in the Julian calendar system, which is automatically extended for dates
 59 : prior to its adoption on 45-Jan-1 BC.  The Julian calendar is useful for
 60 : matching historical dates. The Gregorian calendar more accurately corresponds
 61 : to the Earth's orbital motion and seasons. A "Gregorian-only" calendar mode is
 62 : available if such physical events are the primary interest.
 63 :
 64 : REFERENCE FRAME AND COORDINATES
 65 :
 66 :   International Celestial Reference Frame (ICRF)
 67 :
 68 :     The ICRF is an adopted reference frame whose axes are defined relative to
 69 :     fixed extragalactic radio sources distributed across the sky.
 70 :
 71 :     The ICRF was aligned with the prior FK5/J2000 dynamical system at the ~0.02
 72 :     arcsecond level but is not identical and has no associated standard epoch.
 73 :
 74 :   Symbol meaning:
 75 :
 76 :     JDTDB    Julian Day Number, Barycentric Dynamical Time
 77 :     del_T    Time-scale conversion difference TDB - UT (s)
 78 :       X      X-component of position vector (km)
 79 :       Y      Y-component of position vector (km)
 80 :       Z      Z-component of position vector (km)
 81 :       X_s    X-direction 1-sigma position uncertainty (km)
 82 :       Y_s    Y-direction 1-sigma position uncertainty (km)
 83 :       Z_s    Z-direction 1-sigma position uncertainty (km)
 84 :
 85 :    "n.a." indicates the value for that field is not currently available.
 86 :
 87 : ABERRATIONS AND CORRECTIONS
 88 :
 89 :  Geometric state vectors have NO corrections or aberrations applied.
 90 :
 91 : Computations by ...
 92 :
 93 :     Solar System Dynamics Group, Horizons On-Line Ephemeris System
 94 :     4800 Oak Grove Drive, Jet Propulsion Laboratory
 95 :     Pasadena, CA  91109   USA
 96 :
 97 :     General site: https://ssd.jpl.nasa.gov/
 98 :     Mailing list: https://ssd.jpl.nasa.gov/email_list.html
 99 :     System news : https://ssd.jpl.nasa.gov/horizons/news.html
100 :     User Guide  : https://ssd.jpl.nasa.gov/horizons/manual.html
101 :     Connect     : browser        https://ssd.jpl.nasa.gov/horizons/app.html#/x
102 :                   API            https://ssd-api.jpl.nasa.gov/doc/horizons.html
103 :                   command-line   telnet ssd.jpl.nasa.gov 6775
104 :                   e-mail/batch   https://ssd.jpl.nasa.gov/ftp/ssd/hrzn_batch.txt
105 :                   scripts        https://ssd.jpl.nasa.gov/ftp/ssd/SCRIPTS
106 :     Author      : Jon.D.Giorgini@jpl.nasa.gov
107 : *******************************************************************************
reading line : 2460273.500000000, A.D. 2023-Nov-25 00:00:00.0000,      69.182918, -6.907813730189458E+07, -1.197693917281251E+08, -5.191795012180165E+07,            n.a.,            n.a.,            n.a.,
reading line : 2460274.000000000, A.D. 2023-Nov-25 12:00:00.0000,      69.182929, -6.791743048766552E+07, -1.203122132748499E+08, -5.215321060669691E+07,            n.a.,            n.a.,            n.a.,
reading line : 2460274.500000000, A.D. 2023-Nov-26 00:00:00.0000,      69.182940, -6.675155153177705E+07, -1.208458189183307E+08, -5.238447776709128E+07,            n.a.,            n.a.,            n.a.,
reading line : 2460275.000000000, A.D. 2023-Nov-26 12:00:00.0000,      69.182951, -6.558058300242192E+07, -1.213701697315464E+08, -5.261173545278894E+07,            n.a.,            n.a.,            n.a.,
reading line : 2460275.500000000, A.D. 2023-Nov-27 00:00:00.0000,      69.182962, -6.440460735955125E+07, -1.218852267613939E+08, -5.283496744860365E+07,            n.a.,            n.a.,            n.a.,
reading line : 2460276.000000000, A.D. 2023-Nov-27 12:00:00.0000,      69.182973, -6.322370708678949E+07, -1.223909509907225E+08, -5.305415744772734E+07,            n.a.,            n.a.,            n.a.,
reading line : 2460276.500000000, A.D. 2023-Nov-28 00:00:00.0000,      69.182984, -6.203796482499160E+07, -1.228873033235693E+08, -5.326928903749281E+07,            n.a.,            n.a.,            n.a.,
reading line : 2460277.000000000, A.D. 2023-Nov-28 12:00:00.0000,      69.182995, -6.084746350158770E+07, -1.233742445923978E+08, -5.348034569713160E+07,            n.a.,            n.a.,            n.a.,
reading line : 2460277.500000000, A.D. 2023-Nov-29 00:00:00.0000,      69.183006, -5.965228645059840E+07, -1.238517355848631E+08, -5.368731080640987E+07,            n.a.,            n.a.,            n.a.,
[[ 2.46027350e+06  6.91829180e+01 -6.90781373e+07 -1.19769392e+08
  -5.19179501e+07]
 [ 2.46027400e+06  6.91829290e+01 -6.79174305e+07 -1.20312213e+08
  -5.21532106e+07]
 [ 2.46027450e+06  6.91829400e+01 -6.67515515e+07 -1.20845819e+08
  -5.23844778e+07]
 [ 2.46027500e+06  6.91829510e+01 -6.55805830e+07 -1.21370170e+08
  -5.26117355e+07]
 [ 2.46027550e+06  6.91829620e+01 -6.44046074e+07 -1.21885227e+08
  -5.28349674e+07]
 [ 2.46027600e+06  6.91829730e+01 -6.32237071e+07 -1.22390951e+08
  -5.30541574e+07]
 [ 2.46027650e+06  6.91829840e+01 -6.20379648e+07 -1.22887303e+08
  -5.32692890e+07]
 [ 2.46027700e+06  6.91829950e+01 -6.08474635e+07 -1.23374245e+08
  -5.34803457e+07]
 [ 2.46027750e+06  6.91830060e+01 -5.96522865e+07 -1.23851736e+08
  -5.36873108e+07]]
```