# W3-L2 — корректность, план R8

Начало: 2026-10-27T10:18:21Z. Ветка `experiment/kani-k1-correct-20261027`.
Доля $5,4; потрачено $0, незавершённых собственных сборок на входе нет.
L2-0 начат; L2-1 не начат; L2-2 — маршрутная таблица, без нового proof credit.

## L2-0 — опыт специализации

`correct.rs`: `K1MergePerm`, blanket/default = прежний подсчёт произвольной
пробы; специализация `Tagged { key: u64, tag: u64 }` = Copy-снимок входа
(`keys[64]`, маска `u64`) и проверка каждой выходной пары с равенством масок.
Дополнительное requires действует только для Tagged: метки <64 и различны.
Равные ключи разрешены; ключи полные символические u64.
Снимок берётся через `old()`; generic T не клонируется.

Первая сборка: diagnostic, 11 гармоник ×2 мин, `gcb-e2-standard-4`, jobs=1.
Цель — проверить осуществимость и контроли; измерительный зачёт не заявлен.

| Гармоника | Ожидание | Назначение |
|---|---|---|
| `l2_tagged_contract4`, `l2_tagged_contract8` | SUCCESS | реальный `proof_for_contract(bidirectional_merge)`, метки 8..11 и 56..63 |
| `l2_probe_contract4` | SUCCESS | обычный u64, прежняя проба, контроль выбора default |
| `l2_tagged_stub4`, `l2_tagged_stub8` | SUCCESS | stub настоящего merge; независимый oracle сканирует входные пары и маски |
| `l2_probe_stub4` | SUCCESS | stub сохраняет прежнее число проб u64 |
| `l2_contract_mutant_key` | FAILED, `k1_merge_matches` | kani-only копия с тем же постусловием, ключ изменён при сохранённой метке |
| `l2_contract_mutant_label` | FAILED, `k1_merge_matches` | kani-only копия с тем же постусловием, одна пара заменена другой, маска теряет бит |
| `l2_stub_mutant_key`, `l2_stub_mutant_label` | FAILED, `tagged_oracle` | после stub настоящего merge те же мутации нарушают независимую проверку caller |
| `l2_r11_bad_labels` | FAILED, `k1_merge_input_ok` | память и sorted halves корректны, метки повторены |

Мутантные функции не используются через `stub_verified`. Для реального stub
предусмотрены доказательства ровно тех же Tagged/u64, comparator и N.
Длинные прогоны и использование новых контрактов в зачёт ждут исхода L2-0
и GO координатора. Контроли сохраняются отдельно от положительных запросов
итогового CI (при сведении L1).

## L2-2 — тип → фактический маршрут → контракт

Таблица составлена до переноса верхних гармоник на Tagged. Исходники:
`smallsort.rs` (trait dispatch, general, fallback), `merge.rs` (K-10),
`network.rs` (K-10). Luna High, read-only разведка; main проверил условия
`size_of::<T>() <= 16` и `has_efficient_in_place_swap::<T>() <= 8`.

| Тип / вход | Фактический маршрут | Проверяемый контракт / пробел |
|---|---|---|
| u8/u64, stable Freeze и прямой general | general: N8..15 presort4; N>=16 presort8; вставки в половины, merge | K-10 стубит только bm, остальные тела реальные. Для gs N13/14/15 нужен bm ровно N13/14/15; доказанные прежние инстанциации не переносятся на Tagged |
| u8/u64, unstable trait | network, размер <=8, Copy+Freeze | сети9/13 и insertion-хвост; верхние K-10 стубят сети, хвост реальный |
| Tagged16, stable/unstable trait | general, размер16 >8; N>=16 также presort8 | отдельные доказанные инстанциации Tagged/comparator/регионов; не заменяет результаты u8/u64, не свидетельствует о network |
| u8/u64, прямой fallback | insertion_sort_shift_left(offset=1), insert_tail регионов 2..N | прежние K-10 fallback НЕ стубят insert_tail. Главный резерв — отдельные proof с этой заглушкой и предварительным контрактом всех регионов 2..N |
| u8/u64, network N15..17 | sort13 + insertion-хвост | новые fixed-N solver-варианты / контракт insert_tail, без выдачи sortedness за полную перестановку |

Прежний измеренный контракт `insert_tail_net_u64` охватывает 2..17 с
`lt_u64` (RESULT-network, job39). Для u8 есть код гармоники, но самостоятельное
основание полного диапазона пока не установлено; перед новым зачётом перепроверить.
Пробел fallback u64 включает N8, хотя шаг L2-2 назван «9..16».

## Решения R7 / редукции

