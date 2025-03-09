import datetime
import logging

from settings import settings


class UtcFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created).astimezone(
            datetime.timezone.utc
        )
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat(timespec="milliseconds")


_formatter = UtcFormatter(
    fmt="%(levelname)s %(asctime)s.%(msecs)03dZ %(pathname)s:%(lineno)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


def get_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    handler = logging.StreamHandler()
    handler.setFormatter(_formatter)
    logger.addHandler(handler)
    return logger
