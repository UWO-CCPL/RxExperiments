from paho.mqtt.client import MQTTMessage, MQTTv31

from source.mqtt_source import MQTTSource
from utils.mqtt_wrapper import MQTTClientWrapper

if __name__ == '__main__':
    client = MQTTClientWrapper("test_id", protocol=MQTTv31)
    client.connect("127.0.0.1")
    source = MQTTSource(client, "#")



    def fun(x: MQTTMessage):
        print(x.topic, x.payload)

    source.subscribe(
        fun
    )
    client.loop_forever()
