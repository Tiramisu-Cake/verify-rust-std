# OPTION-OPTIN — вариант только для владельца

`OPTION-OPTIN.patch` — **неприменённый вариант на рассмотрение владельца**. Он
добавляет `#[cfg(kani_smallsort_controls)]` к 19 вызовам макросов с
proof harnesses. При применении патч исключит их из обычного набора Kani;
конфигурация `kani_smallsort_controls` оставит harnesses доступными как
контрольные. Тела proofs и их домены патч не сужает.

Этот вариант не решает проблему остальных harnesses, попавших под наш
120-секундный скрининг в GCB. Это скрининг-бюджет GCB, а не таймаут
организаторов: на macOS у организаторов таймаут autoharness — 600 секунд.

Атрибут `cfg` стоит перед вызовом макроса на уровне item. Он управляет самим
вызовом, а значит и созданным им proof harness.

## Точные имена harnesses

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

Всего 19 вызовов макросов: 1 merge contract, 1 insertion permutation,
15 exact-tail proofs и 2 проверки маршрутов сортировки.

## Домены, исключаемые из обычного набора

- `merge::merge_contract_u64_n16` проверяет контракт
  `bidirectional_merge` на точной длине 16: вход — произвольный полноширинный
  `[u64; 16]`, назначение — отдельный неинициализированный
  `[u64; 16]`. Предусловия контракта, включая упорядоченность половин,
  сохраняются.
- `network::insertion_permutation_u64_n12` выполняет реальный insertion sort
  на произвольном полноширинном `[u64; 12]`, с произвольным probe и
  недетерминированными результатами сравнений. Proof проверяет сохранение
  кратности значений относительно произвольного probe; отдельный cover
  показывает достижимый случай, когда элементы перемещаются. Перемещение не
  требуется для каждого входа.
- Пятнадцать harnesses `network::insert_tail_contract_u64_start1_tail2` …
  `network::insert_tail_contract_u64_start1_tail16` задают все точные концы
  `tail` от 2 до 16 при `start == 1`. Вместе они покрывают прежний диапазон
  концов для start 1 на произвольном полноширинном `[u64; 17]`. Каждый proof
  сохраняет предусловие контракта `insert_tail`, `lt_u64`, проверки frame и
  cover своего точного конца. Применение патча исключит все 15 этих случаев
  из обычного набора.
- `merge::general_sorted_permutation_u64_n16` и
  `merge::stable_sorted_permutation_u64_n16` вместе проверяют оба маршрута на
  произвольных полноширинных `[u64; 16]`. Stable-маршрут сохраняет scratch
  длиной 48; оба маршрута сохраняют проверки отсортированности и сохранения
  глобального probe.

## Зависимость проверок от stubs

Оба N16 harness для general/stable маршрутов используют
`stub_verified(bidirectional_merge)`. `merge::merge_contract_u64_n16` —
соответствующая проверка контракта merge для длины 16. При выборе этого
варианта для обычного набора из него совместно исключаются оба N16 proof
маршрута и поддерживающий их merge contract.

Exact-tail harnesses используют `proof_for_contract(insert_tail)`; патч не
меняет предусловия или тела этих proofs. У
`network::insertion_permutation_u64_n12` нет verified-operation stub.

Проверка патча выполнена только командой `git apply --check`. Патч не
применялся; компиляторы, сборки и proofs не запускались.
