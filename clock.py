#!/usr/bin/python

import time
from rpi_ws281x import *
import argparse
import math

# LED strip configuration:
LED_COUNT_MINUTES = 60
LED_COUNT_HOURS = 36
LEDS_PER_HOUR = LED_COUNT_HOURS / 12

MINUTE_RANGE_BEGIN = 0
MINUTE_RANGE_END = MINUTE_RANGE_BEGIN + LED_COUNT_MINUTES

HOUR_RANGE_BEGIN = MINUTE_RANGE_END
HOUR_RANGE_END = HOUR_RANGE_BEGIN + LED_COUNT_HOURS

LED_COUNT      = LED_COUNT_MINUTES + LED_COUNT_HOURS
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
# 96 * 60 ma = 5760 ma. Halving brightness reduces that it 2880 ma.
LED_BRIGHTNESS = math.floor(255 / 2)     # Set to 0 for darkest and 255 for brightest
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


TIME_BLUE_COLOR = Color(125, 253, 254)
TIME_ORANGE_COLOR = Color(223, 116, 12)

class ClockTime:
    # hour in [0,23] and minute in [0, 59]
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute

def setAllPixels(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def powerOnTest(strip):
    # Show solid red, green, blue over 6 seconds.
    timeToShowColorSeconds = 2
    setAllPixels(strip, Color(255, 0, 0))
    time.sleep(timeToShowColorSeconds)
    setAllPixels(strip, Color(0, 255, 0))
    time.sleep(timeToShowColorSeconds)
    setAllPixels(strip, Color(0, 0, 255))
    time.sleep(timeToShowColorSeconds)

def convertHourLEDTo12Hour(hourLED):
    # Normalize range to 0 and divide by number of LEDs per hour then convert to 12 hour time
    return math.floor((hourLED - HOUR_RANGE_BEGIN) / LEDS_PER_HOUR) % 12

def updateStripToTime(strip, currentTime):
    # Blue on even hours, orange on odd hours
    minuteFillColor = TIME_BLUE_COLOR
    minuteDrainColor = TIME_ORANGE_COLOR
    hourFillColor = TIME_BLUE_COLOR
    hourDrainColor = TIME_ORANGE_COLOR

    # Swap for odd hours
    if (currentTime.hour % 2) == 1:
        tempColor = minuteFillColor
        minuteFillColor = minuteDrainColor
        minuteDrainColor = tempColor

    if (currentTime.hour > 11):
        tempColor = hourFillColor
        hourFillColor = hourDrainColor
        hourDrainColor = tempColor

    minute = 0
    for led in range(MINUTE_RANGE_BEGIN, MINUTE_RANGE_END):
        if minute <= currentTime.minute:
            strip.setPixelColor(led, minuteFillColor)
        else:
            strip.setPixelColor(led, minuteDrainColor)
        minute += 1
    
    for led in range(HOUR_RANGE_BEGIN, HOUR_RANGE_END):
        hourForLED = convertHourLEDTo12Hour(led)
        if hourForLED < (currentTime.hour % 12):
            strip.setPixelColor(led, hourFillColor)
        else:
            strip.setPixelColor(led, hourDrainColor)

    strip.show()

def updateStripForActualTime(strip):
    currentTime = time.localtime()
    updateStripToTime(strip, ClockTime(currentTime.tm_hour, currentTime.tm_min))

def showTimeTest(strip):
    for hour in range(0, 24):
        for minute in range(0, 60):
            updateStripToTime(strip, ClockTime(hour, minute))
            # 8 minutes per second which is 24 hours in 3 minutes
            time.sleep(0.125)

if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', action='store_true', help='run with time test loop')
    args = parser.parse_args()
 
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    # see https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/library/rpi_ws281x/rpi_ws281x.py
    # see https://tutorials-raspberrypi.com/connect-control-raspberry-pi-ws2812-rgb-led-strips/
    # see https://github.com/jgarff/rpi_ws281x

    try:
        powerOnTest(strip)

        while True:
            if args.test:
                showTimeTest(strip)
            else:
                updateStripForActualTime(strip)
                # Sleep tenth of a second.
                time.sleep(0.1)
    except KeyboardInterrupt:
        setAllPixels(strip, Color(0,0,0))