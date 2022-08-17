import logging
import shutil
from pathlib import Path

import pytest

from common.Logger import get_logger


@pytest.fixture()
def clean_log_dir():
    log_dir = Path(__file__).parents[0].joinpath("test_logs")
    yield log_dir
    shutil.rmtree(str(log_dir))


def test_get_logger(clean_log_dir):
    test_log_dir = clean_log_dir
    logger = get_logger(name=__file__, log_path=test_log_dir.joinpath("test.log"))
    assert len(logger.handlers) == 2
    assert isinstance(logger.handlers[1], logging.FileHandler)
    # test use created logger if same name given
    assert logger == get_logger(name=__file__)
    assert logger != get_logger(test_log_dir)


def test_logging():
    logger = get_logger()
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")
