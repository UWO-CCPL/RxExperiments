from serial import Serial

from .serial import SerialControl


class CameraControlCommand:
    def __init__(self):
        self.exposure = None
        self.power = None
        self.trigger = None

    def set_exposure(self, exposure: float):
        """

        :param exposure: exposure (in microseconds)
        :return:
        """
        self.exposure = exposure
        return self

    def set_power(self, power: bool):
        self.power = power
        return self

    def set_trigger(self, trigger: bool):
        self.trigger = trigger
        return self


class CameraControl(SerialControl):
    def __init__(self, name="camera"):
        super().__init__(name)

    def create_serial_connection(self) -> Serial:
        port = self.config["cameraControl"]["port"]
        baud = self.config["cameraControl"]["baud"]
        return Serial(port, baud)

    def on_command(self, x):
        assert isinstance(x, CameraControlCommand)
        if x.power is not None:
            self.serial.write(f"s_power {1 if x.power else 0}\n".encode())
            self.logger.debug("power on" if x.power else "power off")

        if x.trigger is not None:
            self.serial.write(
                "arm_trigger\n".encode() if x.trigger else
                "disarm_trigger\n".encode()
            )
            self.logger.debug("trigger armed" if x.trigger else "trigger disarmed")

        if x.exposure is not None:
            tick = int(x.exposure * 72)
            self.serial.write(
                f"s_exposure {tick}\ncommit\n".encode()
            )
            self.logger.debug(f"exposure tick set to {tick}")
