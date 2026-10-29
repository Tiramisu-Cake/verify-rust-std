# OPTION-OPTIN — вариант только для владельца

`OPTION-OPTIN.patch` — **неприменённый вариант на рассмотрение владельца**. Он
добавляет `#[cfg(kani_smallsort_controls)]` к 19 вызовам макросов, создающим
проверочные функции Kani. При применении патч исключит их из обычного набора;
конфигурация `kani_smallsort_controls` оставит функции доступными как
контрольные. Тела проверок и их домены патч не сужает.

Этот вариант не решает проблему остальных проверок, попавших под наш
120-секундный скрининг в GCB. Это скрининг-бюджет GCB, а не таймаут
организаторов: на macOS у организаторов таймаут autoharness — 600 секунд.

Атрибут `cfg` стоит перед вызовом макроса на уровне item. Он управляет самим
вызовом, а значит и созданной им проверочной функцией.

## Точные имена проверок

- `merge::merge_contract_u64_n16`
- `network::insertion_permutation_u64_n12`
- `network::insert_tail_contract_u64_start1_tail2`
- `network::insert_tail_contract_u64_start1_tail3`
- `network::insert_tail_contract_u64_start1_tail4`
- `network::insert_tail_contract_u64_start1_tail5`
- `network::insert_tail_contract_u64_start1_tail6`
- `network::insert_tail_contract_u64_start1_tail7`
- `network::insert_tail_contract_u64_start1_tail8`
- `network::insert_tail_contract_u64_start1_tail9`
- `network::insert_tail_contract_u64_start1_tail10`
- `network::insert_tail_contract_u64_start1_tail11`
- `network::insert_tail_contract_u64_start1_tail12`
- `network::insert_tail_contract_u64_start1_tail13`
- `network::insert_tail_contract_u64_start1_tail14`
- `network::insert_tail_contract_u64_start1_tail15`
- `network::insert_tail_contract_u64_start1_tail16`
- `merge::general_sorted_permutation_u64_n16`
- `merge::stable_sorted_permutation_u64_n16`

Всего 19 вызовов макросов: 1 проверка контракта merge, 1 проверка
перестановки при сортировке вставками, 15 проверок для точных концов и
2 проверки маршрутов сортировки.

## Домены, исключаемые из обычного набора

- `merge::merge_contract_u64_n16` проверяет контракт
  `bidirectional_merge` на точной длине 16: вход — произвольный полноширинный
  `[u64; 16]`, назначение — отдельный неинициализированный
  `[u64; 16]`. Предусловия контракта, включая упорядоченность половин,
  сохраняются.
- `network::insertion_permutation_u64_n12` выполняет реальную сортировку
  вставками на произвольном полноширинном `[u64; 12]`, с произвольным probe и
  недетерминированными результатами сравнений. Проверка устанавливает
  сохранение кратности значений относительно произвольного probe; отдельный
  cover показывает достижимый случай, когда элементы перемещаются.
  Перемещение не требуется для каждого входа.
- Пятнадцать проверок `network::insert_tail_contract_u64_start1_tail2` …
  `network::insert_tail_contract_u64_start1_tail16` задают все точные концы
  `tail` от 2 до 16 при `start == 1`. Вместе они покрывают прежний диапазон
  концов для start 1 на произвольном полноширинном `[u64; 17]`. Каждая проверка
  сохраняет предусловие контракта `insert_tail`, `lt_u64`, проверки
  неизменности памяти вне изменяемой области и cover своего точного конца.
  Применение патча исключит все 15 этих случаев из обычного набора.
- `merge::general_sorted_permutation_u64_n16` и
  `merge::stable_sorted_permutation_u64_n16` вместе проверяют оба маршрута на
  произвольных полноширинных `[u64; 16]`. Стабильный маршрут сохраняет
  scratch-массив длиной 48; оба маршрута сохраняют проверки упорядоченности и
  сохранения общего probe.

## Зависимость проверок от stubs

Обе проверки N16 для общего и стабильного маршрутов используют
`stub_verified(bidirectional_merge)`. `merge::merge_contract_u64_n16` —
соответствующая проверка контракта merge для длины 16. При выборе этого
варианта для обычного набора из него совместно исключаются обе проверки N16
маршрутов и поддерживающая их проверка контракта merge.

Проверки для точных концов используют `proof_for_contract(insert_tail)`;
патч не меняет предусловия или тела этих проверок. У
`network::insertion_permutation_u64_n12` нет заглушки для проверенной операции.

Проверка патча выполнена только командой `git apply --check`. Патч не
применялся; компиляторы, сборки и проверки Kani не запускались.
