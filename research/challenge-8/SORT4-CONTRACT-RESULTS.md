# Sort4 contract diagnostics and architecture closeout

Phase [SORT4-CONTRACT-PHASE](SORT4-CONTRACT-PHASE.md), approved by owner commit
`54485d632bfca9d69fee853bd6aa30bc330647c9`. Target actual
`sort4_stable<T,F>` in [smallsort.rs](../../library/core/src/slice/sort/shared/smallsort.rs:612),
Git blob `e555fce440872898e47fd5114f32eb15401d07df`, unchanged.
**CLOSED on2026-10-06; stop at the owner architecture decision below.**

## Diagnostic evidence

First run [37464581019](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37464581019),
source `a082e0cf0c45d8bccf4c7df46eff9b84278a9f67`, FAILURE. The unchanged
values control verifies0/267failed and12/12covers. Coincident buffers reject ONLY
`ptr::copy_nonoverlapping::<i32>.precondition_instance.1`, description
`memcpy src/dst overlap`, location `library/core/src/ptr/mod.rs:555:14`.
Ascending source0→dst0 is the first UB boundary; no post-UB output claim.

Shifted/witness cases initially fail unrelated `memcmp.unwind.0` at builtin
memcmp:25; their byte-wise array equality needs more than unwind6. Strict
classification rejects both, so this run establishes no shifted multiset/output
result. A proof-only4/5-element equality helper replaces byte equality with the
same value conditions; all original assertions, unwind6 and checks remain.
That new source requires a new run, not a rerun of the old SHA.

Retry [37465676476](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37465676476),
source `6ff3d9f8f559555c17f722f500a1c7de16d9fe7d`, same selection
`sort4_contract_diagnostics`/90min, FAILURE only at diagnostic-label acceptance.
Values and coincident cases accepted; shifted1/170failed only at the explicit
multiset assertion; witness0/130failed and1/1cover establishes zero output.
All other shifted default checks pass/unreachable. Kani gave the Rust assert!
a formatted-panic placeholder message, so the classifier refused acceptance.
The same condition is now kani::assert with the predeclared static string;
classifier location audit updated to that exact spelling. No generic placeholder
is accepted.

Final run [37466906281](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37466906281),
source `7f96aa2f3262cf209ff3dcafd06e355e5590885b`, **SUCCESS**, same90min
selection/default-check profile, Kani0.67.0 pin
`152c6a8c875d9886a67e229247b4826d6105ccfd`, Rust nightly-2026-02-05,
CBMC6.10.0. Full hosted log and all artifacts inspected.

| Isolated actual-body case | Raw exit / failed checks / covers | Accepted evidence |
| --- | --- | --- |
| Unchanged values positive | 0 / 0 of267 / 12 of12 | Sorted exact original i32 multiset and unchanged source, all12 covers |
| Coincident [0,1,2,3], dst=src | 1 / 1 of86 / none | ONLY check54 copy_nonoverlapping::<i32>.precondition_instance.1, memcpy src/dst overlap, ptr/mod.rs555:14 |
| Shifted [0,4)→[1,5) in [0,1,2,3,4] | 1 / 1 of170 / none | ONLY check76 negative_shifted_original_multiset.assertion.15, original multiset preserved, injected smallsort.rs1192:9; all memory/trace/sorted checks pass or unreachable |
| Separate shifted output witness | 0 / 0 of130 / 1 of1 | Original snapshot[0,1,2,3], backing[0,0,0,0,0], hence destination[0,0,0,0] |

For the concrete ascending shifted route, all five comparisons complete before
writes and return false. Selected source indices0,1,2,3 are pointers, not
snapshots of values. The writes0→1,1→2,2→3,3→4 each have distinct one-cell
regions, yet propagate zero into the next unread source. Sortedness passes;
count(0) becomes4 instead of1, and1/2/3 disappear. This observed multiset loss
is **not a demonstrated UB** in this initialized i32/default-check domain.
The coincident first0→0 copy violates non-overlap; no post-UB state is asserted.
These cases do not classify all overlap mappings or generic validity.

