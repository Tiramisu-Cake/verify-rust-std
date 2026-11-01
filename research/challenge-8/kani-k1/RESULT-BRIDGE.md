# RESULT BRIDGE — B1 SUCCESS

G1 `642e7d4e-60e8-429b-8aed-1817ecd233d9`, request `bridge-g1-20261101`, GO/head `08bcec360d`.
Library commit `b07dc219a27af35e9832335c129bb8759926b7ca`, unchanged tree
`f3bf04b5ccf83592e98c1d536d21713e7c01363a`; Kani `9461e07af7`, nightly-2026-10-12.
Cloud Build SUCCESS, six rows expected, Kani exit1 from intentional negatives; check-tooling passes.
Own 1 build, spent **$0.1215**, reserved $0 (cap $0.75); no compile error, so no G2.

Raw `bidirectional_merge<T,F>` -> `adapter<T: FreezeMarker + MergeBridge<F>,F>` -> sole
u8/fn-pointer impl -> `merge_profile::<LtU8>(v,dst,*is_less)` verified replacement.
No comparator substitution/transmute/blanket fallback. Leaf/A3 PFCs have no substitutions.
Caller and leaf: T=u8, F=`fn(&u8,&u8)->bool`, value=LtU8::CMP (key x>>1), N3, halves1+2;
separate initialized exact source `[u8;3]`, offset0; separate `MaybeUninit<[u8;3]>` dst, offset0;
right pair sorted, dst-only frame; independent LtU8 full-value probe set before call.
Oracle uses that same probe, key sortedness/full-value count, unchanged source/probe, no F calls.
Wrong-F keeps sorted domain/regions/type; unsorted has right keys[1,0], no sortedness assume.
A3: separate initialized source3, initialized backing4, dst[0..3), sentinel[3], same fn/probe;
modifies only dst3, mutation inside target at :122 after cover at :119. Distinct geometry;
this calibrates this target's frame, without extending leaf or establishing all profile frames.

| # | Harness suffix (bridge::) | Status | VT s | Failed/total; unreachable | Covers |
|---|---|---|---|---|---|
| 1 | bridge_leaf_u8_n3 | SUCCESS | 24.659 | 0/566;68 | 1/1 |
| 2 | bridge_caller_positive_u8_n3 | SUCCESS | 2.861 | 0/538;65 | 3/3 |
| 3 | bridge_caller_wrong_f_u8_n3 | FAILED expected | 0.899 | 1/538;70 | 2/3 |
| 4 | bridge_caller_unsorted_u8_n3 | FAILED expected | 0.779 | 1/532;71 | 2/3 |
| 5 | bridge_frame_positive_u8_n3 | SUCCESS | 11.219 | 0/442;40 | 2/5 |
| 6 | bridge_frame_negative_u8_n3 | FAILED expected | 20.019 | 1/442;40 | 3/5 |

Only failures: row3 canonical requires at specfix.rs:317; row4 sorted-halves requires at :318;
row6 `Check that *var_15 is assignable` at bridge.rs:122. No OOB/unsupported/unwind/other failure.
Substitution established: reported raw/verified stubs + all3 positive caller covers (adapter
included) + rows3–4 exact requires rejection under unchanged --no-assert-contracts lane.
A3 write reachability after its unconditional cover follows from failure at that write;
terse output gives only aggregate covers, extra unreachable cover identities remain UNKNOWN.
Monomorphization and recursion did not block this exact u8/fn-pointer/N3 smoke. Wider T/F,
actual sorting callers, N9/scratch geometries and unsupported-F compilation remain untested.
Static ordinary exact200 preserved, cfg-on forecast382->388; rustfmt/source checks pass.
Whole verify wall2:18.77, kani-compiler RSS1.72GiB, sampled cbmc peak0.51GiB; uninit off.
B1 is not B2/full CI or N16 credit. Next: actual Stable u8 N9 A real-body / B bridge with
same fn-pointer/probe and independently matching leaves; no automatic leaf-domain transfer.
Artifacts: `bridge/g1.{summary.md,summary.json,extracted.txt,acceptance.json,status.json,tooling.txt}`,
`g1.cost.txt`, dispatch/watch, budgets; `bridge/PREBUILD.md` is the historical review packet.
REVIEW REQUEST `08bcec360de5d25be2b3631d2eac4d9004ed7312` — accepted by coordinator.
**BRIDGE ЗАВЕРШЁН**
