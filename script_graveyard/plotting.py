#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 16:08:21 2017

@author: A. Buetow
"""
#plotting stuff
#2017/09/04
#Alexander Buetow
#alexander.buetow@freenet.de
#Institute for Space Sciences
#Free University of Berlin

import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')

plot_path = '/home/axel/Dropbox/Dokumente/studium/WeWi/5Loch/documentation/plots/'

def ql_timestamps(df,smooth,nom,plot_path,pre,za=5000,ze=5020,
                  time_col='time',ext='pdf'):
    """
    Quick look plotting functions for DataFrames wipdfth different smoothing
        values. Returns simple plots to quick check timestamp jitter and
        smoothing performance.
    Imput:
        df - DataFrame
        smooth - list of smoothing values to be plotted
        nom - int values for nominal logging interval in seconds
        plot_path - str of destination path to save plots
        pre - str, filename prefix
        out - str, filename with extension (.pdf, .png, .jpg, ...)
        za - int value for start point of zoomed data slicing
        ze - int value for end point of zoomed data slicing
        time_col - str of timestamp column in df
        ext - str, file extension (pdf, png, jpg, ...)
    Output:
        None
    """
    
    a = df[time_col][(df[time_col] > df[time_col].values[za]) &
               (df[time_col] < df[time_col].values[ze])].values[0]
    e = df[time_col][(df[time_col] > df[time_col].values[za]) &
               (df[time_col] < df[time_col].values[ze])].values[-1]
    #figure 1:
    y = df[time_col][(df[time_col] > a) & (df[time_col] < e)]
    y = y - y.values[0]
    plt.plot(range(0,len(y)),y,label=r'$\Delta T_{Log}$')
    ynom = np.arange(0,(ze-za)*nom,nom)
    plt.plot(range(0,len(ynom)),ynom,
             label=r'$\Delta T_{nom}=' + str(nom) + r'\ s$',color='grey',
             linestyle='--') #theoretischer timestamp bei f=50Hz
    for i,s in enumerate(smooth):
        if s == 0:
            df_new = df
        else:
            df_new = pp.time_interpol(df,smooth=s,time_col=time_col)
        y = df_new[time_col][(df_new[time_col] > a) & (df_new[time_col] < e)]
        y = y - float(y[:1])
        l = len(y)
        if s == 0:
            label_str = r'$\Delta T_{Log}$'
        label_str = r'$\Delta T_{S' + str(s) + r'}$'
        plt.plot(range(0,l),y,label=label_str)
    plt.xlabel('Samples [$n$]')
    plt.ylabel(r'$\Delta T_{k}$ [$s$]')
    plt.legend(loc=2)
    
    plt.savefig(plot_path + pre + '_plot_1.' + ext)
    plt.close()
   
    #figure 2:
    mid = round(len(df)/2)
    beg = round(len(df)/20)
    cut = len(df)-round(len(df)/20)
    
    df_diff = (df[time_col].values[beg+1:cut]-df[time_col].values[beg:cut-1])
    df_diff_mean = np.mean(df_diff[df_diff < np.median(df_diff)*3])
    df_diff_std = np.std(df_diff[df_diff < np.median(df_diff)*3])
    
    print(pre,df_diff_mean,df_diff_std,df_diff_std/df_diff_mean*100)
    
    plt.plot(range(0,len(df_diff)),df_diff,label=r'$\Delta T_{L}$')
    for i,s in enumerate(smooth):
        if s == 0:
            df_new = df
        else:
            df_new = pp.time_interpol(df,smooth=s,time_col=time_col)
        df_new_diff = (df_new[time_col].values[1:]-df_new[time_col].values[:-1])[beg:cut]
        df_new_diff_mean = np.mean(df_new_diff[df_new_diff < np.median(df_new_diff)*3])
        df_new_diff_std = np.std(df_new_diff[df_new_diff < np.median(df_new_diff)*3])
        print(pre,df_new_diff_mean,df_new_diff_std,df_new_diff_std/df_new_diff_mean*100)
        plt.plot(range(0,len(df_new_diff)),df_new_diff,label=r'$\Delta T_{S' + str(s) + r'}$')
    plt.xlabel(r'Samples [$n$]')
    plt.ylabel(r'$\Delta T$ [$s$]')
    leg = plt.legend(loc=1)
    leg.get_frame().set_alpha(0.8)
    
    plt.axhline(df_diff_mean+df_diff_std,linestyle='--',color='grey')
    plt.axhline(df_diff_mean-df_diff_std,linestyle='--',color='grey')
    
    plt.savefig(plot_path + pre + '_plot_2.' + ext)
    plt.close()
    
    return(None)

#cpt6100 sensors
ql_timestamps(press_spd,smooth=[1,40],nom=0.02,plot_path=plot_path,pre='spd',ext='png')
ql_timestamps(press_alt,smooth=[1,40],nom=0.02,plot_path=plot_path,pre='alt',ext='png')
ql_timestamps(press_alp,smooth=[1,40],nom=0.02,plot_path=plot_path,pre='alp',ext='png')
ql_timestamps(press_bet,smooth=[1,40],nom=0.02,plot_path=plot_path,pre='bet',ext='png')

ql_timestamps(hmt_data,smooth=[1,40],nom=0.54,plot_path=plot_path,pre='hmt',ext='png')

ql_timestamps(nova0,smooth=[1,40],nom=0.05,plot_path=plot_path,pre='nova0',ext='png')
ql_timestamps(nova1,smooth=[1,40],nom=0.05,plot_path=plot_path,pre='nova1',ext='png')

ql_timestamps(usb1608_data,smooth=[1,40],nom=0.02,plot_path=plot_path,pre='usb1608',ext='png')



#+++PLOTTING MAPS+++
from mpl_toolkits.basemap import Basemap

#llon = np.min(data['lon'])-0.2
#llat = np.min(data['lat'])-0.2
#ulon = np.max(data['lon'])+0.2
#ulat = np.max(data['lat'])+0.2
llon = 12.7
llat = 53.75
ulon = 13.1
ulat = 54.05


mlon = np.mean(data['lon'])
mlat = np.mean(data['lat'])

my_map = Basemap(projection='stere', area_thresh=1000, resolution='l',
                 lat_0=mlat, lon_0=mlon,
                 llcrnrlon=llon, llcrnrlat=llat,
    urcrnrlon=ulon, urcrnrlat=ulat)

my_map.drawcoastlines()
my_map.drawcountries()
my_map.bluemarble(alpha=0.7)
#my_map.fillcontinents(color='#00000033')
my_map.drawmapboundary()

#my_map.drawmeridians(np.arange(llon, ulon, 1))
#my_map.drawparallels(np.arange(llat, ulat, 1))

time = 60 #plot a barb every n-th second
r = int(time/((data['time'].values[-1]-data['time'].values[0])/len(data)))
x,y = my_map(data['lon'].values[::r],data['lat'].values[::r])
u = data['u'].values[::r]
v = data['v'].values[::r]
h = data['height'].values[::r]

maxi = 3000 #max height in meters for color palete
for i in range(0,len(u)):
    plt.get_cmap('brg_r')(255)
    try:
        c = int(h[i]/maxi*255)
        rgb = plt.get_cmap('brg_r')(c)
        farbe = '#%02x%02x%02x' % (int(rgb[0]*255),int(rgb[1]*255),
                                    int(rgb[2]*255))
        my_map.barbs(x[i],y[i],u[i]*3.6/1.852,v[i]*3.6/1.852,color=farbe)
    except:
        pass
 
plt.savefig('/home/axel/Dropbox/Dokumente/studium/WeWi/5Loch/python/map.pdf')

plt.show()












