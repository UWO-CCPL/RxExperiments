import rx
from rx import operators
import pandas as pd


def data_framer():
    """
    Accept incoming pandas DataFrame, append into the internal buffer and feed next.
    :return:
    """

    def reducer(acc: pd.DataFrame, new: pd.DataFrame):
        return acc.append(new)

    op = rx.pipe(
        operators.scan(reducer, pd.DataFrame())
    )
    return op
