#Loading routines for Wingpod ASCII data streams and MEVIS csv files with
#   pressure data
#2018/06/13
#Alexander Buetow
#Institute for Space Sciences
#Free University of Berlin

#+++MODULES+++
import numpy as np
import re
import pandas as pd
from datetime import datetime

#+++FUNCTIONS+++
def skiprow_column_finder(file, sep=None):
    """
    Finds an returns unusable rows without a timestamp, erroneous lines and
    status prints which are useless for the postprocessing. Also returns the
    max number of columns of a csv file which is usable for the User
    
    Input:
        file - file string
        sep - seperator(s) of columns in csv file
        
    Output:
        rows - rows to be skipped
        max_n - maximum number of columns
    """       
    f = open(file, "r")
    n = 1
    rows = list()
    max_n=0
    for line in f:
        num = line.rstrip()[0:17]
        try:
            num = float(num) #fine, if first characers is a number -> timestamp
        except:
            rows.append(n) #if not, append the line number
        if not sep == None:
            words = len(re.split(sep, line)) #seperate line to count columns
            if words > max_n:
                max_n = words
        n += 1
        
    if sep == None:
        return(np.array(rows)-1)
    else:
        return(np.array(rows)-1,max_n)
        

def dataframe_to_numeric(df, cols=None):
    """
    Converts pd.DataFrame columns to numeric
    
    Input:
        df - pd.DataFrame
        cols - list of column names to convert
        
    Output:
        df - pd.DataFrame with numeric cols
    """
    if cols == None:
        cols = df.columns
    for i in cols:
        df[i] = pd.to_numeric(df[i], errors='coerce')
    df = df.dropna()
    
    return(df)
    

def load_cpt6100(file, col, delim='\ '):
    """
    reads in pressure data from cpt6100 data files
    
    Input:
        file - str, file string
        col - str, name of pressure value column
        delim - str, regex of delimiter
        
    Output:
        df - plain data from file
    """
    print('Loading CPT6100 data...')
    t = skiprow_column_finder(file)
    df = pd.read_csv(file, skiprows=t, delim_whitespace=True, names=[
            'time', 'x', col])
    df = df.drop(['x'], axis=1) #checksum column not needed
    df = df.dropna()
    df[col] = df[col] * 100 #output in mbar or hPa, calculation into Pa
    
    return(df)

def load_hmt310(file):
    """
    Reads in temperature and humidity data from HMT310 data files.
    
    Input:
        file - file string
        delim - delimiter
        
    Ouput:
        data - plain data from file
    """
    
    print('Loading HMT310 data...')
    t = skiprow_column_finder(file)
    time, rh, t, td, a, x, pw, pws, w = [], [], [], [], [], [], [], [], []
    cols=['time', 'rh', 'T', 'Td', 'a', 'x', 'pw', 'pws', 'h']
    ai = (0, 21, 33, 45, 69, 84, 123, 139, 153)
    ei = (17, 27, 39, 51, 75, 91, 131, 147, 160)
    f = open(file, 'r')
    for line in f:
        n = 0
        for var in (time, rh, t, td, a, x, pw, pws, w):
            var.append(line[ai[n]:ei[n]])
            n += 1
    df = pd.DataFrame({cols[0]: time, cols[1]: rh, cols[2]: t, cols[3]: td,
                       cols[4]: a, cols[5]: x, cols[6]: pw, cols[7]: pws,
                       cols[8]: w},columns=cols)
    df = dataframe_to_numeric(df)
    
    #Conversion into SI units
    df['T'] = df['T'] + 273.15 #temperature  °C -> K
    df['Td'] = df['Td'] + 273.15 #dewpoint  °C -> K
    df['a'] = df['a'] / 1000 #absolute humidity  g/m^3 -> Kg/m^3
    df['x'] = df['x'] / 1000 #mixing ratio  g/Kg -> Kg/Kg
    df['pw'] = df['pw'] * 100 #water vapor pressure  hPa -> Pa
    df['pws'] = df['pws'] * 100 #water vapor pressure  hPa -> Pa
    
    return(df)

