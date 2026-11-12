# Source-bound Hrepr / Hepoch cross-cut

Only `library/kani_core/src/mem_init.rs`. Frozen R1 `1cd96e354ec45346b61c245554a50a8af8cb5ce7`, U `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`, intermediate R5-01 `bcc1a2af3fe13599b88acabc78c33e1394407dc5`. INPUTS.json binds their committed blobs/dependencies and the complete R5 package at c114b13fb4bfc08502529d78c45344ec724d56f2. Historical files are unchanged.

R5 HUNK-MAP atoms use zero-based half-open U/R1 line intervals. This conceptual partition carries coherent operations, not half the changed lines. R6 does not isolate pointer placement, lifetime and private membership from one another.

| R5 atom | Subgroup | Coherent operation |
| --- | --- | --- |
| D01 | Hrepr | Unmarked static Option versus fields of marked MEM_INIT_STATE |
| D02 | Hrepr | Five scalar buffer fields, payload and activity representation |
| D03 | Hrepr | Complete constructor, inactive default false/None; no epoch operation |
| D13 | Hepoch | Epoch invalidation inside initialize; active=false maps to Option=None |
| D14 | Hrepr | Clone+Copy ArgumentBuffer(index:usize,pointer:*const (),layout:usize) |
| D15 capture | Hrepr | R1 lines [405:407]: capture object ID and offset from live source pointer; U keeps thin pointer from preceding unchanged to_raw_parts |
| D15 selection | Hepoch | R1 [407:409]: comment and index0-or-any guard; U [376:378]: bool local plus demonic guard |
| D16 | Hrepr | Payload writes: five scalar assignments versus Some(pointer record) |
| D17 | Hrepr | Paired active/Option read, index/layout check, ID/pointer load and matched clear |
| D18 | Hrepr | Matched return stays attached to consumption |

D15 is split only between capture and selection. The mandatory-return comment remains verbatim R1 in R6-01, although its diagnostic any-only guard no longer guarantees return0. In R6-02 the U bool local is removed and the mandatory guard is inserted without adding that R1 comment. No executable delta is hidden as formatting.

| Candidate | Hrepr | Hepoch | Exact changes from template |
| --- | --- | --- | --- |
| R6-01 25197eb23e9d4b0d6b69d69ff21c2de135bdda7c | R1 scalar marked state | U selection + no reset | From R1: guard becomes `if super::any()`; remove only initialize's active=false |
| R6-02 258d6af1ea44411ec3f3aa0a4921c05c3700d6f9 | U pointer unmarked state | R1 selection + reset adapter | From R5-01: remove should_store local, use index0-or-any; add ARGUMENT_BUFFER=None inside existing initialize unsafe block |

STATIC-AUDIT.py proves complete expected-file equality and inverse Hepoch equality: R6-01 restores exact R1; R6-02 restores exact R5-01. Thus R1/R1 is existing heavy R1 and U/U with R1 Hcopy/GLUE is existing converted R5-01, without creating a third candidate. Hcopy/GLUE whole copy-through-bless span and every other function outside constructor/initialize/store/load are exact R1 bytes, with hashes in STATIC-CHECKS.json. Entire trees differ from R1 only at this file; all compiler, contract, callers, macros, tests, driver and toolchain sources stay exact R1.

R6-01 constructor and matched-load clear remain R1; only epoch clear is removed. A declined store or later initialize can retain active/stale payload. R6-02 constructor/global None, captured pointer, load/match/layout check and matched clear remain U; initialize adds a distinct None write. Its load still calls copy_init_state_single→copy_init_state→R1 copy→copy_by_id. Neither adds marker/assigns registration, pointer reconstruction or assumptions.

Source-site line inventory in STATIC-CHECKS.json is a source observation only. Actual reset placement, retained path/DFCC targets, frame ranges and pointer lifetime remain UNKNOWN until coordinator inventory. Hash/path equality does not establish emitted causality or equivalent obligations.
