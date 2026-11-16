# S1-07: офлайн-приёмка run 43923266772

**1/35 QUALIFIED (`ordinary-bridge`); 34 PENDING. Independent B1/B2/general proof credit NONE.**
Вход g0 `036c5c1a95`; исполненный control `b37f6f75c5b7b77e84297cd7104f9c0868502fd4`,
std `5be85699b8826e3286c0bf89efb9affefac0acb5`, tool `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Применены только решения координатора от 2026-11-16: exact location-only исключение
и semantic success binding. [POLICY-OPTIONS.md](POLICY-OPTIONS.md) содержит предложения;
они не применены к receipt, source или tool.

| Gate | Результат |
|---|---|
| Inventory и source verdicts | 14/14 групп, 35/35 строк, 9986/9986 exact stock/rich properties; 27 source SUCCESS, 8 предобъявленных FAILURE; потерянных/дублированных IDs, неизвестных статусов и посторонних failures нет. |
| Binary identity | 14/14 fixed required before/after snapshots MATCH; BEFORE_CHILD → AFTER_CHILD_SHUTDOWN, shutdown verified, complete, missing/errors пусты. Старые after не восстанавливались и не использовались. |
| Location-only | 18 exact tuples / 2 ID; null file/line, original display, class/description/SUCCESS и сами checks сохранены. Другие missing sites не допущены. |
| Native metadata | 322 embedded files перепроверены по bytes/SHA/JSON; 35/35 exact harness refs. Для 22 PFC подтверждены source span, attrs/target/symbol agreement и manual target-definition membership. Selected impl instance, checked_with/modifies-wrapper/clauses/property edges не экспортированы: полный gate остаётся. |
| Required success | 16/127 semantic bindings закрыты, 111 / 21 root остаются неоднозначными на общем macro callsite/placeholder. Exact candidate IDs и original descriptions сохранены; ordinals не угадывались. |
| Required SAT covers | 113/113 exact IDs/description/status со статическим source-order разбором после assumptions и соответствующих operations/actual call/post/frame. SAT не доказывает полноту domain или отсутствующую expansion provenance. |
| UNREACHABLE | 413 checks разобраны: 226 допустимых source/domain веток, 133 dependency applicability и 54 post-predicate origin UNKNOWN. Установленных mandatory-unreachable blockers нет; UNKNOWN не превращён в доказанную достижимость. Native harness metadata не содержит property origins. |
| Negative return covers | 2 activation return covers после предобъявленного sole failure разрешены только для negative observation с успешным same-run companion. Positive vacuity credit не дают; companion admission всё ещё PENDING. |
| Negatives / unsupported | 8/8 exact predeclared sole-failure oracles, named same-run source SUCCESS companions; 76 unsupported records связаны с exact SUCCESS guard того же harness, с pinned assert(false)→assume(false) semantics. |
| Source/tool/config | Source/variant/file SHA и before/after; tool tree; exact selectors/crate/argv, effective cfg, unwind/checks, отсутствие stubs/timeout/truncation сверены. Group exit отдельно от row verdict. |
| Replacement unions | 4 × N0..3 same-run members и covers сохранены, все 4 unions PENDING из-за member gates. Фиксированная fixture не устанавливает общий smallsort theorem. |

`ordinary-bridge` — обычный bridge/model observation с 12 exact SAT cover bindings
и своим inventory; у него нет PFC chain/remaining UNREACHABLE gates. QUALIFIED здесь
означает квалифицированное bounded source-reported наблюдение, не proof actual
smallsort, независимую B1/B2 верификацию или общий theorem.

Коды оставшихся gates (полные имена и точные данные — [ACCEPT.json](ACCEPT.json),
`rows[].remaining_gate_details`):

- **P** — FULL_QUALIFIED_TARGET_IMPL_CONTRACT_WRAPPER_BINDING: отсутствует selected-instance/contract/property chain.
- **S** — REQUIRED_SUCCESS_SEMANTIC_BINDING: неоднозначные сообщения → exact IDs.
- **U** — UNREACHABLE_APPLICABILITY_OR_ORIGIN_UNKNOWN: конкретные property roles/applicability не установлены.
- **C** — COMPANION_QUALIFICATION_PENDING: собственные gates указанного production companion ещё открыты.

Числа S/U ниже относятся только к открытым bindings/properties этой строки.

| Row | Итог | Gates | S | U | Companion при C |
|---|---|---|---:|---:|---|
| `activation-default` | PENDING | C, P, U | 0 | 15 | stable_default_activation-legal |
| `activation-override` | PENDING | C, P, U | 0 | 16 | stable_freeze_activation-legal |
| `stable_default_cell` | PENDING | P, S, U | 5 | 4 | — |
| `unstable_default_cell` | PENDING | P, S, U | 5 | 4 | — |
| `freeze_copy_u8_n0` | PENDING | P, S, U | 5 | 6 | — |
| `freeze_copy_u8_n1` | PENDING | P, S, U | 5 | 6 | — |
| `freeze_copy_u8_n2` | PENDING | P, S, U | 5 | 6 | — |
| `freeze_copy_u8_n3` | PENDING | P, S, U | 5 | 6 | — |
| `freeze_default_noncopy_n0` | PENDING | P, S, U | 5 | 6 | — |
| `freeze_default_noncopy_n1` | PENDING | P, S, U | 5 | 6 | — |
| `freeze_default_noncopy_n2` | PENDING | P, S, U | 5 | 5 | — |
| `freeze_default_noncopy_n3` | PENDING | P, S, U | 5 | 5 | — |
| `inactive_pairs_read_free` | PENDING | U | 0 | 12 | — |
| `activation_descending_rejected` | PENDING | C | 0 | 0 | inactive_pairs_read_free |
| `activation_effectful_rejected` | PENDING | C | 0 | 0 | inactive_pairs_read_free |
| `activation_unsupported_type_rejected` | PENDING | C | 0 | 0 | inactive_pairs_read_free |
| `snapshot_guards_companion` | PENDING | U | 0 | 2 | — |
| `invalid_snapshot_rejected` | PENDING | C, U | 0 | 11 | snapshot_guards_companion |
| `ordinary-bridge` | QUALIFIED | — | 0 | 0 | — |
| `stable_default_activation-legal` | PENDING | P, U | 0 | 4 | — |
| `stable_freeze_activation-legal` | PENDING | P, U | 0 | 5 | — |
| `corruption_companion` | PENDING | U | 0 | 1 | — |
| `order_corruption_rejected` | PENDING | C, U | 0 | 8 | corruption_companion |
| `count_corruption_rejected` | PENDING | C, U | 0 | 1 | corruption_companion |
| `model_u8_n0_3` | PENDING | S, U | 7 | 4 | — |
| `model_cell_n0_3` | PENDING | S, U | 7 | 4 | — |
| `model_noncopy_n0_3` | PENDING | S, U | 7 | 4 | — |
| `stable_freeze_u8_n0` | PENDING | P, S, U | 5 | 6 | — |
| `stable_freeze_u8_n1` | PENDING | P, S, U | 5 | 6 | — |
| `stable_freeze_u8_n2` | PENDING | P, S, U | 5 | 5 | — |
| `stable_freeze_u8_n3` | PENDING | P, S, U | 5 | 5 | — |
| `unstable_freeze_u8_n0` | PENDING | P, S, U | 5 | 6 | — |
| `unstable_freeze_u8_n1` | PENDING | P, S, U | 5 | 6 | — |
| `unstable_freeze_u8_n2` | PENDING | P, S, U | 5 | 6 | — |
| `unstable_freeze_u8_n3` | PENDING | P, S, U | 5 | 6 | — |

Для каждой U-записи сохранены exact ID/class/status, file/line/function, domain,
роль, target/wrapper relation и причина решения; для каждой P-строки — source и
native target-definition anchors, открытые рёбра. Нативная проекция target definition
не объявлена selected concrete specialization. Подробные варианты закрытия каждого
gate на stock-данных и правкой harness, с потерями гарантии, — [POLICY-OPTIONS.md](POLICY-OPTIONS.md).

Replay из любой cwd:

```sh
PYTHONDONTWRITEBYTECODE=1 python /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/s1-07/run-43923266772/accept/replay.py
```

По умолчанию пересчитывает receipt и сравнивает bytes; `--write` пишет только
`accept/ACCEPT.json`. [INPUTS.json](INPUTS.json) фиксирует hashes входов, включая
W11 packet и неизменённые baseline analyzers/location policy. Success navigation
берётся из S1-06 receipt, но exact inventory/status/source semantics проверяются
на S1-07; навигационный row/selector/messages set сверен с новым request.
`semantic.py` принимает navigation seed явно; `pfc.py` читает source binding и
same-group export нового run вместо отсутствующего legacy structured_preflight.
UNREACHABLE source/domain classifier использован неизменённым из pinned accept-v2.

Пересчитаны compact payload/projection/native hashes. SHA исходных ZIP здесь не
вычислялся заново: ZIP не сохранены, их integrity — историческая download attestation.
Compact archives не распаковывались этим replay; raw logs не читались. Native
invocation namespace не объявлен compiler-instance identity. Per-root process
exit/wall/RSS и отдельный compile exit остаются UNKNOWN и не взяты из group metrics.

Валидация: повторный replay совпал; 28/28 fail-closed checks PASS (inventory,
locations, negatives, snapshot phase/completion/shutdown/errors, native bytes/JSON/
ID pointers). Команды и hashes — [VALIDATION.json](VALIDATION.json).
Локальные cargo/rustc/Kani/CBMC, CI, push, публикации и ledger changes не выполнялись.
Исторические receipts/claims/ledgers не изменены.
