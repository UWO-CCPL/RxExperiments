import rx.operators as ops
from rx.subject import Subject
from utils.mqtt_wrapper import MQTTClientWrapper
from sources.mqtt_source import MQTTSource


class MQTTDS18Source(MQTTSource):
    def __init__(self, client: MQTTClientWrapper, name="ds18", config=None):
        super().__init__(client, None, config=config, name=name)
        self.topic_base = self.config["ds18"]["topicBase"]
        self.topic = self.topic_base + "/temperature/+"
        self.can_subscribe.pipe(
            ops.take_while(lambda x: not x),  # while cannot subscribe, continue to take (should not happen)
        ).subscribe(lambda x: self.subscribe_on_broker(self.topic))
        self.sensors = self.config["ds18"]["sensors"]

    def transform(self, x):
        addr = str(x.topic).split("/")[-1]
        return {
            "name": self.sensors.get(addr, None),
            "addr": addr,
            "value": float(x.payload)
        }
