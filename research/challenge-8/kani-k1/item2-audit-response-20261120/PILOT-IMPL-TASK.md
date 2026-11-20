# Задание воркеру на реализацию q-пилота

Подготовить локальный кандидат из исходников std и отдельного fork control. Цель первой
кампании — проверить пороговую композицию на настоящем `small_sort_network` для N17,
с четырьмя положительными корнями и тремя контролями. Решение владельца зафиксировано
на `543d32cccc81c9ff71752642caeb11a6ade74733`. Контракт этапа и границы результата описаны в
[NEXT-STAGE.md](NEXT-STAGE.md), [RESPONSE-RU.md](RESPONSE-RU.md) §§2–3 и
[PILOT-LIGHT-LANE.md](PILOT-LIGHT-LANE.md).

## Точные входы и выходы

| Часть | Точка отсчёта | Локальный результат |
| --- | --- | --- |
| std | `7b31b060b90ce286e94547993f6a698c549bc5fa`, tree `fccf3284bd678626c8f8cea72bbe6ec72964dbd9` | В новой worktree ветка `experiment/ch8-q-pilot-v1`, один commit поверх этой базы. |
| Kani tool | `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` | Read-only pin. |
| Fork control | `65a9ea656a4b5f1e66f7b31eceffb5eefeba7541`, tree `09938d27a127351f5c51b6c9f451602d797a1c0f` | В новой worktree ветка `experiment/ch8-q-pilot-control-v1`, один commit с request, ссылающимся на точный реализованный std commit. |

Оба commits с `[skip ci]`, автор и коммитер `Tiramisu-Cake <igkharin@gmail.com>`, без
`Co-Authored-By`. Полные SHA новых commits появляются в handoff. Будущий trigger ref
`uninit-ci/ch8-q-pilot-v1` принадлежит координатору и требует review, отдельного GO и ledger.
Исходные worktrees и ветки не переиспользовать для записи. Воркер готовит локальные commits,
проверки и handoff до передачи на независимое ревью. Публикация и native CI вне этой реализации.

## Файлы std и режимы

Все пути начинаются с `library/core/src/slice/sort/shared/`:

- `smallsort.rs` — verification-only attrs для `swap_if_less`, `sort13_optimal` и `insert_tail`.
  Сохранить safety requires и прежние modifies swap/insert. Для `sort13_optimal` точно описать
  первые 13, с полным frame хвоста. Не менять runtime bodies и generic signatures.
- `smallsort/verify.rs` — выделенная регистрация трёх новых модулей, cfg guards и проверка
  взаимоисключения S2 и q-режима. Сохранить прежние модули и ordinary inventory по исходникам.
- `smallsort/verify/sorting_model.rs` — q-поле в `KeyLess<T>` только под q cfg и явный `with_q`.
  Сохранить `new()` и сравнение полных байтов в `call_once`/`call_mut`. Старый `new()` не
  используется новыми положительными корнями.
- `smallsort/verify/sorting_q_model.rs` — guarded facade для `u8/KeyLess<u8>`, owned capture,
  q-монотонность, pair/shift и order-stat посты. Использовать bounded булев DP по индикаторам
  `value>=q`. Вычислять `at_least` из входного префикса один раз на проверку.
- `smallsort/verify/sorting_q_pilot.rs` — четыре положительных корня. Общая реализация fixture
  допустима, если PFC target остаётся однозначным на данном пине и реальные вызовы видны в review.
- `smallsort/verify/sorting_q_controls.rs` — три корня, описанные ниже.

Нормальный `RUSTFLAGS` — `--cfg=kani_smallsort_sorting --cfg=kani_smallsort_q_pilot`, с
`cfg(kani)` от инструмента. Только P-5a/b добавляют `--cfg=kani_smallsort_q_controls`.
Они включают ложный AND→OR пост у actual `swap_if_less`. В этом режиме компилируются
корни P-5a/b, положительные providers/consumers и P-5c исключены. P-5c регистрируется
в нормальном q cfg и меняет только harness output. Вся отличающаяся геометрия/логика
разрешена лишь в проверочных модулях. Дизъюнкция cfg для Kani safety attrs и её дополнение
для `safety::requires` должны давать те же clauses в ordinary и старых режимах. Q cfg
включает эквивалентные safety clauses даже при выключенном `kani_smallsort_s2_assumed`.
Взаимоисключение не затрагивает ранее доступные сочетания без q cfg.

