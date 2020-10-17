from paho.mqtt.client import MQTTMessage
from rx.disposable import Disposable
from utils.mqtt_wrapper import MQTTClientWrapper
from .base_control import BaseControl


class MQTTControlMessage:
    def __init__(self, message):
        self.message = message


class MQTTControl(BaseControl):
    """
    Publish incoming command to MQTT topic. Also, subscribe to that topic and retrieve data.
    """

    def __init__(self, client: MQTTClientWrapper, name: str, topic: str, qos=0, retain=False):
        self.client = client
        self.qos = qos
        self.topic = topic
        self.retain = retain
        super().__init__(name)

    def on_command(self, x):
        assert isinstance(x, MQTTControlMessage)
        self.client.publish(self.topic, x.message, self.qos, self.retain)
        self.update_subject.on_next(x)

    def on_subscribe(self, observer, scheduler=None):
        self.client.subscribe(self.topic, self.qos)

        def message_callback(client, userdata, message: MQTTMessage):
            observer.on_next(message)

        self.client.message_callback_add(self.topic, message_callback)

        def dispose():
            self.client.unsubscribe(self.topic)
            self.client.message_callback_remove(self.topic)

        return Disposable(dispose)
