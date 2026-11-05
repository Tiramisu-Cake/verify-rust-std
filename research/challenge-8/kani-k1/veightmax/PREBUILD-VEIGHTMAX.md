# VEIGHTMAX — exact pre-build packet

Archived pre-build packet. Coordinator GO was granted on `7df3f7d3d68c458185c2f42f72483c13fbe9c161`;
one build finished. Final outcome: [RESULT-VEIGHTMAX.md](../RESULT-VEIGHTMAX.md).
The review boundary and pre-build expectations below are preserved as packet history.
Updated after coordinator NO-GO on `df65bdf52a5ce90cbd987f8bff5cde01d2d9e0d5`:
neutral diagnostic labels and removal of the constant-false explicit-frame machinery.

Worktree `/root/verify-rust-std-kani-veightmax`, branch
`experiment/kani-k1-veightmax-20261105`; stable owner `k1-merge`, stage `veightmax-g1`.
Task `0eb5f3f10980ddb216feb2eb6f59fa93cc38eff1`; base
`6ef2158d9df1e194bbcd2bf7a46e8feafc3e8cab` (CITRIM final ordinary 226).
Library-only commits `[skip ci]`: initial relocation
`271adbb9be880cd0203e4759e71a590fdfe31cb7`, authorized correction
`d3982a624072437d603f0f96ba974bb00ac5eb5b`.
Research is a separate `[skip ci]` commit. Push without force.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; all lane paths unchanged.
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`, nightly `2026-10-22`.

## Exact relocation

Source revisions: WIDEDOMAINS `30b4a0796a` and TAILDIAG `59ada14d0a` only.
`mapping.json` binds their full SHAs, selected items, successful source commits,
build identities and the seven source-reported bounded rows. The checker binds the
selected baseline roots/helpers to their successful build sources, then compares the
current functions modulo only the explicitly listed authorized edits.

All names below are relative to `verify::`; the expected lists and run request use full names.
The first five roots retain their leaf names; only their module path changes.

| Source → target | Prior seconds | Covers |
| --- | ---: | ---: |
| `widedomains::swap_safety_u8_backing32` → `allocationcontracts::swap_safety_u8_backing32` | 33.71013 | 9/9 |
| `widedomains::swap_safety_u64_backing32` → `allocationcontracts::swap_safety_u64_backing32` | 40.420055 | 9/9 |
| `widedomains::unstable_network_safety_u8_n32_stubbed` → `allocationcontracts::unstable_network_safety_u8_n32_stubbed` | 135.0917 | 5/5 |
| `widedomains::merge_safety_u64_len8_scratch48_src32_dst0` → `allocationcontracts::merge_safety_u64_len8_scratch48_src32_dst0` | 80.85085 | 5/5 |
| `widedomains::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` → `allocationcontracts::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` | 7.120541 | 4/4 |
| `taildiag::u64_backing17_tail1_to7_no_explicit_frame` → `tailcontracts::insert_tail_safety_u64_backing17_tail1_to7` | 31.25227 | 5/5 |
| `taildiag::u64_backing17_tail8_to15_no_explicit_frame` → `tailcontracts::insert_tail_safety_u64_backing17_tail8_to15` | 64.20818 | 5/5 |

`authorized-differences.json` lists every permitted token difference beyond relocation
and the two leaf renames: 27 neutral literal replacements (22 allocation, five tail)
and five frame-only edits in tailcontracts: remove FRAME, its exclusive `before` snapshot,
the unreachable `if FRAME` branch, and the false argument at each of its two call sites.
The deleted branch contained one unreachable assertion; no live assertion or cover is removed.
All live conditions, fixtures, comparator operations and proof attributes remain identical.
The script applies exact per-function replacements with occurrence checks, then compares all
remaining tokens. No wildcard deletion or blanket literal normalization is allowed.
No stage names remain in either new library module, including comments and string literals.
Root documentation states T/F, allocation, start, tail/length and initialization.
Both PFC/consumer pairs move together with their own matching function-item comparator.
Only two declarations are added to existing verify.rs; all other existing library files,
the runtime smallsort.rs, ordinary roots and controls remain unchanged.

## Validation

`python3 -B research/challenge-8/kani-k1/veightmax/check_veightmax.py`: PASS.
It uses the existing source lexer/macro expander, never a compiler or verifier.

- Ordinary expected = exact CITRIM final list of 226 + these seven = **233**.
- Full lists: `ordinary-expected.txt`, `new-ordinary.txt`, `opt-in-expected.txt`,
  `cfg-on-expected.txt`. Cfg-on is 267 = 233 + unchanged 34 opt-in roots.
- Ordinary names SHA256:
  `a73e3c308728c7e7e560665547f79775ddffef2676d4ddee1cecd1b572bdd374`.
- All 226 prior ordinary roots and all 34 opt-in roots retain exact tokens.
- All 17 copied functions (seven roots, ten helpers) match modulo the listed edits;
  all proof attributes remain identical. The report records each applied difference.
- The baseline dependency closures and runtime match their successful source commits.
- rustfmt --check: PASS (edition/style 2024, inherited codefix configuration and wrapper).
- git diff --check: PASS. Existing request validator: seven exact SUCCESS roots accepted.
- Lane/tooling files compare equal to the mandated tooling base.

Static inventory and source-reported results do not establish integrated compilation or proof.
The GCB inventory and seven integrated rows remain pending. No prior CITRIM root is rerun.
Prior new-root time sum **392.653726 s**, covers **42/42**; this excludes setup/compilation.
No universal T/F, sortedness, uninitialized-memory, value-validity, permission or
panic-unwinding theorem is added.

## Run request, controls and budget

`veightmax-g1-20261105-02`; the root and packet copies of RUN-REQUEST.json are identical.
Request SHA256 `5e6e812216996d281d57aa8bb2626c27b32fed1be71329b2c7cc96261e6161fc`.
Diagnostic, controls=false, inventory=true, kani_jobs=1, gcb-e2-standard-4,
4 minutes per root, exactly the seven rows above, each expecting SUCCESS.
Acceptance separately requires exact per-root reachable covers (42/42, zero unreachable),
no failed checks, successful inventory compilation, and exact 233-name equality/hash.
A successful runner gate alone is insufficient.

One primary build, zero retries; at most one compile-error repair only if own spent plus
new reserve stays <= $2.00. Main window 180 minutes plus closeout 30 minutes.
Maximum reservation: (7 × 4 + 30) × $0.0135 = **$0.7830**, timeout 58 minutes.
Own spent/reserved before dispatch: $0/$0. Project cap **$118.96**.
Bounded budget snapshot (2026-11-05 UTC): 244 builds, used $105.2430, reserved $0;
with this maximum reservation $106.0260. Recheck immediately before authorized dispatch.
GO and available owner slot remain necessary; package preparation is not dispatch authority.

## After exact-packet GO

1. Confirm local/origin SHA equals the reviewed SHA; recheck owner slot and project/own budget.
   Dispatch once with `research/challenge-8/kani-k1/tools/k1g.sh dispatch experiment/kani-k1-veightmax-20261105`.
2. Record build/source/request/stage identities and deadlines in RUN-LEDGER.json.
   Invoke `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`, then end the turn.
   Do not poll status in a loop or use local cargo/rustc/Kani/CBMC.
3. On the queued completion message, use bounded helper `status`, `summary`, `summary BUILD 0 7`,
   `check-tooling BUILD 59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, and `budget BUILD`.
   Save their bounded outputs under `veightmax/evidence/`; never read raw logs or cache files.
4. Fetch `inventory BUILD 0 80`, then each reported next_offset until done (233 names).
   Bind every page to the exact build/source/request/Kani identities; require consistent
   inventory/names hashes, complete nonoverlapping coverage, no duplicates and sorted
   names exactly equal to `ordinary-expected.txt`. Recompute the canonical names hash.
5. Verify all seven exact requested rows, SUCCESS, zero failed checks and expected covers;
   record actual times and their sum. Preserve errors/discrepancies explicitly. Bounded
   log-grep may clarify compilation or warning failures; no raw evidence or credentials.
6. Write RESULT-VEIGHTMAX.md <=30 lines with identities, mapping, seven-row results,
   inventory count/equality/hash, ordinary 233, time sum and any failures. Update ledger.
   Commit/push research `[skip ci]`, no force, end with REVIEW REQUEST <sha> /
   VEIGHTMAX ЗАВЕРШЁН. Stop after this one stage.
