# PERM12 — полный partition comparator traces для real insertion permutation u64 N12

Дата: 2026-10-31. Исполнитель: свежая сессия Codex. Работать только в
`/root/verify-rust-std-kani-permtwelve`, ветка `experiment/kani-k1-permtwelve-20261031`.
База `e0ff82577d`, исходный library tree `c522edd42ae67c385e1ee42a1c4d1bffb611c90b`.
Это INTEG2 GO / P1-max frozen candidate, не зелёный full CI. Первый коммит поверх базы уже сделан:
`92d89e7a8bca371e9b4a48175d08322d3f24a2e4` — координатор поднял только `CAP_USD=88.96`.
INTEG2 с cap73.96 не трогать, историю cap не переписывать.

Окно от фактического T0: 5 ч, последние 30 мин — закрытие. Cloud Build ≤ $2 и ≤ 2 сборки со всеми
retry/failed/cancelled; k1-standard4 / `gcb-e2-standard-4` (4 CPU, 16 GiB). Общий global cap не выдаёт
каждой сессии весь остаток. Перед каждым dispatch: GO, `k1g.sh budget`, собственные spent/reserved
по UUID/request_id, полный envelope и резерв закрытия в оставшемся окне. Agent label общий.
Применимы глобальные инструкции; Evidence Brief и Select/Merge phases здесь не используются.

## Цель и исходное обязательство

Проверить, снижает ли полное разбиение на 4 случая стоимость блокера
`network::insertion_permutation_u64_n12`, без ограничения u64, alphabet или исходного массива.
Baseline берётся неизменным из frozen tree: any [u64;12], snapshot, произвольный u64 probe,
actual `insertion_sort_shift_left(&mut v, 9, ...)`, volatile reads настоящих аргументов comparator,
произвольный bool на каждом сравнении, full-value count и covers движения/завершения, unwind25.
Предположения sorted prefix в permutation theorem нет. Сохранить именно эту более широкую область.
Новые случаи — opt-in, без правки ordinary/P2, runtime или допуска в submission.

## Владение и подготовка

`S = library/core/src/slice/sort/shared/smallsort`.
Library write scope: только новый `#[cfg(kani_smallsort_controls)] mod perm12` в конце
`S/verify/network.rs`. Внутри — adapter, общие fixture/checker и harnesses; parent private helpers
можно вызывать без изменения определения/visibility. Старые items/imports/macros/cfg не менять.
Не трогать `S/verify/merge.rs`, `S/verify/correct.rs`, `S/verify.rs`, runtime `S.rs`, oracle backend.
Новый typed oracle module принадлежит TYPED; correct.rs не меняет никто.
Research scope: `research/challenge-8/kani-k1/perm12/`, `RESULT-PERM12.md`, RUN-REQUEST.json.
Tool/lane/Kani/toolchain/flags не менять; cap commit уже дан координатором.

Прочитать применимые AGENTS/RTK, существующий K-1 request/tool interface, network.rs:
volatile_reading_less, count_matching_values, prefix_unchanged, insertion_permutation_fixed/macro;
runtime smallsort.rs: insertion_sort_shift_left и insert_tail целиком, включая ранние return.
Только собственный код, без решений конкурентов и ссылок на rust-lang issues.

## Четыре случая и доказательство полноты

1. Разбить по результатам первых ДВУХ comparator invocations всего actual call:
   FF, FT, TF, TT. Это префиксы динамического trace, а не двух заданных пар элементов.
   Comparator в каждом invocation сначала выполняет те же volatile reads actual `a` и `b`,
   затем возвращает заданный bit для первых двух вызовов, далее свежий `kani::any::<bool>()`
   при КАЖДОМ вызове. Часть после префикса никогда не переиспользует один общий bool.
2. Состояние — private phase, saturating на 2, не alias с v/pre/probe. Никакого конечного
   короткого массива bool, лимита числа calls, index wrap, assume или раннего прекращения sort.
   Три tail равны 9,10,11; insert_tail может сканировать до v_base, максимум сравнений
   9+10+11=30, а не 6. Unwind25 исходного harness — per-loop bound, не лимит comparator calls;
   сохранить его, отдельно проверить loop bounds/unwinding assertions.
