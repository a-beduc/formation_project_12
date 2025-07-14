def map_accepted_key(accepted_keys):
    return {
        acc_key: used_key for used_key, acc_keys
        in accepted_keys.items()
        for acc_key in acc_keys
    }


def clean_input_fields(fields):
    if not fields:
        return None
    return {f[0].lower(): f[1] for f in fields}


def clean_sort(sort):
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
    if not sort:
        return None
    return tuple([(keys_map.get(keyword, keyword), is_desc)
                  for keyword, is_desc in sort if keyword in keys_map])


def normalize_fields(fields, keys_map):
    if not fields:
        return None
    return {keys_map.get(k, k): v for k, v in fields.items() if k in keys_map}


def normalize_remove_columns(columns, keys_map):
    if not columns:
        return None
    return [keys_map[column] for column in columns if column in keys_map]

