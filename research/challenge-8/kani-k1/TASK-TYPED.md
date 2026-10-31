# TYPED — typed full-value oracle и проекция witness, пилот механизма и цены

Дата: 2026-10-31. Исполнитель: свежая сессия Codex. Работать только в
`/root/verify-rust-std-kani-typedoracle`, ветка `experiment/kani-k1-typedoracle-20261031`.
База `e0ff82577d`, исходный library tree `c522edd42ae67c385e1ee42a1c4d1bffb611c90b`.
Это замороженный INTEG2 GO / P1-max кандидат, не результат зелёного полного CI.
Первый коммит поверх базы уже сделан координатором:
`6b12002d79b6ccb4ded6c4790b1c592c65d6c591` — только cap, `CAP_USD=88.96`.
Не переносить cap в INTEG2, где остаётся 73.96; не переписывать историю этой ветки.

Окно от фактического T0 сессии: 5 ч, последние 30 мин — закрытие. Cloud Build: ≤ $2 и ≤ 2 сборки
включая неудачные, отменённые и retries; только k1-standard4 / `gcb-e2-standard-4` (4 CPU, 16 GiB).
Перед каждым dispatch: GO, свежий `k1g.sh budget`, собственные spent/reserved по UUID/request_id,
полный envelope в остатке времени и бюджета. Общий agent label не определяет собственный расход.
Все глобальные правила действуют; Evidence Brief и Select/Merge phases к Kani K-1 не применяются.

## Цель и граница результата

Измерить отдельно: (1) проекцию произвольного typed witness в прежний probe; (2) native full-value
count в B вместо bytewise count. Обязательная matched-пара — реальные general/stable u64 N8;
отдельная matched-пара A — PFC actual `bidirectional_merge`, u64 N13. Всё на одном frozen library tree.
Это opt-in пилот перед X6, без N16, миграции семейства и допуска в ordinary/P2.

У A контракт actual callee продолжает использовать generic `probe_count_unrolled`. Меняется только
инициализация witness в PFC fixture. Это «actual PFC с typed witness и generic ensures», а не новый
typed callee contract. Typed assertion в wrapper не заменяет callee `ensures`. Полноценный новый
backend контракта, runtime-selector, clone callee и доказательство клона в этой сессии не делать.
Отсутствие эффекта или TIMEOUT — допустимый итог пилота, не основание ослаблять свойство.

## Владение файлами и исходники

`S = library/core/src/slice/sort/shared/smallsort`.
Разрешено: в `S/verify/merge.rs` только регистрация нового child module под
`#[cfg(kani_smallsort_controls)]`; вся реализация — новый `S/verify/merge/typed_oracle.rs`.
Модуль вправе обращаться к private items родителя, не меняя их определения/visibility.
Не менять существующие helpers, oracle/statics, тела/cfg старых harnesses, `S/verify/network.rs`,
`S/verify/correct.rs`, `S/verify.rs`, runtime `S.rs`, contract attributes и общий oracle backend.
PERM12 владеет только своим новым opt-in блоком в network.rs. correct.rs не меняет никто.
Research-файлы: `research/challenge-8/kani-k1/typed-oracle/`, `RESULT-TYPED.md` и RUN-REQUEST.json.
Tool/lane/pins/toolchain/flags не менять; cap commit — уже существующее исключение координатора.

Перед реализацией прочитать применимые AGENTS/RTK, K-1 request/tool docs и точечные исходники:
merge.rs: probe/matches/count, split direct u64 helpers, u8 N9, merge_length_body/PFC macros;
runtime smallsort.rs: реальные general/stable routes и контракт bidirectional_merge.
Базовые B N8 — `general_direct_u64_n8` и `stable_direct_u64_n8` с const-repeat scratch;
не использовать вместо них старый combined `general_stable_direct_u64_n8` из timeout-диагностики.
Только собственный код: без чтения/переноса решений конкурентов, без ссылок на rust-lang issues.

## Реализация и эквивалентность

1. Native helpers для u64/u8: полный `x == p`, один произвольный p на весь вызов, count на всех
   элементах до/после. Ни `x >> 1`, ни subset/alphabet, ни вероятностный hash не являются oracle.
   Сохранить оригинальные `lt_u64`/`lt_u8` (сравнивают `x >> 1`) и отдельную sortedness-проверку.
