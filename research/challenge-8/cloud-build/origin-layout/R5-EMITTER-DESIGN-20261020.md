# R5 deferred-storage LocalAddrTaken emitter design

## Observed defect

The R4 source-exact controls report has five addressability positives with exporter, decoder, refiner, and verifier exit zero, while strict local-flag qualification remains inconclusive. The pinned `src/verifast.ml` declaration handler already defines `rocq_print_local_addr_taken` at lines 1069–1081 and uses it in ordinary declaration paths at 1093, 1098, and 1195. Its deferred Rust storage branch at 1130–1140 registers the local in the block and adds the MIR storage receipt to the environments, then returns without emitting the local flag. The missing event is therefore an emitter omission, not evidence that the flag is false.

## Narrow change

In that deferred branch, emit `rocq_print_local_addr_taken !address_taken` once after block registration and before `iter`. Reuse the existing `LocalAddrTaken(name, bool)` event and symex-step terminator. Keep all other tool bytes and line endings unchanged. The emitter writes this property at declaration handling time; a later `RustStorageLiveStmt` performs the actual storage allocation and records its path-local owner receipt, while `StorageDead` retires that binding. The bit reports the address-taken prepass result. It does not establish runtime execution of an address-taking expression, a live allocation, or physical ownership.

## Preserved guarantees and diagnostic controls

Keep existing source, stage, target-span, owner, allocation, and strict rejection gates. A deferred scalar whose source takes its address should emit exactly one true local flag and separately retain its `StorageLive` owner receipt. A deferred aggregate selected because of its type but never addressed should emit false, distinguishing false from missing. Ordinary true and false locals should retain their current events; no path should emit duplicates. A true flag before `StorageLive` or after `StorageDead` must not count as a live owner. Missing physical owner and unsupported operand controls remain strict. BeforeLive remains inconclusive unless its existing narrow runtime refusal is bound to the exact parser input, declaration/binder, target span, and stage; this emitter change does not supply that binding.

The change affects only diagnostics and classifier inputs. It adds no storage, alias, ownership, lifetime, layout, or proof rule, and cannot raise proof credit by itself. Preserve R4 artifacts and verdicts byte-for-byte; evaluate any new observations only on the new R5 profile identity.

## Independent review correction before Cloud acceptance

`LocalAddrTaken` also has executable meaning to the separately emitted Rocq
proof-tree consumer: pinned `bin/rust/rocq/SymbolicExecution.v:318–348` maps a
true event to its existing `PointsTo_` allocation/`LSPlace` declaration state.
Its `StorageLive/StorageDead` clauses488–489 currently ignore these operations
with an explicit SOUNDNESS BUG comment. Therefore “diagnostic only” describes
this campaign's intended use and native-verifier delta, not an inert event for
every downstream consumer. The new event changes the emitted tree interpreted
by that existing Rocq rule. No Rocq acceptance/proof is requested or inferred;
this campaign runs native VeriFast and parses the flags as bounded source
observations only. It cannot qualify Rocq storage liveness or establish live,
initialized physical ownership from a flag. Native path/owner checks and strict
classifiers remain necessary, profile accepted=false/proof_credit=false, and
BeforeLive remains non-qualifying. Rocq rules are unchanged; this session does
not repair or accept that consumer's existing storage-model limitation.
