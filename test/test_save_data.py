from configs.config import GlobalConfig

GlobalConfig.initialize_global_configuration()

from sink.save_data_sink import SaveDataSink
import pandas as pd
import rx
from rx import operators
from rx import scheduler


sink = SaveDataSink("test_save", "value", None)
rx.range(1, 100, 1, scheduler=scheduler.ImmediateScheduler()).pipe(
    operators.do_action(lambda x: print(x)),
    operators.map(lambda x: pd.DataFrame([{"value": x}])),
).subscribe(sink)
print("Done")
