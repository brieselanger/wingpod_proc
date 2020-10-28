#Testscript to check for consistency of calculated wind values from testdata
#files
#2019/01/24
#Alexander Buetow
#Institute for Space Sciences
#Free University of Berlin

import os
import sys
import shutil
import numpy as np
import pandas as pd

files = ['const.py', 'conf.py']
test_files = ['cpt6100_port0_data.txt', 'cpt6100_port1_data.txt',
              'cpt6100_port2_data.txt', 'cpt6100_port3_data.txt',
              'hmt310_data.txt', 'novatel2txt_data.txt',
              'usb1608fsplus_out.txt']
cwd = os.getcwd()
seq = ['u', 'v', 'w']

#The test is passed, if the differences between the variables given in the
#testvar.py file and the mean and standard deviation calculated from the
#testdata set is lower than the following pass criterion. 
diff_crit = 0.001

print('+++Testrun+++')

def backup(restore=False):
    '''
    Backups or restores const and conf files in current directory
    
    Input:
        restore - bool, restores a .bak file if true, creates a backup else
        
    Output:
        None
    '''
    
    if restore:
        asuff = '.bak'
        bsuff = ''
    elif not restore:
        asuff = ''
        bsuff = '.bak'
    else:
        return(None)
    for file in files:
        
        astring = cwd + '/' + file + asuff
        bstring = cwd + '/' + file + bsuff
        if restore:
            shutil.move(astring, bstring)
        elif not restore:
            shutil.copy(astring, bstring)
        else:
            return(None)
            
    return(None)

#copy conf.py and const.py over into the main (current) directory. Backup the
#conf and const files first.
backup()

#copy test conf and const into main directory
for file in files:
    shutil.copy(cwd + '/testdata/' + file, cwd + '/' + file)
    
#link testfiles into the 'in/' directory
for file in test_files:
    try:
        os.link(cwd + '/testdata/' + file, cwd + '/in/' + file)
    except:
        sys.exit('Please remove input files from input directory first to ' + 
                 'run the test! Exiting...')
    
testvar = eval(open(cwd + '/testdata/' + 'testvar.py', 'r').read())

print('Read in Testdata.')

import main #import and run testdata

print('')
for var in seq:
    mean = np.mean(main.data[var])
    std = np.std(main.data[var])
    diff = [abs(testvar[var + '_m'] - mean), abs(testvar[var + '_s'] - std)]
    print('Differences for variable ' + var +
          ' (mean and std): %.5f, %.5f' % (diff[0], diff[1]))
    print('Mean and std for reference data: ' +
          str(testvar[var + '_m']) + ', ' + str(testvar[var + '_s']))
    for k in diff:
        if k <= diff_crit:
            print(u'\u001b[32;1m' + 'Passed!' + '\u001b[0m')
        else:
            print(u'\u001b[31;1m' + 'Failed!' + '\u001b[0m')

backup(restore=True) #restore backuped files

print('Difference criterion: ' + str(diff_crit))
print('Reference and installed pandas version: ' + testvar['pd_v'] +
      ' | ' + pd.__version__)
print('Reference and installed numpy version:  ' + testvar['np_v'] +
      ' | ' + np.__version__)

#remove linked files
for file in test_files:
    os.remove(cwd + '/in/' + file)

print('Done!')
