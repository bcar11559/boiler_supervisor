import logging
from applibs.exceptions import LoggingError

class ApplicationLogger():

    logger = None

    def __init__(
            self,
            root_level=logging.DEBUG,
            file_level=logging.DEBUG,
            stream_level=logging.DEBUG,
            log_file="system.log",
            log_format="%(asctime)-15s | %(levelname)-9s | %(message)s",
            name="devicelog"
                ):

        if self.logger:
            raise LoggingError("Only one Application Logger is allowed!")
        else:
            self.name = name

            self.set_logger(logging.getLogger())
            self.logger.setLevel(root_level)

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(stream_level)

            file_handler = logging.FileHandler(log_file, mode="a")
            file_handler.setLevel(file_level)

            formatter = logging.Formatter(log_format)
            stream_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            self.logger.addHandler(stream_handler)
            self.logger.addHandler(file_handler)

            self.logger.info(f'Logging initialised at Level: {self.get_loglevel(self.logger.level)}')
    
    @classmethod
    def set_logger(cls, logger):
         cls.logger = logger
    
    @classmethod
    def get_logger(cls):
         return cls.logger

    @staticmethod
    def get_loglevel(val):
         if val == logging.NOTSET:
              return "NOTSET"
         elif val == logging.DEBUG:
              return "DEBUG"
         elif val == logging.INFO:
              return "INFO"
         elif val == logging.WARNING:
              return "WARNING"
         elif val == logging.ERROR:
              return "ERROR"
         elif val == logging.CRITICAL:
              return "CRITICAL"
         else:
              return "UNKNOWN"