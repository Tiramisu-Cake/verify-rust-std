# KANI3300 D1-A — анализ A + B-lite, worker 14 (DRAFT / NOT ISSUED)

**Заготовка 2026-11-13; HELD до выдачи координатором после D1-P CI.** Runtime Codex, одна сессия, **Cloud $0**.
Это верификация корректности, не security-работа.
Эта заготовка не разрешает начинать анализ отсутствующих runs, запускать CI или продолжать resource/model fixes.

## Handoff координатора — заполнить при выдаче

- D1-P research commit и CI-only commit/tree на каждом pin: **TBD**.
- Runs/jobs, выбранные P1/P2 cases и actual limits: **TBD**; normal verification NOT_RUN (A+B-lite only).
- Локальный каталог выбранных bounded D1 artifacts + manifest/index/hash: **TBD**.
- Известные missing/truncated/upload errors и координаторский acceptance capture: **TBD**.

Читать `TASK-KANI3300-D1-P.md`, `kani3300/d1p/`, весь аудит @ab7509822453bbf0778da0265c67f51bc08b4755
и brief v2 @cbf575f3aa. Source pins:
R1+skip **56cbc5c4a479bc3fb25310b14fcf279d90581a02**;
R6-02b **405c1f059264d8f7cedeeaa01c6d4ad6867a419e**. Late4f64/R7/R8 не подменяют это сравнение.
Читать только переданные локальные bounded projections/receipts точечно по catalogue/координатам; Python-анализ разрешён.
Не скачивать raw archives/full logs, GCS/Cloud Logging/Actions logs; отсутствующие данные запросить конкретным полем/phase,
без повторного Build/solver. Для данных через Brief сохранять identities/exact/complete/coverage и не обходить интерфейс.

## 1. Сначала приёмка данных, затем сравнение

Проверить source parent → CI overlay/tree → frozen input/root → actual commands/tool binaries → snapshots/summary hashes.
Compiler/runtime/check policy на обоих pins не менялись CI-only overlay; одинаковые scripts/input, singleton units.
Разделить pre-DFCC, непосредственный post-DFCC, actual CBMC input и CBMC preprocessing/symex snapshots.
Проверить in-place file sequence; same filename не означает same model hash. Неверная identity → STOP attribution.
Per phase: setup/rc/signal/watchdog/group/timeout, parser/output caps, artifact completeness; normal и symex-only отдельно.
RawKiB/1048576 → GiB; sampled max, time-v maxrss и interrupted-prefix max не смешивать с завершённым peak.
Green job/exit0 dump/успешный parser не дают semantic verdict. При kill отсутствующий failure tail UNKNOWN.
Составить список доступных/неполных данных; не восстанавливать новые counters/outcomes из исторического run.

## 2. Проверить, что именно сравнивается

Сопоставить init/reset → target/select → аргументные Store/Load → mandatory return0 → normal destination → ensures read.
Для каждого узла дать function/PC/guard и source/GOTO binding; presence не доказательство feasibility/исполнения.
Отметить первую видимую разницу CFG/обязательств: frame, Unsupported, source-validity, protocol, dead path/simplification.
R6-02b известен как дешёвый frameFAIL-контраст, не корректный PFC baseline. P1 legal не переименовывать в expected frameFAIL.
Если normal solver не запускался, новый failure verdict не выводить из inventories или условий dump.
Проверить mapping marked main/private buffer, actual cell targets/extent и writes; pointer value не адрес private cell.
Документировать конкретные расхождения пути, из-за которых resource comparison остаётся NON_COMPARABLE/INCONCLUSIVE.

## 3. Результат A + B-lite

Карта выбранных transfer/init/reset/generated bodies/private assigns и writes; actual `Layout<N>` с N/байтами/битами,
associated type/callsite/owner. Не считать весь служебный state однобайтным из-за scalar MaybeUninit<u8> input.
Проверить parser coverage/denominators: all/ignored/retained видимые SSA categories, guards/assumptions/auxiliary gaps,
VCC prefix duplication, source function/PC, operators, constant/symbolic indices/offsets и известные widths.
Пересчитать top-30 expression roots по ширине и кратности из выбранных bounded данных; unknown widths вынести отдельно.
Exact измерения, type/source-derived сведения и textual heuristics разделить. Fingerprint occurrence ≠ unique DAG node.
Для кандидатов разобрать source/helper → actual GOTO write/guard → retained SSA term → widths/occurrences,
с model/file/record/byte coordinates/hashes. Если retainedness/width/owner не установлены, назвать конкретный разрыв.
Проверить гипотезы symbolic byte-extract/update, finite-array index/update, DFCC write-set/snapshot/backing root,
повторной работы/остаточной helper instrumentation; не выбирать одну только по RSS, usize или числу VCC.
B-lite не измеряет converter cache/allocations/стоимость term; наличие большого root само не устанавливает причину OOM.

## Решение и STOP

Приёмочный результат: хотя бы одна конкретная цепочка
**source/helper → GOTO write/guard → retained SSA term → widths/кратность**,
либо явное **«offender не найден»** с перечислением gaps и пределов анализа.
Найденный кандидат — локализованная гипотеза, не доказанная доминирующая цена; никакого solver/proof credit из dump.
Предложить следующий выбор кратко: одна обоснованная локальная оптимизация на4f64 / отдельно одобряемый C /
proposal fail-closed scope с проверкой реального SmallSort graph. Здесь ничего из этого не реализовывать и не выдавать задания.
Если данных недостаточно, вернуть минимальный запрос к уже сохранённым полям, не начинать новые runs/новый экспортёр.
M3, полный gate, PFC scope claim и ресурсный фикс остаются HELD/NOT_ESTABLISHED.

В g0 **kani3300/d1a/**: INPUTS.json (runs/files/hashes/coverage), DATA-ACCEPTANCE.md,
MODEL-MAP.md, SSA-SUMMARY.json, ATTRIBUTION.md (цепочки/неопределённость), RESULT-KANI3300-D1-A.md (≤35 строк).
Никаких compiler/runtime/tests/goldens/workflow изменений, local cargo/rustc/Kani/CBMC/Miri/builds, CI/Cloud dispatch,
новых representation вариантов/PR/issues/сторонних PR links. Секреты/environment/credentials не читать и не сохранять.
Research [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, stage только d1a/, push g0 без force;
concurrency → handoff без reset/stash/чужих файлов. После анализа STOP.
Последняя строка после отдельной выдачи: `READY <sha research-коммита D1-A>`.
