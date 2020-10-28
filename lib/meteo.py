#meteorological calculation collection
#2018/06/13
#Alexander Buetow
#alexander.buetow@freenet.de
#Institute for Space Sciences
#Free University of Berlin

#Sources: H. M. Wallace, P. V. Hoobs: Atmospheric Science. 2nd edition, 
#           Academic Press, 2006


#+++MODULES+++
import numpy as np

#+++FUNCTIONS+++

def add_meteo(df):
    '''
    Adds additional meteorological values to the dataframe
    
    Input:
        
        df - pd.DataFrame, DataFrame containing synchronized measurements
        
    Output:
        
        df - pd.DataFrame, DataFrame with additional values appended
    '''

    def virtual_temp(T, w, e=0.622):
        '''
        Calculation of virtual temperature
        
        Input: 
            
            T     K         dry temperature
            w     Kg/Kg     mixing ratio water to dry air
            e     dimless   ratio of specific gas constant for dry air and
                                water vapour
            
        Output:
            
            Tv - virtual temperature
        '''
        
        Tv = T * ( (w + e) / (e * (1 + w) ) )
        
        return(Tv)
    
    def air_density(ps, Tv, Rd=287.05):
        '''
        Calculation of air density using the ideal gas law
        
        Input:
            
            ps     Pa         static pressure
            Tv     K          virtual temperature
            Rd     J/K/Kg     gas constant for dry air
            
        Ouput:
            
            rho    Kg/m^3     air density
            
        '''
        
        rho = ps / Rd / Tv
        
        return(rho)
        
    def ind_spd(q, rho):
        '''
        Calculation of indicated airspeed
        
        Input:
            
            q     Pa         impact pressure
            rho   Kg/m^3     air density
            
        Output:
            
            u     m/s        indicated airspeed
        '''
        
        u = np.sqrt(2 * q / rho)
        
        return(u)
    
    def pot_temp(T, ps, p0=100000, cp=1004, Rd=287.05):
        '''
        Calculation of potential temperature
        
        Input:
            
            T     K          air temperature
            ps    Pa         (hydro)static pressure
            p0    Pa         reference pressure (1000 hPa commonly used)
            cp    J/K/Kg     specific heat constant for dry air and
                                constant pressure
            Rd    J/K/Kg   gas constant for dry air
                                
        Output:
            
            Theta   K          potential temperature
            
        '''
        
        Theta = T * (p0 / ps)**(Rd / cp)
        
        return(Theta)
        
    def equiv_pot_temp(Theta, T, w, cp=1004, L=2.5E+6):
        '''
        Calculation of equivalent potential temperature
            (in german: "pseudopotentielle Temperatur" [sic]...not to be
            confused with "Äquivalent-potentielle Temperatur")
        
        Input:
            
            Theta   K          potential temperature
            T       K          air temperature
            w       Kg/Kg      mixing ratio water to dry air
            cp      J/K/Kg     specific heat constant for dry air and
                                   constant pressure  
            L       J/Kg       latent heat of vaporization at 0°C
            
        Output:
            
            Theta_e
            
        '''
        
        Theta_e = Theta * np.exp(L * w / cp / T)
        
        return(Theta_e)
        
    def ias(q, rho=1.225):
        '''
        Calculates indicated airspeed
        The indicated airspeed equals the true airspeed within ISA conditions
        
        Input:
            q    Pa       dynamic pressure
            rho  Kg/m^3   air density under ISA conditions
            
        Output:
            
            ias  m/s      indicated airspeed
            
        '''
        
        ias = np.sqrt(2 * q / rho)
        
        return(ias)
        
    df['Tv'] = virtual_temp(df['T'], df['x']) #add virtual temperature
    df['rho'] = air_density(df['p_alt_corr'], df['Tv']) #add air density
    df['T_Theta'] = pot_temp(df['T'], df['p_alt_corr']) #pot temperature
    #equiv. pot. temperature
    df['T_Theta_e'] = equiv_pot_temp(df['T_Theta'], df['T'], df['x'])
    df['ias'] = ias(df['p_spd_corr']) #add indicated airspeed
    
    return(df)
