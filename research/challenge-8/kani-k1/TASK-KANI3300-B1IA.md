# KANI3300 B1I-A — перепривязка fixtures после Uninit Quick, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна сессия, **Cloud $0**; параллельно D0 воркера 14.
Решение B в силе: flat storage сохраняется, raw_eq model — зависимость выпуска; не откатывать и не сужать scope.
Прочитать `PLAN-KANI3300-PART1-B.md`, `TASK-KANI3300-B1I.md` и `kani3300/b1i/{NOTES.md,REVIEW.md,TEST-MANIFEST.json}`
@ research `54b7b7fbc4`. Это продолжение B1I, не отдельный standalone B1R3.
Это верификация корректности, не security-работа.

## Факты координатора — сохранить с provenance

Uninit Quick **`43196180814`**, source **`dc5f5a406749a73f1c3192e0b5338441e79508bb`**,
CI checkout **`b5f87a7e92105965b719b71bb2f4741c14f0816c`** (его parent — source; diff только `.github/workflows/`).
Fmt/build/Clippy PASS; expected uninit **111 passed / 7 failed / 2 ignored**; kani Uninit **22/0**,
ui **14/0**, mem-init-reinstrumentation **1/0**. Это selector counts, не число закрытых proof obligations.
Сведения переданы координатором; новых запусков/независимой проверки этой стадией ещё нет.

| Упавший selector | Сообщённое наблюдение | Корректная интерпретация |
|---|---|---|
| `maybe-uninit-initialized` | Прежний raw_eq legal failure | Открытый D0/model blocker, не новая B1I-регрессия |
| `shim-plain`, `shim-seeded` | Ждали bodyless Shim, получили `calls through function pointers` | До shim guard не дошли; это FnPtr boundary |
| `shim-shadow-argument-only-plain`, `-seeded` | Unsupported layout `(std::mem::MaybeUninit<u16>,)` | Tuple-обёртка, не direct shadow-argument shim guard |
| `shim-shadow-return-only`, `-seeded` | Uninit-read `u16` в `transmute_neo<MaybeUninit<u16>,u16>` | Closure call — Item; возвращённый uninit затем assume_init: настоящий UB, не shim-guard failure |

Прочие существующие controls прошли по сообщению координатора. По разобранным исходам **production-регрессий не выявлено**;
не называть весь Quick зелёным или shim acceptance закрытым. Шесть новых failures — неверные contracts/goldens fixtures.
Review заранее отметил tuple-lowering gap. Не дописывать отсутствующие property IDs, actual MIR или доказательство пустых seeds.

## Рабочая область

Kani **`/root/kani-fix-3300-p1b1`**, ветка **`fix/kani-3300-p1-b1`**, clean HEAD = source SHA выше;
production parent **`cdb439b0a4c36e9e595019895ab803230f332941`**, исходный tree `085bea5cda2df66a5cb4f72410fe124aa816c90b`.
Проверить состояние; при расхождении STOP, без reset/stash. B1I production diff сохранить **без изменений**:
правки этой стадии — только `tests/expected/uninit/unresolved-calls/` и новые research results.
Не менять исходные `kani3300/b1i/` документы: это исторический snapshot; актуальную привязку записать отдельно.

## Что сделать

1. Записать `CI-OBSERVATIONS.md`: source/CI/research SHA, run/status/counts, actual diagnostic из таблицы,
   source-reported vs independently read evidence и перечень оставшихся gaps. Точные MIR/property данные брать только
   из curated отчёта/targeted evidence координатора; если их нет — UNKNOWN и конкретный запрос, без raw/full-log обхода.
2. **FnPtr pair:** исправить комментарии, golden и manifest по реально наблюдённому FnPtr diagnostic.
   Имена/описание больше не должны обещать bodyless Shim. Можно сохранить paths либо осмысленно переименовать pair;
   сохранить bodies/положительный scalar результат и plain/seeded различие. Не считать этот pair новым shim coverage.
3. **Tuple argument pair:** сохранить как точный negative неподдержанного compound tuple layout, переименовать
   harness/описание/при необходимости paths соответственно. Golden должен требовать именно tuple-layout Unsupported,
   а не произвольную FAILURE. Не добавлять tuple/MU layout support и не менять closure ABI ради прежнего ожидания.
   Direct-shadow Shim argument guard остаётся непроверенным: эту ветвь не закрывает ранний layout barrier.