All cases contain22 default checks attributed directly to actual sort4
(reference alignment/validity and index arithmetic). Unsupported-operation
guards all SUCCESS, no UNDETERMINED checks or unwinding failures in final run.
The usual4 unreachable arithmetic/format helpers remain; shifted has a fifth
unreachable same_multiset i+=1 overflow check because it returns false on its
first key0. No target post/cover/resource was deleted. The classifier accepts
all4 actual cases and rejects44 malformed/unrelated/wrong-exit/location/status
variants in hosted tests. Raw negative exit1 remains preserved; green suite
means intended outcomes matched, not that overlapping inputs satisfy the target.

Independent byte audit of downloaded injected source equals git-show(finalSHA,
std)+unchanged values/stability module+diagnostic module exactly. Source audit
PASS; no runtime change, assumed comparator stub, source rewrite or new verifier
profile. Stability was not cold-rerun; its prior actual-body theorem remains.
No explicit uninit/valid-value/extra-pointer profile, VeriFast/refinement/leak
proof, non-Copy/non-Freeze/ZST or comparator-panic theorem is claimed here.

Cost: suite363.05s/RSS1811800KiB; case wall times253.57/35.90/36.46/36.73s;
CBMC9.252569/.30528224/.95132405/.58405024s (11.09322553s total). Remaining
suite351.96s is tool setup/build/std compilation/orchestration. Job12:56:09–
13:06:10UTC601s; common runner preparation227s separately. All three jobs together
1424s; no90min bottleneck. Corrected sources always received new exact-SHA runs.
Workflow-only exposure: researchcdf1b98, main0b54bf8f1f2fc4f7d1a7acef4d428ffe34cd7447.


Historical artifact SHA256 digests (raw files stay outside Git):

| Run | environment.txt | verification.log |
| --- | --- | --- |
| 37464581019 | `9233cbeb799188b1b17f81751cc496a8a139ca816091fa664902fe9c8eb0d3c4` | `f3ce2458ddb15245b0dc8e1965fbc2748fe0f3b534b73801a27326aecf1b0b30` |
| 37465676476 | `b402e79750ed0e16086baecf308bb88040a5c3ad68697b374c7c5fb86a39a762` | `07f6ae7f136e9eb2f0d67b2e099c24129f1c65bc32238697a7262d08e91b0f56` |

## Exact final inputs and artifacts

SHA256 inputs (source SHA above also identifies every file):

| Input | SHA256 |
| --- | --- |
| library/core/src/slice/sort/shared/smallsort.rs | `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959` |
| research/challenge-8/sort4.rs | `dc33133c822833f2b881b0f11e1c595a5873c43c08cd4e0d50b4de71beb3c477` |
| research/challenge-8/sort4-contract-diagnostics.rs | `423a637db18e1f3094f60dc829432ad2052e52f8938212f830e7c9bfc7cf9345` |
| research/challenge-8/classify-sort4-contract.py | `7615de58c3b9418fcf2ddbe0f6d5466bf48bc34a4c258d0010cc471d4f0f5fe1` |
| research/challenge-8/run-sort4-contract.sh | `fba49f7f774c908065ad597696ee667f4b273268875c115258c3b2ab6c17443b` |
| research/challenge-8/test-sort4-contract-classifier.py | `eb856d58949d1d5e5ec5cc92a4f8e5616ae757a20bac35e3c97d73455b4d7d11` |
| scripts/run-kani.sh | `059abb4036e352b72051bd59888849a35322d89b6718190415cde71f527a4d02` |
| tool_config/kani-version.toml | `b2c99f41fc652d96a37e52c1701182ebd92f5b782a734b9a4a06b3e92e4826fd` |
| rust-toolchain.toml | `20180f8307182dce745e0304bcbee56ee2a85fc7608392b2c8b266dfe533c78c` |

Kani script SHA256 `28a81c48fd72627ed2449993730636bc830abeffeaea4d85d9297b2ec4393af2`;
Kani driver `9ae446cbe90b2eb9a394506d83e26624de675c3fd0eb80f5674ff4fd2d61d842`;
CBMC `05f93fd2f2ba6247b345f2bfb3d74c38402966515c65ff69f94adf7a674593f0`.
Artifact11415738147, zip digest
`8cfd3a37812afb6b2ceda7358c4596dd5cde0af56b1c82a16df3b6cc6fddc5c6`.
Generated source/logs/build output stay outside Git; raw-file hashes:

