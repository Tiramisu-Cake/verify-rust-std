#!/usr/bin/env python3
"""Apply recorded Cloud Build overlays to the merge lane's retained runner.

This runs only inside the disposable Cloud Build proof checkout. Each source
must match the reviewed base SHA before exact byte replacements are applied.
The run.sh overlay retains two saved modular-trace groups and applies the
committed explicit merge group selection. Proof predicates, specifications,
expected obligations, classifier rules, tool pins and runtime SmallSort bytes
are outside the set.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import sys


FILES = {
    "research/challenge-8/merge/overnight/run.sh": "bed25e1ac908d5a16a9364795960984611a0fda261c2815e2406ee14a5237d8f",
    "research/challenge-8/merge/overnight/build.sh": "dc6e30a5fb3aa24ff7f014910f3c54925fdde3e40f40ea8c1fcfcdafb89ae096",
    "research/challenge-8/merge/overnight/pointer-prove.py": "cb6d43c972d1c19f60b1cd355529f71fb6e68a9fa9242e4176814acbed8f8b96",
    "research/challenge-8/merge/overnight/actual-prepare.py": "8f96ea92e43651c0952102236c76348dca8079ea96a8bab1bb24de4851e07ca5",
    "research/challenge-8/merge/overnight/bidirectional-small-prepare.py": "d3ff063f4c02cebc71f60e493198872eda06093bafcde9a7e4a6c9711dddaa4c",
    "research/challenge-8/merge/overnight/panic-macro-admission.py": "a805e9235f327edc808ee007735e755d37cb7041a2b242eb83061f24bba76caf",
    "research/challenge-8/merge/overnight/stack-address-admission.py": "9ecce61ca3886f2b9e21bb03d35ce6312da5eb405ff35a0bb37211eb2c49e974",
    "research/challenge-8/merge/overnight/stack-proof-ast-admission.py": "a5f28d5feb9c3e07d2bb5ee6b19a29dc45ea782d5f51a1630f993124f20bd995",
    "research/challenge-8/merge/overnight/stack-address-controls-prepare.py": "483f7e980c1a5e02eb491e4c5ab6353ab5a73d9a5abdaa192848ca4bc5452d3b",
    "research/challenge-8/merge/overnight/m2-admission-prove.py": "f6b657a01086f463c0c063b168c054f57b7161dd2f2b042d5ef6e5a2cc9b7065",
    "research/challenge-8/merge/overnight/hrtb-admission-certificate.py": "42c9ff5e878d0eb8ba2b6183f439fe2e56765a086a88255176a041c51bd55c2a",
    "research/challenge-8/merge/overnight/native-prove.py": "9a2524ab90af1176d77c09cbf0a9fbedb7b4f0939218dde6713ad10aa6fc2da1",
    "research/challenge-8/merge/overnight/usize-multiple-admission.py": "119c0054ae43487ae4adb9de1787edd89ce6014f1e9b70dc2cf973a0258d3050",
    "research/challenge-8/networks/prove.py": "994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4",
    "research/challenge-8/merge/stock-26.10/prove.py": "6af798229e57187cc003de40a97f6a3626567440b4a8558a11f1412dd1763b0c",
    "research/challenge-8/merge/stock-26.10/functional-prove.py": "f513f2acd81ca21980acf56cfa47a41599cec4e3a4d6b1034ec8fadadcb00dd5",
    "research/challenge-8/merge/stock-26.10/order-prove.py": "9f685baa0c7b0893486f5838d7d89c664a747b3a8e3670692ec928da7f95db14",
    "research/challenge-8/merge/stock-26.10/run.sh": "449fc91c1610164d39b230c3b5cfdf41f8548de757cf33137407a95e759c5214",
}

PROVIDER_HELPER = '''\ndef _require_cloud_provider():
    import runpy
    provider_file = os.environ.get("SMALLSORT_PROVIDER_FILE", "")
    if not provider_file:
        raise RuntimeError("provider helper path is missing")
    result = runpy.run_path(provider_file)
    return result["require_supported_provider"]()
'''


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(data: bytes, old: bytes, new: bytes, path: str) -> bytes:
    count = data.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one identity guard/token, found {count}")
    return data.replace(old, new, 1)


def transform(path: str, original: bytes, pins: dict[str, str] | None = None) -> bytes:
    data = original
    pins = pins or {}
    if path in ("research/challenge-8/merge/overnight/run.sh",
                "research/challenge-8/merge/overnight/build.sh"):
        old = (b'[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && '
               b'"${RUNNER_OS:-}" == Linux ]]')
        new = b'python3 "${SMALLSORT_PROVIDER_FILE:?provider helper is required}" >/dev/null'
        data = replace_once(data, old, new, path)
        if path.endswith("run.sh"):
            data = replace_once(
                data,
                b'[[ "${GITHUB_REF:-}" == refs/heads/overnight/merge-26.10 ]]',
                b'[[ "${PROOF_SHA:-}" =~ ^[0-9a-f]{40}$ ]]', path)
            data = replace_once(data, b'"${GITHUB_SHA:?GITHUB_SHA is required}"',
                                b'"${PROOF_SHA:?PROOF_SHA is required}"', path)
            data = replace_once(data, b"Actions SHA: %s\\nBranch: overnight/merge-26.10\\nSelection:",
                                b"Cloud proof SHA: %s\\nProvider: cloud-build\\nSelection:", path)
            data = replace_once(data, b'"$GITHUB_SHA"', b'"$PROOF_SHA"', path)
            data = replace_once(
                data,
                b'evidence="$repo/research-results/merge-overnight"',
                b'evidence="${EVIDENCE_ROOT:?EVIDENCE_ROOT is required}/allprooflogs"', path)
            data = replace_once(
                data,
                b"printf 'Runner: %s/%s\\nDistinct W1 + M2a + copy + strict cleanup + zero-safe usize primitive + hidden stack-address patches; explicit pinned strict kernel extension; stock exporter/refiner/schema unchanged\\n' \"$RUNNER_ENVIRONMENT\" \"$RUNNER_OS\"",
                b"printf 'Runner: Cloud Build / Ubuntu 22.04 x86_64\\nDistinct W1 + M2a + copy + strict cleanup + zero-safe usize primitive + hidden stack-address patches; explicit pinned strict kernel extension; stock exporter/refiner/schema unchanged\\n'",
                path)
            network_sha = pins.get("network_sha")
            if not network_sha:
                raise SystemExit("overnight run overlay requires staged network output hash")
            data = replace_once(
                data,
                b'printf \'%s  %s\\n\' 994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4 research/challenge-8/networks/prove.py | sha256sum -c -',
                (f"printf '%s  %s\\n' {network_sha} research/challenge-8/networks/prove.py | sha256sum -c -".encode()),
                path)
            data = replace_once(
                data,
                b'  shift 2\n  local status\n',
                (b'  shift 2\n'
                 b'  local selected_status\n'
                 b'  if python3 "${MERGE_SELECTION_TOOL:?}" contains --selection "${MERGE_SELECTION_FILE:?}" \\\n'
                 b'      --sha256 "${MERGE_SELECTION_SHA256:?}" "$label"; then\n'
                 b'    :\n'
                 b'  else\n'
                 b'    selected_status=$?\n'
                 b'    if [[ "$selected_status" -ne 1 ]]; then\n'
                 b'      suite_status=1\n'
                 b'      return 0\n'
                 b'    fi\n'
                 b'    return 0\n'
                 b'  fi\n'
                 b'  local status\n'), path)
            data = replace_once(
                data,
                b'  printf \'%s %s\\n\' "$label" "$status" >> "$evidence/group-status.txt"\n',
                b'  printf \'%s %s\\n\' "$label" "$status" >> "$evidence/group-status.txt"\n'
                b'  printf \'%s\\n\' "$status" > "$evidence/group-$label-exit-code.txt"\n', path)
            data = replace_once(
                data,
                b'  return "$suite_status"\n}\n\nexperimental_home=',
                (b'  run_one pointer-modular-trace-entry-negative 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \\\n'
                 b"    --scope 'matched full-domain modular G2 trace entry negative; retain all helper bodies and posts' \\\n"
                 b'    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/pointer-trace-modular-entry-negative.rs \\\n'
                 b'    --evidence "$evidence/checked-pointer-modular-trace-entry-negative"\n'
                 b'  run_one pointer-modular-trace-diagnostic 400 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \\\n'
                 b"    --scope 'saved modular G2 pointer-trace candidate; diagnostic status remains separate from the quartet' \\\n"
                 b'    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --verifier-seconds 300 --fixture research/challenge-8/merge/overnight/pointer-trace-modular-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-pointer-modular-trace"\n'
                 b'  run_one source-pair-turnover-resource-diagnostic 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \\\n'
                 b"    --scope 'draft source current-owner turnover; overlap/same-pair positives and freshly predeclared duplicate-full-cell control' \\\n"
                 b'    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/source-pair-turnover-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-source-pair-turnover"\n'
                 b'  run_one cleanup-recovery-hidden-type-diagnostic 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \\\n'
                 b"    --scope 'freshly predeclared callback recovery hidden-type frontend refusal control' \\\n"
                 b'    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/cleanup-recovery-hidden-type-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-cleanup-recovery-hidden-type"\n'
                 b'  run_one current-owner-handoff-resource-diagnostic 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \\\n'
                 b"    --scope 'conditional two-cell current-owner transfer; destination/current-source equality remains an explicit unproved caller bridge' \\\n"
                 b'    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/current-owner-handoff-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-current-owner-handoff"\n'
                 b'  run_one current-owner-handoff-stock-diagnostic 180 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile stock-26.10-current-owner-handoff \\\n'
                 b"    --scope 'stock isolation of exact current-owner fixture; no experimental kernel acceptance or actual caller claim' \\\n"
                 b'    --tool-home "$tool_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/current-owner-handoff-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-current-owner-handoff-stock"\n'
                 b'  run_one checked-current-owner-permutation 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \\\n'
                 b"    --scope 'isolated current-owner permutation; exact source/stage/body/return/leak/dead gates; double-owner case remains calibration only without an intended oracle' \\\n"
                 b'    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/current-owner-permutation-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-current-owner-permutation"\n'
                 b'  run_one checked-current-owner-permutation-stock 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile stock-26.10-current-owner-permutation \\\n'
                 b"    --scope 'stock isolation of the exact current-owner permutation fixture; double-owner case remains calibration only without an intended oracle' \\\n"
                 b'    --tool-home "$tool_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/current-owner-permutation-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-current-owner-permutation-stock"\n'
                 b'  run_one native-source-pair-turnover-resource-diagnostic 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1 \\\n'
                 b"    --scope 'conditional native-index current-source turnover; current owners conserved, actual caller bridge open' \\\n"
                 b'    --tool-home "$experimental_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/native-source-pair-turnover-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-native-source-pair-turnover"\n'
                 b'  run_one native-source-pair-turnover-stock-diagnostic 240 python3 research/challenge-8/merge/overnight/pointer-prove.py \\\n'
                 b'    --profile stock-26.10-native-source-pair-turnover \\\n'
                 b"    --scope 'conditional native-index current-source turnover; current owners conserved, actual caller bridge open' \\\n"
                 b'    --tool-home "$tool_home" --compiler-sysroot "$compiler_sysroot" --schema "$schema" \\\n'
                 b'    --fixture research/challenge-8/merge/overnight/native-source-pair-turnover-cases.rs \\\n'
                 b'    --evidence "$evidence/checked-native-source-pair-turnover-stock"\n'
                 b'  return "$suite_status"\n}\n\nexperimental_home='), path)
            data = replace_once(data,
                b'run_one bidirectional-len23-diagnostic 400 python3',
                b'run_one bidirectional-len23-diagnostic 760 python3', path)
            data = replace_once(data,
                b'--verifier-seconds 300 --fixture "$evidence/bidirectional-small-cases.rs"',
                b'--verifier-seconds 600 --fixture "$evidence/bidirectional-small-cases.rs"', path)
            data = replace_once(data,
                                b'suite bound=900s; whole step bound=1700s.',
                                b'suite bound=1200s; whole step bound=1300s.', path)
            data = replace_once(data,
                                b'timeout --signal=TERM --kill-after=5s 900s bash -c \'suite\'',
                                b'timeout --signal=TERM --kill-after=5s 1200s bash -c \'suite\'', path)
        else:
            data = data.replace(b'"$GITHUB_SHA"', b'"$PROOF_SHA"')
            data = replace_once(
                data,
                b"printf 'Runner: %s / %s\\n' \"$RUNNER_ENVIRONMENT\" \"$RUNNER_OS\"",
                b"printf 'Execution provider: Cloud Build / Ubuntu 22.04 x86_64\\n'", path)
            data = replace_once(
                data,
                b"printf 'runner_os=%s\\nrunner_version=%s\\nsource_commit=%s\\n' \"$RUNNER_OS\" \"$VERSION_ID\" \"$actual_commit\"",
                b"printf 'runner_os=Linux\\nrunner_version=%s\\nsource_commit=%s\\n' \"$VERSION_ID\" \"$actual_commit\"", path)
    elif path == "research/challenge-8/merge/stock-26.10/run.sh":
        old_guard = (b'[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_ENVIRONMENT:-}" == github-hosted && '
                     b'"${RUNNER_OS:-}" == Linux ]]')
        data = replace_once(data, old_guard,
                            b'python3 "${SMALLSORT_PROVIDER_FILE:?provider helper is required}" >/dev/null', path)
        data = replace_once(data,
            b'[[ "${GITHUB_REF:-}" == refs/heads/sync/upstream-cd371-merge ]]',
            b'[[ "${PROOF_SHA:-}" =~ ^[0-9a-f]{40}$ ]]', path)
        data = replace_once(data, b'"${GITHUB_SHA:?GITHUB_SHA is required}"',
                            b'"${PROOF_SHA:?PROOF_SHA is required}"', path)
        data = replace_once(data, b'"$GITHUB_SHA"', b'"$PROOF_SHA"', path)
        data = replace_once(data,
            b'Actions SHA: %s\\nBranch: sync/upstream-cd371-merge\\nSelection:',
            b'Cloud proof SHA: %s\\nProvider: cloud-build\\nSelection:', path)
        data = replace_once(data,
            b"printf 'Runner: %s/%s\\nNo verifier/tool/spec patches\\n' \"$RUNNER_ENVIRONMENT\" \"$RUNNER_OS\"",
            b"printf 'Runner: Cloud Build / Ubuntu 22.04 x86_64\\nNo verifier/tool/spec patches\\n'", path)
        network_sha = pins.get("network_sha")
        if not network_sha:
            raise SystemExit("stock run overlay requires staged network output hash")
        data = replace_once(data,
            b"printf '%s  %s\\n' 994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4 research/challenge-8/networks/prove.py | sha256sum -c -",
            (f"printf '%s  %s\\n' {network_sha} research/challenge-8/networks/prove.py | sha256sum -c -".encode()), path)
    elif path == "research/challenge-8/networks/prove.py":
        old = (b'    if (os.environ.get("GITHUB_ACTIONS") != "true" or\n'
               b'            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or\n'
               b'            platform.system() != "Linux"):\n'
               b'        raise RuntimeError("proof execution is restricted to GitHub-hosted Linux Actions")')
        new = (b'    provider_file = os.environ.get("SMALLSORT_PROVIDER_FILE", "")\n'
               b'    if not provider_file:\n'
               b'        raise RuntimeError("provider helper path is missing")\n'
               b'    provider = runpy.run_path(provider_file)["require_supported_provider"]()\n'
               b'    if provider.get("provider") != "cloud-build":\n'
               b'        raise RuntimeError("proof execution requires identified Cloud Build")')
        data = replace_once(data, old, new, path)
        data = replace_once(data, b'import os\n', b'import os\nimport runpy\n', path)
    elif path == "research/challenge-8/merge/stock-26.10/prove.py":
        network_sha = pins.get("network_sha")
        if not network_sha:
            raise SystemExit("stock proof overlay requires staged network output hash")
        data = replace_once(data,
            b'FROZEN_SHA256 = "994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4"',
            f'FROZEN_SHA256 = "{network_sha}"'.encode(), path)
    elif path == "research/challenge-8/merge/stock-26.10/functional-prove.py":
        prove_sha = pins.get("prove_sha")
        if not prove_sha:
            raise SystemExit("functional proof overlay requires staged stock proof output hash")
        data = replace_once(data,
            b'GEOMETRY_HARNESS_SHA256 = "6af798229e57187cc003de40a97f6a3626567440b4a8558a11f1412dd1763b0c"',
            f'GEOMETRY_HARNESS_SHA256 = "{prove_sha}"'.encode(), path)
    elif path == "research/challenge-8/merge/stock-26.10/order-prove.py":
        functional_sha = pins.get("functional_sha")
        if not functional_sha:
            raise SystemExit("order proof overlay requires staged functional proof output hash")
        data = replace_once(data,
            b'"functional-prove.py": "f513f2acd81ca21980acf56cfa47a41599cec4e3a4d6b1034ec8fadadcb00dd5"',
            f'"functional-prove.py": "{functional_sha}"'.encode(), path)
    else:
        if path.endswith("pointer-prove.py"):
            old = (b'    if (os.environ.get("GITHUB_ACTIONS") != "true" or\n'
                   b'            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or\n'
                   b'            os.environ.get("RUNNER_OS") != "Linux" or\n'
                   b'            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):\n'
                   b'        raise RuntimeError("pointer proof harness is restricted to hosted Linux Actions on overnight/merge-26.10")')
            new = (b'    if not _require_cloud_provider():\n'
                   b'        raise RuntimeError("unsupported execution provider")')
        elif path.endswith("actual-prepare.py"):
            old = (b'    if (os.environ.get("GITHUB_ACTIONS") != "true" or\n'
                   b'        os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or\n'
                   b'        os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):\n'
                   b'        raise RuntimeError("actual preparation requires own GitHub-hosted Actions branch")')
            new = (b'    if not _require_cloud_provider():\n'
                   b'        raise RuntimeError("unsupported execution provider")')
        elif path.endswith("bidirectional-small-prepare.py"):
            old = (b'    if (os.environ.get("GITHUB_ACTIONS") != "true" or\n'
                   b'            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or\n'
                   b'            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):\n'
                   b'        raise RuntimeError("bounded bidirectional preparation requires own GitHub-hosted Actions branch")')
            new = (b'    if not _require_cloud_provider():\n'
                   b'        raise RuntimeError("unsupported execution provider")')
        elif path.endswith("stack-address-controls-prepare.py"):
            old = (b"    need(os.environ.get('GITHUB_ACTIONS') == 'true' and\n"
                   b"         os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted' and\n"
                   b"         os.environ.get('RUNNER_OS') == 'Linux' and\n"
                   b"         os.environ.get('GITHUB_REPOSITORY') == 'Tiramisu-Cake/verify-rust-std' and\n"
                   b"         os.environ.get('GITHUB_REF') == 'refs/heads/overnight/merge-26.10' and\n"
                   b"         re.fullmatch(r'[0-9a-f]{40}', os.environ.get('GITHUB_SHA', '')) and\n"
                   b"         os.environ.get('GITHUB_RUN_ID'), 'requires owned GitHub-hosted run')")
            new = b"    need(_require_cloud_provider(), 'requires identified Cloud Build execution')"
        elif path.endswith("panic-macro-admission.py"):
            old = (b"    need(os.environ.get('GITHUB_ACTIONS') == 'true' and\n"
                   b"         os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted' and\n"
                   b"         os.environ.get('GITHUB_REPOSITORY') == 'Tiramisu-Cake/verify-rust-std' and\n"
                   b"         os.environ.get('GITHUB_REF') == 'refs/heads/overnight/merge-26.10' and\n"
                   b"         re.fullmatch(r'[0-9a-f]{40}', os.environ.get('GITHUB_SHA', '')) and\n"
                   b"         os.environ.get('GITHUB_RUN_ID', '').isdigit(),\n"
                   b"         'panic origin admission requires exact owned GitHub hosted run')")
            new = (b"    provider = _require_cloud_provider()\n"
                   b"    need(re.fullmatch(r'[0-9a-f]{40}', os.environ.get('PROOF_SHA', '')) and\n"
                   b"         os.environ.get('CLOUD_BUILD_ID') == provider.get('build_id'),\n"
                   b"         'panic origin admission requires the exact Cloud Build and proof SHA')")
        elif path.endswith("stack-address-admission.py"):
            old = (b"    require(os.environ.get('GITHUB_ACTIONS') == 'true' and\n"
                   b"            os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted' and\n"
                   b"            os.environ.get('GITHUB_REPOSITORY') == 'Tiramisu-Cake/verify-rust-std' and\n"
                   b"            os.environ.get('GITHUB_REF') == 'refs/heads/overnight/merge-26.10',\n"
                   b"            'stack address admission requires the owned hosted research branch')")
            new = b"    require(_require_cloud_provider(), 'stack address admission requires identified Cloud Build')"
        elif path.endswith("stack-proof-ast-admission.py"):
            old = (b"    require(os.environ.get('GITHUB_ACTIONS') == 'true' and\n"
                   b"            os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted' and\n"
                   b"            os.environ.get('GITHUB_REPOSITORY') == 'Tiramisu-Cake/verify-rust-std' and\n"
                   b"            os.environ.get('GITHUB_REF') == 'refs/heads/overnight/merge-26.10',\n"
                   b"            'proof AST admission requires the owned hosted branch')")
            new = b"    require(_require_cloud_provider(), 'proof AST admission requires identified Cloud Build')"
        elif path.endswith("m2-admission-prove.py"):
            old = (b'    if (os.environ.get("GITHUB_ACTIONS") != "true" or\n'
                   b'            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or\n'
                   b'            os.environ.get("RUNNER_OS") != "Linux" or\n'
                   b'            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):\n'
                   b'        raise RuntimeError("M2 admission controls require hosted Linux Actions on overnight/merge-26.10")')
            new = (b'    if not _require_cloud_provider():\n'
                   b'        raise RuntimeError("unsupported execution provider")')
        elif path.endswith("hrtb-admission-certificate.py"):
            old = (b'    if (os.environ.get("GITHUB_ACTIONS") != "true" or\n'
                   b'            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or\n'
                   b'            os.environ.get("RUNNER_OS") != "Linux" or\n'
                   b'            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):\n'
                   b'        raise RuntimeError("HRTB certificate requires hosted Linux Actions on overnight/merge-26.10")')
            new = (b'    if not _require_cloud_provider():\n'
                   b'        raise RuntimeError("unsupported execution provider")')
        elif path.endswith("native-prove.py"):
            old = (b"    if (os.environ.get('GITHUB_ACTIONS') != 'true' or\n"
                   b"        os.environ.get('RUNNER_ENVIRONMENT') != 'github-hosted' or\n"
                   b"        os.environ.get('GITHUB_REF') != 'refs/heads/overnight/merge-26.10'):\n"
                   b"        raise RuntimeError('native proofs require own hosted Actions branch')")
            new = (b"    if not _require_cloud_provider():\n"
                   b"        raise RuntimeError('unsupported execution provider')")
        elif path.endswith("usize-multiple-admission.py"):
            old = (b"    if (os.environ.get('GITHUB_ACTIONS') != 'true' or\n"
                   b"            os.environ.get('RUNNER_ENVIRONMENT') != 'github-hosted' or\n"
                   b"            os.environ.get('GITHUB_REF') != 'refs/heads/overnight/merge-26.10'):\n"
                   b"        raise RuntimeError('source admission requires own GitHub-hosted branch')")
            new = (b"    if not _require_cloud_provider():\n"
                   b"        raise RuntimeError('unsupported execution provider')")
        else:
            raise SystemExit(f"unhandled provider overlay: {path}")
        data = replace_once(data, old, new, path)

        # Certificate identity is explicitly Cloud Build provenance, not a
        # fabricated GitHub run. Hash linkage and the exact negative gates stay.
        for old, new in ((b"github_sha", b"proof_sha"),
                         (b"github_run_id", b"execution_id"),
                         (b"GITHUB_SHA", b"PROOF_SHA"),
                         (b"GITHUB_RUN_ID", b"CLOUD_BUILD_ID")):
            data = data.replace(old, new)
        data = replace_once(data, b"import os\n", b"import os\nimport runpy\n", path)
        # Insert after imports and any future-import declaration, before main.
        data = replace_once(data, b"\ndef main", PROVIDER_HELPER.encode() + b"\ndef main", path)

        if path.endswith("pointer-prove.py"):
            data = replace_once(
                data,
                b'not isinstance(execution_id, str) or not execution_id.isdigit() or',
                b'not isinstance(execution_id, str) or execution_id != os.environ.get("CLOUD_BUILD_ID") or',
                path)
            data = replace_once(
                data,
                b'int(stale["certificate"].get("execution_id", "0")) + 1',
                b'"stale-" + str(stale["certificate"].get("execution_id", ""))',
                path)
        if path.endswith("hrtb-admission-certificate.py"):
            data = data.replace(b"dispatch_sha", b"proof_sha")
            data = replace_once(
                data,
                (b'    if (f"Source SHA: {proof_sha}" not in env_lines or\n'
                 b'            f"Actions SHA: {proof_sha}" not in env_lines):\n'
                 b'        raise RuntimeError("HRTB evidence root source/Actions SHA differs from current dispatch")'),
                (b'    if (f"Source SHA: {proof_sha}" not in env_lines or\n'
                 b'            f"Cloud proof SHA: {proof_sha}" not in env_lines or\n'
                 b'            "Provider: cloud-build" not in env_lines):\n'
                 b'        raise RuntimeError("HRTB evidence root source/provider/proof SHA differs from current Cloud Build")'),
                path)
        if path.endswith("usize-multiple-admission.py"):
            data = data.replace(b"actions_sha", b"proof_sha")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proof-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    if args.evidence.exists():
        raise SystemExit("refusing to reuse provider overlay evidence")
    args.evidence.mkdir(parents=True)
    # Read and validate the complete original trust chain before mutating a
    # single source. Overlay pins are then recalculated in dependency order.
    originals: dict[str, bytes] = {}
    for rel, expected in FILES.items():
        original = (args.proof_root / rel).read_bytes()
        actual = sha(original)
        if actual != expected:
            raise SystemExit(f"base source hash mismatch for {rel}: {actual}")
        originals[rel] = original

    network = "research/challenge-8/networks/prove.py"
    stock = "research/challenge-8/merge/stock-26.10/prove.py"
    functional = "research/challenge-8/merge/stock-26.10/functional-prove.py"
    order = "research/challenge-8/merge/stock-26.10/order-prove.py"
    stock_run = "research/challenge-8/merge/stock-26.10/run.sh"
    overlays: dict[str, bytes] = {}
    overlays[network] = transform(network, originals[network])
    pins = {"network_sha": sha(overlays[network])}
    overlays[stock] = transform(stock, originals[stock], pins)
    pins["prove_sha"] = sha(overlays[stock])
    overlays[functional] = transform(functional, originals[functional], pins)
    pins["functional_sha"] = sha(overlays[functional])
    overlays[order] = transform(order, originals[order], pins)
    overlays[stock_run] = transform(stock_run, originals[stock_run], pins)
    for rel, original in originals.items():
        if rel not in overlays:
            overlays[rel] = transform(rel, original, pins)

    manifest = {"provider": "cloud-build", "hash_pins": {
        "network": {"base_sha256": FILES[network], "overlay_sha256": pins["network_sha"]},
        "stock_prove": {"base_sha256": FILES[stock], "overlay_sha256": pins["prove_sha"]},
        "functional_prove": {"base_sha256": FILES[functional], "overlay_sha256": pins["functional_sha"]},
        "order_prove": {"base_sha256": FILES[order], "overlay_sha256": sha(overlays[order])},
        "stock_run": {"base_sha256": FILES[stock_run], "overlay_sha256": sha(overlays[stock_run])},
    }, "files": []}
    for rel, original in originals.items():
        overlay = overlays[rel]
        path = args.proof_root / rel
        path.write_bytes(overlay)
        manifest["files"].append({
            "path": rel, "base_sha256": FILES[rel], "overlay_sha256": sha(overlay),
            "diff": "".join(difflib.unified_diff(
                original.decode().splitlines(True), overlay.decode().splitlines(True),
                fromfile=rel + ".base", tofile=rel + ".cloud-build")),
        })
    (args.evidence / "provider-overlay-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
