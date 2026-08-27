#!/usr/bin/env python3

import numpy as np
import urllib.request

############### INPUTS ###############
# The following list of query parameters is by no means exhaustive, but just meant for students to have a minimal
# working example that is representative of what may be required for the assignment.
body_id = '10'  # 10 is the Sun's center. Body IDs for other bodies can be found in the Horizons System web app.
                # More info here: https://ssd.jpl.nasa.gov/horizons/manual.html
                # and here: https://ssd.jpl.nasa.gov/horizons/app.html#/
obj_data = 'YES'  # Specify whether you want to receive summary data of the requested body or not
ephem_type = 'VECTORS'  # Select type of ephemerides. Most handy for general use are VECTORS for Cartesian state and
                        # uncertainties; and ELEMENTS for osculating orbital elements. More info here:
                        # https://ssd-api.jpl.nasa.gov/doc/horizons.html#ephem_type
center = '500@399'  # Coordinate center specified with format [site@body]. Value 500@399 is the geocenter. More info
                    # here: https://ssd.jpl.nasa.gov/horizons/manual.html#center
ref_plane = 'FRAME'  # Plane used as reference for the generation of the ephemerides. Three options:
                     #     1. ECLIPTIC or E (default): ecliptic x-y plane derived from the reference frame
                     #     2. FRAME or F: x-y axes of reference frame
                     #     3. BODYEQUATOR or B: body mean equator and node of date
                     # Note: default reference frame is ICRF; it can be changed to B1950 through the REF_SYSTEM query
                     # parameter (though not recommended unless strictly required)
start_time = '2023-11-25'  # Start epoch for ephemerides retrieval. Accepted formats here:
                           # https://ssd.jpl.nasa.gov/horizons/manual.html#time
                           # Note: when using calendar formats, hours, minutes and seconds can be dropped.
stop_time = '2023-11-29'  # Stop epoch for ephemerides retrieval. Accepted formats here:
                           # https://ssd.jpl.nasa.gov/horizons/manual.html#time
                           # Note: when using calendar formats, hours, minutes and seconds can be dropped.
step_size = '12h'  # Time interval between consecutive epochs of the retrieved ephemerides. Accepted formats here:
                  # https://ssd-api.jpl.nasa.gov/doc/horizons.html#stepping
vec_table = '1x'  # Format of the vector table. Only used when the EPHEM_TYPE is set to VECTORS. Accepted formats here:
                  # https://ssd-api.jpl.nasa.gov/doc/horizons.html#vec_table
vec_labels = 'YES'  # Specify whether labels should be included for the elements of the vector table or not. Only used
                   # when the EPHEM_TYPE is set to VECTORS.
csv_format = 'YES'  # Specify whether to give comma-separated value format to the output or not.
vec_delta_t = 'YES'  # Specify whether the time varying difference TDB-UT must be retrieved or not.

############### BODY ###############
# Note that there are many '%27' along the url. They are used to URL-encode the apostrophe character (as different from
# the regular string delimiter in python).
url = ('https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND=%27' + body_id + '%27&OBJ_DATA=%27' + obj_data
       + '%27&EPHEM_TYPE=%27' + ephem_type + '%27&CENTER=%27' + center + '%27&REF_PLANE=%27' + ref_plane
       + '%27&START_TIME=%27' + start_time + '%27&STOP_TIME=%27' + stop_time + '%27&STEP_SIZE=%27' + step_size
       + '%27&VEC_TABLE=%27' + vec_table + '%27&VEC_LABELS=%27' + vec_labels + '%27&CSV_FORMAT=%27' + csv_format
       + '%27&VEC_DELTA_T=%27' + vec_delta_t + '%27')

# Make a request to the Horizons API through the generated URL, read the retrieved text and decode it from UTF-8 format
response = urllib.request.urlopen(url).read().decode('utf-8')  # This can also be done step-by-step, but this way is
                                                               # more <<pythonic>>

# Split single string into a list of strings, each containing a line
lines = response.splitlines()

c=0
for line in lines:
    c+=1
    print("{:>3} : {:}".format(c,line))

# Splitting each line at the commas into a list, having as a result a list of lists, until reaching end of file
lines_mod = []
start=False
for line in lines:
    if line == '$$SOE':
        start=True
        continue
    if not start:
        continue
    if line == '$$EOE':
        break
    else:
        lines_mod.append(line.split(','))
        print(f"reading line : {line}")

# Transform list of lists into 2-dimensional numpy.array
arr = np.array(lines_mod, dtype=object)

# Delete unnecessary columns (the columns to delete may vary depending on your interests)
arr=np.delete(arr, [1, 6, 7, 8, 9], 1)

############### OUTPUT ###############
# Transform content from string type to float type
arr = arr.astype(float)

# With this we reach an array with each row corresponding to an epoch and each column corresponding to an element of the
# ephemerides. From here, e.g., the ephemerises could be used to create an interpolator, so that they can be evaluated at
# any arbitrary epoch.

print(arr)