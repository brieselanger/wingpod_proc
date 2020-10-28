# coding: utf-8

# # Aerodynamik II
# ## Übung II
# Alexander Bütow | WiSe 16/17 | 07.12.17

# ## Funktionen

# In[2]:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')

#1.)

def cp_comp(m,p_s,p_x,k=1.402):
    """
    Calculation of compressible cp-Value
    """
    return(2/(k*m**2)*((p_x/p_s)-1))

def cp_incomp(rho,u,p_s,p_x,k=1.402):
    """
    Calculation of incompressible cp-Value
    """
    return((p_x-p_s)/(.5*rho*(u**2)))

def cp_crit(m_k,k=1.402):
    """
    Calculation of critical cp-value for a given critical m-value
    See Script [6.3]
    """
    return((2/(k*m_k**2))*((((1+((k-1)/2)*m_k**2)/(1+((k-1)/2)))**(k/(k-1)))-1 ))

#2.)

def cp_corr(cp_0,m,corr='pg',k=1.402):
    """
    Correction for a given incompressible cp-Value at a given Mach-speed
    Options for 'corr' attribute:
        'pg' - Prandtl-Glauert (default)
        'kt' - Karman-Tsien
        'la' - Laitone
    """
    if corr == 'pg':
        return(cp_0/((1-m**2)**.5))
    elif corr == 'kt':
        return(cp_0/(((1-m**2)**.5)+(((m**2)/(1+((1-m**2)**0.5)))*(cp_0/2))))
    elif corr == 'la':
        return(cp_0/((1-m**2)**.5)+((((m**2)/(2*((1-m**2)*0.5)))*(1+(((k-1)/2)*m**2)))*cp_0))
    else:
        return(None)
    
def rho_calc(p,T,R=287):
    """
    Calculation of air density with the ideal gas law
    """
    
    return(p/(R*T))

def a_speed_calc(T,pol=1.402,R=287):
    """
    Calculation of Mach number
    """
    
    return((T*pol*R)**.5)

#lineare Interpolation
#aus Satmeteovorlesungen übernommen

def linear_interpol(x,xv,yv):
    """
    x - ort der interpolation
    xv (mess)punkt, must be ascending!
    yv (mess)wert
    """
    
    def find_upper_index(x,xv):
        """
        verbatim
        xv must be ascending!
        """
        if x < xv[0]:
            return(None)
        for ixvv , xvv in enumerate(xv):
            if x <= xvv:
                return(ixvv)
        return(None)

    def find_index_and_weight(x,xv):
        """
        """
        i_upper=find_upper_index(x,xv)
        if i_upper is None:
            return(None)
        if i_upper == 0:
            return((0,0),(0,1.))
        i_lower=i_upper-1
        w_lower=(xv[i_upper]-x)/(xv[i_upper]-xv[i_lower])
        w_upper=1.-w_lower
        
        return((i_lower,w_lower),(i_upper,w_upper))

    iw=find_index_and_weight(x,xv)
    if iw is None:
        return(None)
    out=0.
    for iix in iw:
        out=out+yv[iix[0]]*iix[1]
    return(out)

#Berechnung des ca-Wertes

def ca_calc(cp_lo,cp_up,dx=0.1):
    """
    Calculation of ca value between a given dx
    cp_lo - cp value(s) below the wing
    cp_up - cp value(s) above the wing
    dx    - step size(s) (default dx=0.1)
    """
    return((cp_lo-cp_up)*dx)


# ## 1.)

# In[3]:

#Daten einlesen

files=['03','04','05','06','_krit']

for i,item in enumerate(files):
    file_string='./cast7_m' + item + '.dat'
    
    #Einlesen der Umgebungsvariablen
    single_vars=pd.read_csv(file_string, skiprows=1, nrows=4, header=None, delimiter='=')
    T_g=single_vars.iloc[0,1]
    p_g=single_vars.iloc[1,1]
    p_s=single_vars.iloc[2,1]
    m=single_vars.iloc[3,1]
    
    #Einlesen der Druckmessdaten
    data=pd.read_csv(file_string, delimiter='\t', skiprows=8, header=None)
    
    #kompressibler cp-Wert berechnen
    t=cp_comp(m=m, p_s=p_s, p_x=data[2])
    
    #Plotten der Messdaten
    plt.plot(data[1],t)
    plt.ylim((1,-1.5))
    plt.axhline(0,color='grey', linestyle='--')
    plt.ylabel(r'$c_p$')
    plt.xlabel(r'$x/l$')
    plt.savefig('./plots/plot_1_' + str(i) + '.pdf')
    
    plt.close()

