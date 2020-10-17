import logging
from typing import Union

import rx
from rx import operators
from rx import typing as rx_t, subject
from rx.disposable import CompositeDisposable
from rx.subject import BehaviorSubject

from datamodel.node import Node
from utils import mqtt_wrapper


class MQTTSource(Node, rx.Observable):
    def __init__(self, client: mqtt_wrapper.MQTTClientWrapper, topic: Union[str, None], qos=0, options=None,
                 properties=None, config=None, name=""):
        self.options = options
        self.properties = properties
        self.qos = qos
        self.topic = topic
        self.client = client
        self.message_subject = subject.Subject()
        self.broker_subscribed = False
        self.subscription: rx.disposable.Disposable = None
        self.can_subscribe = BehaviorSubject(False)
        Node.__init__(self, name=name, config=config)
        rx.Observable.__init__(self, subscribe=self.subscribe_func)

    def subscribe_func(self, observer, scheduler=None) -> rx_t.Disposable:
        if not self.broker_subscribed:
            self.client.connected_subject.subscribe(self.configure_subscription)
            logging.debug("subscribe to on_connect event")
        subscription = self.message_subject.pipe(operators.map(self.transform)).subscribe(observer)

        return subscription

    def configure_subscription(self, x):
        if x:
            if self.topic:
                self.subscribe_on_broker(self.topic)
            self.can_subscribe.on_next(True)

    def transform(self, x):
        return x

    def subscribe_on_broker(self, topic):
        self.subscription = self.client.subscribe(topic, self.qos, self.options, self.properties)
        self.client.message_callback_add(topic,
                                         lambda client, userdata, message: self.message_subject.on_next(message))

    def __del__(self):
        if self.subscription:
            self.subscription.dispose()
