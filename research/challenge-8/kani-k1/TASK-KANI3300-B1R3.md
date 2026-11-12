# KANI3300 B1R3 — узкий standalone upstream-кандидат после аудита, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна стадия, **Cloud $0**, без запусков.
Трек независим от D0-A/M0: переносим проверенные решения B1I, не Part 1 memory model.
Это верификация корректности, не security-работа.

## Вход и границы

Прочитать `AUDIT-REPORT-KANI-B1-B3-RU.md` @ t0 **`d1f44b300e`**: B1 §1–6, §12–14;
старые `kani3300/b1pr/PR-DRAFT.md`, `kani3300/b1r2/` — история, не актуальный контракт.
Kani **`/root/kani-fix-3300-b1`**, clean `fix/kani-uninit-unresolved-call` @
**`d5f072f2bcf61a04d84bb0e8b54115f3011252fc`**. При другом HEAD/dirty state STOP, без reset/stash.
Создать новую ветку **`fix/kani-uninit-unresolved-call-v2`** от чистого upstream
**`bf9c58e662fd65c64381ef2ac97a6397ffc0693a`**; существующую v2 не перезаписывать, старую ветку сохранить.

Read-only источники решений: `/root/kani-fix-3300-p1b1` — production `cdb439b0a4c36e9e595019895ab803230f332941`,
B1I `dc5f5a406749a73f1c3192e0b5338441e79508bb`, test-fix **`6134e42dd1c65dc980336e7d9455aba02d423edf`**;
research g0 `kani3300/b1i/` @ `54b7b7fbc4`, `kani3300/b1ia/` @ `e3e1125988`.
Читать commits через правильный clone, не cherry-pick whole Part 1. Его Quick `43199156872` (119/1/2 ignored,
единственный FAIL raw_eq legal) — результат **другого дерева/модели**, не evidence нового standalone-кандидата.

## Что сделать

1. Пересобрать узкий fix + финальные тесты в **один commit непосредственно от base**. Call operands обходятся один раз;
   Err/Unsupported выходы сохраняют target ровно один раз через общий flush. Порядок: entry LoadArgument → operand
   checks → Unsupported → исходный call. Не терять ранее собранные ops/targets/points-to edges, не дублировать diagnostic.
2. Адаптировать общий resolver/classification из B1I: local visitor владеет FnPtr/Virtual диагностикой независимо от
   delayed seeds; seed collection fallible и собирает только распознанные intrinsic targets; points-to не unwrap body
   заведомо неподдерживаемого callee. Для generated Shim проверять **actual body availability**, а не считать
   definition-level `has_body()` эквивалентом `Instance::body().is_some()`. Сверить API по pinned toolchain.
   Foreign/allocator/intrinsic models base сохранить; bodyless guard не должен случайно отвергнуть штатные foreign models.
3. **Убрать расширение shadow transfer через bodyful Shim из d5f072f2b.** До StoreArgument отвергать Shim с union/shadow
   аргументом **или** union/shadow destination, пока ABI-парность не установлена. Проверить callee-entry путь к LoadArgument:
   нет допуска неподтверждённого shim transfer через fallback/скрытое ABI-разворачивание. Tuple wrapping не доказывает
   отсутствие shadow; неизвестный/compound layout не обходить. Если для этой границы нужен более широкий model/ABI fix — STOP.
   Non-shadow MIR-backed Shim продолжает обычный путь анализа/инструментирования; **не** вводить blanket Shim rejection.
   Сохранить ordinary drop/closure glue, различая bodyless, FnPtr внутри shim и supported generated body.
4. Строго сохранить standalone модель base: shadow здесь — top-level union, union-only legacy argument transfer,
   без нового return0 handshake; не расширять predicate до Part 1 flat storage.
   Не переносить Part 1 signature/count/size protocol, MU/flat admission, masks, reset/Move, raw_eq, library/mem_init ABI
   или hook/backend расширения. Ordinary Item поведение не расширять под новые fixtures. Изменения production — только
   необходимые caller/classification/entry guard и seed/points-to integration sites с обоснованием каждого hunk.
5. Reachability имеет собственный ранний resolver unwrap до global passes. Проверить фактический путь и явно ограничить
   claim изменёнными проходами; local Unsupported не является защитой от предшествующего compile-time отказа.
   Если acceptance требует незакрытого раннего пути — записать blocker и STOP, не объявлять его безопасным пропуском.
   Отдельный `visit_statement` UnionAsField flush/index defect не чинить здесь; PR claim ограничить Call terminator.

## Тесты и честная привязка

- Сохранить нужные standalone plain/seeded pairs: direct Item positive, FnPtr, Virtual, erased/wrapped/global,
  pending operand read, statement-free entry initialized/partial. Seed — supported copy/cast ordinary bytes, не raw_eq.
  Требовать named read/load outcomes перед Unsupported, а не одну общую FAILURE; actual seeds/relevance — отдельный binding.
