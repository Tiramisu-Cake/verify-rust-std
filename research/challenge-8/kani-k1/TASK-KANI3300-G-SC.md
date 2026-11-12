# KANI3300 G-SC — fail-closed PFC scope, worker 15

**HELD / NOT ISSUED — коррекция владельца 2026-11-13. Реализацию НЕ выдавать до ответа второго аудитора.**
Ниже сохранён неутверждённый implementation draft; он не разрешает создавать source-кандидат или начинать кодирование.
Runtime Codex, предполагаемая одна сессия реализации/review, **Cloud $0** — только после нового поручения координатора.
Это верификация корректности, не security-работа. Local compiler/verifier/builds запрещены; fork CI запускает координатор.
Владелец приостановил решение о реализации: scope cut и альтернативы открыты для независимой оценки.
Worker15 не получает implementation stage. Worker14 по TASK-KANI3300-G-SC-C.md готовит только read-only инвентарь.
Все нижеследующие implementation/CI/oracle инструкции — исторический draft, не действующее разрешение.

## Вход и точная база

Прочитать аудит `AUDIT-REPORT-KANI3300-PFC-RESOURCE-RU.md` @ab7509822453bbf0778da0265c67f51bc08b4755 §5–8,
`kani3300/d1a/{RESULT-KANI3300-D1-A.md,ATTRIBUTION.md,MODEL-MAP.md}` @15276d57238f4a70b2ea5fca9141ef047cce120c.
D1: offender не найден, normal verification NOT_RUN; R6 frameFAIL-контраст не корректный performance baseline.
Никаких новых representations/R9, converter profile C, DFCC exemptions или утверждений об исправлении OOM.

Base **4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c**, tree **af28e22ec446b254cfa3a28b2882eafa58d5a458**.
Создать `/root/kani-fix-3300-gsc`, branch `fix/kani-3300-pfc-transfer-scope` от exact base;
existing/dirty destination → STOP без reset/stash. Старые source clones read-only. Не начинать от R7/R8/filtered Quick.
Сохранить A3 snapshot/pairing/return0/false/data-padding semantics, B1, M1 immutable masks и S3 в поддержанной области.
Для controls импортировать **только test-only delta** G-SC-C после READY (если ещё нет — композицию оформляет координатор).
R7-C fe36afc4a8 и R8-C e588fa6437 — источники тестов, не production; их source ancestors/R7/R8 runtime не переносить.

## 1. Контракт поставляемой границы

При `-Z uninit-checks` выбранный PFC **SimpleCheck/RecursiveCheck** harness, содержащий reachable shadow call-transfer,
должен получить явный Unsupported, а не ложный SUCCESS, payload-uninit proof или resource cutoff.
Ordinary/Original и ordinary Assert того же тела этим решением не отклонять. PFC без transfer должен остаться доступен.
Сочетание двух глобальных -Z флагов, наличие атрибута/MaybeUninit в исходной сигнатуре или имя helper — недостаточные критерии.

Предпочтение — **консервативный admission check выбранного harness** по выбранным transformed bodies/effects:
пер-харнесс root/mode context, complete effect summary → reject до materialization дорогостоящего DFCC/Boolean пути.
Можно отклонить весь затронутый PFC harness, включая его setup; это осознанно более широкая граница, не минимальность.
В DESIGN/SCOPE указать, включён ли setup, какие clauses/helpers входят, и дать причины каждого отказа.
Альтернатива path guard допустима только с доказанной полнотой/размещением до первого эффекта и отсутствием дорогого prefix;
если это не обеспечивается в одной стадии, STOP с конкретным API gap, не переходить к blanket global ban.

Admission rule: TRANSFER → Unsupported; NO_TRANSFER допускается только при complete analysis;
UNKNOWN_REACHABILITY/неподдержанный effect → отдельный явный Unsupported в этом PFC-контексте, не «эффекта нет».
Для known intrinsics/models нужны обоснованные summaries; неизвестное ребро нельзя молча считать безвредным.
Рекурсию анализировать fixed-point/visited context; depth/node cap означает UNKNOWN, а не NO_TRANSFER.
Не отвергать ordinary harness из-за неизвестного PFC-ребра в другом root; прежние B1 checks/диагностики сохранить.

## 2. Что считать transfer и откуда брать context

Pinned anchors: `kani_middle/transform/contracts.rs::contract_mode` (SimpleCheck/RecursiveCheck/Replace/Assert/Original),
`transform/mod.rs` (FunctionWithContractPass перед UninitPass), `check_uninit/ptr_uninit/{mod.rs,uninit_visitor.rs}`
и `check_uninit/mod.rs` (операции/lowering). Проверить exact names/types по4f64; поздний R8 не source API oracle.
Сейчас visitor получает Instance, не весь выбранный PFC context: context передать явно, не угадывать по локальному callee.
Обход должен наблюдать тела после mode selection и transforms, раскрывающих relevant generated closures/clauses/helpers.
Не вызывать дополнительные mutating BodyTransformation queries ради диагностики; анализ не должен менять ordinary body.