- D1. Сначала малый diagnostic с таймаутом 2 мин; measurement требует 10 мин
  на гармонику и резервировал бы деньги без пользы до проверки компиляции.
- D2. `Tagged` имеет размер16 и два полных u64 без padding (repr C). Его
  general-маршрут совпадает по presort-порогам с u64; network-маршрут другой.
- D3. Для маски требуется уникальный tag<64 на входе. Это явная предпосылка
  представления H1; метки присваиваются позициям, ключи не ограничиваются.
  Второй регион может иметь ненулевые метки; тестируются также метки 56..63.
- D4. Разрушение ключа и потеря метки проверяются раздельно: surrogate
  `proof_for_contract` использует фактический matcher, caller под настоящим
  stub использует независимый oracle. Это не мутация runtime-кода std.
- D5. Lane и прочие агентские файлы не меняются. Имена agent в schema старые,
  поэтому запрос использует `k1-merge`; роль W3-L2 указана в request_id/purpose.

## Бюджет и builds

Перед первым dispatch выполнить `k1g.sh budget`. Собственный резерв первого
запроса: (11×2 + 30)×$0,0194 = $1,0088, меньше доли $5,4.
Фактическая стоимость после summary: (wall whole run, мин +8)×$0,0194.
Ни `VERIFIED_ARCHIVE`, ни diagnostic gate не объявляются формальным зачётом.

REVIEW REQUEST 7401b1a74e2ff3a5ce90b44aebfed68d756377fa

Файлы: `library/core/src/slice/sort/shared/smallsort.rs` (только attrs),
`library/core/src/slice/sort/shared/smallsort/kani_k1.rs` (mod correct),
`library/core/src/slice/sort/shared/smallsort/kani_k1/correct.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`, данный RESULT.
Результатов Kani ещё нет; новый контракт и шаблон ждут review координатора.

### Build 86f791b7-729b-42e3-bd6c-e22a476e377c — отправлен

Request `w3-l2-specialization-001`, head `0287b2d8` (код `7401b1a7`).
Перед dispatch: used $19,7668, reserved других сборок $1,7072.
После dispatch: общий максимум $22,4828/$33,96; собственный резерв $1,0088.
Фактические статусы/стоимость пока неизвестны. Следующее действие после
пробуждения — summary, peaks, check-tooling против `67a4b452a932d070cf77853a3682c7998de93870`.

### Build 86f791b7 — COMPILE_ERROR, все гармоники NOT_RUN

Summary: gate false, Kani exit1; whole run 51,82 с, max RSS 1768088 KiB,
подготовка до verify 369 с, swap off. check-tooling полностью ok против
`67a4b452a932d070cf77853a3682c7998de93870`.
Ошибка `kani_middle/reachability.rs:476:58`: `Failed to resolve ...
core::kani::Arbitrary::any ... correct::Tagged`. Это подготовка havoc
памяти Tagged в stub, не FAILED проверки постусловия.

D6 (R7). Добавлен явный `impl kani::Arbitrary for Tagged`: оба поля —
неограниченные `kani::any::<u64>()`; предпосылка меток остаётся явной
в контракте. Никаких ограничений ключа или дополнительной редукции.
Повторить те же 11 гармоник, новый request_id и коммит.

Стоимость по формуле (51,82/60+8)×$0,0194 = $0,171955; для своей доли
консервативно округлено вверх: 9 пул-минут, **$0,1746**, нарастающий итог
**$0,1746/$5,4**. Следующий резерв $1,0088; с потраченным $1,1834.

REVIEW REQUEST 3a9a58932296de4b37ba810e560c704e4e4a621c

Продолжение `7401b1a7`: в correct.rs добавлен только unrestricted Arbitrary
для Tagged; остальные изменения — запрос и отчёт. Итоговый список файлов
тот же. Первый build не исполнил ни одной проверки Kani.

### Build d3c8bdd8-3819-4df0-83f9-660aacef3616 — отправлен

Request `w3-l2-specialization-002`, head `4165f2f4` (код `3a9a5893`).
Перед dispatch: общий used $20,2324, reserved других сборок $4,1710;
после — максимум $25,4122/$33,96. Собственный резерв $1,0088,
нарастающие фактические расходы $0,1746. Статусы ещё не получены.
Следующее действие после watch — summary, затем peaks/check-tooling.

### Build d3c8bdd8 — COMPLETE, gate false (ожидаемый текст мутантов)

Head `4165f2f46ed5825686850afb41f58df7becad23d`, Kani `9461e07a`,
whole run 5:59,78, max RSS 1808732 KiB. Peaks: compiler 1,72 GiB,
cbmc 1,37 GiB, max sampled sum RSS 2,01 GiB; swap off, check-tooling ok.

