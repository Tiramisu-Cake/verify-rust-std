# KANI3300 T1 — DRAFT, bounded context trace

Предложение координатору, не выданное задание и не GO. Runtime Codex; новый worktree/ветка, окно, owner/phase/ledger и exact published packet задаются при выдаче. T0 ничего не регистрирует и не резервирует.
Цель: различить relevance/constant-shadow gap и cache/order/другой механизм контекстного отказа IndexRange. Результат — локализация или UNKNOWN; исправление production не входит.
Основание: DESIGN-TRACE.md; planner cmp4/PLANNER-AFTER-CMP3-ANSWER.md §3–6 и внешний PLANNER-3300-SCOPE-ANSWER.md §6,8.

## Подготовка до разрешённых экспериментов

1. Реализовать отдельную diagnostic delta поверх CMP2; production patch оставить byte-identical. Никаких изменений library/harness/model, новых checks/reads/assume/seed и исправления constant transfer.
2. Host-only collector: function-filtered MIR/relevance/points-to/MemoryInitOp, root order и shared-cache provenance; bounded noncompact CBMC counterexample projection и op→helper/symbol mapping по DESIGN-TRACE. Не вызывать transformer дополнительно ради trace.
3. Tooling от KT2: строго opt-in schema/env/args, sidecar → `summary.json.diagnostic_trace`, новый bounded `trace-field` reader; не использовать `native.tests` для verify-std. Не читать raw logs/archives, включая локальные копии.
4. До dispatch: статические checks и existing preflight, meaningful synthetic/service tests tooling; отдельный independent tooling review и review диагностической Kani delta на immutable identities. Test failures/ошибки подготовки сначала исправлять статически, не тратить Build на тот же дефект.
5. Review должен проверить отсутствие semantic изменений, сохранение исходных exits/checks/controls, recorder opt-out, bounded allocation/output, footer/omissions и identity binding; opt-in emission-equivalence сохранить в машинном отчёте, если её нельзя установить статически — не заявлять заранее.
6. Зафиксировать полный diagnostic commit/patch SHA256, combined patch SHA256 и expected applied tree; tooling SHA/recipe hash, запросы, generated flags и artifact schema. Точные pins ещё не существуют: не подставлять T0 SHA как готовую реализацию.
7. Подготовить два запроса и exact-packet coordinator review/GO, стоимость/slots/deadline проверить существующим coordinator. Cloud только после отдельного разрешения T1; прочие клоны read-only, Actions/PR/issues запрещены.

## Общие immutable inputs

