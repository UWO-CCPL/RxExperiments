import json

import rx
from paho.mqtt.client import MQTTMessage

from utils import mqtt_wrapper
from .mqtt_source import MQTTSource


class FBRMSource(MQTTSource):
    def __init__(self, client: mqtt_wrapper.MQTTClientWrapper, topic_base: str):
        super().__init__(client, topic_base + "/counts")
        self.sizes = None
        client.subscribe(topic_base + "/sizes")

        def save_sizes(x):
            self.sizes = json.loads(x[2].payload)
            self.logger.info("fbrm size loaded")

        rx.from_callback(client.message_callback_add)(topic_base + "/sizes").subscribe(save_sizes)

    def transform(self, x):
        message: MQTTMessage = x
        return {
            "sizes": self.sizes,
            "counts": json.loads(message.payload),
        }
