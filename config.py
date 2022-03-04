'''
author: bg
type: config 
ref: 
refactors: 
'''
import configparser 
import argparse 

SETTINGS = '''
    [defaults]
    img_resize_to = None
    input_dir = data
    input_extension = png
    tess_method = Tessellator
    show_results = True
    dehaze_input = True 
'''

config = configparser.ConfigParser()
config.read_string( SETTINGS ) 
config = config['defaults']
