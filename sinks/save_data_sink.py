import os
from datetime import datetime

import pandas as pd
import rx
from pandas import DataFrame
from rx import operators

from sinks.base_sink import BaseSink
import pickle


class SaveDataSink(BaseSink):
    df: DataFrame

    def __init__(self, name, key, interval=10, scheduler=None, auto_timestamp=False):
        """
        Automatic data store as hdf5. The on_next message must be of pandas.Dataframe
        :param auto_timestamp:
        :param store_name: file name of the stored file. The target_dir option is respected in configs.ini
        :param interval: if None, store every time when new data come. Otherwise, only store after interval seconds.
        """
        super().__init__(name, on_next=self.on_new_data)

        self.auto_timestamp = auto_timestamp
        self.key = key
        self.save_path = os.path.join(self.config["data"]["base"], name + ".h5")
        self.interval = interval
        self.df = pd.DataFrame()

        # for timed data store
        self.new_data_flag = False

        if interval is not None:
            self.logger.info(f"storing data every {self.interval} seconds")
            rx.interval(interval, scheduler).pipe(
                operators.filter(lambda *args: self.new_data_flag)
            ).subscribe(
                lambda *args: self.save_data()
            )

    def on_new_data(self, x: pd.DataFrame):
        self.logger.debug("new data received")

        if self.auto_timestamp:
            x["timestamp"] = datetime.now()
        try:
            self.df = self.df.append(x)
        except Exception as ex:
            self.logger.error("failed to append new data.", exc_info=ex)

        if self.interval is None:
            self.save_data()

        self.new_data_flag = True

    def save_data(self):
        try:
            self.df.to_hdf(self.save_path, self.key, append=True, format="table")
            self.df = DataFrame()
            self.logger.debug(f"file saved")
        except Exception as ex:
            self.logger.error(f"failed to save file", exc_info=ex)

        self.new_data_flag = False
