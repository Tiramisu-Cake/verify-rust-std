# TASK — worker13: репродьюсер kani#5151 и подсчёт по #649 на прототипе (одна стадия, без dispatch)

Это верификация корректности, не security-работа. Отвечай кратко.

kani#5151 (мейнтейнер Kani): `-Z uninit-checks` не поддерживает массивы `MaybeUninit<T>` с нетривиальным `T`. Репродьюсер —
`[MaybeUninit<D>; 2]`, где у `D` есть `Drop`, запись в слот 0 и `drop_in_place` на слот 0 при неинициализированном слоте 1
(точно — по тексту issue: `gh issue view 5151 -R model-checking/kani --comments`). Там же: на решении Challenge 2
(verify-rust-std#649) при Kani `c5e65fd` 91 из 394 harness падают на unsupported, 77 — из-за union в буфере.

Прототип: наш финальный стек C2, дерево `9829702c1a` (коммит `8e299aa624`; объекты в `/root/kani-ch8-b-census-w14`), база 0aac.
Подготовить один CI-пакет (по образцу наших `uninit-ci/**` пакетов) с двумя частями:
1. Репродьюсер #5151 как тест (`tests/expected/uninit/...`) — на stock 0aac (ожидание: unsupported) и на прототипе (ожидание:
   проверка проходит/падает по существу — записать заранее, что считаем успехом).
2. По возможности — 77 harness из #649 под `-Z uninit-checks` на прототипе: выделить их список (по комментарию в #5151 и
   исходникам #649), оценить время; если в один прогон не помещается — предложить разбиение. Toolchain/версии std для #649
   выяснить; если несовместимо с 0aac — STOP с объяснением для части 2, часть 1 всё равно готовить.

Выход: g0 `kani3300/wave0/5151-repro/`: тест, PACKAGE.md, CI-REQUEST.json, HANDOFF.md (ожидания, время, artifacts).
Коммит [skip ci], author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> <control SHA> или STOP <причина>.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
