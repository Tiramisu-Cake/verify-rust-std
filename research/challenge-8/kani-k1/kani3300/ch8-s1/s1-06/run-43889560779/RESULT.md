# S1-06 intake — run 43889560779

Вход g0 `f58f131cfa575698617e551707f665445a454625`. Executed control `a14a513eb7a77297a0cc10ff6eefa7577c2c383c` имеет тот же tree `e2d7a9f47c88ac498e3c344ee2b88737f45af2b4`, что fix `b25dd39a46ba90b167500997d546a5f2f5bd8f3b`. Std `5be85699b8826e3286c0bf89efb9affefac0acb5`, tool `0aac16ef62da9e9d5645782d458593e5d78143ba`. Request SHA256 `0ff35bdc40434ac6b22b4f4b5919923ab09d849c08c9930f291c014f8b96fe7b`.

**14/14 artifacts получены; 35/35 harness завершены: 27 SUCCESS, 8 FAILURE. Все 9986/9986 rich properties сохранены, descriptions полны, 9968 имеют допустимые file/line. Qualified acceptance PENDING, independent proof credit NONE.**

GitHub ZIP SHA256 проверен до извлечения для всех 14 архивов; SHA256/bytes всех компактных JSON entries совпали. Stock/rich exact inventories согласованы по ID/status/class/buckets и named failure/unsupported records неизменённым decoder. Это проверка целостности и source-reported observations, не независимое доказательство корректности.

| Группа | Строк | job | child exit | elapsed s | RSS KiB | missing sites |
|---|---:|---|---:|---:|---:|---:|
| activation-default-u34 | 1 | success | 1 | 33.103 | 1935360 | 0 |
| activation-override-u34 | 1 | failure | 1 | 60.058 | 1930560 | 1 |
| cell-u34 | 2 | success | 0 | 753.287 | 8138992 | 0 |
| freeze_copy_u8-n01-u34 | 2 | failure | 0 | 52.130 | 2612792 | 2 |
| freeze_copy_u8-n23-u34 | 2 | failure | 0 | 113.899 | 2670224 | 2 |
| freeze_default_noncopy-n01-u34 | 2 | failure | 0 | 51.150 | 2664388 | 2 |
| freeze_default_noncopy-n23-u34 | 2 | failure | 0 | 328.124 | 2639156 | 2 |
| light-controls-u34 | 9 | failure | 1 | 84.423 | 2344080 | 1 |
| light-corruption-u4 | 3 | success | 1 | 31.422 | 1943668 | 0 |
| light-model-u5 | 3 | success | 0 | 67.442 | 2480800 | 0 |
| stable_freeze_u8-n01-u34 | 2 | failure | 0 | 55.732 | 2601632 | 2 |
| stable_freeze_u8-n23-u34 | 2 | failure | 0 | 316.173 | 2667624 | 2 |
| unstable_freeze_u8-n01-u34 | 2 | failure | 0 | 56.411 | 2632980 | 2 |
| unstable_freeze_u8-n23-u34 | 2 | failure | 0 | 105.785 | 2642528 | 2 |

Elapsed total 2109.139 s включает compile. Compile upper bounds 507.628 s отдельно не прибавляются. RSS — sampled process-group peak; wall/exit/RSS каждого отдельного harness не измерены и оставлены UNKNOWN. Per-harness stock verification_time_s записан отдельно в collected.json. Все compile markers COMPLETE, нет timeout/signal/caps; source_before/after совпадают с request.

Все heavy child exits = 0 и все 16 heavy verdicts = SUCCESS. Runner/job exit1 вызван **ValueError: rich metadata incomplete: file/line missing**, а не failed proof assertion. Та же причина у light-controls и activation-override; их child exit1 согласован с восемью заранее заданными негативами всего batch, но failed group нельзя считать принятой negative-проверкой. Group success также не заменяет per-row verdict: activation-default и light-corruption имеют child exit1 при успешном сборе evidence.

