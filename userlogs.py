import logging

# Format for logging
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    '''
    To setup as many loggers as you want
    '''

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        logger.addHandler(handler)

    return logger