`old(...)` захватывает значения/биты и q, а не заём изменяемого среза. Проверить definedness
с учётом раскрытия `old` и `modifies`: guard inactive pair внутри capture до любых чтений
и предотвращение invalid slice/offset ещё до чтения. В `sort13_optimal` q-контракт можно
сразу ограничить `len==17` для активной пары, с total prefix target и `modifies` только
первых 13 элементов. Для `insert_tail` q pre — initialized/writeable same-allocation span,
length 2..17 и q-монотонность `[begin,tail)`. Если атрибут контракта выражает более широкий
домен, manifest провайдера фиксирует проверенные T/F, длины, offsets, allocation и точный q-domain.
Все captures и bounds должны быть определены в Check и Replace. Specs утверждают q-frame,
`modifies` не расширяется на компаратор или хвост. Нет loop contracts, compiler workaround
с ослаблением checks, `kani::stub` или PANIC stub.

## Семь exact roots

Селектор начинается с `slice::sort::shared::smallsort::verify::`, затем модуль и `::` с именем
из таблицы. Каждый root получает unwind36 и свой свежий процесс. Все initialized V34
имеют независимо символьные полные u8. В positive PFC и consumers брать независимый
`let q: u8 = kani::any()` и передавать тот же компаратор через actual call graph. Значения
могут подпадать под именованный `Pre(X,q)` контракта, например q-монотонность префикса P-3.
Consumer утверждает тот же Pre в Replace. Запрещены дополнительные assumes, ограничения
q через данные, константа в positive constructor или переписывание q после havoc.

| ID и селектор после общего префикса | Реализация и проверяемые роли |
| --- | --- |
| P-1 `sorting_q_pilot::p1_swap_u8_v34_q_any` | Actual `proof_for_contract(swap_if_less)` без stubs. Base 0..20, a,b 0..12, a=b допустимо. Min/max биты AND/OR, полный frame прочих позиций V34, неизменный q. Cover swapped, untaken/reversed, equal indices, split threshold и полезного возврата. |
| P-2 `sorting_q_pilot::p2_sort13_u8_b01_len17_q_any` | `proof_for_contract(sort13_optimal)` и `stub_verified(swap_if_less)`. Actual `&mut v[1..18]`. Order-stat q для `[1..14]`, byte frame `[14..18]` и внешних позиций V34, q-frame. Сопоставить все 45 swap calls с P-1 на base1. Cover activation, mixed threshold/ties и полезный возврат. |
| P-3 `sorting_q_pilot::p3_insert_u8_b01_rel1_16_q_any` | Actual `proof_for_contract(insert_tail)` без stubs. Base1, relative tail ∈1..16. В contract pre включить q-монотонность, без numeric sorted premise. Для tail≥q ожидается старый вектор префикса с единицей в конце. Иначе ноль в начале и префикс сдвигается. Assert q-post и frame, cover всех 16 tails, early return, full sift и q-монотонного численно неотсортированного префикса. |
| P-4 `sorting_q_pilot::p4_network_u8_b01_n17_q_any` | `proof`, `stub_verified(sort13_optimal)` и `stub_verified(insert_tail)`. Actual `small_sort_network(&mut v[1..18], &mut f)`, в том числе actual `insertion_sort_shift_left`. P-2 покрывает вызов на len17, P-3 покрывает tails13..16 под одним q. Assert N17 order-stat q, q/outside-value frame, covers mixed threshold/ties, q=0/q=255 и полезного возврата. |
| P-5a `sorting_q_controls::p5_swap_false_or_q_any` | Actual `proof_for_contract(swap_if_less)`, как P-1 в mutant cfg, arbitrary q. Нужен failure единственной назначенной q-ensures property с различными входными индикаторами. |
| P-5b `sorting_q_controls::p5_swap_false_or_q_fixed0` | Тот же mutant и геометрия, q=0. Native SUCCESS ожидаем, поскольку все индикаторы единицы. Не предъявлять coverage, требующее q>0 или mixed threshold в этом корне. Отказ fixed0 в provider gate проверяется отдельным синтетическим тестом. |
| P-5c `sorting_q_controls::p5_network_n17_qpost_corrupt` | Normal cfg, stubs как P-4. После actual network записать 255 в конкретную позицию, если исходный срез был `[0;17]`. Для q>0 до порчи там гарантирован нулевой индикатор даже при havoc байтов. Cover пути с исходным `[0;17]`, q=1, возвратом и порчей. Ожидается лишь назначенный `q`-post FAILURE. |

