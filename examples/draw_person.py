#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import time
import traceback

from PIL import Image, ImageDraw, ImageFont

PICDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
LIBDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(LIBDIR):
    sys.path.append(LIBDIR)
from waveshare_epd import epd4in2



logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd4in2 Demo")
   
    epd = epd4in2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    
    #display 4Gra bmp
    Himage = Image.open(os.path.join(PICDIR, 'test.bmp'))
    epd.display_4Gray(epd.getbuffer_4Gray(Himage))
    time.sleep(4)
    
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