def load_novatel(file, delim=';|,|\t|\*', decim='.', leap=37):
    """
    Reads in novatel data logged with 'hgpstools' by Hauke Daempfling
    Input:
        file - input file
        skipr - how many header lines to skip
        delim - delimiter of the logging file
        decim - decimal sign
        leap - leap seconds between UTC and TAI
    Output:
        df - DataFrame with selected columns relevant for wind vector
                calculation
    """
    #+++CONSTANTS+++
    gps_init = 315964800 #begin of GPS time in UNIX Epoch
    week_sec = 604800 #No. of seconds of one week
    smpl_rt = 125 #internal sample rate of the IMU, 1/s
    
    #+++PROGRAMME+++
    print('Loading Novatel data...')
    t = skiprow_column_finder(file, sep=delim)
    df = pd.read_csv(file, skiprows=t[0], sep=delim, header=None,
                     engine='python', names=range(t[1]))
    idx = (df.loc[df.ix[:,1].str.contains('%IMURATECORRIMUSA'),1].index.values,
              df.loc[df.ix[:,1].str.contains('%IMURATEPVASA'),1].index.values)    
    cols0 = ['time', 'gnss_time_1', 'gnss_time_2', 'theta_dot', 'psi_dot',
             'x_ddot', 'y_ddot', 'z_ddot']
    cols1 = ['time', 'gnss_time_1', 'gnss_time_2', 'lat', 'lon', 'height',
             'u_p', 'v_p', 'w_p', 'psi', 'theta', 'phi', 'ins_state']
    #NOTE: to convert 'm/s/sample' into m/s, multiply the value with the 
    #sampling-rate (NOT logging-rate) in Hz of the used IMU. In asynchronous
    #logging modes, the used SPAN-IGM-S1 IMU gets sampled at smpl_rt=125 Hz.
    df0 = pd.DataFrame({
                        cols0[0]: df.ix[idx[0],0].values, #server timestamp
                        cols0[1]: gps_init+ #gnss timestamps
                            pd.to_numeric(df.ix[idx[0],2].values)*week_sec+
                            df.ix[idx[0],3].values-leap+19,
                        cols0[2]: gps_init+df.ix[idx[0],4].values*week_sec+
                            pd.to_numeric(df.ix[idx[0],5].values)-leap+19,
                            #theta_dot, rad/s/sample:
                        cols0[3]: pd.to_numeric(
                                df.ix[idx[0],6].values)*smpl_rt*(-1),
                            #psi_dot, rad/s/sample:
                        cols0[4]: pd.to_numeric(
                                df.ix[idx[0],8].values)*smpl_rt*(-1),
                            #x_ddot, m/s/sample:
                        cols0[5]: pd.to_numeric(
                                df.ix[idx[0],9].values)*smpl_rt,
                            #y_ddot, m/s/sample:
                        cols0[6]: pd.to_numeric(
                                df.ix[idx[0],10].values)*smpl_rt,
                            #z_ddot, m/s/sample:
                        cols0[7]: pd.to_numeric(
                                df.ix[idx[0],11].values)*smpl_rt
                        },
                        columns=cols0
                        )
    df1 = pd.DataFrame({
                        cols1[0]: df.ix[idx[1],0].values, #server timestamp
                        cols1[1]: gps_init+ #gnss timestamps
                            pd.to_numeric(df.ix[idx[1],2].values)*week_sec+
                            df.ix[idx[1],3].values-leap+19,
                        cols1[2]: gps_init+df.ix[idx[1],4].values*week_sec+
                            pd.to_numeric(df.ix[idx[1],5].values)-leap+19,
                        cols1[3]: df.ix[idx[1],6].values, #lat, deg
                        cols1[4]: df.ix[idx[1],7].values, #lon, deg
                        cols1[5]: df.ix[idx[1],8].values, #height, m
                        cols1[6]: df.ix[idx[1],10].values, #u, m/s
                        cols1[7]: df.ix[idx[1],9].values, #v, m/s
                        cols1[8]: df.ix[idx[1],11].values, #w, m/s
                        cols1[9]: df.ix[idx[1],14].values, #psi, deg
                        cols1[10]: df.ix[idx[1],13].values, #theta, deg
                        cols1[11]: df.ix[idx[1],12].values, #phi, deg
                        cols1[12]: df.ix[idx[1],15].values #ins_state
                        },
                       columns=cols1
                       )
    #transfer inertial solution status ('ins_state' column in nova1
    #dataframe) into a numeric value and drop data without complete alignment:
    ins_sol = {'INS_INACTIVE': 0., 'INS_ALIGNING': 1., 'INS_HIGH_VARIANCE': 2.,
               'INS_SOLUTION_GOOD': 3., 'INS_SOLUTION_FREE': 6., 
               'INS_ALIGNMENT_COMPLETE': 7., 'DETERMINING_ORIENTIATION': 8., 
               'WAITING_INITIALPOS': 9.}
    for i in ins_sol:
        df1['ins_state'][df1['ins_state'] == i] = ins_sol[i]
    df1['ins_state'] = pd.to_numeric(df1['ins_state'])
    #convert all columns to float objects:
    for i in [df0, df1]:
        i = dataframe_to_numeric(i)
    #if no position has been found, the IMU's GNSS time is set to the begin of
    #GPS time (06-01-1980, 0000z) --> filter dates with timestamps older than
    #about 2015ish:        
    thrs_time = 1420066800 #Thu 1. Jan 00:00:00 CET 2015
    df1 = df1[(df1['gnss_time_1'] > thrs_time) &
       (df1['ins_state'].isin([2,3,7]))]
    df0 = df0[(df0['gnss_time_1'] > thrs_time) &
               (df0['gnss_time_1'] > float(df1['gnss_time_1'][:1])) &
               (df0['gnss_time_1'] < float(df1['gnss_time_1'][-1:]))]
    
    #convert to SI units (deg -> rad)
    for var in ['psi', 'phi', 'theta']:
        df1[var] = df1[var] * np.pi / 180
    
    return(df0,df1)

