#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 OR MIT
# GitHub-hosted VeriFast 26.09 explicit borrow-recovery control.
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != true || "${RUNNER_ENVIRONMENT:-}" != github-hosted || "${RUNNER_OS:-}" != Linux ]]; then
    echo 'Borrow-recovery pilot requires a GitHub-hosted Linux Actions runner' >&2
    exit 2
fi

repo=$(git rev-parse --show-toplevel)
cd "$repo"
evidence="$repo/research-results/verifast-borrow-recovery"
export VFVERSION=26.09 VFPLATFORM=linux RUSTUP_TOOLCHAIN=nightly-2026-02-05
selection=${PROOF_SELECTION:-verifast_borrow_recovery}
budget=${1:-90}
case "$budget" in 30|60|90|120) ;; *) echo 'Budget must be 30, 60, 90 or 120 minutes' >&2; exit 2 ;; esac

if [[ "${2:-}" != --inside ]]; then
    [[ ! -e "$evidence" ]] || { echo "refusing to reuse prior evidence directory: $evidence" >&2; exit 2; }
    mkdir -p "$evidence"
    set +e
    /usr/bin/time -v -o "$evidence/resources.txt" \
        timeout --signal=TERM --kill-after=30s "${budget}m" \
        bash "$repo/research/challenge-8/run-verifast-borrow-recovery.sh" "$budget" --inside \
        2>&1 | tee "$evidence/execution.log"
    status=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$status" > "$evidence/exit-code.txt"
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
        printf '### VeriFast explicit borrow-recovery pilot\n\nSelection: `%s`; exit `%s`.\n' \
            "$selection" "$status" >> "$GITHUB_STEP_SUMMARY"
    fi
    exit "$status"
fi

mkdir -p "$evidence"
{
    printf 'Source commit: '
    git rev-parse HEAD
    printf 'Selection: %s\nBudget including setup and all cases: %s minutes\n' "$selection" "$budget"
    printf 'VeriFast pin: %s (%s)\nRust toolchain: %s\n' "$VFVERSION" "$VFPLATFORM" "$RUSTUP_TOOLCHAIN"
    printf 'Hosted runner: %s / %s\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
    uname -a
    sha256sum research/challenge-8/verifast-borrow-recovery-cases.rs \
        research/challenge-8/run-verifast-borrow-recovery.sh verifast-proofs/setup-verifast-home
} > "$evidence/environment.txt"

source "$repo/verifast-proofs/setup-verifast-home"
{
    rustc --version --verbose
    sha256sum "$VERIFAST_HOME/bin/verifast" "$VERIFAST_HOME/bin/refinement-checker" \
        "$VERIFAST_HOME/bin/vf-rust-mir-exporter" "$VERIFAST_HOME/bin/rust/prelude.rsspec"
} >> "$evidence/environment.txt" 2>&1

vf_source_commit=809de4596839b739dd999f9e462242c835e3af46
vf_schema_sha=7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9
sudo apt-get update
sudo apt-get install --yes --no-install-recommends capnproto
capnp --version >> "$evidence/environment.txt"
schema="$evidence/vf_mir.capnp"
curl --fail --silent --show-error --location \
    "https://raw.githubusercontent.com/verifast/verifast/$vf_source_commit/src/rust_frontend/vf_mir/vf_mir.capnp" \
    --output "$schema"
printf '%s  %s\n' "$vf_schema_sha" "$schema" | sha256sum -c -
printf 'VeriFast source commit: %s\nSchema SHA-256: %s\n' \
    "$vf_source_commit" "$vf_schema_sha" >> "$evidence/environment.txt"

workdir="$evidence/cases"
mkdir -p "$workdir"
python3 - "$repo/research/challenge-8/verifast-borrow-recovery-cases.rs" "$workdir" <<'PY'
import hashlib, json, re, sys
from pathlib import Path

source = Path(sys.argv[1]).read_bytes()
root = Path(sys.argv[2])
names = ("positive_i32", "positive_generic", "negative_missing_token",
         "negative_missing_debt", "negative_false_post")
marker = re.compile(rb"(?ms)^// CASE_BEGIN ([a-z0-9_]+)\n(.*?)^// CASE_END \1\n")
matches = list(marker.finditer(source))
cases = {m.group(1).decode(): m for m in matches}
if tuple(cases) != names or len(matches) != len(names):
    raise SystemExit("case markers missing, duplicated, reordered, or unexpected")
prefix = source[:matches[0].start()]
blocks = re.compile(rb"(?s)/\*@.*?@\*/")
ghost_lines_re = re.compile(rb"(?m)^\s*//@[^\n]*(?:\n|$)")
def strip_ghost(data): return ghost_lines_re.sub(b"", blocks.sub(b"", data))

