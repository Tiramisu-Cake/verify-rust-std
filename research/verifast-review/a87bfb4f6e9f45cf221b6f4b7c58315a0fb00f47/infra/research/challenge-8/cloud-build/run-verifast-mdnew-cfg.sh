#!/usr/bin/env bash
# Bounded Cloud-only source-built baseline/candidate gate for MDnew CFG.
set -euo pipefail

lane=${1:?usage: run-verifast-mdnew-cfg.sh verifast-mdnew-cfg}
[[ "$lane" == verifast-mdnew-cfg ]] || { echo 'unexpected lane' >&2; exit 2; }
infra_root=${INFRA_ROOT:-/workspace/infra}
proof_root=${PROOF_ROOT:-/workspace/proof}
evidence_root=${EVIDENCE_ROOT:-/workspace/evidence}
cloud_dir="$infra_root/research/challenge-8/cloud-build"
all="$evidence_root/allprooflogs"
cases="$all/cases"
deadline=${SMALLSORT_DEADLINE_EPOCH:?SMALLSORT_DEADLINE_EPOCH is required}
base_sha=f76012fb518703b1d98e243ac4f487f16877cfcb
candidate_sha=1435539475fdaa7810bc2bc780fba0514f765f48
candidate_tree=be55d8d934fb10617309a289e0d546ca1aed6ea0
rustc_commit=f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f
archive_sha=5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd
deps_sha=8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580
rustup_sha=20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c
schema_sha=f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469
input_rel="research/challenge-8/verifast-input/$candidate_sha"
work=/workspace/verifast-mdnew-cfg
source_repo="$work/source"
baseline_tool="$source_repo"
candidate_tool="$work/candidate"
stock_archive="$work/verifast-26.10-linux.tar.gz"
stock_home="$work/verifast-26.10"
deps_archive="$work/vfdeps-adf88dc-linux.txz"
deps_home="$work/vfdeps-adf88dc"
verifast_input="$proof_root/$input_rel"
source_certificate="$evidence_root/source-input-certificate.json"
proof_audit="$evidence_root/proof-audit.json"
auditor="$cloud_dir/mdnew-audit.py"
restore="$cloud_dir/restore-verifast-input.py"
audited=0
status=0

mkdir -p "$all" "$work"
[[ -d "$cloud_dir" && -d "$proof_root" && -d "$evidence_root" ]] || exit 2
if [[ -n "$(find "$all" -mindepth 1 -print -quit)" ]]; then
  echo "evidence lane already contains files: $all" >&2; exit 2
fi
mkdir -p "$cases"

write_incomplete_audit() {
  local code=$?
  trap - EXIT
  if (( audited == 0 )); then
    python3 "$auditor" "$cases" --output "$proof_audit" > "$all/audit-failure.log" 2>&1 || true
    audited=1
  fi
  if (( code != 0 )) && [[ -f "$proof_audit" ]]; then
    python3 - "$proof_audit" "$code" <<'FAILCLOSED'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1])
try: d=json.loads(p.read_text())
except Exception: d={}
d.update({'accepted':False,'classification':'INCONCLUSIVE','runner_exit_status':int(sys.argv[2])})
d.setdefault('reason','runner failed before successful completion')
p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
FAILCLOSED
  fi
  if (( code == 0 )); then
    python3 - "$proof_audit" <<'CHECK'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1])
try: d=json.loads(p.read_text())
except Exception: raise SystemExit(2)
raise SystemExit(0 if d.get('accepted') is True else 2)
CHECK
    code=$?
  fi
  exit "$code"
}
trap write_incomplete_audit EXIT

