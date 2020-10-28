#some plots for Carsten
#2018/01/15
#Alexander Buetow
#Institute for Space Sciences
#Free University of Berlin

#plotting example for turbidity within and out of the PBL by showing vertical
#wind component w

t_o = [1502793671,1502794741]
t_i = [1502786212,1502787282]

def slicer(df,key,time):
    """
    Slicing data
    """
    
    return(df[key][(df['time'] > time[0]) & (df['time'] < time[1])])

#removing bias by simply subtracting mean
w_o = slicer(data,'w',t_o)
w_o = w_o - np.mean(w_o)
time_o = slicer(data,'time',t_o)
time_o = (time_o-time_o.iloc[0])/60
h_o = np.mean(slicer(data,'height',t_o))

#mean wind speed
wspd_mean_o = np.mean(slicer(data,'wspd',t_o))
wspd_mean_i = np.mean(slicer(data,'wspd',t_i))

#mean wind directory
wdir_mean_o = np.mean(slicer(data,'wdir',t_o))
wdir_mean_i = np.mean(slicer(data,'wdir',t_i))

w_i = slicer(data,'w',t_i)
w_i = w_i - np.mean(w_i)
time_i = slicer(data,'time',t_i)
time_i = (time_i-time_i.iloc[0])/60
h_i = np.mean(slicer(data,'height',t_i))

plt.plot(time_i,w_i,label='innerhalb PBL (ca. 230m AGL)',color='red')
plt.plot(time_o,w_o,label='oberhalb PBL (ca. 2450m AGL)',color='blue')
plt.axhline(0,color='black',alpha=0.5,linestyle='--')
plt.xlim(0,16)
plt.ylim(-4,4)
plt.xlabel('relative Flugzeit (min)')
plt.ylabel('Vertikalkomponente des Windes (m/s)')

plt.legend(framealpha=0.8)

plt.savefig('out.png',dpi=500)

plt.close()

sec = 20
a = round(len(time_i)/2)
b = a + 1000*sec
time_i_new = (time_i[a:b]-time_i.iloc[a])*60
time_o_new = (time_o[a:b]-time_o.iloc[a])*60

#10s example
plt.plot(time_i_new,w_i[a:b],label='innerhalb PBL (ca. 230m AGL)',color='red')
plt.plot(time_o_new,w_o[a:b],label='oberhalb PBL (ca. 2450m AGL)',color='blue')
plt.axhline(0,color='grey',alpha=0.5,linestyle='--')
for i in np.arange(0,sec+1,2):
    plt.axvline(i,color='grey',alpha=0.8,linestyle='--',linewidth=0.4)
plt.xticks(np.arange(0,sec+1,2))
plt.xlim(0,sec)
plt.ylim(-4,4)
plt.xlabel('relative Flugzeit (s)')
plt.ylabel('Vertikalkomponente des Windes (m/s)')

plt.legend(framealpha=0.8)

plt.savefig('out_zoomed.png', dpi=500)