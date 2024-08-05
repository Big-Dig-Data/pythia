from bookrank.models import (
    Publisher,
    Author,
    Language,
    SubjectCategory,
    OwnerInstitution,
    WorkCategory,
)
from core.exceptions import BadRequestError
from hits.logic.request_attrs import val_to_int_or_bad_request


class RequestParameterExtractor:
    topic_type_to_explicit_topic = {
        'publisher': Publisher,
        'author': Author,
        'language': Language,
        'psh': SubjectCategory,
        'owner': OwnerInstitution,
        'work-type': WorkCategory,
    }
    ORDERING_TYPES_RAW = (  # (param name, db query param name)
        ('score', 'score'),
        ('score_size_ratio', 'ratio'),
        ('work_count', 'work_count'),
        ('absolute_growth', 'absolute_growth'),
        ('relative_growth', 'relative_growth'),
        ('new_works_acquisition_score', 'new_works_acquisition_score'),
    )
    ORDERING_TYPES_REMAP = dict(ORDERING_TYPES_RAW)
    ORDERING_TYPES = [ot[0] for ot in ORDERING_TYPES_RAW]
    ORDER_BY_PARAM = 'order_by'
    MIN_TOPIC_SIZE_FILTER_PARAM = 'min_topic_size'
    OWNER_INSTITUTION_FILTER_PARAM = 'owner_inst'
    YOP_TO_FILTER_PARAM = 'yop_to'
    YOP_FROM_FILTER_PARAM = 'yop_from'
    WORK_CATEGORY_FILTER_PARAM = 'work_category'
    LANG_FILTER_PARAM = 'lang'
    WORK_FILTER_VALUE_PARAM = 'filter_value'
    WORK_FILTER_TYPE_PARAM = 'filter_type'
    HIT_TYPE_PARAM = 'hit_type'

    @classmethod
    def _extract_hit_type_filter(cls, request) -> dict:
        out = {}
        hit_type = request.query_params.get(cls.HIT_TYPE_PARAM)
        if hit_type:
            out['typ_id'] = hit_type
        return out

    @classmethod
    def _extract_work_filter(cls, request) -> dict:
        """
        If a filter should be used on works, this is where we extract it. The filter may
        be on the Work model directly or on the related Topic models - e.g. only Works that
        are related to language 'cze' might be requested
        :param request:
        :return:
        """

        def year_to_int_or_bad_request(inp):
            if inp is None:
                return inp
            try:
                return int(inp)
            except ValueError:
                raise BadRequestError(f'Invalid value "{inp}" for year - must be integer')

        ret = {}
        # language
        lang_value = request.query_params.get(cls.LANG_FILTER_PARAM)
        if lang_value is not None:
            ret['lang__name'] = lang_value
        # YOP
        yop_from = year_to_int_or_bad_request(request.query_params.get(cls.YOP_FROM_FILTER_PARAM))
        yop_to = year_to_int_or_bad_request(request.query_params.get(cls.YOP_TO_FILTER_PARAM))
        if yop_from:
            ret['end_yop__gte'] = int(yop_from)
        if yop_to:
            ret['start_yop__lte'] = int(yop_to)
        # owner organization
        owner_org = request.query_params.get(cls.OWNER_INSTITUTION_FILTER_PARAM)
        if owner_org:
            ret['owner_institution_id'] = val_to_int_or_bad_request(owner_org)
        # work category
        work_cat = request.query_params.get(cls.WORK_CATEGORY_FILTER_PARAM)
        if work_cat:
            ret['category'] = val_to_int_or_bad_request(work_cat)
        # free-style topic based filter
        topic_filter_type = request.query_params.get(cls.WORK_FILTER_TYPE_PARAM)
        topic_filter_value = request.query_params.get(cls.WORK_FILTER_VALUE_PARAM)
        if (topic_filter_type is None) ^ (topic_filter_value is None):
            # one is true, other not
            raise BadRequestError(
                f'You must provide both "{cls.WORK_FILTER_VALUE_PARAM}" and '
                f'"{cls.WORK_FILTER_TYPE_PARAM}" params (or neighter)'
            )
        if topic_filter_type:
            ret.update({topic_filter_type: topic_filter_value})
        return ret

    @classmethod
    def _extract_post_aggregation_filter(cls, request) -> dict:
        out = {}
        min_size = request.query_params.get(cls.MIN_TOPIC_SIZE_FILTER_PARAM)
        if min_size:
            min_size = val_to_int_or_bad_request(min_size)
            out['work_count__gte'] = min_size
        return out