3. На normal return все три insertion выполнены и каждая вызывает comparator хотя бы раз,
   значит первые два bool существуют. Каждый trace имеет единственный двухбитовый префикс;
   объединение 4 случаев — все исходные trace, после префикса все продолжения произвольны.
   Ошибки до второго comparison не исключать: их пути также проверяются cases; completion
   phase==2 можно assert после normal return, нельзя assume до/во время sort.
4. Формально описать симуляцию: для любых input/probe и nondet choices исходного comparator
   выбрать case первых двух результатов, затем воспроизвести весь оставшийся trace в adapter;
   actual values/reads/moves/count совпадают. Обратно каждый adapter trace разрешён исходным
   arbitrary comparator. Case selection независим от input/probe, не требует sortedness/порядка.
   Новый closure F явно отметить: source-level эквивалентность не означает тождество Kani instance.
   При невозможности обосновать correspondence — STOP/OPEN, без закрытия исходного proof obligation.
5. Все 4 wrapper используют один fixture: any [u64;12], snapshot, arbitrary u64 probe, actual
   insertion begin9 без stub/clone; исходный shared full-value count_matching_values и covers
   движения/завершения. Не заменять Eq на equality key (`>>1`) и не добавлять sortedness assume.
   Нужны unwind25, все safety/unwinding/count assertions и достижимые covers каждого case.
   Cover постоянного case bit сам по себе не является проверкой невакуозности.
6. Тем же adapter подготовить unpartitioned trace baseline: phase с начала равен 2, каждый
   invocation volatile-reads actual refs и возвращает fresh any bool. Это отделяет влияние
   closure/codegen от собственно partition. Остальные fixture/checker/covers те же.
7. Отдельный negative control на unpartitioned adapter: real insertion, затем `v[0] ^= 1`,
   затем ТОТ ЖЕ full-value count checker. Cover после flip до deliberate assert. Ожидается
   count failure при некотором arbitrary probe; других failures/OOB/unwind не должно быть.
   Не фиксировать probe, не делать control-specific count и не заменять им positive cases.

Объединение всех 4 принятых cases и обоснованная симуляция — обязательны для рекомендации о
покрытии исходного bounded theorem. Три успешных случая из четырёх дают только PARTIAL.
Пилот не доказывает общий insertion sort и не устанавливает автоматически machine proof credit
неизменного baseline, если он TIMEOUT. Сохранять эту разницу в итоговом отчёте.

## Requests, цена и STOP

Подготовить все helpers, source audit, coverage argument, exact manifest и G1/G2 requests до G1.
Новые entry names ниже — `network::perm12::...`, JSON использует полный namespace
`slice::sort::shared::smallsort::verify::...`.
G1: kind measurement, jobs1, controls:true, timeout ровно10мин, ровно 7 entries:

| Entry | Expect |
| --- | --- |
| network::insertion_permutation_u64_n12 (исходный) | SUCCESS |
| insertion_permutation_u64_n12_trace_unpartitioned | SUCCESS |
| insertion_permutation_u64_n12_ff | SUCCESS |
| insertion_permutation_u64_n12_ft | SUCCESS |
| insertion_permutation_u64_n12_tf | SUCCESS |
| insertion_permutation_u64_n12_tt | SUCCESS |
| insertion_permutation_u64_n12_value_corruption_control | FAILED, только full-value count |

G1 envelope100мин/$1.350 = (7×10+30)×$0.0135.
Все baseline expect SUCCESS по request schema; возможный TIMEOUT — цензурированное измерение,
не принятый proof. Aggregate gate=false не стирает индивидуально проверенные rows.
expect_check сверить с frozen source actual message/file:line/class; matcher mismatch оставить
явным, не переписывать исторический request/gate. Ровно intended count failure, covers достижимы.