2. Проекция p: создать прежний Probe с `p.to_ne_bytes()` в первых 8 байтах для u64 / p в первом
   байте для u8; остальные байты — нули. Писать через исходный raw-static pattern без живой ссылки.
   В proof lemma разрешён произвольный unused tail, чтобы проверить его ненаблюдаемость.
   Не предполагать little endian; u64/u8 не имеют padding и допускают все bit patterns.
   Исходный matches читает ровно sizeof(T) байт. Зафиксировать, что все достигнутые обращения
   к этому probe в выбранной копии имеют тот же T. Не менять p/probe во время real call.
3. Положительный bridge harness: произвольные x64/p64 и x8/p8; после соответствующей проекции
   доказать `matches_value_probe::<T>(&x) == (x == p)` для обоих типов, достижимый completion cover.
   Проверить bounds/valid reads. Объяснить точечно, почему равенство предикатов даёт равенство counts
   и почему проекция покрывает все наблюдаемые значения старого arbitrary 128-byte probe.
   Никаких assume о значениях/совпадениях, axioms, trusted rules или verified stubs.
4. Копии B вызывают исходные реальные тела: general — `small_sort_general`; stable — исходный
   `StableSmallSortTypeImpl::small_sort` и тот же const-repeat scratch48. Any [u64;8], snapshot,
   comparator function item, unwind34, свойства и completion covers сохраняются.
   G8 projected-generic меняет только initializer; G8/S8 native меняют initializer и final count.
   Native-копии проверяют sortedness и native count общим typed checker, без дублирования старого
   generic count в измеряемом postcondition. Parent helpers остаются неизменными baseline.
5. A13: opt-in PFC wrapper на actual `crate::slice::sort::shared::smallsort::bidirectional_merge`,
   как исходный macro/merge_length_body: any [u64;13], отдельный MaybeUninit<[u64;13]> destination,
   `lt_u64`, unwind34, исходные requires/modifies/ensures, completion cover. Единственное изменение
   fixture — typed projection вместо set_value_probe. Не подменять target/body/F или layout.
6. Payload control: real general u64 N2 с тем же comparator, затем `v[0] ^= 1`, затем тот же native
   sortedness/count checker, что у новых B. Flip сохраняет key, обязан дать только count failure
   для подходящего arbitrary p. Cover после real call/flip до deliberate assert; sortedness проходит.
   Не вводить самостоятельный более слабый control-oracle или assume для выбора p.
7. Сразу подготовить u8 native helper и optional matched general N9 копию исходного B
   `general_direct_u8_n9`, с его nonconst fixture и реальным телом; u8 N2 payload control аналогичен.
   Их отсутствие измерения отражать NOT_RUN, а не как измеренную экономию u8.

## Запросы и PRE-BUILD REVIEW

Подготовить manifest, semantic/source audit и оба request до G1. Новые имена ниже идут под
`merge::typed_oracle::`; в JSON — полный namespace `slice::sort::shared::smallsort::verify::...`.
G1: `kind:measurement`, `kani_jobs:1`, `controls:true`, timeout ровно 10 мин на entry, 9 entries:

| Entry | Expect |
| --- | --- |
| merge::general_direct_u64_n8 (исходный) | SUCCESS |
| general_u64_n8_projected_generic | SUCCESS |
| general_u64_n8_native | SUCCESS |
| merge::stable_direct_u64_n8 (исходный) | SUCCESS |
| stable_u64_n8_native | SUCCESS |
| merge::merge_contract_u64_n13 (исходный) | SUCCESS |
| merge_u64_n13_projected_actual_pfc | SUCCESS |
| probe_bridge_u64_u8 | SUCCESS |
| value_corruption_control_u64_n2 | FAILED, только typed full-value count |

Envelope G1 = 9×10+30 = 120 мин, резерв $1.620 при $0.0135/мин.
G2 только условно: тот же frozen library tree, measurement/jobs1/controls:true, 3 entries:
исходный `merge::general_direct_u8_n9`, новый `general_u8_n9_native` (SUCCESS),
`value_corruption_control_u8_n2` (intended FAILED). Envelope60мин/$0.810.
Запуск G2 лишь если actual own spent + reserved + $0.810 ≤ $2, остаётся полный envelope и закрытие.
Сумма полных резервов $2.430 > $2: вторую сборку не обещать. При нехватке G2=NOT_RUN без нарушения
обязательного u64/A пилота. Retry может лишь занять оставшийся slot вместо G2, после delta-review/GO.

