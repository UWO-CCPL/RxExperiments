from .base_control import BaseControl
from serial import Serial


class SerialControl(BaseControl):
    serial: Serial

    def __init__(self, name, config=None):
        super().__init__(name, config=None)
        self.serial = self.create_serial_connection()

    def create_serial_connection(self) -> Serial:
        """
        Override this with configs to create a serial connection
        :return:
        """
        raise NotImplementedError()
