"""Provide utility functions."""
from typing import Any, Union


def flatten_dict_in_dict(base_dict: dict[str, Union[str, dict[str, Any]]]):
    """
    Flatten dict in dict. This function is destructive!.

    Example: {'author': {'id': 1, 'name': 'name', ...}} -> {'author-id': 1, 'author-name': 'name'...}
    """

    drop_keys: list[str] = []
    add_dict: dict[str, Any] = dict()
    for base_dict_key, base_dict_value in base_dict.items():
        __flatten_dict(base_dict_key, base_dict_value, drop_keys, add_dict)
    for drop_key in drop_keys:
        del base_dict[drop_key]
    base_dict.update(add_dict)


def __flatten_dict(key: str, value: Any, drop_keys: list[str], add_dict: dict[str, Any]):
    if isinstance(value, dict):
        drop_keys.append(key)
        for k, v in value.items():
            add_dict[f"{key}-{k}"] = v
