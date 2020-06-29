
# pin configs
V_OUT_PIN     = const(15)        # D8
MUX_PIN1      = const(14)        # D5
MUX_PIN2      = const(13)        # D7
DHT_PIN       = const(12)        # D6
SCL_PIN       = const(5)         # D1
SDA_PIN       = const(4)         # D2
ADC_PIN       = const(0)         # only available ADC pin on ESP8266
MAX_ATTEMPTS  = const(2)         # max attemptes to read sensor values
MAX_WIFI_WAIT = const(10)        # max time (in seconds) to wait for wifi after reading

# start by importing the help functions
from utils import *

# import rest of the necessary modules
from machine import ADC, I2C, Pin, RTC
import time

# initialize the pins (this will power up the sensors)
mux1, mux2 = init_pins(Pin, V_OUT_PIN, MUX_PIN1, MUX_PIN2)

# the temperature sensors 
from dht import DHT11
from mcp9808 import MCP9808

# create sensor objects, with the correct pins
fc28 = ADC(ADC_PIN)
dht  = DHT11(Pin(DHT_PIN))
mcp  = MCP9808(scl_pin=SCL_PIN, sda_pin=SDA_PIN)


# need to check we should read data and publish or if
# host wants to configure something
if run:

    # need to wait for the DHT11 to initialize
    time.sleep(1.5)

    attempts = 0
    result = None
    # sometimes reading the sensors throws an error (probably because
    # they're not ready yet.) This is usually fine because the wifi
    # establishment usually takes a while anyways
    while attempts < MAX_ATTEMPTS and result is None:
        try:
            # read the sensors 
            result = read_sensors(mux1, mux2, mcp, dht, fc28)
        except:
            attempts += 1

    if attempts != MAX_ATTEMPTS:

        t1 = time.time()
        # if we're not connected to the wifi yet, we wait max X seconds
        while not wlan.isconnected() and time.ticks_diff(time.time(), t1) < MAX_WIFI_WAIT:
            pass

        if wlan.isconnected():
            # publish the result to the MQTT-broker
            try:
                publish(MY_ID, SERVER, result)
                # need to wait a little bit before sleeping, otherwise
                # the data is sometimes not sent (not sure why)
                time.sleep(.2)
            except:
                # if we fail, there's probably something wrong with
                # the broker, we'll go straight back to sleep, no 
                # reason to try again
                pass

    go_sleep(SLEEP_TIME)


# if this is reached, we are NOT in sensor mode, but probably in repl
print('\n\n[* Temperature-humidity-and-moisture-sensor with ESP8266 *]\n\n')