# KANI3300 M2-A — локализация legal-pair и минимизация ресурсов, worker 14

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна аналитическая/подготовительная сессия,
**Cloud $0**. CI и любые compiler/verifier запуски — только координатор. Это верификация корректности, не security-работа.
Цель: отделить ложный uninit от контрактного режима и ресурсного исхода; подготовить маленькие различающие inputs.
Production/model repair и активация M3 в эту стадию не входят. Worker 15 продолжает независимый B3R2, его задания не менять.

## Вход, identities и уже известные исходы

- Читать `/root/kani-fix-3300-m2` на **5f7f2b7364135a0a8b7cfd86c43b4491a8911bac**,
  tree **b2bbb7366a9fbac33398fb01be7300f83a1d27bd**, parent M1 **5abdcf982da6aff65662e198af27a9c776830a89**.
  M2 test-only; production **254ae69662b3206cd4432dae0cd44c534b1b13fb** не изменён. Clone/ветку не менять.
- Прочитать `kani3300/m2/{RESULT-KANI3300-M2.md,QUALIFICATION-MAP.json,CFG-BINDINGS.md,CI-REQUEST.md}`,
  M1 SOURCE-BINDINGS и M0 contract. Сохранять unresolved obligations из исходной M2 matrix, не начинать новый model design.
- По координатору Quick **43229982767** дважды прерван shutdown раннера, exit143 в expected uninit.
  Это INCOMPLETE, не установленный OOM и не semantic FAIL. Отдельный memprobe **43232249168**,
  CI-only **cc29c82bf1e2ed4b29e7dcc0980744074be459e9** (parent exact M2), runner16GB, по одному test selector:
  out-pointer 3.3s/225MB, 1SUCCESS+1FAILURE, сообщения `*const u8`/`u8`; normal-abort 1s/203MB,
  FAILURE `transfer qualification abort`; оба matched compiletest golden. Это ещё не exact intended-property qualification.
  legal-pair с `-Z function-contracts`: 14:16, peakRSS15.07GB (CBMC14.6GB), **ОБА** roots
  `legal_ordinary_transfer` и `legal_pfc_transfer` FAILED uninit-read `[u8;3]`, хотя golden требует SUCCESS.
  postcondition-hole — OOM/runner killed, verdict UNKNOWN. Единицы здесь source-reported; для новых измерений сохранить raw units.
- Новый C1-T2-A **7f9eec41e8**, baseline Quick **43230538511** expected127/7, M1 composition **83ceadf048**,
  Quick **43230532195** expected138/0/2ignored: все8 mixed matched, шесть legal baseline falseFAIL→M1 PASS.
  Это controls другой композиции, не свидетельство PASS M2. Не cherry-pick их production/старую базу поверх M1.

## 1. Сначала source/mode и имеющиеся точечные сведения

Сохранить хеши четырёх M2 inputs/goldens, actual argv/toolchain/root selection и доступные curated observations memprobe.
Отсутствующие exact property IDs/трейсы/память — UNKNOWN и конкретный запрос, без догадок по одному тексту ошибки.
Исторические m2 results не переписывать. M2-A готовит новый package и заканчивает сессию до CI координатора.

**Ordinary root здесь не автоматически no-contract.** Он вызывает декорированный `write_initialized`:
`kani-compiler/src/kani_middle/transform/contracts.rs` выбирает Assert при default assert_contracts;
`no_assert_contracts` выключает Assert, но Check для proof_for_contract имеет приоритет и остаётся PFC.
Проверить actual mode/wrapper по pin. Сравнить default ordinary, ordinary с `--no-assert-contracts` и undecorated body;
один `-Z function-contracts` и имя harness не устанавливают режим. Ensures не содержит `old`, не объяснять сбой old-copy без binding.

Для **каждого** root развести три equality sites: body `value == [1,2,3]`, ensures `*out == [1,2,3]`,
root `out == [1,2,3]`. По actual MIR/retained CheckAs/property связать ОБА operands:
origin/carrier/AllocId и mask→backend symbol→object/offset/extent→witness reset/seed→последний setter/transfer→read.
Различить promoted RHS, stack assume_init temporary, out referent и generated contract copies. AllocId не runtime object ID.
Проверить normal-edge setters, source-following false и macro/hook copy лишь там, где actual путь установлен.
UntrackedDeref/generated-copy, отсутствующий seed и повтор старого D0 — альтернативные гипотезы, не готовый диагноз.
Если сведений недостаточно, первым запросом является singleton MIR/property inventory, не тяжёлый повтор полного solver.

## 2. Адаптивная минимизация: один compiler root и solver за раз

