import sys
from Dashboard import Dashboard
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("econometrics")

if __name__ == '__main__':
    log_size = 10 * pow(10,6) # 10MB

    log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    log_handler = RotatingFileHandler('econometrics.log',mode='a',
                                      maxBytes=log_size,backupCount=2,
                                      encoding=None, delay=0)

    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.DEBUG)
    # Not sure why need to set the log level twice
    # https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)

    dashboard = Dashboard()

