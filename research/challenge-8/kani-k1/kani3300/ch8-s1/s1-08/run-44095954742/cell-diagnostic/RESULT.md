# cell-u34: CONFIRMED timeout, secondary completeness error

Exact missing RESULTS: `slice::sort::shared::smallsort::verify::sorting_entry_smoke::stable_default_cell`.
Stock export явно сообщает `TIMEOUT`, 600.031112420 s при лимите 600 s;
`n_properties=null`, rich inventory отсутствует (0 сохранённых records, не нулевой успешный inventory).
У `slice::sort::shared::smallsort::verify::sorting_entry_smoke::unstable_default_cell`
RESULTS присутствует: 301 property, export `COMPLETED/SUCCESS`, 594.575884753 s.
Это source-reported observation, independent proof credit NONE; оба row receipts остаются UNKNOWN.

Первичная причина CONFIRMED: per-harness CBMC timeout. Pinned producer
`call_cbmc.rs:220–253` при timeout убивает CBMC и записывает `ExitStatus::Timeout`;
его Err renderer (`619–650`) не печатает RESULTS. Затем `rich_evidence.py:110–123`
требует закрытый RESULTS каждого selector, а `runner.py:1038` вызывает validation
до разбора row outcomes: полученный completeness ValueError вторичен.
Ошибку формата property/message этот диагноз не показывает.

Group original exit=1, signal=null, outer timed_out=false; caps/interrupt не отмечены.
Peak group RSS=7,567,972 KiB при cap=12,582,912 KiB; per-root RSS UNKNOWN.
Compile COMPLETE, initial-export marker INCOMPLETE — ожидаемый начальный snapshot,
финальный export COMPLETE. Job elapsed=1605 s; runner step≈1240 s;
child wall=1240.444 s; compile upper bound=34.145 s; export wall=1206.214 s.
Original OS exit/signal самого CBMC и точная solver subphase UNKNOWN.

Labels: compiler extraction/renderer defect как первичная причина этой cell не подтверждается:
обе native roots скомпилированы, восемь `unstable_default_cell::*` labels
наблюдаются как SUCCESS descriptions. Stable label verdicts UNKNOWN после timeout.
Причинность labels/замены `assert!`→`kani::assert` для роста времени UNKNOWN:
контролируемого сравнения и stable inventory нет; elapsed/property count её не доказывают.

ZIP digest проверен до извлечения; SHA/bytes всех 10 embedded и 23 nested native
members совпали. Repository/run/attempt/job/group/head/request/source/tool сверены.
Bounded job log не запрашивался: условие task §3 не наступило, artifact уже даёт причину.
См. DIAGNOSTIC.json, PROVENANCE.json и compact projections.

Следующий адресный шаг: координатор решает, разрешать ли targeted retry
`stable_default_cell` с достаточным per-harness/group бюджетом. Отдельный prospective
decoder fix должен сохранять TIMEOUT и UNKNOWN inventory. Ни retry, ни fix не выполнялись.
