# R12: disable composite upload, gate proof on synthetic publication

T0 2026-10-21T10:53:30Z; main12:53:30Z/absolute13:23:30Z; fresh3600 Cloud seconds.
Owner admin report for484a4382 says packaging succeeded but automatic composite
upload needed forbidden storage.objects.get on temporary component objects.
This new attribution is owner/admin evidence; historical UNKNOWN stays immutable.

The actual generated package-upload shell exports
CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False before all gcloud calls.
SDK image/service account/bucket/precondition flags/failure propagation and final
upload-complete ordering stay fixed. Effective SDK properties enter upload-policy
in the packaged evidence. The final external upload marker also records actual
archive bytes and measured archive upload time/rate; it follows all prerequisites.
These observations describe publication, never verifier acceptance.

Probe in the existing merge lane uses a committed explicit mode card to bypass
all proof preparation/compiler tools. It generates512MiB of random bytes in
Cloud only. Official documentation gives a default150MiB composite threshold:
https://docs.cloud.google.com/storage/docs/parallel-composite-uploads
The pinned SDK's effective threshold is separately recorded; gate requires actual
compressed archive bytes above that threshold. Actual historical archive size is
not available through allowed metadata, so512MiB tests the reported size-trigger
class with >3x default-threshold margin, not an established equal-size reproduction.

Tests execute the actual generated upload shell against isolated fake storage,
using tiny synthetic package inputs only: inherited True is overridden; uploads
retain create-only preconditions and receipt-last ordering; config/first-object/
text-index/final-marker failures propagate and never set upload.ok. No production
archive/log or raw GCS read is involved. A separate Luna HIGH review precedes CI.

A new R12 account gates proof mode on a successful, accounted synthetic Build
with accessible Brief and verified archive/inventory/publication identities.
Normal R11 tool/model/std/spec/invariant/control/matrix bytes are frozen against
source0c1d0d78. Synthetic diagnostic completion explicitly has proof_attempted=false,
verification_accepted=false/credit0. No semantic/profile/tool fix is authorized.
