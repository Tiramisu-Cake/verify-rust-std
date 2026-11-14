# KANI3300 SEL1 — select_unpredictable через fallback body

2026-11-14. Worker15, одна стадия реализации/подготовки CI. Это верификация корректности, не security-работа.
Подготовлено для выдачи координатором; этим файлом выполнение не начинается. Локальные cargo/rustc/Kani/CBMC/Miri/builds
запрещены. Preparation Cloud $0; fork CI, source push/dispatch и review — координатор. Без PR/issue/публикаций.

## 1. Принятые входы и параллельная работа

- Exact base `69b13711e60a87458200833445d47488ab466344`, tree `1df668c6896eaed2b08385d307b8ddf178613c6f`,
  read-only `/root/kani-fix-3300-c2-s1`. Изолированный clone **`/root/kani-fix-3300-sel1`**, ветка **`fix/kani-3300-sel1`**.
  Existing destination/dirty или другой base → STOP без reset/stash; не брать latest C2-S2 или старый C1b вместо этого pin.
- Gate B′ завершён: run **43600834435**, research `141fa79499` (`2c3f0af825~1`),
  `kani3300/gateb-prime-result/RESULT.md`. Start prerequisite старого TASK-DRAFT-SEL1-R4.md выполнен.
  На tool C1: merge-raw-closure-on SUCCESS0/570; concrete merge-profile-closure-on SUCCESS0/1028, обе подложки;
  sort4-closure-on — ровно1 `select_unpredictable` Unsupported, без comparator/layout/uninit/frame failures.
  Receipt outcome UNKNOWN — verdicts review взяты из stdout, не из этого поля. Это bounded C1 evidence, не новый gate на69.
- Std snapshot `70ba5befc617627073738e26cb1466bd4fb76e41`; успешный B′ test-only пакет:
  std branch `prep/kani3300-gateb-prime` @`01d75b8e83`, overlay `933b20a237`; CI recipe `0c1cc8a7d0` над `ac49cf8f62`.
  При подготовке сверить full SHA/tree/patch hashes из самого пакета; краткие refs не заменяют immutable binding.
- Прочитать R4 F8/ответ3, `TASK-DRAFT-SEL1-R4.md`, SEL0 `DESIGN-SELECT.md` @`898fdb62943394e227c7f9b67deb313779be1d7d`
  в read-only `/root/verify-rust-std-kani3300-sel`, actual fallback/visitor/points-to на69.

Worker14 ведёт C2-S2 и следующие стадии в других клонах. Не писать в его source/g0 результаты и не переносить незавершённые
F5/F6/F7 сюда. Возможные пересечения visitor/points-to/transform описать в handoff. SEL1 — отдельный трек/будущий PR,
не незаметное расширение scope A текущего C2. После final C2 понадобится reviewed port и новая заморозка.

## 2. Дизайн F8: единственный владелец transfer — fallback body

R4 заменяет старый SEL0 Scope1. Pointer-only recognition с запретом storage-result **не решает** задачу:
полный hint wrapper вызывает select дважды для pointers и третий раз для `MaybeUninit<T>` перед assume_init.
Требуется только exact standard intrinsic `core::intrinsics::select_unpredictable(bool,T,T)->T`, когда codegen/reachability
используют его пригодное fallback body: тот же predicate `!must_be_overridden && has_body`, с checked_body semantics #5152.
Результат — строго выбранный condition arm. Не nondet result, не union initializedness и не bless обоих pointees.
Допущены только sized payloads с вычислимыми существующими masks/protocol; это не поддержка произвольных nested/unsized T.

1. Согласовать `has_transfer_protocol`, caller и callee entry: только этот bodyful intrinsic получает paired argument
   Store/Load и обязательный return0 как обычная bodyful функция. Отдельная прежняя entry-проверка InstanceKind::Intrinsic
   не должна отрезать этот load. Сохранить signature/original indices/count/current-call pairing и normal-return destination.