- Fn-trait pointer pair больше не обещает bodyless Shim: итоговое ожидание определяется реальным FnPtr path.
  Уточнить comments/harness names/goldens; добавить non-shadow generated-shim/function-item positive и сохранить drop-glue
  regression controls. Его actual kind/body и достигнутые properties остаются NOT_RUN до CI, не угадывать по Fn::call.
- Для tuple-MU и Item-MU return источников B1I-A составить явный **port map**. Там установлены tuple-layout Unsupported
  и genuine Item-return uninit-read, а не shim guards. Чистый base не имеет Part 1 MU conversion/return model:
  **не копировать PASS/negative goldens вслепую**. Переносить только применимый input/ожидание с отдельным обоснованием;
  несовместимые probes оставить в research как excluded/NOT_RUN с причиной, не добавляя model ради их исполнения.
- Genuine Shim argument-only/return-only, bodyless generated instance и FnDef resolver Err — отдельные compiler/MIR
  obligations. Если остаются specifications, так и записать: source FnOnce/tuple/FnPtr не закрывает эти ветви.
  Невозможную для legal MIR форму не конструировать ради фиктивного coverage; не строить новый test framework.
- Все существующие controls не ослаблять. Custom MIR — по pinned API/edition/panic=abort; partial negative должен
  достигать нужного read, initialized companion — не иметь этого failure. Не добавлять ранний UB/layout barrier,
  который маскирует целевой call check. Если diagnostic меняется — объяснить конкретное изменение свойства.

## PR-DRAFT.md на английском по §12

Заголовок **`Preserve memory initialization checks at unresolved calls`**, **`Refs #3300`**.
Описать потерю Call target/entry loads/operand checks, один обход/один flush, точную политику resolver и Shim,
local diagnostic ownership и ограничения более ранних фаз. Не обещать general ABI/union-return/indirect effects support.
Пример — точный regression fixture с pinned ссылкой; measured false SUCCESS на base для entry-partial пока не установлен.
Не выдавать illustrative/custom-MIR source за измеренный минимальный repro. Не обобщать fix на statement-target loss.

Testing: новый candidate SHA/tree **NOT_RUN** до targeted/full fork CI координатора. Исторические standalone
`43110714635` (CI `0e83acc6823d25949f7d303e70a69441d2cfb138`, source d5f072f2b: 22/83/14/1 PASS) и
`43112332778` (d5f072f2b: Ubuntu 22.04/24.04/ARM64, macOS 15 Intel и ancillary jobs PASS; macOS 14 без test steps,
overall cancelled) можно привести только как history, **не validation нового diff**. Причину отмены не выдумывать.
Не ссылаться в upstream-тексте на внутренние Part 1 stages/paths, конкурентов или сторонние PR.
Заключительные точные строки:

`By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.`

`*Disclosure: this change and description were prepared with AI assistance.*`

## Review, результат и STOP

Статика: разрешённая rustfmt-обёртка
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --config-path rustfmt.toml`,
`git diff --check`, imports/unused/`-D warnings` source audit и API hashes. Локальные cargo/rustc/Kani/CBMC/Miri запрещены.
Один независимый Luna High semantic review адаптированного diff + test contracts + PR; delta — тому же reviewer,
без вложенной делегации. Новые runtime/MIR/property outcomes везде NOT_RUN.

Финальный Kani HEAD: один fix-plus-tests commit, единственный parent = base, CI workflows отсутствуют;
author/committer **Tiramisu-Cake <igkharin@gmail.com>**, нейтральное сообщение без `[skip ci]`.
Разрешено amend только **нового локального неопубликованного v2** для review fixes; d5f072f2b/старую ветку не переписывать.
Записать full SHA/parent/tree/diff inventory; равенства tree с d5f072f2b не ожидать. **Kani не пушить.**

В **t0** `research/challenge-8/kani-k1/kani3300/b1r3/`: `NOTES.md` (≤35 строк), `PORT-MAP.md`,
`TEST-MANIFEST.json` (expected/observed/provenance/gaps отдельно), `PR-DRAFT.md`, `REVIEW.md`, `CI-REQUEST.md`,
`RESULT-KANI3300-B1R3.md` (≤20 строк). CI request: exact-SHA Uninit Quick и нужные singleton/JSON/MIR checks,
затем штатный full gate. Matched base run нужен до false-success claim; его отсутствие не заменять прежними counts.
Research commit `[skip ci]`, тот же author/committer, stage только `kani3300/b1r3/`, push t0 без force;
чужие active/untracked/staged файлы (включая b3p) не включать. Concurrent/non-fast-forward → handoff без reset/stash/force.
Без builds/Actions/Cloud dispatch/workflow edits, raw logs/archives/credentials, PR/issue/комментариев.
Не трогать D0/C1/Part 1/B3 и не продолжать в следующую стадию. CI запускает координатор.
Последняя строка: `READY <sha нового локального Kani-кандидата>`. STOP; это prepared candidate, не CI PASS.
