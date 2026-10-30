# BACKING — кандидат с GO координатора после двух правок

База: `e5a0d8dd511730f374e2f757c8ac37f733062842`.
Library commit: `bff6e4863e4f69cfbd3b3f0cda4cc01e9d9f3c22`.
Изменены только новые модули `backing` в конце merge.rs и network.rs, всего 144 строки.
Оба закрыты `cfg(kani_smallsort_controls)`; старые файлы — побайтные префиксы новых.
Существующие символы, visibility, opt_split, oracle, lane, flags и pin не изменены.

## Adapter и память

Оба private `scratch_view` принимают `&mut MaybeUninit<[T;48]>` из caller, возвращают
`&mut [MaybeUninit<T>]` длины 48 с lifetime входного borrow; локальной памяти helper нет.
`as_mut_ptr().cast()` сохраняет provenance настоящего holder, offset 0 и выравнивание T.
MaybeUninit и массив сохраняют layout/размер элементов; весь view помещается в holder.
Сам view не читает T и не требует инициализации: нет `assume_init` или `&mut [T;48]`.
Holder живёт до конца вызова sort/контроля и при живом view недоступен через исходный borrow.
`v`/`dst` — другие локальные объекты, независимые от holder; assume о памяти/alias нет.
Две локальные копии helper сохраняют изоляцию модулей без изменения старой visibility.
Их исходный текст одинаков; этот adapter повторяет геометрию production small_sort_general.

## Matched B/N8

Old: `merge::opt_split::stable_direct_u64_n8` по полному имени в request, без вызова private body.
New: `merge::backing::stable_direct_u64_n8`, тот же StableSmallSortTypeImpl trait-вход.
`stable_direct_body` совпадает с old после замены лишь создания scratch и передачи adapter view.
Остались any `[u64;8]`, orig, arbitrary byte probe, `lt_u64` (ключ x>>1), unwind(34),
настоящий `assert_sorted_and_probe_preserved`, реальное тело sort/merge без stubs.
Cover после oracle имеет тот же текст; обе стороны запускаются в одном build jobs=1.

## Reuse A/N8: отдельно от новой B/dispatch-проверки

Источник G2: `c81c10e3061e07bb83c732d81413632ada757d2c`.
Build: `0e44427c-18bd-4de4-95b2-e8730abec632`, request `opt-split-n8-20261030`.
Reuse: `merge::opt_split::{stable_contract_u64_n8,general_contract_u64_n8}`.
Исходный merge.rs, smallsort.rs, verify.rs, FreezeMarker и tooling/pin/flags идентичны базе;
после базы изменились только append-блоки, транзитивный oracle/probe сохранён.
`check_source.py` проверяет исходную идентичность и matched bodies; tooling проверен через k1g.
Обе A — proof_for_contract(bidirectional_merge), u64, N8, F=тот же function item lt_u64,
probe arbitrary, unwind(34), controls on, jobs=1, timeout 600, штатный --no-assert-contracts.
Stable A имеет `[MaybeUninit<u64>;48]`, general A — `MaybeUninit<[u64;48]>`.
Обе: src offset 0, ровно prefix 8 из any input, хвост uninit, отдельный initialized any dst.
PFC предполагает sorted halves/valid destination/N2..32, modifies dst[..8], проверяет
sortedness/full-value counts тем же probe. A не вызывает stable trait и не доказывает adapter.
Для нового B при N8 sort4_stable заполняет только две половины [0..4), [4..8) scratch;
ветвь sort8 не выбирается, дополнительных записей в хвост нет. Merge получает prefix 8
offset 0, хвост uninit, отдельный initialized v как dst, тот же F/probe/frame.
Любые значения dst (включая корреляции с input) входят в независимый any dst домен A.
Следовательно, A достаточно для этой merge-части caller после законного adapter.
Новый B всё равно требует отдельного direct proof; G2 PASS не переносится на новый SHA/имя.
Reuse не покрывает dispatch bytes17/N32/arbitrary comparator и старый array-of-MaybeUninit
контекст не выдаётся за новое доказательство; G2 сохраняет свои source identities.

## Matched dispatch

`network::backing::dispatch_safety_stable_bytes17_n32_{old,new}`: только stable ветвь.
Old вызывает прежний dispatch_safety_fixed::<[u8;17],32,true>; new повторяет true-ветвь
с aggregate holder/view, не меняя arbitrary_value/from_fn, T, N и volatile_reading_less.
Обе имеют unwind(65), stub panic_on_ord_violation -> super::assume_order_violation,
cover normal return с одинаковым текстом. Comparator по-прежнему произвольный и читает T.
Прежний pair-harness и его 509 с macOS не являются baseline этой пары.

## Три отрицательных контроля

`merge::backing::stable_value_corruption_control_u64_n2`: реальный stable sort на aggregate,
cover normal return, затем v[0]^=1 сохраняет ключ; настоящий oracle должен отказать на
count-assert merge.rs:846; sortedness-assert :844 должна пройти. Probe не ограничивается.
Kani печатает placeholder: expect_check="This is a placeholder message"; принять только
после проверки location count-assert в summary и SUCCESS sortedness в bounded log-lines.
`unsorted_halves_control_u64_n4`: aggregate prefix [6,0,2,4], корректная отдельная any dst,
cover до вызова, stub_verified merge; ожидается требует `merge_inputs_are_sorted`.
`allocation_bounds_control_u64`: view.as_mut_ptr().cast::<u64>().wrapping_add(48), cover,
ptr::write за всю 384-байтовую allocation. Нет safe indexing, uninit read или fake assume.
Ожидается located memory check `pointer outside object bounds`; после запуска проверить
конкретные check/location и отсутствие посторонней причины. Compile error/unsupported не PASS.

## Request, бюджет и продолжение

`RUN-REQUEST.json` = `matched.request.json`, 7 явных entries: B2 + dispatch2 + controls3.
measurement, k1-standard4, jobs=1, controls:true, 600 с; A переиспользуется из G2.
Envelope (7*10+30)=100 минут, максимум $1.35. Своих builds 0/2, spent/reserved $0/$0.
Свой список UUID/request_id хранится в builds.json: общий label k1-network не разделяет расходы.
Лимит задачи $3/2 builds, CAP_USD=73.96. Резерв второй сборки — только необходимый subset.
GO на 77050e614f получен с двумя правками; обе внесены, повторный review не требуется.
Перед dispatch проверить k1g budget и полный envelope + 20 минут на закрытие.
Консервативный deadline 2026-10-31 01:00 UTC; ожидание review тоже расходует окно.
После dispatch записать UUID/request/source, запустить только k1g.sh watch BUILD и завершить ход.
Собрать summary/peaks/log-grep/log-lines/check-tooling; проверить covers и checks по месту.
Изменение counts из-за представления/инициализации допустимо; SUCCESS/counts сами не приёмка.
Принимаются только new SUCCESS, нужные covers, три правильных отказа и измеримый спад RSS;
VT <=600 с, сумма VT, wall и цена отдельно. Old TIMEOUT сохранить как данные, без speedup ratio.
macOS UNKNOWN, fixture 48 slots не доказывает любой stack/heap backing или E1/uninit.
