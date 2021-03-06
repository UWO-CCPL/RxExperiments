from typing import Callable, Optional

from rx import Observable
from rx.core import typing
from rx.core.typing import Mapper
from rx.disposable import Disposable


def from_callback(func: Callable, mapper: Optional[Mapper] = None) -> Callable[[], Observable]:
    def function(*args):
        arguments = list(args)

        def subscribe(observer: typing.Observer, scheduler: Optional[typing.Scheduler] = None) -> typing.Disposable:
            def handler(*args):
                results = list(args)
                if mapper:
                    try:
                        results = mapper(args)
                    except Exception as err: # pylint: disable=broad-except
                        observer.on_error(err)
                        return

                    observer.on_next(results)
                else:
                    if isinstance(results, list) and len(results) <= 1:
                        observer.on_next(*results)
                    else:
                        observer.on_next(results)

                    # observer.on_completed()

            arguments.append(handler)
            func(*arguments)
            return Disposable()

        return Observable(subscribe)
    return function