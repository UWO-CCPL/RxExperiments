import json

import rx
from paho.mqtt.client import MQTTMessage

from utils import mqtt_wrapper
from .mqtt_source import MQTTSource


class RamanSource(MQTTSource):
    def __init__(self, client: mqtt_wrapper.MQTTClientWrapper, topic_base: str="raman"):
        super().__init__(client, topic_base + "/data")
        self.wave_number = list(range(100, 3426))

    def transform(self, x):
        message: MQTTMessage = x
        return {
            "wave_number": self.wave_number,
            "data": json.loads(message.payload),
        }
