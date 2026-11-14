# SEL1-R4 — select_unpredictable через fallback body (DRAFT / NOT ISSUED)

2026-11-14. Worker15, отдельный следующий трек/PR. Это верификация корректности, не security-работа.
Владелец разрешил направление параллельно C2, **но задание не выдавать до завершения и review Gate B′**.
Сейчас только черновик. Ни local cargo/rustc/Kani/CBMC/Miri/builds, ни push/CI/Cloud/публикаций. Preparation Cloud $0.

## Start gate и база

Координатор передаёт результат≤3 B′ строк, точный comparator failure class/следующий блокер и accepted C2-S1 SHA/tree,
построенный на U `0aac16ef62…` + B1 `6fe484b300…`. Отсутствующий accepted port — STOP, не брать latest/random C1b.
Не ждать всего C2 freeze: implementation branch может идти параллельно C2-S2…S6 в isolated clone `/root/kani-fix-3300-sel1-r4`.
C2 scope A не включает этот branch; до проверки SEL1 не cherry-pick'ить его в C2 и не переиспользовать старые gates.
После C2 fixes потребуется reviewed port SEL1 на final C2, новый candidate freeze и новые gate receipts.
Worker14 владеет C2 integration; возможные общие области visitor/points-to передавать как exact patches, без записи в чужой clone.

## Основание и смысл изменения

Прочитать R4 F8/ответ3, фактический fallback путь codegen/reachability на base и SEL0 DESIGN @`898fdb6294`.
R4 **заменяет** старый SEL0 Scope1: pointer-only реализация не пройдёт третий select реального hint wrapper над MU<T>.
Цель — только intrinsic `core::intrinsics::select_unpredictable(bool,T,T)->T` при пригодном fallback body.
Runtime семантика — точный выбранный arm `if condition { a } else { b }`, не nondet result и не объединение shadow двух arm'ов.
Codegen уже идёт в fallback, когда instance не must_be_overridden и имеет body. Uninit/points-to должны использовать
**тот же** пригодный body/предикат и B1/#5152 checked_body semantics, а не отдельную расходящуюся эвристику по имени.
Никакой общей поддержки «все intrinsic с телом», вызовов через fn-pointer/trait-object или новой backend result-модели.
Выбор значения pointer не равен его последующему косвенному вызову. Допущены только sized payloads,
для которых существующие typed masks/парный протокол вычислимы; unsized/nested unsupported layouts дают точный
Unsupported до частичных Store/Load/deinit, а не обещание поддержки произвольного T.

## Один владелец shadow transfer — fallback body

1. Узко расширить `has_transfer_protocol` для exact intrinsic с `(bool,T,T)->T` и тем же fallback predicate.
   Для этой формы caller protocol, callee entry LoadArgument и return StoreArgument должны быть парными.
   Сохранить signature/original indices/mandatory return0/normal-edge destination и проверки current call.
2. Caller снимает snapshots всех actual shadow operands пока sources живы; только после этого deinit actual Move sources.
   Если оба arm передаются Move, сбрасываются оба, несмотря на выбор одного результата. Copy-источники остаются живыми.
   False, selected witness и padding переносятся штатной typed mask семантикой; отсутствие witness не значит true payload.
3. Local intrinsic visitor допускает только этот доказанно bodyful путь. Не убирать operand traversal/union/raw read/validity checks.
   Обойти лишь generic intrinsic Unsupported, заменённый ordinary protocol. No usable body/must_be_overridden —
   operator-specific Unsupported до частичной загрузки return/buffer, с сохранением pending checks. No generic can_skip exemption.
4. Points-to не должен оставлять Unimplemented no-op для допущенного select: идти в фактическое fallback тело как ordinary call,
   откуда Return даёт dest→referents обоих value arms до fixed point. Не добавлять condition edge/лишний уровень arm-slot address.
   Любой специализированный shortcut обязан быть эквивалентен этому body analysis; предпочтение единому владельцу из F8.
5. Pointer value selection не читает/не инициализирует pointees и не bless обоих объектов. MU-result получает exact chosen-arm
   shadow через protocol, не второй conditional-copy/backend model. Alias graph и value/shadow lowering должны согласоваться.

Primary paths, строки перепроверить на C2-S1: `check_uninit/ptr_uninit/uninit_visitor.rs` (entry, call, return, has_transfer_protocol),
`points_to/points_to_analysis.rs` (intrinsic/regular-call effects), codegen statement/reachability fallback predicate.
Файлы C2-S3/F6 и C2-S4/F7 могут меняться параллельно: keep patch separation и отдельный conflict/semantic map при port.
Runtime buffer representation, DFCC, generic alias resolution и production std algorithms не менять ради select.
No-body classification, unsized layouts и unsupported nested aggregates остаются границами; state-reset fixes C2 сохраняются.

## Контроли до реализации оракулов

Составить finite manifest/source expectations до CI; не копировать старые SEL0 storage Unsupported goldens без пересмотра.
- Scalar condition true/false и actual fallback branch, pointer value/null/dangling selection без dereference;
  последующее invalid dereference не должно стать legal из-за select.
- Обязательный SEL0 контрпример: select двух pointers → cast к padded type → write → read исходного u64 при обоих условиях;
  delayed-UB обязан сохранить intended FAILURE на padding, source→dest aliases обоих arm не теряются.
- MU legal/selected-hole для каждого arm; initialized/uninitialized альтернативы, false не превращается в initialized result.
  Copy/live-source, actual Move обоих sources, overwritten destination и payload/padding — отдельные различающие случаи.
- Полный `core::hint::select_unpredictable` wrapper для u8 и *const u64, включая третий MU select и assume_init.
- No-body/overridden/другой unmodeled intrinsic остаётся explicit Unsupported; B1 fn-pointer/trait-object negatives неизменны.
- Matched Gate B raw sort4 legal/hole: после поддержки wrapper legal ожидается SUCCESS, negative — intended source[1] read;
  exact failure set и полезная reachability, не ранний frame/layout/Unsupported. Closure merge positives B′ не должны регрессировать.

Не вводить assumes об initializedness/aliasing и не уменьшать geometry/unwind исходного replay ради успеха.
Если codegen и analysis выбирают разные bodies либо протокол сработал дважды — STOP с minimal instance/body/operation map.
Static checks: exact Rust operand/cast/signature review, `git diff --check`; compiler/typecheck/Kani — только CI координатора.
Per-harness expected-files: точное число intended failures, смысловые descriptions, own useful SUCCESS и итоговый verdict,
без std line/host/nightly golden inventories. Дополнительные output mappings — research, не новая большая JSON-обвязка.

## Приёмка, интеграция, последующие gates

Research `kani3300/sel1-r4/`: INPUTS, FALLBACK/TRANSFER-MAP, CONTROL-MANIFEST, REVIEW, CI-REQUEST, RESULT (новое NOT_RUN).
Source local neutral commit(s), Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push/PR; финал после выдачи `READY <sha>`.
Сначала targeted controls/обычный Quick на exact base+SEL1, затем reviewed port на final C2 и новый frozen candidate.
После production изменения Gate A на принятых3 платформах и SmallSort Gate B повторяются; не ссылаться на C1/C2 receipts как на новые.
Replay использует согласованные closure companions B′ и реальные raw sort4 paths с ON/OFF/negative criteria по отдельному request;
production fn-pointer profile остаётся named boundary, его SUCCESS не обещать. SEL1 не закрывает всё #3300/весь SmallSort автоматически.
Этот документ не выдаётся до Gate B′; публикацию отдельного upstream PR решает владелец после готового reviewed package.
