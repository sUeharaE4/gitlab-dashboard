"""Provide Exception classes."""
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SettingNotFoundError(Exception):
    conf_path: Path
    sample_conf_path: Path

    def __str__(self) -> str:
        msg = (
            "Please make sure "
            "that you have created the environment setting file."
            "The preferences file should be located at this location: "
            f"{str(self.conf_path)}"
            "\n"
            "If you haven't created the file yet, "
            "please copy and edit this sample configuration file: "
            f"{str(self.sample_conf_path)}"
        )
        return msg


@dataclass(frozen=True)
class ResourceNotFoundError(Exception):
    target_resource: str
    search_condition: dict[str, Any]

    def __str__(self) -> str:
        return f"{target_resource} not found. Search condition is {search_condition}."
