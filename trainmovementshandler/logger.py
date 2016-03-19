import logging
import logging.handlers
import sys

__all__ = ['LOG']

DEBUG_LOG_FILENAME = '/var/log/train-movements-handler/debug.log'
INFO_LOG_FILENAME = '/var/log/train-movements-handler/info.log'
WARNING_LOG_FILENAME = '/var/log/train-movements-handler/warning.log'

TEN_MEGABYTES = 10 * 1024 * 1024
HUNDRED_MEGABYTES = 100 * 1024 * 1024

# set up formatting
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s %(name)s: %(message)s')

# set up logging to STDOUT for all levels DEBUG and higher
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)

# set up logging to a file for all levels DEBUG and higher
fh = logging.handlers.RotatingFileHandler(
    DEBUG_LOG_FILENAME, maxBytes=TEN_MEGABYTES, backupCount=10)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

# set up logging to a file for all levels DEBUG and higher
fh = logging.handlers.RotatingFileHandler(
    INFO_LOG_FILENAME, maxBytes=TEN_MEGABYTES, backupCount=10)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

# set up logging to a file for all levels WARNING and higher
fh2 = logging.handlers.RotatingFileHandler(
    WARNING_LOG_FILENAME, maxBytes=HUNDRED_MEGABYTES, backupCount=3)
fh2.setLevel(logging.WARN)
fh2.setFormatter(formatter)

logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)

# create Logger object
LOG = logging.getLogger('')
LOG.setLevel(logging.DEBUG)
LOG.addHandler(sh)
LOG.addHandler(fh)
LOG.addHandler(fh2)
