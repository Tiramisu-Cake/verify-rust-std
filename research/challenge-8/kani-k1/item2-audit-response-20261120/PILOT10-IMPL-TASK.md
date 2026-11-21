# Кампания 10. Оставшиеся no-merge длины network

Подготовить одну кампанию для **N0, N1, N3–7, N10, N11, N14 и N15**. В кампании 9 получены ожидаемые native исходы на N2, N8, N9, N12, N13, N16 и N17. У N01 был timeout 301,143 с при 2,65 GiB. Последние отметки показывают разворачивание actual `insert_tail` и insertion loop, а завершение symex и первая CNF в bounded stdout отсутствуют. Разворачивание показывает исследованную ветку CBMC. Реальный вызов вставки для входа длины 0 или 1 оно не устанавливает. В кампании 10 использовать два отдельных литеральных ранних возврата. Офлайн-qualification кампании 9 ведётся отдельно. [Сводка кампании 9](run-44862241314/SUMMARY.md) · [Чек-лист qualification](QUALIFICATION-CHECKLIST.md)

## Std и доказательные обязательства

База `d968b9a8c341485e4df63ad852ac0806f37bb71b`, tree `d8eaa9033b531e8be2413599e19315f294c5aafb`, worktree `/root/verify-rust-std-ch8-q-pilot-v1`. Один новый локальный commit поверх базы, только добавления harnesses в `smallsort/verify/sorting_q_pilot.rs`. Существующие harnesses и controls сохраняются. Runtime, контракты листьев, компаратор, q-модель и регистрация побайтно сохраняются.

- Все новые корни — `#[kani::proof]`, `#[kani::unwind(36)]` и normal-only `#[cfg(not(kani_smallsort_q_controls))]`. Использовать независимые `kani::any()` для `[u8;34]` и `q: u8`, сохранить `before=v`, проверить активность `u8/KeyLess<u8>`. Actual `small_sort_network(&mut v[1..K], &mut f)` получает срез с литеральным концом `K=1+n`. Runtime sort9, sort13 и insertion loop сохраняются. `--no-assert-contracts` оставляет sort13 в режиме Original, поэтому контрактный `requires(len==17)` в N14/N15 не применяется.
- У N0 и N1 вызовы на `v[1..1]` и `v[1..2]` соответственно, оба набора stubs пусты. После вызова проверить `v==before` и `f.q()==q`. Равенство всего backing фиксирует frame и точный результат на пустом/одноэлементном срезе. Использовать метки с префиксами `N00_PLAIN_` и `N01_LITERAL_PLAIN_`. Проверить `ACTIVE`, `UNCHANGED`, `Q_FRAME`; covers `Q_ZERO`, `Q_MAX`, `USEFUL_RETURN` после утверждений. У N1 ещё `Q_ABSENT` по `before[1]!=q`. Символьный выбор длины, отдельный цикл frame и вызовы общего q-oracle здесь не нужны.
- Для N3–7/N10/N11/N14/N15 сохранить схему кампании 9. `order_target` по всему логическому входу до вызова, затем `order_post` по тому же срезу, q-frame и byte frame по всем остальным индексам V34. Уникальные метки `Nnn_PLAIN_ACTIVE/QPOST/Q_FRAME/OUTSIDE_VALUE_FRAME` и все шесть covers `MIXED_THRESHOLD`, `THRESHOLD_TIES`, `Q_ZERO`, `Q_MAX`, `Q_ABSENT`, `USEFUL_RETURN`. `Q_ABSENT` проверяет активный вход, полезный возврат расположен после вызова и проверок.

## Exact roster

Общий префикс selector — `slice::sort::shared::smallsort::verify::`. Все строки normal / Proof. В колонке Replace указан полный набор verified stubs, ordinary stubs пусты. У 11 positives ожидается `SUCCESS`.

