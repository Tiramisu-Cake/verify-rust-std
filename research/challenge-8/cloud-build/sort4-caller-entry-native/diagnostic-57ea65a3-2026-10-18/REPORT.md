# Updated Brief diagnosis — 2026-10-18

Build `57ea65a3-475e-4370-810c-19ad36803174`; immutable proof/infra
`9678ddf631902765d7013f5ed1b9fd05159463a6`. This supplements the earlier
`08887c25` diagnosis; historical reports, verdicts, pins and ledger stay unchanged.

## Newly available evidence

The ordinary Evidence Brief now uses processor0.4.0 / derived/v2. Its failure
section is CORROBORATED / CORROBORATED_SOURCE_REPORT, with verified archived
member references. The archive is unchanged:
`02901f734338f175e9969c47fe59c35d369e75e2150308b06495ba6acc2e6c0f`.
[Brief](brief.md) and [index](evidence-index.json) were fetched via the existing
reader only and their exact SHA256 matched [processing receipt](processing-receipt.json):

- Brief SHA256 `d5769542be569ef13b380e0c707b3adb1f59bf5bf61bf75315c3792d6688501f`.
- Index SHA256 `7c59a7fb1079e16363243b26a9aca88c4c99222d093cbac1e16e1eff52596d81`.

The first corroborated blocker is **tool-reconstruction → R-only native-reference
build**. Runner records `RuntimeError: A1-TOOL: R-only native reference build`.
Stage `a1-R-only-native-reference-build` is TERMINAL, exit2, timeout budget541s.
The exporter compile failed with two `unused_mut` diagnostics:

| Diagnostic location | Brief log line | Exact R-source binding |
| --- | --- | --- |
| src/lib.rs:843:17 | 68 | `let mut kind = out.init_kind();` in encode_required_gen_arg |
| src/lib.rs:906:60 | 83 | `mut out: clause_cpn::Builder<'_>` in encode_required_clause |

Brief log line91 reports `could not compile vf_mir_exporter (lib) due to 2 previous
errors`. This is not the merge provider-pin defect. The stage failed with a
compiler diagnostic, not a reported timeout.

Provenance supplied by the reader:

- `proof-audit.json`: SHA256
  `88a0e0838b3eb6172156be9d9ab8057e90ec3b99ea85b55b8573d1dc2c56d068`.
- `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build-stage.json`:
  SHA256 `ddc330bc8f67e0aa0a068ced23a8a8d2e3e201df9293a100b9858712dc80d563`.
- The corresponding `.log`: SHA256
  `fce1d5e4658d815703b38bb15a7517818224d25ce3515480b9c4f138bdcef4ee`.

The pinned command at a1-tool.py:226 is:

```text
make -C <isolated-A1-tool>/src build-vf-rust-mir-exporter ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
```

This argv is reconstructed from pinned source; the reader exposes stage name,
exit and diagnostic references, not a raw argv field or cargo's individual exit
status. No raw log/receipt member was downloaded or read by this agent.

## Source correspondence and minimum fix

The exact exporter was reconstructed without compilation: `git show` the tool
base `f76012fb518703b1d98e243ac4f487f16877cfcb`, then apply only the exporter hunks
of the published R patch in a temporary source directory. Both hashes matched
published profile values:

- R-before exporter `11f1e10bb8e52a4950611f874b1123c11e2c87cbb1378c3f5060992f74425f00`.
- R-after exporter `469c377dfb9e3a249abd0fd4205a54ee1d41b091da41aca0f8fe07959e48e6bf`.

The diagnostic line numbers and bindings match exactly. Line6 contains
`#![deny(warnings)]`, so unused_mut is fatal. No warning policy change is needed.

[PROPOSED-unused-mut-fix.patch](PROPOSED-unused-mut-fix.patch) removes **only** the
unused mut modifier from those two bindings. It is a separate reviewable proposal
against the R-after source, not an applied change to the active R patch/profile.
Other mut bindings remain, including the separate encode_required_ty builder.
Function argument types, serialization, region handling, clauses, kernel,
model/prelude/refinement and checks are unchanged by the proposed token edits.

Source-only apply check, exact two-line delta and hashes pass:
[checks](source-check.json). Proposed exporter SHA256:
`c29d0d4692eab84257fe61036d6e41dbc11ee3ad999005df4ffb157bb8b463ad`.
Proposal patch SHA256:
`0918c514472e1702650306b3dcdf554d13bf29f66581107bc4cc26b807aff296`.
No compiler or verifier was invoked locally; successful compilation after this
change is not yet established.

## P1,26 rows and false31

The new report explicitly gives **26 source-reported rows, NOT_RUN=26** with
proof-audit SHA256 provenance. The earlier UNKNOWN result reflected the older
Brief's reporting gap; that historical report is retained. For this supplemental
assessment, the same pinned26-row inventory is reconciled in [diagnostic.json](diagnostic.json):

```text
OFF P0a P0b P0c P-dispatch P1
N-binder-collapse N-alpha-valid N-free-region N-region-swap N-no-F N-clauses
N-default-contract N-freeze-contract N-false31 N-source N-binding
N-clause-redirect N-duplicate R1 R2 R3 R4 R5 R6 R7
```

P1 is NOT_RUN, and there is no native reference comparison or small_sort proof
credit. N-false31 is NOT_RUN. Its own two body/conformance proofs, own receipt,
caller and threshold32/len32 observation are downstream of the failed tool build
and were not reached according to pinned flow. Individual false31 substage
receipts are not independently exposed by this report. No unrelated positive
receipt, intended-negative credit or formal verification result is substituted.

The corroborated chain is exporter compile errors → R-only make exit2 → caught
reconstruction error → mandatory matrix NOT_RUN → diagnostic_complete=false →
final verdict exit1. It explains why the execute wrapper could still return0.
The last directly reported attempted stage is the failed R-only build; successful
R-only console construction and later C/P1/proof stages are not established.

## Validation plan for a future separately authorized Build

1. Review the two token removals, fold them into a **new candidate** R patch, and
   publish a new immutable candidate profile/release binding. Preserve old files
   and historical pins. Compute the new R-patch SHA from its actual bytes; the
   overlay proposal SHA above is not the R-patch SHA.
2. In the new candidate's maps, preserve r_before; set exporter in r_after,
   c_before and c_after to the proposed source hash after exact reconstruction.
   Refresh the new profile byte pin/proof/infra binding. Keep all other compiler,
   schema/translator/kernel/tool pins and mandatory26 routes unchanged unless
   another separately justified change is reviewed.
3. Repeat source-only patch/closure/hash/config preflight and addressed independent
   review. Do not use allow(unused_mut), disable deny(warnings), bypass the R-only
   build gate, or mint its receipt before build success.
4. Under a new explicit Cloud account/window/Build authorization, run the existing
   mandatory matrix: first require R-only exporter+console build exit0, retain
   its independent reference receipt, then final C tool and each required target.
   Verify P1 full native interface, all26 classifications and false31's own
   body→receipt→caller lifecycle. No mandatory row is omitted for budget.
5. Read only updated Evidence Brief/index/receipt afterwards. A build that passes
   these two diagnostics can still reveal a later blocker; this proposal does
   not predict matrix acceptance or full A1/A2 proof.

No new Build was submitted. Existing closed account, spent330s/retired630s,
all historical verdicts/pins/ledger and proof credit are unchanged. The old
administrative request is retained as history; raw audit is not needed to select
this minimum fix from the newly available ordinary report. Active source pins
were intentionally not edited under the current diagnostic-only instructions.
