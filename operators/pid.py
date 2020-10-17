import rx
from rx import operators
from simple_pid import PID


class PIDInput:
    def __init__(self, setpoint, value):
        self.setpoint = setpoint
        self.value = value


def pid(p, i, d, sample_time=1, limit=4, linearization_point=0):
    """

    :param sample_time:
    :param linearization_point:
    :param p:
    :param i:
    :param d:
    :return:
    """
    control = PID(p, i, d, sample_time=sample_time, setpoint=linearization_point)
    control._integral=linearization_point

    def pid_calculation(x: PIDInput):
        control.setpoint = x.setpoint
        control.output_limits = (x.value - limit, x.value + limit)
        return control(x.value)

    return rx.pipe(
        operators.map(pid_calculation)
    )
