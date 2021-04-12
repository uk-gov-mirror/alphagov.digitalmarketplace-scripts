import logging


# define a new log level for logging queue log levels
# not as high as INFO, but not as low as DEBUG
AUDIT = 15


def audit(logger: logging.Logger, msg, *args, **kwargs) -> None:
    logger.log(AUDIT, msg, *args, **kwargs)


logger = logging.getLogger("dmscripts.email_engine")

# monkey-patching technique from https://stackoverflow.com/a/28127947
logger.audit = audit.__get__(logger, logging.Logger)
