'''
author: bg
type: extractor   
ref: 
refactors: 
'''
from pathlib import Path 
import cv2 
import numpy as np
from tessellator import imutils as IM 
from skimage import img_as_ubyte 
import skimage.feature as skfeats  #hessian,  
import matplotlib.pyplot as plt 
from datetime import datetime 

def log_info(msg):        
    pass 

_TESSELLATORZ_REGISTRY = dict() 
def register_tessellator(f):
    ''' register add '''
    _TESSELLATORZ_REGISTRY[ f.__name__ ] = f 
    log_info( f"Available methods: {_TESSELLATORZ_REGISTRY}" ) 
    return f 

@register_tessellator 
class Tessellator:
    brightz = lambda x, t: img_as_ubyte( ( (x-x.min())/(x.max()-x.min() + 1e-16) ) >= t ) 
    def __call__(self, img, *argz, **kwargz):
        with_dehazing = kwargz.get('with_dehazing', True ) 
        im = IM.preclean_image( img , dehaze=with_dehazing)          
        ## i. separate red and green 
        r = np.copy( im[:,:,0])
        g = np.copy( im[:,:,1])         
        ## ii. preprocess red 
        r = self.devessel_and_debrights_red(r, g)         
        ## iii. segment choroidal tubulars 
        o = self.choroid_segment( r )   
        ## iv. output update        
        oc =  cv2.subtract(o, r) 
        oc[ oc >= 250 ] = 0
        oc[ oc <= 30 ] = 0 
        oc = oc*255      
        return o , oc 
    
    def devessel_and_debrights_red( self, r, g, bS=11, mnT=7, brightz_thresh=.2):
        ## i. devessel 
        gt = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, bS, mnT) 
        rgt = r #np.copy(r)  
        rgt = cv2.inpaint(rgt, cv2.bitwise_not(gt) , 3, cv2.INPAINT_TELEA)  
        ## ii. debright
        rt = Tessellator.brightz( r , brightz_thresh )
        rgt[ rgt >= rt ] = np.max( rgt )
        rgt = cv2.bitwise_and(rgt, rgt, mask=rt)
        rgt = cv2.GaussianBlur(rgt, (3,3), 0)
        return IM.range_norm( rgt  ) 
    
    def choroid_segment(self, r):
        ''' default method is intensity thresholding-based '''
        crt = r #np.copy( r )         
        crt = cv2.adaptiveThreshold(crt, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 13, 2)         
        ## clean up 
        kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3) ) 
        crt = cv2.erode( crt, kern, iterations=1) 
        crt = cv2.dilate( crt, kern, iterations=1) 
        return crt 
        
@register_tessellator 
class HessianTessellator(Tessellator):      
    def __init__(self, sigmaz=(.1,7.7,.5), h_thresh=0.0099): #(3.3,4.7,.5)
        super().__init__()
        self.sigmaz = sigmaz   
        self.h_thresh = h_thresh  #9 0.0099 #np.percentile(l1, 1) #0.001  last working = .0001 before dehazor 
        
    def choroid_segment(self, r):
        ''' alternate approach using edge detection - TODO: finetune '''
        h_ = [] 
        for s in np.arange( *self.sigmaz ):
            H_ = skfeats.hessian_matrix( r, s ) 
            l1, l2 = skfeats.hessian_matrix_eigvals(H_)             
            l1[ l1 <= self.h_thresh ] = 0
            #t = np.max(l1) #np.percentile(l1, 90)
            #l1[ l1 >= t ] = 0
            h_.append( l1 ) 

        o = IM.range_norm( np.sum( h_, axis=0 ) ) 
        o = cv2.threshold( IM.range_norm(o), 0, 255, cv2.THRESH_BINARY_INV)[1] 
        o = cv2.dilate( o, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3) ), iterations=2) 
        o = cv2.erode( o, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2) ), iterations=1) 
        return o 
        
        
def segment_choroid_tubulars(img, method, method_kwargz=None):
    method_kwargz = {} if method_kwargz is None else method_kwargz
    extractor = _TESSELLATORZ_REGISTRY[method]( ) 
    return extractor( img , **method_kwargz ) 


class FundusImage:
    
    output_titlez = ['binary', 'output']
    
    def __init__(self, fdata, 
                 img_resize=None,
                 with_dehazing=True, 
                 tess_method=None):
        mz = list(_TESSELLATORZ_REGISTRY.keys())
        assert tess_method in [None,]+mz, \
                    f"Your input: {tess_method}. Valid tessellation methods = {mz} "
        self.tess_method = "Tessellator" if tess_method is None else tess_method 
        self.imdata, self.fname = (fdata, self.gen_name() ) if isinstance(fdata, (np.ndarray,) ) \
                                    else (IM.load_image(fdata,resize=img_resize) ,Path(fdata).stem )        
        self.with_dehazing = with_dehazing 
        
        self._seg_resultz = None 
        self._out_dir = None 
        
    def gen_name(self):
        t = datetime.now() 
        return f"xcvd_{t}"
    
    @property 
    def output_dir(self):
        if self._out_dir is None: 
            o = Path(__file__).parent.resolve() / "../tessallation_output" / self.tess_method
            for so in self.output_titlez:  
                (o/so).mkdir( parents=True, exist_ok=True) 
            self._out_dir = o 
        return self._out_dir 
    
    @property 
    def choroid_tessellation(self):
        if self._seg_resultz is None:
            tess_method = "Tessellator" if self.tess_method is None else self.tess_method 
            method_kwargz = dict(
                with_dehazing=self.with_dehazing  
                )
            self._seg_resultz = segment_choroid_tubulars( self.imdata, tess_method, method_kwargz ) 
        return self._seg_resultz
    
    def save_segmentations(self):
        rez = self.choroid_tessellation   
        for t, im in zip( self.output_titlez, rez ):
            IM.save_image( self.output_dir/ t / f"{self.fname}.png" , im )  
            
    def show_segmentation(self):            
        titlez = ['input','binary','output']
        nc = 3 
        nr = 1 
        _, axz = plt.subplots( nr, nc, figsize=(4*nr, 4*nc))  
        axz = axz.flatten() 
        im = self.imdata 
        coo, cim = self.choroid_tessellation 
        for j, aim in enumerate([im, coo, cim]): 
            ax = axz[j] 
            ax.imshow( aim , cmap='gray') 
            ax.axis('off')
            ax.set_title( titlez[j]) 
                
        plt.tight_layout()
        plt.show()
        plt.clf();


# if __name__== "__main__":    
#     from pathlib import Path    
#     basedir = Path(__file__).parent.resolve()    
#     fdir = basedir / "../data" 
#     fpathz = list( fdir.glob("*.png") )  
    
#     for tmethod in _TESSELLATORZ_REGISTRY.keys():
#         for fp in fpathz:#[::-1]
#             log_info( f"START [{tmethod}]: {fp}" )
#             f = FundusImage( fp , tess_method=tmethod) 
#             f.save_segmentations()
#             f.show_segmentation() 
#             log_info( f"FINI [{tmethod}]: {f.fname}" )