| Гармоника | expected/actual | Время с | failed/total | cover |
|---|---|---:|---|---|
| `l2_tagged_contract4` | SUCCESS/SUCCESS | 42,610 | 0/354 | 1/1 |
| `l2_tagged_contract8` | SUCCESS/SUCCESS | 108,360 | 0/354 | 1/1 |
| `l2_probe_contract4` | SUCCESS/SUCCESS | 51,159 | 0/449 | 1/1 |
| `l2_tagged_stub4` | SUCCESS/SUCCESS | 8,094 | 0/461 | 3/3 |
| `l2_tagged_stub8` | SUCCESS/SUCCESS | 30,004 | 0/461 | 3/3 |
| `l2_probe_stub4` | SUCCESS/SUCCESS | 5,640 | 0/474 | 2/2 |
| `l2_contract_mutant_key` | FAILED/FAILED | 3,097 | 1/287 | 1/1 |
| `l2_contract_mutant_label` | FAILED/FAILED | 3,078 | 1/287 | 1/1 |
| `l2_stub_mutant_key` | FAILED/FAILED | 6,510 | 1/461 | 2/3 |
| `l2_stub_mutant_label` | FAILED/FAILED | 6,830 | 1/461 | 2/3 |
| `l2_r11_bad_labels` | FAILED/FAILED | 0,521 | 1/372 | 1/1 |

Отрицательные caller-контроли не доходят до последнего cover после
преднамеренно падающего assertion; оба cover до него выполнены.
Положительные гармоники выполнили все свои covers.

Два surrogate-мутанта: фактически упало ровно постусловие
`k1_merge_matches` (correct.rs:236,237). Kani печатает его в несколько строк;
summary сохраняет description первой строки `| _ | CopyOnDrop :: < Tagged > ::`.
Поэтому заданный `expect_check=k1_merge_matches` не совпал, expectation met=false.
Ограниченный `log-lines 2730 32` подтвердил полный текст matcher и location;
raw logs не открывались. Caller-мутанты падают на `tagged_oracle`, correct.rs:182;
R11 — `k1_merge_input_ok`, smallsort.rs:862.

D7 (R7). Только два surrogate-контроля повторяются с expect_check,
совпадающим с первой строкой. Код L2-0 не меняется (кроме импорта lt_u8).
Остальные девять гармоник уже дали ожидаемые статусы, новых причин их
повторять нет. L2-0 пока не объявлен закрытым; GO review ещё не получен.

Стоимость (359,78/60+8)×$0,0194 = $0,271529; консервативно 14 минут,
$0,2716. Нарастающий итог **$0,4462/$5,4**.

## L2-2 — первый измерительный шаг

Добавлены fixed-N fallback с `stub_verified(insert_tail)`, cadical,
массивы ровно N, те же lt_u8/lt_u64 и полная произвольная проба, без редукции
значений. N8(u64)/N9(u8) — прежние первые TIMEOUT; N16 — верхняя граница.
Новый proof_for_contract u8: префиксы размера2..17 массива17, сохранение
суффикса, covers2/16/17; по образцу `network::insert_tail_prefix_u64`.
Для u64 этот шаблон уже SUCCESS в job58 (`432813d9`, 471,659 с, cover4/4).
`insert_tail` и его спецификация с того доказательства не менялись;
для применения к массивам N8/9/16 сохраняется раскрытая общая посылка
переноса той же функции на другую аллокацию. Требование R4 включает
u8 proof в следующую сборку; пока SUCCESS не получен, зачёта caller нет.
R11 insert_tail отдельно нарушает только sorted-prefix requires, expect FAILED
`k1_tail_pre`. Новые fallback-гармоники не используют bm и не зависят от L2-0.
Первый решатель cadical; варианты kissat/minisat — при оставшемся пробеле.

Следующий запрос: measurement, восемь гармоник ×10 мин. Собственный резерв
(80+30)×$0,0194=$2,1340; с уже потраченным максимум $2,5802 < $5,4.
Длинные N20/24/32 по L2-1 ещё не запускаются.

REVIEW REQUEST 8e499dcda307b2a9db6d56ecb46434f25cb68737

Итоговые файлы: `smallsort.rs` (контрактные attrs L2-0), `kani_k1.rs`
(mod correct), `kani_k1/correct.rs` (L2-0 плюс новый fallback/template u8
insert_tail prefix/R11), `RUN-REQUEST.json`, `RESULT-w3-l2.md`.
Изменения L2-2 только в correct.rs; runtime/lane неизменны.
