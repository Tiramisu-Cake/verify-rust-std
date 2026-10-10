# C3 pre-capture exact-delta review

**Verdict: conditional GO for the source/MIR/pre-AST capture only.** This is
not a C3 proof, helper proof, pointer-provenance result, accepted profile, or
permission to admit a bounded C3 projection. Review was read-only; no tests,
compiler, exporter, verifier, or proof were run here.

The incremental patch is pinned to C2 translator
`daf29b03fbb7aa10e6f580c70780a9fdc5a2eb6d3f4470e1c38673212ca3d9a3`, patch
SHA-256 `392042884052677d325d881c74d49b724649f21242f3d773906b3445a97104d0`,
and expected patched translator
`c7692ab6f4f70ad12a0f3bea886834bd072667ed4dc5ba6a314607f5b8b38a76`. The
patch changes only `vf_mir_translator.ml`. Its C3 opt-in defaults off, rejects
mixed C1/C2/C3 modes, requires the isolated strict-cut environment and exact
verified-source hash, requires exactly one `cmp2` and one `cmp3` parsed
declaration, and checks ordered cuts `cmp`, `cmp2`, `cmp3`. On capture it
serializes the target's pre-transform AST and then deliberately refuses with
`FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF`.

`prepare` starts from the pinned C2 annotated source SHA-256
`ecd83f8c0840a07f138bc8afa2a36c661f296d748693afa2a0a61667cb3372e4`, inserts
the ghost-only helper source, inserts `selected_four_limits` immediately
before the original `let a = v_base.add(c1 as usize);`, and replaces exactly
the original C3 call line with the candidate annotation. It checks helper
ghost stripping, exact anchor counts, and byte-identical ghost-stripped
runtime against `original/lib.rs`. The certificate and result explicitly set
`profile_accepted=false`, `proof_credit=false`,
`actual_sort4_callable_summary=false`, and `target_proof=NOT_RUN`.

The driver now checks the fresh C2 result (`positive_ok` and zero exit), the
C2 translator/patch identities, and a before/after tool snapshot. The latter
requires unchanged tool HEAD, all non-translator critical files, all binaries
except the intentionally rebuilt `bin/verifast`, effective RSSpec files, and
proof std inputs. It also gates on Cloud provider and the assigned lane. The
outer C1 runner separately rejects GitHub Actions before invoking this driver.
The default-off C2 positive regression and mandatory unbound-C2 refusal run
before capture; these preserve gates and do not count as C3 proof.

The snapshot check is intra-invocation (before versus after the C3 patch/build),
not a comparison against the saved `c2-bound-tool-snapshot.json`. The same
in-process lane passes the fresh C2 result and C2 translator hash, and then
replays the default-off C2 positive. Preserve both snapshots for later review;
the fresh correspondence audit should compare their frozen fields before any
bound C3 admission.

The exported normal/readonly MIR is only a generic full-record inventory:
callback count, block/local counts, and unwind lines. It is explicitly marked
`UNREVIEWED_COMPLETE_GRAPH_CAPTURE`; it does not certify C3's `(c,a)` operands,
direct `Continue` edge, declaration liveness, or pointer provenance. The
captured pre-AST likewise records the original full AST, before any bounded
projection. Do not use this result to enable C3 transformation.

Before any later bound-profile admission, independently audit and pin the
fresh source certificate, full normal and readonly MIR, and pre-AST. Confirm
the exact C3 call operands and direct-unwind edge, all four source-derived
bool-offset cases and provenance, the C3 temporaries' storage/init/address/free
effects, and the ordered named declarations/cuts. Inspect the raw capture
refusal and verify the result has `target_proof=NOT_RUN`. Separately prove the
selected split/inverse join helpers at this source version; this capture does
not validate their syntax or VCs. Preserve C1/C2 defaults and refusal controls
and the complete original posts, return, leak, and dead-code gates in the
subsequent proof phase.
