"""Helpers functions to do basic data manipulation.

Functions
    map_accepted_key            #
    clean_input_fields          #
    clean_sort                  #
    normalize_sort              #
    normalize_fields            #
    normalize_remove_columns    #
"""


def map_accepted_key(input_key_map):
    """Helper that create a new dict where multiples keys can refer
    to the same value.

    Args
        input_key_map (dict): input dict where a key refer to an iter of
            values.

    Returns
        dict: new dict where multiple keys can refer to the same value
    """
    return {
        acc_key: used_key for used_key, acc_keys
        in input_key_map.items()
        for acc_key in acc_keys
    }


def clean_input_fields(fields):
    """Helper to lower input keyword and transform a given iter of args
    in a dict.

    Args
        fields (iter[tuple[str, Any]]): iterable to transform input in
            a dict.

    Returns
        dict: Transformed input dict
    """
    if not fields:
        return None
    return {f[0].lower(): f[1] for f in fields}


def clean_sort(sort):
    """Helper to clean the provided sort. It lowers input and add a
    sorting direction (ascending) or (descending).

    Args
        sort (iter[str]): iterable of provided sorting elements.

    Returns
        tuple[tuple[str, bool]]|None: A tuple of tuple element of
            sorting element and their direction with True = descending.
    """
    if not sort:
        return None
    sort = [s.lower() for s in sort]
    output = []
    for s in sort:
        if ":desc" in s:
            output.append((s.split(":desc")[0], True))
        elif ":asc" in s:
            output.append((s.split(":asc")[0], False))
        else:
            output.append((s, False))
    return tuple(output)


def normalize_sort(sort, keys_map):
    """Helper to normalize the provided sort, it replaces the sort key
    by sort key that are expected at the service layer.

    Args
        sort (iter[tuple[str, bool]): iterable of provided sorting
            elements.
        keys_map (dict): dict where keys are whitelisted input and
            value are the new key we want to use for the sorting.

    Returns
        tuple[tuple[str, bool]]|None: A tuple of tuple element of
            sorting element and their direction with True = descending.
    """
    if not sort:
        return None
    return tuple([(keys_map.get(keyword, keyword), is_desc)
                  for keyword, is_desc in sort if keyword in keys_map])


def normalize_fields(fields, keys_map):
    """Helper to normalize the provided filter, it replaces the fields
    key by filter key that are expected at the service layer.

    Args
        fields (dict): dict of filters input.
        keys_map (dict): dict where keys are whitelisted input and
            value are the new key we want to use for the sorting.

    Returns
        dict: Transformed input dict
    """
    if not fields:
        return None
    return {keys_map.get(k, k): v for k, v in fields.items() if k in keys_map}


def normalize_remove_columns(columns, keys_map):
    """Helper to remove columns from result

    Args
        columns (iter[str]): Iterable of column names.
        keys_map (dict): dict where keys are whitelisted input and value
        are attribute name of data transfer objects.

    Returns
        list: List of column names (attribute) removed from result to
        display.
    """
    if not columns:
        return None
    return [keys_map[column] for column in columns if column in keys_map]
