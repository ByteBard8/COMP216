import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes
from random import randint, choice
import time
import json

from group_2_data_generator import DataGenerator
from group_2_util import Util

datagenerator = DataGenerator(min_value=16, max_value=28)

util = Util()

#Publisher – Sending data to broker
BROKER = 'localhost'
PORT = 1883

def on_log(client, userdata, level, buf):
    print(client, userdata, level, buf)

def on_connect(client, userdata, flags, reason, properties):
    # print(client)
    # print(userdata)
    # print(flags)
    print(f'Connection Code: {reason}')
    # print(properties)

def on_publish(client, userdata, mid, reason, properties):
    print(f'Published Message {mid} -- Code: {reason}')
    # print(properties)

def on_disconnect(client, userdata, falgs, reason, properties):
    print(f'Disconnect Code: {reason}')
    client_pub.loop_stop()


con_properties = Properties(PacketTypes.CONNECT)
con_properties.SessionExpiryInterval = 30

publ_properties = Properties(PacketTypes.PUBLISH)
publ_properties.MessageExpiryInterval = 5

client_pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=str(randint(1, 100)),
                         protocol=mqtt.MQTTv5)

client_pub.on_log = on_log
client_pub.on_connect = on_connect
client_pub.on_publish = on_publish
client_pub.on_disconnect = on_disconnect

client_pub.connect(BROKER, PORT, properties=con_properties)

client_pub.loop_start()

counter = 0

#return randomly a list of garbase value denoting invalid tranmissions
#this signfies transmission error
def fn_return_garbage_value(data):
    return choice([0,-1,100])


#return 100 which is way out of range value but still follow the json structure
#this signifies an error in reading data from sensor
def fn_return_out_of_range_value(data):
    data["temperature"]["current"] = choice([100,0])
    return data

def fn_return_same(data):
    return data


while True:
    data = util.create_data(datagenerator)
    data_formatted = json.dumps(data)
    counter += 1    #to track number of transmissions
    if counter % 10 == 0:   #if x transmissions reached we invoke disruption
        my_list = [fn_return_out_of_range_value, fn_return_garbage_value, fn_return_same]   #define list of modifiers
        modified_data = choice(my_list)(data)   #choose a list of modifiers and pass our data
        data_formatted = json.dumps(modified_data)
    client_pub.publish('data/temp', data_formatted, properties=publ_properties, qos=2, retain=True) #publish valid data
    print(f'Publishing data: {data_formatted}')

    time.sleep(2)


client_pub.disconnect()
print('Publisher disconnect')


