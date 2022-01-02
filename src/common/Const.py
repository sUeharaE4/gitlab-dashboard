"""Provide common const values."""
import os
import sys
from pathlib import Path

from . import errors

__mode = os.environ.get("APP_EXEC_MODE", "prod")
__prop_name = f".app_prop_{__mode}"
__sample_prop_name = ".app_prop_sample"

SRC_ROOT = Path(__file__).parents[1]
APP_PROP_PATH = SRC_ROOT.parents[0].joinpath(__prop_name)
SAMPLE_PROP_PATH = SRC_ROOT.parents[0].joinpath(__sample_prop_name)
ST_CACHE_TIME_SHORT = 60 * 5

if not APP_PROP_PATH.exists():
    err = errors.SettingNotFoundError(APP_PROP_PATH, SAMPLE_PROP_PATH)
    print(err, file=sys.stderr)
    raise err
else:
    print(f"load apprication properties from {str(APP_PROP_PATH)}")