#Plotten von cp_crit

x=np.linspace(0.2,1,100)
cp_k=cp_crit(m_k=x)

plt.plot(x,cp_k, linestyle='--', color='black', label=r'$c_{p,krit}$')
plt.ylim(0,-10)
plt.xlabel(r'$x/l$')
plt.ylabel(r'$c_p$')
plt.legend()
plt.savefig('./plots/plot_1_b.pdf')

plt.close()


# 
# ## 2.)

# In[4]:

#Datensatz einlesen

#Umgebungsvariablen einelsen und setzen
single_vars=pd.read_csv('./cast7_m03.dat', skiprows=1, nrows=4, header=None, delimiter='=')
T_g=single_vars.iloc[0,1]+273.15
p_s=single_vars.iloc[2,1]
p_g=single_vars.iloc[1,1]
m=single_vars.iloc[3,1]
rho=rho_calc(p=p_s, T=T_g)
u=a_speed_calc(T_g)*m

#Datensatz einlesen
data=pd.read_csv('./cast7_m03.dat', delimiter='\t', skiprows=8, header=None)

#Referenz-cp-Werte bei M=0.3 generieren
cp_ref=cp_incomp(rho=rho, u=u, p_s=p_s, p_x=data[2])

files2=['04','05','06']

#Datensätze einlesen und plotten
for i, item in enumerate(files2):
    #Einlesen der Umgebungsvariablen
    file_string='./cast7_m' + item + '.dat'
    data=pd.read_csv(file_string, delimiter='\t', skiprows=8, header=None)
    single_vars=pd.read_csv(file_string, skiprows=1, nrows=4, header=None, delimiter='=')
    m=single_vars.iloc[3,1]
    p_s=single_vars.iloc[2,1]

    
    pg=cp_corr(cp_0=cp_ref,m=m,corr='pg')
    kt=cp_corr(cp_0=cp_ref,m=m,corr='kt')
    la=cp_corr(cp_0=cp_ref,m=m,corr='la')
    t=cp_comp(m=m, p_s=p_s, p_x=data[2])

    plt.plot(data[1], t, label=r'$c_{p,comp}$')
    plt.plot(data[1], pg, label='Prandtl-Glauert')
    plt.plot(data[1], kt, label='Karman-Tsien')
    plt.plot(data[1], la, label='Laitone')
    plt.axhline(0, linestyle='--', color='grey')
    plt.ylim(2,-2)
    plt.legend(loc=4)
    plt.xlabel(r'$x/l$')
    plt.ylabel(r'$c_p$')
    plt.savefig('./plots/plot_2_' + str(i) + '.pdf')
    plt.close()


# ## 3.)

# In[5]:

#rechnerische/grafische Bestimmung zur Bestimmung des kritischen cp- und Mach-Wertes
x=np.linspace(0.3,0.8,1000)
cp_k=cp_crit(m_k=x)

#Einlesen der Umgebungsvariablen
single_vars=pd.read_csv('./cast7_m03.dat', skiprows=1, nrows=4, header=None, delimiter='=')
T_g=single_vars.iloc[0,1]+273.15
p_s=single_vars.iloc[2,1]
p_g=single_vars.iloc[1,1]
m=single_vars.iloc[3,1]
rho=rho_calc(p=p_s, T=T_g)
u=a_speed_calc(T_g)*m

single_vars_krit=pd.read_csv('./cast7_m_krit.dat', skiprows=1, nrows=4, header=None, delimiter='=')
m_krit=single_vars_krit.iloc[3,1]
p_s_krit=single_vars_krit.iloc[2,1]

#Datensäte einlesen
data=pd.read_csv('./cast7_m03.dat', delimiter='\t', skiprows=8, header=None)
data_krit=pd.read_csv('./cast7_m_krit.dat', delimiter='\t', skiprows=8, header=None)

#Referenz-cp-Werte bei M=0.3 generieren
cp_ref=cp_incomp(rho=rho, u=u, p_s=p_s, p_x=data[2])

