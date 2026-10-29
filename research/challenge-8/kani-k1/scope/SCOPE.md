# SCOPE: предложенный состав, пригодность для CI не проверена

2026-10-29. Ветка `experiment/kani-k1-scope-20261029`. Сборок, Kani, CBMC и внешних
CI-запусков не было. Это пересмотр состава доказательств и заявлений PR, а не подтверждение
прохождения organizer CI. Все неизвестные времена и allocation gaps сохранены явно.

Основа — библиотека `e96555151df91080fa0ccc106f60ee38a919c50e`, не C3c.
Коммит восстановления `778204a` возвращает `library/` побайтно к этой основе.
Отдельный library-коммит `c8fce2febdb97e73ab13ebe5d58d026a1e036087` добавляет только 189 item-level
`#[cfg(kani_smallsort_controls)]` в correct/merge/network. Ни тела, ни домены, ни assertions,
ни helper-макросы, ни covers, ни solver/unwind не изменены. Разбиения C3c не выбраны.
Подающая ветка не изменялась. Все коммиты содержат `[skip ci]`.

## Основания и принцип выбора

П-6: 8/8 ordinary-партиций Actions run `40748125754` относится к
`6cfc76cb211d088aebaff8a449bcac953e97f942`. Это историческое свидетельство из задания,
не свежая проверка данного патча. Оно не распространяется автоматически на весь `e9655515`.
В основе SCOPE статически 328 ordinary: 324 неизменённых П-6 модели и четыре C3a types/smoke.
Старое имя smoke совпадает, но его тело C3a изменено: прежние 0,1 с не присвоены новой модели.
Для C3a отдельно сохранены [результаты](c3a-evidence.json), measurement heads и library-tree SHA,
[заметки об ограничениях](c3a-notes.md) и [копия RESULT-C3A](RESULT-C3A-source.md)
из `87fdd544ffbb7728135002591b1c1cb83aa25217`. Первые N0..2 измерялись до исправления covers;
изолированный Cell N7 и smoke имеют собственные результаты. Новый состав целиком не доказан.

Сначала сохранены полезные свойства и нужные callee, затем убраны дорогие дубли и целые верхние
группы. Сохранены реальные trait-входы, переходы алгоритмов и типов, максимумы trait-safety,
полная группа insertion N20 со всеми offsets, normal-return Drop и положительные witnesses.
Отрицательные проверки остаются opt-in. Семейства сравниваются по сумме, а не только по max.
Точное сохранение cheap names не самоцель: группы промежуточных длин дают заметную общую цену.

Все 44 ordinary insertion-stub/merge-stub callers (`correct` 19 + `merge` 25 нетривиальных)
переносятся вместе с расширенными контрактными доменами. Дополнительно переносятся два trivial
merge callers N0/1 на каждый тип. Итого `correct` stub callers 19, `merge` callers 29.
В предлагаемом ordinary нет `stub_verified`: это устраняет оставленные conditional claims,
но **не доказывает** прежние allocation transfers. Самостоятельные prefix u8, merge N2..4,
sort4 и swap контракты сохраняют только свои конкретные домены.

У `correct` u64 fallback нужен begin0, а shifted begin1..15 в `[u64;17]` его не заменяет.
У u8 prefix `[17]` и exact-N callers различаются allocation models; scratch48 starts0/6/7
не равны произвольному scratch-домену. Exact-N merge witnesses не закрывают source/destination
subregions scratch48 у general/stable и вложенного sort8. Сохранённый ordinary contract
сам по себе не повышает старое conditional composition до whole-route theorem.
[Карта зависимостей](dependency-review.md) и per-name `required_proofs`/`contract_domain_gap`
в [scope.tsv](scope.tsv) сохраняют эти границы.

## Решения владельцу

Числа — ordinary до→после; стоимость — сумма **известных** macOS VT, секунды.
`T600` означает censored timeout без VT, не прибавленные 600 с.
`U4` — четыре неизвестных C3a macOS времени, не нули. Каждая строка развёрнута в scope.tsv.

