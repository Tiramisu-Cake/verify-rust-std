# Overnight actual-helper candidates

Current resumed checkpoint O22: exact generic `checked_forget_owned` is an
[accepted local component](../overnight-forget-own/RESULT-O22.md), returning
the SAME T.own+thread under falseunwind. The complete actual-owner admission
gate passes, then nested ghost metadata lookup fails before actualproof;
[causal repair](ACTUAL-NESTED-GHOST-SCOPE-BEFORE.md) is separately reviewed.
SAFEforget, actualnestedDrop and outerassume_init/helper remain unproved.
The dated O7 account below is historical evidence.

Historical status O7 proves the pointer-specialized local `transmute_neo` body and
G1 direct framed-body fixtures under their recorded profile. The actual
`assume_init` call linkage and actual helper remain **unproved**.
O4 run 37702049156 and O5 run 37702922138 show the two G1 framed-call
positives reach return/leak checks but fail mandatory dead-code at the
synthetic callee-unwind successor. The next G1 positives place the exact
generic forget body directly inside the framed probe; any verified result
will establish the framed body property, not the separate call linkage.
The G1 precondition does not contain `<T>.own`; a positive is **value/frame
evidence only**, not a SAFE generic-forget ownership contract or a nominal
DropOnPanic forget summary.
This directory is an independent component. `BEFORE.md` records the
obligation, trust boundary and controls;
`../OVERNIGHT-GUARD-DESIGN.md` explains the resource protocol.

Run only in the pinned GitHub-hosted checkout with the same configured
VeriFast source/profile as the surrounding overnight workflow:

```sh
python3 research/challenge-8/overnight-helper/check-helper.py \
  --tool-home "$tool_home" \
  --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" \
  --evidence "$ev/helper" \
  --deadline-epoch "$deadline" \
  --a1-primitive-matrix \
  --a1-linkage-capture \
  --a1-linkage-proof
```

`--s6-specs` supplies the exact ordered timed preamble names, comma separated;
the default is the historical six-function S6 list. It is an exact identity
gate, never a prefix count inferred from a live log. `--g1-variants` selects
a comma-separated subset for a bounded diagnostic. A subset cannot make the
full matrix flags true. `--actual-capture` adds unchanged actual
`select_unpredictable<*const Element>` source and complete typed MIR capture.

The driver captures A1 method and separate local `transmute_neo` first, then
optionally checks the direct-body primitive matrix and G1 variants. The
`--a1-linkage-capture` option adds a two-body diagnostic unit: the exact
source-specialized local callee precedes the exact method adapter, whose
Rust call still resolves to `std::mem::transmute_neo`. It records complete
typed MIR for both and never redirects the call or marks the method proved.
`--a1-linkage-proof` exercises the separately patched opt-in redirect on the
O9-reviewed two-body graph, source/admission mutations and the method's
positive and negative contracts. Its first hosted run remains experimental
until the exact failure locations and full return/leak/dead-code traces are
reviewed.
The primitive matrix includes exact admission and type controls; its O7
evidence is specific to the pointer domain and cannot mark actual call
linkage accepted. Every
case records original/verified sources, source pins,
NORMAL/readonly exported binaries and decoded MIR, full verifier log and
refinement log when export succeeds. It stops stage execution near the passed
deadline and keeps partial results `INCONCLUSIVE`. `summary.json` never marks
either component accepted. G1 positive evidence is labeled
`EXPERIMENTAL_POSITIVE`; intended negatives require exact timed headers and
specified proof/leak/dead-code obligation. Location/message mappings are
deliberately strict and may need correction from first hosted evidence.

A1 O4 captures have independently reviewed **prepatch** full-record manifests
for both local bodies. The `prepare-assume-init-2610.py check` command
requires a separately reviewed
manifest that pins the entire decoded method record hash and source. This
source/MIR admission check does not implement compiler `transmute_unchecked`, assert that
an uninitialized wrapper contains a pointer, or prove the actual helper.
`test-helper-certificates.py` provides hosted tamper controls for source pairs,
separate annotation clauses and full-MIR manifest rejection. It is independent
of the proof matrix and should run on GitHub-hosted Actions only.

The present actual-helper capture has no guard destructor reachability proof.
The next implementation decision requires reviewing the complete new MIR,
checking exact guard nominal type and drop flags, then proving the source-linked
forget frame protocol and pointer-only extraction. A positive auxiliary
generic-forget fixture cannot be used as an actual SAFE forget summary by
itself. No arbitrary `DropOnPanic.own=true` or `Element` memory right is used.
