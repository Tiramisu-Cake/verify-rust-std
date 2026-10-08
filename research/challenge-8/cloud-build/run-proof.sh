#!/usr/bin/env bash
# SmallSort B stock diagnostics and C source-built constructor component.
set -euo pipefail

lane=${1:?usage: run-proof.sh stock|constructor}
[[ "$lane" == stock || "$lane" == constructor ]] || exit 2
proof_root=${PROOF_ROOT:-/workspace/proof}
infra_root=${INFRA_ROOT:-/workspace/infra}
cloud_dir=${INFRA_CLOUD_DIR:-$infra_root/research/challenge-8/cloud-build}
work_root=${WORK_ROOT:-/workspace/smallsort-work}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
deadline=${SMALLSORT_DEADLINE_EPOCH:?SMALLSORT_DEADLINE_EPOCH is required}
if [[ "$lane" == stock ]]; then
  proof_sha=a0cfd30e066acbaf1b5406cd9773f54388cc45be
else
  proof_sha=1378f0ffc8342233349fae3df5a938c4a021c8d7
fi
for path in "$proof_root" "$infra_root" "$work_root" "$evidence_root"; do
  [[ "$path" == /workspace/* ]] || { printf 'path outside /workspace: %s\n' "$path" >&2; exit 2; }
done
mkdir -p "$work_root" "$evidence_root"
ev="$evidence_root/allprooflogs"
cases="$ev/cases"
mkdir -p "$ev"
if [[ -n "$(find "$ev" -mindepth 1 -print -quit)" ]]; then
  printf 'evidence lane already contains files: %s\n' "$ev" >&2; exit 2
fi
CURRENT_STAGE=provider
write_incomplete_audit() {
  local status=$?
  if (( status != 0 )) && [[ ! -f "$evidence_root/proof-audit.json" ]]; then
    python3 - "$evidence_root/proof-audit.json" "$lane" "$status" "$CURRENT_STAGE" <<'FAILURE'
import json,pathlib,sys
path,lane,status,stage=sys.argv[1:]
pathlib.Path(path).write_text(json.dumps({
 "accepted":False,"classification":"INCONCLUSIVE","lane":lane,
 "exit_status":int(status),"failed_stage":stage,
 "evidence_root":"allprooflogs"},indent=2,sort_keys=True)+"\n")
FAILURE
  fi
  return "$status"
}
trap write_incomplete_audit EXIT
git -C "$proof_root" rev-parse --git-dir >/dev/null
[[ -d "$cloud_dir" ]] || exit 2
[[ "$(git -C "$proof_root" rev-parse HEAD)" == "$proof_sha" ]] || {
  printf 'proof checkout SHA mismatch\n' >&2; exit 2;
}

require_provider() {
  if [[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]]; then
    CLOUD_BUILD_ID=${CLOUD_BUILD_ID:?CLOUD_BUILD_ID is required} \
    CLOUD_BUILD_PROJECT_ID=${CLOUD_BUILD_PROJECT_ID:?CLOUD_BUILD_PROJECT_ID is required} \
    CLOUD_BUILD_REGION=${CLOUD_BUILD_REGION:?CLOUD_BUILD_REGION is required} \
    python3 "$cloud_dir/provider.py" > "$ev/provider.json"
  elif [[ -z "${SMALLSORT_EXECUTION_PROVIDER:-}" &&
          "${GITHUB_ACTIONS:-}" == true &&
          "${RUNNER_ENVIRONMENT:-}" == github-hosted &&
          "${RUNNER_OS:-}" == Linux ]]; then
    python3 "$cloud_dir/provider.py" > "$ev/provider.json"
  else
    printf 'explicit cloud-build identity or genuine GitHub-hosted identity required\n' >&2
    exit 2
  fi
}
require_provider

remaining() {
  local seconds=$((deadline - $(date +%s)))
  (( seconds > 0 )) || { printf 'deadline elapsed\n' >&2; exit 124; }
  printf '%s' "$seconds"
}

stage() {
  local name=$1; shift
  CURRENT_STAGE=$name
  local code=0
  local budget
  budget=$(remaining)
  /usr/bin/time -v -o "$ev/$name-resources.txt" \
    timeout --signal=TERM --kill-after=10s "${budget}s" "$@" \
    > "$ev/$name.log" 2>&1 || code=$?
  printf '%s\n' "$code" > "$ev/$name-exit-code.txt"
  cat "$ev/$name.log"
  (( code == 0 )) || return "$code"
  CURRENT_STAGE=complete
}

# Apply only the two audited provider-guard checker overlays to the frozen proof
# checkout. Full source bytes and guard-only diffs are recorded before use.
python3 - "$proof_root" "$cloud_dir" "$ev" "$lane" <<'OVERLAY'
import difflib, hashlib, json, pathlib, shutil, sys
proof, cloud_dir, evidence = map(pathlib.Path, sys.argv[1:4])
lane = sys.argv[4]
sha = lambda b: hashlib.sha256(b).hexdigest()
proof_sha = "a0cfd30e066acbaf1b5406cd9773f54388cc45be" if lane == "stock" else "1378f0ffc8342233349fae3df5a938c4a021c8d7"
import subprocess
if subprocess.check_output(["git", "-C", str(proof), "rev-parse", "HEAD"], text=True).strip() != proof_sha:
    raise SystemExit("unexpected proof SHA in overlay phase")
specs = [
 ("research/challenge-8/check-stock-2610.py",
  "overlays/check-stock-2610.py",
  "5abbbddec6acf29c77d47ed7748c0232ac6a3e87fe5d35eea19092d002c7127c",
  "88e6275d6231d5913257d82f32e576e4bcd45b7654992fc040bf499245cdcbc5",
  b" assert os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_ENVIRONMENT')=='github-hosted'\n",
  b" provider_path = Path(__file__).resolve().parent / 'cloud-build' / 'provider.py'\n spec = importlib.util.spec_from_file_location('smallsort_provider', provider_path)\n provider = importlib.util.module_from_spec(spec); spec.loader.exec_module(provider)\n provider.require_supported_provider()\n"),
 ("research/challenge-8/overnight-s6/check-maybeuninit-new-pointer.py",
  "overlays/check-maybeuninit-new-pointer.py",
  "07bf73f75135515a1de69e83cfb8b4525368a34f7acccb3c564e1dfde163b5ff",
  "2d4c7f3ee027ae55cb016321d26f59d5ece28cddcc780c10efedb39ed19c3ded",
  b'    if os.environ.get("GITHUB_ACTIONS") != "true" or \\\n            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \\\n            os.environ.get("RUNNER_OS") != "Linux":\n        raise SystemExit("MaybeUninit constructor checks require GitHub-hosted Linux Actions")\n',
  b'    provider_path = Path(__file__).resolve().parents[1] / "cloud-build" / "provider.py"\n    spec = importlib.util.spec_from_file_location("smallsort_provider", provider_path)\n    provider = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(provider)\n    provider.require_supported_provider()\n'),
]
if lane == "stock":
    specs = specs[:1]
manifest = {"proof_sha": proof_sha, "files": []}
for rel, overlay_rel, base_sha, overlay_sha, old, new in specs:
    target = proof / rel
    original = target.read_bytes()
    overlay = (cloud_dir / overlay_rel).read_bytes()
    if sha(original) != base_sha or sha(overlay) != overlay_sha:
        raise SystemExit(f"provider overlay pin mismatch: {rel}")
    if original.count(old) != 1 or original.replace(old, new, 1) != overlay:
        raise SystemExit(f"overlay changes more than provider guard: {rel}")
    target.write_bytes(overlay)
    manifest["files"].append({
        "path": rel, "base_sha256": base_sha, "overlay_sha256": overlay_sha,
        "diff": "".join(difflib.unified_diff(
            original.decode().splitlines(True), overlay.decode().splitlines(True),
            fromfile=rel + ".base", tofile=rel + ".cloud-build")),
        "guard_only": True,
    })
provider_dest = proof / "research/challenge-8/cloud-build/provider.py"
provider_dest.parent.mkdir(parents=True, exist_ok=True)
provider_src = cloud_dir / "provider.py"
audit_src = cloud_dir / "proof-audit.py"
if sha(provider_src.read_bytes()) != "771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616":
    raise SystemExit("provider helper pin mismatch")
if sha(audit_src.read_bytes()) != "5e0e0a0b9294cd1499afed9801963905441baf822dc708b9dc62f6fb58d998b6":
    raise SystemExit("proof audit pin mismatch")
shutil.copyfile(provider_src, provider_dest)
manifest["provider_sha256"] = sha(provider_dest.read_bytes())
shutil.copyfile(audit_src, provider_dest.parent / "proof-audit.py")
manifest["proof_audit_sha256"] = sha(audit_src.read_bytes())
(evidence / "provider-overlay-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
OVERLAY

cd "$proof_root"

export RUSTUP_HOME="$work_root/rustup"
export CARGO_HOME="$work_root/cargo"
export PATH="$CARGO_HOME/bin:$PATH"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export SORT4_SELECT_PROFILE=experimental-s6-26.10-v1
mkdir -p "$RUSTUP_HOME" "$CARGO_HOME"
mkdir -p "$work_root/tmp"
export TMPDIR="$work_root/tmp"
task_temp="$work_root/$lane"
mkdir -p "$task_temp"
stock_archive="$task_temp/verifast-26.10-linux.tar.gz"
stock_home="$task_temp/verifast-26.10"
source_home="$task_temp/source"
schema="$source_home/src/rust_frontend/vf_mir/vf_mir.capnp"

if [[ "$lane" == stock ]]; then
  profile=stock-26.10-baseline-v1
  patches=NONE
else
  profile=source-built-s6-cfg-constructor-26.10-v1
  patches=S6-20f7d07ac9bdaca7+CFG-593d09405379974f
fi
printf 'lane=%s\nproof_sha=%s\nprofile=%s\npatches=%s\n' \
  "$lane" "$proof_sha" "$profile" "$patches" > "$ev/environment.txt"
printf 'provider=%s\n' "$(cat "$ev/provider.json")" >> "$ev/environment.txt"
printf 'SMALLSORT_DEADLINE_EPOCH=%s\n' "$deadline" >> "$ev/environment.txt"

stage package-index apt-get update
runtime_packages=(capnproto ripgrep time libgmp10 libmpfr6 libgomp1 libffi8 \
  libncurses6 libtinfo6 zlib1g libz3-4 libgtk-3-0 libgtksourceview-4-0)
if [[ "$lane" == stock ]]; then
  stage packages-install apt-get install --yes --no-install-recommends "${runtime_packages[@]}"
else
  stage packages-install apt-get install --yes --no-install-recommends \
    build-essential m4 patch unzip "${runtime_packages[@]}"
fi
stage download curl -fL --retry 2 -o "$stock_archive" \
  https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' 5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd \
  "$stock_archive" | sha256sum -c - > "$ev/archive-sha256.log"
stage extract tar -xzf "$stock_archive" -C "$task_temp"
stage source-checkout git clone --depth 1 --branch 26.10 \
  https://github.com/verifast/verifast.git "$source_home"
[[ "$(git -C "$source_home" rev-parse HEAD)" == f76012fb518703b1d98e243ac4f487f16877cfcb ]] || exit 2
[[ "$(sha256sum "$schema" | cut -d' ' -f1)" == f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469 ]] || exit 2
rustup_init="$work_root/rustup-init-1.28.2"
stage rustup-init-download curl -fL --retry 2 -o "$rustup_init" \
  https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
printf '%s  %s\n' 20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c \
  "$rustup_init" | sha256sum -c - > "$ev/rustup-init-sha256.log"
chmod +x "$rustup_init"
stage rustup-init "$rustup_init" -y --no-modify-path --default-toolchain none --profile minimal
stage compiler rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal \
  --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
rustc --version --verbose > "$ev/compiler-version.txt"
python3 - "$ev/compiler-version.txt" "$ev/tools.json" <<'TOOLPIN'
import json,pathlib,sys
text=pathlib.Path(sys.argv[1]).read_text()
rows=dict(line.split(": ",1) for line in text.splitlines() if ": " in line)
if rows.get("commit-hash") != "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f":
 raise SystemExit("nightly compiler commit differs from frozen pin")
if rows.get("host") != "x86_64-unknown-linux-gnu":
 raise SystemExit("compiler target differs from frozen pin")
pathlib.Path(sys.argv[2]).write_text(json.dumps({"rustc":rows,"verifast_source_sha":"f76012fb518703b1d98e243ac4f487f16877cfcb","std_base_sha":"cd371e035c7e573760c43bf934d53e8118ee3e7d","rustup_init_version":"1.28.2"},indent=2)+"\n")
TOOLPIN
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock_home/bin:${LD_LIBRARY_PATH:-}"

python3 - "$stock_home" "$source_home" "$ev" "$compiler_sysroot" <<'AUDIT'
import hashlib,json,pathlib,sys
home,src,ev,sysroot=map(pathlib.Path,sys.argv[1:])
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows={}
for p in sorted((home/'bin/rust').rglob('*')):
 if p.is_file():
  rel=p.relative_to(home)
  if p.suffix=='.rsspec' and (not (src/rel).is_file() or p.read_bytes()!=(src/rel).read_bytes()):
   raise SystemExit(f'stock specification source mismatch: {rel}')
  rows[str(rel)]={'sha256':h(p),'source_exists':(src/rel).is_file(),
   'source_equal':(src/rel).is_file() and p.read_bytes()==(src/rel).read_bytes(),
   'effective_rsspec':p.suffix=='.rsspec'}
stock={str(p.relative_to(home)) for p in (home/'bin/rust').rglob('*.rsspec')}
source={str(p.relative_to(src)) for p in (src/'bin/rust').rglob('*.rsspec')}
if stock!=source: raise SystemExit('stock specification inventory differs')
(ev/'stock-spec-hashes.json').write_text(json.dumps(rows,indent=2)+'\n')
parts=['src/rust_frontend/vf_mir_exporter','src/rust_frontend/vf_mir_decoder','src/refinement_checker']
for root in parts:
 for p in sorted((src/root).rglob('*')):
  if p.is_file(): rows[str(p.relative_to(src))]=h(p)
for rel in ['src/rust_frontend/vf_mir/vf_mir.capnp',
            'src/rust_frontend/vf_mir_decoder/dune',
            'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',
            'src/rust_frontend/vf_mir_exporter/src/main.rs']:
 rows[rel]=h(src/rel)
(ev/'source-component-hashes.json').write_text(json.dumps(rows,indent=2)+'\n')
rows={str(p.relative_to(home)):h(p) for p in sorted((home/'bin').iterdir()) if p.is_file()}
(ev/'binary-hashes.json').write_text(json.dumps(rows,indent=2)+'\n')
files=['core/src/mem/mod.rs','core/src/mem/manually_drop.rs','core/src/mem/maybe_uninit.rs',
 'core/src/ptr/mod.rs','core/src/slice/sort/shared/smallsort.rs']
std={}
for rel in files:
 a=pathlib.Path('library')/rel; b=sysroot/'lib/rustlib/src/rust/library'/rel
 std[rel]={'repo_sha256':h(a),'sysroot_sha256':h(b),'equal':a.read_bytes()==b.read_bytes()}
(ev/'std-export-source.json').write_text(json.dumps({'sysroot':str(sysroot),
 'fixture_body_source':'repository library/core/src/mem/mod.rs exact forget body; external std metadata from nightly sysroot, not a repository std build',
 'files':std},indent=2)+'\n')
AUDIT

{
  rustc --version --verbose
  capnp --version
  sha256sum "$stock_archive" "$stock_home/bin/verifast" \
    "$stock_home/bin/vf-rust-mir-exporter" "$stock_home/bin/refinement-checker" \
    "$stock_home/bin/rust/std/lib.rsspec"
  cat "$source_home/rust-toolchain.toml"
} >> "$ev/environment.txt"
ldd "$stock_home/bin/verifast" > "$ev/console-ldd.txt"
if rg -q 'not found' "$ev/console-ldd.txt"; then exit 2; fi

if [[ "$lane" == stock ]]; then
  baseline_status=0
  stage baseline python3 "$proof_root/research/challenge-8/check-stock-2610.py" \
    --tool-home "$stock_home" --schema "$schema" --compiler-sysroot "$compiler_sysroot" \
    --evidence "$cases" --deadline-epoch "$deadline" || baseline_status=$?
  acceptance_status=0
  stage acceptance python3 "$proof_root/research/challenge-8/cloud-build/proof-audit.py" \
    --lane stock --evidence "$cases" --output "$evidence_root/proof-audit.json" \
    --diagnostic-exit-code "$baseline_status" || acceptance_status=$?
  (( baseline_status == 0 && acceptance_status == 0 )) || exit 1
  exit 0
fi

# Cold, source-built S6+CFG constructor profile, with only the two accepted
# O3 patches; no main20 or other component patch.
candidate="$proof_root/research/challenge-8/overnight-s6/verifast-s6-26.10-candidate.patch"
cfg="$proof_root/research/challenge-8/verifast-manuallydrop-new-cfg-2610.patch"
[[ "$(sha256sum "$candidate" | cut -d' ' -f1)" == 20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c ]] || exit 2
[[ "$(sha256sum "$cfg" | cut -d' ' -f1)" == 593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781 ]] || exit 2
printf 'candidate_patch_sha256=%s\ncfg_patch_sha256=%s\n' \
  "$(sha256sum "$candidate" | cut -d' ' -f1)" "$(sha256sum "$cfg" | cut -d' ' -f1)" >> "$ev/environment.txt"
stage s6-patch-check git -C "$source_home" apply --check "$candidate"
stage s6-patch-apply git -C "$source_home" apply "$candidate"
stage cfg-patch-check git -C "$source_home" apply --check "$cfg"
stage cfg-patch-apply git -C "$source_home" apply "$cfg"
printf '%s\n' bin/rust/std/lib.rsspec \
  src/rust_frontend/vf_mir_translator/vf_mir_translator.ml > "$ev/allowed-files.txt"
git -C "$source_home" diff --name-only > "$ev/modified-files.txt"
cmp "$ev/allowed-files.txt" "$ev/modified-files.txt"
git -C "$source_home" diff > "$ev/applied.patch"
printf 'effective_patch_sha256=%s\n' "$(sha256sum "$ev/applied.patch" | cut -d' ' -f1)" >> "$ev/environment.txt"
python3 - "$stock_home" "$source_home" "$ev" <<'SPECAUDIT'
import hashlib,json,pathlib,sys
stock,source,evidence=map(pathlib.Path,sys.argv[1:])
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a={str(p.relative_to(stock)):p for p in (stock/'bin/rust').rglob('*.rsspec')}
b={str(p.relative_to(source)):p for p in (source/'bin/rust').rglob('*.rsspec')}
if a.keys()!=b.keys(): raise SystemExit('patched specification inventory differs')
changed=[k for k in a if a[k].read_bytes()!=b[k].read_bytes()]
if changed!=['bin/rust/std/lib.rsspec']:
 raise SystemExit(f'unexpected effective specification changes: {changed}')
(evidence/'spec-audit.json').write_text(json.dumps({k:{'stock_sha256':h(a[k]),
 'profile_sha256':h(b[k]),'equal':a[k].read_bytes()==b[k].read_bytes()} for k in a},indent=2)+'\n')
SPECAUDIT

deps_archive="$task_temp/vfdeps-adf88dc-linux.txz"
stage deps-download curl -fL --retry 2 -o "$deps_archive" \
  https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' 8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580 \
  "$deps_archive" | sha256sum -c - > "$ev/deps-sha256.log"
stage deps-extract tar -xjf "$deps_archive" -C "$work_root"
deps_home="$work_root/vfdeps-adf88dc"
[[ -d "$deps_home" ]] || exit 2
if [[ ! -e /tmp/vfdeps-adf88dc ]]; then
  ln -s "$deps_home" /tmp/vfdeps-adf88dc
elif [[ "$(readlink -f /tmp/vfdeps-adf88dc)" != "$deps_home" ]]; then
  exit 2
fi
export PATH="$deps_home/bin:$PATH"
export CAPNP_INC_DIR="$deps_home/include"
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$source_home/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
stage decoder-install cargo install --locked --git \
  https://github.com/btj/capnpc-ocaml-decoder \
  --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2
stage console-build make -C "$source_home/src" ../bin/verifast \
  WITHOUT_LABLGTK=yes VERBOSE=yes
cp -an "$stock_home/bin/." "$source_home/bin/"
if [[ -d "$stock_home/lib" ]]; then
  mkdir -p "$source_home/lib"
  cp -an "$stock_home/lib/." "$source_home/lib/"
fi
for binary in vf-rust-mir-exporter refinement-checker vf-cxx-ast-exporter libz3.so; do
  cmp "$stock_home/bin/$binary" "$source_home/bin/$binary"
done
python3 - "$stock_home" "$source_home" "$ev" <<'BINARYAUDIT'
import hashlib,json,pathlib,sys
stock,profile,evidence=map(pathlib.Path,sys.argv[1:])
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['verifast','vf-rust-mir-exporter','refinement-checker',
       'vf-cxx-ast-exporter','libz3.so','rust/std/lib.rsspec']
data={name:{'stock_sha256':h(stock/'bin'/name),
            'profile_sha256':h(profile/'bin'/name),
            'equal':(stock/'bin'/name).read_bytes()==(profile/'bin'/name).read_bytes()}
       for name in names}
(evidence/'profile-binary-hashes.json').write_text(json.dumps(data,indent=2)+'\n')
(evidence/'profile-hashes.json').write_text(json.dumps({k:h(profile/k) for k in
 ['bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker',
  'bin/rust/std/lib.rsspec','src/rust_frontend/vf_mir/vf_mir.capnp',
  'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml']},indent=2)+'\n')
BINARYAUDIT
ldd "$source_home/bin/verifast" > "$ev/built-console-ldd.txt"
if rg -q 'not found' "$ev/built-console-ldd.txt"; then exit 2; fi

constructor_status=0
stage constructor python3 "$proof_root/research/challenge-8/overnight-s6/check-maybeuninit-new-pointer.py" \
  --stock-home "$stock_home" --tool-home "$source_home" --schema "$schema" \
  --compiler-sysroot "$compiler_sysroot" --evidence "$cases" --components-only || constructor_status=$?
acceptance_status=0
stage acceptance python3 "$proof_root/research/challenge-8/cloud-build/proof-audit.py" \
  --lane constructor --evidence "$cases" --output "$evidence_root/proof-audit.json" \
  --diagnostic-exit-code "$constructor_status" || acceptance_status=$?
(( constructor_status == 0 && acceptance_status == 0 )) || exit 1
