# KANI3300 S3-COMPAT — ordinary contract regressions — выдана стадия CC2 (2026-11-13 → worker14)

2026-11-13. Это верификация корректности, не security-работа. **Выдана только стадия CC2.** CC1 принят координатором; CC3 — отдельной выдачей.
Это последовательность CC1→CC2→CC3: координатор выдаёт **одну стадию на одну session**, не весь план автоматически.
Local cargo/rustc/Kani/CBMC/Miri/builds запрещены;
Cloud $0, push/CI/caps — только координатор после отдельного GO. Никаких raw downloads, публикаций или nested agents.

## База и invariants

CC1 base: C2 **fef9e0f38c0c645027f20223a562c7008969d9a9**; read-only reference `/root/kani-fix-3300-compose1`.
Research g0 `experiment/kani-k1-kani3300g0-20261111`, findings `d992c289a1a0000ea5a46b2d26e5f0385d55e327`.
Прочитать `PLANNER-S3-COMPAT-REVIEW.md`, `kani3300/mode-findings/FINDINGS.md`, original S3 `58497d98d0`,
mode-boundary sources и существующие `tests/json-handler/uninit-contract-oracles` на C2.
Source BASE каждой следующей стадии — только reviewed результат предыдущей, exact SHA/tree фиксирует координатор.
CC2: isolated clone `/root/kani-fix-3300-cc2` (git clone из /root/kani-fix-3300-cc1, ветка fix/kani-3300-cc2 от CC1 b2e1a392ad27bd21758473bc208ff66c2d7d0405); reference clones read-only.
Dirty/wrong pin → STOP без reset/stash. Исходные findings/failed exports/ORACLES не переписывать задним числом.

Quick43434557435 и8 oracle PASS — прежний набор; новые mode findings не аннулировать и не считать покрытыми этим Quick.
Сохранить S3 actual registration/discarded-body handling для nonrecursive путей, M1 masks, A3 pairing/Move/false,
whole-state private assigns, marker diagnostics, default solver/checks и per-test object-bits12 policy.
Не исправлять модель через runtime/DFCC exemptions, asserts→assumes, global default b или фильтрацию bool/receiver checks.

## CC1 — остановить статический cycle явным Unsupported

Цель: реальный cycle не вызывает stack overflow и не возвращает недоаппроксимированный graph как успешный результат.
Sites: `points_to/points_to_analysis.rs::run/apply_regular_call_effect` и delayed_ub caller.
Различать внутрипроцедурный MIR fixed point (уже есть) и повторный interprocedural run по active instance (его guard нет).
Tracked key должен отражать exact monomorphized instance и фактическое выбранное body/override; объяснить контекст.
Repeated active call — detected cycle, не «любой повторный вызов»; законченные repeated calls в DAG остаются допустимы.

Вернуть отдельный error/unsupported result с bounded cycle path и привязать его к **этому entry root** через штатный Unsupported.
Нельзя на recursion возвращать empty/initial/partial graph, усекать depth или тихо брать source panic вместо override.
Partial summaries не кэшировать/не переносить в другой root. Нельзя кэшировать input-dependent analysis только по Instance
и переиспользовать с другим initial graph без доказанного monotone summary/fixed point.
Поддерживать правильное очищение active context на всех return/error paths, separate root contexts и discarded bodies.
Ошибка одного root не должна abort-ить сборку verify-std/другие roots; missing export/collection crash не целевой исход.
Если штатный per-root Unsupported нельзя внедрить без большего дизайна — STOP, не заменять его fatal compiler error.

Synthetic/source controls: self-cycle, mutual cycle, diamond/repeated nonrecursive callee, два initial graphs,
override/discarded distinction, A→B→A с исходным active stack, два независимых roots в обоих порядках.
Real CI-request: original `recursive_check` из mode-boundaries и его ordinary/SimpleCheck companions отдельно,
capture-free legal recursive-mode control и nonrecursive P1. Для cycle root ожидается targeted Unsupported с cycle reason,
без stack overflow; остальные исходы фиксируются полно и не объявляются прошедшими, если остаются bool/layout failures.
Full recursive/SCC support и общая mode qualification **не входят** в CC1. Существующая документированная граница сохраняется.

## CC2 — обычные scalar/ref slots и copies, без bless pointees

Цель: исправить реальные missing entry/copy setters, открытые новым корректным alias route, а не удалить checks.
Перед patch составить SETTER-MAP для `initialized:bool`, сохранённого `&bool` capture slot и wrapper/upvar копий:
source MIR operation → actual storage/type/mask → entry/normal edge/copy → read CheckRef.
Получать нужные selected MIR/model поля только через coordinator CI request, если source данных недостаточно.
Не выводить last setter/witness из одного property description; UNKNOWN сохраняется до привязки.

Обоснованно инициализировать **data bytes конкретного storage slot** известного корректного scalar/ref value.
Инициализация callee parameter не должна скрывать плохое чтение caller: сохранить source-read obligations и paired negative.
Покрыть normal-return destination и aggregate/upvar copy там, где карта действительно выявила пропуск;
не вставлять unconditional entry initializer для любого T.
Reference/raw-pointer slot — только representation bytes; referent/neighbor/caller MU/union holes не становятся true.
Padding остаётся вне data mask; direct MU/flat slots/ordinary union сохраняют existing transfer/false rules.
Типы с вложенным MU/union не flatten-ить как полностью initialized aggregate; unsupported type не превращать в all-true.
Если требуется новый transfer protocol или смена lifetime/Move model — STOP с отдельным дизайном.

