#!/usr/bin/env bash
set -Eeuo pipefail

die() { printf 'cold-image: %s\n' "$*" >&2; exit 2; }

ROOT=/workspace
PROOF_DIR="$ROOT/proof/research/challenge-8/network/rr/g1/cloud"
EVIDENCE_ROOT=${EVIDENCE_ROOT:-/workspace/evidence}
OUT="$EVIDENCE_ROOT/cold-image"
ALL="$EVIDENCE_ROOT/allprooflogs"
CONTEXT="$ROOT/rr-image-context"
REGISTRY=us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools/refinedrust-g1
BUILD_ID=${CLOUD_BUILD_ID:-unknown}
TAG=${COLD_IMAGE_TAG:-n7-${BUILD_ID}}
IMAGE="$REGISTRY:$TAG"
mkdir -p "$OUT"
mkdir -p "$ALL/cases/cold-image"

status=0
on_exit() {
  status=$?
  python3 - "$OUT/build-status.json.tmp" "$BUILD_ID" "$IMAGE" "$status" <<'STATUS' || true
import json,pathlib,sys
path=pathlib.Path(sys.argv[1]); path.write_text(json.dumps({'schema':'refinedrust-g1-cold-build-status-v1',
    'stage':'cold-image','state':'COMPLETE' if int(sys.argv[4])==0 else 'FAILED',
    'build_id':sys.argv[2],'image':sys.argv[3],'exit_code':int(sys.argv[4])},sort_keys=True)+'\n')
STATUS
  mv "$OUT/build-status.json.tmp" "$OUT/build-status.json" 2>/dev/null || true
  printf '%s\n' "$status" > "$ALL/cold-image-exit-code.txt" || true
  if [[ -f "$OUT/docker-build.log" || -f "$OUT/docker-push.log" ]]; then
    cat "$OUT/docker-build.log" "$OUT/docker-push.log" 2>/dev/null > "$ALL/cold-image.log" || true
  else
    printf 'Cold image stage failed before Docker build; original exit status %s.\n' "$status" > "$ALL/cold-image.log"
  fi
  python3 "$ROOT/infra/research/challenge-8/cloud-build/network-rr/cold-image-audit.py" \
    --status "$OUT/build-status.json" --receipt "$OUT/registry-receipt.json" \
    --build-id "$BUILD_ID" --output "$ALL/proof-audit.json" 2>/dev/null || true
  if [[ -f "$ALL/proof-audit.json" ]]; then
    cp "$ALL/proof-audit.json" "$ALL/cases/cold-image/result.json" 2>/dev/null || true
  fi
  exit "$status"
}
trap on_exit EXIT

[[ "$EVIDENCE_ROOT" == /workspace/* ]] || die 'EVIDENCE_ROOT must remain under /workspace'
[[ "${SMALLSORT_EXECUTION_PROVIDER:-}" == cloud-build ]] || die 'SMALLSORT_EXECUTION_PROVIDER must be cloud-build'
[[ "$BUILD_ID" =~ ^[A-Fa-f0-9-]{16,64}$ ]] || die 'CLOUD_BUILD_ID is missing or malformed'
[[ "$TAG" == "n7-$BUILD_ID" ]] || die 'COLD_IMAGE_TAG must be exactly n7-<CLOUD_BUILD_ID>'
[[ -S /var/run/docker.sock ]] || die 'Docker daemon socket is unavailable'
[[ -f "$PROOF_DIR/Dockerfile.candidate" && -f "$PROOF_DIR/IMAGE-INPUTS.json" && -f "$PROOF_DIR/write-image-receipt.py" ]] || die 'pinned proof package files are missing'
[[ -f "$ROOT/infra/research/challenge-8/cloud-build/network-rr/cold-image-audit.py" ]] || die 'cold image audit helper is missing'

rm -rf "$CONTEXT"
mkdir -p "$CONTEXT"
cp "$PROOF_DIR/Dockerfile.candidate" "$PROOF_DIR/IMAGE-INPUTS.json" "$PROOF_DIR/write-image-receipt.py" "$CONTEXT/"
cp "$PROOF_DIR/IMAGE-INPUTS.json" "$OUT/image-inputs.json"
sha256sum "$PROOF_DIR/Dockerfile.candidate" "$PROOF_DIR/IMAGE-INPUTS.json" "$PROOF_DIR/write-image-receipt.py" > "$OUT/package-files.sha256"

docker build --pull --file "$CONTEXT/Dockerfile.candidate" --tag "$IMAGE" "$CONTEXT" 2>&1 | tee "$OUT/docker-build.log"
container=$(docker create "$IMAGE")
docker cp "$container:/opt/g1-image-receipt.json" "$OUT/image-receipt.json"
docker cp "$container:/opt/refinedrust/rr_frontend/Cargo.lock" "$OUT/Cargo.lock"
docker cp "$container:/opt/g1-executables.sha256" "$OUT/g1-executables.sha256"
docker rm "$container" >/dev/null
sha256sum "$OUT/image-receipt.json" "$OUT/Cargo.lock" "$OUT/g1-executables.sha256" > "$OUT/internal-artifacts.sha256"

docker push "$IMAGE" 2>&1 | tee "$OUT/docker-push.log"
docker inspect --format='{{json .RepoDigests}}' "$IMAGE" > "$OUT/repo-digests.json"
python3 - "$OUT/repo-digests.json" "$REGISTRY" "$BUILD_ID" "$IMAGE" "$OUT/image-receipt.json" "$OUT/Cargo.lock" "$OUT/registry-receipt.json" "$OUT/image-digest.txt" <<'RECEIPT'
import hashlib,json,pathlib,re,sys
source,repository,build_id,tag,internal,lock,out,digest_path=sys.argv[1:]
raw=json.loads(pathlib.Path(source).read_text())
if not isinstance(raw,list) or not all(isinstance(v,str) for v in raw):
    raise SystemExit('RepoDigests has wrong shape')
matches=[v for v in raw if v.startswith(repository+'@sha256:')]
if len(matches)!=1 or not re.fullmatch(re.escape(repository)+r'@sha256:[0-9a-f]{64}',matches[0]):
    raise SystemExit('no unique canonical digest for configured registry repository')
canonical=matches[0]
digest=canonical.rsplit('@',1)[1]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
receipt={'schema':'refinedrust-g1-registry-image-receipt-v1','build_id':build_id,
         'stage':'cold-image','image_tag':tag,'image_digest':canonical,'digest':digest,
         'internal_receipt_sha256':sha(internal),'cargo_lock_sha256':sha(lock)}
pathlib.Path(out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
pathlib.Path(digest_path).write_text(canonical+'\n')
RECEIPT
