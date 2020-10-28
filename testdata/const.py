#Constants file for routine_wind.py
#2018/08/26
#Alexander Buetow
#Institute for Space Sciences
#Free University of Berlin

#+++DESCRIPTION+++
#
#This file containts constants that are CRUCIAL for any ACCURATE wind vector
#calculation and have to be determined on the aircraft utilizing special
#calibration maneuvers and analyzing methods.
#It also contains fix constants to eleminate outliers in raw data files.

#+++CONSTANTS+++
#
#LEAP SECONDS BETWEEN TAI AND UTC
#
#The number of UTC leap seconds since begin of TAI has to be known to
#accuratly calculate Unix time from GNSS week timestamps of the IMU logs. This
#is necessary because leap seconds are deduced from Unix time. Unix time does
#NOT represent precisely the elapsed seconds since Epoch!
#Last introduced leap second: 31st December 2016
#Last checked: 13th March 2018
#unit in s
utc_leap = 37

#PRESSURE OFFSET VALUE
#
#Fix pressure offset values for pressure sensors p_alp, p_bet and p_spd.
#As the sensors are prone for drifting over time, sensor values need frequently
#re-zeroing.
#
#unit in mbar
p_offset = {
        'p_alp': -0.0342, #obtained bef. testflight conducted on 17th Aug 2017
        'p_bet': -0.0159, #obtained bef. testflight conducted on 17th Aug 2017
        'p_spd': -0.0523, #obtained bef. testflight conducted on 17th Aug 2017
        'p_alt': 0 #unknown
        }


#SPEED DEPENDEND CORRECTION TERMS FOR STATIC PRESSURE
#
#pressure measurement correction terms for the static port, which affects p_spd
#and p_alt measurements
#
#dimless fractions
ps_q_corr = {
        'C2': -4.14E-5,
        'C1': 0.127
        }

#SPEED DEPENDEND LINEAR CORRECTION TERM FOR DYNAMIC PRESSURE
#
#pressure measurement correction term for the dynamic pressure port, which
#affects p_spd measurements only
#
#dimless fractions
q_q_corr = -0.0273

#PROBE DIFFERENTIAL PRESSURE SENSITIVITY CONSTANT - ANGLE OF ATTACK
#
#The C-value determines the sensitivity of the pressure readings to flow
#angles. In best case, its a constant, so flow angle and measured differential
#pressure - normalized by dynamic pressure - are linked linear.
#C = 0.078 is the theoretical value according to potential flow theory. The
#real value is likely to be greater than value offered by theory.
#
#unit is in 1/deg
C_alp = 0.0905

#ALPHA OFFSET-ANGLE
#
#The alpha offset-angle is the angle between the probe and INS platform.
#An inaccurate value leads to erratic vertical wind component values.
#[insert example, offset-Winkel durch Umströmung nennen/erklären]
#
#unit in deg
alp0 = 5.531

#PROBE DIFFERENTIAL PRESSURE SENSITIVITY CONSTANT - YAW ANGLE
#
#Refer to explaination of C_alp.
#
#unit is in 1/deg
C_bet = 0.0725

#BETA OFFSET-ANGLE
#
#The beta offset-angle is the azimut angle between the probe and INS platform.
#An inaccurate value leads to erratic horizontal wind component values.
#
#unit in deg
bet0 = -0.601

#THEORETICAL DIFFERENTIAL PRESSURE SENSITIVITY CONSTANT
#
#Refer to explaination of C_alp. Practically never changes.
#
#unit in 1/deg
C_k = 0.079

#PRESSUE RESPONSE TIME OFFSET
#
#pressure measurements tend to lag behind IMU measurements, as they have a
#physical response time. While the response time of the IMU is assumed to be 0,
#the following values represent the relative lag of the pressure in respect to
#IMU measurements. Therefore, the values specified here are SUBTRACTED from
#the respective pressure sensor time stamps in order to compensate the response
#time lag.
#
#unit in s
p_time_offset = {
        'p_alp': 0.011, #determined in the master thesis
        'p_bet': 0.011, #assumed to be equal to p_alp sensor
        'p_spd': 0.011, #assumed to be equal to p_alp sensor
        'p_alt': 0.011 #assumed to be equal to p_alp sensor
        }

#DISTANCE BETWEEN IMU COORDINATION SYSTEM ORIGIN ANDPROBE TIP
#
#the Lengh L has to be measured in order to correct wind calculation for
#differential pressure due to angular velocities of the airplaine.
#
#unit in m
L = 0.85

#TAT PROBE RECOVERY FACTOR
#
#The recovery factor r determines how 'good' the TAT housing works. Value is 1
#for an ideal TAT probe. 'Flush bulb' type probes have recovery factors
#of ~0.6-0.8.
r = 1

#OUTLIER LIMITS
#
#You can define fixed outliers for the logger data streams as lists here.
p_lim_spd = [-1,19] #19 hPa is equivalent to ~200 kph in ISA conditions.
p_lim_alt = [500,1040] #CPT6100 absolute pressure sensors
p_lim_diff = [-10,10] #CPT6100 bidirectional sensors (alpha and beta measurements)

T_lim_hmt = [-40,40] #Temperature limit for HMT310 sensor
Td_lim_hmt = [-80,35] #Dewpoint limit for HMT310 sensor

V_lim_usb = [2,5.5] #Voltage limit for USB1608 logger on a PT100


