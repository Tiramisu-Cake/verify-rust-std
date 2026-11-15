# S2 qualification и будущая S3 geometry/cost карта

Все строки NOT_RUN. Exact source candidate — CHECKPOINT; base/tool — INPUTS.
S2 не зависит от принятия S1 как proof: P1 остаётся prerequisite для запуска пакета.

## S2 frozen probe

| Root | Body/mode | T/F и harness inputs | Property/admission |
|---|---|---|---|
| sorting_leaf_probe::s2_swap_u8_backing13 | PFC actual swap_if_less, Original | u8/KeyLess<u8>; arbitrary initialized [u8;13], base0, independent a,b∈0..12, включая equality/reverse | existing safety+frame и proposed exact conditional transfer; covers taken/unchanged/equal/endpoints/useful return |
| sorting_leaf_probe::s2_sort13_u8_verified_swap | actual sort13_optimal Original; only swap Replace verified | та же пара и [u8;13], N13, base0, arbitrary full bytes | activation + sorted/full-count по owned S1 Snapshot, meaningful return/duplicate/unsorted covers |

Consumer не PFC sort13: S2 измеряет тело с отдельным checker. S3 actual sort13 attrs/PFC
ещё нужны для его использования как summary. Swap PFC должен иметь proposed attrs,
consumer должен выбрать этот exact monomorphization; старые FnPtr leaves не substitutes.
Есть 13²=169 ordered position pairs, не только45 использованных network edges.
Все256 значений каждого входного byte symbolic независимы. Никаких order assumptions.
Ни panic_on_ord_violation, ни abort/error paths не stubbed. Не требовать callback covers
в replaced calls. Ошибка requires до summary havoc не считается expected named checker fail.

В этом пакете НЕТ assumed-summary cost arm: verified arm остаётся pending до callee PASS.
Если координатор позже выберет §5 diagnostic arm, это отдельный opt-in source/manifest,
без formal credit; текущий weak-summary negative не является таким arm.

## S3 требуется квалифицировать отдельно

| Leaf | Используемый finite domain | Backing/topology и initialized ranges | Dependencies |
|---|---|---|---|
| swap | u8/KeyLess, all relative positions в действительном prefix; a=b и a>b | S2 separate backing13/base0 сохранён; добавить backing32, symbolic interior base o и a,b<32-o; только две initialized позиции читаются | actual original body; frame остальных bytes |
| sort9 | u8/KeyLess; region len9..12, width9 | backing32, symbolic o с o+region_len<=32; все live v initialized; prefix9 меняется, tail и outside frame неизменны | matching swap32 |
| sort13 | u8/KeyLess; region len13..17, width13 | S2 backing13 плюс backing32 symbolic o; initialized input, active prefix13 | matching swap13/32 |
| insert_tail | u8/KeyLess p1..16; Cell/KeyLess p1..15 fallback; NonCopyByte/KeyLess p1..15 general | backing32/v или backing48/scratch, symbolic begin offset с begin+p<capacity; initialized только [begin,begin+p] и sorted первые p; outside живые sentinels отдельно | actual finite body, guard/drop нормального возврата |
| sort4 | u8 и NonCopyByte, их KeyLess; width4 | general source backing32/v → destination backing48/scratch с offsets0,h; внутри sort8 дополнительно src+4 и scratch+4; destination uninit допустим | actual original body; no copy/frame claim для arbitrary F |
| sort8 | u8 и NonCopyByte, их KeyLess; width8 | source v32 (offset0,h); dst и temp в ОДНОМ scratch48, ranges disjoint; offsets ниже; source initialized8, dst/temp не читаются до writes | qualified sort4 и merge8 same-allocation |

Stability/rank-id/extra-UB theorem здесь не заявлен: только full-byte count и порядок.
Это **план domain**, не verdict. NonCopyByte не превращать в Copy ради fixtures;
Cell::get не подменять raw byte projection без отдельного review. Возвраты generic
inactive не доказывают эти instances. Дополнительные u128/oversized/ZST/type rows —
отдельная qualification, u8 не поглощает их. Existing old roots/controls не удаляются.

Для каждого N16..32, h=N/2: sort8(source=v+0,dst=scratch+0,temp=scratch+N) и
sort8(source=v+h,dst=scratch+h,temp=scratch+N+8). Внутренние merge8 имеют34 разных
(scratch source offset, scratch output offset): (N,0),(N+8,h). Схема two separate
arrays не покрывает этот same-allocation случай. Вне них merge нужен scratch→v и
v→separate network stack scratch. Worker15 владеет merge proof, не W11.
Source/dst/temp active ranges sort8 pairwise disjoint в ЭТИХ callers; более общий
alias-domain не утверждается. Actual source sort8 не пишет v; frame разрешает dst8/temp8.

Stable external scratch может быть произвольной legal большей длины. Harness backing48
сам по себе НЕ закрывает такие allocations/offsets. Нужен отдельный prefix-locality
аргумент/квалификация или узкий disclosed domain/stub guard; не выдавать конечную
матрицу offsets за универсальный allocation theorem. Файл geometry.json хранит ровно
перечисленные offsets, не AST/MIR binding и не автоматическое CI admission.

## Оценка стоимости и будущий receipt

- Swap: два reads snapshot + точный transfer O(1), havoc только2 cells; loops/root13
  для explicit frame, unwind15. Это предположение о размере формулы, не wall/RSS замер.
- Sort13:45 swaps, 90 element write targets до coalescing, 104 symbolic input bits.
  S1 checker:12 adjacent comparisons +13×13 count iterations (338 equality tests,
  повторения на duplicates допустимы); snapshot13. Unwind15 сохраняет все bounds checks.
- Sort9:25 swaps; checker8 adjacent +81 count iterations. Sort4 делает5 comparisons;
  sort8 — два sort4 + merge8; count work16/64 соответственно. Цена pointer checks,
  havoc, extraction и solver может доминировать; эмпирической секунды/байта пока нет.
- Insert_tail: p<=16, до16 comparison/moves, active len<=17, full checker O(289).
  Никаких33 separate per-N roots/solver sweeps. S3 рассматривает symbolic p/offset и
  необходимые topology roots; split допустим лишь по конкретному finding.

Будущий coordinator batch: jobs1 сначала; organizer flags clean0aac, --no-assert-contracts,
object-bits12, extra-UB OFF. Сначала P1 и exact leaf+controls; consumer cost только после
qualification. Для каждой строки сохранить source/tree/tool/backend/config/contract hash,
T/F/length/offset/topology, selected PFC/Replace target и native original exit.
Измерить compile/extraction/model/havoc/checker/backend phases по доступности; если фаз
нет — UNKNOWN, не вычитать из total догадкой. Wall, driver RSS, backend RSS и измеренный
concurrent aggregate RSS раздельно, единицы KiB/bytes явны. Proposal gate из плана:
600s/root и aggregate<=6GiB, запас до лимита; фактический budget/dispatch не выдан.
KANI_JOBS=2, shards, macOS/Linux matched arms — только после P2, не текущая сессия.
NOT_RUN/timeout/infra error/control mismatch не PASS. No local runtime estimate.
