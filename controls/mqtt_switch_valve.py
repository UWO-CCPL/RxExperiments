from rx.subject import Subject

from utils.mqtt_wrapper import MQTTClientWrapper
from .base_control import BaseControl


class MQTTSwitchValve(BaseControl):
    def __init__(self, client: MQTTClientWrapper, name="switch_valve", config=None):
        super().__init__(name, config=config)
        self.client = client

        self.topic_base = self.config["switchValve"]["topicBase"]
        self.message_subject = Subject()

        topic = self.topic_base + "/state"
        self.client.subscribe(topic)
        def cb(client, userdata, message):
            self.message_subject.on_next(int(message.payload))
        self.client.message_callback_add(topic, cb)

    def on_command(self, x):
        if x in [0, "0", False, "false", "left"]:
            state = "0"
        elif x in [1, "1", True, "true", "right"]:
            state = "1"
        else:
            self.logger.error(f"{x} is not a valid command")
            return

        self.client.publish(self.topic_base + "/state", state, retain=True)
        self.logger.debug(f"State updated = {x.state}")

    def on_subscribe(self, observer, scheduler=None):
        return self.message_subject.subscribe(observer, scheduler)