Runnable drafts хранить в research **kani3300/m2a/cases/**, вне активной suite; по одному root на input.
Флаги/edition/-D warnings/source hashes/semantic oracle задать явно: прямой Kani CLI не исполняет compiletest comments.
Проверить поддержку CLI по исходникам pin, включая exact harness filter, serial execution и codegen/MIR-only режим.
Сохранять copyright/license headers. Ни локальных запусков, ни нового runner/watchdog/serde/trace framework.

Первая CI-REQUEST — **не более шести configurations**, последовательных и выбираемых по source findings:

1. Original ordinary и original PFC отдельно: сначала существующий codegen/MIR/property-inventory путь,
   без повторения 15GB solver. Записать compiled/selected roots и actual contract mode; source order не codegen order.
2. Минимальный ordinary с исходными transfer/array3/promotion sites: default Assert против `--no-assert-contracts`;
   undecorated companion с uninit-only против uninit+contracts flag — если это нужно для различения mode/flag/body.
   Не строить всю декартову матрицу: приоритет actual failing site; до6 configs включает codegen-only requests.
3. Tiny genuine PFC legal/false-postcondition calibration, если нужен для объяснения ресурсов:
   сначала scalar/MU<u8>, без array equality/heap; потом вернуть только установленный array trigger.
   Отдельный PFC root должен проверять полезное ensures, а hole оставаться valid MU до intended read именно в ensures.

Если начальная очередь требует больше6 configs, выбрать наиболее различающие и остальные пометить DEFERRED.
Modifies-only/scalar-only/array-only ensures reductions — следующая очередь после mode/site binding, не массовый запуск.
Все запросы — существующий Quick/memprobe с одним input/root и без parallel CBMC. Полный Quick пока не запрашивать:
его исходные heavy selectors не стали безопаснее от появления маленьких probes.

Цель минимального semantic probe — примерно ≤60s и ≤2GiB RSS; для первого solver batch предложить предел
≤180s/≤6GiB на процесс/runner с записью actual enforcement координатором. Не выдавать ulimit виртуальной памяти за RSS.
Если существующий CI не умеет точный cap, согласовать применимый существующий лимит, не писать новую инфраструктуру.
Cutoff/OOM/timeout — RESOURCE_INCOMPLETE, не diagnostic PASS/FAIL; baseline для новой resource-оценки нужен matched.
Фиксировать elapsed/RSS units, per-process vs process-tree, concurrency, solver/flags и available program/VCC sizes.
Большой исходный solver повторять только по отдельному решению координатора после маленьких результатов.

При необходимости запросить узкий trace **уже установленного** property через существующие поддержанные опции.
Property-filtered run — диагностика, не full harness proof. Никаких новых64MiB global dumps/raw archives/full logs;
D0-A прежняя raw-access exception сюда не переносится. Неполный report → точный targeted запрос, не обход интерфейса.

## 3. Сохранение смысла и условия STOP

В MINIMIZATION-LEDGER каждую убранную feature/assertion связать с исходным obligation:
RETAINED / QUALIFIED_ELSEWHERE(exact property/run) / STILL_UNRESOLVED. Разбиение на маленькие tests допустимо,
но scalar-only, no-assert-contracts, исчезнувший array equality или снятый PFC/frame не закрывают исходное combined obligation.
Смена assert_eq на assert/размера/attr может менять lowering: это отдельный input, исчезновение FAIL не model fix.
Не менять initializedness assumptions, expected semantic verdicts, checks, required bounds/negative reads ради ресурса/PASS.
Исходные четыре M2 inputs/goldens остаются неизменными; replacement patch только после отдельного принятия CI findings.
Модель/ABI/setters/registry в этой стадии не менять. Для concrete source gap — минимальный reproducer, proposed narrow repair
и falsifying negative, затем STOP для отдельного задания. Nested MU-of-flat, B3/G1/B4/T1b не добавлять.

Out-pointer вторично квалифицировать по **всем** Failed Checks: сообщение `*const u8` может быть extra early failure;
совпадение substring `u8` с golden его не легализует. Нужны intended middle-hole read и legal endpoint checks.
Abort golden тоже не доказывает отсутствие normal-return эффекта без CFG/путевого binding. Не объявлять эти gaps закрытыми.
Postcondition-hole нельзя заменить ранним assume_init UB в body: return MU legal, первый payload read остаётся в ensures.
Фактические normal/check/Assert/Original modes, frame и false propagation должны оставаться различимыми в итоговой matrix.

## Результаты и handoff

g0 **kani3300/m2a/**: `INPUTS.json`, `SITE-MAP.md`, `MINIMIZATION-LEDGER.md`, runnable `cases/` + `TEST-MANIFEST.json`,
`CI-REQUEST.md`, `REVIEW.md`, `RESULT-KANI3300-M2A.md` (≤25 строк: established/hypothesis/UNKNOWN/resource gates).
До новых CI — PREPARED/AWAITING_CI, не completed causality/resource fix. Existing memprobe facts помечать coordinator-reported.
Один bounded Luna High review: valid inputs, mode axes и сохранение obligation ledger, без nested delegation/повторного model audit.
Статика/hash/diff --check; никакого local cargo/rustc/Kani/CBMC/Miri/сборок. CI/Actions/Cloud dispatch/workflow edits запрещены.
Не читать/качать raw archives/full logs/credentials, не публиковать PR/issue/комментарии, без ссылок на сторонние PR.
Research-only commit [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com> через git -c;
stage только kani3300/m2a/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
M3 остаётся HELD до actual legal/PFC/postcondition qualification и принятого ресурсного решения, не по READY.
После reviewed package STOP. Последняя строка: `READY <sha research-коммита M2-A>`.
