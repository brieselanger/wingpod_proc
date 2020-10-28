def barb_gen(path='/home/axel/Dropbox/Dokumente/studium/WeWi/5Loch/python/data/barbs/',maxi=200):
    """
    Generates a set of wind barbs which can be used in google earth
    Input:
        path - str, output path
        maxi - int, maximum wind barb in knots
    Output:
        None
    """

    for i in range(0,maxi+1,5):
        plt.get_cmap('brg_r')(255)
        rgb = plt.get_cmap('brg_r')((i*1.5/maxi*256-1)/256)
        
        farbe = '#%02x%02x%02x' % (int(rgb[0]*255),int(rgb[1]*255),
                                    int(rgb[2]*255))
        plt.barbs(0,i,color=farbe)
        plt.xlim(-0.02,0.02)
        plt.ylim(-0.02,0.02)
        plt.savefig(path + str(i) + '.png', dpi=200)
        plt.close()
    
    #os.system('./barb_converter.sh ' + path) #doesnt work properly for some
    #                                         #reason
    
    return(None)
