#!/usr/bin/env bash
# Exact-source, single-pass upstream Linux make test; Cloud execution only.
set -euo pipefail
[[ "${1:-}" == verifast-slice-upstream ]] || exit 2
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || exit 2

infra_root=${INFRA_ROOT:-/workspace/infra}
proof_root=${PROOF_ROOT:-/workspace/proof}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
all="$evidence_root/allprooflogs"
work=/workspace/verifast-slice-upstream
source_repo="$work/source"
candidate="$work/candidate"
stock="$work/verifast-26.10"
deps="$work/vfdeps-adf88dc"
deadline=${SMALLSORT_DEADLINE_EPOCH:?}
base=0a83dba42db7ce0b445034ece5298afe980e57dc
head=1ef8474610274bbf9d0652613ac2cabbb1fc476b
tree=f21bda99968f8dc7fee4de3303768b0ecb4ddf55
rustc_commit=f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f
stock_sha=5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd
deps_sha=8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580
rustup_sha=20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c
llvm_sha=7bc39ea82589679a10a4d03cbd7e1d032fffb644774aff60a46bdf973171ef7a
input="$proof_root/research/challenge-8/verifast-input/$head"
cloud_dir="$infra_root/research/challenge-8/cloud-build"
mkdir -p "$all" "$work"
[[ -z "$(find "$all" -mindepth 1 -print -quit)" ]] || exit 2
status=1
stage=initial
finished=0
finish() { local rc=$?; trap - EXIT; python3 "$cloud_dir/slice-upstream-audit.py" "$all" "$rc" "$stage" > "$evidence_root/proof-audit.json" || true; exit "$rc"; }
trap finish EXIT

remaining() {
  local seconds=$((deadline-$(date +%s)))
  (( seconds > 0 )) || return 124
  printf '%s\n' "$seconds"
}
snapshot() {
  local name=$1
  { date -u +%FT%TZ; ps -eo pid,ppid,stat,etimes,%cpu,%mem,rss,comm,args --sort=-rss | head -80
    cat /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.events /sys/fs/cgroup/cpu.stat 2>/dev/null || true
    df -h /workspace; free -m; } > "$all/$name" 2>&1 || true
}
run_stage() {
  local name=$1 limit=$2 cwd=$3 mode=$4; shift 4
  local budget rc=0 watcher=
  stage=$name
  budget=$(remaining) || return 124
  (( budget > limit )) && budget=$limit
  if [[ "$name" == make-test ]]; then
    (sleep "$((budget>10?budget-10:1))"; snapshot make-test-before-timeout.txt) & watcher=$!
  fi
  if [[ "$mode" == combined ]]; then
    /usr/bin/time -v -o "$all/$name-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${budget}s" \
      bash -c 'cd "$1"; shift; exec "$@"' bash "$cwd" "$@" \
      > "$all/$name.stdout.log" 2>&1 || rc=$?
    printf 'combined into %s\n' "$name.stdout.log" > "$all/$name.stderr.log"
  else
    /usr/bin/time -v -o "$all/$name-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${budget}s" \
      bash -c 'cd "$1"; shift; exec "$@"' bash "$cwd" "$@" \
      > "$all/$name.stdout.log" 2> "$all/$name.stderr.log" || rc=$?
  fi
  if [[ -n "$watcher" ]]; then kill "$watcher" 2>/dev/null || true; wait "$watcher" 2>/dev/null || true; fi
  printf '%s\n' "$rc" > "$all/$name-exit-code.txt"
  if (( rc == 124 || rc == 137 )); then snapshot "$name-after-timeout.txt"; fi
  return "$rc"
}

[[ -d "$infra_root" && -d "$proof_root" && -f "$input/bundle" && -f "$input/manifest" ]] || exit 2
python3 "$cloud_dir/provider.py" > "$all/provider.json"
python3 - "$evidence_root/source-input-certificate.json" "$infra_root" "$proof_root" "$all/source-identity.json" <<'IDENTITY'
import json,pathlib,subprocess,sys
cert,infra,proof,out=map(pathlib.Path,sys.argv[1:])
c=json.loads(cert.read_text())
assert c['lane']=='verifast-slice-upstream'
for key,root in [('infra',infra),('proof',proof)]:
 assert c[key]['commit']==c[key]['head']==subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
 assert c[key]['commit']==__import__('os').environ[key.upper()+'_SHA']
assert c['infra']['head']==c['proof']['head']
out.write_text(json.dumps({'infra_sha':c['infra']['head'],'proof_sha':c['proof']['head'],
 'source_input_archive_sha256':c['archive_sha256'],'infra_tree':c['infra']['root_tree'],
 'proof_tree':c['proof']['root_tree']},indent=2,sort_keys=True)+'\n')