remaining() {
  local seconds=$((deadline - $(date +%s)))
  (( seconds > 0 )) || { echo 'Cloud deadline elapsed' >&2; return 124; }
  echo "$seconds"
}
run_stage() {
  local name=$1 limit=$2 cwd=$3 output=$4 mode=$5; shift 5
  local budget rc=0
  budget=$(remaining)
  (( budget > limit )) && budget=$limit
  mkdir -p "$(dirname "$output")"
  if [[ "$mode" == combined ]]; then
    /usr/bin/time -v -o "$all/$name-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${budget}s" \
      bash -c 'cd "$1"; shift; exec "$@"' bash "$cwd" "$@" \
      > "$output" 2>&1 || rc=$?
    printf 'stderr merged into %s\n' "$output" > "$all/$name-stderr.log"
  else
    /usr/bin/time -v -o "$all/$name-resources.txt" \
      timeout --signal=TERM --kill-after=10s "${budget}s" \
      bash -c 'cd "$1"; shift; exec "$@"' bash "$cwd" "$@" \
      > "$output" 2> "$all/$name-stderr.log" || rc=$?
  fi
  printf '%s\n' "$rc" > "$all/$name-exit-code.txt"
  return "$rc"
}

# Only an identified Cloud Build on the pinned lane may proceed.
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build && -z "${GITHUB_ACTIONS:-}" ]] || {
  echo 'explicit Cloud Build provider required' >&2; exit 2;
}
provider_json=$(CLOUD_BUILD_ID=${CLOUD_BUILD_ID:-} \
  CLOUD_BUILD_PROJECT_ID=${CLOUD_BUILD_PROJECT_ID:-} \
  CLOUD_BUILD_REGION=${CLOUD_BUILD_REGION:-} \
  python3 "$cloud_dir/provider.py")
printf '%s\n' "$provider_json" > "$all/provider.json"

python3 - "$source_certificate" "$proof_root" "$infra_root" "$all/identities.json" <<'IDENTITIES'
import json,pathlib,subprocess,sys
certificate,proof,infra,out=map(pathlib.Path,sys.argv[1:])
c=json.loads(certificate.read_text())
if c.get('lane')!='verifast-mdnew-cfg': raise SystemExit('source-input lane mismatch')
for key,root in (('proof',proof),('infra',infra)):
 rec=c.get(key,{})
 if not rec.get('commit') or not rec.get('head'): raise SystemExit(f'{key} source identity absent')
 if rec.get('commit') != rec.get('head'): raise SystemExit(f'{key} source-input commit/head mismatch')
actual_proof=subprocess.check_output(['git','-C',str(proof),'rev-parse','HEAD'],text=True).strip()
actual_infra=subprocess.check_output(['git','-C',str(infra),'rev-parse','HEAD'],text=True).strip()
if actual_proof != c['proof']['head'] or actual_infra != c['infra']['head']:
 raise SystemExit('restored Git heads differ from source-input certificate')
if c['proof']['head'] != c['infra']['head']:
 raise SystemExit('proof and infrastructure must be the same frozen delivery commit')
for envkey,key in (('PROOF_SHA','proof'),('INFRA_SHA','infra')):
 expected=__import__('os').environ.get(envkey)
 if expected and expected != c[key]['commit']: raise SystemExit(f'{envkey} differs from source-input certificate')
out.write_text(json.dumps({'infra_sha':c['infra']['commit'],'proof_sha':c['proof']['commit'],
 'infra_tree':c['infra']['root_tree'],'proof_tree':c['proof']['root_tree'],
 'source_input_archive_sha256':c['archive_sha256']},indent=2,sort_keys=True)+'\n')
IDENTITIES
infra_sha=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["infra_sha"])' "$all/identities.json")
proof_sha=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["proof_sha"])' "$all/identities.json")
[[ -f "$verifast_input/bundle" && -f "$verifast_input/manifest" ]] || {
  echo 'committed VeriFast delivery bundle/manifest absent from proof input' >&2; exit 2;
}
mkdir -p "$all/tool-input"
cp "$verifast_input/bundle" "$all/tool-input/bundle"
cp "$verifast_input/manifest" "$all/tool-input/manifest"

