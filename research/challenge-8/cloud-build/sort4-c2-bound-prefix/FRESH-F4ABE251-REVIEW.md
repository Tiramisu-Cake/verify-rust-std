# Independent raw review — fresh C1+C2 bounded prefix

Build `f4abe251-23f9-459e-a418-6372b6553057`; evidence root
`/tmp/c2-f4abe251-read/allprooflogs/cases/sort4-c1-current-recovery`.
**Verdict: PASS for the bounded C1→C2 resource composition and its allocation
placement, conditional on treating this exact experimental translator profile
as the theorem being assessed.** This review does not accept the translator as
globally trusted, prove full `sort4_stable`, or supply native/caller composition.
The collector's original `accepted=false` and pending fields are preserved.
No local compiler, extractor, verifier, or proof execution was used.

The fresh positive has `0 errors found (184 statements verified)`. Directly
checked pins are annotated source SHA-256 `ecd83f8c0840a07f138bc8afa2a36c661f296d748693afa2a0a61667cb3372e4`,
complete normal/readonly MIR `e270457999f9371bc94664917ebd96699eecec0b91148899aa48c511f398c82b` /
`3598b01b91af60d4ad5f96cabc8225aad30bb9a2bd73eb7fc7add15473fb1a29`,
pre-AST `4fa7d49e420dc80681328bacdf08bb1d674dc2413001b99501da1c09b11dbb0a`,
and post-AST `96b7dd87721cb35e3808fae4f1084e8c270078052dff93ef4fbf913190fa7ec9`.
The post-AST keeps the original target header and complete raw non-ZST
pre/normal/unwind CURRENT contracts. The source/runtime inventory remains five
FnMut calls, eight selects and four copies; this bounded AST executes the first
two comparisons and returns after their normal recovery. The files named
`normal-sort4-full-mir.txt` inside the copied positive fixture are older C1
fixture data; the admitted C2 pins are the evidence-root
`c2-normal-sort4-full-mir.txt` and `c2-readonly-sort4-full-mir.txt` above.

Target AST inventory: 143 retained local declarations, comprising 125 outer,
8 in the C1 strict `'cmp` block and 10 in its sibling C2 strict `'cmp2` block,
each original C1 `_27`–`_34` and C2 `_63`–`_72` declaration occurring once.
The 18 declarations for future `_98`–`_103`, `_105`–`_110`, `_134`–`_139`
are absent. The 125 outer include five eager future `std_tuple_0_` locals;
they remain an extra produce/free obligation. The complete MIR edge audit
reports linear noncleanup blocks and direct `Continue` unwinds in both modes;
first `StorageLive` of every removed future normal-MIR local is after C2
FnMut BB53 (first at BB62), and the corresponding readonly locals first live
after C2 BB4 (first at BB21). No C1/C2 unwind enters that future suffix.

Allocation admissibility follows from the emitted AST and the frozen kernel,
not from a guessed per-local log count. In `src/verify_expr.ml` around
1510–1523 and 1565, address-taken preprocessing attaches each declaration
to its lexical `BlockStmt`'s `locals_to_free` list. In `src/verifast.ml` around
988–1072, an uninitialized struct/tuple declaration registers with that block
and `produce_object` creates its local object; non-address-taken uninitialized
pointer/bool/usize locals are symbolic. `free_locals` around 180–201 consumes
each registered `RefType` object; `BlockStmt` around 2880–2901 invokes this on
normal, return and outward goto paths. Consequently C1's tuple is produced
once after C1 entry and freed on C1 normal/unwind; C2's tuple is produced only
after C1 normal join and freed on C2 normal/unwind; the outer unit locals are
freed at every target return. The raw positive trace corroborates scope frees
at lines 1271/1333 (C1), 1610/1672 (C2), and root frees at 1306/1645/1708,
each followed by the original return-post consumption and leak check on the
respective C1 unwind, C2 unwind and normal path. `-verbose 2` does **not**
identify every local producer or chunk; this is a deterministic kernel/AST
derivation plus observed path exits, not an assertion of 59 visible heap chunks.
Removing the future 18 prevents their eager translated object footprint from
being imported into the artificial return before their source storage lifetime.

The post-AST has exactly two callback switches and two independently registered
`Output=bool` projection equalities, under the distinct `'cmp`/`'cmp2` scopes.
C1 normal closes its debt and recovers pair/joins four at source 193/194 before
entering C2 at 196; C1 direct unwind recovers/joins at 187/188 and returns at
190 without entering C2. C2 normal closes debt, exits scope at 225, recovers
at 226, joins at 227 and reaches the bounded normal return at 258. Its direct
unwind recovers/joins at 220/221 and returns at 223. Same-unit `recover_pair`
and `join_four_owned_cells` are verified before target entry. On all three
paths the raw trace consumes the original CURRENT source/F/optional-destination
post and performs the leak check. C2 therefore receives current source/F/thread
resources derived from C1's verified normal recovery, with only the unchanged
raw target precondition supplied at entry. This is the completed internal
bounded C1→C2 composition; native→C1 and actual caller→sort4 are still open.

All seven negative controls have target entry and the intended *first* failure:
C2 normal/unwind missing-close fail the comparison-debt precondition at
`verified/lib.rs:68` after their respective recovery calls; normal/unwind
omit-join fail the original `foreach<T>(..., own)` post at lines 142/149;
normal false-post fails the original normal post at 140; C1/C2 direct-unwind
false assertions fail inside the respective epilogues at 190/223. These are
reachability/resource checks, not proof of an absent later suffix. The exact
source mutant is refused before proof, saved MIR/pre-AST mutants refuse
admission, the default-off C1 profile remains VF0, and the unbound C2 scaffold
still refuses. No dead-code error or disabled post/leak check appears in the
positive. The fresh result establishes only this source-linked two-comparison
prefix under the reviewed experimental profile.
