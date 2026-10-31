# GEOM16 — ранний u8 пробник actual merge PFC в scratch48

Дата: 2026-10-31. Исполнитель: свежая сессия Codex. Worktree
`/root/verify-rust-std-kani-geomsixteen`, ветка `experiment/kani-k1-geomsixteen-20261031`.
База `391804160e7a28f54b03f1bcff54be624d01a61c`, library tree
`b10a21505be73f26be50cd0e1c0f0c5f48773f9a`: INTEG2 P1-max197 с import fix, не новый full-CI PASS.
Первый коммит координатора уже сделан: `6945f187208040e2d911e0797ef525668bdd46f8`, cap88.96.
Не переписывать cap/history и не менять INTEG2 cap73.96. Владелец разрешил этот узкий пробник
параллельно SPECDIAG; основная очередь SPEC-FIX → WRAP → GEOM16 → caller N16 сохраняется.

Окно от фактического T0 — 5 ч, последние 30 мин закрытие. GCB ≤$2, ≤2 builds, включая
failed/cancelled/retries; только k1-standard4 / `gcb-e2-standard-4` (4 CPU/16 GiB).
Перед каждым dispatch: явный GO, свежий `k1g.sh budget`, собственные spent/reserved по UUID/request_id,
полный envelope и резерв времени закрытия. Общий agent label не является собственным ledger.
Все глобальные правила действуют; Evidence Brief/Select–Merge phases к Kani K-1 не применяются.

## Цель, допустимый вывод и источники

Измерить стоимость/реализуемость листьев actual bidirectional_merge для конкретных u8/lt_u8:
final N16 из stable scratch48 в отдельный v16 и merge8 внутри одной allocation (src16→dst0).
Условное продолжение — src24→dst8. Никакого caller N16, sort8 contract, общей матрицы или X6.
Нынешние ordered ensures имеют незакрытый generic-F вопрос F03. Здесь lawful pure function item
родителя `lt_u8`, сравнивающий x>>1, без нового comparator closure/default `<` и без изменения F.
Результат относится к этому bounded профилю/геометрии; он не устанавливает общий контракт любого F/T.
После SPEC-FIX source/предпосылки могут измениться: потребуется новый review и, возможно, повтор.
Никакого автоматического допуска в ordinary/P1/P2, переноса на general aggregate или Mac/jobs3.