export RUSTUP_HOME="$work/rustup" CARGO_HOME="$work/cargo"
export RUSTUP_TOOLCHAIN=nightly-2026-09-25
export PATH="$CARGO_HOME/bin:$PATH"
export TMPDIR="$work/tmp"
mkdir -p "$RUSTUP_HOME" "$CARGO_HOME" "$TMPDIR"
export LANG=C.UTF-8 LC_ALL=C.UTF-8
printf 'lane=%s\ninfra_sha=%s\nproof_sha=%s\nbase_sha=%s\ncandidate_sha=%s\nprovider=%s\ndeadline=%s\n' \
  "$lane" "$infra_sha" "$proof_sha" "$base_sha" "$candidate_sha" \
  "$provider_json" "$deadline" > "$all/environment.txt"

run_stage package-index 300 /workspace "$all/package-index.log" split apt-get update
run_stage packages-install 300 /workspace "$all/packages-install.log" split \
  apt-get install --yes --no-install-recommends build-essential m4 patch unzip \
  capnproto ripgrep time libgmp10 libmpfr6 libgomp1 libffi8 libncurses6 \
  libtinfo6 zlib1g libz3-4 libgtk-3-0 libgtksourceview-4-0
run_stage vfdeps-download 180 /workspace "$all/vfdeps-download.log" split curl -fL --retry 2 -o "$deps_archive" \
  https://github.com/verifast/vfdeps/releases/download/25.01/vfdeps-adf88dc-linux.txz
printf '%s  %s\n' "$deps_sha" "$deps_archive" | sha256sum -c - > "$all/vfdeps-sha256.log"
run_stage vfdeps-extract 120 /workspace "$all/vfdeps-extract.log" split tar -xjf "$deps_archive" -C "$work"
[[ -d "$deps_home" ]] || { echo 'pinned vfdeps directory absent' >&2; exit 2; }
for prefix in /vfdeps-adf88dc /tmp/vfdeps-adf88dc; do
  if [[ ! -e "$prefix" ]]; then ln -s "$deps_home" "$prefix"
  elif [[ "$(readlink -f "$prefix")" != "$deps_home" ]]; then echo "conflicting dependency prefix $prefix" >&2; exit 2
  fi
done
export PATH="$deps_home/bin:$PATH" CAPNP_INC_DIR="$deps_home/include"

run_stage stock-download 180 /workspace "$all/stock-download.log" split curl -fL --retry 2 -o "$stock_archive" \
  https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz
printf '%s  %s\n' "$archive_sha" "$stock_archive" | sha256sum -c - > "$all/stock-archive-sha256.log"
mkdir -p "$stock_home"
run_stage stock-extract 120 /workspace "$all/stock-extract.log" split tar -xzf "$stock_archive" -C "$work"

run_stage tool-checkout 240 /workspace "$all/tool-checkout.log" split \
  git clone --no-checkout https://github.com/verifast/verifast.git "$source_repo"
run_stage tool-base-checkout 120 /workspace "$all/tool-base-checkout.log" split \
  git -C "$source_repo" checkout --detach "$base_sha"
[[ "$(git -C "$source_repo" rev-parse HEAD)" == "$base_sha" ]] || { echo 'upstream base checkout mismatch' >&2; exit 2; }
python3 "$restore" --repository "$source_repo" --bundle "$verifast_input/bundle" \
  --manifest "$verifast_input/manifest" --destination "$candidate_tool" \
  --receipt "$all/restore-receipt.json" --infra-sha "$infra_sha" --proof-sha "$proof_sha" \
  > "$all/restore.log" 2>&1 || { cat "$all/restore.log"; exit 2; }
[[ "$(git -C "$candidate_tool" rev-parse HEAD^{tree})" == "$candidate_tree" ]] || exit 2
schema="$baseline_tool/src/rust_frontend/vf_mir/vf_mir.capnp"
candidate_schema="$candidate_tool/src/rust_frontend/vf_mir/vf_mir.capnp"
[[ "$(sha256sum "$schema" | cut -d' ' -f1)" == "$schema_sha" ]] || { echo 'pinned MIR schema mismatch' >&2; exit 2; }
cmp "$schema" "$candidate_schema"

