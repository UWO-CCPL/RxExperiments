from paho.mqtt.client import MQTTMessage, MQTTv31
from utils.mqtt_wrapper import MQTTClientWrapper
from configs import config
from controls.mqtt_fp50 import MQTTFP50Control, FP50Command
if __name__ == '__main__':
    config.GlobalConfig.initialize_global_configuration()
    client = MQTTClientWrapper("test_id", protocol=MQTTv31)
    client.connect("192.168.43.1")
    fp50 = MQTTFP50Control(client)
    fp50.on_command(FP50Command(34))

    def output(x):
        print(x)
    fp50.subscribe(output)
    client.loop_forever()