| Artifact file | SHA256 |
| --- | --- |
| environment.txt | `2c8367c9b9edde97faa78b05d4dc0cac75bc21f3c16368be3f0fd9038432f05a` |
| verification.log | `22240a9b32d8eba19a74d35861cf01464e5977c8514f792f4b536610265ada63` |
| smallsort-with-sort4-contract.rs | `851ca4918a01e26577f50c1b2f11d51ce9d50af6f55c33fac2977030b8271431` |
| prove_sort4_values.log | `887e9b6e252640d1fbe1f596badb0b3ab835fb87b4b0c64621a968c07c288b51` |
| negative_coincident_copy_overlap.log | `38e9fba463dc1bba84848c945e85502ac530eed01a8e18fa5a807a47a69394f9` |
| negative_shifted_original_multiset.log | `0ab45f6bb51148a3cedb1686c42624bda8278d11f478ee0381d9aa02d222ef95` |
| prove_shifted_output_witness.log | `bc5342c4b1842fc2c81bd50e4b3bc307319651c7461aa17201710c3c557f6b13` |
| sort4-contract-summary.json | `7ee97c5320466ea500f9d8be42f1f6831cde2de3408236ca833ff3a21d07faa2` |
| classifier-regression.txt | `bd2a5fa3c86913688632cf8071998970cf99a98a1bb3ec2df8b552662bb60b2e` |

## Contract delta and established boundaries

[Full research contract](SORT4-CONTRACT.md) now gives separate local copy safety,
sequence preservation and original-element sorting premises, sufficient range
separation, provenance/alignment/initialization, optional uninitialized scratch,
prior destination resource disposition, ZST/padding, non-Copy/non-Freeze effects,
and explicit full normal and five direct-panic resource posts.

Physical initialized copies are not independent owners. The proposed retained-
originals post returns one current source ownership sequence and initialized
nondroppable scratch Shadow. A move-to-destination interpretation requires an
explicit transport and later caller recovery; no unproved ownership bridge is
assumed. Current F/interior/frame effects survive normal return and panic.
Every comparator panic precedes sort4's first destination write; it does not
roll back prior callback effects or prior other sort4 invocations.

The actual caller audit maps direct sort4 to separated v/scratch half-ranges at
len>=8 and nested sort8 to distinct source/output/temp regions at len>=16,
bounded by scratch.len>=len+16. Caller FreezeMarker is not a sort4 restriction
and does not imply Copy. MaybeUninit scratch is not dropped as T. Later scratch
access, insertion/merge and restoration remain separate unproved composition.

The short SAFETY comment omits local non-overlap and ownership policy. Full
range separation is sufficient; these examples do not prove every overlap
unsafe. Contract clarification needs acceptance before claiming the unrestricted
public target. No std comment/runtime/signature was edited; existing functional
values and tagged stability proofs remain unchanged. No new generic theorem,
all-five-panic proof or four-UB-category coverage is established here.

## One selected architecture and next owner decision

[Architecture decision](SORT4-SAFETY-DECISION.md) recommends a bounded prerequisite
experiment: source-defined normal/direct-Continue recovery continuations with
a checked ordinary helper, using narrowly reviewed tuple2/HRTB/strict-lifetime
capabilities. Existing strict-cut changes both translator and kernel; its partial
debt unwind post is not full ownership recovery. A new exceptional routing
capability is required and is NOT IMPLEMENTED/AUTHORIZED here.

Two additional whole-sort4 dependencies are explicitly unresolved: pinned
VeriFast copy summary requires initialized typed destination, whereas actual
scratch may be uninitialized; exact hint::select_unpredictable pointer helper/
intrinsic semantics have no established applicable callee proof. Also open:
repeated sharing across five comparisons, ZST/padding/provenance, and generic
scratch access/ownership transport. Existing MD/Drop patches are not imported.

Next owner decision: authorize or reject the one-callback full-normal/full-panic
recovery experiment and its explicit trust/regression gate; separately accept or
clarify the separated-range, single-owner research contract. Whole generic
sort4 remains NO-GO until copying/selection and five-call recovery dependencies
are resolved. No new VeriFast run/build/apply/edit, tool-semantic implementation,
later sorting phase or external publication is performed in this phase.