rustup_init="$work/rustup-init-1.28.2"
run_stage rustup-init-download 180 /workspace "$all/rustup-init-download.log" split \
  curl -fL --retry 2 -o "$rustup_init" \
  https://static.rust-lang.org/rustup/archive/1.28.2/x86_64-unknown-linux-gnu/rustup-init
printf '%s  %s\n' "$rustup_sha" "$rustup_init" | sha256sum -c - > "$all/rustup-init-sha256.log"
chmod +x "$rustup_init"
run_stage rustup-init 120 /workspace "$all/rustup-init.log" split "$rustup_init" -y --no-modify-path --default-toolchain none --profile minimal
run_stage compiler-install 300 /workspace "$all/compiler-install.log" split rustup toolchain install "$RUSTUP_TOOLCHAIN" --profile minimal \
  --component rustc-dev --component llvm-tools-preview --component rust-src
compiler_sysroot=$(rustc --print sysroot)
rustc --version --verbose > "$all/compiler-version.txt"
python3 - "$all/compiler-version.txt" "$rustc_commit" <<'RUSTPIN'
import pathlib,sys
rows=dict(line.split(': ',1) for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if ': ' in line)
if rows.get('commit-hash')!=sys.argv[2] or rows.get('host')!='x86_64-unknown-linux-gnu': raise SystemExit('rustc pin mismatch')
RUSTPIN
export LD_LIBRARY_PATH="$compiler_sysroot/lib:$stock_home/bin:$deps_home/lib:${LD_LIBRARY_PATH:-}"
run_stage decoder-install 300 /workspace "$all/decoder-install.log" split cargo install --locked --git \
  https://github.com/btj/capnpc-ocaml-decoder --rev 2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2

for tree in "$baseline_tool" "$candidate_tool"; do
  name=baseline
  [[ "$tree" == "$candidate_tool" ]] && name=candidate
  target="$tree/bin"
  mkdir -p "$target"
  cp -an "$stock_home/bin/." "$target/"
  rm -f "$target/verifast"
  if [[ -d "$stock_home/lib" ]]; then mkdir -p "$tree/lib"; cp -an "$stock_home/lib/." "$tree/lib/"; fi
  [[ "$(sha256sum "$tree/bin/rust/std/lib.rsspec" | cut -d' ' -f1)" == "$(sha256sum "$stock_home/bin/rust/std/lib.rsspec" | cut -d' ' -f1)" ]] || exit 2
done
for pair in 'baseline_tool baseline' 'candidate_tool candidate'; do
  read -r var profile <<< "$pair"
  tree=${!var}
  run_stage "$profile-console-build" 720 "$tree" "$all/$profile-console-build.log" split \
    make -C "$tree/src" ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
  ldd "$tree/bin/verifast" > "$all/$profile-console-ldd.txt"
  if rg -q 'not found' "$all/$profile-console-ldd.txt"; then echo "$profile console has missing shared libraries" >&2; exit 2; fi
done

python3 - "$stock_home" "$baseline_tool" "$candidate_tool" "$all/runtime-components.json" "$compiler_sysroot" "$verifast_input/manifest" <<'COMPONENTS'
import hashlib,json,pathlib,subprocess,sys
stock,base,candidate,out,sysroot,manifest_path=map(pathlib.Path,sys.argv[1:])
BASE="f76012fb518703b1d98e243ac4f487f16877cfcb"
manifest=json.loads(manifest_path.read_text())
candidate_sha=manifest["candidate_commit"]
changed=subprocess.check_output(["git","-C",str(candidate),"diff","--name-only",BASE,candidate_sha],text=True).splitlines()
if sorted(changed)!=sorted(manifest["selected_files"]): raise SystemExit("candidate changed-path set differs from committed input manifest")
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=['src/rust_frontend/vf_mir_exporter','src/rust_frontend/vf_mir_decoder','src/refinement_checker']
components={}
def committed_files(repo,prefix):
 import os
 rows={}
 raw=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','-z','HEAD','--',prefix])
 for item in raw.split(b'\0'):
  if not item: continue
  meta,path=item.split(b'\t',1); mode,kind,oid=meta.decode().split(' '); rel=path.decode(); checkout=repo/rel
  if kind!='blob' or mode not in ('100644','100755','120000'): raise SystemExit(f'unsupported component Git entry: {rel}')
  committed=subprocess.check_output(['git','-C',str(repo),'show','HEAD:'+rel])
  if mode=='120000':
   if not checkout.is_symlink() or os.readlink(checkout).encode()!=committed: raise SystemExit(f'component symlink differs from committed blob: {rel}')
  elif checkout.is_symlink() or not checkout.is_file() or checkout.read_bytes()!=committed:
   raise SystemExit(f'component checkout differs from committed blob: {rel}')
  rows[rel[len(prefix)+1:]]={'mode':mode,'git_blob':oid,'sha256':hashlib.sha256(committed).hexdigest()}
 return rows
