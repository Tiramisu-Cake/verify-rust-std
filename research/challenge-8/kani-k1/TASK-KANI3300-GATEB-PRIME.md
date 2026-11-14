# KANI3300 Gate B′ — closure comparator replay on immutable C1

2026-11-14. Worker15, одна стадия подготовки. Это верификация корректности, не security-работа.
Подготовлено для выдачи координатором; этим файлом стадия не запускается. Локальные cargo/rustc/Kani/CBMC/Miri/builds
запрещены. Cloud $0; fork CI, push/dispatch и review выполняет координатор. Без PR/issue/публикаций.

## Вход и задача

Владелец принял R4 §5: граница A, Gate B′≤3 строки, C2 отдельно. Прочитать аудит F1 и ответ1,
`kani3300/final-gate/gateb-run4/{RESULT,DIAGNOSTICS}.md`, текущие REPLAY-REQUEST/ROOT-MAP и replay scripts.
Kani **неизменный C1** `1658f4cadfa83139e41180ce3865e23f79d889aa`, tree `bfb5eb9db13ffb91ec4585b7c7ef41ddfe0008fb`.
Std snapshot `70ba5befc617627073738e26cb1466bd4fb76e41`, original library tree `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`.
Действующая рабочая CI-обвязка run4 — overlay `ac49cf8f62`; использовать её URL/--destination/submodule fixes,
не старую неиспытанную версию GATE-P. Exact source/script identities записать до правок; dirty/wrong base → STOP без reset/stash.

Дословные прежние отказы: sort4-pfc и merge-raw-pfc — `Cannot determine layout for an unsupported type <fn item>`
в shim `FnMut::call_mut` (`function.rs:166`), а merge-profile — calls through function pointers.
Не называть оба случая запретом любого fn-item вызова: raw-строка run4 проходит comparator и останавливается позже на select.
Цель — проверить closure comparator без изменения инструмента, алгоритмов и memory model. Не реализовывать layout FnDef/fn-pointer.

## Test-only overlay: три ON строки

Общий prefix selectors: `slice::sort::shared::smallsort::verify`.
В отдельном std clone поверх frozen snapshot подготовить новый patch/manifest; исходный replay пакет не перезаписывать.
Ни production SmallSort bodies/контракты, ни `Profile::CMP` не менять. Правки только test harnesses/новый cfg test-only модуль.

| ID | Selector / target и изменение | Предварительный оракул |
|---|---|---|
| `merge-raw-closure-on` | `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0`, прежний PFC `bidirectional_merge`; callback `&mut |a: &u64,b: &u64| tail_less_u64(a,b)` | **SUCCESS**,0 failures/Unsupported; полезный body/frame checks достигнуты |
| `merge-profile-closure-on` | Новый `replay_gateb_prime::merge_profile_closure_scratch48_u8_n9`, PFC нового concrete test-only target `merge_profile_closure_u8`; ниже контракт | **SUCCESS**,0 failures/Unsupported, ensures и обе backing alternatives достигнуты |
| `sort4-closure-on` | `helper_contracts::sort4_safety_u64`, прежний PFC `sort4_stable`; callback `&mut |a: &u64,b: &u64| arbitrary_less::<u64>(a,b)` | **BOUNDARY**, ожидается1 named `select_unpredictable` Unsupported, hint.rs:871;0 fn-item-layout/fn-pointer, uninit и frame failures |

M1 сохраняет u64 N8, scratch48 `[MU<u64>;48]`, initialized src[32..40], uninitialized dst[0..8], source readbacks/frame,
исходный panic-on-order-violation stub и unwind34. Замыкание без захватов делегирует прежним volatile reads/nondet bool,
не заменять его произвольной константой/чистым comparator: исходный safety-domain сохраняется.
Sort4 сохраняет initialized src4, отдельный `MU<[u64;4]>` dst, source frame и output readbacks, unwind16.
Для sort4 SUCCESS вместо ожидаемой границы требует review фактического body/достижимости; не засчитывать автоматически.