В отличие от S1-05 декодер сохранил все records, suffix и следующие harness. Rich.error = null означает отсутствие ошибки streaming-разбора; полнота всё равно INCOMPLETE, а точный validation error находится в group receipt.reason и повторён в collected reconciliation. Четыре группы / 9 строк COMPLETE; 10 групп / 26 строк INCOMPLETE. Из последних только 18 строк сами имеют missing site; ещё 8 light-controls строк индивидуально полны.

У каждой heavy строки отсутствует site ровно одной property: class `unreachable`, description `unreachable code`, status **SUCCESS**. Всего в heavy 16 occurrences (12 u8, 4 NonCopyByte); ещё 2 u8 occurrences — production и mutated stable_freeze_activation. Всего 18 occurrences / 2 exact IDs:

- `slice::sort::shared::smallsort::small_sort_general_with_scratch::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.unreachable.1` — 14 occurrences, из них heavy 12.
- `slice::sort::shared::smallsort::small_sort_general_with_scratch::<slice::sort::shared::smallsort::verify::sorting_model::NonCopyByte, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<slice::sort::shared::smallsort::verify::sorting_model::NonCopyByte>>.unreachable.1` — 4 heavy occurrences.

Original location display: `library/core/src/lib.rs:0:0 in function <соответствующая функция>`. Имя файла присутствует в display, но line0/column0 не дают действительной координаты, поэтому decoder сохраняет file/line=null. Точные row IDs, полные displays и records — missing-sites.json. Нулевую строку не заменяли line1 или координатой начала функции.

Pinned stock compiler создаёт этот class только из MIR `TerminatorKind::Unreachable`, с assert(false) перед assume(false): exact source excerpts, SHA и поиск producer сохранены в STOCK-ROLE.json. Это служебные stock checks недостижимости, а не mandatory user post/frame/relation assertions/covers. При этом их нельзя удалять: они проверяют недостижимость блока, включая случаи intrinsic unreachable. **Class unreachable / status SUCCESS не равен status UNREACHABLE.** Причина нулевого source span и точный originating MIR block UNKNOWN; ID и file-display сами их не устанавливают.

По текущей политике координаты продолжают блокировать completeness. POLICY-QUESTION.md предлагает координатору сохранить все sites либо отдельно разрешить узкое location-only исключение для этих exact успешных stock records. Ни один вариант ослабления не принят, trusted gates и classifier policy не менялись. Непосредственный runner blocker — именно координаты; утверждать, что qualified acceptance блокируется только ими, нельзя: after fingerprints не достигнуты в 10 failed-группах, остаются source/contract/required-message/unreachable-role gates.

Офлайн-приёмка: **0 qualified; 8/8 exact predeclared negative observations**, из них 3 в COMPLETE группах. Все **113/113 required covers** связаны с unique same-run SATISFIED ID; **13/127 required-success messages** имеют unique source-callsite→SUCCESS property binding, остальные114 PENDING. Это observations, не proof acceptance. Точные gates — accept/ACCEPTANCE.md и accept/ACCEPT.json. Отсутствие location у stock checks не объявлено отсутствием обязательных post/frame/relation/covers; последние проверяются отдельно по IDs/смыслу.

Нового package defect, требующего semantic fix этой стадии, не установлено: retention и fail-closed работают по прежнему contract. Отсутствующий after snapshot — отдельное неизвестное измерение, не восстанавливаемое по source_after или из другого run. Нового fix control commit нет.

Структурный replay: `PYTHONDONTWRITEBYTECODE=1 python3 intake.py`. Контрольные pins, hashes, exact inventory reconciliation, исходные exits и ограничения подтверждены VALIDATION.json. Без push/CI/публикаций/ledger, локальных cargo/rustc/Kani/CBMC и полных raw logs. Исторические receipts/ledgers не изменены.
