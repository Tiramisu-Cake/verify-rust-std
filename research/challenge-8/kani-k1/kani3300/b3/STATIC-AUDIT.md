# KANI3300 B3 — static audit

- Task input: `TASK-KANI3300-B3.md` at research `423b4721c864ee02936e43f7b46c2a05e92a1383`; only B3, Cloud $0.
- Kani branch `fix/zst-union-codegen`, clean upstream start `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`. Both commits authored/committed as Tiramisu-Cake using per-command `-c`.
- Tests-only `dc590936c56556ecfb20fc714da06fcb13e884db`: paired 7-harness sources differ only by `// kani-flags: -Z uninit-checks`; expected summaries require 7 successes, 0 failures per mode.
- Shapes: `[(); 2]` arm with memset + typed read/write, original padded C/default-repr payload, align(8) ZST, union nested at offset 8, all-ZST union, nondeterministic array read/write/reference indexing.
- Union arms have offset zero by definition; `AtOffset.value` puts the containing union at offset 8, asserted explicitly, with prefix preservation controls.
- Typed-copy assertions read data fields only; byte-array unions cover all bytes. No padding reads or negative-property expectations. Initial byte stores use valid aligned allocated pointers; all-ZST zero-count store also uses an aligned object pointer.
- Fix `9dddcb1134f8a55ee3a4451df9513941ca3c8fc3`: Python/subprocess comparison confirms exact backend diff equality to `d760bad^..d760bad`. The entire `cprover_bindings` Git subtree is already identical at base and d760bad; no changes needed there.
- `UnionField.typ` remains logical (`field_typ`, `typ`, `lookup_field_type`); serialization and size use `padded_typ`. Only zero-width payload within the padded wrapper becomes registered unit. Nonzero payloads, padding bits and `padding == 0` branch remain unchanged.
- Source signatures checked: `Type::sizeof_in_bits(&SymbolTable) -> u64`; `codegen_ty_unit(&mut self) -> Type` registers an empty struct; `ensure_struct` supplies mutable context to its closure. Field/index lowering remains unchanged.
- Authorized rustfmt wrapper `--check --config-path rustfmt.toml` passed for both test sources and changed backend source. `git diff --check` passed for tests and cumulative base-to-fix diff.
- Clippy / `-D warnings`: source audit only; imports, field uses, mutable borrows, unsafe blocks and backend signatures inspected. No new production imports, unused locals, lint suppressions or unit comparisons/bindings.
- Review packet and spec were checked using `smallsort-session review check`: exact candidate/spec identities, `PACKET_VALID_NOT_REVIEWED`. Independent reviewer verdict is recorded separately in `REVIEW.md`.
- No local cargo/rustc/Kani/CBMC, builds, dispatch, Cloud, Actions, PR, issue, comments, Kani push, stash, raw logs/archives or credentials. Compilation, clippy execution, actual MIR, abort reproduction and verification outcomes remain NOT_RUN; proof credit NONE.
- Coordinator next gate: narrow fork CI at tests-only SHA and fix SHA in both modes; Unsupported/setup error is not evidence that abort is absent. This stage neither establishes upstream reproducibility nor successful runtime repair.
- Review revision: AllZst.unit was only initialized; added explicit reference projection in both modes. Folded into tests-only commit by local autosquash; initial review-packet retained, final identities in review-packet-final. No reset/stash or Kani publication.
