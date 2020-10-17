from utils.mqtt_wrapper import MQTTClientWrapper
from .base_control import BaseControl
from rx.subject import Subject

import numbers


class MQTTPump(BaseControl):
    def __init__(self, client: MQTTClientWrapper, name: str, base_topic: str, config=None):
        """

        :param client:
        :param name:
        :param base_topic: Topic prefix without trailing slash
        """
        super().__init__(name, config)
        self.base_topic = base_topic
        self.client = client
        self.enable = True
        self.update_subject = Subject()

    def on_subscribe(self, observer, scheduler=None):
        return self.update_subject.subscribe(observer, scheduler=scheduler)

    def on_command(self, x):
        if isinstance(x, numbers.Number):
            x = str(x)

        if x == "0":
            self.client.publish(f"{self.base_topic}/enable", "0")
            self.enable = False
            self.logger.info("Pump deactivated")
        else:
            if not self.enable:
                self.client.publish(f"{self.base_topic}/enable", "1")
                self.enable = True
                self.logger.info("Pump activated")
        self.client.publish(f"{self.base_topic}/sps", x)
        self.update_subject.on_next(float(x))
        self.logger.info(f"Pump set to {x}")
