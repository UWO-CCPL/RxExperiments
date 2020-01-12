import logging
import time

from rx import scheduler

logging.root.setLevel(logging.DEBUG)
from configs.config import GlobalConfig
GlobalConfig.initialize_global_configuration()

from source.harvesters_source import HarvestersSource
from rx import operators

source = HarvestersSource()

def got_image(x):
    print (x)
source.pipe(
    operators.take(5),
    operators.observe_on(scheduler.ImmediateScheduler())
).subscribe(got_image)

input()