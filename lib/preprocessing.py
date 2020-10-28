
#finds spikes and removes distortion due to harmonic vibration
#2018/10/08
#Alexander Buetow
#alexander.buetow@freenet.de
#Institute for Space Sciences
#Free University of Berlin

#+++MODULES+++
import pandas as pd
import numpy as np
from math import floor,ceil
from datetime import datetime

pd.options.mode.chained_assignment = None

#+++FUNCTIONS+++
def jitter_corr(df, name, smooth=9, time_col='time'):
    """
    Interpolates timestamps within a selected, centralized moving average
        window. This is necessary to remove artificial time jitter of
        timestamps, which got generated due to inconsistant communication
        buffering between the RPi and sensors and run time delays within the
        logging processes.
        
    Input:
        df - pd.DataFrame with 'time' column containing timestamps
        name - str, name of dataframe
        smooth - int, smoothness of running mean function in seconds
        time_col - str, column name where the timestamps are stored in df
        
    Output:
        t_int - np.array, interpolated (smoothed) timestamps
    """
    
    def run_mean(x, n):
        """
        Running mean function using simple cumsum method
        IMPORTANT: Ouput values between :(floor(n/2)) and -(ceil(n/2)): will be
            dismissed. Choose an odd number to get centralized running
            mean.
            
        Input:
            x - 1D np.array
            n - bin size of interpolation
            
        Output:
            out - 1D np.array
        """
        out = np.cumsum(np.insert(x, 0, 0))
        out = (out[n:] - out[:-n]) / n
        
        return(out)
    
    #find discontinuities/jumps in timestamp array
    tmstmp = df[time_col].values
    tmstmp_diff = abs(tmstmp[1:] - tmstmp[:-1]) #timestamp differences
    tmstmp_diff_med = np.median(tmstmp_diff) #median of timestamp differences
    tmstmp_diff_mean = np.mean(tmstmp_diff) #mean of time differences
    #calculate number of samples containing smoothing time frame:
    smooth = int(round(smooth / tmstmp_diff_mean))
    smooth = smooth - 1 + smooth % 2 #subtract one, if smoothing value is even
    #select rows where the timestamp differences are much larger than the
    #median plus the last line:
    sel_rows = np.append(np.where(tmstmp_diff > tmstmp_diff_med * 5)[0] + 1,
                         len(tmstmp))
        
    new = pd.DataFrame(columns=df.columns)
    for i,r in enumerate(sel_rows):
        if i == 0: #set a: start index
            a = 0
        else:
            a = sel_rows[i-1]
        new_tmp = df[(a + floor(smooth / 2)):(r - floor(smooth / 2))]
        new = new.append(new_tmp)
        new[time_col][(len(new) - len(new_tmp)):] = run_mean(
                                            df[time_col].values[a:r], n=smooth)
        
    return(new)

def hard_limit(df, cols, lims):
    """
    Substitutes invalid data rows with NaN's but keeps the timestamps.
    
    Input:
        df - DataFrame
        cols - list, columns to check
        lims - list, containing limits:
                                    [[lower_1,upper_2],[lower_2,upper_2],..]
        
    Output:
        df - DataFrame with removed rows
    """    
    for i,c in enumerate(cols):
        df = df[(df[c] < lims[i][1]) & (df[c] > lims[i][0])]
        
    return(df)

def p_offset_corr(p, offset):
    '''
    p_alp/p_bet/p_spd offset correction function for pressure sensor values.

    Input:
        p - array, pressure values
        offset - float, single offset value
        
    Output:
        array, corrected pressure values
    '''
    
    return(p - offset)
    
def p_dyn_corr(p, q, slope):
    '''
    Dynamic (linear) correction of pressure sensor data accouning for dynamic
        pressure effects.
        
    Input:
        p - array, pressure values
        q - array, indicated dynamic pressure values, only corrected for offset
        slope - float, correction values
    '''
    
    return(p - (q * slope))
    
def time_offset_corr(time, time_offset):
    '''
    Response time offset correction for a timestamp.
    
    Input:
        time - array, timestamps
        time_offset - float, time offset
        
    Output:
        array, corrected timestamps
    '''
    
    return(time - time_offset)


