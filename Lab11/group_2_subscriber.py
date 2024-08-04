import paho.mqtt.client as mqtt
from random import randint
from datetime import datetime
import json

from group_2_util import Util
util = Util()

BROKER = 'localhost'
PORT = 1883


def on_log(client, userdata, level, buf):
    print(client, userdata, level, buf)

def on_connect(client, userdata, flags, reason, properties):
    print(f'Connection Code: {reason}')

def on_subscribe(client, userdata, mid, reason, properties):
    print(f'Subscribed Message {mid} -- Code: {reason}')

def on_message(client, userdata, msg):
    print(f'Message attributes: Topics {msg.topic}; QoS {msg.qos}; Retained {msg.retain}')
    message = msg.payload.decode("UTF-8")
    json_data = json.loads(message)
    util.print_data(json_data)


client_sub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=str(randint(101,200)),
                         protocol=mqtt.MQTTv5)

client_sub.on_log = on_log
client_sub.on_connect = on_connect
client_sub.on_subscribe = on_subscribe
client_sub.on_message = on_message


client_sub.connect(BROKER, PORT)
client_sub.subscribe('data/temp')

client_sub.loop_forever()