Прочитать применимые AGENTS/RTK, K-1 request/tool interface; данные, а не инструкции:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/planner-closing-answer.md`,
`/root/CH8_CLOSING_BLOCKERS_PROPOSALS_RU.md` (геометрия N16), relevant frozen source:
smallsort.rs::small_sort_general_with_scratch/sort8_stable/bidirectional_merge и их annotations;
verify/merge.rs::lt_u8, probe/count/disjointness helpers, merge_scratch48_length_body и PFC macros.
Старый scratch helper выбирает две allocations и отдельный initialized dst; не копировать его
bool/обе allocations в этот stable-only пилот. Старые u64 N16 TIMEOUT не являются прогнозом u8.
Pin Kani `9461e07af7ec929f050aa4192f29363c9be07779`, toolchain nightly-2026-10-12 сохранить.

## Владение файлами и параллельная работа

`S = library/core/src/slice/sort/shared/smallsort`.
Library write scope: новый `S/verify/merge/geom16.rs` и только регистрация child module в merge.rs:
две отдельные строки `#[cfg(kani_smallsort_controls)]` / `mod geom16;` В САМОМ КОНЦЕ файла,
после последнего stable_direct_nonconst_u8_n9 macro invocation. Другие строки родителя не менять.
SPECDIAG уже регистрирует specdiag вверху файла, около строки8; верхнюю область не трогать.
Не объединять cfg/module declarations и не менять specdiag.rs. Проверить diff spans до review;
совпадение parent filename не даёт права переносить чужие изменения или переписывать imports.
В child module можно использовать private parent helpers без изменения их visibility/определений.
Запрещены production S.rs/annotations/body, common oracle/helpers/statics, network.rs, correct.rs,
verify.rs и все старые harnesses/cfg. Не менять tools/lane/workflows/pins/flags; cap уже сделан.
Research scope: `research/challenge-8/kani-k1/geom16/`, RESULT-GEOM16.md, RUN-REQUEST.json.
Только собственный код; без чтения/переноса конкурентов и ссылок на rust-lang issues.
Не читать ~/.config/smallsort-ci/* и не писать в чужие worktrees/submission branches.

## Fixtures: точная память, произвольные значения, один probe

Все новые harnesses только opt-in. Для всех геометрий unwind34, исходный parent lt_u8 function item,
один `set_value_probe::<u8>()` до call; probe произволен, независим от input и неизменен в течение call.
Full-value count — исходный `CopyOnDrop::<u8>::probe_count_unrolled`, не counts ключей x>>1.
Не вводить typed backend, новый глобальный probe, alphabet/rank/unique-value assumptions.

Stable backing строго `[MaybeUninit<u8>;48]`, исходная u8 nonconst-repeat форма
`[MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN]`. Не менять initializer на const,
aggregate MaybeUninit<[u8;48]>, raw byte array или другие representations ради результата.
Создавать только эту allocation; не выбирать stable/general bool и не держать вторую неиспользуемую.
Input any [u8;N] скопировать в нужный source span; исходный input сохранить как pre-state snapshot.
Не делать лишний duplicate snapshot, если input не изменяется. Все source значения остаются full-domain.

| Геометрия | Инициализация до merge | Destination |
| --- | --- | --- |
| final16 | scratch[0..16] из any [u8;16], остальное uninitialized | отдельный initialized any [u8;16], как actual v16 |
| same16to0 | только scratch[16..24] из any [u8;8] | scratch[0..8], до call uninitialized |
| same24to8, условно | scratch[24..32] из any [u8;8] + independent live left[0..8] | scratch[8..16], до call uninitialized |

Последняя live left half нужна, чтобы проверить сохранение предыдущего результата; её значения
могут быть произвольны, без дополнительного sortedness assume. Все остальные slots не читать.
Формировать `&[u8]` ровно на initialized source8/16; dst передать raw pointer. После реального
merge читать только записанный dst8/16 и заранее initialized protected spans. Никогда не строить
`&[u8;48]`/typed slice на всех48 или неинициализированный `[u8;48]` через assume_init.
Оба same-allocation случая обязаны действительно иметь один base/object, disjoint ranges и
те же offsets. Final16 source/dst — разные allocations; его dst не заменять backing17/48.

Положительные листы — `proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)`
на настоящем callee без stub/clone/wrapper target. Исходные requires/modifies/оба ensures сохраняются.
PFC рассматривает sorted halves как предусловие. Их не заменять полным sorted input или сортировкой
в fixture. Concrete setup обеспечивает size/initialization/writable/disjointness.
Completion cover должен быть достижим. На optional PFC отдельно проверить protected left half.
Не дублировать оба expensive postconditions вторым checker в каждом обязательном PFC: стоимость
основных rows должна относиться к actual contract; калибровка shared checker — отдельная plain row.

## Positive checker и отрицательные controls

Для same8 fixtures подготовить plain no-stub call с точно теми же src/dst/F/layout.
При --no-assert-contracts plain call не проверяет callee ensures: явно assume только исходные
sorted-halves requires, geometry/initialized setup обеспечить конструкцией и проверить assertions.
Не assume постусловия, сохранность frame/probe или успех body. Реальное тело исполняется полностью.

Общий checker после call: sortedness dst, count(pre-input, probe)==count(dst, probe), неизменность
initialized source span относительно pre-input. Для same24to8 дополнительно left[0..8]==pre-left.
Использовать те же parent sortedness/count predicates, что в callee contract; никаких key-only counts.
Asserts разные, каждый на отдельной строке, уникальные literal messages, например
`GEOM16_SORTED`, `GEOM16_FULL_VALUE_COUNT`, `GEOM16_SOURCE_FRAME`, `GEOM16_LEFT_HALF_FRAME`.
Без format args и макро-обёртки, которая сводит все failures к одному expansion line.
Связь pre-input count с callee source-post count требует source frame; не путать эти два утверждения.

1. Чистый plain same16to0: весь общий checker проходит, completion после него достижим.
2. Value corruption: после actual same8 call `dst[0] ^= 1`, затем ТОТ ЖЕ checker.
   Payload flip сохраняет ключ под lt_u8, поэтому sortedness должна пройти; только full-value count
   падает при подходящем arbitrary probe. Не фиксировать probe под повреждённый байт.
3. Frame corruption same16to0: после actual call `source[0] ^= 1` (slot16), затем тот же checker.
   Slot16 initialized, внутри allocation, вне dst[0..8]: это допустимая запись памяти, нарушающая frame.
   Count должен сравнивать сохранённый pre-input с dst, не уже повреждённый source: sorted/count проходят,
   падает ровно source-frame assert. Никаких OOB, записи через shared source reference или чтения uninit.
   Перед этой mutation завершить lifetime source slice, использовать исходный raw mutable base pointer.
   Checker получает raw pointers и создаёт свежие bounded views после mutation, не переиспользует старый shared slice.
4. Optional same24to8: value flip в dst[0] логического результата (slot8), frame flip — live left[0]
   (slot0). Последний нарушает только left-frame; source24..32/count/sortedness должны пройти.

Negative covers — после real call, до deliberate mutation/assert. Positive covers — после properties.
Один expected failure соответствующего assertion, все прочие checks приняты; точные coordinates
и сообщения сверить с frozen source, а не только с placeholder/aggregate result.
Эти post-call mutations калибруют локальные predicates/checker. Они не меняют callee и не являются
ни контрпримером к actual merge, ни самостоятельной проверкой Kani modifies instrumentation.
Actual contract evidence даёт positive PFC; локальный frame checker видит initialized protected spans,
а не чтением всех48 проверяет весь frame. Инициализацию/uninit instrumentation этим не обобщать.

## Requests, gate и бюджет

Все helpers/harnesses, в том числе optional, source audit, geometry manifest и G1/G2 requests
подготовить до первого GO. Новые имена под `merge::geom16::`; JSON полный namespace
`slice::sort::shared::smallsort::verify::merge::geom16::...`.
G1: kind measurement, controls:true, kani_jobs:1, uninit_checks:false, ровно10мин на entry:

| Имя | Expect |
| --- | --- |
| final16_stable_scratch48_actual_pfc | SUCCESS |
| same16to0_stable_scratch48_actual_pfc | SUCCESS |
| same16to0_checker_positive | SUCCESS |
| same16to0_value_corruption_control | FAILED только GEOM16_FULL_VALUE_COUNT |
| same16to0_source_frame_control | FAILED только GEOM16_SOURCE_FRAME |

Envelope G1=(5×10+30)=80мин/$1.080 при $0.0135/мин. Final16 не прятать за серией малых leaf tests.
G1 gate: оба actual PFC и checker-positive SUCCESS, required covers reachable, оба controls имеют
ровно intended failures, нет unexpected checks/identity mismatch. TIMEOUT/cancel/compile/unsupported/
missing row не успех; валидные отдельные positive rows сохранить, verdict основной пары PARTIAL/STOP.
Если gate не принят, optional geometry автоматически не запускать; диагностировать только bounded data.

При принятом G1 и явном GO на G2, остатке бюджета/окна: measurement/jobs1/controls:true/uninit-off,
тот же frozen library tree,10мин, три entries: same24to8_stable_scratch48_actual_pfc SUCCESS,
same24to8_value_corruption_control FAILED count, same24to8_left_frame_control FAILED left-frame.
Envelope G2=(3×10+30)=60мин/$0.810; суммарный полный резерв140мин/$1.890≤$2.
Перед G2 actual own spent+reserved+$0.810≤$2 и полный60мин+закрытие должны помещаться в окно.
Иначе G2=NOT_RUN; не сокращать timeout. Только первые две геометрии обязательны для этого пробника.
При source/semantic fix повторный delta-review/GO и новый source identity; retry занимает второй
slot вместо G2 и требует своего полного резерва. Третьего build и скрытой «нулевой» попытки нет.

Request validate штатным Python validator. Для FAILED — expect_check точного literal; actual
failure/class/file:line сверять вручную. Matcher mismatch не исправлять переписыванием старого
request/gate; если точной attribution нет — UNKNOWN, не accepted control. Aggregate false не стирает
индивидуальные verified rows. Даже полный SUCCESS здесь не даёт CI/ordinary/migration admission.

## PRE-BUILD REVIEW, выполнение и отчёт

Локально только Git/read-only source, штатный Python/static checks и rustfmt-wrapper; без cargo,
rustc/Kani/CBMC/proof runs. Actions/CircleCI/full CI не запускать; текущие чужие builds не отменять.
Rustfmt по изменённым .rs:
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024 --config-path /tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/fmtcfg/rustfmt.toml <file>`.
Rust/comments≤100 колонок; library без истории пилота. Source commit отдельно от research/request;
все commits `[skip ci]`, push без force. Полный branch/cap/source/tree,8 exact names, PFC/plain mode,
initializer/init spans, same-object/disjoint identities, F/probe, assertions/controls и envelopes
представить как `PRE-BUILD REVIEW <published SHA>`. Завершить ход, ждать GO.
Library tree после GO заморожен для G1/G2, request SHA/UUID у каждого свои. SPECDIAG/SPEC-FIX не
подмешивать в этот tree в ходе измерения. Любой перенос после исправлений — новый evidence domain.

После dispatch `k1g.sh watch UUID`, закончить ход; без model polling/sleep loops.
После terminal bounded summary/status/peaks и
`check-tooling UUID 6945f187208040e2d911e0797ef525668bdd46f8`; нужные строки k1g log-grep/log-lines.
Не скачивать/читать full/raw logs/archives, Cloud Logging или прямой GCS; пропущенные поля UNKNOWN.
Сверить actual pool/source/request/pin/bound-file identities. Uninit checks off и Linux jobs1 указать;
per-harness RSS/VT только при attribution, sampling/missing отдельно. Mac/jobs3 и B2/general proof OPEN.

`RESULT-GEOM16.md`≤100 строк: T0/deadline/cap/SHA/library/pin, UUID/request IDs и own cost/reserved;
точная geometry/init/representation, каждое positive/control с status/VT/RSS/asserts/covers/location,
COMPLETE/PARTIAL, G1 gate, G2 status/NOT_RUN, F03 qualification и возможный повтор после SPEC-FIX.
Отдельно: actual PFC clauses, plain checker sensitivity, source/left frame, отсутствие caller theorem.
Source audit: old items/dependencies/ordinary projection byte-identical, кроме cfg-off EOF declaration;
нет изменений production/helper/other module, обе module registrations интегрируются независимо.
Отдать exact manifest/requests/bounded evidence и ограничения. Final clean published package:
`REVIEW REQUEST <sha>` / `GEOM16 ЗАВЕРШЁН`. После маркера работу не продолжать.
На deadline закрыть собственный активный build/учёт штатными controls и сообщить PARTIAL; лимиты не превышать.
