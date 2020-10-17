from utils import mqtt_wrapper
from .mqtt_source import MQTTSource


class DS18Source(MQTTSource):
    def __init__(self, client: mqtt_wrapper.MQTTClientWrapper, id=None):
        topic = f"temperature/ds18/{id}/value" if id else "temperature/ds18/+/value"
        super().__init__(client, topic)

    def transform(self, x):
        return float(x.payload)

