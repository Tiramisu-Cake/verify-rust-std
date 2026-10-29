# VALID-B: 144/144 SmallSort SUCCESS; полный job завершён с двумя std TIMEOUT

Объект: `9be5499c459e3157be0d86dc366b2eccd1e911c8`, ветка `experiment/kani-k1-scope-20261029`.
Во всех трёх сборках library tree `2532dc573cf9793aa05b94caa884733fab1991be` совпадает с объектом.
После объекта изменены только lane, requests и отчётные материалы; library не исправлялась.
[Привязка исходников](valid-b/source-bindings.json) подтверждает также неизменность workflow, runner script и pins.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, toolchain `nightly-2026-10-12`.
GCB: Ubuntu 24.04.5, e2-standard-4, 4 CPU, 15,63 GiB, swap off для proof-прогона.

## Сборки и стоимость

| Назначение | Build UUID | Измеренный HEAD | Cloud wall, с | USD |
|---|---|---|---:|---:|
| ordinary inventory | bb71a182-76ec-4e8d-a6db-939c125a66f5 | 6ba5e109ea75 | 2579,713 | 0,5805 |
| controls inventory | e489cd59-0518-41fc-bd37-4fbd0948c859 | cd2af83cc7ea | 3023,185 | 0,6885 |
| full autoharness | c1a782cf-ea1f-46d5-8ca5-8fd23c8abbca | 20ee8d6941b1 | 10291,944 | 2,3220 |

Источники: [status/summary/pages/peaks](valid-b/evidence/), [вычисления](valid-b/metrics.json).
USD — ledger: Cloud start/finish, округление вверх до минуты × $0,0135; не счёт billing.
Итого **3/5 сборки, $3,5910/$7**, резерв завершённых сборок нулевой: [budget-final](valid-b/budget-final.txt).
Перед отправками глобальный used+reserved составлял $51,5400, $52,7550 и $52,8090;
с последним резервом максимум $56,8590 < неизменного CAP_USD=$63,96. Других запусков не было.

## Inventory и предупреждения

Добавлен kind `inventory`: supported `kani list --format json`, без `--harness` и proof-запуска;
controls RUSTFLAGS выставляется до компиляции; exit и артефакт привязаны к request/build/HEAD/Kani.
Обе сборки SUCCESS/COMPLETE. Native ordinary **144**, controls **423**, каждое имя встречается один раз.
Сверены точные мультимножества: missing=0, extra=0 в обеих конфигурациях; SHA256 списков в metrics.json.
Controls классифицируется как 144 ordinary + 252 extended-positive + 26 expected-FAILED + 1 deferred.
Это классификация списка, не proof результатов controls. Все страницы прошли binding/offset/hash проверки.
`log-grep 'smallsort/verify|unused_macros|unused_imports|dead_code|warning: unused|warning:.*never used' 200`
дал `(no match)` в обеих конфигурациях: [ordinary](valid-b/evidence/ordinary.warnings.txt),
[controls](valid-b/evidence/controls.warnings.txt). Найденных оснований менять library или ordinary нет.

## Полная эмуляция kani_autoharness

Literal команда извлечена из workflow: include/exclude сохранены, unwind1000, jobs3, timeout10m/harness,
failure propagation через pipefail. Общий бюджет работы270мин; повторный inventory не запускался.
Job завершился сам: **COMPLETE, Kani exit1, gate=false, GCB FAILURE**; общий timeout не сработал.
Cloud wall10291,944с; GNU time wall включая std codegen **9909с (2:45:09)**.

| Область | SUCCESS | FAILED | TIMEOUT | Нет результата | ΣVT, с | Источник |
|---|---:|---:|---:|---:|---:|---|
| Все manual harnesses | 1890 | 0 | 2 | 0 | 17176,482 | summary pages, metrics.json |
| Из них SmallSort | 144 | 0 | 0 | 0 | 9751,393 | per-harness.tsv, inventory144 |
| Automatic functions | 246 | 0 | 0 | 0 | NA | function-summary.txt, native final line |
| Всего manual + automatic | 2136 | 0 | 2 | 0 | NA | сумма двух независимых итогов выше |

Summary-парсер lane экспортирует manual harnesses; времена automatic functions им не экспортируются.
Их итог246/246 получен отдельно через bounded log-lines, не включён в manual ΣVT.
Оба TIMEOUT вне SmallSort: `num::nonzero::verify::nonzero_check_isqrt_u32` и
`ptr::non_null::verify::non_null_check_write_unaligned_i128`: [bounded failure lines](valid-b/evidence/autoharness.failures.txt).
Отдельных FAILED/OOM/missing-result manual строк нет; отсутствующих ordinary имён, лишних и дубликатов — 0.
Все144 времени/статуса/checks/covers: [per-harness.tsv](valid-b/per-harness.tsv), источник — bounded pages.
SmallSort max444,323с (`network_safety_unstable_u64_n30_to32`); >120с — 28; >300с — 3.
Ещё два >300с: `dispatch_safety_stable_unstable_bytes17_n32`350,330с и `...bytes16_n32`330,589с.
Это GCB значения; macOS цель300с ими не подтверждается и не опровергается.