### Почему для profile нужен новый target

Существующий `merge_profile<P>` принимает fn pointer, `P::CMP` тоже fn pointer. Coercion замыкания в fn pointer вернёт прежний
отказ. Поэтому M2 — **concrete test-only companion**, не повтор доказательства оригинального `merge_profile<P>`.
Новый module declaration, wrapper и harness закрыть `#[cfg(kani_smallsort_controls)]`. Определить concrete u8 wrapper, вызывающий реальный `bidirectional_merge`
с `&mut |a: &u8,b: &u8| super::merge::lt_u8(a,b)`. Внутри замыкания нужен direct free-function call,
**не `LtU8::CMP(a,b)`**. Канонический порядок — `(*a >> 1) < (*b >> 1)`, не `*a < *b`.
Перенести без ослабления concrete аналоги `merge_regions`, `merge_halves_sorted::<LtU8>`, modifies dst[0..len],
ensures `model_sorted::<LtU8>` и `model_count::<LtU8>(src)==model_count::<LtU8>(dst)` с тем же probe setup.
Fn-address guard отсутствует потому, что нет comparator-параметра и comparator зафиксирован телом; это не разрешение
произвольного FnMut. Сделать correspondence table original clauses→concrete clauses→fixed comparator equivalence.
Harness копирует N9 initialized prefix в nondet выбранный flat48/general `MU<[u8;48]>` backing, dst отдельный initialized N9;
сохраняет обе covers и unwind34. Production profile/его generic proof credit неизменны.
Если такую correspondence нельзя сохранить test-only — STOP до CI, не заменить строку ослабленным ordinary/safety-only тестом.

## Обвязка, пределы и свидетельства

Только эти3 ON строки, jobs1/max-parallel1, object-bits12, исходные unwind16/34 и штатные solver/slicing/default checks.
Сохранить organizer flags, включая --no-assert-contracts для ordinary контекста, выбранные PFC Check targets,
valid-value OFF и controls cfg ON. Ни OFF matrix, ни дополнительные negative/calibration rows в этот лимит не добавлять.
Проверенный raw-negative run4 остаётся отдельным историческим свидетельством, не новым negative этого overlay.
Пакет CI-only поверх run4 recipe, с unchanged C1 source binding; все собственные workflow только в CI overlay.
Предложение caps: прежний root timeout2400s,≤3 invocation, общий job envelope180min с setup/report reserve;
фактические runner/caps назначает координатор. Нет автоповторов/перебора geometry после отказа.
До исполнения только Python-only wrapper tests, explicit Rust type/closure/contract review и `git diff --check`.

Координатор собирает для каждой строки source/overlay hashes, effective argv, C1 binary/runtime/solver hashes,
selected PFC target/body, полный failure list/Unsupported inventory, useful reached checks/ensures/covers, original exit/signal/RSS.
Artifacts сохраняются и при отказе, truncation/missing → UNKNOWN. Unsupported/layout/frame/timeout не может дать merge SUCCESS.
Новый отказ merge — результат BLOCKED с точным следующим препятствием, не причина менять Kani или ослаблять контракт.
Sort4 named boundary — диагностический успех задачи, не verification SUCCESS и не положительное whole-SmallSort evidence.

## Handoff / STOP

Worker15 пишет только отдельный test-only overlay, bounded replay request/scripts и research `kani3300/gateb-prime/`:
INPUTS, PATCH/CONTRACT-MAP, ROW-ORACLES, CI-REQUEST, REVIEW, RESULT-template. Existing C1/C1b и research run4 неизменны.
Базовый tool pin должен оставаться C1, даже если параллельно готовится C2; Gate A C1b из-за test-only изменения не повторяется.
Завершить после подготовки `READY <package sha>`; source/CI push и запуск — координатор. Результат Gate B′ передать
в план C2 и SEL1: позитивная merge-строка квалифицирует только её bounded geometry/target, не снимает общие границы scope A.
