# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


def merge(obj_1: dict, obj_2: dict) -> dict:
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
    """
    if type(obj_1) is not type(obj_2):
        return obj_2
    if isinstance(obj_1, dict):
        res = dict(**obj_1)
        for k, v in obj_2.items():
            res[k] = merge(res[k], v) if k in res else v
        return res
    return obj_2