#Berechnen von den cp-Werten für den kompressiblen Fall bei M=0.63 (kritische Mach-Zahl)
cp_krit=cp_comp(m=m_krit, p_s=p_s_krit, p_x=data_krit[2])
cp_krit_min=np.min(cp_krit)

#Berechnung vom inkompressiblen cp-Wert und finden des Maximums
cp_min=np.min(cp_ref)

#extrapolieren mit Hilfe von Prandtl-Glauert und Karman-Tsien
cp_pg=cp_corr(cp_0=cp_min, m=x, corr='pg')
cp_kt=cp_corr(cp_0=cp_min, m=x, corr='kt')

#plotten
plt.plot(x, cp_pg, label='Prandtl-Glauert')
plt.plot(x, cp_kt, label='Karman-Tsien')
plt.plot(x, cp_k, linestyle='--', color='black', label=r'$c_{p,krit}$')
plt.ylim(0,-3)
plt.xlabel(r'$M$')
plt.ylabel(r'$c_p$')

#finde einfach nächsten Wert, ohne Interpolation
diff_pg=cp_k-cp_pg
diff_kt=cp_k-cp_kt

ind_pg=np.where(diff_pg == np.min(np.abs(diff_pg)))
ind_kt=np.where(diff_kt == np.min(np.abs(diff_kt)))

plt.plot(x[ind_pg], cp_pg[ind_pg], 'o', color='black', ms=3)
plt.axhline(cp_pg[ind_pg], xmin=.5, xmax=.9, linestyle='-', color='grey')
plt.axvline(x[ind_pg], ymin=.1, ymax=.5, linestyle='-', color='grey')
plt.text(x[ind_pg],cp_pg[ind_pg]+0.4, r'$M_{pg}=' + str(np.round(x[ind_pg],decimals=3)) +
         '$\n $c_{p,pg}=' + str(np.round(cp_pg[ind_pg],decimals=3)) + '$')

plt.plot(x[ind_kt], cp_kt[ind_kt], 'o', color='black', ms=3)
plt.axhline(cp_kt[ind_kt], xmin=.5, xmax=.9, linestyle='-', color='grey')
plt.axvline(x[ind_kt], ymin=.1, ymax=.5, linestyle='-', color='grey')
plt.text(x[ind_kt]-0.12,cp_kt[ind_kt]-0.2, r'$M_{kt}=' + str(np.round(x[ind_kt],decimals=3)) +
         '$\n $c_{p,kt}=' + str(np.round(cp_kt[ind_kt],decimals=3)) + '$')

plt.plot(m_krit, cp_krit_min, 'o', color='red', ms=3, label=r'$c_{p,krit}$ Messung')
plt.legend()

plt.savefig('./plots/plot_3_1.pdf')
plt.close()


# ## 4.)

# In[6]:

ca_all_exp=np.zeros(len(files)) #experimentell ermittelte ca-Werte
ca_all_exp_pg=np.zeros(len(files))
m_all=np.zeros(len(files))

