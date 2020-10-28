#Calculation of wind and misc flight parameters according to Lenschow (1986)
#2018/03/19
#Alexander Buetow
#Institute for Space Sciences
#Free University of Berlin

#Sources: D. Lenschow. Probing the atmospheric boundary layer.
#           American Meteorological Society, 1986
#         D. Lenschow and P. Spyers-Duran. Measurement techniques: Air motion
#           sensing. National Center for Atmospheric Research (NCAR) Research
#           Aviation Facility (RAF) bulletin, 23, 1989.
#         Source Code of 'egads' repository on GitHub (last check:
#                                                       13th Feb 2018):
#           https://github.com/EUFAR/egads/blob/master/egads/algorithms/
#               thermodynamics/wind_vector_3d_raf.py

#+++MODULES+++
import numpy as np
import pandas as pd

#+++FUNCTIONS+++

def ups_angl(q, dp, C, tau0, rad=True):
    """
    This function transfers measured differential and dynamic
        pressure to a flow angle in rad
        
    Input:
        q       Pa          dynamic pressure
        dp      Pa          differential pressure
        rad     bool        returns rad if True, deg otherwise
        C       1/deg       flow angle sensitivity factor
        tau0    deg         offset angle between probe and IMU
            
    Output:
        a       rad         upstream flow angle
    """
    if rad:
        fac = np.pi / 180
    else:
        fac = 1
    a = ((dp / (C * q)) - tau0) * fac
    
    return(a)

