from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import time
import exifread
import os
from subprocess import call
from time import gmtime, strftime
from stat import *

RASPISTILL_DIRECTORY = 'raspistillweb/pictures/'

IMAGE_EFFECTS  = ['none','negative','solarise','sketch','denoise','emboss',
    'oilpaint','hatch','gpen','pastel','watercolour','film','blur','saturation',
    'colourswap','washedout','posterise','colourpoint','colourbalance','cartoon']

EXPOSURE_MODES = ['off','auto','night','nightpreview','backlight','spotlight',
    'sports','snow','beach','verylong','fixedfps','antishake','fireworks']
    
AWB_MODES = ['off','auto','sun','cloud','shade','tungsten','fluorescent',
    'incandescent','flash','horizon']

# image parameter commands
image_width = 800
image_height = 600
image_effect = 'none'
exposure_mode = 'off'
awb_mode = 'off'
preferences_success_alert = False
preferences_fail_alert = ""

# not implemented yet
image_quality = '100'
image_sharpness = '0'
image_contrast = '0'
image_brightness = '50'
image_saturation = '0'
image_ISO = '300'

###############################################################################
################################### Views #####################################
###############################################################################


# View for the /settings site
@view_config(route_name='settings', renderer='settings.mako')
def settings_view(request):
    global preferences_success_alert, preferences_fail_alert
    
    preferences_success_alert_temp = False
    if preferences_success_alert:
        preferences_success_alert_temp = True
        preferences_success_alert = False
        
    preferences_fail_alert_temp = ""    
    if preferences_fail_alert:
        preferences_fail_alert_temp = preferences_fail_alert
        preferences_fail_alert = ""
        
    return {'project' : 'raspistillWeb',
            'image_effect' : image_effect,
            'exposure_mode' : exposure_mode,
            'awb_mode' : awb_mode,
            'image_effects' : IMAGE_EFFECTS,
            'exposure_modes' : EXPOSURE_MODES,
            'awb_modes' : AWB_MODES,
            'image_width' : image_width,
            'image_height' : image_height,
            'preferences_success_alert' : preferences_success_alert_temp,
            'preferences_fail_alert' : preferences_fail_alert_temp} 
                    
# View for the / site
@view_config(route_name='home', renderer='home.mako')
def home_view(request):
    filename = strftime("%Y-%m-%d.%H.%M.%S.jpg", gmtime())
    take_photo(filename)        
    f = open(RASPISTILL_DIRECTORY + filename,'rb')
    exif = extract_exif(exifread.process_file(f))    
    filedata = extract_filedata(os.stat(RASPISTILL_DIRECTORY + filename))       
    return {'project': 'raspistillWeb',
        'imagedata' : filedata + exif,
        'image_effect' : image_effect,
        'exposure_mode' : exposure_mode,
        'awb_mode' : awb_mode,
        'image_url' : 'pictures/'+filename}

# View for settings Form data - no site will be generated      
@view_config(route_name='save')
def save_view(request):
    global exposure_mode, image_effect, preferences_success_alert, image_width, image_height, preferences_fail_alert, awb_mode
    image_width_temp = request.params['imageWidth']
    image_height_temp = request.params['imageHeight']
    
    preferences_success_alert = True
    if image_width_temp:
        if 0 < int(image_width_temp) < 2500 :
            image_width = image_width_temp
        else:
            preferences_success_alert = False
            preferences_fail_alert += ' Please enter an image width between 0 and 2500. '
    
    if image_height_temp:
        if 0 < int(image_height_temp) < 1500 :
            image_height = image_height_temp
        else:
            preferences_success_alert = False
            preferences_fail_alert += ' Please enter an image width between 0 and 1500. '
    
    exposure_mode = request.params['exposureMode']
    image_effect = request.params['imageEffect']
    awb_mode = request.params['awbMode']
    return HTTPFound(location='/settings')  

###############################################################################
############ Helper functions to ceep the code clean ##########################
###############################################################################

def take_photo(filename):
    call (['raspistill -t 0'
        + ' -w ' + str(image_width)
        + ' -h ' + str(image_height)
        + ' -ex ' + exposure_mode
        + ' -awb ' + awb_mode
        + ' -ifx ' + image_effect 
        + ' -o ' + RASPISTILL_DIRECTORY + filename],shell=True)
    return

def extract_exif(tags):
    return [
        {'key' : 'Image Resolution', 'value' : str(tags['Image ImageWidth']) 
        + ' x ' + str(tags['Image ImageLength'])},
        {'key' : 'ISO', 'value' : str(tags['EXIF ISOSpeedRatings'])},
        {'key' : 'Exposure Time', 'value' : str(tags['EXIF ExposureTime'])}
        ]
    
def extract_filedata(st):
    return[
        {'key' : 'Date' , 'value' : str(time.asctime(time.localtime(st[ST_MTIME])))},
        {'key' : 'Filesize', 'value' : str((st[ST_SIZE])/1000) + ' kB'}
    ]    