def load_usb1608(file):
    """
    reads in raw data from USB1608 stream
    TODO: return multiple channel
    Input:
        file - file string
    Ouput:
        data - data from file
    """
    #Kanäle werden abgescannt, dann Zeitstempel generiert und
    # im Log unterhalb des Zeitstempels geprintet
    
    def make_df(time, vals, smpl):
        """
        Generates pandas DataFrame after scanning of USB1608 Logger is
            completed.
        Input:
            time - timestamps
            vals - values
            smpl - number of samples in one bin
        Output:
            df - pd.DataFrame
        """
        #Create Timestamps between sample packets
        #first: throw away first packet of values, since the time difference
        #between first and last sample in the first packet cannot be known
        vals = vals[smpl[0]:]
        time_new = []
        for i in range(0,len(time)-1):
            time_diff = (time[i+1]-time[i])/smpl[i+1]
            for j in range(0,smpl[0]):
                time_new.append(time[i]+time_diff+j*time_diff)
        cols = ['time', 'V']
        df = pd.DataFrame({cols[0]: time_new, cols[1]: vals},
                           columns=cols)
        f.close()

        return(df)
    
    print('Loading USB1608 data...')
    f = open(file, 'r')
    time, vals, smpl = [], [], []
    while True:
        buffer = f.readline()
        if buffer == '': #EOF reached
            try:
                return(make_df(time, vals, smpl))
            except:
                f.close()
                print('WARNING: File ' + file +
                      ' is empty. Nothing to return.')
                return(None)
        if buffer[0:4] == 'time': #if a timestamp has been found
            try:
                buffer_time = float(buffer[6:23]) #get the timestamp
                buffer_vals = [] #empty values buffer
                buffer = f.readline() #read in next line
                buffer_samples = int(buffer[22:24]) #read number of samples
                n = 0
                while n < buffer_samples:
                    buffer = f.readline()
                    if buffer == '': #EOF reached
                        return(make_df(time, vals, smpl))
                    elif buffer[0:4] == 'Scan':
                        buffer_vals.append(float(buffer[46:54]))
                    else:
                        n = buffer_samples #exit the loop
                    n += 1
                if len(buffer_vals) == buffer_samples:
                    [vals.append(i) for i in buffer_vals]
                    time.append(buffer_time)
                    smpl.append(buffer_samples)
            except:
                pass
    return(None)    
