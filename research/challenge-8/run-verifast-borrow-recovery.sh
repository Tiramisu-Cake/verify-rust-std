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
profile=${BORROW_RECOVERY_PROFILE:-baseline}
case "$profile" in
    baseline) evidence="$repo/research-results/verifast-borrow-recovery" ;;
    manually_drop_only) evidence="$repo/research-results/verifast-borrow-recovery-manually-drop-only" ;;
    *) echo "Unknown BORROW_RECOVERY_PROFILE: $profile" >&2; exit 2 ;;
esac
export VFVERSION=26.09 VFPLATFORM=linux RUSTUP_TOOLCHAIN=nightly-2026-02-05
if [[ "$profile" == manually_drop_only ]]; then
    selection=${PROOF_SELECTION:-verifast_borrow_recovery_manually_drop_only}
else
    selection=${PROOF_SELECTION:-verifast_borrow_recovery}
fi
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
    printf 'Profile: %s\nSelection: %s\nBudget including setup and all cases: %s minutes\n' "$profile" "$selection" "$budget"
    printf 'VeriFast pin: %s (%s)\nRust toolchain: %s\n' "$VFVERSION" "$VFPLATFORM" "$RUSTUP_TOOLCHAIN"
    printf 'Hosted runner: %s / %s\n' "$RUNNER_ENVIRONMENT" "$RUNNER_OS"
    uname -a
    sha256sum research/challenge-8/verifast-borrow-recovery-cases.rs \
        research/challenge-8/run-verifast-borrow-recovery.sh verifast-proofs/setup-verifast-home
} > "$evidence/environment.txt"

source "$repo/verifast-proofs/setup-verifast-home"
tool_home="$VERIFAST_HOME"
{
    rustc --version --verbose
    sha256sum "$VERIFAST_HOME/bin/verifast" "$VERIFAST_HOME/bin/refinement-checker" \
        "$VERIFAST_HOME/bin/vf-rust-mir-exporter" "$VERIFAST_HOME/bin/rust/prelude.rsspec"
} >> "$evidence/environment.txt" 2>&1

if [[ "$profile" == manually_drop_only ]]; then
    source_home="$RUNNER_TEMP/verifast-borrow-recovery-manually-drop-only"
    [[ ! -e "$source_home" ]] || { echo "refusing to reuse source build directory: $source_home" >&2; exit 2; }
    bash "$repo/research/challenge-8/build-verifast-tuple-parser.sh" \
        "$VERIFAST_HOME" "$evidence/source-build" "$source_home" manually_drop_only
    tool_home="$source_home"
