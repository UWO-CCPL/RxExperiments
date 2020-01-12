import configparser
import logging
import time
from typing import Optional
import numpy as np
from genicam.gentl import TimeoutException
from harvesters.core import Harvester, Buffer
from rx.core import Observable, typing, Observer
from rx.disposable import Disposable
from rx.scheduler import NewThreadScheduler

from datamodel.image import Image
from datamodel.node import Node

SECTION = "harvesters"


class HarvestersSource(Node, Observable):
    def __init__(self):
        Node.__init__(self, "Harvesters")
        Observable.__init__(self, self._on_subscribe)

        self.harvester = Harvester()
        self.cti_file = self.config[SECTION]["ctiFile"]
        self.harvester.add_cti_file(self.cti_file)
        self.logger.info(f"Loaded harvester cti file {self.cti_file}")
        self.harvester.update_device_info_list()
        self.logger.info(f"Found {len(self.harvester.device_info_list)} devices.")

    def _on_subscribe(self, observer: Observer, scheduler=None):
        self.acquirer = self.harvester.create_image_acquirer(list_index=0)
        self.reload_camera_driver()
        self.configure_callback(observer)
        self.acquirer.start_image_acquisition()

        def dispose():
            def _async_dispose(*args):
                # prevent join in the same thread.
                self.logger.info("Stopping image acquisition")
                self.acquirer.stop_image_acquisition()
                self.acquirer.destroy()
                self.logger.info("Stopped image acquisition")
            (scheduler or NewThreadScheduler()).schedule(_async_dispose)

        return Disposable(dispose)

    def reload_camera_driver(self):
        node = self.acquirer.device.node_map
        node.LineSelector.value = 'Line1'
        node.LineMode.value = 'Output'
        node.LineInverter.value = True
        node.LineSource.value = "ExposureActive"
        node.ExposureTime.value = 45.0
        node.AcquisitionFrameRateMode.value = "Basic"
        node.AcquisitionFrameRate.value = self.config[SECTION]["fps"]

    def configure_callback(self, observer):
        def _read_buffer():
            try:
                buffer: Buffer = self.acquirer.fetch_buffer(timeout=0.1)
                payload = buffer.payload
                component = payload.components[0]
                width = component.width
                height = component.height
                content = component.data.reshape(height, width)
                observer.on_next(Image(content.copy(), time.time_ns()))
                buffer.queue()
            except TimeoutException as ex:
                pass
            except Exception as ex:
                self.logger.error(ex)

        self.acquirer.on_new_buffer_arrival = _read_buffer
