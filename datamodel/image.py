import numpy as np

from utils import image_encoder


class Image:
    def __init__(self, image: np.ndarray, time: float):
        self.image = image
        self.time = time
        self._jpeg = None

    @property
    def jpeg(self):
        if self._jpeg is None:
            self._jpeg = image_encoder.ImageEncoder.encode(self.image)

        return self._jpeg

