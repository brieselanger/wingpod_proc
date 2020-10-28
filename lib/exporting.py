#data export tools
#requires 'simplekml' package:
#https://pypi.python.org/pypi/simplekml/
#2018/08/20
#Alexander Buetow
#Institute for Space Sciences
#Free University of Berlin

#+++MODULES+++
import simplekml
import numpy as np
from datetime import datetime
import os
import zipfile

#+++FUNCTIONS+++
def kml_imu_export(nova1, path, trk_res = 100, pin_res = 300):
    """
    Exports a kml file of the flight track and sets points along with data of
        the IMU. Useful to quickly verify data captured by the
        IMU and to show the flown track. Requires simplekml module.
        
    Input:
        nova1 - Novatel-data of Logger %IMURATEPVASA
        path - export path
        trk_res - density of linestrings in the kml (plot every n-th datapoint)
        pin_res - density of pins containing IMU data (same as above)
        
    Output:
        None
    """
    kml = simplekml.Kml(open = 1)
    linestring = kml.newlinestring(name = "Pfad 1")
    for i in range(0, len(nova1), trk_res):
        linestring.coords.addcoordinates([(nova1['lon'].values[i],
                                               nova1['lat'].values[i],
                                               nova1['height'].values[i])])
    
    linestring.altitudemode = simplekml.AltitudeMode.relativetoground
    linestring.extrude = 1
    linestring.style.linestyle.color = 'ff0000ff'
    
    pnt = kml.newpoint()
    pnt.name = 'Start: ' + datetime.utcfromtimestamp(
                nova1['gnss_time_1'].values[0]).strftime('%H%Mz')
    pnt.coords = [(nova1['lon'].values[0], nova1['lat'].values[0],
                       nova1['height'].values[0])]
    pnt = kml.newpoint()
    pnt.name = 'Stop: ' + datetime.utcfromtimestamp(
                nova1['gnss_time_1'].values[-1]).strftime('%H%Mz')
    pnt.coords = [(nova1['lon'].values[-1], nova1['lat'].values[-1],
                       nova1['height'].values[-1])]
    for i in range(0, len(nova1), pin_res): #every 5 miniutes
        pnt = kml.newpoint()
        pnt.name = datetime.utcfromtimestamp(
                    nova1['gnss_time_1'].values[i]).strftime('%H%Mz')
        pnt.coords = [(nova1['lon'].values[i],nova1['lat'].values[i],
                           nova1['height'].values[i])]
        time = datetime.utcfromtimestamp(
                    nova1['gnss_time_1'].values[i]).strftime('%H%M')
        height = round(nova1['height'].values[i],1)
        u_p = round(nova1['u_p'].values[i], 1)
        v_p = round(nova1['v_p'].values[i], 1)
        w_p = round(nova1['w_p'].values[i], 1)
        spd = round(np.sqrt(u_p**2 + v_p**2 + w_p**2),1)
        azi = round(nova1['psi'].values[i] / np.pi * 180, 1)
        roll = round(nova1['phi'].values[i] / np.pi * 180, 1)
        pitch = round(nova1['theta'].values[i] / np.pi * 180, 1)
        ins = int(nova1['ins_state'].values[i])
        pnt.description = '''Time: {0} z\n
        Height: {1} m
        u_p: {2} m/s
        v_p: {3} m/s
        w_p: {4} m/s
        Speed: {5} m/s
        Azimuth: {6} deg
        Roll: {7} deg
        Pitch: {8} deg
        INS status: {9}
        
        INS status legend:
            0: 'INS_INACTIVE'
            1: 'INS_ALIGNING'
            2: 'INS_HIGH_VARIANCE'
            3: 'INS_SOLUTION_GOOD'
            6: 'INS_SOLUTION_FREE'
            7: 'INS_ALIGNMENT_COMPLETE'
            8: 'DETERMINING_ORIENTIATION'
            9: 'WAITING_INITIALPOS'
        '''.format(time, height, u_p, v_p, w_p, spd, azi, roll,
        pitch, ins)
    kml.save(path + "ins_track.kml")
    
    return(None)

