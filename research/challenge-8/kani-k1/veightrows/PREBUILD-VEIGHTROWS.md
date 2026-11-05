# VEIGHTROWS — exact pre-build packet

Archived pre-build packet: coordinator GO on `01caba2d4d7386759de16ee395518aa866cafbb4`;
the single authorized build completed. Final outcome: [RESULT-VEIGHTROWS.md](../RESULT-VEIGHTROWS.md).
The pre-build expectations and review boundary below are preserved as history.

Task `ec0ed3b1e0127592d2690a461671849df974c9c9`; base
`ab99e39380a7fe2415d77f3082012510f4a60627`.
Worktree `/root/verify-rust-std-kani-veightrows`, branch
`experiment/kani-k1-veightrows-20261105`, owner `k1-merge`, stage `veightrows-g1`.
Preparation only: **no dispatch before exact-packet coordinator GO**.

## Source and exact request

No library commit or code change. The candidate's entire `library` Git tree equals
`d3982a624072437d603f0f96ba974bb00ac5eb5b:library`:
`51aa04b15525498e8aec5ab23c15ca9b08bb5b46`.
The tracked working library has no difference from that reference and no untracked files.
All lane paths equal tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`;
tooling, scripts, workflows and runtime remain unchanged.
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`.

Root and packet `RUN-REQUEST.json` copies are byte-identical:
`veightrows-g1-20261105-01`, SHA256
`e80d8942192e78db648f9e9c8c9471d84783ac6c8891f6be17d8bb40615e62db`.
Diagnostic, controls=false, **inventory=false**, jobs=1, gcb-e2-standard-4,
4 minutes per root; exactly five entries, each expecting SUCCESS.
Existing `kani_k1.py validate` accepts the request; generated arguments and runner
are retained beside this packet. No local compiler or verifier was invoked.

Names below are relative to `slice::sort::shared::smallsort::verify::`.
The full names and covers are in `expected-covers.json`, selected without changes
from `veightmax/expected-covers.json` (source hash bound in `check-report.json`).

| Root | Required reachable covers |
| --- | ---: |
| `allocationcontracts::swap_safety_u8_backing32` | 9 |
| `allocationcontracts::swap_safety_u64_backing32` | 9 |
| `allocationcontracts::unstable_network_safety_u8_n32_stubbed` | 5 |
| `tailcontracts::insert_tail_safety_u64_backing17_tail1_to7` | 5 |
| `tailcontracts::insert_tail_safety_u64_backing17_tail8_to15` | 5 |

Acceptance requires five SUCCESS rows, zero failed checks, **33/33 reachable covers**,
zero unreachable covers, consistent build/source/request/Kani identities and COMPLETE
verification. Ordinary inventory is not requested or rerun.
VEIGHTMAX build `daf1045c-5454-4662-93a7-df16cfd23e00`, source
`7df3f7d3d68c458185c2f42f72483c13fbe9c161`, already established merge8 and sort8
SUCCESS on this same library: 86.45552 s + 8.113433 s = **94.568953 s**, covers 5/5 + 4/4.
Only these two rows carry into the final seven-root sum; VEIGHTMAX's overall acceptance
was FAIL and the other five rows receive no proof/time credit before this build finishes.
The previous 233-name inventory remains historical evidence on the identical library.

## Timing and budget feasibility

The unchanged dispatcher sets Cloud timeout `(5 × 4 + 30)` = **50 minutes**.
The runner cuts verification at `(5 × 4 + 24)` = **44 minutes after validate**;
setup, Kani build, compilation and instrumentation consume that same bound.
The six minutes between runner cutoff and Cloud timeout are not counted as verify time.

Two prior own diagnostic requests explicitly used inventory=false, controls=false,
jobs=1 and standard4. Their bounded peaks outputs are saved in `prebuild-evidence/`;
build/source/request identities and references to tracked summaries/statuses are in
`check-report.json`. Both runs ended Cloud FAILURE due to harness expectations;
their preparation timings remain useful observations, not successful proof claims.

| Prior build | Validate → verify start | First sampled CBMC after verify start | Combined |
| --- | ---: | ---: | ---: |
| CITRIM G1 `76b1664d-a0bf-4268-92fc-3b69220d556f` | 348 s | 76 s | 424 s |
| CITRIM G2 `bd623a0c-935a-4bcd-a5c1-5d6f148c6bec` | 354 s | 74 s | 428 s |

First sampled CBMC is a process-sampling observation, not an exact compiler timer.
Use a conservative **720 s (12 min)** planning allowance for setup, compilation and
instrumentation, above both observations. Estimated remaining verify time is
2640 − 720 = **1920 s (32 min)**, exceeding the required 5 × 240 = **1200 s (20 min)**
by 720 s. This meets the task's pre-build feasibility condition; it is not a guarantee
of future setup duration or root success. If dispatch conditions change materially,
stop for the coordinator; do not change tooling or timeout parameters.

One build only, no retries, no repair. Own cap **$1.00**, project cap **$118.96**;
maximum reservation 50 × $0.0135 = **$0.6750**. Own spent/reserved $0/$0.
Bounded project snapshot at packet preparation: 245 builds, used **$105.9720**,
reserved **$0.0000**; with this maximum reservation **$106.6470**.
Recheck immediately before authorized dispatch. Main window 120 min + closeout 20 min;
record its start/deadlines with the coordinator GO, without extending any supplied T0.

## After exact-packet GO

1. Confirm local/origin source equals the exact reviewed SHA, unchanged library tree,
   lane equality, owner slot and budget. Record approved SHA and window/deadlines in
   `RUN-LEDGER.json`; avoid a new source commit before dispatch unless re-reviewed.
2. Dispatch exactly once via
   `research/challenge-8/kani-k1/tools/k1g.sh dispatch experiment/kani-k1-veightrows-20261105`.
   Record build/source/request identities and reservation in the ledger.
3. Invoke `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`, then end the turn.
   No status polling loop. No local cargo/rustc/Kani/CBMC or credential reads.
4. On completion use bounded helper status, summary, `summary BUILD 0 5`, peaks,
   `check-tooling BUILD 59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, budget BUILD,
   and targeted log-grep only where needed to establish covers/warnings or clarify errors.
   Save bounded outputs; do not read raw logs, archives or cache files. Do not request inventory.
5. Bind Cloud source to the reviewed commit and its library tree to the reference.
   Reconcile five exact rows, failed checks, times, covers and completion/exit/gate.
   Keep incomplete or failed outcomes explicit, with no retries or repairs.
6. Write `RESULT-VEIGHTROWS.md` in at most 20 lines: identities; table of five statuses,
   times and covers; seven-root sum with carried merge8/sort8, covers out of 42.
   If any times/results are missing, do not claim a complete seven-root sum or credit.
   Update ledger, research commit `[skip ci]`, push without force; finish with
   `REVIEW REQUEST <sha>` / `VEIGHTROWS ЗАВЕРШЁН`, then stop.

All new files in this packet are research records. No new proof or compiler-inventory
claim is made by the pre-build checks.