Запросы по существующей схеме валидировать штатным Python validator, timeout не сокращать.
У baseline с возможным TIMEOUT expect остаётся SUCCESS: цензурированный результат не успех proof;
aggregate gate=false не стирает отдельные принятые rows. expect_check control сверить по actual
message/file:line/check class frozen source; matcher mismatch не переименовывать в gate=true.
Не добавлять inventory/build ради справки или пустые entries. Все новые items только opt-in.

Source/library commit отдельно от research/request, все коммиты `[skip ci]`, push без force.
Подать `PRE-BUILD REVIEW <published SHA>`: base/cap/library tree, полный diff scope, theorem mapping,
bridge argument, exact entries/controls, заранее определённые метрики и бюджеты; завершить ход,
ждать явного GO. Library tree после GO фиксирован для G1/G2; request SHA/UUID у каждого свои.
Semantic fix требует нового опубликованного delta-review/GO; не запускать исправление автоматически.

## Выполнение, оценка и закрытие

Локально только Git/source, rustfmt-wrapper, штатный Python validator/static checks; без cargo,
rustc/Kani/CBMC и proof runs. Не запускать Actions/CircleCI, submission CI, не менять submission ветки.
Rustfmt для каждого изменённого .rs:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <file>`.
Rust/comments — ≤100 колонок, без истории пилота в library. Не читать ~/.config/smallsort-ci/*.
После dispatch выполнить `k1g.sh watch UUID`, закончить ход; никаких model polling/sleep loops.
После terminal — bounded `summary`, `peaks` с attribution, `status`, `check-tooling UUID <полный cap SHA>`;
нужные строки только через bounded k1g log-grep/log-lines. Не скачивать/читать full/raw logs/archives,
Cloud Logging и обходные GCS-команды. Недостающие поля сообщить UNKNOWN, не выдумывать.
Pin Kani/toolchain/flags и bound files проверять на actual build/request/source SHA. Uninit-checks off
сохранить и указать; B1 bounded evidence не превращать в B2/general proof. Linux jobs1 не равен Mac/jobs3.

Для каждого entry: статус, actual assertion/cover counts, reached covers, verification time, harness
wall time, CBMC/driver RSS по PID, missing/timeout/OOM отдельно. Оценивать matched old/new отдельно
G8 projection, G8 native, S8 native, A13 projection; дополнительные clauses/bridge не прятать в speedup.
TIMEOUT — censored, numeric speedup не считать. Различия F, layout, scratch, stub-target/contract scope
недопустимы; ordinary source projection должна остаться исходной, кроме cfg-off module declaration.
Если positive/bridge/control не приняты — evidence PARTIAL/FAIL, без переноса proof credit.
Если приняты, но эффекта нет — COMPLETE как пилот, рекомендация STOP; это не GO на миграцию/X6.
Даже при эффекте single-run даёт предварительный сигнал: jobs3/Mac, N16 и full typed A backend OPEN.

Вторичный пункт без сборок: ≤30 мин read-only аудит A u8 N5..8 на frozen базе после подготовки
основного пакета или terminal G1, без задержки закрытия. `typed-oracle/A-U8-CONSUMERS.md` ≤50 строк:
actual graph consumers в P1/P2, resolved stub targets/T/F/N, offset/frame/init/probe assumptions;
включить sort8_stable → два sort4 → merge N8, shifted source и dst в одной allocation при disjointness,
сопоставить с standalone A fixtures (scratch48 prefix0 + отдельный dst). По каждому edge — покрыто,
разрыв или UNKNOWN с source coordinates. Direct B proof не объявлять заменой callee theorem.
Не ретирить A, не править матрицы/evidence. При нехватке времени аудит NOT_RUN.

`research/challenge-8/kani-k1/RESULT-TYPED.md` ≤100 строк: T0/deadline, SHA/tree/pins, UUID/request IDs,
own cost/reserved, COMPLETE/PARTIAL, exact properties/control locations, paired metrics и limitations;
явно разделить native B / projected actual A / bridge / unrun u8 / static A-audit.
Передать source audit, manifest и requests; dirty tree отсутствует. Итог `REVIEW REQUEST <SHA>`,
`TYPED ЗАВЕРШЁН`. После маркера не продолжать работу. На deadline — PARTIAL и корректное закрытие
активного build/учёта по штатным controls; ни третьей сборки, ни превышения $2.
