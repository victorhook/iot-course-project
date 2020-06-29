from settings import config
import binascii
import machine
import network

# connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(1)
wlan.connect(config['ssid'], config['passwd'])

run = True
# if it's a hard-reset, we probably want access to the repl
if machine.reset_cause() == machine.HARD_RESET:
    # we skip deepsleep
    run = False

# set some global variables
MY_ID      = config['client_id']
SERVER     = config['server']
SLEEP_TIME = config['sleep_time']

import gc
# do a garbage collection before we start sensors
gc.collect()