def sync(dfs, dfm, dfm_gnss_col, intp_wdth, skip_cols, periodic,
         periodic_rad=True, time_col='time'):
    """
    Synchronizes all DataFrames and interpolates them on a common time stamp.
    
    Input:
        dfs - dict, containing pd.DataFrames to be synchronized
        dfm - str, name of DataFrame with GNSS-timestamp
        dfm_gnss_col - str, name of GNSS-time column on which the IMU data will
                        be interpolated (reference time)
        intp_wdth - int, frequency of interpolation in 1/s
        skip_cols - str or list, containing column name(s) which will not be
                    interpolated
        periodic - list, names of columns which contain periodic values
        periodic_rad - bool, periodic unit. rad if 'True', deg otherwise
        time_col - str, name of common time column in each DataFrame
        
    Output:
        out - pd.DataFrame, synchronized and interpolated data
    """
    
    def cut_neg_jumps(df, time_col='time', maj=-5):
        """
        Cuts away dataframe piece after a huge negative jump in time stamp
            occured.
            
        Input:
            df - pd.DataFrame
            time_col - str, name of column containing the time stamp
            maj - numeric, threshold value after which 
            
        Output:
            df - pd.DataFrame
        """
        
        diff = df[time_col].values[1:] - df[time_col].values[:-1]
        row = np.where(diff <= maj)
        try:
            idx = row[0][-1]
            df = df[:idx]
            return(df)
        except:
            return(df)
    
    def periodic_adder(ser, periodic_rad=True):
        """
        Adds periods to a cyclic series (for example azimuth angles). Needed
            before interpolation processes to prevent interpolation artifacts.
            
        Input:
            ser - pd.Series, input array or series on which the cyclic/periodic
                    accumulation should be applied
            periodic_rad - bool, periodic unit. rad if 'True', deg otherwise
            
        Output:
            ser - pd.Series, output array or series
        """
        
        if periodic_rad:
            peri_val = 2*np.pi
        else:
            peri_val = 360
        serneg = ser.loc[ser.values[1:]-ser.values[:-1] >
                         (peri_val-peri_val*0.2)] #positive periods
        serpos = ser.loc[ser.values[1:]-ser.values[:-1] <
                         -(peri_val-peri_val*0.2)] #negative periods
        for i in serpos.index:
            ser.loc[i+1:] = ser.loc[i+1:]+peri_val
        for i in serneg.index:
            ser.loc[:i] = ser.loc[:i]+peri_val
            
        return(ser)
        
    def periodic_remover(ser, periodic_rad):
        """
        Removes periods from cylic series.
        
        Input:
            ser - pd.Series, input array or series on which the cyclic/periodic
                    accumulation should be applied
            periodic - list, names of columns which contain periodic values
            periodic_rad - bool, periodic unit. rad if 'True', deg otherwise
            
        Output:
            ser - pd.Series, output array or series
        """
        
        if periodic_rad:
            peri_val = 2*np.pi
        else:
            peri_val = 360
        ser = ser % peri_val
        
        return(ser)
    
    #calculate time diff between smoothed rpi time stamp and gnss time
    df_td = pd.DataFrame({'time': dfs[dfm][time_col].values,
                                't_diff': dfs[dfm][time_col].values- \
                                dfs[dfm][dfm_gnss_col].values},
                                columns=['time', 't_diff'])
    #allocating lists to find latest start and earliest stopping time stamps:
    start,stop = [],[]
    #apply time correction via interpolation of the time difference column:
    for i in dfs:
        dfs[i] = cut_neg_jumps(dfs[i])
        inter = np.interp(dfs[i][time_col].values,
                          df_td['time'].values, df_td['t_diff'].values)
        dfs[i][time_col] = dfs[i][time_col] - inter
        start.append(dfs[i][time_col].values[0])
        stop.append(dfs[i][time_col].values[-1])
    start = ceil(np.max(start))
    stop = floor(np.min(stop))
    #create output dataframe with unified time stamp and append columns with
    #interpolated data afterwards:
    master_time = np.linspace(start, stop, (stop - start) * intp_wdth)
        #int((dfs[dfm][dfm_gnss_col].values[-1]- \
        #                           dfs[dfm][dfm_gnss_col].values[0])* \
        #                            intp_wdth)+1)
    out = pd.DataFrame(master_time, columns=['time'])
    #interpolate and append INS dataframes first
    if type(skip_cols) != list: #make a list if only a string is given
        skip_cols = list(skip_cols)
    #list of ALL column names to be skipped for interpolation:
    skip_cols.append(time_col)
    #starting actual interpolation...interate over all dataframes
    for i in dfs:
        #columns to be skipped
        col = [col for col in dfs[i].columns if col not in skip_cols]
        #add periods before interpolation
        for j in periodic: #apply on all periodic columns
            if j in dfs[i].columns: #if columns contain periodic column
                dfs[i][j] = periodic_adder(dfs[i][j], periodic_rad)
        if i in ['nova0', 'nova1']: #exclusively for novatel log w/ gnss time
            for j in col:
                out[j] = np.interp(master_time, dfs[i][dfm_gnss_col],
                                   dfs[i][j])
        else: #all other time columns
            for j in col:
                out[j] = np.interp(master_time, dfs[i][time_col], dfs[i][j])
    for j in periodic: #last step: remove periods per modulo
        if j in out.columns:
            out[j] = periodic_remover(out[j], periodic_rad)
            
    return(out)

