# E-02 intake — primitive upstream reproduction established

Одна стадия `TASK-CH8-E02-INTAKE-W15.md`, вход g0
`32e297ea0c02a07612e2a1c6c99f7a3ae40e25ad`. Корректность, не security.

## Identities и проверка

[Run 43792979809](https://github.com/Tiramisu-Cake/kani/actions/runs/43792979809)
завершён success runner; это не proof acceptance. Sibling
`4a8f7e7b10742d913d2805e7303775a90fbb98d7` и control
`79baf66106a59e6ef9bcede8000fa893a5a8509d` имеют tree
`c07b5aded52231540eab49e2a173a57ed7b903c9` и sole parent U.

| Pin | Tool SHA | Artifact | SHA256 zip |
|---|---|---|---|
| U | `0aac16ef62da9e9d5645782d458593e5d78143ba` | 14193351491 | `b54934bad34088dd52ff774aed60db75fcb2274d4df4b09cae3c9406001d2dc4` |
| S | `14bc57fdb99960240c4944845a3d985c8af4dcf7` | 14193800295 | `cddfa0aa3488fcb423c7dcf9fccb9fd1eb59a7def4c6d57a7dea32db04780705` |

Zip получены read-only `gh api` в `/tmp/ch8-e02-intake-w15/`; digests совпали
с GitHub metadata. Читались только JSON metadata/receipts/exports; ни raw logs,
ни bounded tails не читались. Build receipts COMPLETE/exit0; before/after pins
совпали. Оба run COMPLETE, missing/incomplete receipts пусты. Все 24 invocations
OBSERVED, без timeout/signal/truncated export; NOT_RUN нет.

Проверены request SHA `792474d95b3e9fa67284991e68106c12dc021efcf17bfc4b175f9a6357570ee0`,
rows SHA `3406ce125fafa5d5b6a1c951339e6901f76716898c1cf88a5217bf9f6b23a6e6`,
fixture SHA относительно frozen CI-REQUEST, exact single-harness selection,
export `kani_commit`, dirty=false, ON/OFF uninit axis.
Общее окружение: Kani0.68.0; Rust1.101.0-nightly (7189d39d9 2026-10-22,
nightly-2026-10-23); CBMC6.11.0; x86_64-unknown-linux-gnu; resolved CaDiCaL;
600s/harness, jobs1, object-bits12, default checks без suppression/unwind override.
Solver binary version и actual MIR opt level независимо не связаны.

## Классификация против frozen rows.json / ORACLES.md

I=intended, X=unexpected, S=setup/unsupported. P/F — export properties/failed,
включая cover properties; C — satisfied/total covers; U — unreachable checks.
I=13, X=6, S=5. I означает соответствие oracle, не independent proof credit.

W = `Check that self->value is assignable`, class `assigns`,
`kani::mem_init::MemoryInitializationState::set::<1>.assigns.1`,
`library/kani_core/src/mem_init.rs:93` (U) / `:120` (S).
O = `Offset result address must equal original pointer address plus offset`,
class `safety_check`,
`kani::rustc_intrinsics::offset::<u8, *const u8, usize>.safety_check.2`,
export location `library/kani/src/lib.rs:63` (macro expansion);
model definition `library/kani_core/src/models.rs:156–161`.
A = exact `e_s_false_value.assertion.2`, `assertion failed: value == value.wrapping_add(1)`,
class assertion, fixture:18.
M = `std::cmp::impls::<impl std::cmp::Ord for usize>::max.unsupported_construct.1`,
unsupported uninit intrinsic `integer_max`, pinned core `cmp.rs:2388`.

| Pin | Root | Axis | Verdict P/F | C | U | Class | Observation |
|---|---|---|---|---|---|---|---|
| U | `e_h_issue_mre` | OFF | SUCCESS 69/0 | 1/1 | 0 | I | SUCCESS oracle |
| U | `e_h_issue_mre` | ON | FAILURE 79/1 | 0/1 | 14 | S | union/raw-pointer unsupported at fixture:8; no assigns reproduction |
| U | `e_h_primitive_no_loop` | OFF | SUCCESS 14/0 | 1/1 | 0 | I | SUCCESS oracle |
| U | `e_h_primitive_no_loop` | ON | SUCCESS 33/0 | 1/1 | 0 | I | SUCCESS oracle |
| U | `e_h_primitive_no_write` | OFF | SUCCESS 70/0 | 1/1 | 0 | I | SUCCESS oracle |
| U | `e_h_primitive_no_write` | ON | SUCCESS 94/0 | 1/1 | 0 | I | SUCCESS oracle |
| U | `e_h_primitive_write` | OFF | SUCCESS 71/0 | 1/1 | 0 | I | SUCCESS oracle |
| U | `e_h_primitive_write` | ON | FAILURE 95/1 | 1/1 | 0 | X | W only |
| U | `e_s_false_value` | OFF | FAILURE 70/2 | 3/3 | 3 | X | O + A; contaminated negative |
| U | `e_s_false_value` | ON | FAILURE 117/1 | 0/3 | 24 | S | M; covers unreachable |
| U | `e_s_unbounded_slice` | OFF | FAILURE 69/1 | 3/3 | 3 | X | O; positive fails |
| U | `e_s_unbounded_slice` | ON | FAILURE 116/1 | 0/3 | 23 | S | M; covers unreachable |
| S | `e_h_issue_mre` | OFF | SUCCESS 69/0 | 1/1 | 0 | I | SUCCESS oracle |
| S | `e_h_issue_mre` | ON | FAILURE 224/2 | 1/1 | 8 | I | 2×W: set::<1> and set::<8>, diagnostic oracle |
| S | `e_h_primitive_no_loop` | OFF | SUCCESS 14/0 | 1/1 | 0 | I | SUCCESS oracle |
| S | `e_h_primitive_no_loop` | ON | SUCCESS 46/0 | 1/1 | 0 | I | SUCCESS oracle |
| S | `e_h_primitive_no_write` | OFF | SUCCESS 70/0 | 1/1 | 0 | I | SUCCESS oracle |
| S | `e_h_primitive_no_write` | ON | SUCCESS 110/0 | 1/1 | 0 | I | SUCCESS oracle |
| S | `e_h_primitive_write` | OFF | SUCCESS 71/0 | 1/1 | 0 | I | SUCCESS oracle |
| S | `e_h_primitive_write` | ON | FAILURE 115/1 | 1/1 | 0 | X | W only |
| S | `e_s_false_value` | OFF | FAILURE 70/2 | 3/3 | 3 | X | O + A; contaminated negative |
| S | `e_s_false_value` | ON | FAILURE 179/1 | 0/3 | 24 | S | M; covers unreachable |
| S | `e_s_unbounded_slice` | OFF | FAILURE 69/1 | 3/3 | 3 | X | O; positive fails |
| S | `e_s_unbounded_slice` | ON | FAILURE 177/1 | 0/3 | 23 | S | M; covers unreachable |

Все failed properties перечислены выше кодами W/O/A/M и union blocker.
SEL1 issue-MRE ON имеет 2 assigns failures на `:120`, 213 успешных checks,
8 unreachable checks и 1 satisfied cover (224 properties). Его diagnostic oracle
разрешает именно такое последующее unreachable inventory; это не positive PASS.
Upstream issue-MRE ON: 63 успешных checks, один union failure, 14 unreachable
checks и unreachable body cover. Он не подтверждает upstream shadow-assigns.

Runner сохраняет UNBOUND_FAILURE/UNKNOWN для W и O/O+A;
COVER_INVENTORY_MISMATCH/UNKNOWN для upstream issue-MRE ON и E-S ON;
NAMED_FAILURE_OBSERVATION для SEL1 issue-MRE ON. Эти исходные статусы не
переписывались. У E-S OFF все 3 covers satisfied, но дополнительно есть
3 unreachable checks и status-SUCCESS unsupported inventory: caller_location,
rust_begin_unwind и same_allocation/unallocated-memory. Это не дополнительные
достигнутые failures и не основание принимать storage proof. Во всех exports
warnings пусты. Covers сопоставлены с frozen single-root sources по порядку;
export не содержит их descriptions и не устанавливает полное GOTO/body binding.

## Чистый primitive repro и причина

`fixtures/shadow_write_u8_candidate.rs`, SHA256
`163650e4ded1bed5fabc2ecbe35faca04d5774fedec7c0b43566fffca5eb5962`,
содержит только initialized u8, raw pointer, counter, explicit loop contract и
write/read/assertion. Нет union/MaybeUninit, slice allocation, quantifier predicate,
проектных helpers, stub/assume или новой shadow модели. Это проверенная минимальная
primitive reduction относительно прежних confounders, не заявление о кратчайшем
возможном синтаксисе. Удаление оставшихся attrs/cover отдельно не запускалось.

U ON: 94 checks = 93 success + единственный W, 1 satisfied return cover,
без unreachable/unsupported/warnings; OFF:70 successful checks + cover.
No-write ON/OFF и no-loop ON/OFF полностью проходят на U и S.
No-write не утверждает равенство havoced payload17 и не является uninit negative.
Контроли локализуют взаимодействие raw-write instrumentation с loop frame.

На upstream `uninit_visitor.rs:132–156` в
`kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/`
добавляет Set(true) после raw dereference store;
`library/kani_core/src/mem_init.rs:218–232` вызывает `MEM_INIT_STATE.set`,
а `:93` изменяет shadow value. `codegen/statement.rs:260–274` сохраняет
пользовательские loop targets; `overrides/hooks.rs:884–904` добавляет generated
locals и выводит assigns без shadow-static allowance. Для function modifies
`codegen/contract.rs:142–170,230` такая allowance уже есть (все три пути под
`kani-compiler/src/codegen_cprover_gotoc/`). Это source-based объяснение,
согласующееся с export и controls; transformed GOTO/CBMC причинная цепочка
не исследована. Нельзя считать простое blanket shadow havoc корректным fix.

[ISSUE-DRAFT.md](ISSUE-DRAFT.md) использует этот выполненный код: удалены только
две устаревшие строки комментариев про E-02/NOT_RUN. Остальные строки, включая
имя harness, attrs и cover, сохранены; code block статически сверен.

## E-S: что ломается и следующий шаг

Bounds в fixture корректны относительно предоставленного slice:
positive `.add(index)` на :13, false на :16; `len != 0`, `index < len`;
для u8 `len <= isize::MAX` задаёт сам generator. Генератор в
`library/kani/src/arbitrary.rs:205–218` выделяет `len.max(1)` bytes и строит
slice длины len; CAP нет. Namespace теперь корректен, все строки дали export.

OFF ломается конкретно равенство full-width адреса после pointer addition,
не `index < len`, не loop assigns и не intended false-value assertion.
`models.rs:127–161` прямо документирует ограничение CBMC pointer encoding:
при 64-bit pointers и object-bits12 для offset остаётся 52 бита, а модель
разрешает длины вплоть до 2^63−1. Защитный check не даёт молча принять
алиасинг после wrap/invalid-pointer lowering. Kani allocator shim
`library/kani/kani_lib.c:41–47` передаёт size в malloc без object-bits bound.
Следовательно, исходный fixture не содержит выявленной ошибки in-bounds
арифметики; результаты согласуются с ограничением Kani/CBMC при таком storage.
Но успешность giant malloc, конкретные len/index и точный wrap в этом
counterexample НЕ установлены: exports содержат только trace_available=true,
без witness values. Детали CBMC allocator требуют отдельной проверки.

ON имеет независимый ранний blocker: `len.max(1)` в генераторе попадает в
unsupported uninit `integer_max`; все 3 covers unreachable. Он не является
доказательством провала или успеха offset guard с uninit-checks.

Следующий отдельный шаг: получить структурированный witness для O
(len/index/исходный и итоговый адрес), связать allocation size с object bounds;
если текущий export его не предоставляет, подготовить отдельную диагностическую
строку OFF и её небольшой matched control для границы 2^52. Для ON исследовать
эквивалентное `if len == 0 { 1 } else { len }` отдельно от offset проблемы.
Ни CAP, ни отключение offset check, ни молчаливое сужение storage domain
не закрывают исходный E-S oracle. Новых запусков в этой стадии нет.

## Read-only duplicate check

2026-11-16 через `gh`: прочитан model-checking/kani#5175 (стиль draft),
затем `gh search issues --repo model-checking/kani --limit 30 --json number,title,url,state`
с queries `"loop_modifies" "uninit-checks"`, `"loop" "initialization"`,
`"loop" "assignable"`; дополнительно limit40 queries `"loop" "uninit"`,
`"self->value"`, `"shadow" "assigns"`. Поиск включает open/closed issues.
Первый и shadow/assigns запросы пусты; self->value даёт нерелевантную токенизацию.
Read-only прочитаны тела [#4906](https://github.com/model-checking/kani/issues/4906)
(temporaries) и [#4790](https://github.com/model-checking/kani/issues/4790)
(memcmp locals). Другие loop results: #4940, #4949, #4982, #5110, #4584,
#4929, #4159, #3867; они не являются найденным точным shadow/uninit дубликатом.
Точного совпадения не найдено в этих запросах; абсолютное отсутствие дубликата
поиском не доказывается. Issue/comment не создавались.

## Координаты export / SHA256

Archive/member identities ниже фиксируют прочитанные JSON, не AST/MIR binding.
Для каждой строки member = `rows/<Root>/<axis lowercase>/export.json`.

| Pin | Root | Axis | SHA256 export |
|---|---|---|---|
| U | `e_h_issue_mre` | OFF | `e3e74a59e4eebaad8722cd62caf8b864dba5698e4732f98c6b8810871b34ca3d` |
| U | `e_h_issue_mre` | ON | `c337c6a17fbf06d6b8bc8b7001c9138013c98dccc102994ee6829076ae27496c` |
| U | `e_h_primitive_no_loop` | OFF | `e8b068cced62d519565143942c79da13259ae98635e56d06188d93db4c3dc096` |
| U | `e_h_primitive_no_loop` | ON | `31446091f7b9e31f70a2869bdc3b564625e2daf0caddb3099e08d2c923caabaa` |
| U | `e_h_primitive_no_write` | OFF | `04b091807d9387947d67de8ff9f78dae8acac0eba1ea4ab40944e7767d5ea112` |
| U | `e_h_primitive_no_write` | ON | `53f2736bd57f7806af933ccb776576a2747ef8fc7d36ad92817d01b5afbd0122` |
| U | `e_h_primitive_write` | OFF | `7ffabef0180bf26ae5235f063f8796cd3d2d54e978a03a95e7d4921a5cc0dd00` |
| U | `e_h_primitive_write` | ON | `2c9bd1dcf5d388ed820e9fa1d9f9ae9b69f5553d58906caa357a87294f03882d` |
| U | `e_s_false_value` | OFF | `e34440e911eecac7e716316ebf64da6da9ff4388aa7838bd15e43bb40c0973e3` |
| U | `e_s_false_value` | ON | `68351d5d7f6c4939ee9f99d597b6154f20bf1ed72894ce4976e7386637ceac1c` |
| U | `e_s_unbounded_slice` | OFF | `023768f6c0a753a3682a7cec67cb92e9656724a1677d0c04dec0a13e84e4c32c` |
| U | `e_s_unbounded_slice` | ON | `bee9ddaddd1d60f2cde10bf3a1cd5cd9e0c8762818929cacd2e7093db6f464ef` |
| S | `e_h_issue_mre` | OFF | `c21b5646cd8d7702bdcf12e3ba520e4744c856b3c7d7150aa266dfbb411ff955` |
| S | `e_h_issue_mre` | ON | `ed6d3b1312b2cac82a20046bcb153c2f8485caff61b4a6af41f81fb5c196cf00` |
| S | `e_h_primitive_no_loop` | OFF | `16315d347884e907f0bd6f0ed5f558d599abe8ace439199ca2c53018a4b4293d` |
| S | `e_h_primitive_no_loop` | ON | `9870421a36bb6a565cf832ed20d576fe25665673ad514f44574c14825543c377` |
| S | `e_h_primitive_no_write` | OFF | `1ab9cb3842da3167624ca6ae9e062c78f94f3d2c64d4dd981a7f961df9bfc485` |
| S | `e_h_primitive_no_write` | ON | `c3dcd70e22eea58b4cf324548cd27e3310d45b7e36c35350d01fc28c92fe9604` |
| S | `e_h_primitive_write` | OFF | `7b348d20d9c25f4f977c35b32bde8aede565e099b9b36ee0ffe2d32a39c559df` |
| S | `e_h_primitive_write` | ON | `e25aeb7fafbca9c8819b5757ae9aa7c9792a32817894356056bfabc5dddddd3c` |
| S | `e_s_false_value` | OFF | `4ea082034e22cc9af5ef0685ec53cc6789781562bdbd3f952d77afef2cafb8c5` |
| S | `e_s_false_value` | ON | `1218ad6190d25af093d6a3deba3f8530ae6fe1016e0ad394782f15dfb6ba9dd7` |
| S | `e_s_unbounded_slice` | OFF | `26155dbb42078aceb715d638481830dcbd8df12b60ccb8a1c31c2a52d2d9ffd9` |
| S | `e_s_unbounded_slice` | ON | `f9dbb606a5656eb8b52d4af110494ce0284caa0ef1808def183aea90d940b76c` |

## Граница результата

Intake завершён; issue draft готов, E-S OPEN. Runtime source observations
не дают независимого B1/B2 credit; proof credit NONE, общие obligations E/Q/H
и historical STOP не сняты. Никаких push/CI/публикаций/ledger или локальных
cargo/rustc/Kani/CBMC. Изменения только в трёх документах этого run directory.
