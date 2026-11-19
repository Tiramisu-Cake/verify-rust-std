# Initialized / read / write / post-init sets

These are source-derived **obligations**, not proved summaries or executable assumptions. Scope: normal return, concrete `u8, KeyLess<u8>` (pure comparator, no external writes), live aligned disjoint raw output regions, exact 8faf bodies. Generic T padding/validity, non-Copy ownership and panic/unwind/Drop posts need separate proofs. For u8, `ptr::read` does not clear physical initialization bits; an ownership move/gap is not automatically an uninitialized byte. Track logical ownership separately.

Use disjoint labelled allocation/region coordinates: `V[a,b)`, `D[a,b)`, `S[a,b)`. `K` is the actual initialized byte set on entry, established by real initialization stores, not a ghost assumption. `I` below is the required subset of K. `R` is a may-read set over executions (includes comparator data reads); `W` is a may-write footprint of the actual helper, not its broader declared modifies. `P` is the intended exact initialized set on normal return, conditional on B-MASK's store/state coupling. No additional bytes become initialized merely because pointers are made. Auxiliary pointer/scalar locals start initialized when assigned; fresh byte temporaries start initialized only when written from initialized inputs. Every earlier hole outside W must remain a hole, but the current oracle alone cannot establish that complete negative-set claim.

| Helper / route | I: initialized on entry | R: data reads | W: data writes | P: post-init / sequencing |
| --- | --- | --- | --- | --- |
| `KeyLess<u8>` comparison | argument cells `{a,b}` | `{a,b}` | empty | `K`; receiver is initialized; no storage mutation |
| `swap_if_less` | `V{a,b}` | `V{a,b}` plus initialized local temp | `V{a,b}`; temp initialized by selected `ptr::read` | `K`; both positions stay init, including a=b case. Other V bytes may be holes if no full typed V slice is formed |
| `sort9_optimal` | entire supplied typed slice `V[0,n)`, n>=9 | `V[0,9)` | `V[0,9)` | `K`; suffix stays unchanged; direct network comparison positions are fixed |
| `sort13_optimal` | entire typed slice `V[0,n)`, n>=13 | `V[0,13)` | `V[0,13)` | `K`; suffix unchanged |
| `insert_tail(begin,tail)` | `V[0,t+1)`, t>=1 | `V[0,t+1)` and temp | subset of `V[0,t+1)`; none on early return; temp written from tail | `K`; never an initializer for an unwritten tail; temp plus CopyOnDrop fills logical gap before return |
| `insertion_sort_shift_left(v,offset)` | `V[0,n)`, 1<=offset<=n | `V[0,n)` | subset of `V[0,n)` | `K`; sorted-prefix premise concerns sorting, not initialization |
| `small_sort_fallback` | `V[0,n)` | V if n>=2, else empty algorithm read set | subset of V if n>=2 | `K`; no scratch output |
| `sort4_stable(v_base,dst)` | `V[0,4)`; D need only writable | `V[0,4)` | exactly `D[0,4)` | `K union D[0,4)`; four actual nonoverlap copies; source unchanged, dst is not read by body |
| `merge_up(left,right,dst)` | `{left,right}` | both source cells | exactly `{dst}` | `K union {dst}`; selected source copied before dst advances; returned pointers are geometry, not readable cells |
| `merge_down(left,right,dst)` | `{left,right}` | both source cells | exactly `{dst}` | `K union {dst}`; dst.sub(1) formation needs bounds; wrapping source pointers are not dereferenced after exhaustion |
| `bidirectional_merge(v,dst)` | typed `V[0,n)`, n>=2; sorted halves separately | `V[0,n)` | exactly `D[0,n)` on normal return | `K union D[0,n)`; after j pairs, init D prefix `[0,j)` and suffix `[n-j,n)`; odd remainder fills the middle. No dst reads before fill |
| `sort8_stable(v_base,dst,scratch)` | `V[0,8)`; D/S only writable | first V, then `S[0,8)` **after** two sort4 calls | `S[0,8)` and `D[0,8)` | midpoint `K union S8`; return `K union S8 union D8`. Actual body does not write V despite broader safety wording |
| `CopyOnDrop::drop {src,dst,len}` | `SRC[0,n)` | `SRC[0,n)` | exactly `DST[0,n)` if n>0 | `K union DST[0,n)`; n=0 leaves K. Separate memcpy-state proof required. This row is a footprint obligation, not a new proof of panic restoration |
| `small_sort_general_with_scratch`, n<2 | `V[0,n)`; scratch backing valid as MU | empty algorithm data set | empty | `K`; no claim scratch payload is initialized |
| same, 2<=n<8 | `V[0,n)`, S writable capacity>=n+16 | V; initialized growing S halves; then S[0,n) | `S[0,n)`, `V[0,n)` | `K union S[0,n)`; seed both halves with one copy; copy each next element **before** insert_tail; form source slice only once all S[0,n) initialized |
| same, 8<=n<16 | same | V; growing S halves; then S[0,n) | `S[0,n)`, `V[0,n)` | `K union S[0,n)`; sort4 seeds 4 cells at each half's base; remaining scratch stays as entered |
| same, 16<=n<=32, u8 | same | V; `S[n,n+16)` after sort4 seeds; growing `S[0,n)`; final merge S[0,n) | `S[n,n+16)`, `S[0,n)`, V | `K union S[0,n+16)`; two sort8 calls use temp blocks at n/n+8; for other type-size routes this formula changes |
| `small_sort_general` | `V[0,n)`; fresh local raw scratch allocation | general-with-scratch R above | same plus local scratch | external post-init `K`; local scratch post-init as above then lifetime ends. `MaybeUninit<[T;48]>` allocation/extraction remains a mandatory support path |
| `small_sort_network`, n<2 | typed V | empty algorithm reads | empty | `K`; stack scratch not created |
| same, 2<=n<18 | `V[0,n)` | V | subset of V | `K`; allocated MU32 scratch payload is not read/written on this return route. Its creation may still affect support |
| same, 18<=n<=32 | `V[0,n)` | V; then local scratch `[0,n)` **after merge** | V and local `S[0,n)` | before copyback `K union S[0,n)`; external return `K`; scratch suffix `[n,32)` stays unwritten then allocation dies |
| stable/unstable trait dispatch wrappers | full typed V; writable MU scratch where required by route | selected concrete callee R; old/spec reads only V | selected callee W | route-specific P above; no generic dispatch/init theorem follows from any bounded callee |
| geometry helpers / threshold / efficient-swap predicate | initialized pointer/scalar arguments | no pointee data | no pointee data | `K`; address equality/distance alone creates no init or ownership |
| `panic_on_ord_violation` | no additional input bytes | no caller data needed | no normal caller output | no normal post; retain failure/abort boundary. Does not discharge unwind/Drop obligations |

