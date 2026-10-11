# Fresh physical-node and MU-dependence review

Build `009ad1c2-119b-4598-98cf-573dcfb34c76`; proof=infra
`f8115f33f35d745b9da9ab5e01f0ee3b7908ce56`. Cloud SUCCESS means diagnostic
collection only: summary `verification_accepted:false`; native target exit1.
Archive SHA256 `48b943568293e42d56374af931963a85637fc69c2c62324f15df1ad90c5efc5d`;
archive, manifest, every file and published text chunks integrity verified by
controller download. Create00:57:30.491156→finish01:04:00.234829 UTC,390sec.
Current session charge1076/3600; all three Builds terminal/accounted/downloaded.
Independent explorer raw review agrees with the main review below.

## Exact physical identity

The unchanged console dead-code map keys use physical source-location identity.
The diagnostic adds a second map with the same equality, never removes a key
or marks a visit except where the original verifier does. Registration-order
IDs are run-local, not addresses stable across builds. Statement traversal and
original decision/exit remain unchanged. No `allow_dead_code` flag is passed.

| Physical ID | Post-AST root list | Traversal ordinal | Statement | Predecessor label | EXEC | DEAD |
| --- | --- | --- | --- | --- | --- | --- |
| 202 | 136 | 254 | Goto63 | 62 | twice | no |
| 203 | 138 | 256 | Goto63 | 3 | never | yes |
| 204 | 140 | 258 | Return | 63 | twice | no |

All print `verified/lib.rs(228,2)`; only203 causes the refusal. It maps to
original pre-AST root131, immediately after Label3. This is now observed,
not the previous textual-position candidate. Saved reader command:

```sh
python3 research/challenge-8/cloud-build/sort4-native-c1-bound/read-dead-node.py /tmp/native-c1-zst-diag-009-read/allprooflogs/cases/sort4-c1-current-recovery/supplied/native-c1-bound-positive/verification.log
```

Reports205 registered,204 visited physical locations; only203 dead and
unvisited. The reader's small synthetic cases distinguish equal printed
positions, reject a visited DEAD node, and do not pretend old logs identify IDs.

## Preserved source/MIR/AST and paths

Verified source SHA2567ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742;
original7c35a7e01915233308d113b081f26784c4ad5aaf6f7049dc209d126e3eb326a1.
Full normal MIR8e9adcccd136d3c1ee4dc1e7bd929c3cd60883f497178eab24da40f60754dee4;
readonlybde6d797d56e0e11e9837fc922f6def819c6931d1349f42c5b36d4570e2001aa.
Pre-AST18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5;
post-ASTc5fa49a0c3cf7fdaa03cb6ba22f3fd0fcd539e9fab743ee3d724716e47755a5e.
All six exactly match3521; diagnostics did not change the transformed program.
Both full-MIR exports/decodes and refinement pass before verifier.

Source145 `size_of::<T>() == 0` remains. MIR bb1 size call→bb2 `_7=(_8==0)`;
SwitchInt values[0],targets[4,3] gives false/nonzero→bb4, true/zero→bb3.
Both ASTs preserve If(_7,Goto3,Goto4), Label3 and its Goto63 edge. In symbolic
execution the zero assumption at log4101 is immediately abandoned; nonzero
continues at4103 to source151. Normal actual C1, direct comparator unwind and
len<8 early return reach complete native CURRENT posts/unit/free/leak checks.
The sizezero path is excluded; no full native theorem or generic ZST claim.

## Model localization, fresh callback-free controls

The same size guard with native `&mut[T]` and no callback passes VF0 on unchanged
frozen C4 console8d686fef29ae6fe5b6adb91a946ff9942aef682baf934b273cc61d71a625527b.
Adding only unused `&mut[MaybeUninit<T>]` gives VF1 `dead code(12,2)`.
Both paired normal/readonly exports, decodes and refinement pass; both ASTs
retain the guard. Positive/negative here are diagnostic comparisons, not std
C1 proof or generic layout admissibility evidence.

Native target log3594–3620 produces source array<T>; log3620–3645 produces
scratch array<MU<T>>. The scratch array_inv post introduces
`sizeof(MaybeUninit_type_info(T_typeid))` at3633, before executing body or calling
len(source144) or size_of(source145). Minimal with-MU log1429–1444 likewise
introduces MU size in entry array_inv. Stock size_of call requires only true,
returns sizeof(T), and has false unwind. No source-specific positive-size assume,
Freeze/sizedness restriction or CFG drop was found. The static frozen generic
struct-size axiom plus MU size equality explains the observed dependency; the
verbose4 log does not name its trigger event. A targeted entry-before-calls
assertion/verbose6 follow-up is recorded before dispatch in the session card.

## Controls and verdict

False-normal226 fails Cannot prove false after full normal cleanup assertions;
false-unwind mapped210 fails after recover_pair/join_four_owned_cells and full
native cleanup. Default-off refuses strict entry172. Source-hash, extra-body,
malformed-opt-in and mixed-env controls all refuse at their own admission gates.
All8 source pairs immutable and paired support/refinement pass. Diagnostic
patch only changes verify_expr/vfconsole logging; effective kernel37ed2550,
translator381e80eb and every effective RSSpec/proof std/refiner pin match.
Native C1 **INCOMPLETE**, native connected C4 **NOT_RUN**; old supplied raw C1→C4
PASS remains separate. No inverse/optional-T adapter, peer profile, strict-cut
draft, external caller/as_mut_ptr/guards/overflow/selector/C5/copy extension.
