from datamodel.image import Image
from sink.base_sink import BaseSink


class SaveImageSink(BaseSink):
    def __init__(self):
        super().__init__()

    def on_image(self, x):
        assert isinstance(x, Image)
