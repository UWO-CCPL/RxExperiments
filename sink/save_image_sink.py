import os

from datamodel.image import Image
from sink.base_sink import BaseSink
from rx.subject import Subject

class SaveImageSink(BaseSink):
    def __init__(self, name="save_image"):
        super().__init__(name, self.on_image)
        self.dir_path = os.path.join(self.config["data"]["base"], self.config["data"]["image"])
        os.makedirs(self.dir_path, exist_ok=True)

        self.file_saved_subject = Subject()

    def on_image(self, x):
        assert isinstance(x, Image)
        path = os.path.join(self.dir_path, f"{x.time}.jpg")
        with open(path, "wb") as f:
            f.write(x.jpeg)
        self.file_saved_subject.on_next(path)
        self.logger.debug("Saving file:" + path)
