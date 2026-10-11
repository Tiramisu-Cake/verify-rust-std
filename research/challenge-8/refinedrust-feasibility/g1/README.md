# G1 candidate implementation

**Cloud execution NOT AUTHORIZED; frontend/injector/image NOT_RUN.** These files
are review candidates, not a registered lane. Source c7ca8c467aecf10a4b53039372ee97714f854ee3,
RR 332d945fafa14bf55c0c8390cb35ec4b0c012cff, compiler
e457a7b0d326d67b4322ef0d11bd715cfaeda48f; full blob/tree/byte receipts in inputs.json.

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
The collector verifies its externally reviewed SHA256 and every selected artifact
hash/body/block/edge; missing fields cannot grant PASS.

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
`test_service.py`/`test_correspondence.py` suites after inspecting imports. They
import no driver/injector/toolchain/Cloud modules. Do not invoke run.py,
annotate.py, Dockerfile or write-image-receipt.py locally. Neither fixture Rust
code nor actual annotated core was compiled or generated on VPS.

[Cloud candidates](cloud/REVIEW.md) document remaining provider/transport/
registration/evidence-packaging gaps. Production scripts and coordinator are
unchanged; max two slots and one per owner/ledger remain mandatory.