IDENTITY
cp "$input/bundle" "$all/tool-input.bundle"
cp "$input/manifest" "$all/tool-input.manifest"
export RUSTUP_HOME="$work/rustup" CARGO_HOME="$work/cargo" TMPDIR="$work/tmp"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25 LANG=C.UTF-8 LC_ALL=C.UTF-8
mkdir -p "$RUSTUP_HOME" "$CARGO_HOME" "$TMPDIR"
export PATH="$CARGO_HOME/bin:$PATH"
printf 'base=%s\nhead=%s\ntree=%s\nNUMCPU=4\n' "$base" "$head" "$tree" > "$all/fullmake-plan.txt"

run_stage package-index 300 /workspace split apt-get update
run_stage packages-install 300 /workspace split apt-get install --yes --no-install-recommends \
  build-essential m4 patch unzip capnproto ripgrep time libgmp10 libmpfr6 libgomp1 \
  libffi8 libncurses6 libtinfo6 zlib1g libz3-4 libgtk-3-0 libgtksourceview-4-0 cmake ninja-build
{ cmake --version; ninja --version; } > "$all/build-dependencies.txt"
run_stage vfdeps-download 180 /workspace split curl -fL --retry 2 \
  -o "$work/vfdeps-adf88dc-linux.txz" https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' "$deps_sha" "$work/vfdeps-adf88dc-linux.txz" | sha256sum -c - > "$all/vfdeps-sha256.txt"
run_stage vfdeps-extract 120 /workspace split tar -xjf "$work/vfdeps-adf88dc-linux.txz" -C "$work"
[[ -d "$deps" ]] || exit 2
for prefix in /vfdeps-adf88dc /tmp/vfdeps-adf88dc; do
  if [[ ! -e "$prefix" ]]; then ln -s "$deps" "$prefix"; fi
  [[ "$(readlink -f "$prefix")" == "$deps" ]] || exit 2
done
export PATH="$deps/bin:$PATH" CAPNP_INC_DIR="$deps/include"
run_stage stock-download 180 /workspace split curl -fL --retry 2 \
  -o "$work/verifast-26.10-linux.tar.gz" https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' "$stock_sha" "$work/verifast-26.10-linux.tar.gz" | sha256sum -c - > "$all/stock-sha256.txt"
run_stage stock-extract 120 /workspace split tar -xzf "$work/verifast-26.10-linux.tar.gz" -C "$work"
run_stage checkout 240 /workspace split git clone --no-checkout https://github.com/verifast/verifast.git "$source_repo"
run_stage base-checkout 120 /workspace split git -C "$source_repo" checkout --detach "$base"
[[ "$(git -C "$source_repo" rev-parse HEAD)" == "$base" ]] || exit 2
python3 "$cloud_dir/restore-slice-upstream.py" "$source_repo" "$input" "$candidate" > "$all/restore.json"
[[ "$(git -C "$candidate" rev-parse HEAD)" == "$head" && "$(git -C "$candidate" rev-parse HEAD^{tree})" == "$tree" ]] || exit 2

run_stage rustup-download 180 /workspace split curl -fL --retry 2 \
  -o "$work/rustup-init-1.28.2" https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
printf '%s  %s\n' "$rustup_sha" "$work/rustup-init-1.28.2" | sha256sum -c - > "$all/rustup-sha256.txt"
chmod +x "$work/rustup-init-1.28.2"
run_stage rustup-init 120 /workspace split "$work/rustup-init-1.28.2" -y --no-modify-path --default-toolchain none --profile minimal
run_stage compiler-install 300 /workspace split rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal \
  --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
rustc --version --verbose > "$all/rustc.verbose.txt"
[[ "$(rg '^commit-hash:' "$all/rustc.verbose.txt" | cut -d' ' -f2)" == "$rustc_commit" ]] || exit 2
printf '%s\n' "$compiler_sysroot" > "$all/rustc.sysroot.txt"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock/bin:$deps/lib:${LD_LIBRARY_PATH:-}"
run_stage decoder-install 300 /workspace split cargo install --locked --git \
  https://github.com/btj/capnpc-ocaml-decoder --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
run_stage llvm-download 180 /workspace split curl -fL --retry 2 \
  -o "$work/vf-llvm-clang-build-5710e1b-Linux.tar.gz" \
  https://github.com/verifast/vf-llvm-clang-build/releases/download/v3/vf-llvm-clang-build-5710e1b-Linux.tar.gz
printf '%s  %s\n' "$llvm_sha" "$work/vf-llvm-clang-build-5710e1b-Linux.tar.gz" | sha256sum -c - > "$all/llvm-sha256.txt"
run_stage llvm-extract 180 /workspace split tar -xzf "$work/vf-llvm-clang-build-5710e1b-Linux.tar.gz" -C /
[[ -d /vf-llvm-clang-build-5710e1b ]] || exit 2
if [[ ! -e /tmp/vf-llvm-clang-build-5710e1b ]]; then ln -s /vf-llvm-clang-build-5710e1b /tmp/vf-llvm-clang-build-5710e1b; fi
[[ "$(readlink -f /tmp/vf-llvm-clang-build-5710e1b)" == /vf-llvm-clang-build-5710e1b ]] || exit 2
export VF_LLVM_INSTALL_DIR=/tmp/vf-llvm-clang-build-5710e1b VF_VFDEPS_DIR="$deps"

