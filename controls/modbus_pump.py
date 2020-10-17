import math
import struct
import time

from rx import operators
from rx.scheduler import NewThreadScheduler
from rx.subject import Subject
from serial import Serial

from .serial import SerialControl
from pymodbus.client.sync import ModbusSerialClient


class ModbusPumpControlCommand:
    def __init__(self):
        self.slurry_pump = None
        self.clear_pump = None

    def set_slurry_pump(self, slurry_pump):
        self.slurry_pump = slurry_pump
        return self

    def set_clear_pump(self, clear_pump):
        self.clear_pump = clear_pump
        return self


class ModbusPumpControl(SerialControl):
    serial: ModbusSerialClient

    def __init__(self, name="pump_control"):
        super().__init__(name)
        self.pump_control_config = self.config["pumpControl"]
        self.control_delay = self.pump_control_config["controlDelay"]
        self.tq = Subject()
        self.scheduler = NewThreadScheduler()
        self.update_subject = Subject()

        def on_next(job):
            try:
                job()
            except Exception as ex:
                self.logger.error(ex)

        self.tq.pipe(operators.observe_on(self.scheduler)).subscribe(
            on_next,
            lambda ex: self.logger.error(ex),
            lambda: self.serial.close()
        )
        self.state = [0.0, 0.0]
        self.enable_remote_control(True)

    def create_serial_connection(self):
        self.pump_control_config = self.config["pumpControl"]
        port = self.pump_control_config["port"]
        baud = self.pump_control_config["baud"]
        timeout = self.pump_control_config["timeout"]
        client = ModbusSerialClient(method="rtu", port=port, baudrate=baud, timeout=timeout)
        client.connect()
        return client

    def enable_remote_control(self, enable=True):
        def _enable_remote_control(unit, enable=True):
            self.tq.on_next(lambda: self.serial.write_coil(0x1004, 1 if enable else 0, unit=unit))
            self.tq.on_next(lambda: time.sleep(self.control_delay))

        _enable_remote_control(self.pump_control_config["endpoint"]["slurry"]["address"], enable)
        _enable_remote_control(self.pump_control_config["endpoint"]["clear"]["address"], enable)

    def set_speed(self, slurry_speed, clear_speed):
        if slurry_speed is not None and slurry_speed != self.state[0]:
            self.ctrl_pump(self.pump_control_config["endpoint"]["slurry"]["address"], slurry_speed)
            self.logger.debug(f"Slurry pump speed updated: {slurry_speed}")
            self.state[0] = slurry_speed
        if clear_speed is not None and clear_speed != self.state[1]:
            self.ctrl_pump(self.pump_control_config["endpoint"]["clear"]["address"], clear_speed)
            self.logger.debug(f"Clear pump speed updated: {clear_speed}")
            self.state[1] = clear_speed

    def ctrl_pump(self, unit, speed):
        def start_pump(unit, enable=True):
            self.tq.on_next(lambda: self.serial.write_coil(0x1001, 1 if enable else 0, unit=unit))
            self.tq.on_next(lambda: time.sleep(self.control_delay))

        def direction(unit, direction=True):
            self.tq.on_next(lambda: self.serial.write_coil(0x1003, 65280 if direction else 0, unit=unit))
            self.tq.on_next(lambda: time.sleep(self.control_delay))

        def rate(unit, speed):
            buffer = struct.pack("f", math.fabs(speed))
            lb = struct.unpack("<H", buffer[0:2])[0]
            hb = struct.unpack("<H", buffer[2:4])[0]
            self.tq.on_next(lambda: self.serial.write_registers(0x3001, [hb, lb], unit=unit))
            self.tq.on_next(lambda: time.sleep(self.control_delay))

        # stop pump first otherwise cannot adjust direction
        start_pump(unit, False)

        rate(unit, speed)
        if speed == 0:
            return
        direction(unit, speed > 0)
        start_pump(unit, True)

    def on_command(self, x):
        assert isinstance(x, ModbusPumpControlCommand)
        self.set_speed(x.slurry_pump, x.clear_pump)
        self.update_subject.on_next(x)

    def on_subscribe(self, observer, scheduler=None):
        self.update_subject.subscribe(observer, scheduler)