for prefix in paths:
 fa=committed_files(base,prefix); fb=committed_files(candidate,prefix)
 if fa!=fb: raise SystemExit(f'baseline/candidate component source differs: {prefix}')
 components[prefix]={'source_file_count':len(fa),'source_files_sha256':hashlib.sha256(json.dumps(fa,sort_keys=True).encode()).hexdigest()}
specs={}
for tree_name,tree in (('baseline',base),('candidate',candidate)):
 rows={str(p.relative_to(tree/'bin/rust')):h(p) for p in sorted((tree/'bin/rust').rglob('*.rsspec')) if p.is_file()}
 specs[tree_name]=rows
stock_specs={str(p.relative_to(stock/'bin/rust')):h(p) for p in sorted((stock/'bin/rust').rglob('*.rsspec')) if p.is_file()}
if not stock_specs or specs['baseline']!=specs['candidate'] or specs['baseline']!=stock_specs: raise SystemExit('effective stock/baseline/candidate specification inventory mismatch')
binaries={}
for name in ('vf-rust-mir-exporter','refinement-checker','vf-cxx-ast-exporter','libz3.so','rust/std/lib.rsspec'):
 a=stock/'bin'/name; b=base/'bin'/name; c=candidate/'bin'/name
 if not a.is_file() or not b.is_file() or not c.is_file() or b.read_bytes()!=c.read_bytes() or a.read_bytes()!=b.read_bytes(): raise SystemExit(f'unchanged pinned component mismatch: {name}')
 binaries[name]={'sha256':h(a),'baseline_equal':True,'candidate_equal':True}
version=subprocess.check_output(['rustc','--version','--verbose'],text=True)
path={'baseline_source_sha':subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],text=True).strip(),
      'candidate_source_sha':subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD'],text=True).strip(),
      'candidate_tree':subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD^{tree}'],text=True).strip(),
      'changed_paths':changed,
      'stock_distribution_sha256':h(pathlib.Path('/workspace/verifast-mdnew-cfg/verifast-26.10-linux.tar.gz')),
      'distribution_provenance':{'release':'26.10','tag_commit':BASE,'github_release_asset_id':611766606,'asset_bytes':97804993,'asset_url':'https://github.com/verifast/verifast/releases/download/26.10/verifast-26.10-linux.tar.gz'},
      'vfdeps_archive_sha256':h(pathlib.Path('/workspace/verifast-mdnew-cfg/vfdeps-adf88dc-linux.txz')),
      'compiler_sysroot':str(sysroot),'rustc_verbose':version,
      'components':components,'pinned_stock_binaries':binaries,'specification_inventory':specs,'stock_specification_inventory':stock_specs,
      'console_binary_sha256':{'baseline':h(base/'bin/verifast'),'candidate':h(candidate/'bin/verifast')},
      'console_profile':'two source-built verifast consoles at pinned base and candidate; stock-26.10 exporter/refiner/specs reused identically after source-component audit'}
pathlib.Path(out).write_text(json.dumps(path,indent=2,sort_keys=True)+'\n')
COMPONENTS

