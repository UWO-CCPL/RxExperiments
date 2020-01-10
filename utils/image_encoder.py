import numpy as np
import turbojpeg as tj

from configs.config import GlobalConfig


class ImageEncoder:
    _encoder = None
    _quality = 100

    @classmethod
    def encode(cls, image: np.ndarray, config=None):
        if cls._encoder is None:

            config = config or GlobalConfig.get_global_config()
            path = config["turbojpeg"]["path"]
            quality = config["turbojpeg"]["quality"]

            cls._encoder = tj.TurboJPEG(path)
            cls._quality = quality

        if len(image.shape) == 2:
            return cls._encoder.encode(image[:, :, np.newaxis], quality=cls._quality,
                                  jpeg_subsample=tj.TJSAMP_GRAY, pixel_format=tj.TJPF_GRAY)
        else:
            raise NotImplementedError("Multi-channel image encoding is not supported.")