For general sort let h=floor(n/2), p=1/4/8 for the three rows. Seed `S[0,p)` and `S[h,h+p)`. For each half `(o,d)=(0,h)` or `(h,n-h)`, just before copying index i, require initialized `S[o,o+i)`; copy V[o+i]→S[o+i], then call insert_tail on the now-initialized `[o,o+i+1)`. Only after both halves is the typed merge input `S[0,n)` legal. Sorting/order premises remain separate. A planning invariant must later be checked against actual stores; do not insert it as an unchecked assume.

Source/spec helpers also have memory footprints. `span::capture/ordered(p,n)` and `sorting_model::snapshot` read exactly the initialized source span; `span::post` and the functional post read exactly the now-initialized output span. Their W is empty and P=K. They must not create slices/snapshots across holes. `active/enabled` read type/scalar model state, not payload; their W is empty. An Init query reads shadow state, with **empty payload R/W**; tracked-coordinate changes made by compiler models are not user data stores. Known-value frame/canary helpers read only explicitly initialized outside-dst cells; no whole-backing `[u8;48]` view is allowed.

## Exact MU48 continuation masks

These retain the S3 diagnostic geometry at 8faf; they are new ON proposals, not promotion of those diagnostics. The independent `before: [u8;48]` seed is fully initialized, but it does not initialize the distinct MU backing. Only the listed actual writes do.

| Case | I=K0 after harness writes | Actual merge R | Actual merge W | Intended K1 | Remaining holes |
| --- | --- | --- | --- | --- | --- |
| L, src32→dst0, n8 | `[32,40)` | `[32,40)` | `[0,8)` | `[0,8) union [32,40)` (16 cells) | `[8,32) union [40,48)` |
| R, src40→dst16, n8 | `[0,8) union [32,48)` | `[40,48)` | `[16,24)` | `[0,8) union [16,24) union [32,48)` (32 cells) | `[8,16) union [24,32)` |

K0 sizes 8/24; exactly8 destination cells added. Source and destination are disjoint; K0 and destination are disjoint. Cell8 is an unwritten sentinel in both. Query positive initialization of source and dst only; compare full independent source values, output sortedness/count and all K0 outside-dst values, with a known-init canary. Assert Init of dst before loading its values. Neither functional success nor a single sentinel counterexample proves the full remaining-hole set. B-MASK must be resolved for that theorem.

Existing partial fixtures use `assume_init()` output loads and a 48-iteration setup/frame loop with unwind50. Do not run those unchanged under this plan's bound36 or treat their OFF outcome as init evidence. A later harness design may use explicit initialized ranges (8/24 entry cells,8 output cells) without changing K0/K1 or source value freedom; no cap adjustment is proposed.
