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
- D0-A `ff5cabbfca`: .2 — immutable promoted RHS (A AllocId9 / B AllocId5, Some×4), selected byte false после init;
  left temporary SetRef/normal edge работает, get TRUE на .2 paths. 12 captures capped, 4 полных target fragments;
  extent static/mask-derived, runtime OBJECT_SIZE UNKNOWN. Причина этого отказа не требует K0; inventory order delta остаётся.
- M0 `742c77fa03` принят: exact immutable mask после witness reset; registry lifetime уточнён как один exported
  GotocCtx/model, не общий compiler CodegenUnit. Действующий left setter сохраняется.
- C1-L `a8f6b7196a` подготовлен, отдельный compile-only CI/runner отменён координатором. Вместо него C1-T через обычный Quick.
- C1-P `d8d3e6d4ca` подготовлен. Worker 14 ведёт M1; worker 15 после C1-T готовит C1-T2 от того же production 6134e42dd1.
  Достаточно **двух** воркеров: model/интеграция у одного владельца,
  B1I/контроли/ограничения ABI у другого. Третий постоянный исполнитель не нужен; bounded Luna High review — по semantic gate.
- C1-T `28e684cbae`, research `51b86a5214`: по координатору Quick `43219870063` (CI `172a7cfdbc`) expected 125/1/2 ignored;
  все 6 C1-T matched уже на baseline, known D0 legal FAIL остаётся. Механизм/actual origins/место hole failure не установлены.
  Worker 15 — C1-T2 mixed inputs и запрос bindings; worker 14 уведомлён файлом M1-NOTICE-C1T2.md, без смены model base.
- M1 `5abdcf982da6aff65662e198af27a9c776830a89`, production `254ae69662`, research `1027035e6b`: по координатору
  Quick `43222702257` (CI `05024a2112`) fmt/build/clippy PASS, unit5/0, kani22/0, expected130/0/2 ignored, ui14/0, script1/0.
  Unchanged D0 legal теперь PASS; immutable-masks4 matched, C1-T6 matched и раньше. Не full gate/полная model qualification.
  Сейчас 14 — M2; C1-T2 уже подготовлен c2d607d9d5 @research10b5800a8e, 15 — следующий C1-T2-A после CI handoff.
  M3 подготовлен, HELD до приёмки actual M2/C1-T2 CI/bindings.
- C1-T2 CI: по координатору baseline43225818126 expected125/9, M1 43225812282 (composition d8a39dbc00, CI2ae27bd269)
  unit5/0 expected134/4. Четыре u8 raw/== cases baseline false FAIL→M1 PASS; четыре MU cases обеих lanes — ранний
  Unsupported nested `MU<[MU<u8>;3]>`, не intended raw_eq failure. Выбор (a): 15 делает direct-flat test repair;
  nested support вынесен отдельным scope question. M2/M3 не расширяют domain ради fixture setup.

## Стадии и зависимости