def kml_wind_export(df, barb_path, out_path, spd_scale, res = 5, maxi = 200,
                    step = 5, scale = 1):
    """
    Exports wind data as kml file with wind barbs.
    
    Input:
        df - pd.DataFrame, containing the wind data
        barb_path - str, input path of wind barb icons
        out_path - str, saving directory for packed kmz file
        spd_scale - int, scaling facor for wind speed
        res - int, time resolution in seconds for the plot
        maxi - int, wind speed in knots of the wind barbs with maximum wind
                speed
        step - int, stepping size of wind barbs (5 knots is common)
        scale - float, scaling factor for icon size
        
    Output:
        None
    """
    
    #open output file
    f = open(out_path + 'wind_data.kml', 'w')
    #write header
    f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n' + 
            '<kml xmlns="http://www.opengis.net/kml/2.2">\n' +  
            '<Document>\n\n')
    #generate style classes for wind barbs
    for i in range(0, maxi+1, step):
        f.write(
                '<Style id="{0}">\n'.format(i) + 
                '<IconStyle>\n' + 
                '<scale>{0}</scale>\n'.format(scale) +
                '<Icon>\n' +
                '<href>{0}.png</href>\n'.format(i) +
                '</Icon>\n' +
                '</IconStyle>\n' +
                '</Style>\n\n'
                )
        
    #generate placemarks
    res = 5 #set a placemark every n-th second
    dur = int(df['time'].values[-1]-df['time'].values[0])
    for i in range(0, len(df), int(len(df)/dur*res)):
        spd = round(df['wspd'].values[i])*spd_scale
        if not np.isnan(spd) and spd <= maxi:
            spd = int(spd)
            f.write(
                    '<Placemark>\n' +
                    '<styleUrl>#{0}</styleUrl>\n'.format(
                    int(df['wspd'].values[i])*5) +
                    '<Style>\n' +
                    '<IconStyle>\n' + 
                    '<heading>{0}</heading>\n'.format((df['wdir'].values[i] + 
                              180) % 360) +
                    '</IconStyle>\n' + 
                    '</Style>\n' +
                    '<description>\n' +
                    'Time: {0} UTC\n\n'.format(datetime.utcfromtimestamp(
                    df['time'].values[i]).strftime('%H:%M:%S')) + 
                    'Height: {0} m\n'.format(
                            round(df['height'].values[i], 2)) +
                    'TAS: {0} m/s\n\n'.format(round(df['vtas'].values[i], 2)) +
                    'horiz. wind speed: {0} m/s\n'.format(
                            round(df['wspd'].values[i], 2)) +
                    'horiz. wind dir.: {0} °\n\n'.format(
                            round(df['wdir'].values[i], 1)) +
                    'Temperature: {0}°C\n'.format(
                            round(df['T'].values[i] -273.15, 1)) +
                    'Dewpoint: {0}°C\n'.format(round(
                            df['Td'].values[i] - 273.15, 1)) +
                    'Relative Humidity: {0}%\n\n'.format(
                            round(df['rh'].values[i], 1)) +
                    'u: {0} m/s\n'.format(round(df['u'].values[i], 2)) +
                    'v: {0} m/s\n'.format(round(df['v'].values[i], 2)) +
                    'w: {0} m/s'.format(round(df['w'].values[i], 2)) +
                    '</description>\n' +
                    '<Point>\n' + 
                    '<coordinates>{0}, {1}, {2} </coordinates>\n'.format(
                            df['lon'].values[i], df['lat'].values[i],
                            df['height'].values[i]) +
                    '<altitudeMode>absolute</altitudeMode>\n' + 
                    '</Point>\n' + 
                    '</Placemark>\n\n'
                    )
    #write footer and close file
    f.write('</Document>\n</kml>')
    f.close()
    
    zip = zipfile.ZipFile(out_path + 'wind.kmz', 'w', zipfile.ZIP_DEFLATED)
    zip.write(out_path + 'wind_data.kml', arcname='wind_data.kml')
    for file in os.listdir(barb_path):
        zip.write(barb_path + file , arcname=file)
    zip.close()
    
    os.system('rm ' + out_path + 'wind_data.kml')
    
    return(None)

def csv_export(df, out_path, file_name, compress=True, sep=','):
    """
    Exports (and compresses) dataframes containing any data as csv.
    
    Input:
        df - pd.DataFrame, contains data to be exported
        out_path - str, output path
        file_name - str, name of output file.
        compress - bool, compresses ascii output file if true
        sep - str, seperator string
        
    Output:
        None
    """
    df.to_csv(out_path + file_name, sep=sep, encoding='utf-8')
    
    if compress: #compress if '.zip' suffix
        out_string = file_name + '.zip'
        zip = zipfile.ZipFile(out_path + out_string, 'w', zipfile.ZIP_DEFLATED)
        zip.write(out_path + file_name, arcname=out_string)
        zip.close()
        os.system('rm ' + out_path + file_name)
    
    return(None)