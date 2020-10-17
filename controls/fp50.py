import json

import rx
from rx import operators
from rx.subject import Subject

from utils.mqtt_wrapper import MQTTClientWrapper
from .base_control import BaseControl
from utils.observable_factory import from_callback

# TODO: do not output!
class FP50Command:
    def __init__(self, setpoint):
        self.setpoint = setpoint


class FP50Message:
    def __init__(self, power, temperature, setpoint):
        self.power = power
        self.temperature = temperature
        self.setpoint = setpoint

    def dict(self):
        return {
            "power": self.power,
            "temperature": self.temperature,
            "setpoint": self.setpoint,
        }


class FP50Control(BaseControl):
    def __init__(self, client: MQTTClientWrapper, name="fp50", config=None):
        super().__init__(name, config=config)
        self.client = client

        self.topic_base = self.config["waterBath"][name]["topicBase"]
        self.topic = self.topic_base + "/setpoint"
        self.message_subject = Subject()

        self.client.subscribe(self.topic_base + "/power")
        self.client.subscribe(self.topic_base + "/temperature")
        self.client.subscribe(self.topic_base + "/setpoint")

        power_sub = Subject()
        temp_sub = Subject()
        setpoint_sub = Subject()
        self.client.message_callback_add(self.topic_base + "/power", lambda *args: power_sub.on_next(args))
        self.client.message_callback_add(self.topic_base + "/temperature", lambda *args: temp_sub.on_next(args))
        self.client.message_callback_add(self.topic_base + "/setpoint", lambda *args: setpoint_sub.on_next(args))
        rx.combine_latest(
            power_sub,
            temp_sub,
            setpoint_sub
        ).pipe(
            operators.map(lambda x: FP50Message(
                float(x[0][2].payload),
                float(x[1][2].payload),
                float(x[2][2].payload)
            ))
        ).subscribe(
            self.message_subject
        )

    def on_command(self, x):
        assert isinstance(x, FP50Command)
        self.client.publish(self.topic_base + "/setpoint", str(x.setpoint), retain=True)
        self.logger.debug(f"setpoint updated = {x.setpoint}")

    def on_subscribe(self, observer, scheduler=None):
        return self.message_subject.subscribe(observer, scheduler)
