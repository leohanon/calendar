#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import logging
import traceback

from PIL import Image, ImageDraw, ImageFont

PICDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
LIBDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(LIBDIR):
    sys.path.append(LIBDIR)
from waveshare_epd import epd4in2

logging.basicConfig(level=logging.DEBUG)

from PIL import Image, ImageDraw, ImageFont
import os
import pickle
import time

from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Create a Grayscale version of the image
def get_pixel(image, i,j):
    return image.getpixel((i,j))

def create_image(i, j):
    image = Image.new("RGB", (i, j), "white")
    return image

def convert_grayscale(image):
    # Get size
    width, height = image.size

    # Create new Image and a Pixel Map
    new = create_image(width, height)
    pixels = new.load()

    # Transform to grayscale
    for i in range(width):
        for j in range(height):
            pixel = get_pixel(image, i, j)

            red = pixel[0]
            green = pixel[1]
            blue = pixel[2]

            gray = (red * 0.299) + (green * 0.587) + (blue * 0.114)

            # Set Pixel in new image
            pixels[i, j] = (int(gray), int(gray), int(gray))

    # Return new image
    return new

import random
def get_pic():
    pics = os.listdir(os.path.join(PICDIR,'randos')

    im = Image.open(os.path.join(PICDIR,'randos',random.choice(pics))

    old_size = im.size
    width, height = old_size
    ratio = max(400/width, 300/height)

    new_size = tuple([int(x*ratio) for x in old_size])

    im = im.resize(new_size, Image.ANTIALIAS)

    new_im = Image.new("RGB", (400, 300))
    new_im.paste(im, ((400-new_size[0])//2,
                        (300-new_size[1])//2))

    new_im = convert_grayscale(new_im)

    return new_im

import datetime
from dateutil.parser import parse

def filter_events(events):
    BLOCKS = ['8','2']
    MY_EMAIL = 'leo@outschool.com'
    DECLINED_CODE = 'declined' 

    filtered = []
    for event in events:
        try:
            if event['colorId'] in BLOCKS:
                continue
        except:
            pass
        try:
            exit = False
            for attendee in event['attendees']:
                me = attendee['email'] == MY_EMAIL
                declined = attendee['responseStatus'] == DECLINED_CODE
                if me and declined:
                    exit = True
                    break
            if exit:
                continue
        except:
            pass
        filtered.append(event)
    return filtered

MAX_CUTOFF = 8 * 60 * 60
MIN_CUTOFF = -15 * 60
DATE_NOW = datetime.datetime.now().astimezone()

def stringify_secs(time_secs):
    string = ''
    if time_secs < 0:
        string = '-'
    if abs(time_secs) > 3600:
        string += f'{abs(time_secs) // 3600} hr '
    string += f'{(abs(time_secs) % 3600) // 60} min'
    return string

PADDING = 15
WIDTH = 400

FONT70 = ImageFont.truetype(os.path.join(PICDIR,'Font.ttc'), 70)
FONT25 = ImageFont.truetype(os.path.join(PICDIR,'Font.ttc'), 25)

def make_lines(string, font, lines = []):
    words = string.split(' ')
    for x in range(len(words)):
        pos = len(words) - x
        to_test = ' '.join(words[:pos])
        if font.getsize(to_test)[0] < WIDTH - (2*PADDING):
            lines.append(to_test)
            if pos != len(words):
                make_lines(' '.join(words[pos:]), font, lines)
            return lines

def cut_line(string, font):
    for x in range(len(string)):
        pos = len(string) - x
        to_test = string[:pos] + '...'
        if font.getsize(to_test)[0] < WIDTH - (2*PADDING):
            return to_test

def draw_text_wrap(drawing, text, start, font):
    height = font.getsize('0')[1] + 2
    lines = make_lines(text, font, [])
    for num, line in enumerate(lines):
        drawing.text((PADDING, start + height * num), line, font=font, fill=0)
        
def draw_text_cut(drawing, text, start, font):
    height = font.getsize('0')[1] + 2
    line = cut_line(text, font)
    drawing.text((PADDING, start), line, font=font, fill=0)

credentials = pickle.load(open("token.pkl", "rb"))
service = build('calendar', 'v3', credentials=credentials)

def refresh():
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=20, singleEvents=True,
                                        orderBy='startTime').execute()
    return filter_events(events_result['items'])

pic = get_pic()

def process_events(filtered):
    time_left = int((parse(filtered[0]['start']['dateTime']) - DATE_NOW).total_seconds())

    if time_left > MAX_CUTOFF:
        current = None
    elif time_left < MIN_CUTOFF:
        time_left = int((parse(filtered[1]['start']['dateTime']) - DATE_NOW).total_seconds())
        if time_left > MAX_CUTOFF:
            current = None
        else: 
            current = 1
    else:
        current = 0

    if current is not None:
        Himage = Image.new('1', (400, 300), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        time_left_str = stringify_secs(time_left)
        draw.text((15, 20), time_left_str, font = FONT70, fill = 0)

        cur_meeting_str = filtered[current]['summary']
        draw_text_wrap(draw, cur_meeting_str, 100, FONT25)

        next_up = filtered[current+1]["summary"]
        next_up_time = int((parse(filtered[current+1]['start']['dateTime']) - DATE_NOW).total_seconds())
        draw.text((15, 223), f'Next up: ({stringify_secs(next_up_time)})', font = FONT25, fill = 0)
        draw_text_cut(draw, next_up, 253, FONT25)
    else:
        Himage = pic.copy()
        draw = ImageDraw.Draw(Himage)
        
    return Himage

try:
    logging.info("epd4in2 Demo")
   
    epd = epd4in2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    
    #display 4Gra bmp
    old_image = Image.new('1', (400, 300), 255)
    while True:
        filtered = refresh()
        Himage = process_events(filtered)
        if Himage != old_image:
            epd.Clear()
            epd.display_4Gray(epd.getbuffer_4Gray(Himage))
            old_image = Himage
        time.sleep(60)

    epd.Clear()
    logging.info("Goto Sleep...")
    epd.sleep()
    time.sleep(3)
    epd.Dev_exit()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd4in2.epdconfig.module_exit()
    exit()