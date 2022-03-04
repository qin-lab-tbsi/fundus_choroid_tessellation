'''
author: bg
type: main 
ref: 
refactors: 
'''
from pathlib import Path 
from tessellator import choroid_segment
import logging 
from config import config  

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO) 
logger = logging.getLogger("Tessellator")

if __name__== "__main__":    
    ## i. config read
    in_dir = config.get( "input_dir","data")  
    ext = config.get("input_extension", "png") 
    tmethod = config.get('tess_method', "Tessellator") 
    img_resize = config.get("img_resize_to", 256) 
    img_resize = None if img_resize in ('',"None",None) else int(img_resize)  
    with_dehazing = config.getboolean('dehaze_input', False) 
    plot_results = config.getboolean('show_results', False) 
    
    ## ii. in dir setup 
    basedir = Path(__file__).parent.resolve()    
    fdir = basedir / in_dir      
    N = len( list(fdir.glob(f"*.{ext}")))
    fpathz = fdir.glob(f"*.{ext}") 
    logger.info(f"INCOMING: {N} files from {fdir.resolve() }")
    ## iii. run 
    #for tmethod in choroid_segment._TESSELLATORZ_REGISTRY.keys():    
    for i, fp in enumerate( fpathz, 1 ): 
        logger.info( f"[{tmethod}] START: {fp}" )
        f = choroid_segment.FundusImage( fp , 
                                        img_resize=img_resize,
                                        with_dehazing=with_dehazing, 
                                        tess_method=tmethod) 
        f.save_segmentations()
        if plot_results:
            f.show_segmentation() 
        logger.info( f"[{tmethod}] FINI {i}/{N}: {f.fname}.{ext} results saved to {f.output_dir.resolve()}" ) 