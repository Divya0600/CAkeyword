import logging


def setup_logger(log_name: str) -> logging.Logger:
    """
    Sets up a logger with the specified log_name

    Args:
        log_name (str): Name of the logger to set up

    Returns:
        (logging.Logger): Logger object.
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger

logger = setup_logger('keyword-extraction')