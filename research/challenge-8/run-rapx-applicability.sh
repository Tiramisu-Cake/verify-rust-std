#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

budget=${1:-90}
gate=${2:-A}
toolchain=nightly-2026-02-05
rapx_version=0.7.50
rapx_vcs=7d61d9377033c48a4df8954f34cc076e97a93816
expected_package_sha=e210328ce0e6c417ecf0498118ca0738f80851e9f2d204432a095ad703f8c0b8
target=library/core/src/slice/sort/shared/smallsort.rs
fixture_dir=research/challenge-8/rapx-applicability
classifier=research/challenge-8/classify-rapx-applicability.py
classifier_tests=research/challenge-8/test-rapx-applicability-classifier.py

[[ "$budget" == 90 ]] || { echo 'RAPx applicability is authorized only with a 90-minute total budget' >&2; exit 2; }
[[ "$gate" == A ]] || { echo 'This continuation authorizes gate A only; B and C remain outside scope' >&2; exit 2; }
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_OS:-}" == Linux && "${RUNNER_ENVIRONMENT:-}" == github-hosted ]] || {
    echo 'RAPx applicability requires a GitHub-hosted Linux Actions runner' >&2; exit 2;
}
for path in "$target" "$fixture_dir/Cargo.toml" "$fixture_dir/src/lib.rs" "$fixture_dir/src/zst.rs" \
    "$fixture_dir/src/bin/layout.rs" \
    "$fixture_dir/src/u64_controls.rs" "$classifier" "$classifier_tests" "$0" .github/workflows/smallsort-research.yml; do
    git ls-files --error-unmatch "$path" >/dev/null 2>&1 || { echo "Input not committed: $path" >&2; exit 2; }
    git diff --quiet HEAD -- "$path" || { echo "Input differs from dispatched commit: $path" >&2; exit 2; }
done