prefix_lines = prefix.splitlines()
helper_decl = next(i for i, line in enumerate(prefix_lines) if re.search(rb"\blem recover_pair<T>\(", line))
helper_open = next(i for i in range(helper_decl, len(prefix_lines)) if b"{" in prefix_lines[i])
depth = 0
helper_close = None
for i in range(helper_open, len(prefix_lines)):
    depth += prefix_lines[i].count(b"{") - prefix_lines[i].count(b"}")
    if depth == 0:
        helper_close = i
        break
if helper_close is None:
    raise SystemExit("recovery helper body braces are unbalanced")
helper_lines = {"declaration": helper_decl + 1, "start": helper_open + 1, "end": helper_close + 1}
manifest = {"fixture_sha256": hashlib.sha256(source).hexdigest(), "cases": {}}
for name, match in cases.items():
    d = root / name
    (d / "original").mkdir(parents=True, exist_ok=True)
    (d / "verified").mkdir(parents=True, exist_ok=True)
    verified = prefix + match.group(2)
    original = strip_ghost(verified)
    if b"lem_auto" in verified or b"assume(" in verified or b"assume_correct" in verified or b"end_lft_binding" in verified:
        raise SystemExit(f"forbidden automatic lemma, assumption, or lifetime extension in {name}")
    (d / "verified/lib.rs").write_bytes(verified)
    (d / "original/lib.rs").write_bytes(original)
    case_lines = match.group(2).splitlines()
    call_matches = [i for i, line in enumerate(case_lines) if re.search(rb"\brecover_pair::<[^>]+>\(left, right\);", line)]
    if len(call_matches) != 1:
        raise SystemExit(f"expected one explicit recover_pair call in {name}")
    call_line = len(prefix_lines) + call_matches[0] + 1
    manifest["cases"][name] = {
        "verified_sha256": hashlib.sha256(verified).hexdigest(),
        "original_sha256": hashlib.sha256(original).hexdigest(),
        "ghost_strip_exact_bytes": strip_ghost(verified) == original,
        "recovery_helper_body_lines": helper_lines,
        "helper_call_line": call_line,
    }
    if not manifest["cases"][name]["ghost_strip_exact_bytes"]:
        raise SystemExit(f"ghost stripping mismatch in {name}")
(root / "extraction.json").write_text(json.dumps(manifest, indent=2) + "\n")
PY
sha256sum "$workdir"/extraction.json "$workdir"/*/original/lib.rs "$workdir"/*/verified/lib.rs \
    > "$evidence/case-files-sha256.txt"

compiler_sysroot=$(rustc --print sysroot)
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$VERIFAST_HOME/bin:${LD_LIBRARY_PATH:-}"
printf 'Compiler sysroot: %s\n' "$compiler_sysroot" >> "$evidence/environment.txt"
case_names=(positive_i32 positive_generic negative_missing_token negative_missing_debt negative_false_post)
printf 'case\texporter_exit\tdecode_exit\tverifast_exit\trefinement_exit\tcaller_header_count\thelper_header_count\thelper_body_records\thelper_call_records\tclassification\n' \
    > "$evidence/case-summary.tsv"