def time_selection(df, sel, time_col='time'):
    '''
    Applies the time selection defined in the configuration file.
    
    Input:
        df - pd.DataFrame, containing data to be sliced
        sel - list, contains time stamp of desired host time
        time_col - str, name of common time column in each DataFrame
        
    Output:
        out - pd.DataFrame, synchronized and interpolated data
    '''
    
    #slice time ranges, if specified in conf.py:
    if not sel == []:
        try:
            print("Time selected between: '" + sel[0] + "' and '" + sel[1] + 
                      "' UTC")
            myfmt = '%Y-%m-%d %H:%M:%S'
            epoch = datetime(1970, 1, 1)
            beg = (datetime.strptime(sel[0],myfmt)-epoch).total_seconds()
            end = (datetime.strptime(sel[1],myfmt)-epoch).total_seconds()
            if len(df[(df[time_col] >= beg) & (df[time_col] <= end)]) == 0:
                print('\033[1;30;43m' + 'WARNING:' + '\33[0m' +
                       ' Option "time_sel" seems to be specified ' + 
                       'incorrectly. Time selection skipped..')
            else:
                df = df[(df[time_col] >= beg) & (df[time_col] <= end)]
        except:
            print('\033[1;30;43m' + 'WARNING:' + '\33[0m' +
                  ' time selection option not specified ' + 
                  'correctly or something other went wrong. Please check ' +
                  'time format in configuration ' + 
                  'option "time_sel". Time selection skipped...')
    
    return(df)

def flow_angle_ps_error(angl, qi, const):
    '''
    Calculates the flow angle dependend static defect by using a simple 
        quadratic correction function. The constants used have to be determined
        by oscillatory flight maneuvers for the corresponding flow angles.
        
    Input:
        angl - array, indicated flow angle in rad
        qi - array, indicated dynamic pressure in mbar
        const - dict, contains the constants C2 (quadratic term) and
                    C1 (linear term)
        
    Output:
        out - array, pressure offset error
    '''
    
    out = (const['C2'] * angl**2 + const['C1'] * angl) * qi
    
    return(out)
    

    
def dyn_press_ps_error(qi, C):
    '''
    Calculates the impact pressure dependend static defect by using a quadratic 
        correction function. The constant used have to be determined by
        fast-slow flight maneuvers.
        
    Input:
        C - dict, correction constants for the static defect
        qi - array, indicated dynamic pressure in mbar
        
    Output:
        out - array, pressure offset error
    '''
    
    out = C['C2'] * qi**2 + C['C1'] * qi
    
    return(out)
    
def dyn_press_q_error(qc, C):
    '''
    Calculates the impact pressure dependend dynamic pressure defect by using a 
    simple linear correction function. The constant used have to be determined
    by reverse-heading flight maneuvers.
        
    Input:
        C - float, correction constant for the dynamic pressure error
        qc - array, indicated dynamic pressure in mbar
        
    Output:
        out - array, pressure offset error
    '''
    
    out = C * qc
    
    return(out)
