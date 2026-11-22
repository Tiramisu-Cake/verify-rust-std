# #752: прямые контракты на trait-методах `small_sort` — бриф координатора (2026-11-22)

## Что изменилось
- Организаторы обновили пин Kani в verify-rust-std до `9834c96ce90ff57d8495416530b080dc3d52ce25` (upstream #784, merged 2026-11-21). В пин входят kani#5135 (proof_for_contract на trait-методе с собственным generic `F`) и kani#5153 (контрактные атрибуты на specialization `default fn`, закрыл kani#5116).
- Прогон: голова #752 `872d5a43380752786415bc00d2a12ce0e930cb37`, слитая с upstream main `b5adb2c5c9ace62ae847833e33e008a53186fac7` (пин 9834c96ce9) = коммит `5402b33188d51d4c30e1302af710a27c7a60d831` (ветка форка `ci/ch8-pin9834-20261121`, чистый merge-tree). Workflow организаторов kani.yml в форке, run 44946596047: SUCCESS, все 16 джобов, 235/235 harness Challenge 8, 0 failures. Самый долгий шард — partition 2 macOS, 77 мин.

## Цель
Закрыть оговорку «Contracts on the trait methods» из Limitations #752: контракты (сортировка) прямо на `<T as StableSmallSortTypeImpl>::small_sort`, `<T as UnstableSmallSortTypeImpl>::small_sort`, `<T as UnstableSmallSortFreezeTypeImpl>::small_sort`, включая specialization `default fn`, и `proof_for_contract` для них на пине 9834c96ce9.

## Заготовка
G3 (commit `70ba5befc617627073738e26cb1466bd4fb76e41`, ветка `experiment/kani-k1-traitpfc-20261110`): `RESULT-TRAITPFC-G3.md`, `traitpfc/g3/build2/library.patch`, `contracts.json`. Модель `SortModel<T, F>`, `ensures` с `old(...)` на трёх trait-методах; bounded PASS для u64/canonical comparator N2/N3 на Kani f046b70 (с #5135, без #5153); 235→242 harness; отрицательные контроли K1–K4 падают на назначенных проверках. Открыто в G3: generic T/F, `default fn`, другие длины/типы, B2, CI на пине с #5135.

## Рамки
- База — `5402b33188` (голова #752 + main). Итог: новый коммит(ы) поверх неё; push в ветку #752 (`submission/ch8-smallsort` форка) только после одобрения владельца, merge-коммитом, без force.
- Runtime-тела std не менять. Существующие 235 harness сохранить; новые — в том же стиле, что и #752 (контракты под `cfg_attr(kani, ...)`, правило формы: один ensures с `old` на `&mut`-аргументе, всё в `old` — Clone/Copy).
- Бюджет CI организаторов: новые harness не должны заметно удлинять критический шард (сейчас 77 мин macOS partition 2); укажи ожидаемое время на harness.
- Локально только rustfmt (`/root/rustfmt-toolchains/bin/kani-fmt-check.sh`); никаких cargo/rustc/Kani/CBMC. Проверка — fork CI (kani.yml организаторов, workflow в форке включается координатором на один dispatch) или GCB через k1g.sh по решению координатора.
- Тексты для PR/описания — без внутренних имён (G3, B1, q-pilot и т.п.) и ссылок на исследовательские ветки.

## Что нужно от планера
1. План и задание воркеру (IMPL) на перенос G3 на базу `5402b33188` с контрактами на `default fn`, с перечнем harness, контролей и ожидаемого времени.
2. Критерии GO для fork CI.
3. Набросок правки раздела Limitations и описания #752 (владелец вычитывает).
