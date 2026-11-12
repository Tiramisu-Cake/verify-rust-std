# KANI3300 Part 1 — план после выбора B, 2026-11-12

**Решение владельца:** flat `[MaybeUninit<T>;N]` / `[MaybeUninit<T>]` остаются в scope для SmallSort scratch.
Direct-MU-only экспорт отклонён. Полная для заявленного домена raw_eq-модель — зависимость выпуска; откат с оговоркой,
type-only skip, default true и потеря negative checks не являются вариантом. Runtime Codex; Cloud $0, CI только координатора.
Это верификация корректности, не security-работа.

## Исходное состояние

- Аудит R2 `124a45e373`, особенно блокеры §1–2, ответы 2–5 и 11–13; R0 `8ad13e016e`, `kani3300/r0/` — статическая карта, не proof.
- Аудированный source `a0a2386001a15fecfe2facc2f6cd87f3dee13b60` — baseline D0, сохраняется неизменным.
- B1I `dc5f5a406749a73f1c3192e0b5338441e79508bb`, research `54b7b7fbc4`; Uninit Quick `43196180814`, workflow-only
  `b5f87a7e92105965b719b71bb2f4741c14f0816c`: по сообщению координатора fmt/build/clippy PASS, expected 111/7/2 ignored,
  kani 22/0, ui 14/0, script 1/0. Семь failed selectors — known raw_eq legal и шесть неверно bound новых fixtures;
  прочие existing controls прошли, production-регрессий по этим данным не выявлено. Это не Quick PASS и не shim coverage.
- B1I-A test-fix `6134e42dd1c65dc980336e7d9455aba02d423edf`, research `e3e1125988`, production как dc5f5a4067.
  По координатору Quick `43199156872`, workflow-only `fcba2fe76883c3441182bb6c7506ca8565c62797`: fmt/build/clippy PASS,
  kani 22/0, expected 119/1/2 ignored, ui 14/0, script 1/0; единственный FAIL — известный raw_eq legal. ABI gaps остаются.
- Worker 14 продолжает D0; worker 15 готовит C1-P. Достаточно **двух** воркеров: model/интеграция у одного владельца,
  B1I/контроли/ограничения ABI у другого. Третий постоянный исполнитель не нужен; bounded Luna High review — по semantic gate.

## Стадии и зависимости

| Стадия | Владелец и порядок | Результат / STOP |
|---|---|---|
| **D0-P → CI → D0-A** | 14 сейчас; TASK-KANI3300-D0.md. Подготовка, запуск координатором, анализ в следующей сессии | Два legal harness по одному и вместе AB/BA: actual MIR/points-to/relevance, runtime witness и allocation mapping. STOP до достаточных данных, без исправления модели |
| **B1I-A** | 15 параллельно D0; TASK-KANI3300-B1IA.md | Перепривязать шесть fixtures: FnPtr, tuple-layout Unsupported, Item-return uninit; сохранить negative и добавить initialized Item companions. Production неизменен. Настоящие shim/Err branches остаются gaps; после test review STOP до targeted/Quick rerun координатора |
| **C1-P — подготовка** | 15 сейчас; TASK-KANI3300-C1P.md, параллельно D0 | Матрица/research-only drafts и compiler-input specs без production, Kani-suite activation и запусков. Переиспользовать existing controls; STOP до D0-A/M0 |
| **M0 — контракт модели** | 14 после D0-A; 15 готовит тестовую матрицу по R0 и аудитам | Зафиксировать allocation identity/offset/extent, immutable init masks, runtime shadow lifecycle/false, supported writes/normal returns и Unknown→Unsupported. Каждую гипотезу связать с D0; missing setter не предполагать по типу temporary. Review → STOP design gate до реализации |
| **M1 — anonymous/promoted allocations** | 14 после M0; 15 параллельно C1 ниже | Протянуть referent AllocId, смещение, фактические Some/None bytes до seed/points-to/relevance и init model; учесть coalescing равных allocations. Нельзя выводить initializedness из backend zero-fill или из &T. Targeted legal + false-mask negative → STOP/review/CI |
| **C1 — контроли и ABI-границы** | 15 после B1I-A и M0, отдельный clone; production files не пересекаются с M1/M2 | Test-only controls; отдельными ограниченными commits — guards для by-value DST, retained ordinary-union constant, непарного hook/shim, если нужны. Не расширять ABI/union model. Если нужен общий файл/изменение интерфейса — передать владельцу модели, STOP параллельной правки |
| **M2 — call destinations и state transfer** | Тот же model owner, последовательно после M1 | По D0 закрыть реальные gaps relevance/setter на normal-return destination: ordinary T только доказанная typed initialization; shadow-carrying значение — фактический transfer с false и typed mask. Не bless padding/false, не менять unwind/abort edge. Существующий корректный setter не дублировать. Review + reached controls → STOP |
| **M3 — композиция и интеграция** | 14 после принятых M1/M2/C1 и B1I; 15 проверяет матрицу/property binding | Aliases/offsets/subranges, overwrite/reset/reuse и cross-call effects; promotion↔local dynamic choice, оба raw_eq operands, flat arrays/slices, zero extent. Неизвестные эффекты — честный guard, не скрытое расширение heap/foreign/realloc. Targeted gate до полного CI |
| **K0 — условная cache-зависимость** | Только если D0/targeted показывает order-dependent verdict/property в заявленном домене | Отдельный causal matched experiment с теми же roots/MIR/checks; fresh transformer — проверяемая гипотеза, не принятый fix. После доказанного ремонта отдельный review и regressions. Пока зависимость не закрыта — STOP выпуска |
| **G1 — matched gate** | Координатор запускает; 15 анализирует, 14 владеет repairs отдельными стадиями | Одни fixtures на base bf9c58e662 / R1 1cd96e354 / a0a2386001 / финальном кандидате: два legal equality, legal retained raw_eq, left/right holes, flat-slot raw-copy hole. Зафиксировать реальные различия lowering и reached properties, не требовать от старой unchecked модели нового failure |
| **G2 — полный gate и экспорт** | После G1, неизменённый source/test SHA; один интегратор | Все штатные ordinary/opt-in regression jobs, Linux x86_64/AArch64 и platform statuses; PFC legal/frame/clause, B1, layout/ZST/flat/overwrite и multi-root controls. Затем source/test-only export и актуальный PR. Упаковка с тем же tree сохраняет только same-tree связь со старыми runs, не новый PASS |

