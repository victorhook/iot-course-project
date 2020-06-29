def init_pins(Pin, VCC_PIN, MUX_PIN1, MUX_PIN2):

    vcc = Pin(VCC_PIN, Pin.OUT)
    mux1 = Pin(MUX_PIN1, Pin.OUT)
    mux2 = Pin(MUX_PIN2, Pin.OUT)

    vcc(1)
    mux1(0)
    mux2(0)
    return vcc, mux1, mux2


def read_sensors(mux1, mux2, mcp, dht, fc28):

    measurements = [0, 0, 0, 0, 0]

    # 1st moisture sensor
    mux1(0)
    mux2(0)
    measurements[0] = fc28.read() >> 2

    # 2nd moisture sensor
    mux1(1)
    measurements[1] = fc28.read() >> 2
    
    # 3rd moisture sensor
    mux1(0)
    mux2(1)
    measurements[2] = fc28.read() >> 2

    dht.measure()
    measurements[3] = dht.humidity()
    measurements[4] = int((dht.temperature() + mcp.get_temp()) / 2)

    return measurements


def publish(client_id, server, result):

    from umqtt.simple import MQTTClient

    # unpack the result 
    basil, thyme, oregano, humidity, temp = result

    # connect to the MQTT-broker and publish the messages
    client = MQTTClient(client_id, server)
    client.connect()
    client.publish('sensors/plants', 
                    '{"basil":"%s", "thyme":"%s", "oregano":"%s"}' \
                    % (basil, thyme, oregano) )
    client.publish('sensors/weather', 
                    '{"temperature":"%s", "humidity":"%s"}' \
                    % (temp, humidity) )


def go_sleep(sleep_us):
    # with esp8266 we can use the esp module do handle the alarm for us
    # since this is written in the firmware, it runs faster than python
    import esp
    esp.deepsleep(sleep_us)

    """
    if you're not using esp8266, you can use the following to manually
    setup the alarm:

    import machine  
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)  
    rtc.alarm(rtc.ALARM0, sleep_time_ms)

    # go sleep
    #machine.deepsleep()
    """
