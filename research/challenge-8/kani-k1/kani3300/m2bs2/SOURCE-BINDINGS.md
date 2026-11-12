# M2-B/S2 operand binding — static progress, runtime BLOCKER

Input hashes: INPUTS.json. Coordinator reports exact5f7 + unchanged C03, CI4804129592,
runs43248579074/43249480111. Complete argv/env, source receipt and binary hashes were not
supplied; generated-file identities are recorded independently. Coordinates below are 1-based
in the local supplied files, not proof of source/compiler identity. `T` means the supplied
`m2a__...legal_ordinary_transfer.symtab.kani.mir`; `G` means goto-functions.txt.

## Failed property selects LEFT, not a source site

properties.json records `<u8 as std::array::equality::SpecArrayEq<u8, 3>>::spec_eq.safety_check.1`,
class safety_check, expression `var_4 != FALSE`, equality.rs:157:18. trace.txt:434–442
reports .1 FAILURE and .2 SUCCESS. T:2072–2125 binds .1 to `_4 = _8(_6,[true;3])`,
`_6 = _5 as *const [u8;3]`, `_5 = &raw const (*_1)`; .2 is `_11 = _15(_13,[true;3])`,
`_13 = &raw const (*_3)`, `_3 = _2 as &[u8;3]`. Both precede `raw_eq(_1,move _3)`.
G:15828–15865 confirms left check/assert, right check/assert, then memcmp(a,b,3).
The CheckAs producer is uninit_visitor.rs:562–585, iterating both raw_eq args.
The PartialEq wrapper T:3724 forwards `_1,_2` unchanged; no operand reversal here.

| Actual emitted call | Left raw_eq referent | Right raw_eq referent | Bound evidence |
| --- | --- | --- | --- |
| body line30, Assert inner body `write_initialized::{closure#3}::{closure#0}` | `_20=&_16`, `_16:[u8;3]` returned from assume_init of `_17:MaybeUninit<[u8;3]>` | `_21:&[u8;3]=b"\x01\x02\x03"` | T:2885–3160; G:11317–11334 |
| ensures line14, `write_initialized::{closure#3}::{closure#1}` | `_6 = no_retag ((*_1).0: &[u8;3])`, captured reference to mutable out referent | `_5:&[u8;3]=b"\x01\x02\x03"` | T:2848–2882; G:11546–11552 |
| harness line39, `legal_ordinary_transfer` | `_8=&_1`, harness local out:[u8;3] | `_9:&[u8;3]=b"\x01\x02\x03"` | T:1189–1255; G:13088–13094 |

The ensures reference is created after inner body returns: T:1861–1878 / G:11841–11865
reborrow out, construct closure `{ &*out }`, then apply_closure. It reads out bytes, not
closure/capture storage bytes. No old() or array-value capture appears. G:12328–12359
computes mode4 outside contract clauses (mode0 inside); TASK mode contract and contracts.rs
identify 4=Assert. A concrete failing call still requires trace. Original branch in outer
write_initialized is distinct: its .assertion.1/.2 are rendered UNREACHABLE; do not use those
statuses to declare the inner Assert body assertion unreachable. Inner body properties are
separate identities in the inventory, even when descriptions/locations coincide.

## Emitted RHS binding and reset seed already exist

All THREE calls above lower their RHS pointer to
`m2a.a7ad3e73aae47d8a::m2a::AllocId(1, ThreadLocalIndex)` + byte offset0
(G:11332,11550,13092), typed backend unsignedbv[8][3]*. This is a shared emitted symbol,
not proof that original source allocations were identical or proof of a numeric runtime ID.
G:15214–15216, instructions6940–6941, in initialize_memory_initialization_state:
match live pointer_object(address_of(symbol)), base pointer_offset==0 and tracked_offset<3;
assign value={1,1,1}[tracked_offset]. Thus emitted positive RHS seed is present at reset.
Source finalizer admits frozen, Mutability::Not, relocation-free allocations and patches reset
returns; this source rule plus emitted seed does not substitute for an actual source registry
snapshot of every origin/Some/None alternative. Those original descriptor fields stay UNKNOWN.
In particular m2a.mir's `alloc1` is a REENTRY static; it must NOT be identified with the GOTO
symbol's `AllocId(1, ThreadLocalIndex)`. T's alloc16 is MEM_INIT_STATE, not RHS storage.

The reset definition also preserves nondet tracked_object_id and tracked_offset and initial
value=false (G:14988,15007,15015,15034,15054). Harness calls reset before local initial
out assignment and its normal true setter (G:13037–13053). These establish static order,
not which branch/object/offset was selected in the failed execution. Left stack/out storage
has no immutable seed justification. No mutable destination may be blessed at ensures entry.

## Concrete suspicious difference; causal link still absent

T's inner Assert body sets up MU copy/store/false-input/load effects but after
`_16=assume_init(move _17)` goes straight to `&_16` and equality. After `(*_22)=_16`
it returns; there is no local normal setter for _16 or out in that body. The outer Original
body has typed read and out true setter at bb63/bb66 (T:2700–2720). This is a bounded
candidate for subsequent relevance investigation, not an established cause of .1 FAILURE.
Need the actual reached invocation and full witness history; do not change D0, general
retarget/DFCC/ABI, or add seeds on this observation alone.

trace.txt is a rendered result report: 352 checks, 340 SUCCESS/1 FAILURE/11 UNREACHABLE,
zero State step markers and no JSON trace objects. `--trace` reaching CBMC does not make
Kani regular renderer print its assignments. call_cbmc.rs:179–191 forces --json-ui in the
regular path; cbmc_property_renderer.rs:466–488 consumes only the last trace location for
the failure message. Consequently actual call site, both runtime pointer object IDs,
selected offset, seed branch and last setter/copy/retarget before .1 stay UNKNOWN.
No extra rendered failure exists; inventory's 489 properties (including instrumentation,
reachability and unsupported_construct) are not the 352 processed result checks. Neither
missing inventory/result equality nor a dormant Unsupported entry is a new verdict.

The missing information is specifically a counterexample trace, not another MIR/global dump.
See CI-REQUEST.md for the source-supported passthrough and bounded return fields.
