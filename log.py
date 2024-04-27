import logging

def setup_log(name):
    logger = logging.getLogger(name)   # create logger

    logger.setLevel(logging.DEBUG)  # set logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    filename = f"./logs/{name}.log"
    log_handler = logging.FileHandler(filename)
    log_handler.setLevel(logging.DEBUG)
    if name == "app":
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)

    return logger

