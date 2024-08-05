from collections import Counter
from typing import Iterable, Optional, Callable, Any

from bookrank.logic.static_score import YEARS
from ..models import Candidate

trivial_weights = {'authors': 1.0, 'languages': 1.0, 'subjects': 1.0, 'publisher': 1.0}


def update_candidates_static_scores(
    candidates: Optional[Iterable[Candidate]] = None,
    batch_size=10000,
    callback: Optional[Callable[[Any, int, dict], None]] = None,
    score_type: str = 'static',
):
    """
    if `callback` is given, it will be called after each batch has been processed with the
    following arguments:

    1/ the currently processed year
    2/ the number of processed records for that year
    3/ overall stats as a Counter/dict
    """
    stats = Counter()
    if not candidates:
        candidates = Candidate.objects.all()
    for year in ['all', *YEARS]:
        to_save = []
        for i, candidate in enumerate(
            candidates.annotate_score_lowlevel(trivial_weights, year, score_type).iterator()
        ):
            # for some reason, None sometimes creeps into the scores, even though it should not,
            # so we `or` it with 0.0 to make sure only numbers are used
            scores = {
                'authors_score': candidate.authors_score or 0.0,
                'languages_score': candidate.languages_score or 0.0,
                'subjects_score': candidate.subjects_score or 0.0,
                'publisher_score': candidate.publisher_score or 0.0,
            }
            key = f'score_{year}'
            old_scores = getattr(candidate, f'{score_type}_scores')
            if old_scores.get(key) != scores:
                old_scores[key] = scores
                to_save.append(candidate)
                stats['updated'] += 1
            else:
                stats['unchanged'] += 1
            if i and i % batch_size == 0:
                Candidate.objects.bulk_update(to_save, [f'{score_type}_scores'])
                to_save = []
                if callback:
                    try:
                        callback(year, i, stats)
                    except Exception:
                        pass  # we ignore any errors in the callback function
        Candidate.objects.bulk_update(to_save, [f'{score_type}_scores'])
    return stats
