#  Creates a logger that writes timestamps and messages to logs/automation.log

import logging
import os

class LogGen:

    @staticmethod
    def loggen():
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            file_handler = logging.FileHandler(
                "logs/automation.log")
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        return logger