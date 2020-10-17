import logging
import logging
import time

from genicam.gentl import TimeoutException
from harvesters.core import Harvester, Callback, ImageAcquirer
from rx.core import Observable, Observer
from rx.disposable import Disposable
from rx.scheduler import NewThreadScheduler

from datamodel.image import Image
from datamodel.node import Node

SECTION = "harvesters"


class CallbackOnNewBuffer(Callback):
    def __init__(self, ia: ImageAcquirer, observer: Observer, logger=None):
        super().__init__()
        self.logger = logger or logging.getLogger("Callback")
        self.acquirer = ia
        self.observer = observer

    def emit(self, context=None):
        try:
            with self.acquirer.fetch_buffer(timeout=0.1) as buffer:
                # Work with the fetched buffer.
                payload = buffer.payload
                component = payload.components[0]
                width = component.width
                height = component.height
                content = component.data.reshape(height, width)
                self.observer.on_next(Image(content.copy(), time.time_ns()))
        except TimeoutException:
            pass
        except Exception as ex:
            self.logger.error(ex)


class HarvestersSource(Node, Observable):
    def __init__(self):
        Node.__init__(self, "Harvesters")
        Observable.__init__(self, self._on_subscribe)
        self.cfg = self.config[SECTION]
        self.harvester = Harvester()
        if self.cfg["disableInternalLogger"]:
            self.harvester._logger.setLevel(100)

        self.cti_file = self.cfg["ctiFile"]
        self.harvester.add_file(self.cti_file)
        self.logger.info(f"Loaded harvester cti file {self.cti_file}")
        self.harvester.update()
        self.logger.info(f"Found {len(self.harvester.device_info_list)} devices.")

    def _on_subscribe(self, observer: Observer, scheduler=None):
        self.acquirer = self.harvester.create_image_acquirer(list_index=0)
        self.reload_camera_driver()
        self.acquirer.add_callback(self.acquirer.Events.NEW_BUFFER_AVAILABLE,
                                   CallbackOnNewBuffer(self.acquirer, observer))
        self.acquirer.start_image_acquisition(run_in_background=True)
        self.logger.info("Started acquisition in background")

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
        node.LineSelector.value = self.cfg["lineSelector"]
        node.LineMode.value = self.cfg["lineMode"]
        node.LineInverter.value = self.cfg["lineInverter"]
        node.LineSource.value = "ExposureActive"
        node.ExposureTime.value = self.cfg["exposureTime"]
        if node.has_node("acquisitionFrameRateMode"):
            # Allied Vision Camera
            node.AcquisitionFrameRateMode.value = "Basic"
        node.AcquisitionFrameRate.value = self.cfg["acquisitionFrameRate"]

        if self.cfg["extraNodes"]:
            extra_nodes: dict = self.cfg["extraNodes"]
            for k, v in extra_nodes.items():
                node.get_node(k).value = v
