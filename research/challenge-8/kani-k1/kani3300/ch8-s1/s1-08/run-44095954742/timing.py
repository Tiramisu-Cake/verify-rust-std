"""Per-harness descriptive comparison; missing values and censoring stay explicit."""
import math
import statistics


def duration(value):
    return value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None


def measure(old, new, expected, compatible, limit):
    def resource(harness):
        value = harness.get('resources')
        return duration(value.get('verification_time_s')) if isinstance(value, dict) else None
    a, b = resource(old), resource(new)
    ao, bo = old.get('outcome'), new.get('outcome')
    ao = ao if isinstance(ao, dict) else {}
    bo = bo if isinstance(bo, dict) else {}
    timeout = 'TIMEOUT' in (ao.get('kind'), bo.get('kind'))
    completed = all(o.get('kind') == 'COMPLETED' and o.get('verdict') in ('SUCCESS', 'FAILURE')
                    for o in (ao, bo))
    cohort = 'UNKNOWN'
    if timeout:
        cohort = 'TIMEOUT_CENSORED'
    elif completed:
        if ao['verdict'] == bo['verdict'] == 'SUCCESS':
            cohort = 'SUCCESS_SUCCESS'
        elif ao['verdict'] == bo['verdict'] == 'FAILURE' and expected == 'DETECTED':
            cohort = 'INTENDED_FAILURE_FAILURE'
        else:
            cohort = 'VERDICT_CHANGED' if ao['verdict'] != bo['verdict'] else 'OTHER_COMPLETED'
    exact = compatible and completed and a is not None and b is not None
    bound = (limit / a if compatible and bo.get('kind') == 'TIMEOUT' and
             ao.get('kind') == 'COMPLETED' and a is not None and a > 0 and
             duration(limit) is not None else None)
    return {'s107_raw_verification_time_s': a, 's108_raw_verification_time_s': b,
            's107_outcome': ao, 's108_outcome': bo, 'cohort': cohort,
            'delta_s': b - a if exact else None,
            'completed_ratio_s108_over_s107': b / a if exact and a > 0 else None,
            'ratio_status': ('KNOWN' if exact and a > 0 else
                             'UNKNOWN_ZERO_BASELINE' if exact and a == 0 else
                             'CENSORED' if timeout else 'UNKNOWN_INCOMPATIBLE_OR_MISSING'),
            'censoring': {'observed_s107_elapsed_s': a, 'observed_s108_elapsed_s': b,
                          's108_cutoff_s': limit, 'completion_time_ratio_lower_bound': bound,
                          'interpretation': 'Conditional lower bound if verification eventually completes; no exact slowdown'}
                         if timeout else None}


def summarize(rows):
    result = {}
    for cohort in sorted({r['cohort'] for r in rows}):
        members = [r for r in rows if r['cohort'] == cohort]
        pairs = [r for r in members if r['compatible'] and r['delta_s'] is not None]
        ratios = [r['completed_ratio_s108_over_s107'] for r in pairs
                  if r['completed_ratio_s108_over_s107'] is not None]
        positive = [x for x in ratios if x > 0]
        result[cohort] = {'rows': len(members), 'comparable_completed_pairs': len(pairs),
                          'known_ratios': len(ratios),
                          'ratio_min': min(ratios) if ratios else None,
                          'ratio_median': statistics.median(ratios) if ratios else None,
                          'ratio_max': max(ratios) if ratios else None,
                          'ratio_geomean': math.exp(sum(map(math.log, positive)) / len(positive))
                                           if positive and len(positive) == len(ratios) else None,
                          's107_completed_seconds_sum': sum(r['s107_raw_verification_time_s'] for r in pairs),
                          's108_completed_seconds_sum': sum(r['s108_raw_verification_time_s'] for r in pairs)}
        if not pairs:
            result[cohort]['s107_completed_seconds_sum'] = None
            result[cohort]['s108_completed_seconds_sum'] = None
    return result
