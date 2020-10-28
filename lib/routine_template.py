#Routine Name
#yyyy-mm-dd
#Alexander Buetow
#Free University of Berlin

#Sources: what- and whoever

#+++LIBRARIES+++
import numpy as np
import matplotlib.pylab as plt
import pandas as pd

#+++FUNCTIONS+++
def example(tas,alp,bet,the,psi,up,vp,wp):
    
    """
    +++simplified 3D wind vector calculation according to LENSCHOW (1986)+++
    
    DISCRIPTION: Calculates the 3D wind vector form aircraft INS and gust probe
                 measurements via a simplified method, suitable for small
                 attack angles on the gust probe.
    
    INPUT:
            tas      m/s    true aispeed (TAS)
            alp      rad    angle of attack (alpha)
            bet      rad    sideslip angle (beta)
            the      rad    pitch angle (theta)
            psi      rad    true heading (psi)
            up       m/s    easterly component of acft velocity
            vp       m/s    northerly component of acft velocity
            wp       m/s    vertical component of acft velocity          
            
    CONSTANTS:
            what     b/s    thingy
        
    OUTPUT:
           u         m/s    easterly wind component
           v         m/s    northerly wind component
           w         m/s    vertical wind component
           
    REFERENCES:
        F. Bar: Blabla. American Meteorology Society, 1900

    """
    
    u = tas*sin(psi+bet)+up
    v = tas*cos(psi+bet)+vp
    w = -tas*sin(the-alp)+wp
    
    return u, v, w
