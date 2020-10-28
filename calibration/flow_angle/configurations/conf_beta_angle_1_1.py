#Configuration file for wind calculation
#2019/02/10
#Alexander Buetow
#Institute for Space Sciences
#Free University of Berlin

#+++DESCRIPTION+++
#
#This file containts configuration statements (data input directory etc.)

#+++CONFIGURATION+++

#SELECT TIME
#
#Select a timestamp in format "['YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM:SS']" in
#UTC, if only a specific time range is desired. Select "[]" to
#disable this option. The selected time refers to the 'true' time derived from
#GPS-time in UTC.
time_sel = ['2017-08-14 16:06:40','2017-08-14 16:07:40'] #default: []

#KML EXPORT
#
#exports TWO files: a kml file containing 'IMURATEPVASA' log of the SPAN IGM
#and a second kmz file showing processed wind data and barbs.
kml_export = False

#ASCII EXPORT
#
#exports an csv file of processed data and compress it if desired
#ATTENTION: export is VERY slow with compression enabled. Expect large file
#size, especially using a high upsampling rate!
csv_export = False
csv_compress = True

#FILE NAMES
#
#Input file names.
cpt_spd = 'cpt6100_port0_data.txt' #sensor data for airspeed
cpt_alt = 'cpt6100_port1_data.txt' #sensor data for barometric pressure
cpt_bet = 'cpt6100_port2_data.txt' #sensor data for beta angle
cpt_alp = 'cpt6100_port3_data.txt' #sensor data for alpha angle

imu_data = 'novatel2txt_data.txt' #IMU data

vais = 'hmt310_data.txt' #Vaisala measurements

pt100 = 'usb1608fsplus_out.txt' #sensor data logged with USB1608 AD-converter

#SMOOTH WIDTH
#
#Sets the width of the running mean window for smoothing the time stamps of the
#logs in seconds. If you select e.g. a value of 10, the width of the
#CENTRALIZED running mean window is 10 seconds. Since all measurements within
#this timeframe are weighted equally, all data 5 seconds after beginning and
#5 seconds before the end of a data set will be clipped in this case.
#Value in seconds.
smooth = 60

#UPSAMPLING RATE
#
#Determines the upsampled time resolution of output data in 1/s.
#REMEMBER: All logger data streams have to be synchronized using linear
#   interpolation. A low value in order of magnitude of the sensor sampling
#   rate might smooth peaks out. Choose the value as high as possible to
#   prevent interpolation artifacts, however, keep in mind that very high
#   upsampling rate bloats up the processing time, memory usage and output file
#   size, which might lead to system freezing.
#Value in 1/s.
upsmpl_rate = 100
