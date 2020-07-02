<h1> DIY wall-mounted dashboard with local full stack </h1>
In this proejct I've made a wall-mounted dashboard to monitor the weather and the moisture in my plants. The project works like following:

1.  **The sensor-node** consists of a ESP8266 NodeMcu running Micropython, connected to a MCP9808 temperature sensor, DHT11 temp/humidity sensor, and three FC28 mositure sensors. The ESP8266 has a wifi chip which allows for easy communication. The data is pushed to a MQTT-broker over wifi.
2. **Dashboard Monitor** consists of an old PC-screen with the aid of a Raspberry Pi W Zero. The RPI uses Grafana together with openbox and chromium to display the graph on the monitor. 
3. The **Backend** consists of mysql, Node-red and mosquitto. These programs allow a really nice way of working with the dataflow.

![monitor.jpg]()
