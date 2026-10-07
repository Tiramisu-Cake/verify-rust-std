# Overnight actual-helper candidates

Status: source fixtures and a hosted driver are prepared, **no VF26.10 proof
run has been attributed to these files**. This directory is an independent
component. `BEFORE.md` records the obligation, trust boundary and controls;
`../OVERNIGHT-GUARD-DESIGN.md` explains the resource protocol.

Run only in the pinned GitHub-hosted checkout with the same configured
VeriFast source/profile as the surrounding overnight workflow:

```sh
python3 research/challenge-8/overnight-helper/check-helper.py \
  --tool-home "$tool_home" \
  --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" \
  --evidence "$ev/helper" \
  --deadline-epoch "$deadline"
```

`--s6-specs` supplies the exact ordered timed preamble names, comma separated;
the default is the historical six-function S6 list. It is an exact identity
gate, never a prefix count inferred from a live log. `--g1-variants` selects
a comma-separated subset for a bounded diagnostic. A subset cannot make the
full matrix flags true. `--actual-capture` adds unchanged actual
`select_unpredictable<*const Element>` source and complete typed MIR capture.

The driver captures A1 method and separate local `transmute_neo` first, then
checks G1 variants. Every case records original/verified sources, source pins,
NORMAL/readonly exported binaries and decoded MIR, full verifier log and
refinement log when export succeeds. It stops stage execution near the passed
deadline and keeps partial results `INCONCLUSIVE`. `summary.json` never marks
either component accepted. G1 positive evidence is labeled
`EXPERIMENTAL_POSITIVE`; intended negatives require exact timed headers and
specified proof/leak/dead-code obligation. Location/message mappings are
deliberately strict and may need correction from first hosted evidence.

A1 `capture.json` and `adapter-full-mir.txt` are **unreviewed**. The
`prepare-assume-init-2610.py check` command requires a separately reviewed
manifest that pins the entire decoded method record hash and source. This
capture/check does not implement compiler `transmute_unchecked`, assert that
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
