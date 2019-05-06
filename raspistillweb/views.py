# raspistillWeb - web interface for raspistill
# Copyright (C) 2013 Tim Jungnickel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import exifread
import os
import threading
import tarfile
from time import strftime, localtime, asctime, mktime, sleep, time
from stat import ST_MTIME, ST_SIZE

from PIL import Image
from picamera import PiCamera

from sqlalchemy.exc import DBAPIError

import transaction

from .models import (
    DBSession,
    Picture,
    Settings,
    Timelapse,
    )


# Modify these lines to change the directory where the pictures and thumbnails
# are stored. Make sure that the directories exist and the user who runs this
# program has write access to the directories.
RASPISTILL_DIRECTORY = 'raspistillweb/pictures/' # Example: /home/pi/pics/
THUMBNAIL_DIRECTORY = 'raspistillweb/thumbnails/' # Example: /home/pi/thumbs/
TIMELAPSE_DIRECTORY = 'raspistillweb/time-lapse/' # Example: /home/pi/timelapse/

IMAGE_EFFECTS = [
    'none', 'negative', 'solarise', 'sketch', 'denoise', 'emboss', 'oilpaint',
    'hatch', 'gpen', 'pastel', 'watercolour', 'film', 'blur', 'saturation',
    'colourswap', 'washedout', 'posterise', 'colourpoint', 'colourbalance',
    'cartoon'
    ]

EXPOSURE_MODES = [
    'off', 'auto', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports',
    'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks'
    ]

AWB_MODES = [
    'off', 'auto', 'sun', 'cloud', 'shade', 'tungsten', 'fluorescent',
    'incandescent', 'flash', 'horizon'
    ]

ISO_OPTIONS = [
    'auto', '60', '100', '150', '200', '250', '300', '400', '500',
    '600', '700', '800'
    ]

IMAGE_RESOLUTIONS = [
    '800x600', '1024x786', '1900x1200', '1280x720', '1920x1080', '2593x1944',
    '3280x2464'
    ]

ENCODING_MODES = [
    'jpeg', 'png', 'bmp', 'gif'
    ]

TIMELAPSE_UNITS = [
    'ms', 's', 'min', 'h', 'd', 'w', 'm', 'y'
    ]

IMAGE_HEIGHT_ALERT = 'Please enter an image height between 0 and 2464 (or 1944 for the older v1 camera module).'
IMAGE_WIDTH_ALERT = 'Please enter an image width between 0 and 3280 (or 2592 for the older v1 camera module).'
IMAGE_EFFECT_ALERT = 'Please enter a valid image effect.'
EXPOSURE_MODE_ALERT = 'Please enter a valid exposure mode.'
ENCODING_MODE_ALERT = 'Please enter a valid encoding mode.'
AWB_MODE_ALERT = 'Please enter a valid awb mode.'
ISO_OPTION_ALERT = 'Please enter a valid ISO option.'
IMAGE_ROTATION_ALERT = 'Please enter a valid image rotation option.'
TIMELAPSE_TIME_INTERVAL_ALERT = 'Time-lapse interval needs to be smaller than total duration of time-lapse.'

THUMBNAIL_SIZE = 240, 160
THUMBNAIL_QUALITY = 80

TIME_CONVERSION_MILLI_SECONDS = {
    'ms': 1,
    's': 1000,
    'min': 60000,
    'h': 3600000,
    'd': 86400000,
    'w': 604800000,
    'y': 31536000000
}

timelapse = False
timelapse_database = None
percentage_completed = 0
starttime = 0

preferences_fail_alert = []
preferences_success_alert = False

# not implemented yet
image_quality = '100'
image_sharpness = '0'
image_contrast = '0'
image_brightness = '50'
image_saturation = '0'


###############################################################################
################################### Views #####################################
###############################################################################


