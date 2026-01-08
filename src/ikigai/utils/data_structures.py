# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


from typing import Any

from ikigai.utils.missing import MISSING


def merge_dicts(obj_1: dict, obj_2: dict, *, sentinel: Any = MISSING) -> dict:
    """
    Merge two dictionaries recursively, with the second taking precedence.

    Performs a deep merge of nested dictionaries. When keys conflict between
    the two dictionaries, values from obj_2 override those from obj_1.

    Parameters
    ----------

    obj_1 : dict
        The first dictionary to merge.

    obj_2 : dict
        The second dictionary to merge (takes precedence in conflicts).

    sentinel: Any
        Sentinel value, when present in obj_2 will remove
        the corresponding key from the result.
        Avoid using None or MISSING as sentinel, instead create a sentinel
        using `object()` to ensure uniqueness.

    Returns
    -------

    dict
        The merged dictionary.

    Examples
    --------

    Simple merge with conflict resolution:

    >>> merge({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
    {'a': 1, 'b': 3, 'c': 4}

    Nested dictionary merge:

    >>> merge({'a': {'b': 1}}, {'a': {'c': 2}})
    {'a': {'b': 1, 'c': 2}}

    List values are replaced, not merged:

    >>> merge({'a': {'b': [1, 2]}}, {'a': {'b': [3, 4]}})
    {'a': {'b': [3, 4]}}

    Using sentinel to remove a value from obj_1

    >>> sentinel = object()
    >>> merge({'a': 1, 'b': 2}, {'b': sentinel}, sentinel=sentinel)
    {'a': 1}
    """
    if type(obj_1) is not type(obj_2):
        return obj_2

    use_sentinel = sentinel is not MISSING
    if isinstance(obj_1, dict):
        result = dict(**obj_1)
        for k, v in obj_2.items():
            if use_sentinel and v is sentinel:
                result.pop(k, None)
                continue

            result[k] = (
                merge_dicts(result[k], v, sentinel=sentinel) if k in result else v
            )
        return result
    return obj_2