Для positives сохранить meaningful covers на replayable domain, в том числе граничные q
и разные индикаторы, где применимо. Assert activation, полезный frame и invariants явными
именованными ролями. Для P-5a/b общий fixture и ложный контракт, меняется домен q и
согласованные с ним требования к covers. Непойманные safety/unwind/panic warnings, compile
failure, missing metadata binding или неожиданная property не подтверждают ожидаемый контроль.
Положительный q-результат P-4 зависит от P-1/P-2/P-3 и не превращается в приёмочный proof.

## Файлы control и проверки перед публикацией

Добавить только `.github/workflows/ch8-q-pilot.yml` и `ch8-q-pilot-control/{CI-REQUEST.json,run.py,test_run.py}`.
`CI-REQUEST.json` фиксирует source/tool pins и trees, профиль, root order, selectors, cfg,
domain и expected role/cover/control map, source files и их hash. Зафиксировать точные
ожидаемые modes, PFC targets и verified stub graph. Не предсказывать native property IDs
там, где для них ещё нет измерения. Для обязательных ролей дать различающие literal labels
и привязку к callee/site, а при неоднозначности вернуть `UNKNOWN`. В request/record отдельно
хранить `all_u8` и `{0}` как разные домены. `test_run.py` проверяет, что native SUCCESS с
`{0}` отвергается для универсальной композиции с `Q_DOMAIN_NOT_UNIVERSAL`, а корректный
P-1 с `all_u8` проходит именно проверку домена. Это синтетическая проверка поля и правила.
Source review устанавливает соответствие этого поля реальному генератору входов.

До передачи на review выполнить `git diff --check` в обеих worktrees, static Rust
source/cfg correspondence, сверку old vs new ordinary clauses/bodies, exact names/paths,
баз, деревьев, hashes, YAML/JSON schema и types. Локальный уже установленный `rustfmt`
допустим в check-only режиме на изменённых Rust-файлах, с настройками пина и без рекурсии
в другие модули. Если бинаря нет или он не может прочитать experimental syntax, сохранить
`NOT_RUN` или точную ошибку и использовать статический просмотр. Не ставить новый toolchain
на VPS ради форматирования. Для runner выполнить новый targeted synthetic набор из дорожки,
включая bounded containment/cleanup и stock vs rich record agreement. Проверить, что launcher
использует frozen pins/cfg, exact singleton, caps и отказ на повреждённом manifest. Проверки
локальные и не запускают cargo, rustc, Kani, CBMC, CI или скрипты аудитора. Native discovery,
компиляция, timings, условия PFC и исходы семи roots остаются `NOT_RUN` до dispatch.

В handoff независимому ревьюеру и координатору передать пути worktrees, обе ветки, полные
commit/tree/parent IDs и tool pin, request/workflow/runner hashes, cfg → selectors,
provider → call/domain map, проверенные commands/results, ограничения и точные blockers.
Указать предложенные лимиты и будущий trigger ref, state `READY_FOR_REVIEW` либо `BLOCKED`,
native `NOT_RUN`, `GO=NOT_GRANTED`, `proof_credit=NONE`. Следующий этап указан в
[PILOT-REVIEW-TASK.md](PILOT-REVIEW-TASK.md).
