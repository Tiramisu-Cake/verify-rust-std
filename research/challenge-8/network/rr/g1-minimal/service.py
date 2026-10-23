"""Pure saved-data helpers; no subprocess, extraction, compiler or Cloud imports."""
import re


def online_freeze(freeze, submitted_image):
    """Validate the owner-authorized online image pins; never grants proof credit."""
    prefix = 'us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools/refinedrust-g1@sha256:'
    if (not isinstance(freeze, dict) or freeze.get('schema') != 'rr-g1-online-freeze-v2' or
            not isinstance(freeze.get('image_digest'), str) or
            not re.fullmatch(re.escape(prefix) + '[0-9a-f]{64}', freeze['image_digest']) or
            freeze['image_digest'] != submitted_image):
        raise ValueError('online image freeze absent or submitted image mismatch')
    bins = freeze.get('binaries')
    paths = {'rustc': '/opt/rust/bin/rustc', 'cargo': '/opt/rust/bin/cargo',
             'cargo-refinedrust': '/opt/rr-bin/cargo-refinedrust',
             'refinedrust-rustc': '/opt/rr-bin/refinedrust-rustc'}
    if not isinstance(bins, dict):
        raise ValueError('online binary freeze missing')
    for name, path in paths.items():
        spec = bins.get(name)
        if (not isinstance(spec, dict) or spec.get('path') != path or
                not isinstance(spec.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', spec['sha256'])):
            raise ValueError('online binary freeze invalid: ' + name)
    if (freeze.get('cargo_home') != '/opt/g1-cargo' or
            freeze.get('rr_frontend_lock_sha256') != 'b66b9e281478be8263eab9ba210964cdd8f1db92535b7b81305f50dea03682aa' or
            not isinstance(freeze.get('image_receipt_sha256'), str) or
            not re.fullmatch('[0-9a-f]{64}', freeze['image_receipt_sha256'])):
        raise ValueError('online receipt/lock/Cargo path freeze invalid')
    return bins


def first_diagnostic(log):
    """A review hint, never automatic causal or target attribution."""
    for number, line in enumerate(log.splitlines(), 1):
        if re.search(r"error(?:\[|:)|panicked at|UnknownProcedure|unsupported", line, re.I):
            return {"line": number, "text": line[:2000], "attribution": "UNREVIEWED"}
    return None


def audit(commands, failed_stage, inventory):
    target = commands.get("target", {}) if isinstance(commands, dict) else {}
    if not isinstance(target, dict):
        target = {}
    attempted = bool(target)
    collected = (attempted and type(target.get("returncode")) is int and
                 target.get("timed_out") is False and 0 <= target['returncode'] <= 255 and
                 inventory is True and failed_stage is None)
    return {"accepted": False, "verification_accepted": False,
            "proof_status": "NOT_RUN", "target_admission": "MANUAL_REVIEW_REQUIRED" if attempted else "NOT_RUN",
            "classification": "INCONCLUSIVE", "diagnostic_complete": collected,
            "failed_stage": failed_stage,
            "first_blocker": (failed_stage if failed_stage else
                              "frontend diagnostic requires source/span review" if target.get("returncode") else
                              "generated resource/linking obligations unproved" if attempted else "target not run"),
            "commands": commands}
