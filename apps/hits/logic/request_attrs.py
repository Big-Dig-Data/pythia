from core.exceptions import BadRequestError

START_DATE_PARAM = 'start_date'
END_DATE_PARAM = 'end_date'


def val_to_int_or_bad_request(inp):
    """
    Converts input to integer or raise BadRequestError
    """
    if inp is None:
        return inp
    try:
        return int(inp)
    except ValueError:
        raise BadRequestError(f'Invalid value "{inp}" - must be integer')


def date_filter_from_request(
    request, start_date_param=START_DATE_PARAM, end_date_param=END_DATE_PARAM
) -> dict:
    """
    Takes a request and return a dictionary suitable to define a filter on date attribute.
    """
    out = {}
    start_date = request.query_params.get(start_date_param)
    if start_date:
        out['date__gte'] = start_date
    end_date = request.query_params.get(end_date_param)
    if end_date:
        out['date__lte'] = end_date
    return out