# View for the /settings site
@view_config(route_name='settings', renderer='settings.mako')
def settings_view(request):
    app_settings = DBSession.query(Settings).first()
    global preferences_fail_alert, preferences_success_alert

    preferences_fail_alert_temp = []
    if preferences_fail_alert is not []:
        preferences_fail_alert_temp = preferences_fail_alert
        preferences_fail_alert = []

    preferences_success_alert_temp = False
    if preferences_success_alert:
        preferences_success_alert_temp = True
        preferences_success_alert = False

    return {'project' : 'raspistillWeb',
            'image_effects' : IMAGE_EFFECTS,
            'image_effect' : app_settings.image_effect,
            'exposure_mode' : app_settings.exposure_mode,
            'awb_mode' : app_settings.awb_mode,
            'encoding_modes' : ENCODING_MODES,
            'encoding_mode' : app_settings.encoding_mode,
            'exposure_modes' : EXPOSURE_MODES,
            'awb_modes' : AWB_MODES,
            'image_width' : str(app_settings.image_width),
            'image_height' : str(app_settings.image_height),
            'image_iso' : app_settings.image_ISO,
            'iso_options' :  ISO_OPTIONS,
            'timelapse_units': TIMELAPSE_UNITS,
            'timelapse_interval' : str(app_settings.timelapse_interval),
            'timelapse_interval_unit' : str(app_settings.timelapse_interval_unit),
            'timelapse_time' : str(app_settings.timelapse_time),
            'timelapse_time_unit' : str(app_settings.timelapse_time_unit),
            'preferences_fail_alert' : preferences_fail_alert_temp,
            'preferences_success_alert' : preferences_success_alert_temp,
            'image_rotation' : app_settings.image_rotation,
            'image_resolutions' : IMAGE_RESOLUTIONS
            }

# View for the /archive site
@view_config(route_name='archive', renderer='archive.mako')
def archive_view(request):

    pictures = DBSession.query(Picture).all()
    picturedb = []
    for picture in pictures:
        imagedata = get_picture_data(picture)
        picturedb.insert(0,imagedata)
    return {'project' : 'raspistillWeb',
            'database' : picturedb
            }

# View for the / site
@view_config(route_name='home', renderer='home.mako')
def home_view(request):
    pictures = DBSession.query(Picture).all()
    if len(pictures) == 0:
        return HTTPFound(location='/photo')
    else:
        picture_data = get_picture_data(pictures[-1])
        if timelapse:
            return {'project': 'raspistillWeb',
                    'imagedata' : picture_data,
                    'timelapse' : timelapse,
                    }
        #elif (mktime(localtime()) - mktime(picture_data['timestamp'])) > 1800:
        #    return HTTPFound(location='/photo')
        else:
            return {'project': 'raspistillWeb',
                    'imagedata' : picture_data,
                    'timelapse' : timelapse,
                    }

# View for the /timelapse site
@view_config(route_name='timelapse', renderer='timelapse.mako')
def timelapse_view(request):
    global timelapse_database

    #if timelapse_database is not None:
    #    DBSession.add(timelapse_database)
    #    timelapse_database = None

    app_settings = DBSession.query(Settings).first()
    timelapse_collection = DBSession.query(Timelapse).all()
    timelapsedb = []
    for timelapse_rec in timelapse_collection:
        timelapse_data = get_timelapse_data(timelapse_rec)
        timelapsedb.insert(0,timelapse_data)

    return {'project': 'raspistillWeb',
            'timelapse': timelapse,
            'timelapseUnits': TIMELAPSE_UNITS,
            'timelapseInterval': str(app_settings.timelapse_interval),
            'timelapseIntervalUnit': str(app_settings.timelapse_interval_unit),
            'timelapseTime': str(app_settings.timelapse_time),
            'timelapseTimeUnit': str(app_settings.timelapse_time_unit),
            'timelapseDatabase': timelapsedb,
            'percentage_completed': percentage_completed
            }

