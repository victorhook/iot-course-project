import ast
import paho.mqtt.client as mqtt
import mysql.connector
from datetime import datetime

"""
    This script uses MQTT to subscribe to several topics of interested
    on a given server. Once data is received it's stored into a MySql
    database, running on (in this case) the same server.

    The topics and database fields are hardcoded, but in the future
    this could be generalized, and use a config file so that you can
    simply add/delete/edit subscriptions and data-handling.

    This script is together with a starter script loaded into systemd,
    so it should run on boot and run as a daemon.

    author: Victor Krook
"""

class MySqlClient:

    def __init__(self):

        self.mysql = self._init_db()

    def _get_config(self):
        import json
        with open('config.json') as f:
            return json.load(f)


    """ creates a connection to the database and creates the
        tables if they don't already exists """
    def _init_db(self):
        config = self._get_config()

        _mysql = mysql.connector.connect(
            host = config['host'],
            user = config['user'],
            password = config['password'],
            database = config['database']
        )

        cursor = _mysql.cursor()

        # create tables if they don't already exist
        cursor.execute(f'CREATE TABLE IF NOT EXISTS weather (\
            time DATETIME, \
            temperature int, \
            humidity int)' )

        cursor.execute(f'CREATE TABLE IF NOT EXISTS plants (\
            time DATETIME, \
            basil int, \
            thyme int, \
            oregano int)')

        return _mysql


    def _get_date(self):
        return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')


    def save_data(self, table, data):
        cursor = self.mysql.cursor()
        date = self._get_date()
        print(f'{date}: Topic: {table} Data: {data}')

        # repack the data into a valid query
        columns, values = ', '.join(data.keys()), ', '.join(data.values())
        query = f'INSERT INTO {table} (time, {columns}) \
                VALUES ("{date}", {values})'

        # execute query and don't forget to commit!
        cursor.execute(query)
        self.mysql.commit()

    def close(self):
        self.mysql.cmd_quit()



class MqttClient:

    """ wrapper for paho's MQTT Client """

    def __init__(self, server):

        self._server = server

        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        self.mysql_client = MySqlClient()

    def __enter__(self):
        self.connect(self._server)
        return self

    def __exit__(self, *ignore):
        self.close()

    def close(self):
        self.mysql_client.close()
        self._client.disconnect()

    def connect(self, server, port=1883, keep_alive=60):
        self._client.connect(server, port, keep_alive)

    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("sensors/weather")
        client.subscribe("sensors/plants")


    # The callback for when a PUBLISH message is received from the server.
    def _on_message(self, client, userdata, msg):
        
        data = ast.literal_eval(msg.payload.decode('utf-8'))
        table = msg.topic.split('/')[1]

        self.mysql_client.save_data(table, data)

    def listen(self):
        self._client.loop_forever()


SERVER = '192.168.0.7'

if __name__ == "__main__":
    
    with MqttClient(SERVER) as client:
        client.listen()

        # we'll just listen forever ...