# Assert all fixtures are the exact candidate Git blobs before either console sees them.
python3 - "$candidate_tool" "$baseline_tool" "$candidate_sha" "$cases" <<'FIXTURES'
import hashlib,pathlib,shutil,subprocess,sys
candidate,baseline,cases=map(pathlib.Path,(sys.argv[1],sys.argv[2],sys.argv[4]))
sha=sys.argv[3]
for name in ('forget','shared_cleanup','false_normal_post','shared_false_unwind','dead_code_pre'):
 rel=pathlib.Path('tests/rust/purely_unsafe/manuallydrop_new_cfg')/(name+'.rs')
 src=candidate/rel; data=src.read_bytes()
 recorded=subprocess.check_output(['git','-C',str(candidate),'show',sha+':'+rel.as_posix()])
 if data!=recorded: raise SystemExit(f'candidate fixture differs: {name}')
 digest=hashlib.sha256(data).hexdigest()
 for side,tree in (('baseline',baseline),('candidate',candidate)):
  out=cases/side/name
  out.mkdir(parents=True)
  (out/'source.rs').write_bytes(data)
  if hashlib.sha256((out/'source.rs').read_bytes()).hexdigest()!=digest: raise SystemExit(f'{side} fixture copy changed: {name}')
  run=out/'run'; run.mkdir()
  (run/(name+'.rs')).write_bytes(data)
  original=run/'original'; verified=run/'verified'; original.mkdir(); verified.mkdir()
  import re
  original_bytes=re.sub(rb"(?m)^[ \t]*//@[^\n]*(?:\n|$)",lambda m: b"\n" if m.group().endswith(b"\n") else b"",data)
  (original/'lib.rs').write_bytes(original_bytes); (verified/'lib.rs').write_bytes(data)
  (out/'fixture.json').write_text(__import__('json').dumps({'source_sha256':digest,'source_bytes':len(data),'original_sha256':hashlib.sha256(original_bytes).hexdigest(),'verified_sha256':digest,'ghost_strip_exact':True,'candidate_commit':str(sha),'git_blob':subprocess.check_output(['git','-C',str(candidate),'rev-parse',str(sha)+':'+rel.as_posix()],text=True).strip()},indent=2,sort_keys=True)+'\n')
FIXTURES

run_verifast() {
  local side=$1 case=$2 mode=$3; shift 3
  local tree binary out_dir log name rc=0
  if [[ "$side" == baseline ]]; then tree=$baseline_tool; else tree=$candidate_tool; fi
  binary="$tree/bin/verifast"
  out_dir="$cases/$side/$case/run"
  case "$mode" in
    diagnostic) log="$cases/$side/$case/full-verification.log"; name="$side-$case-diagnostic" ;;
    allow) log="$cases/$side/$case/allow-full-verification.log"; name="$side-$case-allow" ;;
  esac
  local args=("$binary" -rustc_args '--edition 2021' -verbose 1 -dump_ast_with_locs "$out_dir/verified-ast.txt")
  if [[ "$mode" == allow ]]; then args+=( -allow_should_fail ); fi
  args+=("$case.rs")
  if [[ "$mode" == diagnostic && ( "$case" == false_normal_post || "$case" == shared_false_unwind ) ]]; then
    python3 - "$out_dir/$case.rs" "$cases/$side/$case/source.rs" "$cases/$side/$case" <<'DIAGCOPY'