До G1 зафиксировать инженерный gate: все 4 cases SUCCESS, все необходимые asserts/covers,
control принят, correspondence обосновано; сумма verification time четырёх cases ≤600с.
Если baseline SUCCESS с сопоставимым verification time, сумма должна быть меньше лучшего из
успешных original/unpartitioned baseline. Это gate стоимости пилота, не доказанная универсальная
граница производительности. Дополнительно показать сумму harness wall time, максимум case и RSS;
если метрика отсутствует, gate UNKNOWN, положительный вывод об экономии не делать.
При TIMEOUT baseline численный speedup NA; порог ≤600с — заранее выбранный предел цены partition.
Если случаи не закрыты или сумма превышает gate — STOP по механизму/цене, не дробить дальше,
не менять values/alphabet/unwind и не уходить автоматически в 8/16 cases.

Только если G1 прошёл этот gate, G2: kind diagnostic, kani_jobs:3, controls:true, те же 4 cases,
timeout10мин, source/library tree тот же. Envelope70мин/$0.945.
Проверить завершение всех cases и все covers, active processes/реальные CBMC+driver peaks,
OOM/exit/missing по отдельности. Общий пик не доказывает пик каждого процесса или наличие 3 CBMC.
G2 только если actual own spent + reserved + $0.945 ≤ $2 и весь envelope/закрытие входят в окно.
Полные резервы G1+G2=$2.295 >$2: обе сборки заранее не гарантируются. При нехватке G2=NOT_RUN;
jobs1 proof/cost verdict сохранить, jobs3 admission OPEN. Retry только вместо G2 в оставшемся slot,
после delta-review/GO; не увеличивать бюджет и не запускать третий build.

## Review, выполнение и результат

Локально только Git/static source, штатный Python validator и rustfmt-wrapper; без cargo/rustc,
Kani/CBMC/proof runs. Не запускать Actions/CircleCI/submission CI, не менять submission branches.
Для каждого изменённого .rs:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <file>`.
Rust/comments ≤100 колонок, без истории пилота в library; ~/.config/smallsort-ci/* не читать.
Library/source commit отдельно от research/request; все `[skip ci]`, push без force.
`PRE-BUILD REVIEW <published SHA>`: exact source/library/cap, diff ownership, trace correspondence,
новый F, loop bounds, control location, manifest/requests, gate и envelopes. Завершить ход, ждать GO.
Library tree после GO фиксирован для G1/G2; отдельные request SHA и UUID. Semantic fix — только
после опубликованного delta-review/GO. Не подменять пропущенную/неудачную stage старым evidence.

После dispatch `k1g.sh watch UUID`, закончить ход и ждать штатного wakeup; без model polling.
После terminal: bounded summary/peaks/status и `check-tooling UUID <полный cap SHA>`; точечные
log-grep/log-lines через k1g при необходимости. Без full/raw logs/archives, Cloud Logging, прямых
GCS обходов. Missing/contradictions — UNKNOWN и точные ограничения, а не SUCCESS по одному exit code.
Сверить actual build/request SHA, pinned Kani/toolchain/flags/bound files; uninit-checks off сохранить.
Linux16GiB jobs1/jobs3 не доказывает Mac/fullCI. B1 bounded proof не превращать в B2/general result.

`research/challenge-8/kani-k1/RESULT-PERM12.md` ≤100 строк: T0/deadline, base/cap/source/tree,
manifest, UUID/request IDs, own cost, per-entry statuses/asserts/covers, VT/wall/RSS, сумма 4 cases
и максимум отдельно; partition completeness/simulation, negative failure coordinates, gate PASS/
STOP/UNKNOWN, jobs3 VERIFIED/NOT_RUN, evidence COMPLETE/PARTIAL. Source audit: ordinary projection
и resolved dependencies исходных items сохранены; новое F/adapter и proof-credit граница явны.
При валидном полном partition, но дорогой сумме: proof COMPLETE, optimization STOP — не успех цены.
Никакого автоматического расширения P1/P2 или удаления baseline. Static audit A u8 делает TYPED,
этой сессии его не дублировать. Передать exact готовый пакет и оставшиеся вопросы координатору.
Финал `REVIEW REQUEST <SHA>`, `PERM12 ЗАВЕРШЁН`; после маркера работу не продолжать.
На deadline PARTIAL с закрытием активного build/учёта через штатные controls; лимиты не превышать.
