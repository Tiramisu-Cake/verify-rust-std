# Caller, type and geometry bridges

All kernel citations are at source `8faf8e62af8f82b5c46af020086f8df591b6757e`,
`library/core/src/slice/sort/shared/smallsort.rs`. Intervals below are element
offsets relative to active V or scratch S. Let h=floor(n/2), r=n-h. A numeric
interval check is not a pointer-provenance or locality proof. Each bridge is OPEN;
the first direct-call package exercises its own actual path without importing
a provider. Bounded sorting cases are not automatically summary providers.

| ID | Required connection | Exact outstanding scope |
| --- | --- | --- |
| B-F | fallback -> shift -> insert -> gap restoration | Cell/KeyLess at V34/base1, n5..16; shift offset1, tails1..n-1, spans2..n. Typed frame/init/count and caller loop still required (220–224,667–737). |
| B-Nprefix | network -> actual sort9/sort13 -> swaps | sort9 region lengths9..12 and sort13 lengths13..17; each sorts only its first9/13 and must preserve suffix/exterior.25/45 literal swap sites, full byte values, exact comparator footprint (332–392,494–610). |
| B-Nsuffix | network prefix -> shift -> insertion | Offset9 or13, including zero-iteration offset==len at9/13. n17 includes tail16/span17; n18+ regions have new bases. Prefix sortedness/init plus complete suffix frame are premises, not assumptions granted by matching lengths. |
| B-Nregions | first region -> second region -> sorted halves | For n18..32 use h,r, bases0,h in V; absolute fixture bases1,1+h. Region pointer test must execute twice and terminate; neither equal relative swap indices nor N9/N13 at base1 establishes the second base. n25 is12/13 with different networks. |
| B-Nmerge | sorted V halves -> stack32 merge -> V copy-back | All n18..32, even and odd; V initialized, private MaybeUninit32 initially uninitialized, n output elements initialized before copy/read, exact source/dst frames, nonoverlap/provenance and production copy-back (383–390,937–1018). No standalone merge fixture proves this caller. |
| B-Gseed | V -> sorted scratch halves | n2..7 copy1 seeds, n8..15 sort4, n16..32 size<=16 sort8; size>16 keeps sort4. Extensions copy a fresh V element before inserting it. All typed frames, destination init and desired-length/offset logic (241–314). |
| B-Gsort8 | sort4 + internal merge8 -> actual sort8 | Two sort4 calls initialize each temp8's sorted halves before merge8. Actual sort8 body post plus frame/init, not registration or assumed consumer (812–835). |
| B-Ggeometry | actual sort8 -> all34 scratch contexts | For every n16..32, triples (V+0,S+0,S+n) and (V+h,S+h,S+n+8), each length8; internal merge8 pairs (src,dst)=(n,0),(n+8,h) in one S allocation. COVERAGE.json enumerates34. Separate src8 fixture or one same-allocation pair does not imply these. |
| B-Gmerge | sorted S halves -> final V -> guard disposition | n2..32, S[0,n) -> V[0,n), opposite direction to network merge; CopyOnDrop on permitted failure and mem::forget on success. Odd center, full counts, source/exterior frame and initialized destinations (286–330,937–1018). |
| B-Gscratch | stack48 -> stable caller-supplied scratch | Separate initialized V34/base1 + MaybeUninit48 is one finite fixture. Full48 view, prefix view, exact n+16 allocation, larger/interior scratch and disjoint views within one allocation are distinct contexts. Stable external scratch requires writable valid storage and nonoverlap, not an assumed allocation theorem. |
| B-types | u8 -> Cell / NonCopyByte / large types | No automatic transfer. Cell fallback needs its own concrete model and actual body; NonCopyByte general uses its own exact pair. Its size1 does not exercise size>16. The current model is inactive for other types; a >16 fixture needs a separately reviewed whole-value model, not an inactive/vacuous post or a byte-only projection. |
| B-dispatch | direct helpers -> six trait bodies / real callers | Stable default insertion; stable Freeze general-with-scratch; unstable default fallback; unstable Freeze forwarding; Freeze default conditional general/fallback; Freeze+Copy conditional network/general/fallback. Exact type/cfg, threshold, chosen body, caller scratch and entry length bound must be bound independently (32–192,194–218,1040–1044). |
| B-provider | exact bounded evidence -> valid contract provider -> consumer | Requires actual callee proof at same source/tool/cfg/T/F, contract domain/footprint/init and every caller geometry/premise, plus separately checked consumer use. No bounded admission, PFC declaration, diagnostic assumed/stub consumer, canary or numeric address equality supplies this bridge. |

Dispatch sizes: stable default/unstable default threshold16; stable Freeze
general threshold32 with external scratch for n>=2. Unstable Freeze default
chooses general iff size*48<=4096, else fallback. Freeze+Copy chooses network
iff size<=8 and size*32<=4096, otherwise general iff size*48<=4096, else fallback.
u8 therefore selects stable general and unstable network; NonCopyByte selects
Freeze-default general; Cell selects default insertion/fallback. Size>16 general
rows are real obligations even though neither u8 nor NonCopyByte exercises them.
Large/zero-sized types, arbitrary comparators, generic payloads, callback writes,
ownership, panic/Drop and stability remain beyond these finite sorting posts.

The six-body S1 smoke domains0..3 and historical S3 leaf/domain claims remain
their own records. This task does not review or promote them. Their possible
overlap does not close a fresh S4 helper/caller row. General rows are marked
OPEN_S4_FULL_LENGTH in the map even when a narrower historical smoke/leaf exists.

For future network merges require source-bound even/odd split, both-region
entry, both merge choices, ties, useful return, copy-back and preservation of
outside V. For general add seed-choice, both half extensions, scratch capacity,
internal merge8 source/dst separation and guard disposition obligations. Covers
must be feasible under lawful input ordering; a post-call `cover(true)` alone
does not bind an internal branch. Exact additional bridge-root labels and
lowered property origins must be frozen during those later implementations.

All34 general sort8 contexts and every network absolute region base are
enumerated in COVERAGE.json. Completion at one length is not interpolation;
completion of all lengths at one fixture is still not an all-geometry theorem.