Каждый блок реализации/анализа — одна сессия, завершается review/результатом и STOP; следующий блок выдаёт координатор.
D0-P и D0-A — две сессии вокруг CI, не ожидание/автоматический переход к model fix. Выданы D0-P, B1I-A и C1-P.
M1/M2 не редактировать одновременно: anonymous masks и setters используют общий relevance/shadow pipeline.
Независимые C1 fixture/spec changes можно готовить во время D0; semantic tests/guards финализировать после M0.

## Приёмка и ограничения

- D0 обязан различить compile-time allocation/cache provenance и solver-selected runtime object/witness. Гипотеза о правом
  operand не равна установленному AllocId; отсутствие record/setter при incomplete trace не доказывает его отсутствие.
- B1I приёмка включает согласованность reachability/seed collection/points-to/local visitor: runtime Unsupported не защищает
  от более раннего resolver/body unwrap. Оставшиеся synthetic shim/Err controls должны быть реально bound, а не зачтены по source spec.
- Не разрешены scope reduction flat, raw_eq rollback, глобальное bless, дополнительные assume вместо checks или ослабление goldens.
  Exact per-harness properties/reachability важнее общего FAILURE; script exit status сохранять. Extra FAIL/ICE, пропавший check,
  неверная identity, partial required trace или неподтверждённая парность → STOP соответствующего gate.
- B3 не интегрировать автоматически: отдельный backend PR. Для canonical MU ZST нужны свои copy/reset/arg-return controls;
  padded ordinary unions с ZST arms не заявлять без нужного dependency. G1/compound storage и B4/realloc — отдельные задачи;
  не покрытые foreign/heap effects на tracked bytes требуют установленной границы/Unsupported, а не одного disclaimer.
- Legal no-contract/PFC roundtrip и legal modifies должны пройти, frame negative должен упасть на frame property,
  clause negative — на uninit property, private shadow state не даёт ложный frame. Timeout/OOM — resource outcome,
  base PASS/export OOM фиксируется как регрессия ресурса. Неизменённый source недостаточен без точных flags/toolchain/limits.
- Для claim о SmallSort нужен отдельный legal/negative **actual scratch** replay с точным library/toolchain pin через
  согласованный fork CI пакет. Native unit tests без такого binding не дают этот claim. Недоступный пакет отметить NOT_RUN.
- Cloud планируется $0. Fork Actions доступны; dispatch/workflows/лимиты/публикация — координатор/владелец.
  Локальные cargo/rustc/Kani/CBMC запрещены. Нет разрешения подменять CI Cloud-прогоном или присваивать старый PASS новым SHA.