# View for the timelapse start - no site will be generated
@view_config(route_name='timelapse_start')
def timelapse_start_view(request):
    global timelapse

    app_settings = DBSession.query(Settings).first()

    timelapse_interval_temp = request.params['timelapseInterval']
    timelapse_interval_unit_temp = request.params['timelapseIntervalUnit']
    timelapse_time_temp = request.params['timelapseTime']
    timelapse_time_unit_temp = request.params['timelapseTimeUnit']

    if timelapse_interval_unit_temp and timelapse_interval_temp and timelapse_time_unit_temp and timelapse_time_temp:

        timelapse_interval_ms = convert_to_milli_seconds(timelapse_interval_temp, timelapse_interval_unit_temp)
        timelapse_time_ms = convert_to_milli_seconds(timelapse_time_temp, timelapse_time_unit_temp)

        if timelapse_interval_ms < timelapse_time_ms:
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
            app_settings.timelapse_interval = timelapse_interval_temp
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_time = timelapse_time_temp
        else:
            preferences_fail_alert.append(TIMELAPSE_TIME_INTERVAL_ALERT)
    elif timelapse_interval_unit_temp and timelapse_time_unit_temp:
        if timelapse_interval_unit_temp == 's' and timelapse_time_unit_temp not in ['ms']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'min' and timelapse_time_unit_temp not in ['ms', 's']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'h' and timelapse_time_unit_temp not in ['ms', 's', 'min']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'd' and timelapse_time_unit_temp not in ['ms', 's', 'min', 'h']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'w' and timelapse_time_unit_temp not in ['ms', 's', 'min', 'h', 'd']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'm' and timelapse_time_unit_temp not in ['ms', 's', 'min', 'h', 'd', 'w']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'y' and timelapse_time_unit_temp not in ['ms', 's', 'min', 'h', 'd', 'w', 'm']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        else:
            preferences_fail_alert.append(TIMELAPSE_TIME_INTERVAL_ALERT)


    DBSession.flush()

    timelapse = True
    filename = strftime("%Y-%m-%d.%H.%M.%S", localtime())
    t = threading.Thread(target=take_timelapse, args=(filename, ))
    t.start()
    return HTTPFound(location='/timelapse')


# View to take a photo - no site will be generated
@view_config(route_name='photo')
def photo_view(request):
    if timelapse:
        return HTTPFound(location='/')
    else:
        app_settings = DBSession.query(Settings).first()
        basename = strftime("%Y-%m-%d.%H.%M.%S", localtime())
        filename = '{}.{}'.format(basename, app_settings.encoding_mode)
        take_photo(filename)
        exif = None

        if app_settings.encoding_mode == 'jpg':
            f = open(RASPISTILL_DIRECTORY + filename, 'rb')
            exif = extract_exif(exifread.process_file(f))

        filedata = extract_filedata(os.stat(RASPISTILL_DIRECTORY + filename))
        if exif is not None:
            filedata.update(exif)
        else:
            # populate from settings if exif is unavailable
            filedata['ISO'] = str(app_settings.image_ISO)
            filedata['resolution'] = '{} x {}'.format(app_settings.image_width, app_settings.image_height)
            filedata['exposure_time'] = None

        filedata['filename'] = filename
        filedata['image_effect'] = app_settings.image_effect
        filedata['exposure_mode'] = app_settings.exposure_mode
        filedata['encoding_mode'] = app_settings.encoding_mode
        filedata['awb_mode'] = app_settings.awb_mode

        '''
        imagedata = dict()
        imagedata['filename'] = filename
        imagedata['image_effect'] = 'test'
        imagedata['exposure_mode'] = 'test'
        imagedata['awb_mode'] = 'test'
        imagedata['resolution'] = '800x600'
        imagedata['ISO'] = '300'
        imagedata['exposure_time'] = '100'
        imagedata['date'] = 'test'
        imagedata['timestamp'] = localtime()
        imagedata['filesize'] = 100
        '''
        picture = Picture(filename=filedata['filename'],
                        image_effect=filedata['image_effect'],
                        exposure_mode=filedata['exposure_mode'],
                        awb_mode=filedata['awb_mode'],
                        encoding_mode=filedata['encoding_mode'],
                        resolution=filedata['resolution'],
                        ISO=filedata['ISO'],
                        exposure_time=filedata['exposure_time'],
                        date=filedata['date'],
                        timestamp=time(),
                        filesize=filedata['filesize'])
        DBSession.add(picture)
        return HTTPFound(location='/')

# View for the archive delete - no site will be generated
@view_config(route_name='delete_picture')
def pic_delete_view(request):
    p_id = request.params['id']
    pic = DBSession.query(Picture).filter_by(id=int(p_id)).first()
    DBSession.delete(pic)
    return HTTPFound(location='/archive')

# View for the timelapse delete - no site will be generated
@view_config(route_name='delete_timelapse')
def tl_delete_view(request):
    t_id = request.params['id']
    tl = DBSession.query(Timelapse).filter_by(id=int(t_id)).first()
    DBSession.delete(tl)
    return HTTPFound(location='/timelapse')