Эффекты: callee entry LoadArgument; caller Begin/Store shadow args; Move-source clear; return-only Store0;
normal-return Load0; выбранные requires/ensures/old/generated Check/recursive bodies и reachable helpers.
Использовать тот же критерий union/MaybeUninit и qualification, что реальный instrumenter, включая monomorphized формы;
не дублировать несогласованный «похожий» source-type фильтр. Return-only обязателен даже без MU-аргументов.
Обычная внешняя сигнатура/closure capture/constructor не означает отсутствие скрытого transfer.
Source→selected body/mode→effect inventory→admission location записать в GUARD-MAP с completeness/reason.

Guard должен предшествовать Begin/Store/Move-reset, callee loads и Store0 для return-only; не выполнять частичный протокол.
Ранний compiler diagnostic либо existing Unsupported assert+assume(false) допустимы с явно заданным oracle и source reason;
один assume(false), отключение passes/checks, initialized=true, swallowing ошибок или panic/ICE запрещены.
Если runtime guard остаётся, проверить emitted placement и реально дешёвое завершение; presence guard не устраняет DFCC cost.
Не терять ранее накопленные B1 checks/диагностики при отказе/unknown; один обход/flush и исходные error paths сохранить.

## 3. Cache и Replace — отдельные обязательства

Admission/effect results хранить с harness/root + выбранным mode context либо пересчитывать root-local;
никакого context-dependent Unsupported в общем body cache по одному Instance. Helper `mem_init_fn_cache` остаётся neutral.
Учесть prewarm/MostReachableItems и actual codegen order. Смена порядка ordinary/PFC не меняет их outcomes.
Не маскировать проблему общим fresh transformer/cache reset или выключением существующего cache без обоснованной необходимости.

Replace/stub_verified **не равен Check**: оформить отдельную mode/effect таблицу и независимую qualification.
Uninit-off Replace и поддержанный no-transfer Replace не должны попасть под новый PFC ban.
Для shadow-transfer Replace не обещать soundness по Check-guard; если обнаружена неквалифицированная/ложно успешная граница,
STOP release claim с отдельным решением координатора, не прятать её и не расширять scope cut молча.
Нельзя получать «verified stub» proof credit из PFC, который теперь Unsupported.

## Controls и CI handoff

Worker14 готовит ordinary/PFC пары, no-transfer, return-only, requires/ensures/helper, recursive/generic/generated paths,
unknown calls, Replace и mixed orders. Worker15 может добавить лишь unit tests admission component в своих source files;
integration source/goldens/тестовые names — owner14, без параллельных правок одних файлов.
P1 legal (fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b) и P2 hole
(61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759) сохраняются byte-identical;
оба oracle теперь **Unsupported этой границы**, не P1 SUCCESS/P2 uninit credit. Scope oracle migration — отдельный ledger.
Lawful/negative frame и clauses квалифицировать на оставленных paths, не заменять intended user violation generic frameFAIL.

CI-REQUEST G1: build/fmt/clippy и focused guard/mode matrix, сначала P1/P2 singleton, затем ordinary/Assert/no-transfer,
return/clause/helper/unknown/recursive/Replace и mixed-root actual orders. Существующие 300s/6GiB cap, raw KiB/exit/phase;
Unsupported должен завершаться до resource cutoff; cutoff не acceptance, even expected negative.
Mixed tests: singleton ordinary/PFC, совместный unit в обоих **фактических** codegen orders; source/CLI order не evidence.
Если штатно оба порядка недостижимы — оформить CI-only diagnostic ordering overlay, не production cache rewrite;
READY может быть source-only, mixed gate остаётся NOT_RUN/UNKNOWN до подтверждения координатором.
G2 после focused gate: полный Uninit Quick+unit5/kani/expected/ui/reinstrumentation без удаления тяжёлых selectors,
с возвращёнными legal-pair/postcondition-hole по явному новому scope oracle, а не скрытым исключением.
Поддержанные ordinary/M1/S3/Move/padding controls сохраняют прежние semantic expectations; full platform/M3 gate отдельный.
Новые workflow/runner edits, push Kani и CI/Cloud dispatch работнику запрещены; CI готовит/запускает координатор.

## Приёмка подготовки и STOP

TYPE-AUDIT: mode/Instance/root/context types, lifetimes/shared caches, match exhaustiveness, helper signatures,
условия uninit option и Unsupported lowering; static rustfmt/Luna не compilation (учесть B3 type mismatch).
Разрешены Git/hash/diff/Python source checks и pinned rustfmt; local cargo/rustc/Kani/CBMC/Miri/builds запрещены.
Один bounded Luna High review полноты/context/cache/placement, без nested delegation; исправить конкретные findings.
В g0 **kani3300/gsc/**: INPUTS.json, DESIGN.md, SCOPE.md, GUARD-MAP.md, TYPE-AUDIT.md, SOURCE-MANIFEST.json,
REVIEW.md, CI-REQUEST.md (exact source/test composition), RESULT-KANI3300-G-SC.md (≤30 строк), patch.
До CI SOURCE_READY/NOT_COMPILED, gates NOT_RUN, proof credit0; M3/full gate и практическая совместимость не объявлены PASS.
Local source commit(s) без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, **не push**.
Research [skip ci], тот же author/committer, stage только gsc/, push g0 без force; concurrency → handoff без reset/stash.
Не читать raw archives/full logs/credentials; не публиковать PR/issues и не включать сторонние PR links.
Во всех будущих PR точная строка: *Disclosure: this change and description were prepared with the help of AI assistants.*
После reviewed source/композиции STOP. Последняя строка: `READY <sha локального G-SC source-кандидата>`.