| Семейство, число до→после | Остаётся / уходит в opt-in | Зависимости и потеря ordinary-заявления PR | VT до→после, с |
|---|---|---|---:|
| correct fallback, 17→0 | Все u64 N8..16/u8 N9..16 в opt-in | Insertion-stub callers вместе с регионами; нет unconditional exact-N fallback theorem | 1769,7→0 |
| correct scratch/general, 3→0 | u8 scratch48 и general/stable N14/15 в opt-in | Оба stubs и matching merge N14/15 вместе; нет этих scratch/composed domains | 462,8→0 |
| merge general callers, 29→0 | Вся u8/u64 general/stable группа в opt-in | Matching type/N contracts также opt-in выше4; scratch allocation transfer не заявлен | 1740,9→0 |
| merge exact contracts, 24→0 | N5..16 обоих типов в opt-in; N2..4 в строке остальных | Нет ordinary merge-contract theorem N5..16; callers вынесены | 3894,7 + T600→0 |
| real fallback, 9→7 | u8/u64 N0..6 остаются; combined N7 и u8 N8 opt-in | Без verified stubs; реальное correctness N7/8 больше не ordinary | 369,5→50,2 |
| Drop, 14→13 | Counts fallback2/4/8, general/stable2/4/8/16; tags до8 | Tag-permutation general/stable N16 opt-in; counts не заменяют tags | 369,8→98,0 |
| three-route safety, 31→3 | Целиком route0/1/2..255 при N2/8/16; остальные N opt-in | Прямой general u64/noncopy/stable выше16 не ordinary; не выдавать другие типы за тот же домен | 3100,7→74,7 |
| shifted tail contracts, 15→0 | Все START1..15 в `[u64;17]` в opt-in | Полный shifted family с callers; begin0/иные allocations не следуют из него | 3145,3 + T600→0 |
| network correctness, 27→13 | u8/u64 N0..7, N9; ещё u8 N13; остальные opt-in | N<9: sorted+permutation; N9/13: sortedness, structural permutation argument отдельно | 2943,7→181,5 |
| suffix permutation, 10→4 | u8/u64 N10/14; N11/12/15 opt-in | После width9/13 сохранены самостоятельные suffix witnesses, не full-route composition | 640,5 + T600→17,5 |
| lower insertion safety, 10→2 | Plain/Cell N1..5 все offsets; N6..14 opt-in | Дыры длин не закрываются максимумом20 | 650,9→13,5 |
| upper insertion safety, 56→10 | Plain/Cell N20, объединение offsets1..20; N15..19 opt-in | Сохранён максимальный домен целиком, без заявления о промежуточных lengths | 1709,3→450,3 |
| u64 network safety, 6→2 | Freeze N0..17 и unstable30..32; группы18..29 opt-in | Переход18 остаётся у u8; exact u64 intermediate domains не заявлены | 862,0→381,4 |
| trait dispatch safety, 22→18 | Все типовые группы/15..17/максимумы32; bytes86 до16; standalone31 opt-in | Только bytes16/17/85/Drop N31 теряются; u8 combined31/32 сохранён | 2007,4→1473,9 |
| swap types, 8→6 | u8/u64/bytes16/17/Cell/Drop; bytes85/86 opt-in | Predicate matrix не заменяет контракты bytes85/86 | 742,8→143,4 |
| swap indices, 8→0 | Exact allocations9/12/13/16 opt-in; отдельные17/four-position в остальных | Никакого переноса доказательства между allocations | 222,5→0 |
| mutating Cell routes, 4→3 | Traits N0..8 и13..16; промежуточные9..12 opt-in | Удалён самостоятельный промежуточный length domain | 188,9→152,9 |
| C3a types/smoke, 4→4 | Logical Cell N0..2/N7, Drop N0..2 и predicate matrix | Реальные traits без stubs; C3a covers требуют повторного аудита того же SHA | U4→U4 |
| Остальные 31 без изменений | Assembly5, unit-ZST8, prefix u8, merge-contract2, sort4×4, reachability3, swap4/17×5, mutating permutation3 | Положительные witnesses и самостоятельные локальные домены; не whole generic theorem | 546,0→546,0 |

Набор намеренно существенно меньше старого: **212 перенесено, ни одна гармоника не удалена**.
Ни одна строка таблицы не объявляет временную или логическую эквивалентность разных allocations,
типов, компараторов или длин. Sparse domains перечислены, не замаскированы диапазоном.
Исторические module comments исходной библиотеки про «ordinary N2..16» относятся к пакету-основе;
после cfg-отбора состав и текст заявления PR задаются этой таблицей и манифестами.
Их обновление в нейтральную к конфигурации документацию следует сделать в подающем пакете;
SCOPE не меняет библиотечный текст сверх разрешённых item cfg.

## Прогноз бюджета и память