Отдельные regressions, изолирующие slot дефект от layout: normal scalar/ref parameter через обычный helper и
capture-free contract path, initialized=true/false, normal return, copy/move of reference slot.
Отрицательные controls: valid MU/raw storage с hole, на который указывает initialized reference/raw pointer;
callee/body действительно доходит до read и отвергает именно payload. Не создавать invalid typed bool до целевой операции.
Generated capture controls сохранить для CC3, не засчитывать их Unsupported как PASS bool initialization.

## CC3 — layout обычных nonzero upvars

Цель: нужные ordinary/Assert/SimpleCheck captures scalar/ref больше не получают closure-layout Unsupported.
`ty_layout.rs::data_bytes_for_ty`: реальные monomorphized upvar types + rustc FieldsShape offsets/order,
recursive masks, правильный current_offset и padding. Не делать vec![true;closure_size] и не заменять Closure на tuple
с придуманным layout/order. API internal-rustc codegen_ty_closure — ориентир; bridge rustc_public проверяется на текущем pin.
Сохранить zero-size closure case и остальные coroutine/foreign/unsupported guards.
Captured MU/union by value требует сохранения false/preserve masks; если имеющаяся рекурсия выдаёт UnionAsField,
это прежняя явная граница, не основание bless payload. Plain reference to MU может иметь поддержанный pointer mask,
но отдельный pointee hole обязан оставаться проверяемым.

Контроли: bool true/false capture, два ref fields к initialized/MU values, mixed scalar+ref с padding,
разный logical/physical field order, ZST+nonzero, by-reference/by-value MU/union отдельно, nested ordinary captures.
Для boundary tests нужен actual reached layout request; отсутствие запроса/ранний иной Unsupported — nondiscriminating.
Если нужный исходный legal companion требует broader aggregate/union support, сообщить отдельный release blocker;
не менять исходный predicate/captures так, чтобы спрятать regression.

## Приёмка финальной композиции CC1–CC3

1. Original `replace_ordinary` и `replace_simple_check` должны пройти без bool/&bool/layout FAIL;
   initialized true/false branches и полезные covers/read paths достигнуты, не отрезаны Unsupported/assume.
2. Сохранить original inputs и добавить capture-free legal companions + отдельные captured regressions.
   Для original RecursiveCheck допускается explicit detected-cycle Unsupported, пока mode не заявляется;
   ordinary реально recursive root тоже не может crash/дать underapproximated SUCCESS. Если он получает новый Unsupported,
   это BLOCKED для заявленного ordinary scope, а не успешная mode-exclusion проверка. Нужны отдельный sound summary/SCC
   или явное решение владельца о границе после representative verify-std inventory; этим TASK сужение не разрешается.
3. Replace observation сохранить с полным набором5 failures до нового исполнения. Два u8 checks на havoc result
   не объявлять ложными и не требовать их исчезновения. Нужен отдельный total-predicate Replace diagnostic companion,
   если требуется изучить сам mode; это не означает его общую квалификацию.
4. P1/legal-pair ordinary+PFC/lawful-modifies, все8 strong oracle cases, C03 и S3 ensures left/right-hole const-HOLE controls
   остаются на прежних source-bound оракулах. Bool fix не должен удалить local/delayed Check или разрешить hole.
5. Exact per-harness complete failure sets: P2 read Check+CheckRef, frame-negative именно user *outside,
   no extra frame/protocol/Unsupported/invalid-value failures на поддержанных roots. Mixed root orders и singleton соответствуют;
   никаких partial cached bodies/graph/seed leaks. Для отрицательного read outer assertion может быть UNREACHABLE,
   для legal positive полезный outer assertion должен быть достигнут и SUCCESS.

## CI и результаты каждой стадии

Worker не запускает CI. Каждая CCn отдаёт свой bounded CI-REQUEST с exact roots/source/binary/flags/limits,
object-bits12 и normal solver/slicing/checks. Не повторять H1 matrix/расширять бюджет без coordinator GO.
Сначала build/typecheck, затем целевые regressions. Crash/signal/cap/missing export — не expected negative PASS.
Полные JSON inventories + actual model binding, selected fields/trace при необходимости, original exit/signal/RSS KiB;
никакого raw-download обхода или нового tracing framework. Exact crash cause остаётся provisional до cycle evidence.
На общей reviewed голове — один Quick + сильные JSON suites; затем M3/full/platform/SmallSort gates отдельно.
До закрытия ordinary regressions публикация Part1 **NO-GO**, даже при прежнем зелёном Quick.

Research результаты раздельно `kani3300/s3-compat/cc1/`, cc2/, cc3/: INPUTS, DESIGN, CONTROL-MAP,
TYPE-AUDIT, CI-REQUEST, REVIEW и RESULT≤35строк. До CI statuses NOT_RUN/UNKNOWN; не переписывать mode-findings history.
Одна стадия — reviewed source commit(s) от зафиксированной головы предшественника, без CI overlay/source push;
author/committer через `-c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`.
Research `[skip ci]`, stage только свой directory, без push/выдачи последующей стадии.
Если нужен полный interprocedural SCC, blanket callback policy или новый protocol, STOP и отдельное решение владельца.
После будущей выдачи конкретной CCn: `READY <source-sha>`; сейчас **DRAFT / NOT ISSUED**.

## Итог CC1 (координатор)
CC1 b2e1a392a принят: quick run 43442603191 — expected 162/0 (вкл. points-to-cycles), kani 22/0, ui 14/0, script 1/0, json-оракулы ok.
mode-boundaries: recursive_check/recursive_ordinary → явный Unsupported «interprocedural cycle» (crash устранён);
replace_ordinary/simple_check и recursive companions — ложные bool/&bool (цель CC2). Артефакты: /root/kani3300-h1-ci/cc1-art/.
