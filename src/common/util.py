"""Provide utility functions"""
from typing import Any, Union


def flatten_dict_in_dict(base_dict: dict[str, Union[str, dict[str, Any]]]):
    """
    Flatten dict in dict. This function is destructive!.

    Example: {'author': {'id': 1, 'name': 'name', ...}} -> {'author-id': 1, 'author-name': 'name'...}
    """
    drop_keys = []
    add_dict = dict()
    for base_dict_key, base_dict_value in base_dict.items():
        if isinstance(base_dict_value, dict):
            drop_keys.append(base_dict_key)
            for k, v in base_dict_value.items():
                add_dict[f"{base_dict_key}-{k}"] = v
    for drop_key in drop_keys:
        del base_dict[drop_key]
    base_dict.update(add_dict)