fi
{
    printf 'Effective verifier home: %s\n' "$tool_home"
    sha256sum "$tool_home/bin/verifast" "$tool_home/bin/refinement-checker" \
        "$tool_home/bin/vf-rust-mir-exporter" "$tool_home/bin/rust/prelude.rsspec"
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
python3 - "$repo/research/challenge-8/verifast-borrow-recovery-cases.rs" "$workdir" "$profile" <<'PY'
import hashlib, json, re, sys
from pathlib import Path

source = Path(sys.argv[1]).read_bytes()
root = Path(sys.argv[2])
profile = sys.argv[3]
baseline_names = ("positive_i32", "positive_generic", "negative_missing_token",
                  "negative_missing_debt", "negative_false_post")
manually_drop_names = ("positive_manually_drop", "negative_manually_drop_missing_init")
all_names = baseline_names + manually_drop_names
names = baseline_names + (manually_drop_names if profile == "manually_drop_only" else ())
marker = re.compile(rb"(?ms)^// CASE_BEGIN ([a-z0-9_]+)\n(.*?)^// CASE_END \1\n")
matches = list(marker.finditer(source))
cases = {m.group(1).decode(): m for m in matches}
if tuple(cases) != all_names or len(matches) != len(all_names):
    raise SystemExit("case markers missing, duplicated, reordered, or unexpected")
selected_cases = {name: cases[name] for name in names}
prefix = source[:matches[0].start()]
baseline_prefix, removed = re.subn(
    rb"(?s)/\*@\n// Keep same-reference accesses.*?@\*/\n", b"", prefix, count=1)
if removed != 1:
    raise SystemExit("baseline controls must omit the optional single-cell helpers")
blocks = re.compile(rb"(?s)/\*@.*?@\*/")
ghost_lines_re = re.compile(rb"(?m)^\s*//@[^\n]*(?:\n|$)")
def strip_ghost(data): return ghost_lines_re.sub(b"", blocks.sub(b"", data))

def get_helper_lines(name, prefix_lines):
    decl = next(i for i, line in enumerate(prefix_lines)
                if re.search(rb"\blem " + name.encode() + rb"<T>\(", line))
    body_open = next(i for i in range(decl, len(prefix_lines)) if b"{" in prefix_lines[i])
    depth = 0
    for i in range(body_open, len(prefix_lines)):
        depth += prefix_lines[i].count(b"{") - prefix_lines[i].count(b"}")
        if depth == 0:
            return {"declaration": decl + 1, "start": body_open + 1, "end": i + 1}
    raise SystemExit(f"{name} helper body braces are unbalanced")
manifest = {"fixture_sha256": hashlib.sha256(source).hexdigest(), "cases": {}}
for name, match in selected_cases.items():
    d = root / name
    (d / "original").mkdir(parents=True, exist_ok=True)
    (d / "verified").mkdir(parents=True, exist_ok=True)
    is_manually_drop = name in manually_drop_names
    case_prefix = prefix if is_manually_drop else baseline_prefix
    prefix_lines = case_prefix.splitlines()
    verified = case_prefix + match.group(2)
    original = strip_ghost(verified)
    if b"lem_auto" in verified or b"assume(" in verified or b"assume_correct" in verified or b"end_lft_binding" in verified:
        raise SystemExit(f"forbidden automatic lemma, assumption, or lifetime extension in {name}")
    (d / "verified/lib.rs").write_bytes(verified)
    (d / "original/lib.rs").write_bytes(original)
    case_body = match.group(2)
    case_lines = case_body.splitlines()
    is_manually_drop = name in manually_drop_names
    helper_name = "recover_single" if is_manually_drop else "recover_pair"
    helper_pattern = (rb"\brecover_single::<[^>]+>\(&tmp\);" if name == "positive_manually_drop"
                      else rb"\brecover_pair::<[^>]+>\(left, right\);")
    helper_matches = [i for i, line in enumerate(case_lines) if re.search(helper_pattern, line)]
    if name != "negative_manually_drop_missing_init" and len(helper_matches) != 1:
        raise SystemExit(f"expected one explicit {helper_name} call in {name}")
    if name == "negative_manually_drop_missing_init" and helper_matches:
        raise SystemExit("missing-init negative must fail before helper call")
    helper_call_line = len(prefix_lines) + helper_matches[0] + 1 if helper_matches else 0
    temp_ref_matches = [i for i, line in enumerate(case_lines)
                        if re.search(rb"let _tmp_shared = &\*tmp;", line)]
    temp_ref_line = len(prefix_lines) + temp_ref_matches[0] + 1 if len(temp_ref_matches) == 1 else 0
    metadata = {
        "helper_kind": helper_name,
        "helper_lines": get_helper_lines(helper_name, prefix_lines),
        "helper_call_line": helper_call_line,
        "temp_ref_line": temp_ref_line,
    }
    if is_manually_drop:
        init_ref_count = case_body.count(b"init_ref_share::<T>(cmp_k, t, tmp_ref);")
        precreate_count = case_body.count(b"precreate_ref(&tmp)")
        if temp_ref_line == 0 or precreate_count != 1:
            raise SystemExit(f"{name}: expected exactly one prepared temp reference source")
        if name == "positive_manually_drop":
            required = (b"cell.read()", b"core::mem::ManuallyDrop::new(value)",
                        b"open_frac_borrow(cmp_k, ref_initialized_(tmp_ref), 1/4);",
                        b"let tmp_ptr = core::ptr::addr_of!(tmp) as *const T;",
                        b"let value = tmp_ptr.read();", b"cell.write(value);")
            if any(token not in case_body for token in required) or init_ref_count != 1:
                raise SystemExit("positive ManuallyDrop case is missing a required real operation or init share")
            if case_body.count(b"open_frac_borrow(cmp_k, ref_initialized_(tmp_ref), 1/4);") != 2:
                raise SystemExit("positive ManuallyDrop case must close two quarter lifetime shares")
            if b"ManuallyDrop::into_inner" in case_body or re.search(rb"<\s*T\s*:\s*[^>]*(?:Copy|Freeze)", case_body):
                raise SystemExit("unsupported ManuallyDrop call or generic bound found")
            metadata["mir_audit_required"] = True
        else:
            if init_ref_count != 0 or helper_matches:
                raise SystemExit("missing-init negative must omit init share and stop before recovery")
            metadata["mir_audit_required"] = False
    manifest["cases"][name] = {
        "verified_sha256": hashlib.sha256(verified).hexdigest(),
        "original_sha256": hashlib.sha256(original).hexdigest(),
        "ghost_strip_exact_bytes": strip_ghost(verified) == original,
        **metadata,
    }
    if not manifest["cases"][name]["ghost_strip_exact_bytes"]:
        raise SystemExit(f"ghost stripping mismatch in {name}")
(root / "extraction.json").write_text(json.dumps(manifest, indent=2) + "\n")
PY
sha256sum "$workdir"/extraction.json "$workdir"/*/original/lib.rs "$workdir"/*/verified/lib.rs \
    > "$evidence/case-files-sha256.txt"

compiler_sysroot=$(rustc --print sysroot)
if [[ "$profile" == manually_drop_only ]]; then
    export LD_LIBRARY_PATH="$tool_home/bin:$compiler_sysroot/lib:${LD_LIBRARY_PATH:-}"
else
    export LD_LIBRARY_PATH="$compiler_sysroot/lib:$tool_home/bin:${LD_LIBRARY_PATH:-}"
fi
ldd "$tool_home/bin/verifast" > "$evidence/effective-verifast-ldd.txt"
if [[ "$profile" == manually_drop_only ]] && ! grep -F "libz3.so => $tool_home/bin/libz3.so " "$evidence/effective-verifast-ldd.txt"; then
    echo "Verifier did not resolve the paired libz3 from $tool_home/bin" >&2
    exit 2
fi
printf 'Compiler sysroot: %s\n' "$compiler_sysroot" >> "$evidence/environment.txt"
case_names=(positive_i32 positive_generic negative_missing_token negative_missing_debt negative_false_post)
if [[ "$profile" == manually_drop_only ]]; then
    case_names+=(positive_manually_drop negative_manually_drop_missing_init)
fi
printf 'case\texporter_exit\tdecode_exit\tverifast_exit\trefinement_exit\thelper_kind\tcaller_header_count\thelper_header_count\thelper_body_records\thelper_call_records\ttemp_ref_records\tclassification\n' \
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
        "$tool_home/bin/vf-rust-mir-exporter" verified/lib.rs \
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
        /usr/bin/time -v -o compiler-mir-decode-resources.txt \
            capnp decode "$schema" VfMir < compiler-mir.bin > compiler-mir.txt 2> compiler-mir-decode.log
        decode_status=$?
        set -e
    fi
    printf '%s\n' "$decode_status" > compiler-mir-decode-exit-code.txt
    sha256sum compiler-mir.txt 2>/dev/null > compiler-mir-text-sha256.txt || true
    check_sources_unchanged decoder

    mir_audit_status=0
    if [[ "$case_name" == positive_manually_drop && $decode_status == 0 ]]; then
        manually_drop_mir_function_count=$(grep -F -c 'defPath = "positive_manually_drop"' compiler-mir.txt || true)
        printf '%s\n' "$manually_drop_mir_function_count" > manually-drop-mir-function-count.txt
        awk -v name='positive_manually_drop' '
            index($0, "defPath = \"" name "\"") { active=1; start=NR }
            active && NR > start && index($0, "defPath = ") { exit }
            active { print }
        ' compiler-mir.txt > manually-drop-mir-function.txt
        set +e
        python3 - "$manually_drop_mir_function_count" manually-drop-mir-function.txt <<'PYMIR'
import json, re, sys
from pathlib import Path
function_count = int(sys.argv[1])
text = Path(sys.argv[2]).read_text(errors="replace")
counts = {
    "ManuallyDrop_new": len(re.findall(r"ManuallyDrop(?:::<[^>]+>)?::new", text)),
    "Deref_deref": len(re.findall(r"(?:core|std)::ops::Deref::deref", text)),
    "ptr_read": len(re.findall(r"(?:core|std)::ptr::[^\n\"]*::read", text)),
    "ptr_write": len(re.findall(r"(?:core|std)::ptr::[^\n\"]*::write", text)),
    "ManuallyDrop_into_inner": len(re.findall(r"ManuallyDrop(?:::<[^>]+>)?::into_inner", text)),
}
counts["target_function_records"] = function_count
Path("manually-drop-mir-audit.json").write_text(json.dumps(counts, indent=2) + "\n")
if function_count != 1 or counts["ManuallyDrop_new"] != 1 or counts["Deref_deref"] != 1 or \
   counts["ptr_read"] != 2 or counts["ptr_write"] != 1 or counts["ManuallyDrop_into_inner"] != 0:
    raise SystemExit(f"MIR did not retain the required ManuallyDrop/ref/read/write paths: {counts}")
PYMIR
        mir_audit_status=$?
        set -e
    elif [[ "$case_name" == positive_manually_drop ]]; then
        mir_audit_status=1
    fi
    printf '%s\n' "$mir_audit_status" > manually-drop-mir-audit-exit-code.txt

    vf_status=125
    if (( exporter_status == 0 && decode_status == 0 )); then
        set +e
        /usr/bin/time -v -o verifast-resources.txt \
            "$tool_home/bin/verifast" -rustc_args '--edition 2021' -verbose 1 verified/lib.rs \
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
        "$tool_home/bin/refinement-checker" --rustc-args '--edition 2021' \
        original/lib.rs verified/lib.rs > refinement.log 2>&1
    refinement_status=$?
    set -e
    printf '%s\n' "$refinement_status" > refinement-exit-code.txt
    check_sources_unchanged refiner

    helper_name=$(jq -r --arg name "$case_name" '.cases[$name].helper_kind' "$workdir/extraction.json")
    helper_range=$(jq -r --arg name "$case_name" \
        '.cases[$name].helper_lines | "\(.start)-\(.end)"' "$workdir/extraction.json")
    helper_call_line=$(jq -r --arg name "$case_name" \
        '.cases[$name].helper_call_line' "$workdir/extraction.json")
    temp_ref_line=$(jq -r --arg name "$case_name" '.cases[$name].temp_ref_line' "$workdir/extraction.json")
    caller_header_count=$(awk -v name="$case_name" '
        index($0, "Verifying function '\''" name "'\''") &&
            $0 ~ /^[[:space:]]*[0-9]+[.][0-9]+s: / && $0 !~ /: note: Verifying function / { n++ }
        END { print n + 0 }
    ' verifast.log)
    helper_header_count=$(awk -v name="$helper_name" '
        index($0, "Verifying function '\''" name "'\''") &&
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
    helper_call_records=0
    if (( helper_call_line > 0 )); then
        helper_call_records=$(grep -E -c "verified/lib[.]rs\\(${helper_call_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): Verifying call$" verifast.log || true)
    fi
    temp_ref_records=0
    if (( temp_ref_line > 0 )); then
        temp_ref_records=$(grep -E -c "verified/lib[.]rs\\(${temp_ref_line},[0-9]+(-[0-9]+(,[0-9]+)?)?\\): (Verifying call|Executing statement)$" verifast.log || true)
    fi
    printf '%s\n' "$caller_header_count" > caller-header-count.txt
    printf '%s\n' "$helper_header_count" > helper-header-count.txt
    printf '%s\n' "$helper_body_records" > helper-body-record-count.txt
    printf '%s\n' "$helper_call_records" > helper-call-record-count.txt
    printf '%s\n' "$temp_ref_records" > temp-ref-record-count.txt
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
    elif [[ "$case_name" == positive_manually_drop ]]; then
        if (( exporter_status != 0 || decode_status != 0 || mir_audit_status != 0 || vf_status != 0 ||
            refinement_status != 0 || caller_header_count != 1 || helper_header_count != 1 ||
            helper_body_records < 1 || helper_call_records != 1 || temp_ref_records < 1 )); then
            printf 'ManuallyDrop positive failed: export=%s decode=%s MIR=%s vf=%s refinement=%s caller=%s helper=%s body=%s call=%s ref-source=%s\n' \
                "$exporter_status" "$decode_status" "$mir_audit_status" "$vf_status" "$refinement_status" \
                "$caller_header_count" "$helper_header_count" "$helper_body_records" "$helper_call_records" "$temp_ref_records" >&2
            overall_status=1
            case_classification=manually_drop_positive_failed
        else
            case_classification=manually_drop_positive_verified
        fi
    elif [[ "$case_name" == negative_manually_drop_missing_init ]]; then
        classification=$(grep -E 'bin/rust/aliasing[.]rsspec\([0-9]+,[0-9]+(-[0-9]+(,[0-9]+)?)?\): error: No matching heap chunks: .*ref_initialized' verifast.log | tail -n 2 || true)
        printf '%s\n' "$classification" > negative-failure-classification.txt
        if (( exporter_status != 0 || decode_status != 0 || vf_status == 0 || refinement_status != 0 ||
            caller_header_count != 1 || temp_ref_line < 1 || temp_ref_records < 1 || helper_call_records != 0 )) ||
            [[ -z "$classification" ]] || rg -qi 'Parse error|Rust frontend failed|Failed to run rustc|error\[E[0-9]+\]|error: aborting due' verifast.log; then
            printf 'ManuallyDrop missing-init negative did not fail at its prepared shared-reference construction: export=%s decode=%s vf=%s refinement=%s caller=%s ref-line=%s ref-records=%s helper-call=%s\n' \
                "$exporter_status" "$decode_status" "$vf_status" "$refinement_status" \
                "$caller_header_count" "$temp_ref_line" "$temp_ref_records" "$helper_call_records" >&2
            overall_status=1
            case_classification=manually_drop_negative_misclassified
        else
            case_classification=expected_missing_ref_initialized_at_tmp_borrow
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
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$case_name" "$exporter_status" "$decode_status" "$vf_status" "$refinement_status" "$helper_name" "$caller_header_count" \
        "$helper_header_count" "$helper_body_records" "$helper_call_records" "$temp_ref_records" "$case_classification" \
        >> "$evidence/case-summary.tsv"
    cd "$repo"
done
cd "$repo"
printf '%s\n' "$overall_status" > "$evidence/stages-exit-code.txt"
exit "$overall_status"
