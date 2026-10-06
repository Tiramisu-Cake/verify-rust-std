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

[[ "$budget" == 90 ]] || { echo 'RAPx applicability is authorized only with a 90-minute total budget' >&2; exit 2; }
[[ "$gate" == A ]] || { echo 'Only gate A is enabled; B and C require prior gate completion' >&2; exit 2; }
[[ "${GITHUB_ACTIONS:-}" == true && "${RUNNER_OS:-}" == Linux && "${RUNNER_ENVIRONMENT:-}" == github-hosted ]] || {
    echo 'RAPx applicability requires a GitHub-hosted Linux Actions runner' >&2; exit 2;
}
for path in "$target" "$fixture_dir/Cargo.toml" "$fixture_dir/src/lib.rs" "$fixture_dir/src/zst.rs" \
    "$fixture_dir/src/bin/layout.rs" \
    "$fixture_dir/src/u64_controls.rs" "$classifier" "$0" .github/workflows/smallsort-research.yml; do
    git ls-files --error-unmatch "$path" >/dev/null 2>&1 || { echo "Input not committed: $path" >&2; exit 2; }
    git diff --quiet HEAD -- "$path" || { echo "Input differs from dispatched commit: $path" >&2; exit 2; }
done

out=research-results/rapx-applicability
mkdir -p "$out/mir"
runner_started=$(date +%s)
started=${RAPX_JOB_STARTED_EPOCH:-$runner_started}
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
Checkpoint flags: --mode targeted --postfix-repeat auto --prepare-targets --debug-contracts
Logging: RAPX_LOG=debug
MIR dump: -Zdump-mir=all (fixture only)
EOT
uname -a >> "$out/experiment-environment.txt"
git status --short --branch >> "$out/experiment-environment.txt"
sha256sum "$target" research/challenge-8/SORT4-CONTRACT.md "$fixture_dir/Cargo.toml" \
    "$fixture_dir/src/lib.rs" "$fixture_dir/src/zst.rs" "$fixture_dir/src/u64_controls.rs" \
    "$fixture_dir/src/bin/layout.rs" \
    "$classifier" "$0" .github/workflows/smallsort-research.yml >> "$out/experiment-environment.txt"
git rev-parse "HEAD:$target" >> "$out/experiment-environment.txt"
target_blob=$(git rev-parse "HEAD:$target")
if [[ "$target_blob" != e555fce440872898e47fd5114f32eb15401d07df ]]; then
    echo "SmallSort target blob mismatch: $target_blob" | tee "$out/setup-blocker.txt"
    exit 3
fi

crate_archive="$RUNNER_TEMP/rapx-$rapx_version.crate"
curl --fail --location --silent --show-error \
    "https://static.crates.io/crates/rapx/rapx-$rapx_version.crate" -o "$crate_archive"
actual_package_sha=$(sha256sum "$crate_archive" | cut -d ' ' -f 1)
printf 'Downloaded archive SHA256: %s\n' "$actual_package_sha" >> "$out/experiment-environment.txt"
if [[ "$actual_package_sha" != "$expected_package_sha" ]]; then
    echo 'RAPx crate archive identity mismatch' | tee "$out/setup-blocker.txt"
    exit 3
fi
tar -xOf "$crate_archive" "rapx-$rapx_version/.cargo_vcs_info.json" > "$out/package-vcs-info.json"
tar -xOf "$crate_archive" "rapx-$rapx_version/Cargo.lock" > "$out/installed-package-Cargo.lock"
tar -xOf "$crate_archive" "rapx-$rapx_version/Cargo.toml" > "$out/installed-package-Cargo.toml"
sha256sum "$out/installed-package-Cargo.lock" "$out/installed-package-Cargo.toml" >> "$out/experiment-environment.txt"
cat "$out/package-vcs-info.json" >> "$out/experiment-environment.txt"

rustup toolchain install "$toolchain" --profile minimal
rustup component add rustc-dev rust-src llvm-tools-preview --toolchain "$toolchain"
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

cargo +"$toolchain" install rapx --version "=$rapx_version" --locked --force 2>&1 | tee "$out/cargo-install.log"
RAPXFLAGS=--version rapx > "$out/rapx-version.txt" 2>&1
cargo +"$toolchain" rapx --version >> "$out/rapx-version.txt" 2>&1
if ! grep -Eq "(^|[[:space:]])$rapx_version([[:space:]]|$)" "$out/rapx-version.txt"; then
    echo 'Installed RAPx executable did not report the exact pinned version' | tee "$out/setup-blocker.txt"
    exit 3
fi
sha256sum "$(command -v rapx)" "$(command -v cargo-rapx)" >> "$out/experiment-environment.txt"
cat "$out/rapx-version.txt" >> "$out/experiment-environment.txt"
cargo +"$toolchain" install --list > "$out/cargo-install-list.txt"

registry_source=$(find "${CARGO_HOME:-$HOME/.cargo}/registry/src" -path "*/rapx-$rapx_version/src/verify" -type d -print -quit)
[[ -n "$registry_source" ]] || { echo 'Installed RAPx source tree unavailable' | tee "$out/setup-blocker.txt"; exit 3; }
registry_root=${registry_source%/src/verify}
package_metadata=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("package"))' "$registry_root/.cargo-checksum.json")
printf 'Cargo installed package checksum: %s\n' "$package_metadata" >> "$out/experiment-environment.txt"
[[ "$package_metadata" == "$expected_package_sha" ]] || {
    echo 'Installed Cargo package checksum mismatch' | tee "$out/setup-blocker.txt"; exit 3;
}

