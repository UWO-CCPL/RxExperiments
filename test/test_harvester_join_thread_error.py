import time

from harvesters.core import Harvester
from rx import scheduler, operators
import rx
from rx.disposable import Disposable


def create(observer, sc=None):
    h = Harvester()
    h.add_cti_file("C:\\Program Files\\MATRIX VISION\\mvIMPACT Acquire\\bin\\x64\\mvGenTLProducer.cti")
    h.update_device_info_list()
    acquirer = h.create_image_acquirer(0)
    print("create")
    def on_new_buffer_arrival():
        buffer = acquirer.fetch_buffer()
        print("buffer")
        observer.on_next(buffer)
        buffer.queue()

    def dispose():
        # scheduler.NewThreadScheduler().schedule(lambda *args: acquirer.stop_image_acquisition())
        acquirer.stop_image_acquisition()

    acquirer.on_new_buffer_arrival = on_new_buffer_arrival
    acquirer.start_image_acquisition()
    return Disposable(dispose)

observable = rx.create(create)

observable.pipe(operators.take(5)).subscribe(print, print)
time.sleep(5)