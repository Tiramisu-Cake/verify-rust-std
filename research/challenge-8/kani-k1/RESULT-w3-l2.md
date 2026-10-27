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
