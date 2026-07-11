import logging
import sys

def get_logger(name: str = "app_logger") -> logging.Logger: 

    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    # Handler: Envia para o console (Terminal)
    stdout_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)

    return logger