overall_status=0
for case_name in "${case_names[@]}"; do
    case_dir="$workdir/$case_name"
    cd "$case_dir"
    sha256sum original/lib.rs verified/lib.rs > source-before-sha256.txt
    check_sources_unchanged() {
        sha256sum original/lib.rs verified/lib.rs > "source-after-$1-sha256.txt"
        cmp source-before-sha256.txt "source-after-$1-sha256.txt"
    }

    set +e
    /usr/bin/time -v -o exporter-resources.txt \
        "$VERIFAST_HOME/bin/vf-rust-mir-exporter" verified/lib.rs \
        "--sysroot=$compiler_sysroot" --edition 2021 --crate-type lib \
        --vf-rust-mir-exporter:preprocess-readonly > compiler-mir.bin 2> compiler-mir.log
    exporter_status=$?
    set -e
    printf '%s\n' "$exporter_status" > exporter-exit-code.txt
    sha256sum compiler-mir.bin > compiler-mir-sha256.txt
    check_sources_unchanged exporter

    decode_status=125
    if (( exporter_status == 0 )); then
        set +e
        capnp decode "$schema" VfMir < compiler-mir.bin > compiler-mir.txt 2> compiler-mir-decode.log
        decode_status=$?
        set -e
    fi
    printf '%s\n' "$decode_status" > compiler-mir-decode-exit-code.txt
    check_sources_unchanged decoder

    vf_status=125
    if (( exporter_status == 0 && decode_status == 0 )); then
        set +e
        /usr/bin/time -v -o verifast-resources.txt \
            "$VERIFAST_HOME/bin/verifast" -rustc_args '--edition 2021' -verbose 1 verified/lib.rs \
            > verifast.log 2>&1
        vf_status=$?
        set -e
    else
        : > verifast.log
    fi
    printf '%s\n' "$vf_status" > verifast-exit-code.txt
    check_sources_unchanged verifier

    set +e
    /usr/bin/time -v -o refinement-resources.txt \
        "$VERIFAST_HOME/bin/refinement-checker" --rustc-args '--edition 2021' \
        original/lib.rs verified/lib.rs > refinement.log 2>&1
    refinement_status=$?
    set -e
    printf '%s\n' "$refinement_status" > refinement-exit-code.txt
    check_sources_unchanged refiner

    helper_range=$(jq -r --arg name "$case_name" \
        '.cases[$name].recovery_helper_body_lines | "\(.start)-\(.end)"' "$workdir/extraction.json")
    helper_call_line=$(jq -r --arg name "$case_name" \
        '.cases[$name].helper_call_line' "$workdir/extraction.json")
    caller_header_count=$(awk -v name="$case_name" '
        index($0, "Verifying function '\''" name "'\''") &&
            $0 ~ /^[[:space:]]*[0-9]+[.][0-9]+s: / && $0 !~ /: note: Verifying function / { n++ }
        END { print n + 0 }
    ' verifast.log)
    helper_header_count=$(awk '
        index($0, "Verifying function '\''recover_pair'\''") &&
            $0 ~ /^[[:space:]]*[0-9]+[.][0-9]+s: / && $0 !~ /: note: Verifying function / { n++ }
        END { print n + 0 }
    ' verifast.log)
    helper_body_records=$(python3 - "$helper_range" verifast.log <<'PYLOG'
import re, sys
lo, hi = map(int, sys.argv[1].split("-"))
pattern = re.compile(r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): (?:note: )?(?:Executing statement|Verifying call)$")
print(sum(1 for line in open(sys.argv[2]) if (m := pattern.search(line)) and lo <= int(m.group(1)) <= hi))
PYLOG
    )
    helper_call_records=$(grep -E -c "verified/lib[.]rs\\(${helper_call_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): Verifying call$" verifast.log || true)
    printf '%s\n' "$caller_header_count" > caller-header-count.txt
    printf '%s\n' "$helper_header_count" > helper-header-count.txt
    printf '%s\n' "$helper_body_records" > helper-body-record-count.txt
    printf '%s\n' "$helper_call_records" > helper-call-record-count.txt
    cat verifast.log refinement.log

    case_classification=positive
    if [[ "$case_name" == positive_i32 || "$case_name" == positive_generic ]]; then
        if (( exporter_status != 0 || decode_status != 0 || vf_status != 0 || refinement_status != 0 ||
            caller_header_count != 1 || helper_header_count != 1 || helper_body_records < 1 || helper_call_records != 1 )); then
            printf 'positive failed: case=%s export=%s decode=%s vf=%s refinement=%s caller=%s helper=%s body=%s call=%s\n' \
                "$case_name" "$exporter_status" "$decode_status" "$vf_status" "$refinement_status" \
                "$caller_header_count" "$helper_header_count" "$helper_body_records" "$helper_call_records" >&2
            overall_status=1
            case_classification=positive_failed
        fi
    else
        case_classification=expected_call_precondition_failure
        case "$case_name" in
            negative_missing_token)
                classification=$(grep -Ei 'No matching heap chunks: .*lifetime_token|Cannot prove precondition.*lifetime_token' verifast.log | tail -n 3 || true)
                ;;
            negative_missing_debt)
                classification=$(grep -Ei 'No matching heap chunks: .*comparison_debt|Cannot prove precondition.*comparison_debt' verifast.log | tail -n 3 || true)
                ;;
            negative_false_post)
                classification=$(grep -Ei 'Cannot prove.*left_after != left_after|Cannot prove condition.*!\(left_after = left_after\)|Cannot prove.*false' verifast.log | tail -n 3 || true)
                case_classification=expected_false_postcondition_failure
                ;;
        esac
        printf '%s\n' "$classification" > negative-failure-classification.txt
        if (( exporter_status != 0 || decode_status != 0 || vf_status == 0 || refinement_status != 0 ||
            caller_header_count != 1 || helper_header_count != 1 || helper_body_records < 1 || helper_call_records != 1 )) ||
            [[ -z "$classification" ]]; then
            printf 'negative outcome rejected: case=%s export=%s decode=%s vf=%s refinement=%s caller=%s helper=%s body=%s call=%s\n' \
                "$case_name" "$exporter_status" "$decode_status" "$vf_status" "$refinement_status" \
                "$caller_header_count" "$helper_header_count" "$helper_body_records" "$helper_call_records" >&2
            overall_status=1
            case_classification=negative_classification_failed
        fi
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$case_name" "$exporter_status" "$decode_status" "$vf_status" "$refinement_status" "$caller_header_count" \
        "$helper_header_count" "$helper_body_records" "$helper_call_records" "$case_classification" \
        >> "$evidence/case-summary.tsv"
    cd "$repo"
done
cd "$repo"
printf '%s\n' "$overall_status" > "$evidence/stages-exit-code.txt"
exit "$overall_status"