# Compare installed verifier/checker/contract/display sources bytewise with
# the pinned upstream tree. No source patch or fallback is accepted.
upstream="$RUNNER_TEMP/rapx-upstream"
git init -q "$upstream"
git -C "$upstream" remote add origin https://github.com/safer-rust/RAPx.git
git -C "$upstream" fetch --quiet --depth=1 origin "$rapx_vcs"
git -C "$upstream" checkout --quiet --detach FETCH_HEAD
[[ "$(git -C "$upstream" rev-parse HEAD)" == "$rapx_vcs" ]] || {
    echo 'Fetched RAPx upstream source identity mismatch' | tee "$out/setup-blocker.txt"; exit 3;
}
upstream_src="$upstream/rapx/src"
[[ -d "$upstream_src/verify" ]] || upstream_src="$upstream/src"
diff -qr "$registry_root/src/verify" "$upstream_src/verify" > "$out/source-diff-verify.txt" || {
    echo 'Installed verifier sources differ from reviewed upstream profile' | tee "$out/setup-blocker.txt"; exit 3;
}
diff -qr "$registry_root/src/helpers" "$upstream_src/helpers" > "$out/source-diff-helpers.txt" || {
    echo 'Installed helper sources differ from reviewed upstream profile' | tee "$out/setup-blocker.txt"; exit 3;
}
for rel in cli/verify.rs helpers/mir_scan.rs; do
    cmp "$registry_root/src/$rel" "$upstream_src/$rel" || {
        echo "Installed RAPx source differs at $rel" | tee "$out/setup-blocker.txt"; exit 3;
    }
done
(
    cd "$registry_root/src"
    find verify helpers -type f -print0 | sort -z | xargs -0 sha256sum
) > "$out/installed-relevant-source-hashes.txt"
(
    cd "$upstream_src"
    find verify helpers -type f -print0 | sort -z | xargs -0 sha256sum
) > "$out/reviewed-relevant-source-hashes.txt"
cmp "$out/installed-relevant-source-hashes.txt" "$out/reviewed-relevant-source-hashes.txt" || {
    echo 'Installed/reviewed relevant source hash lists differ' | tee "$out/setup-blocker.txt"; exit 3;
}
printf 'Installed relevant source comparison: byte-identical\n' >> "$out/experiment-environment.txt"

export RUSTFLAGS="--cfg=rapx -Zdump-mir=all -Zdump-mir-dir=$(pwd)/$out/mir"
export RAPX_LOG=debug

(cd "$fixture_dir" && cargo +"$toolchain" run --bin layout) 2>&1 | tee "$out/type-layout.log"
printf 'Type layout run exit code: %s\n' "${PIPESTATUS[0]}" >> "$out/experiment-environment.txt"
if ! grep -Eq 'zst\.size=0 zst\.align=8 u64\.size=8 u64\.align=8' "$out/type-layout.log"; then
    echo 'Expected ZST/u64 size and alignment were not observed on the hosted target' | tee "$out/setup-blocker.txt"
    exit 3
fi

if (cd "$fixture_dir" && cargo +"$toolchain" rapx verify --prepare-targets --debug-contracts --mode targeted \
    --crate rapx-applicability --postfix-repeat auto -- --lib) 2>&1 | tee "$out/prepare-targets.log"; then
    printf '0\n' > "$out/prepare-targets-exit-code.txt"
else
    code=${PIPESTATUS[0]}
    printf '%s\n' "$code" > "$out/prepare-targets-exit-code.txt"
    echo 'Target preparation failed; alignment analyses not started' | tee "$out/setup-blocker.txt"
    exit "$code"
fi

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
    IFS=: read -r name module <<< "$item"
    now=$(date +%s)
    remaining=$(( budget * 60 - (now - started) ))
    if (( remaining <= 0 )); then
        printf '124\n' > "$out/$name-exit-code.txt"
        printf '{"case":"%s","outcome":"TIMEOUT_NOT_RUN"}\n' "$name" > "$out/$name.json"
        suite_exit=124
        break
    fi
    log="$out/$name.log"
    printf '\n=== RAPx gate A case: %s / module %s ===\n' "$name" "$module"
    if /usr/bin/time -v -o "$out/$name-resources.txt" timeout --signal=TERM --kill-after=30s "${remaining}s" \
        bash -c 'cd "$1" && RAPX_LOG=debug cargo +nightly-2026-02-05 rapx verify --mode targeted --crate rapx-applicability --module "$2" --postfix-repeat auto --debug-contracts -- --lib' \
        _ "$fixture_dir" "$module" 2>&1 | tee "$log"; then
        raw_code=0
    else
        raw_code=${PIPESTATUS[0]}
    fi
    printf '%s\n' "$raw_code" > "$out/$name-exit-code.txt"
    python3 "$classifier" --case "$name" --exit-code "$raw_code" --log "$log" \
        --contracts "$log" --out "$out/$name.json" || true
    if (( raw_code == 124 )); then suite_exit=124; break; fi
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
find "$out" -type f ! -name artifact-sha256.txt -print0 | sort -z | xargs -0 sha256sum > "$out/artifact-sha256.txt"
exit "$suite_exit"
