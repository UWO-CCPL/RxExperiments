import numpy as np
import pandas as pd
import pickle
from .base_property import Property
from configs.config import GlobalConfig

class TaurineProperty(Property):
    def __init__(self, config=None):
        self.config = config or GlobalConfig.get_global_config()
        with open(self.config["concentration"]["model"], "rb") as f:
            self.model = pickle.load(f)

    def solubility(self, temperature: float):
        MW_taurine = 125.15
        MW_water = 18.01528
        A1 = -3.15
        A2 = -2263.75
        A3 = 9.94
        A4 = -4755.72
        A5 = 12474.32
        A6 = -14846.20
        A7 = 6098.95
        TK = temperature + 273.15
        x0cal = np.exp(A1 + A2 / TK + A3 + (A4 + A5 + A6 + A7) / TK)
        return x0cal * MW_taurine / ((1 - x0cal) * MW_water)

    def raman_concentration(self, input_data: np.ndarray) -> pd.DataFrame:
        """

        :param input_data: (shape: 3327, 1) Must contain column made of wave number and temperature in C
        :return:
        """
        y_pred = self.model.predict(input_data)
        return y_pred