- Library commit `2121ff2d08d50d412c834760af925b202a1d8c01`, tree `919cc3e2dc5fb19ea6e7f7be761914b949160a41` (присутствует в T0); один и тот же для A/B.
- Fixture `library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs`, SHA256 `bd6d51c7ad634644d5e8fc16b539cd84b2eedb6101d52692c4d7d0fb3545e8a6`; всю library tree и adapters сверить, не только этот файл.
- Kani base `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain `nightly-2026-10-23`.
- Production CMP2 reference `b1f0105c0390fb55081e3d186fa286d23867b585`; production-only patch `kani3300/u4/kani-uninit.patch`, SHA256 `46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`; production applied tree `d356238999ab436ddc1dd7ffa845b0db214aa53e` до diagnostic delta.
- Tooling base `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` плюс отдельно reviewed extension; одинаковые tooling/diagnostic delta/recipe для A/B.
- `kind=diagnostic`, `controls=true`, `uninit_checks=true`, `inventory=false`, `runner=gcb-e2-standard-4`, `kani_jobs=1`, harness timeout `3m`, exact matching, прежний production output mode.
- Diagnostic options одинаковы: proposed `KANI3300_TRACE_DIR` (producer output), `KANI3300_TRACE_FILTER` (literal name patterns), `--keep-temps --no-slice-formula`, pass-through `--cbmc-args --trace` последним; без concrete playback/compact trace. Tooling должен явно валидировать и записывать effective argv/env, а не принимать произвольный shell.
- Не включать полный MIR/dot debug dump для обычного чтения; filtered sidecar берёт нужные стадии из уже доступных bodies. Связь actual Assign с константой пока UNKNOWN.

## Exact selectors

Каждое имя ниже дополняется префиксом `slice::sort::shared::smallsort::verify::uninit_probe::`; порядок списка запроса не считать actual codegen order.
A: девять roots из `kani3300/cmp3/RUN-REQUEST.json`, без изменения их expectations:

| # | Suffix | Expected diagnostic outcome |
| --- | --- | --- |
| 1 | cmp3_index_range_len | SUCCESS requested; проверить воспроизведение observed uninit FAIL |
| 2 | cmp3_polymorphic_sized_len | SUCCESS requested; сохранить каждый actual failure |
| 3 | cmp3_polymorphic_unsized_len | SUCCESS requested; сохранить каждый actual failure |
| 4 | cmp3_manually_drop_unsized_len | SUCCESS, проходящий contrast |
| 5 | cmp3_into_iter_len | SUCCESS |
| 6 | cmp3_into_iter_next | SUCCESS |
| 7 | small_sort_general_with_scratch_u8_n4 | SUCCESS |
| 8 | pincheck_calibration_uninit_read_u8 | FAILED, check `Reading from an uninitialized` |
| 9 | pincheck_calibration_init_read_u8 | SUCCESS |

B: четыре roots из `kani3300/cmp4/cmp2/RUN-REQUEST.json`:

| # | Suffix | Expected diagnostic outcome |
| --- | --- | --- |
| 1 | cmp3_index_range_len | SUCCESS |
| 2 | cmp4_index_range_len_runtime | SUCCESS |
| 3 | cmp3_manually_drop_unsized_len | SUCCESS |
| 4 | pincheck_calibration_uninit_read_u8 | FAILED, check `Reading from an uninitialized` |

Payload filter: target roots step1/step4, `crate::array::kani_cmp3` adapters, actual `PolymorphicIter::len`, `IndexRange::{zero_to,len}` names/instances; выбрать по actual qualified names, не вручную угаданным mangled symbols. Header — все unit roots/order/stubs; bounded witnesses допускают origin/cache-writer из любого root.
Не урезать shadow lineage counterexample по function filter: нужны все Set/Copy/Get/reset/retarget и argument/return события до step1 failure, даже из иных функций.

## Предлагаемые cap и stop

- Не более двух Cloud Builds: A один раз, затем B один раз; без retries, третьего clean run и последующего fix/replay. Изменение delta/fixture между A/B делает сравнение несовместимым.
- Предлагаемый общий cap **$1.40**, reserve A `(9×3+30)×$0.0135=$0.7695`, B `(4×3+30)×$0.0135=$0.5670`, всего **$1.3365**; остаток **$0.0635** не разрешает новую попытку.
- Это прежняя стандартная overhead-модель, не гарантия достаточности trace compilation: до GO пересчитать recipe/deadline/full timeout envelope; если не помещается в cap, сообщить границу, timeout/controls не урезать. Cloud $0 до GO.
- Если A не даёт ожидаемый contrast, B остаётся полезен для проверки общей library; если A выявляет broken diagnostics/identity/control/preflight, второй Build не отправлять вслепую: остановить зависимую работу с UNKNOWN, cap не расширять.

## Evidence и приёмка диагностики

Только штатные Brief/summary и reviewed bounded reader; отсутствие Brief/trace сообщать без raw fallback. Existing `native`/`native-field` остаются truthful compiletest интерфейсами, их HTTP/отсутствие report не заменять fabricated results.
Предлагаемые selectors после реализации reader: `k1g.sh trace-field BUILD manifest 0 20`, `... functions 0 20`, затем `... functions.0.relevance 0 20`, `... events 0 20`; фактические keys/schema должны быть зафиксированы в review. Продолжения только по returned `next_start`.
Producer bounds: ≤512 records/256KiB/compiler invocation, record≤2048 bytes, per-run aggregate≤1MiB; reader page≤20 records/12000 bytes. При превышении сохранить original outcomes, state PARTIAL/OVERSIZED, omission counts/coverage и UNKNOWN причинности, не выдавать пустую trace за полную.
Manifest: build/head/request SHA, library tree/fixture, base pin, production+diagnostic/combined hashes и actual applied tree, nightly, tooling/recipe, effective Kani/rustc/CBMC argv, filter/schema, content hashes и stage/root/instance identities. Any source-stage-target mismatch → trace INVALID для causal credit.
Runtime records: property ID, ordinal/call frame, op/source/generated site/symbol, concrete pointer/object+offset/range/data mask, tracked object/offset/R before/after, Get result и transfer/retarget lineage. SUCCESS шага4 имеет static CFG/relevance, runtime snapshot UNKNOWN без существующего witness.
Поддержка (а): совместимые A FAIL/B SUCCESS; actual Constant assignment; полная lineage того же Get/object/data byte показывает пропущенный требуемый R write и R=false, объяснённый origin/relevance context. Same span/FAIL alone недостаточны.
Опровержение (а) для наблюдаемого отказа: actual assignment иное или доказан другой объект/корректный write с иной последующей причиной. Cache/order defect фиксировать отдельно, без автономного production repair.
Невоспроизведение, Unsupported, timeout, missing values/hidden steps, partial/ambiguous mapping, сломанные controls или identities → UNKNOWN. Covers после намеренного UB не дают credit; сохранить все failures, число/omissions, first failed step и original exits.
Итог: краткий RESULT с A/B roots/status/checks/covers, bounded evidence coordinates/identities, выбранной гипотезой либо точной границей UNKNOWN, расходом и следующим предложением. Independent B1/B2 credit NONE; KANI3300/compound/native/upstream acceptance этим не закрывается.
T1 завершается отчётом/review marker и стоп; production fix, новые Builds и PR — только отдельное задание.
