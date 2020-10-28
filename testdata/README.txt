This directory contains a short (180 s) snippet of test data, sliced from
the second campaign flight at Demmin, which took place on August 15, 2017.

In addition to the raw input files (cpt6100_port{0..3}_data.txt,
hmt310_data.txt, novatel2txt_data.txt, usb1608fsplus_out.txt), this directory
contains the required configuration (conf.py) and constant (const.py) files
in order to reproducibly calculate the output values, which are contained in
the testvar.py file.
Furthermore, there is a wind_reference.kmz and a ins_track_reference.kml file
which visualize the wind barbs and the INS track in Google Earth of the data
snippet. It can be compared to the wind.kmz and ins_track.kml which will be
created during the test in the same directory.

In order to run the test, the user simply has to run test.py, after he has 
modified the 'data_dir' variable in the testdata/conf.py file according to his
setup.

The test will be passed, if the differencies between the calculated mean and
standard RMSE of the three wind components u, v and w do not differ more
than 0.001 m/s^2. This values can be modified in the test.py.