for j,item in enumerate(files):

    file_string='./cast7_m' + item + '.dat'
    
    #Einlesen der Umgebungsvariablen
    single_vars=pd.read_csv(file_string, skiprows=1, nrows=4, header=None, delimiter='=')
    T_g=single_vars.iloc[0,1]
    p_g=single_vars.iloc[1,1]
    p_s=single_vars.iloc[2,1]
    m=single_vars.iloc[3,1]
    m_all[j]=m
    rho=rho_calc(p=p_s, T=T_g)
    u=a_speed_calc(T_g)*m
    
    #Einlesen der Druckmessdaten
    data=pd.read_csv(file_string, delimiter='\t', skiprows=8, header=None)
    
    #kompressiblen cp-Wert berechnen
    cp=cp_comp(m=m, p_s=p_s, p_x=data[2])
    
    #Zur Integration der cp-Werte zum ca-Wert, müssen die Messpunkte bestenfalls gegenüberliegen.
    #Da auf der Unterseite des Tragflügels weniger Druckbohrungen vorhanden sind, werden die oberen
    #Bohrpositionen als Referenz genommen und die unteren durch lineare Interpolation errechnet.
    
    i_u=np.arange(29)[::-1] #Indicies für Oberseite, invertiere Reihenfolge
    i_d=np.arange(28,len(data)) #Indicies für Unterseite
    cp_u=np.array(cp[i_u]) #cp-Werte Oberseite
    
    #Interpolation der Werte auf der Unterseite
    xv=np.append(np.array(data[1][i_d]),1) #definiere Messpunkte xv, an denen Messwerte gegeben sind
    yv=np.append(np.array(cp[i_d]),cp_u[len(cp_u)-1]) #zugehörige Messwerte
    x=np.array(data[1][i_u]) #Interpolationspunkte definieren
    
    #Das gleiche für Prandtl-Glauert
    if j == 0: #berechne zusätzlich cp inkompressibel für Prandtl-Glauert Extrapolation
        cp_ref=cp_incomp(u=u, rho=rho, p_s=p_s, p_x=data[2])
        
    cp_u_pg=cp_corr(cp_0=np.array(cp_ref[i_u]), m=m, corr='pg')
    yv_pg=np.append(np.array(cp_ref[i_d]),cp_u_pg[len(cp_u_pg)-1]) #zugehörige Messwerte
   
    #Array alokierenin denen die interpolierten Messwerte geschrieben werden sollen
    cp_l_new=np.zeros(len(x))
    cp_l_new_pg=np.zeros(len(x))
    
    for i,item in enumerate(x):
        cp_l_new[i]=linear_interpol(x=item, xv=xv, yv=yv)
        cp_l_new_pg[i]=linear_interpol(x=item, xv=xv, yv=yv_pg)
    
    x_diff=np.append(0,x[1:len(i_u)]-x[0:len(i_u)-1]) #d(x/l) für jedes x errechnen
    
    #Auftriebsbeiwert für experimentelle Daten integrieren
    ca=np.zeros(len(x))
    ca_pg=np.zeros(len(x))
    for i,item in enumerate(x_diff):
        ca[i]=ca_calc(cp_lo=cp_l_new[i],cp_up=cp_u[i],dx=x_diff[i])
        ca_pg[i]=ca_calc(cp_lo=cp_l_new_pg[i],cp_up=cp_u_pg[i],dx=x_diff[i])
    
    #Das gleiche für die Prandtl-Glauert extrapolierten Auftriebswerte
    
    ca_all_exp[j]=np.sum(ca)
    ca_all_exp_pg[j]=np.sum(ca_pg)
    
plt.plot(m_all, ca_all_exp, label=r'$c_{a,exp}$', color='blue')
plt.plot(m_all, ca_all_exp, 'o', color='blue', ms=3)
plt.plot(m_all, ca_all_exp_pg, label='$c_{a,pg}$', color='green')
plt.plot(m_all, ca_all_exp_pg, 'o', color='green', ms=3)
plt.legend(loc=2)
plt.xlabel(r'Machzahl $M$')
plt.ylabel(r'Auftriebsbeiwert $c_a$')
plt.savefig('./plots/plot_4_1.pdf')
plt.close()


# ## 5.)

# In[10]:

cp_0=np.zeros((100,5))

#Seien folgende Umgebungsvariablen gegeben (ISA auf Meereshöhe)
T_g=15+273.15
p_s=101325
m=np.linspace(0,1,100)
u=a_speed_calc(T=T_g)*m
rho=rho_calc(p=p_s, T=T_g) #Dichte

p_0=p_s+(.5*rho*u**2) #Gesamtdruck im Staupunkt

cp_0=(m, cp_incomp(p_s=p_s, p_x=p_0, rho=rho, u=u),
      cp_comp(m=m, p_s=p_s, p_x=p_0), cp_corr(cp_0=1,m=m,corr='pg'), cp_corr(cp_0=1,m=m,corr='kt'))

plt.plot(cp_0[0], cp_0[1], label=r'$c_{p,inc}$')
plt.plot(cp_0[0], cp_0[2], label=r'$c_{p,com}$')
plt.plot(cp_0[0], cp_0[3], label=r'$c_{p,pg}$')
plt.plot(cp_0[0], cp_0[4], label=r'$c_{p,kt}$')
plt.ylim((0.8,2))
plt.legend(loc=2)
plt.xlabel(r'Mach-Zahl $M$')
plt.ylabel(r'Druckbeiwert $c_p$')
plt.savefig('./plots/plot_5_1.pdf')
plt.close()