Пересчёт воспроизводим: [metrics.json](metrics.json), [prepare_scope.py](prepare_scope.py),
исходные [mac-times.tsv](../c3c-inputs/mac-times.tsv), binding в RESULT-C3C.
Пакет-основа: 328 ordinary; 321 SUCCESS timing суммой **25367,4 с**, ещё три T600 и четыре UNKNOWN.
TSV содержит 322 SmallSort SUCCESS строки суммой25367,5: старые smoke0,1 с здесь исключены.

Предложение: **116 ordinary = 112 с известными временами + 4 C3a UNKNOWN**.
Сумма известных VT **3583,3 с = 59,72 мин**, полный прогноз **3583,3 с + U1+U2+U3+U4**.
Известный max **230,2 с**, полный max `max(230,2; U1; U2; U3; U4)`.
Известных **8 >120 с**; полный счёт `8 + count(Ui>120)`.
Известных >300 с —0; по C3a и по новому SHA это не установлено.
Это исторические Mac точки неизменённых тел при допущении переносимости времени через cfg-отбор;
не новый wall-time замер, не GCB-to-Mac прогноз и не CI acceptance.

Порог ~120 с — идеальный ориентир организаторов из предоставленного #56, а не жёсткое правило.
Рабочие цели **ΣVT≈1 ч и max≤300 с** — наши; они не являются критерием организаторов или
границей wall всего job. При jobs3 SmallSort известный VT даёт идеальные19,91 мин без overhead,
но общий std job, компиляция, inventory, неизвестные C3a и память сюда не входят.
Все восемь известных >120 с сохранены за ценность trait/type boundaries и максимальных safety:
bytes16/17 mid+max, u8 merge route, mutating Cell13..16, u64 Freeze0..17 и unstable30..32.
Одновременно могут выполняться **до трёх тяжёлых проверок**, не восемь и не одна;
последовательность scheduling этим патчем не задаётся. Четыре UNKNOWN могут тоже быть тяжёлыми.

Из [per-harness-memory.tsv](../c3c/per-harness-memory.tsv): baseline GCB library=`e9655515`,
measurement head=`f9bdf626a42ad41ae81f4ddbc0cb08f1b5647810`, build
`e358163c-9006-4ea0-a402-c12a5a009747`. Перенесённые route N32/N31 имели CBMC HWM
4324924/4112844 KiB (4,12/3,92 GiB), tail START1 —2989792 KiB (2,85 GiB).
Из сохранённых есть индивидуальные замеры лишь у **10/116**: max1158900 KiB (1,11 GiB),
assembly unit N32; это **не** верхняя граница памяти остальных моделей или всего job.
Baseline matched-job sampled RSS-sum peak11,02 GiB, driver HWM5,53 GiB — прежний состав,
не прогноз SCOPE. Для C3a известны только общие пики отдельных jobs1 запусков: до2,41 GiB
sampled sum и2,16 GiB driver, без per-harness attribution; см. c3a-evidence.json.
Mac peaks и одновременный пик нового набора UNKNOWN. RSS не равна физической RAM;
нельзя складывать независимые per-PID maxima и объявлять это пиком при jobs3.

Варианты: выбранный состав сохраняет важные safety domains ценой восьми известных >120 с.
Если выбрать жёсткий исторический cutoff120, потребуется дополнительно вынести именно эти восемь:
останется108, известная сумма2239,3 с, известный max119,5 с, но потеряются перечисленные
типовые/максимальные safety domains; C3a и пригодность нового SHA всё ещё UNKNOWN.
Если вернуть все offsets N15..19, добавятся46 гармоник и1259,0 с: known Σ4842,3 с,
плюс U4; это явный вариант приоритета доменов, выходящий за нашу рабочую сумму.
Основной патч фиксирует первый вариант, не автоматически применяет cutoff к отдельным именам.

## Covers, C3c и opt-in

E **не включён**: он меняет тела и coverage policy. Перенос proof item переносит его covers
вместе с ним, а все covers сохранённых ordinary остаются. Отдельная будущая опция E потребует
нового cover-migration manifest, проверки existential witnesses при обеих конфигурациях,
сохранения настоящих dispatch-reachability covers и нового измерения. При известных3583,3 с
и неизвестном остатке оснований ослаблять covers сейчас нет.

