# G1 candidate implementation

**Cloud execution NOT AUTHORIZED; frontend/injector/image NOT_RUN.** These files
are review candidates, not a registered lane. Source c7ca8c467aecf10a4b53039372ee97714f854ee3,
RR 332d945fafa14bf55c0c8390cb35ec4b0c012cff, compiler
e457a7b0d326d67b4322ef0d11bd715cfaeda48f; full blob/tree/byte receipts in inputs.json.

Phase 1 remediation is documented in
[G1-REVIEW-REMEDIATION](../G1-REVIEW-REMEDIATION.md). The independent review
found that the original callee/unwind gates could report false observations.
Events and inventory now share a comment-aware, balanced-term CallS scanner;
the synthetic fixture contains six calls and four distinct location bindings.
Definition existence never resolves a callee binding. The exact pinned Radium
writer could not be retrieved for independent inspection, so its continuation,
linking, annotation and configuration contracts remain **UNKNOWN**. The auditor
has an unconditional UNKNOWN output-contract gate: even a reviewed map cannot
grant real-output admission PASS in this revision. No continuation roles are
inferred from the synthetic fixture or arbitrary Goto occurrences. Completing
R2 requires inspected pinned writer bytes before implementing positive Radium
normal/unwind path acceptance; this package does not claim that work is complete.

`run.py` is the Cloud-only entrypoint driver. It requires a fresh disposable
source checkout, clean pinned RR image checkout, fresh /workspace evidence,
BUILD_ID, SMALLSORT_EXECUTION_PROVIDER=cloud-build, the reviewed dispatcher's
SMALLSORT_DEADLINE_EPOCH and a separately issued authorization receipt.
`authorization.template.json` is non-authorizing: false and null are deliberate.
Its identities must be matched against the independently verified submitted
Cloud config/API by the dispatcher. BUILD_ID/environment and local receipt hashes
alone do not authenticate execution or grant permission.

Future reviewed Cloud command shape (do not run on VPS, including --help):

```text
python3 g1/run.py --repo /workspace/g1-source --rr /opt/refinedrust \
  --out /workspace/g1-evidence --authorization /workspace/authorization.json
```

The runner verifies inputs/image/compiler; runs P0, N1 and saved-certificate N2;
checks native exact core before any annotations; inserts ghost-only attributes;
then invokes stock RR generation. No stdlib summaries are imported into actual
core (`lib_load_paths=[]`): unregistered ordinary callees remain a diagnostic
binding gap. This strict candidate does not promise the available annotations
close every pointer/trait/intrinsic binding. The real generic signatures and
runtime bodies remain intact. The diagnostic may_unwind_if(True) does not assert
CURRENT recovery or replace the final resource contract. No proof is checked.

The wrapper deadline covers source fetch/restore too. The runner subtracts 90 s
for classifier/inventory before the existing outer packaging reserve of 70 s;
process timeouts shorten to remaining allowance, not an independent 1200 s clock.
P0/N1 share 90 s, native check 240 s, RR P1 540 s. Logs, command exit/timing and
cumulative child peak RSS are recorded. Signals/timeouts/setup failures do not
count as intended negatives. Raw selected-callee failure attribution still
requires review when RR diagnostics omit caller/source span.

Evidence root includes identity.json, inputs.json, image-receipt.json,
cargo-config.toml, execution.json, source-receipt.json, original/annotated/stripped
source archives, all command logs/config/environment, stock MIR/NLL/Radium
outputs, summary.json and evidence-manifest.json. Compiler caches are excluded;
MIR and Radium remain outside them. The per-file inventory detects corruption,
missing files, extra files and symlinks. The existing outer packager/upload must
still bind archive/config/source certificate and upload receipt independently.

`evidence.py` reads saved artifacts only. On the first automatic collection,
without an independently reviewed source/MIR/Radium mapping, a successful P1 is
**INCONCLUSIVE**. Stock RR has no machine-readable complete map. A reviewer can
later create `g1-reviewed-correspondence-v1` JSON with `correspondence`, `body_map`,
`locals`, `callee_inventory`, `resource_inventory`; exact schema is in
correspondence.py. Do not guess a map in advance or patch the frontend to emit one.
The collector checks the externally reviewed SHA256 and selected artifact
hashes/body/block occurrences. Edge roles and actual callee linkage remain
UNKNOWN; a map or name occurrence cannot close those gates.

Saved-data collector command shape (service-only, no compiler):

```text
python3 g1/evidence.py --evidence SAVED_DIRECTORY \
  --expected-identities EXTERNALLY_VERIFIED_IDENTITIES.json \
  --reviewed-map INDEPENDENT_REVIEW_MAP.json --reviewed-map-sha256 REVIEWED_SHA256
```

Expected identities must come from dispatcher/submitted config/API, not the
archive's own identity.json. Run the collector from its published reviewed proof
commit; its inputs.json must byte-match the archived pins. Mapping files are
separate replay inputs, never a mutation of original logs/evidence. PASS here is
admission only; verification_accepted=false and proof_status=NOT_RUN always.
Resource inventories identify generated spec definitions; their interpretation,
FnMut current resources, scalar/array conversion, transitive assumptions and
shim applicability require separate review/proof. No arbitrary resolution label
is a theorem or permission to replace ordinary source with a shim.

Permitted VPS checks: AST/JSON parsing, bash -n, Git/hash checks and the synthetic
`test_service.py`/`test_correspondence.py`/`test_evidence.py` suites after inspecting imports. They
import no driver/injector/toolchain/Cloud modules. Do not invoke run.py,
annotate.py, Dockerfile or write-image-receipt.py locally. Neither fixture Rust
code nor actual annotated core was compiled or generated on VPS.

The collector verifies required receipts and artifacts for attempted stages,
command/log/environment/config consistency, and the archived reviewed N2 bytes.
Timeouts/signals never earn P0/N1/native/P1 credit. `local_inventory_valid` is
distinct from `diagnostic_complete`; `evidence_complete` stays false until the
external package/upload protocol is integrated and independently verified.
Per-file hashes and internally consistent records alone do not authenticate
execution. The process-group timeout fix is statically reviewed only; a real
process-tree test is reserved for a separately authorized Cloud session.

[Cloud candidates](cloud/REVIEW.md) document remaining provider/transport/
registration/evidence-packaging gaps. Production scripts and coordinator are
unchanged; max two slots and one per owner/ledger remain mandatory.