# View for settings form data - no site will be generated
@view_config(route_name='save')
def save_view(request):

    global preferences_success_alert, preferences_fail_alert

    image_width_temp = request.params['imageWidth']
    image_height_temp = request.params['imageHeight']
    timelapse_interval_temp = request.params['timelapseInterval']
    timelapse_interval_unit_temp = request.params['timelapseIntervalUnit']
    timelapse_time_temp = request.params['timelapseTime']
    timelapse_time_unit_temp = request.params['timelapseTimeUnit']
    exposure_mode_temp = request.params['exposureMode']
    image_effect_temp = request.params['imageEffect']
    awb_mode_temp = request.params['awbMode']
    image_ISO_temp = request.params['isoOption']
    image_rotation_temp = request.params['imageRotation']
    image_resolution = request.params['imageResolution']
    encoding_mode_temp = request.params['encodingMode']

    app_settings = DBSession.query(Settings).first()

    if image_width_temp:
        if 0 < int(image_width_temp) <= 3280:
            app_settings.image_width = image_width_temp
        else:
            preferences_fail_alert.append(IMAGE_WIDTH_ALERT)

    if image_height_temp:
        if 0 < int(image_height_temp) <= 2464:
            app_settings.image_height = image_height_temp
        else:
            preferences_fail_alert.append(IMAGE_HEIGHT_ALERT)

    if not image_width_temp and not image_height_temp:
        app_settings.image_width = image_resolution.split('x')[0]
        app_settings.image_height = image_resolution.split('x')[1]

    if timelapse_interval_unit_temp and timelapse_interval_temp and timelapse_time_unit_temp and timelapse_time_temp:

        timelapse_interval_ms = convert_to_milli_seconds(timelapse_interval_temp, timelapse_interval_unit_temp)
        timelapse_time_ms = convert_to_milli_seconds(timelapse_time_temp, timelapse_time_unit_temp)

        if timelapse_interval_ms < timelapse_time_ms:
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
            app_settings.timelapse_interval = timelapse_interval_temp
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_time = timelapse_time_temp
        else:
            preferences_fail_alert.append(TIMELAPSE_TIME_INTERVAL_ALERT)
    elif timelapse_interval_unit_temp and timelapse_time_unit_temp:
        if timelapse_interval_unit_temp == 's' and timelapse_time_unit_temp not in ['ms']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'min' and timelapse_time_unit_temp not in ['ms', 's']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'h' and timelapse_time_unit_temp not in ['ms', 's', 'min']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'd' and timelapse_time_unit_temp not in ['ms', 's', 'min', 'h']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'w' and timelapse_time_unit_temp not in ['ms', 's', 'min', 'h', 'd']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'm' and timelapse_time_unit_temp not in ['ms', 's', 'min', 'h', 'd', 'w']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        elif timelapse_interval_unit_temp == 'y' and timelapse_time_unit_temp not in ['ms', 's', 'min', 'h', 'd', 'w', 'm']:
            app_settings.timelapse_time_unit = timelapse_time_unit_temp
            app_settings.timelapse_interval_unit = timelapse_interval_unit_temp
        else:
            preferences_fail_alert.append(TIMELAPSE_TIME_INTERVAL_ALERT)


    if exposure_mode_temp and exposure_mode_temp in EXPOSURE_MODES:
        app_settings.exposure_mode = exposure_mode_temp
    else:
        preferences_fail_alert.append(EXPOSURE_MODE_ALERT)

    if image_effect_temp and image_effect_temp in IMAGE_EFFECTS:
        app_settings.image_effect = image_effect_temp
    else:
        preferences_fail_alert.append(IMAGE_EFFECT_ALERT)

    if awb_mode_temp and awb_mode_temp in AWB_MODES:
        app_settings.awb_mode = awb_mode_temp
    else:
        preferences_fail_alert.append(AWB_MODE_ALERT)

    if image_ISO_temp and image_ISO_temp in ISO_OPTIONS:
        app_settings.image_ISO = image_ISO_temp
    else:
        preferences_fail_alert.append(ISO_OPTION_ALERT)

    if image_rotation_temp and image_rotation_temp in ['0','90','180','270']:
        app_settings.image_rotation = image_rotation_temp
    else:
        preferences_fail_alert.append(IMAGE_ROTATION_ALERT)

    if encoding_mode_temp and encoding_mode_temp in ENCODING_MODES:
        app_settings.encoding_mode = encoding_mode_temp
    else:
        preferences_fail_alert.append(ENCODING_MODE_ALERT)

    if preferences_fail_alert == []:
        preferences_success_alert = True

    DBSession.flush()
    return HTTPFound(location='/settings')

