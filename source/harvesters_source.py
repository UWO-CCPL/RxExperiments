import configparser
import logging
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
        self.logger = logging.getLogger("HarvestersSource")

        super().__init__(self._on_subscribe)

    def _on_subscribe(self, observer: Observer, scheduler=None):
        scheduler = scheduler or NewThreadScheduler()

        harvester = Harvester()
        harvester.add_cti_file(self.config[SECTION]["cti_file"])
        harvester.update_device_info_list()
        self.acquirer = acquirer = harvester.create_image_acquirer(0)
        self.reload_camera_driver()
        self.configure_callback(observer)
        acquirer.start_image_acquisition()

        def dispose():
            if acquirer.is_acquiring_images():
                acquirer.stop_image_acquisition()
            acquirer.destroy()

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
                time = buffer.timestamp_ns
                observer.on_next(Image(content.copy(), time / 1e9))
                buffer.queue()
            except TimeoutException as ex:
                pass
            except Exception as ex:
                self.logger.error(ex)

        self.acquirer.on_new_buffer_arrival = _read_buffer