4. **Item return pair:** сохранить существующий uninitialized-return + assume_init как genuine uninit negative,
   переименовать shim-guard harness/описание и golden в соответствии с Item/uninit-read. Не заменять отрицательный
   пример на initialized и не удалять reached read. Добавить отдельные **initialized companions plain/seeded**:
   тот же noinline generic/closure call, `MaybeUninit::new(7u16)` и scalar `assume_init() == 7` → ожидаемый SUCCESS.
   Не использовать array equality/raw_eq. Цель пары — сохранение true/false через поддержанный Item return0, не shim ABI.
5. Plain/seeded controls сохранять; seed — прежний поддержанный copy/cast над ordinary bytes, без зависимости от raw_eq.
   Само наличие seed helper не доказывает target/relevance execution. Для новых companions и всех изменённых negatives
   обновить source/golden hashes, per-harness expected named properties, actual/expected kind и admission path.
   Новые версии имеют **NOT_RUN** status до rerun; старый diagnostic хранить с прежними SHA/path/harness, не переносить
   observed status на переименованный/изменённый candidate. Counts после новых companions пересчитать по inventory, не гадать.
6. `COVERAGE-GAPS.md`: отдельно реальные bodyful Shim argument-only и return-only, bodyless/generated Shim,
   genuine FnDef resolver Err и необходимые entry/read property bindings. Сохранить четыре compiler-input specifications
   из B1I как **неисполненные specifications**, а не тесты PASS. Описать минимальный следующий compiler/MIR control;
   не строить новый framework и не обещать закрыть ветвь очередным source FnOnce примером без actual kind/ABI binding.
7. `CI-REQUEST.md` для координатора: шесть исправленных selectors + initialized companions, одиночные/JSON property
   проверки, actual MIR/call kind/tuple form, entry loads→operand checks→Unsupported и plain/seeded activation там, где
   требуется acceptance. После targeted — существующий Uninit Quick точного нового SHA; не запускать самому.
   Known raw_eq failure перечислить отдельно, expected final Part 1 остаётся blocked. Любой иной новый FAIL/ICE или
   пропавшая read/load property → STOP и отдельный production-repair task, без изменения checks/goldens ради зелёного CI.

## Статика, review, результат и STOP

`git diff --check`, source `-D warnings` audit; разрешённая rustfmt-обёртка
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --config-path rustfmt.toml`.
Проверить `git diff dc5f5a4067 HEAD -- kani-compiler library cprover_bindings` пуст, весь stage diff ограничен tests.
Bounded Luna High review изменённых test contracts/expected outcomes и manifest; без повторного полного semantic review
неизменённого production и без вложенной делегации. Test/golden rebindings не дают новых runtime результатов.

Один локальный test-fix commit поверх source SHA, нейтральное сообщение без `[skip ci]`, author/committer
`Tiramisu-Cake <igkharin@gmail.com>` через `git -c`; Kani **не пушить**.
В g0 `research/challenge-8/kani-k1/kani3300/b1ia/`: `CI-OBSERVATIONS.md`, `NOTES.md` (≤30 строк),
`TEST-MANIFEST.json`, `COVERAGE-GAPS.md`, `CI-REQUEST.md`, `REVIEW.md`, `RESULT-KANI3300-B1IA.md` (≤20 строк).
Manifest связывает прежний observed input и новый expected candidate, не переписывает исторические claims/evidence.
Research commit `[skip ci]`, тот же author/committer, stage только `kani3300/b1ia/`, push g0 без force;
при concurrent/non-fast-forward — handoff координатору, не включать чужие файлы.

Никаких локальных cargo/rustc/Kani/CBMC/Miri/сборок, Actions/Cloud dispatch/workflow edits, raw logs/archives/credentials,
PR/issue/комментариев и ссылок на сторонние PR. Не трогать D0/source a0, raw_eq/flat/layout/transfer/Move production,
не начинать B1R3/C1/M0 или иной следующий этап. После статического handoff STOP до rerun координатора.
Последняя строка ответа: `READY <sha нового локального test-fix коммита Kani>`. Это готовность пакета, не CI PASS.