| C3a (verify::) | SUCCESS VT GCB, с | Covers | Источник |
|---|---:|---|---|
| smoke::predicate_efficient_swap_type_matrix | 0,1762783 | 12/12 | per-harness.tsv |
| types::sorted_permutation_traits_fallback_cell_u8_n0_to2 | 56,569527 | 14/14 | per-harness.tsv |
| types::sorted_permutation_traits_fallback_cell_u8_n7 | 189,993440 | 5/5 | per-harness.tsv |
| types::sorted_permutation_traits_general_drop_u8_n0_to2 | 67,900345 | 14/14 | per-harness.tsv |

Закрыты четыре UNKNOWN **для GCB**; macOS времена этих четырёх остаются UNKNOWN.
Для140 известных mac VT сумма4520,3с; новые GCB для них9436,753с; четыре C3a добавляют314,640с.
ΣVT всех144 =9751,393с попала в прежний ориентир9000–15000с. Для140 пар исторический MacVT/GCBVT:
median0,4568, min..max0,2357..1,3904; отношение сумм0,4790. Источник — scope.tsv + per-harness.tsv.
Это описательная сверка, не универсальный коэффициент платформ и не новое macOS измерение.

## Память и сравнение с C3c

[peaks](valid-b/evidence/autoharness.peaks.txt): driver VmHWM6184352KiB =5,898GiB;
CBMC VmHWM4401732KiB =4,198GiB; одновременная RSS-сумма11815784KiB =11,268GiB @8219с.
Одновременная сумма CBMC8779624KiB =8,373GiB; это sampled значения с интервалом2с,4820samples.
Независимые PID максимумы не складывались. cgroup cap отсутствует, cgroup peak/oom_kill недоступны;
parser OUT_OF_MEMORY=0, dmesg_oom=none_seen — наблюдение, не доказательство отсутствия OOM.
C3c `be070a8b`: PARTIAL/exit124, Cloud17703,8с; manual1959:1951SUCCESS/5TIMEOUT/3missing,
SmallSort238:233SUCCESS/2TIMEOUT/3missing; ещё183 native ordinary без result row.
Тогда SmallSort ΣVT18045,638с, driver8,06GiB/CBMC4,34GiB/сумма13,54GiB.
Источники сравнения: RESULT-C3C.md и c3c/evidence/autoharness.*; исторические записи не переписаны.
Сейчас состав144 вместо421, отдельный inventory вынесен из job; цензура и состав различаются.
Поэтому меньшие wall/ΣVT/пик не названы matched whole-job speedup или гарантией памяти GitHub.

## Opt-in: перенос по исходникам, не новый прогон

[optin-evidence.tsv](scope/optin-evidence.tsv) содержит252 строки: latest historical PASS, SHA/build/source,
выбранное совместимое свидетельство и результат аудита. Все C3c bounded замеры рассмотрены по finishTime.
Исторический exact PASS найден для185; для67 — NO_EVIDENCE. Перенос допустим для184 перемещённых:
182 по П-6 run40748125754 на `6cfc76cb`, 2 по GCB baseline-memory `e358163c` на `f9bdf626`.
Из68 прежних opt-in:67 без exact PASS,1 RESULT-C3A PASS не переносится из-за изменения helpers.
Итого source-transfer184, **NO_EVIDENCE68**. Поздние C3c PASS с переписанными bodies/helpers не перенесены.
Проверены git library diff, harness/helper bodies и non-cfg attrs; production вне verify неизменён.
[Скрипт](scope/audit_optin_evidence.py) разрешает helper-ссылки/макросы по идентификаторам;
это ограниченный статический source audit, не раскрытие Rust macros компилятором и не формальная эквивалентность.

## Осталось непроверенным

252 opt-in,26 expected-FAILED и deferred не прогонялись на B; полный covers/contract-edge аудит не выполнен.
Нет новых organizer partitions Linux/macOS, macOS autoharness и четырёх C3a mac VT; новый П-6 — решение владельца.
GCB SmallSort144 PASS не превращает общий job с двумя std TIMEOUT в PASS и не закрывает allocation gaps.
Проверки:70 lane tests PASS, оба native inventories/hash bindings, повтор source audit — PASS.
`git diff --check` для кода/отчёта — PASS; literal evidence и per-harness TSV исключены:
их конечные tabs/пробелы сохраняют пустые поля и исходные строки, общий check их отмечает.
Локальных rustc/cargo/Kani/CBMC запусков не было; Rust не менялся, rustfmt для изменённых .rs не требуется.
Все коммиты `[skip ci]`, normal push только экспериментальной ветки; ветка подачи не менялась.
