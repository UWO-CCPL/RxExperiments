"""
RX enabled mqtt wrapper
"""

import paho.mqtt.client as mqtt
from rx import subject


class MQTTClientWrapper(mqtt.Client):
    def __init__(self, client_id="", clean_session=None, userdata=None, protocol=mqtt.MQTTv311, transport="tcp"):
        super().__init__(client_id, clean_session, userdata, protocol, transport)

        self.connected_subject = subject.BehaviorSubject(False)


    @property
    def on_connect(self):
        return lambda *args: self.connected_subject.on_next(True)

    @property
    def on_disconnect(self):
        return lambda *args: self.connected_subject.on_next(False)
