import datetime
import time


class TimeResolver:
    """
    Utility that can be used to convert nanosecond integer values from `time.perf_counter_ns()` into instances of
    `datetime.datetime` using the `resolve` method.
    """

    # Record when BanterBot was initialized as a datetime.datetime.
    _init_time_datetime = datetime.datetime.now()

    # Record when BanterBot was initialized as a perf_counter_ns.
    _init_counter = time.perf_counter_ns()

    @classmethod
    def resolve(cls, counter: int) -> datetime.datetime:
        """
        Converts an integer obtained from from perf_counter_ns into datetime.datetime instance
        """
        dt = datetime.timedelta(microseconds=round(1e-3 * (counter - cls._init_counter)))
        return cls._init_time_datetime + dt