2. Snapshots снимаются пока actual sources живы, до их deinit. Actual `Move(a)` и `Move(b)` оба сбрасываются,
   даже когда результат выбирает один arm; Copy sources остаются живыми. False выбранного source не теряется,
   payload/padding следуют существующей typed mask, не новой full-storage true-маске.
3. Local intrinsic visitor допускает только этот validated fallback путь; generic intrinsic Unsupported заменяется
   ordinary protocol, но operand traversal/raw/union/validity checks сохраняются. No usable body/overridden/unsupported layout
   → точный operator/type Unsupported до частичных Store/Load/Move deinit; pending checks/loads B1 не теряются.
   Не добавлять blanket can_skip для select-storage или всех intrinsics с body.
4. Points-to использует то же fallback body как ordinary call, а не нынешний Unimplemented no-op. Return должен дать
   dest→referents обоих value arms до fixed point; без condition edge и лишнего уровня адреса arm-slot.
   Не заменять body analysis несогласованной backend-only моделью. Selected pointer value не читает/инициализирует pointee.
5. Backend уже вызывает fallback. Не добавлять второй shadow transfer/bless/conditional-copy result model;
   body/protocol — один владелец selected-byte состояния. Если analysis/codegen выбрали разные тела — STOP.

Primary paths (relative to `kani-compiler/src/`): `kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs`
(entry/call/return/has_transfer_protocol), `kani_middle/points_to/points_to_analysis.rs` (intrinsic/regular call),
`codegen_cprover_gotoc/codegen/statement.rs` и `kani_middle/reachability.rs` (точный fallback predicate).
Узкий общий classifier допустим, если устраняет дублирование predicates; не вводить новую general intrinsic framework.
Не менять runtime buffer representation, DFCC/private assigns, std algorithms, general alias resolution и indirect calls.
Вызовы через fn-pointer/trait objects остаются границей; выбор pointer value не равен такому вызову.

## 3. Обязательные controls — R4 ответ3

До CI сделать конечный manifest selectors и смысловых ожидаемых исходов; старые19 SEL0 selectors не копировать вслепую:
их storage/wrapper Unsupported goldens устарели для F8. Новые результаты пока NOT_RUN.

| Контроль | Требование |
|---|---|
| Select scalar/pointer, condition true/false | Верный chosen value, legal initialized reads SUCCESS; null/dangling selection без dereference не читает pointee |
| SEL0 delayed-padding, обе branches | Выбрать pointer к одному из двух u64, cast к padded type, write и read исходного объекта: intended uninit FAILURE при обоих направлениях; оба alias successors сохранены |
| MU-result legal/hole каждого arm | Selected initialized legal SUCCESS; selected hole — intended payload FAILURE; unselected hole не становится true и не делает selected legal результат ложным FAIL |
| Copy/Move/overwrite/padding | Copy source сохраняется; actual Move sources оба deinitialized; overwritten destination не удерживает старое true; typed padding не bless |
| Полный hint wrapper | u8 и `*const u64` проходят все3 intrinsic calls и assume_init; ни primitive imitation, ни hand-written if вместо настоящего wrapper |
| Refusal controls | Другой unmodeled intrinsic/no пригодного fallback/layout остаётся explicit Unsupported; B1 fn-pointer/trait-object и true conflict diagnostics не ослаблены |
| Matched raw sort4 legal/hole | Legal SUCCESS; negative — intended source[1] read smallsort.rs:751, без прежнего select Unsupported/раннего frame/layout отказа |

Custom-MIR допустим для явного Move, не для обхода type/layout guard ради положительного результата.
Никаких initializedness/alias assumptions и global skips. Negative oracle — точное число intended failures/описания,
полезные own assertions SUCCESS и verdict; не host/toolchain/std-line inventories. Дополнительный mapping остаётся research.
Для условного select payload snapshots, selected-arm false и источник чтения связываются с source operation;
просто совпавший FAILED/Unsupported не квалифицирует negative. Setup/timeout/OOM — NOT_RUN/UNKNOWN, не expected failure.

