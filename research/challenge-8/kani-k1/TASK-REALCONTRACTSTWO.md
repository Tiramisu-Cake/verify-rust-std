# REALCONTRACTSTWO — спайк, шаг 2: домены для композиции, `insert_tail` и `sort4_stable`

**Выдано координатором 2026-11-04 (ночь) после RESULT-REALCONTRACTS (`d648179493`).** Dispatch только после
exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-realcontractstwo**, ветка **experiment/kani-k1-realcontractstwo-20261104**
  от **d648179493**. В ветке уже есть контракты на `swap_if_less` и `insertion_sort_shift_left` и
  `verify/realcontracts.rs`.
- Slug **realcontractstwo**; stable owner — свободный на момент dispatch (указать в PRE-BUILD). Request_id
  `realcontractstwo-*`.
- Project cap **$118.96**, свой cap **$3.00**. **До двух сборок**: G1, затем G2 по итогам G1 и с новым GO.
  Один compile-error repair на сборку. Tooling base: **59893bff1f**.
- Окно: main 240 + closeout 30 мин.

## Что известно из шага 1

- Контракт на настоящем `swap_if_less` доказан PFC на backing 4 (u8, u64, `[u8; 17]`).
- `stub_verified(swap_if_less)` работает на реальном маршруте сети u8 N9/N13. Но summary используется на backing
  9 и 13, а PFC был на backing 4, поэтому это ещё не засчитываемая композиция.
- PFC `insertion_sort_shift_left` проходит для len 2/3 (81–105 с); len 1..6 в одном корне — TIMEOUT.

## Что сделать

1. **Домены для честной композиции `swap_if_less`.** PFC на backing 9 и 13 для u8, тот же произвольный компаратор,
   позиции `kani::any()` в пределах backing. Тогда N9/N13 consumers из шага 1 опираются на доказанный домен.
   Записать в RESULT, совпадают ли домены consumer и PFC (тип, backing, компаратор).
2. **`insert_tail`:** `requires`/`modifies` прямо на функции по её safety-комментарию: `begin < tail`, все
   `begin..=tail` валидны и инициализированы, одна аллокация. `modifies` — диапазон `begin..=tail`. PFC на u64,
   tail offset 1..4 в backing 5 (отдельными корнями, если одним не пройдёт). Негативный контроль: consumer с
   `stub_verified(insert_tail)` и `tail == begin` должен упасть на `requires`.
3. **`sort4_stable`:** `requires`/`modifies` по контракту функции: `v_base` читаем на 4 элемента, `dst` записываем
   на 4 элемента, области не пересекаются, `T: Freeze`, если это требуется сигнатурой. PFC на u64 (и при запасе
   `[u8; 16]`).

`ensures` про порядок в этот шаг не входят. Тела и сигнатуры runtime-функций не менять; если для `requires`
нужен helper, он должен быть под `cfg(kani)`.

## Сборки

- **G1:** kind diagnostic, `controls: true`, jobs 1, лимит 10 мин. Строки пунктов 1–3 плюс одна регрессия
  существующего ordinary-корня, который вызывает `insert_tail`. Не больше 8 строк.
- **G2** (необязательная, с GO): разбиение того, что упало по TIMEOUT, или следующий хелпер (`bidirectional_merge`).

## Коммиты, ожидание, RESULT

- Library- и research-коммиты отдельно, `[skip ci]`, push без force. Последней строкой
  `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.
- **RESULT-REALCONTRACTSTWO.md**, ≤ 35 строк:
  - точный текст новых контрактов;
  - таблица строк;
  - какие пары consumer/PFC теперь совпадают по домену;
  - что из этого переносится в ordinary-кандидаты;
  - что дальше.

## Запреты

- Только bounded evidence; raw logs и credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani; чужие PR, их ветки и код не открывать.
- Тела runtime, workflows и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **REALCONTRACTSTWO ЗАВЕРШЁН**, затем стоп.
