import logging

import numpy as np

import config

logger = logging.getLogger(__name__)


def setup_random_seed(seed=None):
    """Configura semilla global de NumPy para reproducibilidad."""
    selected_seed = config.SEED if seed is None else seed

    if selected_seed is None:
        logger.info("Semilla aleatoria no configurada (config.SEED=None)")
        return None

    np.random.seed(selected_seed)
    logger.info("Semilla aleatoria configurada: %s", selected_seed)
    return selected_seed
