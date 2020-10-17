import json

import rx
from rx import operators
from rx.subject import Subject
from rx.scheduler import NewThreadScheduler

from utils.mqtt_wrapper import MQTTClientWrapper
from .base_control import BaseControl
from utils.observable_factory import from_callback
from .fp50 import FP50Command


class MQTTFP50Control(BaseControl):
    def __init__(self, client: MQTTClientWrapper, name="fp50", config=None):
        super().__init__(name, config=config)
        self.client = client

        self.topic_base = self.config["waterBath"][name]["topicBase"]
        self.topic = self.topic_base + "/setpoint"
        self.message_subject = Subject()

        self.client.subscribe(self.topic_base + "/crystallizer_temperature")
        self.client.subscribe(self.topic_base + "/setpoint")
        self.interval_scheduler = NewThreadScheduler()

        def update(x, scheduler=None):
            self.client.publish(self.topic_base + "/crystallizer_temperature", None)

        rx.interval(self.config["waterBath"][name]["interval"], self.interval_scheduler).subscribe(update)

        def convert(x):
            payloads = [xx[2].payload for xx in x]
            for p in payloads:
                if not p:
                    # skipping conversion request
                    return None

            return {
                # "power": float(payloads[0]),
                # "internal_temperature": float(payloads[1]),
                "crystallizer_temperature": float(payloads[0]),
                "setpoint": float(payloads[1]),
            }

        rx.combine_latest(
            from_callback(self.client.message_callback_add)(self.topic_base + "/crystallizer_temperature"),
            from_callback(self.client.message_callback_add)(self.topic_base + "/setpoint"),
        ).pipe(
            operators.map(convert),
            operators.filter(lambda x: x is not None),
            operators.debounce(0.6)
        ).subscribe(
            self.message_subject
        )

    def on_command(self, x):
        assert isinstance(x, FP50Command)
        self.client.publish(self.topic_base + "/setpoint", str(x.setpoint), retain=True)
        self.client.publish(self.topic_base + "/start", "1", retain=True)
        self.logger.debug(f"setpoint updated = {x.setpoint}")

    def on_subscribe(self, observer, scheduler=None):
        return self.message_subject.subscribe(observer, scheduler)