import hashlib,json,pathlib,sys
work,source,out=map(pathlib.Path,sys.argv[1:]); raw=source.read_bytes(); marker=b" //~should_fail"
if raw.count(marker)!=1: raise SystemExit("expected one should_fail marker")
derived=raw.replace(marker,b"",1); work.write_bytes(derived)
(out/"diagnostic-source.rs").write_bytes(derived)
(out/"diagnostic-source-sha256.txt").write_text(hashlib.sha256(derived).hexdigest()+"\n")
fixture=json.loads((out/"fixture.json").read_text()); fixture.update({"diagnostic_source_sha256":hashlib.sha256(derived).hexdigest(),"diagnostic_source_path":"diagnostic-source.rs","diagnostic_line_count_preserved":len(raw.splitlines())==len(derived.splitlines()),"should_fail_marker_count_removed":1}); (out/"fixture.json").write_text(json.dumps(fixture,indent=2,sort_keys=True)+"\n")
(out/"diagnostic-source.json").write_text(json.dumps({"original_sha256":hashlib.sha256(raw).hexdigest(),"diagnostic_sha256":hashlib.sha256(derived).hexdigest(),"marker_count_removed":1,"line_count_preserved":len(raw.splitlines())==len(derived.splitlines())},indent=2,sort_keys=True)+"\n")
DIAGCOPY
  fi
  run_stage "$name" 180 "$out_dir" "$log" combined "${args[@]}" || rc=$?
  if [[ "$mode" == diagnostic ]]; then printf '%s\n' "$rc" > "$cases/$side/$case/exit-status.txt"
  else printf '%s\n' "$rc" > "$cases/$side/$case/allow-exit-status.txt"; fi
  # The root stage receipt always mirrors the verifier log for complete packaging.
  cp "$log" "$all/$name.log"
  cp "$all/$name-stderr.log" "$cases/$side/$case/$name-stderr.log"
  if [[ "$mode" == diagnostic && ( "$case" == false_normal_post || "$case" == shared_false_unwind ) ]]; then cp "$cases/$side/$case/source.rs" "$out_dir/$case.rs"; fi
  cp "$all/$name-resources.txt" "$cases/$side/$case/$name-resources.txt"
  cp "$all/$name-exit-code.txt" "$cases/$side/$case/$name-exit-code.txt"
  return 0
}

