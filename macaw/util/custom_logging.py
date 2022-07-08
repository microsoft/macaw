"""
The internal logger.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import logging


class LoggerFactory:
    @staticmethod
    def create_logger(params) -> logging.Logger:
        """
        Creates a new custom logger with configuration passed in params dictionary. Supported options are
        'logger_name', 'logger_level', and 'logger_file'.
        """
        logger = logging.getLogger(params.get("logger_name", "MacawLogger"))
        logger.setLevel(params.get("logger_level", logging.DEBUG))

        if "logger_file" in params:
            handler = logging.FileHandler(params["logger_file"])
        else:
            handler = logging.StreamHandler()

        formatter = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
