"""Bind final review files to exact audited inputs and targeted execution records."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent.parent
G0 = Path('/root/verify-rust-std-kani3300-g0')
PKG = OUT.parent / 's3-1-r2'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def write(name, doc):
    path = OUT / name
    assert not path.exists(), path
    path.write_text(json.dumps(doc, indent=2) + '\n')


def main():
    audit = load(OUT / 'INPUT-AUDIT.json')
    assert audit['status'] == 'PASS'
    pins = load(PKG / 'PINS.json')
    candidate = load(OUT / 'tests/candidate-execution.json')
    frozen = load(OUT / 'tests/frozen-execution.json')
    source = load(OUT / 'tests/source-preflight.json')
    assert candidate['exit_code'] == 0 and frozen['exit_code'] == 1
    assert source['state'] == 'STATIC_PASS'
    assert source['request_sha256'] == pins['request_sha256']
    assert source['control_sha'] == pins['control']['sha']
    for label, rec in [('candidate', candidate), ('frozen', frozen)]:
        for stream in ('stdout', 'stderr'):
            assert sha(OUT / 'tests' / (label + '.' + stream + '.txt')) == rec[stream + '_sha256']
    assert 'Ran 23 tests' in (OUT / 'tests/candidate.stderr.txt').read_text()
    assert 'recorded worker binary drift: before' in (OUT / 'tests/frozen.stderr.txt').read_text()
    for role in ('source', 'tool'):
        old = load(PKG / 'inputs/frozen-package/PINS.json')[role]
        for key in ('sha', 'tree', 'parent'):
            assert old[key] == pins[role][key]
    identities = {key: pins[key] for key in ('control', 'source', 'tool', 'task', 'intake',
                  'frozen_control', 'frozen_package', 'frozen_review', 'spent_GO',
                  'request_sha256', 'workflow_sha256', 'fixture_sha256')}
    identities['package'] = audit['package']
    identities['review_task_file'] = 'inputs/package/inputs/TASK-W14.md'
    write('EXACT-INPUTS.json', identities)
    write('FINDINGS.json', dict(disposition='APPROVE', package=audit['package'],
        control=pins['control']['sha'], findings=[], blockers=[],
        prior_findings=dict(R14_01='CLOSED in27040; inherited through exact bytes',
                            R14_02='CLOSED in27040; inherited through exact bytes'),
        historical_physical_identity='UNKNOWN', qualification=0, proof_credit='NONE',
        root_GO='NEW_ROOT_DECISION_REQUIRED; NOT_ISSUED_BY_REVIEWER'))
    validation = dict(state='PASS_STATIC_SYNTHETIC_ONLY', candidate=candidate,
        targeted_tests=23, independent_tests=3, inherited_author_tests_executed=20,
        independent_matrix=dict(same_sha_path_mutations_rejected=48, shape_error_mutations_rejected=12),
        frozen=frozen, frozen_result='EXPECTED_DISTINGUISHING_REJECTION', source_preflight=source,
        author_final_validate=audit['checks']['author_final_validate'],
        final_validate_rerun=False, native_compile_proof_fit='NOT_RUN', CI='NOT_RUN',
        qualification=0, proof_credit='NONE', independent_B1_B2='NONE')
    write('VALIDATION.json', validation)
    write('tests/REVIEWER-TOOLING.json', dict(
        preliminary_display_notes=[
            'An exploratory display helper assumed ANCESTRY.json was a dict; it is a list. AttributeError affected display only; the saved audit handles its actual shape and passed on first execution.',
            'Exploratory rg used nonexistent test_s3_provenance.py and a G0-relative path in the control worktree; corrected reads located the actual test_s3_repair.py and G0 review paths.'
        ], candidate_changes=False, failed_tests=0, proof_credit='NONE'))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write('CHECKPOINT.json', dict(status='APPROVE_NEW_ROOT_GO_DECISION_ONLY', runtime='Codex high/FastOFF; no subagents/model/settings changes',
        package=audit['package'], task=pins['task'], control=pins['control'], source=pins['source'], tool=pins['tool'],
        claims=[dict(claim='Future writer canonical path before E0; strict guards and legacy unchanged',
                     assurance='exact byte delta plus independent real-file synthetic service checks',
                     evidence=['INPUT-AUDIT.json', 'tests/candidate-execution.json', 'tests/frozen-execution.json', 'REPORT.md'])],
        blocker=None, open=['Separate root newGO decision', 'Coordinator owns prospective12/17',
                           'Native compile/proof/fit remains NOT_RUN', 'Inherited general proof gaps unchanged'],
        historical='STOPPED/prefix0/firstrowINTERRUPTED-UNKNOWN/later8NOT_RUN/deferred8NOT_SELECTED/8U; physical identityUNKNOWN',
        accounting_reference='31/31+11/17=42/48 unchanged; no agent action',
        proof_obligations_closed=0, qualification=0, proof_credit=0,
        next='Root newGO decision only after this exact APPROVE; no dispatch authorized here',
        closure_reason='All authorized path delta review, exact-input audit, distinguishing regressions, static source gates and timing audit completed. Source/tool changes, native/CI execution and GO/dispatch belong outside this review scope.',
        finalized_utc=now))
    (OUT / 'CURRENT-TASK.md').write_text(
        '# S3-1-review-r2 / SAME14\n\nRuntime: Codex high/FastOFF; no subagents or settings changes.\n\n'
        'APPROVE exact package008fcb7705e658643582668ebfabb5f2e340e95d; '
        'controlcb63033ffcde918f4341146e56373476b8eeb569. Zero blocking findings.\n\n'
        '23 targeted tests PASS; frozen fc29 workflow control rejects as expected; independent source preflight STATIC_PASS. '
        'Author once-only final Validate192PASS/534.581739554s/margin2.020271027x audited, not rerun.\n\n'
        'Next: separate root newGO decision only. Coordinator owns prospective12/17. '
        'Native compile/proof/fit and CI NOT_RUN; proofcredit0. No launch/push/ledger/budget action.\n')
    (OUT / 'HANDOFF.md').write_text(
        '# SAME14 — APPROVE; new root GO decision only\n\n'
        'Exact package `008fcb7705e658643582668ebfabb5f2e340e95d`, task '
        '`e2ea94d04c9d9977ac9cde891c13a73ee65f2ec4`. Full inputs in EXACT-INPUTS.json; '
        'review starts REPORT.md, FINDINGS.json, INPUT-AUDIT.json and VALIDATION.json.\n\n'
        'CONTROL `cb63033ffcde918f4341146e56373476b8eeb569`, tree '
        '`287ebfc7b0bf95428a07cfe1b89ba1608aef3ff7`, sole parent '
        '`9e14e033f9ee31522b571c127609dcdff76d230b`; source513341/tool0aac frozen exact. '
        'Request SHA256 `efbc150280f5f9641c9e8b48fb4486122ae8c3cfa318f78a42486394e1de7656`; '
        'workflow SHA256 `8d5fd03476d3d7666692cc7267d3fe598a0007c54ec6576de3538cef434ac709`.\n\n'
        'Zero blockers in the path delta. Canonical tool input precedes E0 and is reused in actual worker argv. '
        'Strict path/digest/state/error checks and legacy are unchanged. Independent23 targeted tests PASS, '
        'including48 equal-SHA path rejections/12 malformed evidence rejections, alias retarget afterE0, '
        'entry missing-binary no-launch, real-writer/hash/prefix/portable and actual killed-Python-worker recovery. '
        'Exact frozenfc29 workflow control rejects as expected. Independent static source preflight PASS.\n\n'
        '65 package files/64 manifest hashes,18 dependencies,4 patch replays,7/5/2 ancestry and6 maps MATCH. '
        'Author final Validate once-only192PASS/534.581739554s/margin2.020271027x is audited, not rerun or independently witnessed.\n\n'
        'Next: root may decide a NEW GO for these identities only; reviewer issues none. OldGO9929 spent. '
        'Coordinator separately owns prospective12/17 after root consent. Native compile/proof/fit/fullnative runner/CI '
        'NOT_RUN, qualification/proofcredit0/B1B2NONE. Historical STOPPED/prefix0/firstrowUNKNOWN/8laterNOT_RUN/8U '
        'and physicalidentityUNKNOWN retained; native literal observation only.31/31+11/17=42/48 unchanged.\n\n'
        'No candidate/source edits, compiler/Cargo/rustc/rustfmt/Kani/CBMC/expansion/verifier, CI, push, PR/issues/comments, '
        'ledger/budget/reservation, rawlogs/archives/GCS, subagents or model/settings changes. High/FastOFF retained. '
        'Only this new review directory is committed with [skip ci]. The immutable review is the commit containing its MANIFEST.sha256; '
        'full commit SHA is supplied in completion.\n')
    manifest = OUT / 'MANIFEST.sha256'
    files = sorted(path for path in OUT.rglob('*') if path.is_file() and path != manifest)
    assert not manifest.exists()
    manifest.write_text(''.join(sha(path) + '  ' + str(path.relative_to(OUT)) + '\n' for path in files))
    print(json.dumps(dict(state='SEALED', disposition='APPROVE', files=len(files) + 1,
                          manifest_entries=len(files), manifest_sha256=sha(manifest))))


if __name__ == '__main__':
    main()
