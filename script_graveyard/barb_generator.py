#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 12:35:08 2017

@author: axel
"""
maxi = 200

for i in range(0,maxi+1,5):
    plt.get_cmap('brg_r')(255)
    rgb = plt.get_cmap('brg_r')((i*1.5/maxi*256-1)/256)
    
    farbe = '#%02x%02x%02x' % (int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
    print(farbe)
    plt.barbs(0,i,color=farbe)
    plt.xlim(-0.02,0.02)
    plt.ylim(-0.02,0.02)
    plt.savefig('/home/axel/Dropbox/Dokumente/studium/WeWi/5Loch/flights/demmin/test/barb' + str(i) + '.pdf')
    plt.close()