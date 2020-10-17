from datetime import datetime

import rx
from rx import operators
import pandas as pd


def data_framer(window_length=None, auto_timestamp=False):
    """
    Accept incoming pandas DataFrame, append into the internal buffer and feed next.
    :param auto_timestamp: automatically set the incoming DataFrame's timestamp to the current time.
    :param window_length:
    :return:
    """

    def reducer(acc: pd.DataFrame, new: pd.DataFrame):
        if auto_timestamp:
            new["timestamp"] = datetime.now()
        updated = acc.append(new)
        if window_length:
            return updated[-window_length:]
        else:
            return updated

    return rx.pipe(operators.scan(reducer, pd.DataFrame()))