# Copy specification/runtime data, then remove every executable rebuilt by
# make test; a 26.10 binary cannot stand in for the changed master sources.
mkdir -p "$candidate/bin" "$candidate/lib"
cp -an "$stock/bin/." "$candidate/bin/"
[[ ! -d "$stock/lib" ]] || cp -an "$stock/lib/." "$candidate/lib/"
for name in verifast vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter; do rm -f "$candidate/bin/$name"; done
python3 - "$candidate" "$all/pre-build-components.json" <<'BEFORE'
import json,pathlib,sys
root=pathlib.Path(sys.argv[1]); names=['verifast','vf-rust-mir-exporter','refinement-checker','vf-cxx-ast-exporter']
assert all(not (root/'bin'/x).exists() for x in names)
pathlib.Path(sys.argv[2]).write_text(json.dumps({'removed_stock_binaries':names,
 'all_absent_before_build':True},indent=2,sort_keys=True)+'\n')
BEFORE
python3 - "$candidate" "$all/conditional-components.json" <<'CONDITIONAL'
import json,os,pathlib,shutil,sys
root=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])
record={'schema':'verifast-fullmake-conditional-components-v1',
 'assignment_models_directory_present':(root/'assignments').is_dir(),
 'assignment_models_script_present':(root/'assignments/run_model_solutions.mysh').is_file(),
 'java_ast_server_enabled':bool(os.environ.get('VERIFAST_JAVA_AST_SERVER')),
 'rocq_coqc_available':shutil.which('coqc') is not None,
 'z3_in_path':shutil.which('z3') is not None,
 'z3v45_in_path':shutil.which('z3v4.5') is not None,
 'stock_z3_binary_present':(root/'bin/z3').is_file()}
out.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
CONDITIONAL
# Baseline build uses exact base translator. Test bytes stay the candidate's.
cp "$candidate/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" "$work/candidate-translator.ml"
git -C "$candidate" show "$base:src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" > "$candidate/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
run_stage baseline-build 600 "$candidate/src" split make build NUMCPU=4 WITHOUT_LABLGTK=1
sha256sum "$candidate/bin/verifast" > "$all/baseline-binary.sha256"
baseline_rc=0
run_stage baseline-missing-binding 60 "$candidate/tests/rust/safe_abstraction" split "$candidate/bin/verifast" slice_as_mut_ptr.rs || baseline_rc=$?
[[ "$baseline_rc" == 1 ]] || exit 3
cp "$work/candidate-translator.ml" "$candidate/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
[[ -z "$(git -C "$candidate" diff --name-only)" ]] || exit 2
run_stage candidate-build 300 "$candidate/src" split make build NUMCPU=4 WITHOUT_LABLGTK=1
sha256sum "$candidate/bin/"{verifast,vf-rust-mir-exporter,refinement-checker,vf-cxx-ast-exporter} > "$all/candidate-binaries.sha256"
cp "$compiler_sysroot/lib/rustlib/src/rust/library/core/src/slice/mod.rs" "$all/compiler-slice-mod.rs"
sha256sum "$all/compiler-slice-mod.rs" > "$all/compiler-slice-source.sha256"
mkdir -p "$all/cases/slice-binding"
cp "$candidate/tests/rust/safe_abstraction/"slice_as_mut_ptr*.rs "$all/cases/slice-binding/"
run_stage positive 120 "$candidate/tests/rust/safe_abstraction" split "$candidate/bin/verifast" -dump_ast_with_locs "$all/cases/slice-binding/positive.ast" slice_as_mut_ptr.rs
run_stage negative-marked 120 "$candidate/tests/rust/safe_abstraction" split "$candidate/bin/verifast" -allow_should_fail slice_as_mut_ptr_no_init.rs
negative_rc=0
run_stage negative-diagnostic 120 "$candidate/tests/rust/safe_abstraction" split "$candidate/bin/verifast" slice_as_mut_ptr_no_init.rs || negative_rc=$?
[[ "$negative_rc" == 1 ]] || exit 3
run_stage positive-mir 120 "$candidate/tests/rust/safe_abstraction" split "$candidate/bin/vf-rust-mir-exporter" slice_as_mut_ptr.rs "--sysroot=$compiler_sysroot" --crate-type lib
run_stage positive-mir-decode 60 "$candidate" split capnp decode "$candidate/src/rust_frontend/vf_mir/vf_mir.capnp" VfMir < "$all/positive-mir.stdout.log"
snapshot make-test-before.txt
run_stage make-test 800 "$candidate/src" split make test NUMCPU=4
snapshot make-test-after.txt
python3 "$cloud_dir/slice-upstream-audit.py" "$all" 0 completed > "$evidence_root/proof-audit.json"