def wind_out(ps, ps_c, q, q_c, dpa, dpb, Tr, the, the_d, psi, psi_d, phi, u_p,
             v_p, w_p, alp0, bet0, Calp, Cbet, L, r = 1, simple = False):
    """
    Collection of all necessary functions for wind vector
        calculation.  
            
    Input:
        ps      Pa          indicated static pressure from 'altitude' sensor
        ps_c    Pa          corrected static pressure from 'altitude' sensor
        q       Pa          indicated dynamic pressure from 'airspeed' sensor
        q_c     Pa          corrected dynamic pressure from 'airspeed' sensor
        dpa     Pa          differential pressure  from 'alpha' sensor
        dpb     Pa          differential pressure from 'beta' sensor
        Tr      K           measured TAT probe temperature
        the     rad         pitch angle (theta)
        the_d   rad/s       pitch angle rate (theta dot)
        psi     rad         true heading (psi)
        psi_d   rad/s       heading rate (psi dot)
        phi     rad         roll angle (phi)
        u_p     m/s         easterly component of acft velocity
        v_p     m/s         northerly component of acft velocity
        w_p     m/s         vertical component of acft velocity
        alp0    rad         angle of attack offset angle
        bet0    rad         slip offset angle
        Calp    1/deg       differential pressure sensitivity factor - angle of
                                attack
        Cbet    1/deg       differential pressure sensitivity factor - yaw
                                angle
        L       m           distance between IMU coordination system origin and
                                probe tip
        r       dimless     TAT probe recovery factor
        simple  boolean     False for simplified wind calculation algorithm
            
    Output:
        vtas    m/s         true airspeed
        alp     rad         angle of attack
        bet     rad         slip angle
        alp_d   deg         angle of attack in degrees
        bet_d   deg         slip angle in degrees
        u       m/s         wind component in x direction (eastward)
        v       m/s         wind component in y direction (northward)
        w       m/s         wind component in z direction (vertical)
        spd     m/s         absolute wind speed
        dir     deg         wind direction, true north reference
    """
    
    def vtas(qc, psc, Tr, k = 1.402, r = 1, R = 287.1):
        
        """
        Calculates true airspeed
        
        Input:
            qc      Pa          corrected dynamic pressure
            psc     Pa          corrected static pressure
            Tr      K           measured temperature
                
        Constants:
            k       dimless     adiabatic coefficient (may not be exactly
                                                       constant)
            r       dimeless    recovery factor of temperature probe
            R       J/(Kg*K)    gas constant for dry air
            
        Output:
            vtas     m/s         true airspeed
    
        """
        
        p0 = qc + psc # total pressure
        # Mach squared:
        M2 = (2 / (k - 1)) * ((p0 / psc) ** ((k - 1) / k) - 1)
        vtas = np.sqrt((k * R * M2 * Tr)/(r * ((k - 1) / 2) * M2 + 1))
        
        return(vtas)
    
    def wind_s(U_a, alp, bet, the, psi, u_p, v_p, w_p):
        
        """
        SIMPLIFIED calculation of 3D wind vector form aircraft INS and gust
            probe measurements, suitable for small attack angles on the gust
            probe.
        
        Input:
            U_a      m/s    true aispeed (TAS)
            alp      rad    angle of attack (alpha)
            bet      rad    sideslip angle (beta)
            the      rad    pitch angle (theta)
            psi      rad    true heading (psi)
            u_p      m/s    easterly component of acft velocity
            v_p      m/s    northerly component of acft velocity
            w_p      m/s    vertical component of acft velocity          
        
        Output:
            u         m/s    easterly wind component
            v         m/s    northerly wind component
            w         m/s    vertical wind component
        """
        
        u =  U_a * np.sin(psi + bet) + u_p
        v = -U_a * np.cos(psi + bet) + v_p
        w = -U_a * np.sin(the - alp) + w_p
        
        return(u, v, w)
    
    def wind_f(U_a, alp, bet, the, the_d, psi, psi_d, phi, u_p, v_p, w_p, L):
        
        """
        Calculates the 3D wind vector form aircraft INS and gust probe
            measurements, according to LENSHOW (1986). Code mostly copied from
            EUFAR 'egdar' python library.
        
        Input:
            U_a        m/s    true aispeed 
            alp        rad    angle of attack
            bet        rad    sideslip angle (beta)
            the        rad    pitch angle (theta)
            the_d      rad/s  pitch angle rate (theta dot)
            psi        rad    true heading (psi)
            psi_d      rad/s  heading rate (psi dot)
            phi        rad    roll angle
            u_p        m/s    easterly component of acft velocity
            v_p        m/s    northerly component of acft velocity
            w_p        m/s    vertical component of acft velocity    
            L          m      distance between IMU coordination system origin
                                and probe tip
            
        Output:
            u           m/s    easterly wind component
            v           m/s    northerly wind component
            w           m/s    vertical wind component
        
        """
        
        D = (1 + np.tan(alp)**2 + np.tan(bet)**2)**(1 / 2)
        
        u = (-U_a / D * (np.sin(psi) * np.cos(the) + np.tan(bet) *
                         (np.cos(psi) * np.cos(phi) + np.sin(psi) *
                          np.sin(the) * np.sin(phi)) + np.tan(alp) *
                          (np.sin(psi) * np.sin(the) * np.cos(phi) -
                           np.cos(psi) * np.sin(phi))) + u_p - L *
                          (the_d * np.sin(the) * np.sin(psi) - psi_d *
                           np.cos(psi) * np.cos(the)))
                         
        v = (-U_a / D * (np.cos(psi) * np.cos(the) - np.tan(bet) *
                         (np.sin(psi) * np.cos(phi) - np.cos(psi) *
                          np.sin(the) * np.sin(phi)) + np.tan(alp) *
                          (np.cos(psi) * np.sin(the) * np.cos(phi) +
                           np.sin(psi) * np.sin(phi))) + v_p - L *
                          (psi_d * np.sin(psi) * np.cos(the) + the_d *
                           np.cos(psi) * np.sin(the)))
                         
        w = (-U_a / D * (np.sin(the) - np.tan(bet) * np.cos(the) *
                         np.sin(phi) - np.tan(alp) * np.cos(the) *
                         np.cos(phi)) + w_p + L * the_d * np.cos(the))
    
        return(u, v, w)
    
    alp = ups_angl(q_c, dpa, Calp, alp0) # angle of attack, rad
    bet = ups_angl(q_c, dpb, Cbet, bet0) # slip angle, rad
    U_a = vtas(q_c, ps_c, Tr) #true airspeed calculation
    if simple:
        u, v, w = wind_s(U_a, alp, bet, the, psi, u_p, v_p, w_p)
    else:
        u, v, w = wind_f(U_a, alp, bet, the, the_d, psi, psi_d, phi, u_p, v_p,
                         w_p, L)
    wdir = np.arctan2(u, v) * 180 / np.pi + 180
    wspd = np.sqrt(u**2 + v**2)
    cols = ['vtas', 'alp', 'bet', 'u', 'v', 'w', 'wspd',
            'wdir'] #create new columns
    out = pd.DataFrame({cols[0]: U_a, cols[1]: alp, cols[2]: bet, cols[3]: u,
                        cols[4]: v,cols[5]: w, cols[6]: wspd, cols[7]: wdir},
        columns=cols) #append new columns
    
    return(out)
