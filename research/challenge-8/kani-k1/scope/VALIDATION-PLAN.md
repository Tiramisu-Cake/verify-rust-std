# План проверки SCOPE-B — НЕ ВЫПОЛНЕН

Объект проверки — library-коммиты B `b3213b9be0` и review-fix `d627e2ffbd`; итоговый library tree `462e8f1cc3d4104d1513fba0303c4591f32a1da4`. Перед будущей проверкой сверить этот tree на выбранном SHA. В этой работе сборки и CI-запуски запрещены; Python/rustfmt результаты — локальные проверки, не формальное доказательство.

## Инвентарь и компиляционные проверки

1. На одном и том же SHA выполнить compile/codegen и `kani list --format json` с ordinary cfg и с `RUSTFLAGS="--cfg kani_smallsort_controls"`. Сохранить полный SHA, Kani/CBMC pins, toolchain, flags и оба фактических inventories. Сверить ordinary=144 и controls-enabled=423 с актуальными manifests. Проверить exact multiplicities и классификации PASS/FAILED/deferred; расхождения расследовать, не подгонять Python forecast. Фактический inventory — NOT_RUN.
2. В обеих cfg-конфигурациях проверить отсутствие новых warnings `unused_macros`, `unused_imports`, `dead_code`, включая helpers, imports и macro call sites из review. Отдельно проверить actual helper reachability / macro expansion после compilation. Статический Python use check — только прогноз, не замена compiler.
3. Перепроверить item-level cfg diff: bodies, domains, assertions, helper bodies, covers, solver и unwind не изменены; допустимы только cfg, разнесение импортов и top-level комментарии. Сопоставить lists с manifests: 144 ordinary; 252 positive extensions (=68 прежних +184 moved), 26 FAILED controls, 1 deferred unsupported; всего 423. Раскрытые атрибуты должны подтвердить 19 ordinary `stub_verified` callers, 15 matching T/N/comparator edges и 4 N0/1 без вызова merge.

## Доказательства и coverage

4. Выполнить ordinary PASS отдельно от 252 positive opt-in PASS harnesses; 26 expected-FAILED controls выполнять и оценивать отдельно. Deferred ZST contract — отдельная диагностика, вне PASS/FAILED gate. Каждый обязательный harness должен иметь ожидаемый outcome; TIMEOUT, NOT_RUN, missing result, runner/compiler error не засчитываются как PASS или ожидаемый FAILED.
5. Выполнить contract-edge audit: для пятнадцати nontrivial ordinary merge callers exact type/N/comparator/contract должен совпадать; четыре callers N0/1 не вызывают merge. Отдельно сохранять allocation gaps exact-N↔scratch48 и shifted tails; успешные отдельные contracts не делают такую композицию unconditional. Проверить остальные `proof_for_contract` type/N/comparator/region edges по манифесту.
6. Covers audit на обоих cfg: перенесённые covers доступны с controls, retained ordinary covers доступны без controls; проверить применимость, удовлетворение и unreachable/UNSAT по harness, а не только aggregate PASS. Перепроверить C3a N0/1 applicability, Cell N7 covers, type matrix12, normal-return dispatch и insertion all-offsets20. Если появятся E или C3c splits, требуются новые manifests, union map и повторный migration audit.
7. На том же SHA выполнить все четыре organizer `check-kani-on-std` partitions на Linux и macOS (8 jobs), с существующими pins/flags и заново рассчитанными границами всего std inventory. Эти partition проверки не взаимозаменяемы с selected SmallSort.
8. Отдельно выполнить полный `kani_autoharness` на Linux и macOS с исходными include/exclude, unwind1000, jobs3, timeout10m/harness и failure propagation. Сохранять стандартный inventory и whole-job результаты; выбранный список или Linux GCB-emulation не заменяет organizer macOS acceptance.
9. Для отдельного будущего PR2 применить `pr2-ungate.patch` одним коммитом с `[skip ci]`. Локальный прогноз уже проверил копию дерева: ordinary328 точно совпадает с `e9655515`, все прежние opt-in и FAILED26 сохранены. На PR2 SHA потребуются заново оба фактических inventory, предупреждения, full partitions и autoharness; результаты B автоматически не переносятся. Комментарии состава в library описывают основной B: PR2-патч по условию снимает только бюджетные cfg. Ни создание PR2 ветки, ни эти сборки сейчас не выполнялись.

## Метрики и стоимость плана

Для ordinary/autoharness собрать per-harness VT, wall/start/stop/thread, memory PID/model attribution, driver/CBMC/cgroup simultaneous peaks и OOM status. Пересчитать известные ΣVT/max/count>120, оставить 4 C3a UNKNOWN отдельно и зафиксировать число одновременно исполняемых тяжёлых доказательств. Не суммировать независимые PID maxima.

B arithmetic: 144 ordinary; 140 известными VT, сумма 4520,3 с, max 230,2 с, 8 выше120 с, +4 UNKNOWN. Это macOS historic/forecast accounting, не GCB wall или новое измерение. При selected timeout 10 минут и jobs3 ideal capped proof schedule для ordinary — `ceil(144/3)×10 = 480 мин` ($6,48 по $0,0135/мин); эта изолированная оценка перекрывается полными partitions/autoharness и не прибавляется к GCB envelope ниже.

Positive opt-in =252 гармоники: планировать 7 chunks — шесть по40 и последний12; допускается единый bounded chunking с пределом40 и отдельным результатом для каждого harness. При jobs3 и timeout10m идеальный scheduling ceiling на 40-case chunk —140 мин; 210-мин envelope оставляет70 мин на setup/list overhead. Для финальных12 идеальная timeout-граница40 мин; запросить достаточный envelope после setup-измерения. FAILED26: ideal `ceil(26/3)×10=90 мин`, envelope150 мин включая60 мин setup. Не трактовать envelope как обещание завершения.

GCB planning rate: $0,0135 per billed minute. Envelopes:

| Work | Planning envelope | GCB envelope cost |
|---|---:|---:|
| Codegen/inventory, 2 cfgs | 2×60 min | $1,62 |
| Diagnostics: 8 known >120 plus 4 C3a UNKNOWN, memory/covers | 90 min | $1,215 |
| Full Linux autoharness emulation | 300 min timeout / 270 min work | max $4,05 |
| Four Linux ordinary partition jobs | 4×300 min | max $16,20 |
| 252 positive opt-in, seven chunks (40×6 + 12) | 7×210 min | max $19,845 |
| FAILED26, run separately | 150 min | max $2,025 |
| Deferred unsupported diagnostic | 60 min | max $0,81 |

Total listed GCB envelopes: **3390 min / $45,765**, with four partition jobs. This is a conservative planning reserve, not a forecast of proof success, actual runtime or an authorized build budget. Mac partition and autoharness work need separate resources and must not use the GCB rate. Re-estimate after the first measured chunks while preserving external coordinator/owner/slot limits.

## Исторические источники и ограничения

П-6 `check-kani-on-std`: 8/8 partition results на `6cfc76cb211d088aebaff8a449bcac953e97f942`, Actions run `40748125754`, согласно [TASK-SCOPE, правке 1](../TASK-SCOPE.md). Это только историческое основание; на SHA B/C3a не переносить без запуска. Три macOS TIMEOUT600 и гибель Ubuntu runner — данные [TASK-C3C](../TASK-C3C.md), не вывод о причине. [RESULT-C3C](../RESULT-C3C.md) отмечает, что причина остановки исторического Ubuntu run не установлена. Не читать полные логи и не выдавать эти сведения за новый SHA результат.
