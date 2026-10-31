# PRE-BUILD REVIEW — TYPED

Coordinator: Claude Code. State: published package prepared; explicit GO required, no dispatch.
Source commit: `241d94a41182ed6850244e0b51ddc8031daf7435`.
Base: `e0ff82577dc58950621dadc9c141d88a5821987f` (INTEG2 candidate, not green full CI).
Existing cap commit: `6b12002d79b6ccb4ded6c4790b1c592c65d6c591`, CAP_USD=88.96.
Base library tree: `c522edd42ae67c385e1ee42a1c4d1bffb611c90b`.
Frozen pilot library tree: `702a552ae226f885fe03ef5e8af0a386848587ac` for both G1/G2.

Source commits are separate from research/request. Source diff adds the cfg-controls declaration
in merge.rs and the new 190-line typed_oracle.rs only; no old source/contract/helper changes.
Research diff: RUN-REQUEST.json becomes G1; new typed-oracle package and RESULT-TYPED.md only.
`manifest.json` binds every full harness name, fixture, expected property/control and metric fields.
`SEMANTIC-AUDIT.md` gives theorem mapping, exact control sites, bridge/surjectivity argument and limits.
`source-audit.json` + `static-audit.py` record unchanged ordinary projection/lane and hashes.
`A-U8-CONSUMERS.md` is a separate <=50-line source-only consumer audit, without proof credit.

Both requests passed the existing Python validator; prescribed rustfmt passed both changed .rs.
No compiler, cargo, Kani, CBMC, inventory, CI or proof run. Every proof/measurement remains NOT_RUN.
Kani pin `9461e07af7ec929f050aa4192f29363c9be07779`, toolchain `nightly-2026-10-12`;
existing unstable flags, --no-assert-contracts, --object-bits 12 preserved; uninit checks OFF.

## Exact dispatch contract

Both requests: measurement, gcb-e2-standard-4/k1-standard4, controls=true, jobs1, timeout10m per entry.
All names below have prefix `slice::sort::shared::smallsort::verify::`.
New names are under `merge::typed_oracle::`; baseline names remain under `merge::`.

| G1 entry | Expected |
| --- | --- |
| merge::general_direct_u64_n8 | SUCCESS |
| merge::typed_oracle::general_u64_n8_projected_generic | SUCCESS |
| merge::typed_oracle::general_u64_n8_native | SUCCESS |
| merge::stable_direct_u64_n8 | SUCCESS |
| merge::typed_oracle::stable_u64_n8_native | SUCCESS |
| merge::merge_contract_u64_n13 | SUCCESS |
| merge::typed_oracle::merge_u64_n13_projected_actual_pfc | SUCCESS |
| merge::typed_oracle::probe_bridge_u64_u8 | SUCCESS |
| merge::typed_oracle::value_corruption_control_u64_n2 | FAILED, typed full-value count only |

G2 conditional entries: merge::general_direct_u8_n9 (SUCCESS),
merge::typed_oracle::general_u8_n9_native (SUCCESS),
merge::typed_oracle::value_corruption_control_u8_n2 (FAILED, typed full-value count only).
Controls use source-message expect_check; actual file:line/class must be confirmed from bounded logs.
Placeholder/matcher mismatch keeps aggregate gate=false; no automatic reinterpretation or retry.

## Metrics and decisions fixed before dispatch

For every entry record actual status; failed/total/unreachable assertion counts; satisfied/total
covers and reached cover identities; verification seconds; harness wall seconds; CBMC and driver
RSS separately by PID with attribution/source/request/build binding. Missing values stay UNKNOWN.
Report setup separately, and TIMEOUT/OOM/missing separately from unsuccessful assertions.
Pair old/new G8 projection, G8 native, S8 native, A13 projection independently. Also compare
G8 projected-generic/native to separate final-count cost from projection where both are accepted.
Only accepted SUCCESS pairs yield old/new time and RSS ratios; TIMEOUT is censored, no speedup.
Bridge/control/additional safety clauses are separate overhead; no aggregate speedup hides them.
S8 old/native changes both initializer and final count; no S8 projection-only measurement is claimed.
If positive/bridge/control unaccepted: PARTIAL/FAIL. Accepted without effect: COMPLETE pilot, STOP.
Even an effect is a single-run preliminary signal; no migration/X6 approval or B2 proof credit.
Unmeasured G2 stays NOT_RUN and is never described as measured u8 savings.

## Window, money and continuation

Conservative T0 2026-10-31 12:46:00 UTC; first clock 12:46:33; deadline17:46, closing17:16 UTC.
Own ledger: spent0, reserved0, builds0/2, no UUIDs. Own cap USD2 incl failures/cancels/retries.
G1 envelope9x10+30=120min/USD1.620; latest dispatch15:16 UTC incl closing reserve.
G2 envelope3x10+30=60min/USD0.810; latest dispatch16:16 UTC incl closing reserve.
Full reserves total2.430>2; G2 only if actual own spent+reserved+0.810<=2 and full time remains.
Global budget read for preparation: builds127, used65.5395, reserved1.2150, cap88.96;
this is a snapshot, never a substitute for fresh k1g.sh budget immediately before dispatch.
Every dispatch needs explicit GO, current global budget, own UUID/request ledger, full envelope
and unused slot. Each build gets its own request SHA/UUID, with identical library tree.
A retry consumes the second slot instead of G2 and requires delta-review/GO.
Semantic fixes require published delta-review and new GO; never rerun automatically.
After dispatch: k1g.sh watch UUID and END TURN. After terminal: bounded summary/peaks/status,
check-tooling against full cap SHA, selected-UUID budget, targeted log-grep/log-lines only.
Use no Evidence Brief/Select/Merge phases for K-1; no full/raw evidence or credential reads.
