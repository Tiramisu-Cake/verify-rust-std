"""Pure saved-data helpers; no subprocess, extraction, compiler or Cloud imports."""
import re


def first_diagnostic(log):
    """A review hint, never automatic causal or target attribution."""
    for number, line in enumerate(log.splitlines(), 1):
        if re.search(r"error(?:\[|:)|panicked at|UnknownProcedure|unsupported", line, re.I):
            return {"line": number, "text": line[:2000], "attribution": "UNREVIEWED"}
    return None


def audit(commands, failed_stage, inventory):
    target = commands.get("target", {})
    attempted = bool(target)
    collected = (attempted and target.get("returncode") is not None and
                 not target.get("timed_out") and target.get("returncode", -1) >= 0 and
                 inventory is True and failed_stage is None)
    return {"accepted": False, "verification_accepted": False,
            "proof_status": "NOT_RUN", "target_admission": "MANUAL_REVIEW_REQUIRED" if attempted else "NOT_RUN",
            "classification": "INCONCLUSIVE", "diagnostic_complete": collected,
            "failed_stage": failed_stage,
            "first_blocker": (failed_stage if failed_stage else
                              "frontend diagnostic requires source/span review" if target.get("returncode") else
                              "generated resource/linking obligations unproved" if attempted else "target not run"),
            "commands": commands}
