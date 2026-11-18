# Время, стоимость и четыре оставшихся workflow attempts

**PROPOSED_NOT_IMPLEMENTED / NOT_RUN.** Reference only: ledger943d67bd487ea3ab33e5e77a0d0dfe8453a83532, item2=10/14, total39/43, четыре workflow attempts. Ничего не reserved/charged/changed. Реальный accounting/GO — coordinator. Отсутствие RESULTS не compilefail/refund; reported root/backend interruption не даёт оснований назначить charge0.

| Вариант | Workflow / jobs / Rust compilations | Worst-case plan после setup | Решение |
|---|---|---:|---|
| A nine singleton, defer both general32 | 1 /1 /9 | 9×720+180+240=6900s | Предпочтение, conditional W11 |
| B all11 с теми же slots | 1 /1 /11 | 11×720+420=8340s | Не помещается в7500/7560/8100; не выдавать за текущий budget |
| C all11, ужатый prefix | 1 /1 /11 | 9×600+2×720+420=7260s | Возможная отдельная reviewed profile: prefix child480, full general32 child600, compile180 внутри каждого.240s margin до7500; выше риск цензурировать полезные prefix roots |
| D A, затем отдельный full general32 attempt | 2 /≥2 /≥11 суммарно | Второй setup до1800s и свой controlled group | Только явный quota tradeoff root, не preferred r5 |
| E reduced-domain general32 | Не выделено | Стоимость UNKNOWN; новый source/domain/profile | Отдельная задача, новые IDs/nonvacuity/controls; не тихая замена full-domain pair |

A имеет nine child walls600s =5400s, внутри них nine compile subcaps180s =1620s; их НЕ складывать как7020. Nine pre/post120s =1080s: slots6480, overhead180 и cleanup240 дают6900. Остаток до group/controller7500 =600s, до proof step7560 =660s, internal8100 =1200s. Эти slack не разрешают автоматический extra root/retry. Monotonic phase origin общий на schedule; nested wrappers не получают каждый новый8100s.

Сохраняются setup1800s (общий installation + stock-tool build≤min(900,remaining setup)), job10800s, proof step7560s и запас900s для finalization/upload/reserve:1800+7560+900=10260, job slack540s. Внутренний phase8100 не разрешает перекрыть более короткий step7560. Output16MiB/1MiB per-stream, export8MiB per-invocation и total artifact256MiB должны иметь отдельную aggregate accounting:9 bounded exports не повод умножить общую artifact quota. Compact packer обязан сохранить точные omissions/completeness и completed receipt hashes. Setup/compilation/service time не становится free из-за того, что это один workflow.

35.5s reported compilation одного grouped invocation не прогнозирует nine singleton costs.9×35.5=319.5s — лишь иллюстрация repeated work при ложном допущении равной стоимости, не expected runtime или reused budget. Binding-safe baseline предполагает9 compilations; cap1620s для них содержится в5400 child wall, с возможными UNKNOWN. Для11 invocations compile subcap sum1980s; в C child wall sum5520s. Нельзя сохранить900s compile+600s backend каждому из11 и при этом заявить fit в старый7500s group.

Matrix jobs могут оставаться одним workflow attempt по task counting, но nine independent jobs повторяют setup/tool installation/build до9×1800s и потребляют runner capacity; per-job180min не выдаёт9× полномочий или общий оплаченный envelope. Parallel jobs=2 при target6GiB каждый не дают6+6+2GiB безопасного host budget: нужны реальные simultaneous aggregate/cgroup metrics и review. Поэтому A serial1, без matrix, без параллельного compile. Отдельные workflow invocations стоят отдельные attempts.

Full unchanged general32 — отдельные singleton invocations с полной неизменённой семантикой и exact bindings; они могут иметь diagnostic-assumed статус и снова RSS/timeout UNKNOWN. Smaller cap на известном weak root чаще повторяет censored observation; информационный смысл должен иметь различающую гипотезу. Preferred A не тратит на него ещё один attempt.

Reduced-domain варианты можно обсуждать как input alphabet{0,1,2} приN32 либо меньший явно названныйN, сохраняя full-value checker. Они требуют новых root IDs/request/oracles/covers, отдельной scope/domain карты, activation/reachability/nonvacuity/negative controls и новой source authority. Input restriction сама не ограничивает havoc outputs assumed summaries; более узкая summary relation — дополнительное semantic изменение, а не бесплатный speedup. Domain/cardinality/N/model/summary изменения не эквивалентны full-u8/N32 и не квалифицируют assumed consumers. Никаких silent checker weakening, новых axioms или theorem lifting без proof.

| Capacity scenario | Четыре slots | Условие |
|---|---|---|
| Q1 preserve all stages | r5=1; S3=1; S4=1; matched final/contingency=1 | Одна S3 должна закрыть все нужные leaves; одна S4 все выбранные classes. Оба условия не установлены |
| Q2 proof-first | r5=0; S3=2; S4=1; final=1 | Root решает отказаться от дополнительного S2 attempt; не утверждает уже имеющийся proof |
| Q3 failure-aware | r5=1; S3=1; S3-repair ИЛИ S4=1; held final=1 | Если slot3 ушёл на repair, S4 остаётся без отдельного slot. Последний slot можно оставить неиспользованным |

Каждый charged attempt уменьшает capacity, даже при partial/no RESULTS. Solver sweep или automatic retry не предусмотрены. Объединить S3+S4/final в одном workflow можно только при реально подготовленных same-pin domains, proved leaf coverage и совместимых envelopes; количество groups не доказывает возможность такого объединения. Stop/go после r5 описан в DEPENDENCIES.md. Четыре attempts не гарантируют полные16/32 lengths, все impl/type classes, negative matrix или matched final. Новый budget/cap increase требует отдельного решения, review+GO.