## 4. Целевой SmallSort ON gate

После native controls и review подготовить coordinator request на exact candidate и frozen std/B′ overlay, object-bits12,
jobs1, default solver/slicing/checks, valid-value OFF, controls cfg ON и прежние organizer/PFC flags. Никаких tool/std pin upgrades.

- **sort4-closure-on**: тот же `helper_contracts::sort4_safety_u64`, PFC настоящего `sort4_stable`, unwind16,
  initialized src4/отдельный MU output4, прежний noncapturing closure comparator и frame/readbacks из B′.
  Новый oracle **SUCCESS**,0 failed Unsupported/uninit/frame/прочих checks, useful assertions и comparator covers достигнуты.
- **swap-if-less-closure-on**: `helper_contracts::swap_safety_u64_backing4`, PFC настоящего `swap_if_less`, unwind8.
  Отдельный **test-only** std overlay меняет callback в `exercise_swap` на noncapturing closure
  `|a: &T,b: &T| arbitrary_less::<T>(a,b)` с direct free-function call, не fn-pointer coercion/`FnMut` fn-item wrapper.
  Сохранить backing4 initialized values, nondet a/b<4, equality a==b, real helper/contract и outside-position frame asserts.
  Oracle **SUCCESS**,0 failed Unsupported/uninit/frame; comparator true/false, a==b/a<b/a>b и normal return source covers достигнуты.

Не менять production contracts/implementation std и не добавлять layout FnDef поддержку ради swap. Полный hint путь должен
остаться реальным. Два целевых gate — bounded helper evidence, не доказательство всего SmallSort/всех T,N.
Две successful merge closure строки B′ входят в regression request на новом tool, но их C1 counts570/1028 не новый golden.
Полный первоначальный Gate B не запускать автоматически; дополнительные replay rows/caps назначает координатор.
Для каждого root сохранять effective argv/selected PFC body, source/overlay/binary hashes, полные failures и useful reached checks/covers.
Наличие неупавшего unsupported_construct property не равно failure; важны0 failed Unsupported и reached полезные obligations.

## 5. Приёмка и handoff

Статика: explicit Rust operand/signature/cast/borrow review, выбранные Instance/body/Copy-vs-Move paths, `git diff --check`.
CI-request: fmt/build/clippy, targeted native controls, existing Uninit/expected/ui/script и contract/mode suites,
затем named ON gate. Все local compiler/verifier runs запрещены; source/CI push и выполнение — координатор.
Known composition JSON FAIL из S1 (`kani3300/c2-s1/DRIFT.md`) остаётся S5 debt, не блокирует SEL1 приёмку сам по себе.
Не менять его manifest/checker, не auto-bless и не утверждать all-Quick-PASS; новый lost check/status/payload regression
за пределами локализованного S1 drift — STOP/review, не blanket exemption. F5/S2 fixes в эту стадию не импортировать молча.

Research `kani3300/sel1/`: INPUTS, FALLBACK/TRANSFER-MAP, CONTROL-MANIFEST, TARGET-GATE-MAP, REVIEW, CI-REQUEST, RESULT.
Отметить semantic intersections с C2-S3/F6 и S4/F7 для будущего port, сохранённые scope exclusions и все NOT_RUN/UNKNOWN.
Source neutral local commit(s), author/committer Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без source push/PR.
Финал после выдачи: `READY <local SEL1 source sha>`. Не начинать другую стадию и не объявлять Part1/SmallSort release-ready.
Позже — reviewed port на final C2, новый freeze, Gate A на3 принятых платформах и повтор согласованного SmallSort replay;
старые C1/C2 receipts на production delta SEL1 не переносятся. Решение об отдельном upstream PR — за владельцем.
