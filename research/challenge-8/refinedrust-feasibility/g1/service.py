"""Pure admission classifiers; no compiler, Git, network or process imports."""
import re


IDENTITY_KEYS = ('build_id', 'source_sha', 'tool_sha', 'compiler_sha', 'proof_sha',
                 'infra_sha', 'image_digest', 'profile')


def check_identity(actual, expected):
    if set(expected) != set(IDENTITY_KEYS):
        raise ValueError('external expected identity must specify all keys')
    for key in IDENTITY_KEYS:
        if not expected[key] or actual.get(key) != expected[key]:
            raise ValueError('identity mismatch: ' + key)
    for key in ('source_sha', 'tool_sha', 'compiler_sha', 'proof_sha', 'infra_sha'):
        if not re.fullmatch('[0-9a-f]{40}', actual[key]):
            raise ValueError('non-exact commit: ' + key)
    if not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}', actual['image_digest']):
        raise ValueError('image must be an immutable repository digest')


def normal_completion(stage):
    """A shell exit status is usable only after an uninterrupted process exit."""
    code = stage.get('returncode')
    return (type(code) is int and 0 <= code < 128 and
            stage.get('timed_out') is False and
            stage.get('signaled') is False)


def negative_unknown_procedure(exit_code, text, *, timed_out=False, signaled=False):
    # Stock Message::UnknownProcedure Display text, tied to our own DefId path.
    # A Rust setup failure elsewhere must not earn negative credit.
    pattern = r'Unknown procedure:\s*DefId\([^\n]*g1_unregistered[^\n]*\)'
    if (type(exit_code) is not int or not 0 < exit_code < 128 or timed_out or signaled or
            re.search(r'error\[E\d+\]|panicked at|signal: 9', text)):
        return False
    errors = re.findall(r'^error:\s*(.*)$', text, re.MULTILINE)
    intended = [e for e in errors if re.fullmatch(pattern, e)]
    other = [e for e in errors if not re.fullmatch(pattern, e) and
             not re.fullmatch(r'aborting due to 1 previous error', e) and
             not e.startswith('could not compile `rr-g1-n1`')]
    return len(intended) == 1 and not other



def classify(stages, controls, correspondence):
    result = {'verification_accepted': False, 'proof_status': 'NOT_RUN'}
    for name in ('inputs', 'compiler'):
        if name not in stages:
            return dict(result, verdict='INCONCLUSIVE', blocker=name + ': NOT_RUN')
        if stages[name].get('ok') is not True:
            if name == 'compiler' and stages[name].get('interrupted') is True:
                return dict(result, verdict='INCONCLUSIVE', blocker='compiler preflight interrupted')
            return dict(result, verdict='STOP', blocker=name + ': identity/environment mismatch')
    if not all(controls.get(k) is True for k in ('P0', 'N1', 'N2')):
        return dict(result, verdict='INCONCLUSIVE', blocker='admission control missing or failed')
    native = stages.get('native', {})
    if not normal_completion(native) or native.get('returncode') != 0:
        verdict = ('STOP' if normal_completion(native) and
                   native.get('compiler_rejection') is True else 'INCONCLUSIVE')
        return dict(result, verdict=verdict, blocker='native core compatibility: ' + str(native.get('returncode', 'NOT_RUN')))
    target = stages.get('p1', {})
    if not normal_completion(target):
        return dict(result, verdict='INCONCLUSIVE', blocker='P1 NOT_RUN/timeout/signal')
    if target['returncode'] != 0:
        # Do not infer target specificity merely from a generic exporter error.
        return dict(result, verdict='INCONCLUSIVE', blocker='P1 failed; selected-callee/operation attribution requires raw-log review')
    verdict = correspondence.get('verdict', 'INCONCLUSIVE')
    if verdict not in ('PASS', 'INCONCLUSIVE', 'STOP'):
        verdict = 'INCONCLUSIVE'
    return dict(result, verdict=verdict, blocker=correspondence.get('blocker', 'see correspondence checks'))


def validate_source_metadata(receipt, expected_commit, originals):
    if receipt.get('source_commit') != expected_commit:
        raise ValueError('source commit mismatch')
    for label, spec in receipt.get('sources', {}).items():
        if label not in originals or spec.get('original_sha256') != originals[label]:
            raise ValueError('original source SHA256 mismatch: ' + label)
    return set(receipt.get('sources', {})) == set(originals)


def negative_source_certificate(fixture, expected_commit, originals):
    try:
        validate_source_metadata(fixture, expected_commit, originals)
    except ValueError as exc:
        return str(exc) == 'original source SHA256 mismatch: smallsort'
    return False


def positive_unit_definition(text):
    matches = list(re.finditer(r'^Program Definition g1_p0_def\b[^\n]*: function :=', text, re.MULTILINE))
    if len(matches) != 1:
        return False
    end = text.find('Final Obligation.', matches[0].end())
    if end < 0:
        return False
    body = text[matches[0].end():end]
    return (not re.search(r'^Program Definition\b|Final Obligation\.', body, re.MULTILINE) and
            re.search(r'\|\}\.[ \t\r\n]*$', body) is not None and
            'f_code :=' in body and 'f_init :=' in body)