# Captures use each source tree's own schema and unchanged pinned exporter/refiner.
capture_case() {
  local side=$1 case=$2 tree exporter refiner schema workdir outdir source_hash mode name rc
  if [[ "$side" == baseline ]]; then tree=$baseline_tool; else tree=$candidate_tool; fi
  exporter="$tree/bin/vf-rust-mir-exporter"; refiner="$tree/bin/refinement-checker"
  schema="$tree/src/rust_frontend/vf_mir/vf_mir.capnp"
  workdir="$cases/$side/$case/run"; outdir="$cases/captures/$case"
  mkdir -p "$outdir"
  source_hash=$(sha256sum "$cases/$side/$case/source.rs" | cut -d' ' -f1)
  declare -A stages=()
  for mode in normal readonly; do
    local suffix=(); [[ "$mode" == readonly ]] && suffix+=(--vf-rust-mir-exporter:preprocess-readonly)
    name="$side-$case-$mode-export"; rc=0
    run_stage "$name" 180 "$workdir" "$workdir/$mode-mir.bin" split \
       "$exporter" "$case.rs" "--sysroot=$compiler_sysroot" --edition 2021 --crate-type lib "${suffix[@]}" || rc=$?
    stages["$mode-export"]=$rc
    cp "$all/$name-stderr.log" "$outdir/$side-$mode-export.log"
    if (( rc == 0 )); then
      name="$side-$case-$mode-decode"; rc=0
      run_stage "$name" 120 "$workdir" "$workdir/$mode-mir.txt" split capnp decode "$schema" VfMir < "$workdir/$mode-mir.bin" || rc=$?
      stages["$mode-decode"]=$rc
      cp "$all/$name-stderr.log" "$outdir/$side-$mode-decode.log"
      cp "$workdir/$mode-mir.txt" "$outdir/$side-$mode-mir.txt"
    else stages["$mode-decode"]=-1; fi
  done
  name="$side-$case-refinement"; rc=0
  run_stage "$name" 180 "$workdir" "$workdir/refinement.log" split \
    "$refiner" --rustc-args '--edition 2021' original/lib.rs verified/lib.rs || rc=$?
  stages[refinement]=$rc
  cp "$all/$name-stderr.log" "$outdir/$side-refinement.log"
  if [[ "$side" == candidate ]]; then
    cp "$workdir/normal-mir.bin" "$outdir/normal-mir.bin"
    cp "$workdir/readonly-mir.bin" "$outdir/readonly-mir.bin"
    cp "$workdir/refinement.log" "$outdir/refinement.log"
    cp "$workdir/normal-mir.txt" "$outdir/normal-mir.txt"
    cp "$workdir/readonly-mir.txt" "$outdir/readonly-mir.txt"
    cp "$workdir/verified-ast.txt" "$outdir/verified-ast.txt"
  fi
  if [[ "$side" == baseline ]]; then
    cp "$workdir/normal-mir.bin" "$outdir/baseline-normal-mir.bin"
    cp "$workdir/readonly-mir.bin" "$outdir/baseline-readonly-mir.bin"
    cp "$workdir/refinement.log" "$outdir/baseline-refinement.log"
    cp "$workdir/normal-mir.txt" "$outdir/baseline-normal-mir.txt"
    cp "$workdir/readonly-mir.txt" "$outdir/baseline-readonly-mir.txt"
    cp "$workdir/verified-ast.txt" "$outdir/baseline-verified-ast.txt"
  fi
  local status_file="$outdir/baseline-capture-status.json"
  [[ "$side" == candidate ]] && status_file="$outdir/capture-status.json"
  python3 - "$status_file" "$case" "$side" "$source_hash" \
    "$infra_sha" "$proof_sha" "$([[ "$side" == baseline ]] && echo "$base_sha" || echo "$candidate_sha")" "${stages[normal-export]}" "${stages[normal-decode]}" \
    "${stages[readonly-export]}" "${stages[readonly-decode]}" "${stages[refinement]}" \
    "$workdir/normal-mir.bin" "$workdir/normal-mir.txt" \
    "$workdir/readonly-mir.bin" "$workdir/readonly-mir.txt" \
    "$workdir/refinement.log" "$workdir/verified-ast.txt" <<'CAPTURE'
import hashlib,json,pathlib,sys
out,case,side,src,infra,proof,tool,*rest=sys.argv[1:]
exits=list(map(int,rest[:5])); files=list(map(pathlib.Path,rest[5:]))
names=('normal-export','normal-decode','readonly-export','readonly-decode','refinement')
stages={}
for name,code,path in zip(names,exits,files): stages[name]={'exit_status':code,'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None}
record={'schema':'verifast-mdnew-capture-v1','case':case,'side':side,'source_sha256':src,'tool_source_sha':tool,'infra_sha':infra,'proof_sha':proof,'stages':stages,'verified_ast_sha256':hashlib.sha256(files[5].read_bytes()).hexdigest() if files[5].is_file() else None}
pathlib.Path(out).write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
CAPTURE
}

# Run the same five source bytes through each exact source-built console.
for side in baseline candidate; do
  for case in forget shared_cleanup false_normal_post shared_false_unwind dead_code_pre; do
    case "$case" in
      false_normal_post) run_verifast "$side" "$case" diagnostic; if [[ "$side" == candidate ]]; then run_verifast "$side" "$case" allow; fi ;;
      shared_false_unwind) run_verifast "$side" "$case" diagnostic; run_verifast "$side" "$case" allow ;;
      *) run_verifast "$side" "$case" diagnostic ;;
    esac
  done
done
for side in baseline candidate; do
  for case in forget shared_cleanup false_normal_post shared_false_unwind dead_code_pre; do
    capture_case "$side" "$case"
  done
done

python3 "$auditor" "$cases" --output "$proof_audit" > "$all/mdnew-audit.log" 2>&1 || status=$?
audited=1
if (( status != 0 )); then cat "$all/mdnew-audit.log"; exit "$status"; fi
python3 - "$proof_audit" "$all/runtime-components.json" "$all/restore-receipt.json" <<'FINALIZE'
import json,pathlib,sys
proof=pathlib.Path(sys.argv[1]); result=json.loads(proof.read_text())
if result.get('accepted') is not True: raise SystemExit('focused audit did not accept evidence')
for p in map(pathlib.Path,sys.argv[2:]):
 if not p.is_file(): raise SystemExit(f'missing runtime provenance: {p}')
json.loads(pathlib.Path(sys.argv[2]).read_text()); json.loads(pathlib.Path(sys.argv[3]).read_text())
FINALIZE
exit 0
