import lttb
import numpy as np
import pandas as pd
import rx
from rx import operators


def lttb_operator(n_out: int):
    """
    Input frame must be datetime indexed.
    If multiple columns are present, each column will be returned in array of dataframes
    :param n_out:
    :return: array of dataframes
    """
    def lttb_ops(x: pd.DataFrame):
        if x.shape[0] <= n_out:
            # just split into multiple dataframes
            ret = [pd.DataFrame(index=x.index, data=x[col]) for col in x.columns]
            return ret

        # convert DataFrame index (datetime) to int
        x = x.copy()
        x.index = x.index.astype("int64")

        # lttb calculation
        ret = []
        for col in x.columns:
            data = np.array((x.index.values, x[col])).T
            output = lttb.downsample(data, n_out)
            df = pd.DataFrame(index=output[:, 0].astype('datetime64[ns]'), data={col: output[:, 1]})
            ret.append(df)
        return ret

    return rx.pipe(operators.map(lttb_ops))
