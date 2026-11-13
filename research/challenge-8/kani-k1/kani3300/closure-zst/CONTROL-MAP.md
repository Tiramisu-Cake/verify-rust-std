# Controls and qualification boundary

Static preparation only; every new root is NOT_RUN. TEST-MANIFEST pins bytes,
root and property class. All prior inputs/goldens remain byte-for-byte unchanged.

| Rows / exact IDs | Capture and valid storage | Conditional oracle |
| --- | --- | --- |
| P1/P2 original `scalar-pfc-{legal,hole}` | Capture-free PFC; frozen H1 research bytes | P1 useful outer assertion SUCCESS; P2 exactly the two bound checks of one read, no extra failure. |
| `capture-unit-{legal,hole}` | By-value `()` with full capture borrowed by `touch`; payload in MaybeUninit | Confirm layout0 query; initialized17 succeeds, hole read fails. |
| `capture-aligned-{legal,hole}` | By-value align64 ZST; size0 assertion, no size inferred from alignment | Same; test full layout0 with nontrivial alignment. |
| `capture-scalar` / `capture-padded` | Initialized u32 / repr(C) `(u32,u8)` by value; whole-capture borrow, valid fields read, no padding read | Confirm nonzero closure query and explicit closure Unsupported. Never all-data or all-true padding. |
| `capture-reference-{legal,hole}` | By-reference `&Cell<MaybeUninit<u8>>`, shared alias; callback copies valid MU and writes it back through Cell | Confirm closure layout query. Nonzero Unsupported is a boundary, not successful captures or a pointee proof. Earlier Cell/aggregate limitation is nondiscriminating. |
| `capture-raw-{legal,hole}` | By-value `*mut MaybeUninit<u8>` plus copied raw alias; lawful MU raw read/write, then targeted assume_init_read | Pointer initialized in both; pointee differs. Confirm closure Unsupported; never infer pointee init from pointer bytes. |
| `capture-mu-value-{new,uninit}` | By-value valid MaybeUninit::new(17)/uninit | Nonzero closure Unsupported; do not descend past the existing boundary to bless embedded union bytes. |
| `capture-mu-reference-{new,uninit}` | By-reference `&MaybeUninit<u8>` | Nonzero pointer-sized environment; separate pointee checks remain necessary. Same boundary, no embedded-MU admission claim. |
| `capture-union-value` | By-value correctly constructed ordinary union through byte field, wider inactive storage | Nonzero closure Unsupported; no recursive union-as-field workaround. |
| `capture-union-reference` | By-reference to same valid union, active byte read only | Pointer bytes differ from union storage; nonzero closure boundary, no pointee credit. |

Each of the16 new callback controls uses `copy_and_call<F: Copy + Fn(&MU<u8>)>`.
A typed `ptr::read(addr_of!(callback))` explicitly supplies a raw closure-pointee
read for the existing Check route; no fabricated uninitialized typed closure,
reference or scalar exists. Copy excludes ownership duplication of &mut or Drop.
`touch(&capture)` requires the whole capture under Rust2021 precise capture;
unit/align64 stay ZST while by-reference ZSTs would not. Legal/hole paired bytes
differ only in root name and the true/false selected MU state, checked by Python.
`Cell` interior mutation and raw-alias mutation preserve a hole in valid MU
storage. There is no assume about checking outcomes or direct hole→u8 before
the designated read. The union's inactive word is deliberately never read.

Source syntax/size assertions do not prove execution of data_bytes_for_ty.
CI must bind the actual closure type, full rustc size, raw read/copy operation and
resulting mask or closure-specific Unsupported. Earlier failure, optimized-away
query, different type's Unsupported or no path evidence => NONDISCRIMINATING,
not guard confirmation. Normal callbacks alone need not request closure layout.
The expected patterns require a closure-specific type description for nonzero
rows; they still cannot exclude all extra failures or establish the binding.

P1: preserve full bounded inventory/callsite binding; useful ensures reads17 and
outer postcondition_target::{closure#2}.assertion is reached SUCCESS. Reject
Unsupported, frame/protocol/invalid-value early exits and assumes hiding tail.
P2: after lawful return, the same first payload read must fail both local Check
(description *const u8) and delayed CheckRef (u8): both mean pointee init.
Require precisely that full bound failure set and no other failures. New IDs are
UNKNOWN until mapped, historical .1/.4 are not imported. Check/class drift =>
STOP with exact source/MIR mapping, no deduplication. Outer assertion may be
UNREACHABLE in P2 only. Check reachability, useful callback and outer assertion
are separate observations, not implied by total FAILED or empty closure masks.

Preserved source/golden hashes and roots are in manifest for frame/clause,
argument return/buffer/typed-padding, Move/Copy/false, immutable masks and
transfer qualification. They are retained gates, not newly executed tests.
Legal-pair/postcondition-hole and R7-C lawful-modifies remain subsequent gates;
`out` captures may require real upvar-layout support. Expected Unsupported is
not capture qualification: a required legal captured PFC remains a release blocker.