@view_config(route_name='progress_json', renderer='json')
def progress_view(request):
    return {'progress': percentage()}


###############################################################################
############ Helper functions to keep the code clean ##########################
###############################################################################
def setup_camera():
    app_settings = DBSession.query(Settings).first()

    sensor_warmup_time = 4
    # sensor_warmup_time = app_settings.sensor_warmup_time

    # set up camera according to settings
    camera = PiCamera(resolution=(app_settings.image_width, app_settings.image_height))
    camera.exposure_mode = app_settings.exposure_mode
    camera.awb_mode = app_settings.awb_mode
    camera.image_effect = app_settings.image_effect
    camera.rotation = app_settings.image_rotation

    # set iso if appropriate
    if str(app_settings.image_ISO) != 'auto':
        camera.iso = int(app_settings.image_ISO)

    camera.start_preview()
    # warm_up_sensor
    sleep(sensor_warmup_time)

    return camera


def take_photo(filename):
    app_settings = DBSession.query(Settings).first()

    if app_settings.encoding_mode == 'jpg':
        image_format = 'jpeg'
    else:
        image_format = app_settings.encoding_mode

    camera = setup_camera()
    camera.capture('{}/{}'.format(RASPISTILL_DIRECTORY, filename), format=image_format)
    generate_thumbnail(filename)

    camera.close()
    return


def take_timelapse(filename, consistent_images=True):
    global timelapse, timelapse_database, starttime, percentage_completed

    app_settings = DBSession.query(Settings).first()
    timelapsedata = {'filename':  filename}
    timelapsedata['timeStart'] = str(asctime(localtime()))
    os.makedirs(TIMELAPSE_DIRECTORY + filename)

    timelapse_interval_ms = convert_to_milli_seconds(app_settings.timelapse_interval, app_settings.timelapse_interval_unit)
    timelapse_time_ms = convert_to_milli_seconds(app_settings.timelapse_time, app_settings.timelapse_time_unit)

    camera = setup_camera()

    try:
        print('Starting time-lapse acquisition...')

        if consistent_images:
            camera.shutter_speed = camera.exposure_speed
            camera.exposure_mode = 'off'
            gains = camera.awb_gains
            camera.awb_mode = 'off'
            camera.awb_gains = gains

        if app_settings.encoding_mode == 'jpg':
            image_format = 'jpeg'
        else:
            image_format = app_settings.encoding_mode

        # For 'time lapse in progress' bar
        starttime = time()
        d = threading.Thread(target=percentage)
        d.start()

        stop_at = round(timelapse_time_ms/timelapse_interval_ms)

        file_data = {'tl_dir': TIMELAPSE_DIRECTORY,
                     'fn': filename,
                     'counter': '{counter:04d}',
                     'image_format': str(app_settings.encoding_mode)}
        base_filename = '{tl_dir}/{fn}/IMG_{fn}_{counter}.{image_format}'.format(**file_data)

        for i, image_filename in enumerate(camera.capture_continuous(base_filename, format=image_format)):
            if i == stop_at:
                break
            sleep(timelapse_interval_ms/1000)  # wait

        camera.close()
        print('Finished time-lapse acquisition.')
    except:
        raise

    timelapsedata['n_images'] = str(len([name for name in os.listdir(TIMELAPSE_DIRECTORY + filename) if os.path.isfile(os.path.join(TIMELAPSE_DIRECTORY + filename, name))]))
    timelapsedata['resolution'] = str(app_settings.image_width) + ' x ' + str(app_settings.image_height)
    timelapsedata['image_effect'] = app_settings.image_effect
    timelapsedata['exposure_mode'] = app_settings.exposure_mode
    timelapsedata['encoding_mode'] = app_settings.encoding_mode
    timelapsedata['awb_mode'] = app_settings.awb_mode
    timelapsedata['timeEnd'] = str(asctime(localtime()))

    timelapse_data = Timelapse(
                        filename = timelapsedata['filename'],
                        timeStart = timelapsedata['timeStart'],
                        n_images = timelapsedata['n_images'],
                        resolution = timelapsedata['resolution'],
                        image_effect = timelapsedata['image_effect'],
                        exposure_mode = timelapsedata['exposure_mode'],
                        encoding_mode = timelapsedata['encoding_mode'],
                        awb_mode = timelapsedata['awb_mode'],
                        timeEnd = timelapsedata['timeEnd'],
                    )

    print('Adding timelapse to DB')
    DBSession.add(timelapse_data)
    #DBSession.flush()
    transaction.commit()
    print('Added timelapse to DB')
    with tarfile.open(TIMELAPSE_DIRECTORY + filename + '.tar.gz', "w:gz") as tar:
        tar.add(TIMELAPSE_DIRECTORY + filename, arcname=os.path.basename(TIMELAPSE_DIRECTORY + filename))

    #timelapse_database = timelapse_data
    timelapse = False
    percentage_completed = 0
    return

