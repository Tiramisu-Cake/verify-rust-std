#!/usr/bin/env python3
"""Compact classification.json dispatch receipt; no proof/tool execution."""
import json
from pathlib import Path

STATUSES = {'NOT_RUN_PREREQUISITE_FAILED', 'DISPATCHED', 'CAMPAIGN_RETURNED',
            'INCONCLUSIVE_CAMPAIGN_EXCEPTION'}


def record(evidence: Path, *, status: str, binding: dict,
           prerequisites: dict, details: dict | None = None) -> dict:
    if status not in STATUSES:
        raise ValueError('unknown first-comparator dispatch status')
    ready = bool(prerequisites) and all(value is True for value in prerequisites.values())
    if (status == 'NOT_RUN_PREREQUISITE_FAILED') == ready:
        raise ValueError('dispatch status contradicts prerequisite receipt')
    if not all(binding.get(key) for key in ('proof_sha', 'profile', 'profile_sha256', 'tool_commit')):
        raise ValueError('dispatch source/profile identity missing')
    row = {'case': 'first_comparator_campaign_dispatch', 'profile': binding['profile'],
           'classification': status, 'accepted': False, 'proof_credit': False,
           'source_binding': binding, 'prerequisites': prerequisites,
           'reason': ('First-comparator invocation skipped because prerequisite gate failed'
                      if not ready else 'Dispatch observation, not target proof'),
           'details': details or {}}
    directory = Path(evidence) / 'first-comparator-dispatch' / 'cases' / 'dispatch'
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'classification.json').write_text(json.dumps(row, indent=2) + '\n')
    return row