out=research-results/rapx-applicability
mkdir -p "$out/mir" "$out/fixture-source"
cp "$fixture_dir"/src/*.rs "$out/fixture-source/"
cp "$fixture_dir/Cargo.toml" "$out/fixture-source/"
runner_started=$(date +%s)
started=${RAPX_JOB_STARTED_EPOCH:-$runner_started}
# A failed stage must still upload its exit status and complete evidence hashes.
finish() {
    local code=$?
    trap - EXIT
    printf '%s\n' "$code" > "$out/runner-exit-code.txt"
    printf 'Runner elapsed (including recorded job preparation): %s seconds\n' "$(( $(date +%s) - started ))" >> "$out/experiment-environment.txt"
    find "$out" -type f ! -name artifact-sha256.txt -print0 | sort -z | xargs -0 sha256sum > "$out/artifact-sha256.txt"
    exit "$code"
}
trap finish EXIT
run_stage() {
    local label=$1
    shift
    local remaining=$(( budget * 60 - ($(date +%s) - started) ))
    local code
    if (( remaining <= 0 )); then
        printf '124\n' > "$out/$label-exit-code.txt"
        return 124
    fi
    printf 'Stage %s command: ' "$label" >> "$out/commands.txt"
    printf '%q ' "$@" >> "$out/commands.txt"
    printf '\n' >> "$out/commands.txt"
    set +e
    /usr/bin/time -v -o "$out/$label-resources.txt" \
        timeout --signal=TERM --kill-after=30s "${remaining}s" "$@" 2>&1 | tee "$out/$label.log"
    code=${PIPESTATUS[0]}
    set -e
    printf '%s\n' "$code" > "$out/$label-exit-code.txt"
    return "$code"
}
cat > "$out/experiment-environment.txt" <<EOT
Source commit: $(git rev-parse HEAD)
Selection: ${PROOF_SELECTION:-rapx_applicability}
Gate: $gate
Budget including setup and analysis: $budget minutes (workflow job hard limit is 90)
Runner: $RUNNER_OS / $RUNNER_ENVIRONMENT
Toolchain: $toolchain
RAPx exact package requirement: --version '=$rapx_version' --locked
Expected package archive SHA256: $expected_package_sha
Expected upstream VCS SHA: $rapx_vcs
Profile semantics: stock RAPx; no patches or configuration model rewrites
Target-list diagnostic: --prepare-targets --mode targeted
Per-case contracts diagnostic: --debug-contracts --mode targeted
Real verification flags: --mode targeted --postfix-repeat auto (NO --debug-contracts)
Logging: RAPX_LOG=debug
MIR dump: -Zdump-mir=all (fixture only)
EOT
uname -a >> "$out/experiment-environment.txt"
git status --short --branch >> "$out/experiment-environment.txt"
sha256sum "$target" research/challenge-8/SORT4-CONTRACT.md "$fixture_dir/Cargo.toml" \
    "$fixture_dir/src/lib.rs" "$fixture_dir/src/zst.rs" "$fixture_dir/src/u64_controls.rs" \
    "$fixture_dir/src/bin/layout.rs" \
    "$classifier" "$classifier_tests" "$0" .github/workflows/smallsort-research.yml >> "$out/experiment-environment.txt"
git rev-parse "HEAD:$target" >> "$out/experiment-environment.txt"
target_blob=$(git rev-parse "HEAD:$target")
if [[ "$target_blob" != e555fce440872898e47fd5114f32eb15401d07df ]]; then
    echo "SmallSort target blob mismatch: $target_blob" | tee "$out/setup-blocker.txt"
    exit 3
fi

crate_archive="$RUNNER_TEMP/rapx-$rapx_version.crate"
run_stage package-download curl --fail --location --silent --show-error \
    "https://static.crates.io/crates/rapx/rapx-$rapx_version.crate" -o "$crate_archive"
actual_package_sha=$(sha256sum "$crate_archive" | cut -d ' ' -f 1)
printf 'Downloaded archive SHA256: %s\n' "$actual_package_sha" >> "$out/experiment-environment.txt"
if [[ "$actual_package_sha" != "$expected_package_sha" ]]; then
    echo 'RAPx crate archive identity mismatch' | tee "$out/setup-blocker.txt"
    exit 3
fi
archive_tree="$RUNNER_TEMP/challenge8-rapx-archive"
mkdir -p "$archive_tree"
tar -xf "$crate_archive" -C "$archive_tree"
archive_root="$archive_tree/rapx-$rapx_version"
cp "$archive_root/.cargo_vcs_info.json" "$out/package-vcs-info.json"
python3 - "$out/package-vcs-info.json" "$rapx_vcs" <<'PYVCS'
import json, sys
metadata = json.load(open(sys.argv[1]))
assert metadata['git']['sha1'] == sys.argv[2], metadata
assert metadata['path_in_vcs'] == 'rapx', metadata
print('PASS archive VCS identity')
PYVCS
tar -xOf "$crate_archive" "rapx-$rapx_version/Cargo.lock" > "$out/installed-package-Cargo.lock"
tar -xOf "$crate_archive" "rapx-$rapx_version/Cargo.toml" > "$out/installed-package-Cargo.toml"
sha256sum "$out/installed-package-Cargo.lock" "$out/installed-package-Cargo.toml" >> "$out/experiment-environment.txt"
cat "$out/package-vcs-info.json" >> "$out/experiment-environment.txt"

run_stage toolchain-install rustup toolchain install "$toolchain" --profile minimal
run_stage toolchain-components rustup component add rustc-dev rust-src llvm-tools-preview --toolchain "$toolchain"
rustup run "$toolchain" rustc --version --verbose > "$out/rustc-version.txt"
rustup run "$toolchain" rustc --print sysroot > "$out/sysroot-path.txt"
rustup run "$toolchain" rustc --print target-libdir > "$out/target-libdir.txt"
rustc_sysroot=$(cat "$out/sysroot-path.txt")
export RUSTUP_TOOLCHAIN="$toolchain"
export RAPX_SYSROOT="$rustc_sysroot"
export LD_LIBRARY_PATH="$RAPX_SYSROOT/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
rust_src="$rustc_sysroot/lib/rustlib/src/rust/library"
if [[ -d "$rust_src/core/src" ]]; then
    find "$rust_src/core/src/ptr" "$rust_src/core/src/intrinsics" -type f -print0 | sort -z | xargs -0 sha256sum > "$out/sysroot-core-source-hashes.txt"
else
    echo 'Pinned toolchain rust-src core sources are missing' | tee "$out/setup-blocker.txt"
    exit 3
fi
printf 'Target libdir: %s\n' "$(cat "$out/target-libdir.txt")" >> "$out/experiment-environment.txt"
printf 'Tool binaries:\n' >> "$out/experiment-environment.txt"
command -v cargo rustup >> "$out/experiment-environment.txt"
rustup run "$toolchain" rustc --version >> "$out/experiment-environment.txt"
rustup run "$toolchain" cargo --version >> "$out/experiment-environment.txt"
dpkg-query -W -f='${binary:Package} ${Version}\n' libz3-dev libclang-dev pkg-config >> "$out/experiment-environment.txt" 2>&1 || true
pkg-config --modversion z3 >> "$out/experiment-environment.txt" 2>&1 || true

install_root="$RUNNER_TEMP/challenge8-rapx-install"
run_stage cargo-install cargo +"$toolchain" install rapx --version "=$rapx_version" --locked --root "$install_root"
export PATH="$install_root/bin:$PATH"
printf 'Isolated RAPx installation root: %s\n' "$install_root" >> "$out/experiment-environment.txt"
RAPXFLAGS=--version rapx > "$out/rapx-version.txt" 2>&1
cargo +"$toolchain" rapx --version >> "$out/rapx-version.txt" 2>&1
if ! rg -Fx "rapx version $rapx_version" "$out/rapx-version.txt" ||
   ! rg -Fx "cargo-rapx version $rapx_version" "$out/rapx-version.txt"; then
    echo 'Installed RAPx executable did not report the exact pinned version' | tee "$out/setup-blocker.txt"
    exit 3
fi
sha256sum "$(command -v rapx)" "$(command -v cargo-rapx)" >> "$out/experiment-environment.txt"
cat "$out/rapx-version.txt" >> "$out/experiment-environment.txt"
cargo +"$toolchain" install --list --root "$install_root" > "$out/cargo-install-list.txt"

# Cargo bookkeeping files are not a source-identity requirement. Compare
# every installed candidate's complete src tree and published build inputs to
# the verified archive instead, independently of .cargo-checksum.json.
mapfile -t registry_roots < <(find "${CARGO_HOME:-$HOME/.cargo}/registry/src" -mindepth 2 -maxdepth 2 -type d -name "rapx-$rapx_version" -print | sort)
(( ${#registry_roots[@]} > 0 )) || { echo 'Installed RAPx source tree unavailable' | tee "$out/setup-blocker.txt"; exit 3; }
printf '%s\n' "${registry_roots[@]}" > "$out/installed-source-candidates.txt"
for registry_root in "${registry_roots[@]}"; do
    diff -qr "$archive_root/src" "$registry_root/src" >> "$out/source-diff-archive.txt" || {
        echo 'Installed source differs from verified archive' | tee "$out/setup-blocker.txt"; exit 3;
    }
    for rel in Cargo.toml Cargo.lock build.rs; do
        cmp "$archive_root/$rel" "$registry_root/$rel" || {
            echo "Installed package input differs from verified archive: $rel" | tee "$out/setup-blocker.txt"; exit 3;
        }
    done
    if [[ -f "$registry_root/.cargo_vcs_info.json" ]]; then
        cmp "$archive_root/.cargo_vcs_info.json" "$registry_root/.cargo_vcs_info.json" || {
            echo 'Installed package VCS metadata differs from verified archive' | tee "$out/setup-blocker.txt"; exit 3;
        }
    fi
    printf 'PASS full installed source and published inputs match archive: %s\n' "$registry_root" >> "$out/package-audit.txt"
done
registry_root=${registry_roots[0]}
sha256sum "$registry_root/Cargo.lock" "$registry_root/Cargo.toml" "$registry_root/build.rs" >> "$out/package-audit.txt"

# Compare installed verifier/checker/contract/display sources bytewise with
# the pinned upstream tree. No source patch or fallback is accepted.
upstream="$RUNNER_TEMP/rapx-upstream"
git init -q "$upstream"
git -C "$upstream" remote add origin https://github.com/safer-rust/RAPx.git
run_stage upstream-fetch git -C "$upstream" fetch --quiet --depth=1 origin "$rapx_vcs"
git -C "$upstream" checkout --quiet --detach FETCH_HEAD
[[ "$(git -C "$upstream" rev-parse HEAD)" == "$rapx_vcs" ]] || {
    echo 'Fetched RAPx upstream source identity mismatch' | tee "$out/setup-blocker.txt"; exit 3;
}
upstream_src="$upstream/rapx/src"
[[ -d "$upstream_src/verify" ]] || upstream_src="$upstream/src"
diff -qr "$registry_root/src" "$upstream_src" > "$out/source-diff-upstream.txt" || {
    echo 'Installed source differs from reviewed upstream profile' | tee "$out/setup-blocker.txt"; exit 3;
}
cmp "$registry_root/build.rs" "$upstream/rapx/build.rs" || {
    echo 'Installed build configuration differs from reviewed upstream' | tee "$out/setup-blocker.txt"; exit 3;
}
(
    cd "$registry_root/src"
    find . -type f -print0 | sort -z | xargs -0 sha256sum
) > "$out/installed-relevant-source-hashes.txt"
(
    cd "$upstream_src"
    find . -type f -print0 | sort -z | xargs -0 sha256sum
) > "$out/reviewed-relevant-source-hashes.txt"
cmp "$out/installed-relevant-source-hashes.txt" "$out/reviewed-relevant-source-hashes.txt" || {
    echo 'Installed/reviewed source hash lists differ' | tee "$out/setup-blocker.txt"; exit 3;
}
printf 'Installed full src comparison to archive and upstream: byte-identical\n' >> "$out/experiment-environment.txt"

# Fixture registration is declared in lib.rs; do not inject it twice.
export RUSTFLAGS="--cfg=rapx"
# Hosted only: exercise classifier acceptance/rejection before the tool cases.
run_stage classifier-tests python3 "$classifier_tests"

export RAPX_LOG=debug

run_stage type-layout bash -c 'cd "$1" && cargo +nightly-2026-02-05 run --bin layout' _ "$fixture_dir"
if ! rg -q 'zst\.size=0 zst\.align=8 u64\.size=8 u64\.align=8' "$out/type-layout.log"; then
    echo 'Expected ZST/u64 size and alignment were not observed on the hosted target' | tee "$out/setup-blocker.txt"
    exit 3
fi

# Target preparation and contract printing are diagnostics, never proof results.
run_stage prepare-targets bash -c 'cd "$1" && cargo +nightly-2026-02-05 rapx verify --prepare-targets --mode targeted --crate rapx-applicability --postfix-repeat auto -- --lib' _ "$fixture_dir"

cases=(
    'zst_aligned:zst::aligned'
    'zst_source_misaligned:zst::source_misaligned'
    'zst_destination_misaligned:zst::destination_misaligned'
    'u64_aligned:u64_controls::aligned'
    'u64_source_misaligned:u64_controls::source_misaligned'
    'u64_destination_misaligned:u64_controls::destination_misaligned'
)
suite_exit=0
for item in "${cases[@]}"; do
    name=${item%%:*}
    module=${item#*:}
    printf '\nRAPx gate A case: %s / module %s\n' "$name" "$module"
    # The same filter is used in both calls; only the diagnostic prints contracts.
    if run_stage "$name-contracts" bash -c 'cd "$1" && cargo +nightly-2026-02-05 rapx verify --mode targeted --crate rapx-applicability --module "$2" --postfix-repeat auto --debug-contracts -- --lib' _ "$fixture_dir" "$module"; then
        contract_code=0
    else
        contract_code=$?
        suite_exit=1
    fi
    # Save each case's MIR outside Cargo target so its automatic clean cannot
    # remove it; associate dumped blocks with this real verification invocation.
    case_mir="$(pwd)/$out/mir/$name"
    mkdir -p "$case_mir"
    if run_stage "$name" env "RUSTFLAGS=--cfg=rapx -Zdump-mir=all -Zdump-mir-dir=$case_mir" \
        bash -c 'cd "$1" && cargo +nightly-2026-02-05 rapx verify --mode targeted --crate rapx-applicability --module "$2" --postfix-repeat auto -- --lib' _ "$fixture_dir" "$module"; then
        raw_code=0
    else
        raw_code=$?
        suite_exit=1
    fi
    if ! run_stage "$name-classifier" python3 "$classifier" --case "$name" --exit-code "$raw_code" \
        --verify-log "$out/$name.log" --contracts "$out/$name-contracts.log" --contract-exit-code "$contract_code" --out "$out/$name.json"; then
        suite_exit=1
    fi
    if (( raw_code == 124 || contract_code == 124 )); then suite_exit=124; break; fi
done

python3 - "$out" <<'PY' > "$out/gate-a-summary.json"
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
names = ("zst_aligned", "zst_source_misaligned", "zst_destination_misaligned",
         "u64_aligned", "u64_source_misaligned", "u64_destination_misaligned")
rows = []
for name in names:
    path = p / f"{name}.json"
    rows.append(json.loads(path.read_text()) if path.exists() else {"case": name, "outcome": "NOT_RUN"})
print(json.dumps({"gate": "A", "cases": rows,
                  "all_expected": all(x.get("outcome") in ("PROVED_VALID", "INTENDED_DETECTION") for x in rows)}, indent=2))
PY
printf 'Gate A suite raw status: %s\nElapsed seconds: %s\n' "$suite_exit" "$(( $(date +%s) - started ))" >> "$out/experiment-environment.txt"
exit "$suite_exit"