def generate_thumbnail(filename):
    basename = os.path.splitext(filename)[0]

    im = Image.open(RASPISTILL_DIRECTORY + filename)
    im.thumbnail(THUMBNAIL_SIZE)
    im.save(THUMBNAIL_DIRECTORY + basename + '.jpg', quality=THUMBNAIL_QUALITY, optimize=True, progressive=True)
    return

def extract_exif(tags):
    return {
        'resolution' : str(tags['Image ImageWidth'])
        + ' x ' + str(tags['Image ImageLength']),
        'ISO' : str(tags['EXIF ISOSpeedRatings']),
        'exposure_time' : str(tags['EXIF ExposureTime'])
            }

def extract_filedata(st):
    return {
        'date' : str(asctime(localtime(st[ST_MTIME]))),
        'timestamp' : localtime(),
        'filesize': str((st[ST_SIZE])/1000) + ' kB'
            }

def get_picture_data(picture):
    imagedata = dict()
    imagedata['id'] = str(picture.id)
    imagedata['filename'] = picture.filename
    imagedata['image_effect'] = picture.image_effect
    imagedata['exposure_mode'] = picture.exposure_mode
    imagedata['awb_mode'] = picture.awb_mode
    imagedata['resolution'] = picture.resolution
    imagedata['ISO'] = str(picture.ISO)
    imagedata['exposure_time'] = picture.exposure_time
    imagedata['date'] = str(picture.date)
    imagedata['timestamp'] = str(picture.timestamp)
    imagedata['filesize'] = str(picture.filesize)
    return imagedata

def get_timelapse_data(timelapse_rec):
    timelapse_data = dict()
    timelapse_data['id'] = str(timelapse_rec.id)
    timelapse_data['filename'] = timelapse_rec.filename
    timelapse_data['image_effect'] = timelapse_rec.image_effect
    timelapse_data['exposure_mode'] = timelapse_rec.exposure_mode
    timelapse_data['awb_mode'] = timelapse_rec.awb_mode
    timelapse_data['timeStart'] = str(timelapse_rec.timeStart)
    timelapse_data['timeEnd'] = str(timelapse_rec.timeEnd)
    timelapse_data['n_images'] = str(timelapse_rec.n_images)
    timelapse_data['resolution'] = timelapse_rec.resolution
    timelapse_data['encoding_mode'] = timelapse_rec.encoding_mode
    return timelapse_data

# For 'time lapse in progress' bar
def percentage():
    global timelapse, starttime, percentage_completed
    app_settings = DBSession.query(Settings).first()
    timelapse_time_ms = convert_to_milli_seconds(app_settings.timelapse_time, app_settings.timelapse_time_unit)
    while(timelapse and percentage_completed < 100):
        currenttime = time()
        percentage_completed = int(((currenttime - starttime) * 1000 / timelapse_time_ms) * 100)
        if (percentage_completed > 100):
            percentage_completed = 100
        sleep(1)
    return percentage_completed

def convert_to_milli_seconds(value, unit):
    if unit not in TIMELAPSE_UNITS:
        raise ValueError("Unknown unit")

    return value * TIME_CONVERSION_MILLI_SECONDS[unit]
