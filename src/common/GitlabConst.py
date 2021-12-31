"""Provide const values for connecting gitlab."""
import os

from dotenv import load_dotenv

from . import Const

load_dotenv(Const.APP_PROP_PATH)
__ids = os.environ.get("GITLAB_GROUP_IDS", [1])
URL = os.environ.get("GITLAB_URL", "http://localhost")
TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN", "YOUR TOKEN")
if isinstance(__ids, str):
    GROUP_IDS = [int(id) for id in __ids.split(",")]
else:
    GROUP_IDS = __ids