C3c START1/6, route31/32 и correct14 разбиты с полезным max в ряде GCB проб, но измерены
в сочетании с E/K/solver configuration кандидата. После возврата covers/изменения solver
**требуют замера**, не получают чисел из C3c. Для исходного TIMEOUT выигрыш суммы не установлен.
Поэтому не переносим ни successor, ни helper-макросы C3c. Если будущий этап выберет разбиение,
он обязан перенести весь необходимый helper и union domain, без невыбранных E/K.
Карта [domain-map.tsv](domain-map.tsv): исходное имя→то же имя→точно тот же домен, 328 строк;
для212 исходное имя остаётся в opt-in, для116 нет дополнительной копии, controls включает его тоже.

Механизм — только существующий `cfg(kani_smallsort_controls)`; новый cfg не вводится.
Включённый cfg компилирует423 старых имени: ordinary116 + расширенные PASS280 + FAILED26
+ один deferred ZST contract. [manifest.tsv](manifest.tsv) задаёт раздельные ожидания:
[ordinary.txt](ordinary.txt), [extended-positive.txt](extended-positive.txt),
[controls-failed.txt](controls-failed.txt). PASS означает требуемый результат, не полученный.
На runner PASS соответствует `SUCCESS`; FAILED требует ожидаемого нарушения свойства,
а не timeout, OOM или setup/compiler error. Имя `control` само по себе не означает FAILED:
положительные reachability controls находятся в PASS280.
`swap_contract_zero_sized_n2` сохранён и отдельно [отложен](deferred-unsupported.txt):
исторически неподдерживаемая ZST-инструментация — не обычный отрицательный counterexample.
Это явное ограничение opt-in suite, а не удаление гармоники или обещание полного green cfg.

## Статическая проверка и план выполнения

Локально выполнены только Python, git/read и предписанный rustfmt. [static-check.json](static-check.json):
`PASS_STATIC_FORECAST_ONLY`, 328/328 исходных ordinary имён, всего423/423 уникальных,
116 ordinary/307 opt-in, identity unions328, все прежние opt-in сохранены.
Снятие cfg из обеих версий даёт идентичный исходный текст трёх изменённых файлов;
189 новых cfg: correct20/merge84/network85. Rustfmt `--check --edition 2024` с заданным config
завершился exit0; строки Rust≤100. Это **статический прогноз**, не раскрытие макросов компилятором,
не фактический `kani list` и не проверка assertions. Повторить локально можно командами:

```sh
cd /root/verify-rust-std-kani-scope && python3 research/challenge-8/kani-k1/scope/check_scope.py
cd /root/verify-rust-std-kani-scope && python3 research/challenge-8/kani-k1/scope/prepare_scope.py
```

Полный, **не выполненный** [план проверки и стоимости](VALIDATION-PLAN.md) включает обе конфигурации,
фактический inventory, все4×2 ordinary-партиции Linux/macOS, autoharness jobs3/10m на обеих ОС,
явный PASS/FAILED opt-in и аудит covers/контрактов на SHA library-патча.
Печататель будущих команд явно выбирает один список и ничего не запускает:

```sh
cd /root/verify-rust-std-kani-scope && python3 research/challenge-8/kani-k1/scope/reproduction_commands.py --manifest ordinary
cd /root/verify-rust-std-kani-scope && python3 research/challenge-8/kani-k1/scope/reproduction_commands.py --manifest extended-positive
cd /root/verify-rust-std-kani-scope && python3 research/challenge-8/kani-k1/scope/reproduction_commands.py --manifest controls-failed
```

## English PR draft (proposed scope, not a CI result)

To keep the default SmallSort suite practical, extended proof domains are opt-in via
`RUSTFLAGS="--cfg kani_smallsort_controls"`, consistent with the runtime guidance in
[#56](https://github.com/model-checking/verify-rust-std/issues/56). Proof bodies and covers are preserved.
Select positive extensions and intentional failure controls using separate exact-name manifests.
This scope has historical evidence per source SHA; its full CI suitability remains untested.

- `correct`: insertion-stub fallback u64 N8..16/u8 N9..16; u8 scratch48 and general/stable N14/15.
- `merge`: all merge-stub general/stable callers, merge contracts N5..16, real fallback N7/8, tag N16, three-route safety except N2/8/16.
- `network`: shifted u64 tails; network u8 N8/10..12/14..17 and u64 N8/10..14; suffix N11/12/15; insertion N6..19; u64 safety18..29/Cell routes9..12; standalone dispatch31; swap widths85/86 and allocations9/12/13/16.
- Negative controls stay opt-in; positive C3a logical trait checks and smoke remain ordinary with unknown macOS timings.
