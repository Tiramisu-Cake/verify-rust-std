# Replay controls — NOT_RUN / preparation only

Exact source identities and argv are in EXPORT-MANIFEST.json and REPLAY-REQUEST.json.
C1 source SHA/tree are frozen; runtime binary/model hashes await CI, and the final library pin awaits coordinator confirmation. Dispatch
phase/owner/ledger/slot/budget are UNASSIGNED. Preparation Cloud cap $0.

| Control | Exact setup | Required interpretation |
| --- | --- | --- |
| Three legal ON PFC roots | Exact selectors and unwinds16/34/34 in ROOT-MAP; real sort4/merge-profile/real merge | Useful checks/ensures reached, SUCCESS, no Unsupported/frame error; bind selected Check body |
| Matched OFF companions | Same source/tool/model/cfg/geometry/argv except remove -Z uninit-checks | Compatibility only; cannot replace positive ON evidence |
| Ordinary organizer profile | Full upstream unstable list; --no-assert-contracts, exact selector, object-bits12 | Original semantics for ordinary callees; PFC Check takes precedence and needs separate binding |
| Matched raw sort4 legal | New replay_uninit_controls::sort4_raw_all_initialized_u64, ordinary proof, unwind16 | Real helper returns; entry/return covers reached, useful safety checks SUCCESS; same MU src4/dst4 geometry/callback as negative |
| Matched raw sort4 negative | New replay_uninit_controls::sort4_raw_hole_negative_u64; only src[1] unwritten | FAILURE at retained source[1] read in actual sort4/callback path; unrelated requires/early ref/Unsupported/frame/runner failures do not satisfy oracle |
| Sort8 boundary | Existing exact _merge_stubbed root, unwind34 | Inventory only: no destination-initialization postcondition or Replace-transfer credit |
| Optional tail sensitivity | Future separate post-helper read of unwritten scratch tail | Not implemented; cannot replace inside-helper negative |

Own test-only clone: /root/verify-rust-std-kani3300-replay-w15, branch
experiment/kani3300-replay-w15-prep. REPLAY-OVERLAY.json/replay-test-only.patch
bind the commit. One new gated module plus two declaration lines in verify.rs;
no production helper or old test changes. Both roots use one const-generic
exercise function and one callback. Valid [MaybeUninit<u64>;4] and
MaybeUninit<[u64;4]> allocations; write slots0/2/3, conditionally slot1, call
actual sort4_stable with raw pointers. No initialized slice/reference or
assume_init before helper entry. Callback read_volatile reads both supplied
references. No initializedness assumptions. Return cover is not a claim that
destination initializedness was proved.

PFC/Assert cannot use the hole as an inside-body negative: sort4's source
can_dereference requires calls C1 mem.rs:73-79/252-258 assert_is_initialized.
The ordinary --no-assert-contracts route is deliberate: C1
kani-compiler/src/kani_middle/transform/contracts.rs:565-585 selects Check and
Replace first, then Assert only without that flag, otherwise Original. The
negative intentionally violates an unsafe precondition to test instrumentation;
it is not contract proof for that state. Intended first access is
smallsort.rs:751, &*v_base.add(1). Bind callback read_volatile and generated/delayed
checks causally to that source[1] value. If Kani rejects reference formation
before the retained read or fails elsewhere, report GAP; do not relabel it.

| Option axis | Explicit setting for ON and OFF |
| --- | --- |
| Experimental valid-value-checks | OFF, flag absent; organizer default, no added checks-disable option |
| Standard pointer/bounds/overflow/assertion/unwinding checks | Defaults retained; no checks-disabling flags |
| Assertion reachability | Default; no --no-assertion-reach-checks |
| Coverage request | --coverage absent; required existing kani::cover rows still need reachability review |
| Solver/slicing | Default CaDiCaL and normal slicing (Kissat still version-checked as an installed dependency); no override/no-slice-formula |
| Object bits | Exactly12 in final --cbmc-args --object-bits 12 |
| Contracts | Full organizer unstable args, --no-assert-contracts; PFC target separately bound |
| Unwind | Source annotations16/34; no CLI replacement |
| Controls cfg | ON for every replay-manifest invocation; exact selector prevents unrelated controls running |
| Jobs/caps | One exact root, jobs1; proposed harness cap2400s; Build envelopes/aggregate cap require coordinator approval |

These receipts would cover uninit with experimental valid-value OFF, not
valid-value-ON. Historical G3 Build2 was OFF for both uninit/valid-value on
another Kani; it is neither the matched OFF companion nor ON evidence.

Expected outputs per root: exact source/tool/binary/model/profile identities,
effective argv/cfg/check flags, selected mode and Check body, useful SUCCESS
and cover rows, complete failures/locations, available scratch-state observations,
original exit, timeout/signal/resources, normal-return vs panic-cut boundary,
and artifact identities through Evidence Brief. No invented generated property
IDs or learning an oracle from arbitrary FAIL. Object-limit/timeout/OOM leaves
the root open without changing N/backing/offset/contract. Both final C1 CI overlays and the separate std test-only overlay remain unexecuted; all
proof results remain NOT_RUN. Static inventory is not MIR/ADT/Check-body binding.

Final Gate B control checkout/CI commit: REPLAY-CI-OVERLAY.json. The std patch is embedded there; no std production helper is changed and no separate std push is required.
