#!/usr/bin/env

import RPi.GPIO as GPIO
import gpiozero

from datetime import datetime
import logging
import time

# pin numbers 
BLUE      = 26
GREEN     = 19
RED       = 13
TRIG      = 21
ECHO      = 16
MONITOR   = 5

# nice color, had to experiment to find a nice one
NICE_PINK = (221, 0, 86)


class RGBLED:
    
    """ Simple (perhaps useless) wrapper for the RGB LEDS.
        The leds are common anode so everything must be reversed """

    def __init__(self, red_pin, green_pin, blue_pin):
        #self.red = gpiozero.PWMLED(red_pin, frequency=80, initial_value=1)
        #self.green = gpiozero.PWMLED(green_pin, frequency=80, initial_value=1)
        #self.blue = gpiozero.PWMLED(blue_pin, frequency=80, initial_value=1)
        
        """ unfortunately the PWM on the rpi can't be stable enough
            so it flickers too much. That's why I use digital IO instead """
        self.red = gpiozero.LED(red_pin)
        self.green = gpiozero.LED(green_pin)
        self.blue = gpiozero.LED(blue_pin)
        self.leds = [self.red, self.green, self.blue]
        self.off()

    """ on/off are reversed since I'm using commong anode """
    def on(self):
        for led in self.leds:
            led.off()

    def off(self):
        for led in self.leds:
            led.on()

    """ maps the color from 0-255 -> 0-1 """
    def _color_value(self, color):
        if color:   # prevents division by zero
            return 1 - (color / 0xff)
        return 1

    def color(self, red, green, blue):
        self.red.value = self._color_value(red)
        self.green.value = self._color_value(green)
        self.blue.value = self._color_value(blue)
    
    def welcome_animation(self):
        for i in range(25):
            self.color(i*10, i*10, i*10)
            time.sleep(.3)

class Monitor:
        
    # time to wait before being able to turn the monitor
    # on or off again
    DEBOUNCE = 2

    def __init__(self, pin):
        self._pin = gpiozero.LED(pin)
        self._on = False

    def is_on(self):
        return self._on
    
    def turn_on(self):
        self._on = True
        self._toggle()

    def turn_off(self):
        self._on = False
        self._toggle()

    def _toggle(self):
        self._pin.on()
        time.sleep(.5)
        self._pin.off()
        time.sleep(self.DEBOUNCE)

class UsSensor:
    
    # this is the limits of detection (in cm)
    DETECT_RANGE = 10

    def __init__(self, trig, echo):
        self._trig = trig
        self._echo = echo
        
        GPIO.setup(self._trig, GPIO.OUT)
        GPIO.setup(self._echo, GPIO.IN)
    
    def get_distance(self):
        # performs two measuerements, sometimes we get 
        # noise that should be ignore
        measure1 = self._measure()
        measure2 = self._measure()

        return max(measure1, measure2)

    def _measure(self):

        GPIO.output(self._trig, True)
        time.sleep(0.00001)
        GPIO.output(self._trig, False)

        t1 = time.time()
        while not GPIO.input(self._echo) and time.time() - t1 < .5:
            pass

        if time.time() - t1 >= 1:
            return 1000

        t1 = time.time()
        while GPIO.input(self._echo) and time.time() - t1 < .5:
            pass
        
        t2 = time.time() - t1
        if t2 >= 1:
            return 1000

        # this magic just saves a little bit of calculations
        # returns in cm 
        return t2 * 17241


if __name__ == '__main__':

    led = RGBLED(RED, GREEN, BLUE)
    us_sensor = UsSensor(TRIG, ECHO)
    monitor = Monitor(MONITOR)
    led.on()

    while True:

        try:

            if us_sensor.get_distance() < us_sensor.DETECT_RANGE:

                _time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

                if not monitor.is_on():
                    led.on()
                    monitor.turn_on()
                    #led.welcome_animation()
                    #led.color(*NICE_PINK)
                    print(f'[{_time}] ON')

                else:
                    led.off()
                    monitor.turn_off()
                    print(f'[{_time}] OFF')

        except Exception as e:
            print(e)

    # us-sensor wants at least ~60 ms between readings
    time.sleep(.06)
