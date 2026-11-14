# C2-S2 — controls (execution NOT_RUN)

New fixtures are in `tests/expected/uninit/immutable-descriptor-coalescing/`. Each file has one harness, `--edition 2021 -D warnings`, `-Z uninit-checks --output-format=regular`, three own assertion SUCCESS pairs, `** 0 of`, final SUCCESSFUL and one-harness/zero-failure summary. Expected output is an authored oracle, not an observed result. No host/toolchain/std-line/full-inventory golden is added.

| File stem / harness | Source use order | Read form | Required result |
| --- | --- | --- | --- |
| direct-first / direct_first | direct &5, then T[0] | Ordinary | SUCCESS, zero failed properties |
| nested-first / nested_first | T[0], then direct &5 | Ordinary | SUCCESS, zero failed properties |
| direct-first-volatile / direct_first_volatile | direct, then nested | read_volatile on existing refs | Same |
| nested-first-volatile / nested_first_volatile | nested, then direct | read_volatile on existing refs | Same |

All retain `static T: [&u8; 1] = [&5]`. Own assertions require direct value=5, nested value=5 and equality; none assert pointer identity. Volatile companions retain byte observations without casts or new assumptions. Source use order is not claimed to force finalize's HashMap iteration order.

Before proof credit, bind both distinct AllocId keys, their exact Allocation/mask, frozen facts and common emitted symbol in each actual model; confirm the reads/checks remain. If lowering folds the case away, uses one key, or produces no differing qualifications, report NONDISCRIMINATING. Current real-source binding: UNKNOWN; no fatal observed on baseline. Volatile fixture success alone also cannot prove mixed qualification.

New unit tests in `immutable_allocations.rs` (all NOT_RUN):

- `compatible_aliases_combine_qualification_in_either_order`: false→true, true→false, true→true, false→false; duplicate each registration; one symbol, exact Some(0)/None bytes/mask and expected admission.
- `incompatible_storage_never_overwrites_or_combines_qualification`: byte value, Option+mask, extent, isolated Option bytes, isolated mask, layout, mutability, alignment; four qualification pairs. Admitted mismatch yields Err(previous), otherwise inherited Ok; stored descriptor is identical afterwards. Some deliberately inconsistent synthetic descriptors isolate fields; they are not source/provenance examples.
- `unqualified_conflict_keeps_existing_policy`: mismatching holes retained without qualification or replacement.
- `compatible_mutable_aliases_remain_unadmitted`: frozen evidence can accumulate, mutability still excludes seeding.

All five existing unit tests remain: zero/hole distinction, duplicate reuse/genuine conflict, mutable/unqualified non-admission, reset edge/completion preservation and empty extent. Relocation equality/non-admission is checked by source review and existing controls requested below, not a new synthetic provenance test.

Reuse unchanged controls:

| Selector / group | Required observations |
| --- | --- |
| expected/uninit/immutable-masks | initialized zeros and empty legal; zero-byte-hole and copy-hole remain intended failures |
| expected/uninit/mixed-promoted-allocations | all stack/promoted orderings and legal/hole companions preserve results |
| expected/uninit/contract-immutable-masks | ordinary singleton legal; left/right ensures holes retain intended failures |
| expected/uninit/part1-edges/immutable-static-{legal,hole} | named-static qualification and hole distinctions preserved |
| expected/uninit/part1-edges/immutable-relocation-{legal,hole} | no new unconditional seed for relocated origin; existing outcomes preserved |
| expected/uninit/part1-edges/immutable-subrange-{legal,hole} | existing whole-object/subrange boundary preserved |
| kani/{Uninit,Quantifiers,TailCall}; expected/{uninit,quantifier-capture,arbitrary} | accepted Quick coverage on candidate |
| ui/{quantifier-safety-checks,explicit-tail-calls*}; script-based-pre/{mem-init-reinstrumentation,autoharness_explicit_tail_call} | accepted diagnostics/script checks |
| json-handler/uninit-contract-{oracles,mode-boundaries} | retain semantic and mode oracles |
| json-handler/uninit-part1-composition | retain actual failure/exit, compare within narrowly accepted S1/S5 debt |

`baseline-controls.patch` adds exactly the four new unit tests and eight new fixture/oracle files to baseline 69b13711e. Baseline production bytes before cfg(test) are unchanged; patch applies to a temporary index and fixture blobs equal candidate. Overlay tree `208e5f19457ac11789bb92cb06d8203bf9aa7489`. This is a source identity check only. Baseline and candidate unit/targeted runs: NOT_RUN. Candidate expected=PASS and old-register qualification conflict are predictions, not execution evidence.

## Follow-up after coordinator CI

The four original controls PASS on both candidate f96 and old baseline69b, so they are NONDISCRIMINATING (coordinator SUMMARY run43603876627/baseline43603880264). Their source and expected blobs are unchanged. Unit matrix9/0 is reported on f96; baseline unit results are not supplied.

Added aggregate-constant-initializer and const-fn-initializer, one harness each, volatile direct/nested reads, the same three own SUCCESS assertions, zero-failure summary and final SUCCESSFUL oracle. Both new cases: NOT_RUN on baseline and candidate. They are source candidates, not established mixed-qualification discriminators. See format-coalescing-followup/{TRACE,CI-REQUEST,RESULT}.md and its test-only baseline patch for exact mapping criteria and limitations.
