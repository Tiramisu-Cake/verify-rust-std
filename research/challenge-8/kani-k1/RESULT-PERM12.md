# PERM12 — PRE-BUILD REVIEW, evidence PARTIAL

Стадия: source/request package подготовлен; ожидается GO Claude Code, сборок нет.
Окно: консервативный T0 guard 2026-10-31 12:40 UTC, deadline17:40 UTC (20:40 MSK).
Первый записанный clock12:46:38 UTC; точное время начального prompt не записано.
Guard выбран раньше начала измеренного времени; окно не продлевается от GO.
Последние30min — закрытие; dispatch должен вместить полный envelope до17:10 UTC.
Лимиты: USD2, максимум2 builds включая retry/failed/cancelled; собственные spent/reserved=0/0.
Учёт и состояние GO: [perm12/session.json](perm12/session.json), UUID пока отсутствуют.

База: `e0ff82577d` (полный SHA в manifest), frozen library tree:
`c522edd42ae67c385e1ee42a1c4d1bffb611c90b`.
Cap SHA: `92d89e7a8bca371e9b4a48175d08322d3f24a2e4`, CAP_USD=88.96.
Source SHA: `e01ed338d746601dd12eb50d937805db32f085dd`.
Candidate library tree: `521e2b4bd57c83c321f03445ff10f8d12c93fb24`.
Ветка: `experiment/kani-k1-permtwelve-20261031`; cap/history INTEG2 не менялись.

Exact manifest: [perm12/manifest.json](perm12/manifest.json), SHA256 запросов/bound files включены.
G1 request_id=`perm12-g1-measurement-20261031`: measurement/jobs1/controls=true/timeout10min.
Семь entries: original, trace_unpartitioned, FF, FT, TF, TT, value_corruption_control.
Все baseline/cases expect SUCCESS; control expect FAILED с явной проверкой count location.
G2 request_id=`perm12-g2-jobs3-20261031`: diagnostic/jobs3/controls=true/timeout10min, четыре cases.
Запросы: `perm12/g1.request.json`, `perm12/g2.request.json`; root RUN-REQUEST равен G1.
Оба подготовлены до G1 и приняты штатным Python validator; build UUID пока нет.
G1 request SHA — публикуемый research/request commit этого пакета (маркер PRE-BUILD REVIEW).
G2 dispatch/request SHA будет отдельным коммитом при условной установке G2.
Source SHA отделён от research/request commit; после GO library tree фиксирован.

Изменение library: только appended cfg(kani_smallsort_controls) mod perm12 в network.rs.
Ordinary projection после удаления нового opt-in модуля побайтно равна frozen source.
Старые imports/items/macros/cfg и resolved dependency sources сохранены; новые private names
не входят в scopes старых items, экспорта/glob imports нет. runtime/oracle/correct/merge не менялись.
[Static audit](perm12/source-audit.json) = STATIC_PASS; это не AST/MIR binding или machine proof.
Предписанный rustfmt-wrapper --check edition2024/config и git diff --check прошли.
Локальных cargo/rustc/Kani/CBMC/proof runs и submission/Actions/CircleCI запусков не было.

[Correspondence](perm12/COVERAGE.md): FF/FT/TF/TT — первые два dynamic comparator results.
Состояние phase0->1->2 saturating, не alias с v/pre/probe; до результата volatile reads actual refs.
После префикса на КАЖДОМ invocation свежий any bool; unpartitioned начинает с phase2.
Один fixture: any[u64;12], snapshot, arbitrary probe, real insertion begin9, full-value Eq counts.
Нет sortedness/alphabet/value restrictions, assume, stubs, trace-array/call cap/раннего stop.
Каждый normal trace имеет уникальный case; ошибки до второго результата также исследуются.
Симуляция воспроизводит исходные reads/branches/moves/count; обратное включение также описано.
Новый closure F/instances явны: source equivalence не даёт тождество Kani instance или baseline credit.

Unwind25 сохранён: три tails9/10/11; максимум30 comparisons, индивидуальный insert loop<=11,
count/movement loops<=12. Actual safety/unwinding assertions должны быть приняты G1.
Movement cover стоит после real sort до flip; end cover общий. Source witnesses описаны,
observed достижимость пока UNKNOWN для каждого case/control, постоянных case-bit covers нет.
Control: real insertion, v[0]^=1, cover перед общим check_permutation, arbitrary probe сохранён.
Intended count failure: `network.rs:1518`, assertion; phase:1536, flip:1542, cover:1543.
Matcher=`This is a placeholder message` по frozen lane precedent; actual message/class/location
до G1 UNCONFIRMED. Mismatch сохранится в historical request/gate, исправления evidence запрещены.

Predeclared gate: [perm12/GATE.md](perm12/GATE.md). Все4 cases SUCCESS, необходимые asserts/covers,
control принят только на count, correspondence принят; сумма case VT<=600s.
Если baseline SUCCESS и сравним, сумма строго меньше лучшего успешного baseline VT.
При baseline TIMEOUT numeric speedup=NA; <=600s — заранее выбранный потолок стоимости.
Нужны сумма harness wall, максимум case VT/wall и RSS; недостающая метрика => UNKNOWN.
Пока все7 per-entry statuses/asserts/covers/VT/wall/RSS = NOT_RUN/UNKNOWN/NA.
Сумма4 cases и максимум = NA; исходное proof obligation OPEN; savings не установлены.

G1 envelope100min/USD1.350; G2 envelope70min/USD0.945, сумма USD2.295>USD2.
Текущий optimization gate UNKNOWN; jobs3 NOT_RUN, admission OPEN; evidence PARTIAL.
G2 только после G1 PASS и fresh global/own budget, time/envelope/closing checks.
Если все cases приняты, но дорогая сумма: proof COMPLETE / optimization STOP отдельно.
Неполный partition => PARTIAL; отсутствующий baseline proof не заменяется pilot credit.
Пилот B1 bounded, не B2/general insertion theorem, Linux16GiB не доказывает Mac/fullCI.
Автоматического расширения P1/P2/submission, дробления8/16 или удаления baseline нет.

Следующий шаг: PRE-BUILD REVIEW опубликованного research/request SHA, завершить ход, ждать GO.
До GO dispatch запрещён заданием; после dispatch использовать watch UUID и завершить ход.
После terminal: bounded summary/peaks/status и check-tooling UUID полный cap SHA;
сверить actual build/request/source identities, pinned flags/tools, failed assertion и covers.
Окончательные UUID/request SHA/cost/verdict будут записаны после разрешённых стадий.
