'''
author: bg
type: util  
ref: TODO: add dehazor reference 
refactors: 
''' 
import glob
import numpy as np

from skimage import img_as_ubyte 
import skimage.io as skio 
import skimage.transform as sktrans 

import cv2 

# from tessellator.haze.haze_removal import HazeRemoval 

_haze_remover = None 

def load_image( fpath, resize=None):
    im = skio.imread( fpath )
    if resize is not None:
        size = (resize,resize) if isinstance(resize, int) else resize 
        im = sktrans.resize( im, size, anti_aliasing = False)
    return im 

def save_image(fpath, im):
    skio.imsave( fpath, im )  

def range_norm(im):
    im = (im - im.min() )/( (im.max() - im.min() )+1e-16) 
    return img_as_ubyte( im )        

def dehazor(im):
    return im 
    ''' '''
    # global _haze_remover 
    # if _haze_remover is None:
    #     _haze_remover = HazeRemoval()         
    # return range_norm( _haze_remover.do_it_all( range_norm(np.copy(im)) ) )

cc_clahe = lambda x: cv2.createCLAHE(clipLimit=2.,tileGridSize=(8,8) ).apply( range_norm(x) )        
cc_blur = lambda x, b=3: cv2.medianBlur( range_norm(x), b) 
def preclean_image(im, dehaze=True, blur=False): 
    ## i. dehaze
    if dehaze:
        im = dehazor( im )     
    ## ii. clahe and medium blur if desired (clahe only suffices for the most part. Else a blur of 3 or 5)
    cc_cleaner = lambda x: cc_blur( cc_clahe( x) ) if blur else cc_clahe( x ) 
    im = cc_cleaner( im ) if len(im.shape)==2 \
                else np.dstack([ cc_cleaner(im[:,:,c]) for c in range(im.shape[2])])    
    return im 




# if __name__ == "__main__":
#     import matplotlib.pyplot as plt 
#     from pathlib import Path
    
#     basedir = Path(__file__).parent.resolve()    
#     fdir = basedir / "../data" 
#     fpathz = list( fdir.glob("*.*") )  
#     #print( fpathz)
    
#     nc = 2 
#     nr = len( fpathz )
#     _, axz = plt.subplots( nr, nc, figsize=(4*nr, 4*nc))  
#     axz = axz.flatten() 
#     for i, fp in enumerate( fpathz ):
#         print( ">>> Working : ", fp )
#         im = load_image( fp , resize=256) 
#         cim = preclean_image( im ) 
#         for j, aim in enumerate([im, cim]):
#             ax = axz[(i*nc)+j] 
#             ax.imshow( aim ) 
#             ax.axis('off')
            
#     plt.tight_layout()
#     plt.show()
    
    