| № | Root ID | Суффикс selector | Активный срез | Replace | Child, с | Actual маршрут, относительные tails |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | N00-PLAIN | `sorting_q_pilot::n00_literal_plain_no_merge` | `v[1..1]` | ∅ | 300 | Ранний возврат |
| 2 | N01-LITERAL-PLAIN | `sorting_q_pilot::n01_literal_plain_no_merge` | `v[1..2]` | ∅ | 300 | Ранний возврат |
| 3 | N03-PLAIN | `sorting_q_pilot::n03_plain_no_merge` | `v[1..4]` | insert | 600 | Tails 1–2 |
| 4 | N04-PLAIN | `sorting_q_pilot::n04_plain_no_merge` | `v[1..5]` | insert | 600 | Tails 1–3 |
| 5 | N05-PLAIN | `sorting_q_pilot::n05_plain_no_merge` | `v[1..6]` | insert | 600 | Tails 1–4 |
| 6 | N06-PLAIN | `sorting_q_pilot::n06_plain_no_merge` | `v[1..7]` | insert | 600 | Tails 1–5 |
| 7 | N07-PLAIN | `sorting_q_pilot::n07_plain_no_merge` | `v[1..8]` | insert | 600 | Tails 1–6 |
| 8 | N10-PLAIN | `sorting_q_pilot::n10_plain_no_merge` | `v[1..11]` | swap, insert | 600 | Sort9 × 25, tail 9 |
| 9 | N11-PLAIN | `sorting_q_pilot::n11_plain_no_merge` | `v[1..12]` | swap, insert | 600 | Sort9 × 25, tails 9–10 |
| 10 | N14-PLAIN | `sorting_q_pilot::n14_plain_no_merge` | `v[1..15]` | swap, insert | 600 | Sort13 × 45, tail 13 |
| 11 | N15-PLAIN | `sorting_q_pilot::n15_plain_no_merge` | `v[1..16]` | swap, insert | 600 | Sort13 × 45, tails 13–14 |
| 12 | N02-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n02_plain_qpost_corrupt` | `v[1..3]` | insert | 300 | `FAILURE` ровно `N02_CORRUPT_QPOST` |
| 13 | N17-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n17_plain_qpost_corrupt` | `v[1..18]` | swap, insert | 600 | `FAILURE` ровно `N17_CORRUPT_QPOST` |

Два прежних controls дают на новом pin чувствительность общего q-oracle для insertion-only и смешанной схемы. Сохранить все три covers каждого контроля, включая нулевой вход, q=1 на пути порчи и полезный возврат. Для N0/N1 достаточно равенства V34 и отдельных covers возврата. P‑1/P‑3, false-OR и swap-only control остаются в пакете кампании 9. Для использования P‑1/P‑3 и покрытия прежних длин офлайн нужны результат qualification кампании 9 и сверка переноса на новый std commit. Сверять побайтные тела, атрибуты, контракты, cfg и профиль, совместимость доменов и сохранение проверок caller Pre. До подтверждения этого переноса новые результаты с Replace остаются условными. Для N0/N1 такая зависимость отсутствует. [Матрица режима и доменов](PILOT9-IMPL-TASK.md) · [Правила сверки](QUALIFICATION-CHECKLIST.md)

## Control, пределы и handoff

- От control v9 `baad011375b727383f7ea0abe429763c1a78ab13` из `/root/kani-ch8-q-pilot-control-v9` подготовить локальный `experiment/ch8-q-pilot-control-v10` с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Workflow, event ref, guard, sample/receipt и cleanup из v9 сохранить. Дельта ограничена roster, request с новыми std pins/hashes и fixture expectations тестов. Runner собирает bounded raw наблюдения, результаты и перенос доказательств оцениваются офлайн.
- Tool `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, CaDiCaL, object bits **12**, `--exact`, `--jobs=1`, unwind36, `--no-assert-contracts`, normal cfg и OFF-профиль с обычными memory/overflow/unwind checks. Extra CBMC args пусты. Отдельные target dirs. Local nominal cap **10 GiB**, outer 12 GiB, резерв 2 GiB и прежняя формула effective cap. Сохранить 16/1/8 MiB на stdout/stderr/export и 256 MiB aggregate artifact. Сохранять lifecycle, PGID и component RSS, effective cap и исходную причину остановки по каждому root.
- **6 900 с child budget** (10 × 600 и 3 × 300), включая компиляцию. В job 180 мин с setup/build ≤30 мин и резервом финализации/upload 540 с остаётся 26 мин. Latest start вычисляется по timeout корня плюс 30 с до supervisor cutoff. При остановке сохранять уже собранные результаты, для невыполненного — `NOT_RUN` и причину. Длительности N8/N12/N16/N17 из кампании 9 дают ориентиры. Потребность отдельных новых длин в ресурсах ещё не измерена.
- Локально сверить дельту std и 13 selectors, runtime routes, геометрию, Replace, covers и бюджеты. Выполнить rustfmt check-only для добавленного кода, `validate` с синтетическими GitHub metadata, `check-source` и `python3 -m unittest -v test_run.py`. Проверить exact roster, отклонение дрейфа cfg/argv/лимитов, оба окна latest start, отдельные target dirs и существующие error paths. Подготовить `PILOT10-IMPL-HANDOFF.md` с pins/trees, хешами request/workflow и проверками. Коммиты `[skip ci]`, `Tiramisu-Cake <igkharin@gmail.com>`, без Co-Authored-By.
- Задача заканчивается подготовленным локальным кандидатом. Request остаётся `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Cargo, rustc, Kani, CBMC, CI и push вне этой задачи. Запуск потребует review и отдельного GO. [База control и профиль](PILOT9-IMPL-HANDOFF.md)
