# H2b admission candidate: static self-review

This review covers only the local H2b source/ADT and test-tool MIR mutation
matrix prepared after O17. No new hosted result exists for these files.

The H2c patch is four added OCaml lines. It computes the end of the already
span-certified generic local method and requires only whitespace until the
unique, span-certified guard struct header. A declaration attribute such as
`#[repr(packed)]` or an inserted alias in that gap now rejects before the
selected template is enabled. The patch does not alter `gen_drop_contract`,
the H2a redirect, the normal/unwind post, the stock prelude, or ordinary
Drop. `git apply --check` passes against the H2b staged source. It has not
been compiled or verified. This check addresses a genuine layout-source
blind spot: the exported ADT has `isReprC` but no corresponding packed bit.

`capture-h2b-admission.py` reuses the O17 exact same-unit source fixture,
including its checked generic method, nominal owner, constructor, concrete
`u32` witness and ordinary Drop. It builds eight cases: one positive plus
three representation attributes, an extra field, a type alias for the field,
an extra guard ghost statement, and a casted call operand. Each original is
derived solely by stripping ghost annotations from its verified twin. Only
an exact fatal from the H2 gate before either checked body starts counts as
a source-admission rejection. Export/refinement or parser failure is
inconclusive; each variant preserves raw artifacts for inspection. Source
mutants **do not** count as typed-MIR gate controls.

`capture-h2b-mir-mutation.py` first reruns the unwrapped local positive.
Only if it fully proves does it create twelve direct typed-MIR mutants.
The real exporter supplies each canonical graph. A disposable shadow
exporter decodes, changes one selected field in the unique local guard
body and re-encodes. The independent NORMAL and readonly captures, decoder
and refinement use the real tool. Only the full verifier sees the shadow
exporter. The matrix targets receiver mutability, callee name/substitution,
move vs copy, call argument local/projection, destination, normal edge,
unwind edge, cleanup flag, ordered statement inventory and ghost raw text.
The classifier checks wrapper/console hashes, unchanged source, paired
original export/refinement, exact reproducible text mutation, distinct
canonical/mutated binaries, exact fatal reason and no body entry. A failed
encode, absent wrapper selection, different verifier failure, or source
setup failure is inconclusive. Mutated MIR is a *test-tool* profile and
must never be used as positive proof evidence.

The selected template's resource narrowness is still supported by the
O17 local positive and generic callee negatives: false normal/unwind,
retained initialized storage, retained `<T>.own`, wrong cell/target, and
duplicate returned cell. An adversarial generated-AST-post overlay is a
separate future test and is not simulated by changing a caller post.
`Element` does not occur in this generic guard model; no claim about extra
`Element` permissions in the actual helper follows from these cases.
Likewise, none of these local controls establishes the actual nested
`select_unpredictable::DropOnPanic<T>` DefPath. That requires its own
source/typed-MIR certificate and actual helper proof.

Hosted invocation (only after parent review and root dispatch) uses both
`--guard-root` and `--template-root` set to the exact checkout root, plus
`--tool-home`, `--schema`, `--compiler-sysroot`, `--evidence`, and
`--deadline-epoch`. The source runner accepts `--variants`; the MIR runner
accepts `--mutations`. Each refuses an existing evidence directory and
requires a GitHub-hosted Linux environment. The H2c patch must be applied
after the exact O17 H2a and H2b patches.
