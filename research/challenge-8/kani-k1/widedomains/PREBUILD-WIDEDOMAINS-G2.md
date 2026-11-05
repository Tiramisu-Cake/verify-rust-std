# WIDEDOMAINS G2 — exact packet after G1

G2_PRE_BUILD_REVIEW_PENDING. G1 GO is exhausted; G2 requires a new exact-packet coordinator GO.
Worktree `/root/verify-rust-std-kani-widedomains`, branch `experiment/kani-k1-widedomains-20261105`.
Task base `34f69f034b`, library base `4fa6151b6a`; stable owner `k1-merge`, stage `widedomains-g2`.
G1 library `35667f4a956e8f24919275b745455a751df57edc`, reviewed source `90fadd7ccf8b5bb32d04401d274a6f492b612897`.
G2 library commit `ca934b30c79c2bad5fcd81dc306d6cf3d926cc8c` (only the opt-in module).
All G1 function bodies/attributes remain token-identical. G1 proof results are not overwritten.
Tooling must remain equal to `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, nightly `2026-10-22`.

## G1 evidence and reason for the new domains

Build `f303fd59-fa90-4c25-a50d-8c7ab7146fea` completed with Cloud FAILURE, Kani exit 1, gate=false.
Both swap backing32 PFCs passed (33.71013/40.420055 s), and real u8 network N32 passed (135.0917 s).
All 23 covers on these three successful roots were reached. Seven broad tail PFCs timed out at 180 s;
their checks, cover totals and verification times are absent, not inferred. No compile error or OOM
is reported. Bounded targeted diagnostics show exactly seven timeout messages and no error/unused/
widedomains-source match. The broad start + per-element initialization-mask fixtures remain opt-in.
They give no tail proof credit. The fixture complexity is a hypothesis for cost, not a proven cause.
G1 tooling, source/request identities, pool and cost were checked from bounded k1g outputs.
Cost $0.4860; no repair/retry; three <=200-second ordinary candidates total 209.221885 s.

G2 restricts tail PFCs to initialized backing32 with starts 0/16, the actual N32 network half bases.
The four ranges cover tail1..19 at start0 and tail1..15 at start16. There is no claim for other
starts, partially initialized backing32, scratch48 tails, or different allocation sizes.
The standalone insertion len17..20 PFC deliberately uses a prefix of allocation32, not allocation20.

## Proposed run and acceptance

Request `widedomains-g2-20261105-01`, SHA256
`688168c844c7620715a3461e8826a836dd5347994a23b21d58d619e712646a80`.
Diagnostic, controls=true, inventory=false, jobs=1, gcb-e2-standard-4, three minutes per root.
Ten roots: 30 harness-minutes + 30 setup/closeout = 60-minute build timeout, reserve **$0.8100**.
Expected **67/67 covers**, zero unreachable covers; all request entries expect SUCCESS.
A TIMEOUT/failure in a prerequisite PFC blocks all dependent composition credit even if a consumer
is SUCCESS. In particular the transitive tail -> insertion -> network chain must be checked.
The request gate does not establish cover reachability or domain inclusion automatically.

All roots below have prefix `slice::sort::shared::smallsort::verify::widedomains::`.

| Root | Proof role | Expected covers |
| --- | --- | ---: |
| insert_tail_initialized_u64_backing32_tail1_to4 | real insert_tail PFC, restricted start0/16 | 7 |
| insert_tail_initialized_u64_backing32_tail5_to9 | same, tails5..9 | 7 |
| insert_tail_initialized_u64_backing32_tail10_to14 | same, tails10..14 | 7 |
| insert_tail_initialized_u64_backing32_tail15_to19 | same, start16 permits tail15 only | 8 |
| insertion_stubbed_u64_backing32_len1_to16 | insertion PFC + verified tail consumer; starts0/16 | 8 |
| insertion_stubbed_u64_backing32_len17_to20 | insertion PFC + verified tail consumer; start0 | 7 |
| swap_safety_u64_backing32_tail_comparator | matching swap PFC for G2 function-item F | 9 |
| unstable_network_safety_u64_n32_swap_insertion_stubbed | real unstable N32, swap/insertion stubs, real merge | 5 |
| merge_safety_u64_len8_scratch48_src32_dst0 | merge PFC, exact first sort8/general-N32 scratch geometry | 5 |
| sort8_safety_u64_scratch48_src32_dst0_merge_stubbed | real sort8, real sort4 bodies, verified merge stub | 4 |

## Exact domain inclusion and frames

Every G2 root fixes T=u64 and F to this module's new function item `tail_less_u64`. It reads both
references with volatile reads and returns a fresh arbitrary bool. This is not G1's F item;
therefore G2 includes a matching swap PFC rather than reusing G1's differently typed F evidence.
The F item calls a coverage-only hook. In the two insertion PFCs, the verified tail stub removes
all callback execution, so only this hook is replaced with an empty function. Reads, bool generation,
the comparator function-item type and all target requires/modifies remain unchanged. Callback
true/false covers remain in all four tail PFCs and in the swap/merge/network/sort8 roots where real
callbacks run. Insertion roots retain length endpoints, both applicable starts, arbitrary offset
endpoints/nonempty loop and normal-return covers. The original G1 comparator is untouched.

| Consumer calls | Matching PFC union | Why included / frame |
| --- | --- | --- |
| insertion PFC len1..16, start s=0/16, arbitrary offset1..len; actual loop calls insert_tail at relative tails offset..len-1 | Four initialized-tail PFCs, same F/u64/[u64;32], s=0/16, tail1..19 and s+tail<32 | Each call has tail<=15, so both starts are allowed. Initialization includes the whole allocation; only inclusive [s,s+tail] may change. Explicit frame checks all other elements |
| insertion PFC len17..20, s=0, arbitrary offset1..len | Same four tail PFCs | Each relative tail<=19, s+tail<32. Tail partitions cover all values, not only offset1. If offset=len there are no tail calls. Insertion modifies only [s,s+len), with explicit outside-array frame |
| Actual unstable u64 N32 network, two sort13 sites: base0/16, relative swap a,b<=12 | G2 swap PFC: initialized backing32, any base<32 and a,b<32-base, same F; equal positions included | Both real bases/positions fit; only the two absolute positions may change. Separate PFC is required by F identity |
| Same network's actual insertion calls len16, offset13, starts0/16 | Insertion len1..16 PFC, arbitrary offset and both starts, identical F/u64/allocation32 | Both calls included; full-slice insertion frame is supplied by its unchanged contract. Transitive credit additionally requires matching tail PFC SUCCESS. Final merge32 is real, not stubbed |
| Real sort8's merge call: u64, len8, source scratch[32..40], destination scratch[0..8] | Merge PFC: exactly one [MaybeUninit<u64>;48] allocation, same offsets/length/F, initialized source8, outside uninitialized | Two real sort4 calls populate exactly [32..40] from source backing32[0..8]. Other scratch slots remain uninitialized before merge. Source and destination are disjoint within allocation48; modifies only destination8; explicit source8 frame |

The sort8 consumer invokes the real helper body with the same arguments as the first sort8 call
inside small_sort_general N32: v_base at backing32[0], dst at scratch48[0], temporary at [32].
It checks all 32 input values are framed. It does not read output after the safety/modifies-only
merge stub: there is no initialization/sortedness postcondition. This is one merge call site,
not the complete general route, not its second sort8 call (src40/dst16), and not the final merge32.
No generic/stateful comparator, ZST, aliasing, arbitrary allocation or panic-unwinding theorem.
Uninit/value-validity instrumentation stays off, so fixture initialization descriptions do not
constitute a proof of those properties. The explicit order-violation boundary is cut under abort
semantics only in the roots that execute a real merge. The successful G1 network has the same limit.

## Budget, checks and next steps

Own spent $0.4860 + G2 maximum reserve $0.8100 = **$1.2960 <= $4.00**. No retries; at most G1–G3,
one compile-error repair per build only if spent + reserve stays within cap. G1 is build 1 of 3.
Window started 2026-11-05 07:44:34.233475 UTC; main deadline 12:44:34.233475, closeout 13:14:34.233475.
Recheck project/own budget, stable owner authorization, exact pushed SHA and remaining window before
dispatch. A stale GO does not extend the main window or authorize another build.
The current project budget snapshot and maximum total with G2 are in RUN-LEDGER.json.

Static checks must show ordinary=219 unchanged, cfg-on=273 (253 original + 10 G1 + 10 G2), existing
verify files and every G1 function/attribute unchanged, runtime/contracts byte-identical, unchanged
tooling, no static orphan item/import/macro arm, exact ten G2 names and request hash. Rustfmt and
diff check must pass. Source name lists are not compiler inventory; no full std inventory is requested.
Use separate library/research `[skip ci]` commits, push without force, stop with PRE-BUILD REVIEW.
After new exact-packet GO, dispatch once via `research/challenge-8/kani-k1/tools/k1g.sh`, cache
`/tmp/widedomains-k1g-g2`; record UUID, `watch BUILD`, end the turn. No status polling.
After wakeup collect bounded summary/rows/peaks/log-grep and check-tooling, verify each prerequisite,
cover count and domain inclusion before credit. G3 requires analysis and another coordinator GO.
Remaining work includes merge16/32 with their specific actual call-site geometries and still-unproved
general scratch48 insert_tail domains. G2 cannot close G1's broad initialization/start TIMEOUT domains.