| Стадия | Владелец и порядок | Результат / STOP |
|---|---|---|
| **D0-P → CI → D0-A** | Диагноз передан @ ff5cabbfca | Immutable RHS не имеет shadow init; left setter исправен. Fragment/capture limitations сохранены; runtime extent UNKNOWN, general cache independence не заявлена |
| **B1I-A** | 15 параллельно D0; TASK-KANI3300-B1IA.md | Перепривязать шесть fixtures: FnPtr, tuple-layout Unsupported, Item-return uninit; сохранить negative и добавить initialized Item companions. Production неизменен. Настоящие shim/Err branches остаются gaps; после test review STOP до targeted/Quick rerun координатора |
| **C1-P — подготовка** | 15 сейчас; TASK-KANI3300-C1P.md, параллельно D0 | Матрица/research-only drafts и compiler-input specs без production, Kani-suite activation и запусков. Переиспользовать existing controls; STOP до D0-A/M0 |
| **M0 — контракт модели** | Принят @ 742c77fa03 | Reviewed design, не proof. Пер-GOTO-model registry finalize после producer passes, до split/export; immutable seed после reset |
| **C1-L — lowering prep** | READY a8f6b7196a, CI отменён | Новый runner не строить; history сохранить, дальнейший путь — C1-T |
| **C1-T — promoted selectors** | READY 28e684cbae; baseline matched все 6 | Regression controls, не D0 reproducer. Actual origins/instrumentation/место hole failure пока не bound; C1-T2 выясняет через обычный Quick/MIR |
| **C1-T2 — mixed selectors** | READY c2d607d9d5 @10b5800a8e | 8 test-only selectors подготовлены; coordinator baseline/M1 CI по c1t2/CI-REQUEST.md. Не повторять реализацию |
| **C1-T2-A/R — анализ и test repair** | 15 сейчас; TASK-KANI3300-C1T2A.md | u8 differential сохранить, 4 MU inputs исправить на direct flat stack и передать paired rerun. Nested outer MU не поддерживать; intended MU read gate ещё закрыт |
| **M1 — anonymous/promoted allocations** | READY5abdcf982d, Quick43222702257 PASS по координатору | D0 legal исправлены без old golden edits; own immutable-mask/unit controls matched. Уточнённые bindings и границы остаются M2/M3/C1-T2 obligations |
| **C1 — контроли и ABI-границы** | 15 после B1I-A и M0, отдельный clone; production files не пересекаются с M1/M2 | Test-only controls; отдельными ограниченными commits — guards для by-value DST, retained ordinary-union constant, непарного hook/shim, если нужны. Не расширять ABI/union model. Если нужен общий файл/изменение интерфейса — передать владельцу модели, STOP параллельной правки |
| **M2 — call destinations и state transfer** | 14 сейчас; TASK-KANI3300-M2.md | Existing setters/false transfers, новый legal PFC/modifies и targeted gaps; до6 новых selectors. Source repair только по конкретному gap; STOP до qualification CI |
| **M3 — композиция и интеграция** | TASK-KANI3300-M3.md подготовлен, HELD | Только после принятых M2/C1-T2 pins и bindings, отдельная activation. Small bounded alias/offset/overwrite/flat/dynamic-origin matrix, затем targeted gate; не ранний параллельный model rewrite |
| **K0 — условная cache-зависимость** | Для причины D0 .2 не нужен; только по отдельному semantic finding | У второго harness есть +2 SUCCESS ptr::write safety checks. Сохранить inventory regression control; causal cache fix требовать лишь при семантическом дефекте/потере обязательного check, не выводить его из одной разницы counts |
| **G1 — matched gate** | Координатор запускает; 15 анализирует, 14 владеет repairs отдельными стадиями | Одни fixtures на base bf9c58e662 / R1 1cd96e354 / a0a2386001 / финальном кандидате: два legal equality, legal retained raw_eq, left/right holes, flat-slot raw-copy hole. Зафиксировать реальные различия lowering и reached properties, не требовать от старой unchecked модели нового failure |
| **G2 — полный gate и экспорт** | После G1, неизменённый source/test SHA; один интегратор | Все штатные ordinary/opt-in regression jobs, Linux x86_64/AArch64 и platform statuses; PFC legal/frame/clause, B1, layout/ZST/flat/overwrite и multi-root controls. Затем source/test-only export и актуальный PR. Упаковка с тем же tree сохраняет только same-tree связь со старыми runs, не новый PASS |

Каждый блок реализации/анализа — одна сессия, завершается review/результатом и STOP; следующий блок выдаёт координатор.
D0-P/D0-A/C1-P/M0 завершены; C1-L CI отменён, C1-T baseline matched, M1 Quick PASS. C1-T2 готов; M2 активен,
C1-T2-A/R исправляет 4 MU fixtures после CI, M3 HELD до rerun/M2 приёмки. READY не заменяет ни одного gate.
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
