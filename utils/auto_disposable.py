class AutoDisposable(object):
    def __init__(self, disposable):
        self.disposable = disposable

    def __del__(self):
        if self.disposable and not self.disposable.is_disposed:
            self.disposable.dispose()