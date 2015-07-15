import logging


def setup_logger():
    log_formatter              = logging.Formatter('%(asctime)s : %(message)s')
    log_progress_file_handler  = logging.FileHandler(
        'mongo_backup_progress.log',
        mode='a+'
    )
    log_progress_file_handler.setFormatter(log_formatter)

    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(log_formatter)

    logger = logging.getLogger('progress')
    logger.setLevel(logging.INFO)
    logger.addHandler(log_progress_file_handler)
    logger.addHandler(log_stream_handler)

    return logger


LOGGER = setup_logger()
