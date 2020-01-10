from typing import Dict
import uuid
import rx
from rx import typing as rx_t, subject
from rx.disposable import CompositeDisposable

from datamodel.node import Node
from utils import mqtt_wrapper
import logging

from utils.mqtt_wrapper import MQTTClientWrapper


class MQTTSource(Node, rx.Observable):
    def __init__(self, client: mqtt_wrapper.MQTTClientWrapper, topic: str, qos=0, options=None, properties=None):
        self.options = options
        self.properties = properties
        self.qos = qos
        self.topic = topic
        self.client = client
        self.message_subject = subject.Subject()
        self.upstream_subscribed = False
        super().__init__(subscribe=self.subscribe_func)

    def subscribe_func(self, observer, scheduler=None) -> rx_t.Disposable:
        if not self.upstream_subscribed:
            self.client.connected_subject.subscribe(self.configure_subscription)
            logging.debug("subscribe to on_connect event")
        subscription = self.message_subject.subscribe(observer)

        def dispose():
            self.client.message_callback_remove(self.topic)

        return CompositeDisposable(dispose, subscription)

    def configure_subscription(self, x):
        if x:
            self.client.subscribe(self.topic, self.qos, self.options, self.properties)
            self.client.message_callback_add(self.topic,
                                             lambda client, userdata, message: self.message_subject.on_next(message))