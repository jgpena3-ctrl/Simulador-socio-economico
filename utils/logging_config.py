import logging

import config


def setup_logging(level_name=None):
    """Configura logging global del simulador con nivel ajustable."""
    selected_level = (level_name or config.LOG_LEVEL or "INFO").upper()
    level = getattr(logging, selected_level, logging.INFO)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        for handler in root_logger.handlers:
            handler.setLevel(level)
        return

    logging.basicConfig(level=level, format=config.LOG_FORMAT)
