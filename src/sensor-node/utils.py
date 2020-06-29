""" since we're controlling the voltage to
    the sensors, we need to set it high before
    reading. We also need to initialize the pins
    to control the multiplexer """
def init_pins(Pin, VCC_PIN, MUX_PIN1, MUX_PIN2):

    v_out = Pin(VCC_PIN, Pin.OUT)
    mux1 = Pin(MUX_PIN1, Pin.OUT)
    mux2 = Pin(MUX_PIN2, Pin.OUT)

    v_out(1)
    mux1(0)
    mux2(0)
    return mux1, mux2


def read_sensors(mux1, mux2, mcp, dht, fc28):

    measurements = [0, 0, 0, 0, 0]

    # 1st moisture sensor
    mux1(0)
    mux2(0)
    measurements[0] = fc28.read()

    # 2nd moisture sensor
    mux1(1)
    measurements[1] = fc28.read()
    
    # 3rd moisture sensor
    mux1(0)
    mux2(1)
    measurements[2] = fc28.read()

    dht.measure()
    measurements[3] = dht.humidity()

    # take the mean temperature of the two readings.
    # not really interested in the decimals
    measurements[4] = int((dht.temperature() + mcp.get_temp()) / 2)

    return measurements


def publish(client_id, server, result):

    from umqtt.simple import MQTTClient

    # unpack the result 
    basil, thyme, oregano, humidity, temp = result

    # connect to the MQTT-broker and publish the messages
    client = MQTTClient(client_id, server)
    client.connect()

    # data format is JSON
    client.publish('sensors/plants', 
                    '{"basil":"%s", "thyme":"%s", "oregano":"%s"}' \
                    % (basil, thyme, oregano) )
    client.publish('sensors/weather', 
                    '{"temperature":"%s", "humidity":"%s"}' \
                    % (temp, humidity) )


def go_sleep(sleep_ms):
    import machine  

    rtc = machine.RTC()
    # set alarm for wakeup
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)  
    rtc.alarm(rtc.ALARM0, sleep_ms)

    # go sleep
    machine.deepsleep()
