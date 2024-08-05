def prefix_query_filter(filter_dict: dict, prefix: str) -> dict:
    return {prefix + key: value for key, value in filter_dict.items()}
