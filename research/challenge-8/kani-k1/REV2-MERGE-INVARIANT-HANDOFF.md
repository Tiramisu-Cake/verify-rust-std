# REV2 · handoff инварианта фактического merge N32

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`. Компиляция, раскрытие атрибутов в собранном core, нативная привязка и профиль затрат остаются `UNKNOWN`. Стадия завершена локально. Следующая граница — независимое diff-ревью и отдельный GO. [Задание](REV2-MERGE-INVARIANT-TASK.md)

## Идентичности и область diff

| Объект | Значение |
| --- | --- |
| Задание g0 | `a7e5a01d5fc4a00e908e6493c10d46bbe8540e13` |
| Std worktree | `/root/verify-rust-std-rev2-merge-invariant-w15`, ветка `work/rev2-merge-invariant-w15` |
| Std commit | `59bab95385d17bb2968d1ce53bc9afffb85b3616` |
| Std tree | `ad714e9b41713edb5da4424ce37457dc73265ea4` |
| Единственный Std parent (FIX3) | `32129c149a15fb1b60a7314e738f3cb466d076e5`, tree `1b0cc32c571b370178e64f2b8c79773d2ce27051` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25` |
| Exact selector | `slice::sort::shared::smallsort::verify::rev2_merge_invariant::m32_actual_merge_invariant` |
| Профиль исходника | `all(kani, kani_smallsort_cal1, kani_smallsort_rev2_merge_invariant)` |
| Diff | 4 файла, 166 добавленных строк, SHA-256 `0ab819873b92ed6cbb3b15314b632c9d9c823b6c2d2048e497741b91fd01e080`. Полный патч в конце. |

Атрибуты стоят непосредственно на [`for _ in 0..len_div_2` в `bidirectional_merge`](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort.rs:1044). В FIX3 этот `for` на строке 1022. Обе строки тела сохранены побайтно. Новый root вызывает эту функцию через actual body с `T = u8, F = KeyLess<u8>`. Два новых локальных значения перед циклом хранят базу scratch и пороговое наблюдение. Остальной diff Std содержит декларация cfg в `core/Cargo.toml` и регистрация модуля под cfg. Обёрток цикла, подмен и предположений о выходе harness не содержит. [Root](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs:110)

## Инвариант и переход

Пусть `L` и `R` — две половины по 16 байтов из инициализированного `backing[1..33]` массива V34. `B` — база отдельного `MaybeUninit<[u8; 32]>`. На входе root проверяет длину, читаемость source, записываемость scratch и разные allocation IDs. Единственная содержательная предпосылка `kani::assume` — числовой порядок каждой половины. `q: u8` выбирается независимо от V34. `KeyLess<u8>` читает сравниваемые байты, сравнивает их по числовому `<` и сохраняет q. [Root](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs:110) · [KeyLess](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:17)

Стабильный ранг `rank(side,i)` — позиция уникального ключа `(byte, side, i)` в лексикографическом порядке, где `L < R`, а `i` — исходный индекс внутри половины. Пусть `k` — число завершённых пар на loop head, `a,b` — потребление up, `c,d` — потребление down и `s = src`. Отношения указателей задаются объектом и байтовым смещением внутри объекта.

```text
0 <= k <= 16
0 <= a,b,c,d <= 16
a + b = k, c + d = k
left = s + a,          right = s + 16 + b
left_rev = s + (15-c), right_rev = s + (31-d)
dst = B + k,           dst_rev = B + (31-k)
Cut(a,b) && Cut(16-c,16-d)
Cut(l,r) :=
    (l == 0 || r == 16 || L[l-1] <= R[r]) &&
    (r == 0 || l == 16 || R[r-1] <  L[l])
```

В коде `kept_l = 16-c`, `kept_r = 16-d` вычисляются из `*_rev.wrapping_add(1)`. Их сумма равна `32-k`. Guard на объект и разность смещений связывает все шесть курсоров с исходными allocations. Числовой порядок внутри половин и две проверки `Cut` эквивалентны тому, что объединённые префиксы длины `l,r` — первые `l+r` рангов. В первом сравнении равный байт слева идёт раньше правого. Во втором равенство нарушает разрез. Внутри половины исходный индекс уже согласован с порядком. [`loop_head`](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs:34) · [`stable_cut`](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs:101)

На базе `k=a=b=c=d=0`. Forward cut пустой, reverse cut оставляет полные половины, курсоры инициализированы самим merge, ни одна ячейка scratch не читается. Для `k<16` каждая из `a,b,c,d` не больше `k`, поэтому оба up-чтения имеют индексы `a` и `16+b` в своих половинах, оба down-чтения — `15-c` и `31-d`. В `merge_up` условие `!is_less(right,left)` выбирает левый при равенстве. Учитывая `Cut(a,b)`, выбор имеет ранг `k`. Helper прибавляет 1 только к выбранному source-курсору, записывает один элемент в `B+k` и возвращает `dst+1`. В `merge_down` то же условие выбирает правый при равенстве. С учётом второго cut выбран ранг `31-k`. Helper применяет `wrapping_sub(1)` только к выбранному source-курсору, пишет один элемент в `B+(31-k)` и возвращает `dst_rev-1`. Оба scratch-адреса различны и лежат в ещё пустом промежутке. Copy size равен одному элементу `u8`. [`merge_up`](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort.rs:862) · [`merge_down`](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort.rs:895)

Два новых ранга различны, поскольку `k < 31-k`, и оба лежат между накопленными рангами. Выбранная позиция поэтому не повторяется ни в одном проходе. Встречный проход может прочитать уже выбранную позицию в сравнении. Например, для `L=[0..7,248..255]` и `R=[64..79]` перед девятой парой оба прохода снова читают позиции L, уже выбранные встречным проходом, и оба выбирают R. После шага новый up-cut соответствует первым `k+1` рангам, reverse-cut оставляет первые `31-k`. В порядке адресов scratch содержит первые и последние `k+1` рангов. При полном reverse-потреблении половины `*_rev` может указывать перед её началом. Это возможно только после последнего шага, поскольку до него сумма потребления меньше 16. Этот курсор не разыменовывается. `wrapping_add(1)` восстанавливает начало половины при проверке выхода. Up-курсор на последнем шаге также может оказаться за концом своей половины. Все промежуточные `add` и `sub` destination остаются внутри scratch, включая последний `dst_rev=B+15`.

Исполняемая часть инварианта проверяет пороговую проекцию рангов. Перед циклом фиксируется `C = #{i | input[i] < q}` одним счётчиком `u8` с максимумом 32. На каждом head для каждого `i < k || i >= 32-k` проверяется `(scratch[i] < q) == (i < C)`. Для нового up-байта равенство следует из его ранга `k`, для down-байта — из ранга `31-k`. Старые байты сохраняются двумя точными записями helpers. На head `k=16` равенство охватывает все 32 позиции. Для любого фиксированного V34 фактические сравнения, выборы и записи одинаковы при любом q. Поэтому из универсального порогового поста следует порядок байтов: инверсия `x>y` даёт нарушенный порог `q=x`. Равенство всех пороговых счётчиков даёт кратность `x<255` как `C(x+1)-C(x)`, а кратность 255 как `32-C(255)`. Позиционное равенство порогов даже определяет точный байт на каждом выходном ранге. Идентичность позиций при равных байтах следует из доказательства выбора по `Cut` и фактических helpers, поскольку равные `u8` в scratch не различимы. [Пороговое наблюдение и чтение scratch](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs:17)

## Прогресс и чётный выход

Пин раскрывает `for` через `KaniIntoIter` и `KaniIter`: при непустом диапазоне начальный индекс 0, длина 16, guard `index < len`, встроенная часть инварианта `index <= len`. `Range<usize>::nth` возвращает `start.wrapping_add(i)`, а `Range::assumption` возвращает true. Раскрытие прибавляет 1 к индексу перед двумя исходными вызовами. На следующем head индекс опять равен числу завершённых пар. Отрицание guard совместно с инвариантом даёт `k=16`. Нативные base/step и выход при ложном guard дают частичную корректность. Нативной проверки `loop_decreases` у кандидата нет. Внешняя termination-часть опирается на конечный диапазон `0..16`, отсутствие ранних переходов и конечные `KeyLess` и оба helpers в точной мономорфизации. При отсутствии UB и panic на доказанном шаге индекс монотонно растёт от 0 до 16. На пине для нативного decreases нужен один целочисленный measure, читаемый как изменяемый place. Выражение `16 - kani::index` здесь не используется: rewrite `kani::index` относится к invariant, а вычисленная арифметика может стать одноразовым значением. Если понадобится нативная termination-проверка, минимальное расширение — cfg-only mutable `remaining` с уменьшением после фактической пары, invariant `remaining + k == 16`, его место в assigns и `loop_decreases(remaining)`. [Раскрытие for и index на пине](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/library/kani_macros/src/sysroot/loop_contracts/mod.rs#L428) · [Range на пине](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/library/kani_core/src/iter.rs#L128) · [Ограничения decreases](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/docs/src/reference/experimental/loop-contracts.md#limitations) · [Тест decreases для for](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/tests/expected/loop-contract/decreases_variable.rs)

При `k=16` оба cuts задают один и тот же префикс из 16 уникальных рангов. Значит, `a=16-c` и `b=16-d`, обе проверки `forward == reverse.wrapping_add(1)` истинны, odd-ветка недостижима и merge возвращается нормально. Диапазоны `[0,16)` и `[16,32)` покрывают весь scratch. Никакого переноса свойства на нечётный вызов этот шаг не даёт. [Финализация actual merge](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort.rs:1049)

Для actual N32 consumer надо отдельно связать вход этого же `bidirectional_merge` с инициализированными и независимо отсортированными половинами после actual sort13 и insertion, срезом над тем же `v_base` и тем же `len`, а `B` — с отдельным `stack_array` caller. После normal return 32 ячейки scratch пригодны для чтения. Нужна проверка самой `ptr::copy_nonoverlapping(scratch_base, v_base, len)` на 32 записи в исходный срез, применимость непересечения и frame вне среза и q. Тогда пороговый пост scratch переносится на срез, а исходное мультимножество caller требует ещё сохранения байтов при подготовке половин. Мономорфизацию, геометрию и источник поста надо сверить на callsite. Native Proof merge не устанавливает контракт для Replace или результат consumer. [Actual N32 caller](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort.rs:380) · [Вызов и copy-back](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort.rs:422)

## Scratch havoc и значения

`loop_modifies` перечисляет шесть мест хранения курсоров через `&raw mut` и `ptr::slice_from_raw_parts_mut(B,len)`. Это объединение разрешённых записей за весь цикл, плюс generated locals Kani (в частности индекс). Размер scratch-цели для N32 — 32 байта. Source, q, база scratch и snapshot остаются вне write set. Для raw slice пин выводит `__CPROVER_object_upto(data,len*sizeof(T))`. CBMC после base havocs write set, затем предполагает инвариант. В 6.11.0 byte-range havoc вызывает `__CPROVER_havoc_slice(lb,size)`. В абстрактном состоянии весь scratch получает произвольные байты, но только два заполненных диапазона ограничиваются порогом и опрашиваются predicate. Ни base, ни шаг helpers, ни predicate не читают незаполненный промежуток. Факт конкретной инициализации возникает только из двух реальных `copy_nonoverlapping(...,1)` за завершённую пару. Он устанавливается индукцией вместе с индексом, а не из байтового havoc или `can_write`. [Kani raw slice target](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L28) · [CBMC base/havoc/assume](https://github.com/diffblue/cbmc/blob/820ff0f555b43fb78e0cd9332e498461bd14244b/src/goto-instrument/contracts/dynamic-frames/dfcc_instrument_loop.cpp#L364) · [CBMC byte-range havoc](https://github.com/diffblue/cbmc/blob/820ff0f555b43fb78e0cd9332e498461bd14244b/src/ansi-c/library/cprover_contracts.c#L1597)

Профиль использует uninit/validity OFF. Байтовый havoc действует на GOTO после Rust MIR instrumentation и сам по себе не устанавливает Kani shadow initialization для заполненных диапазонов. При включении uninit потребуется явная проверка того, как instrumented invariant видит shadow, с последующим loop-aware моделированием initialization для history заполнения, если shadow теряет эти факты. Нужен отдельный контроль чтения gap и отсутствие необоснованного marking всей области. Источник всегда состоит из инициализированных `u8`, а каждое из 256 значений допустимо для `u8`. Эти условия ограничены данным доменом. [Kani описание shadow memory](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/library/kani_core/src/lib.rs#L112) · [Kani can_write и can_dereference](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/library/kani_core/src/mem.rs#L30)

## Таблица обязательств

Все перечисленные нативные результаты ожидаются от будущего запуска и имеют статус `UNKNOWN`.

| Обязательство | Привязка в Std | Ожидаемое нативное свидетельство | Открытая граница |
| --- | --- | --- | --- |
| Вход и невакуозность | Root, строки 111–126, covers 136–140 | PASS `LENGTH`, `SOURCE_READABLE`, `SCRATCH_WRITABLE`, `DISJOINT`. Достижимость q=0, q=255, mixed q, ties и normal return | Порядок половин — входной домен. Подготовку половин выполняет actual consumer |
| База и связь курсоров с индексом | `smallsort.rs:1014–1044`, `loop_head:34–65` | `loop_invariant_base` на exact loop ID, с индексом 0 и исходной геометрией | Сверить GOTO span и выведенные target objects |
| Переход по рангам и bounds | `smallsort.rs:1045–1046`, helpers 862–921, `stable_cut:101` | `loop_invariant_step` exact ID, фактические вызовы или их inlined тела и PASS checks на арифметику, чтение и `copy_nonoverlapping` | Доказательство уникальности ранга и ties использует исходный выбор, поскольку q-проекция не различает равные байты. FIX3 pair-step служит измерением отдельной обёртки |
| Две записи, assigns и frame | `smallsort.rs:1039–1042,1045–1046`, копии в helpers, root 134–135 | `loop_assigns` exact ID и применимые `assigns` на реальных stores. GOTO-цели обеих одноэлементных копий плюс PASS `SOURCE_FRAME` и `Q_FRAME` | `loop_assigns` проверяет включение в родительский set, а отдельные writes — принадлежность set. Точность двух адресов следует из курсоров и размера копий |
| Инициализация и ограничение havoc | `loop_head:34–80`, actual stores, root 131–133 | Проверка связки guarded scratch loads, byte-range target и base/step. На базе отсутствуют typed scratch reads | Инициализацию несёт аргумент об actual stores и покрытии диапазонов. Uninit/validity OFF |
| Прогресс | `smallsort.rs:1044–1047`, раскрытие Range | Индекс 0, guard `index < 16`, latch с увеличением на 1, native base/step и exit case | Внешнее обоснование конечности. `loop_decreases` отсутствует |
| Чётный выход и точный q-пост | `smallsort.rs:1049–1065`, root 129–140 | PASS `EXACT_Q_POST`, отсутствие order-violation panic, достижимый `USEFUL_RETURN`, отсутствие срабатывания unwinding assertions | Порядок и мультимножество выводятся по всем q для одного выполнения. Copy-back и odd проходят отдельную проверку |
| Actual consumer | `smallsort.rs:380–425`, вызов и `copy_nonoverlapping` | В будущем — отдельная привязка N32 callsite и нативная проверка copy-back с применимостью | В этом Proof открыто |

## Статический аудит и будущая диагностика

- В `smallsort.rs` уже есть `#[cfg(kani)] use crate::kani` и `ptr`. Локальные имена атрибутов находятся в том же `unsafe`-блоке. `kani::index` — ровно двухсегментный псевдопуть, который `KaniIndexReplacer` заменяет до разрешения имён. `loop_invariant` идёт перед `loop_modifies`, поэтому первый макрос забирает clause с того же `for`. Раскрытие использует `kani::KaniIntoIter`, `kani::KaniIter`, `kani::assume` и `kanitool::fn_marker`. Перед будущим запуском нужен sysroot с реализациями макросов под `kani_sysroot` и флаг `-Z loop-contracts` на инструментальном этапе. `core/lib.rs` уже включает `stmt_expr_attributes`, `proc_macro_hygiene`, `register_tool`, `min_specialization` и `unboxed_closures`. Под `cfg(kani)` `kani_lib!(core)` определяет `crate::kani`, реэкспортирует макросы и генерирует итераторные traits и `mem`. Kani compiler регистрирует `kanitool`. [Core gates и генерация](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/lib.rs:149) · [Kani exports](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/library/kani_core/src/lib.rs#L38) · [Регистрация tool](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-compiler/src/kani_compiler.rs#L396)
- Родительский `verify` существует только под `kani`. Новый модуль имеет `pub(super)` из `verify.rs`, а `MergeObservation`, `capture` и `loop_head` видимы ровно в `smallsort` и его потомках. `cal1_model` приватен для `verify` и доступен его дочернему модулю, `KeyLess` и методы `with_q` и `q` в этой области доступны. `cal1_q_merge_model::{active,numeric_order}` видимы в `smallsort`. `active` переиспользует уже имеющуюся специализацию на точную пару. `ptr`, `MaybeUninit` и `ub_checks` — текущие core API. `pointer_object` и `pointer_offset` генерируются как `pub(crate)` в `core::kani::mem` и распознаются по markers как metadata hooks без загрузки памяти. Все прочие новые функции и root приватны. [Регистрация модуля](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify.rs:95) · [Типовой guard](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs:4) · [Visibility hooks](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/library/kani_core/src/mem.rs#L277)
- Сложный cfg требует сразу Kani, CAL1 и opt-in. В cfg-on у любого другого типа, компаратора или длины `capture` возвращает `None` до byte casts, чтений и арифметики N32. `None => false` отклоняет неподходящую reachable мономорфизацию на base. Этот профиль предназначен для одного exact selector. Выражения modifies всё равно типизируются для любого `T`: берут raw-адреса локальных мест и образуют raw slice из исходного `*mut T` и фактического `len`, без чтения значений. Для ZST zero-byte target пин опускает через null/size logic. Даже в выбранном домене произвольные havoc-курсоры исследуются через raw wrapping и metadata, без `offset_from` или разыменования до ограничений. После bounds и cuts читается scratch по сохранённой базе и только в заполненных диапазонах. [Guard](/root/verify-rust-std-rev2-merge-invariant-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs:18) · [Нулевая цель assigns на пине](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L48)
- Сверить exact worktree/tree, профиль и roster в будущей preflight. В cfg-off root должен отсутствовать, в cfg-on должна быть ровно одна новая регистрация с ожидаемым selector. Для нативной привязки сохранить tuple из идентичности мономорфизации, source span loop head, latch и CBMC loop ID. В GOTO до DFCC отследить `kani_register_loop_contract` к backedge, его invariant и explicit assigns. На этом же loop ID сопоставить branch `index < 16`, два actual helper calls или inlined copies, targets и post-DFCC base/step/assigns с ID, Location, status. Привязка по префиксам имён или одному `has_loop_contracts=true` недостаточна. Driver для этого harness должен применить `--dfcc … --apply-loop-contracts --loop-contracts-no-unwind`. В обязательных данных оставить статус каждого ожидаемого property и covers. Не считать успешным прогон, который доказал только bounded исходный цикл или выбрал пороговый helper вместо actual merge. [Kani hook на latch](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs#L840) · [Kani driver](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/call_goto_instrument.rs#L172)
- Различающий контроль для отдельного review pin может добавить `kani::index != 1` как конъюнкт непосредственно у фактического `for`. Ожидается положительная база и отрицательный `loop_invariant_step` того же цикла при `0→1`. Посторонний failure или просто ненулевой exit результата не дают. Если pin не связывает этот цикл или не поддерживает guarded byte-range havoc, сохранить exact stage, diagnostics, дерево и loop/target. Минимальная недостающая часть в таком случае — поддержка explicit raw-slice target на этом latch или корректного абстрактного чтения двух доказанно заполненных диапазонов, в зависимости от наблюдаемого отказа. Обычный bounded fallback или assumed post такую привязку не закрывает.

## Локальные проверки

- `rustfmt --check` прошёл для трёх затронутых Rust-файлов у `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt` с `--edition 2024 --config use_small_heuristics=Max,skip_children=true`. Для существующего `verify.rs` отдельно применён также `reorder_modules=false`, чтобы сохранить исходное расположение `mod comparators;` FIX3.
- `git diff --check` и `git diff --cached --check` прошли. Удаление только двух cfg-локальных объявлений и cfg_attr из `smallsort.rs` даёт родительский blob побайтно, включая оба helper, исходное тело `for`, odd branch и order check. Удаление новой cfg-регистрации из `verify.rs` и новой lint-строки из манифеста даёт соответствующие родительские blobs побайтно. Статическая cfg-off проекция также исключает новый файл модуля.
- Python witness проверил 5 295 наборов половин, 33 979 head states и 8 360 событий чтения встречного выбора. Наборы включали все пары отсортированных половин длины 1–5 над `{0,1,254,255}`, все пары половин длины 16 над `{0,255}`, 128 детерминированных пар полноразрядных N32 и указанный cross-direction fixture. Для каждого набора перебраны все пары границ cut, результаты сверены с отсортированными тройками, а модель обеих операций проверила курсоры, точные записи, отсутствие повторного выбора, gap, чётный выход и пороги. Для 129 полноразрядных N32 рассмотрены все 256 q. Это проверка формулы и модели выбора, без исполнения или анализа машинной модели Rust, Kani или CBMC.
- Cargo, rustc, Kani, CBMC и другие локальные сборки/верификации не запускались. Push, CI и публикации отсутствуют.

## Первый Ubuntu пакет после review и GO

Предпочтительный первый замер — один холодный `m32_actual_merge_invariant` с exact selector и отдельно закреплённый control привязки, если он войдёт в тот же GO. Stock Kani на указанном пине, CBMC 6.11.0/CaDiCaL как FIX3, OB12, unwind 36, штатные safety/overflow/unwind, uninit/validity OFF, `--no-assert-contracts` как в FIX3 и `-Z loop-contracts`. `jobs=1`, холодные target/export/tmp для каждого корня, предел 180 с child cold wall, целевой VT ≤120 с и пик группы 4 GiB на корень. Резерв Ubuntu ≥2 GiB. CFG и итоговые flags подтвердить по фактическому argv. Setup учитывается отдельно от холодного измерения. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md) · [FIX3 профиль](REV2-NETWORK-PROVIDERS-RESULTS-ANALYSIS.md)

Ориентир FIX3 для пары — VT 53,2 с, cold wall 86,8 с, пик группы 2,13 GiB. До лимитов остаются 66,8 с VT и 1,87 GiB относительно измеренной пары. При прежних накладных ~33,6 с прохождение ровно на пределе VT означало бы ~153,6 с cold wall. Это расчёт запаса, компиляция и DFCC нового маршрута имеют собственные накладные. Полный FIX3 Mask достиг 180 с, достигнутый за это время пик 2,42 GiB не даёт верхней оценки памяти до решения. Новый маршрут заменяет 16 пар одним абстрактным переходом, но вводит loop DFCC, havoc шести курсоров и 32 байтов, guard-ограничения порогов, динамические обращения на границах рангов и переоценку инварианта на base, step и выходе. Havoc scratch может добавить существенные byte-array/SSA constraints и увеличить SAT/peak RSS даже с одной парой и без function Check. Первую CNF, VT, group/CBMC RSS, выход и covers измерить отдельно. Профиль `UNKNOWN`, конкретную оценку VT или верхний RSS до замера установить нельзя. [Ориентиры FIX3](REV2-NETWORK-PROVIDERS-RESULTS-ANALYSIS.md)

## Условия будущего control

- `pins` и `finish` независимо получают `HEAD^{tree}` фактического чистого checkout и сверяют его с внешним tree pin координатора. Начальный receipt фиксирует это значение и commit. `finish` повторяет проверку фактического дерева и согласованности с receipt. Пустой, старый и чужой pin ведут к отказу. Совпадение payload и trailer с изменённым деревом также ведёт к отказу, поскольку они описывают заявку, а источник pin находится у координатора. Std overlay tree проверяется отдельно на своей границе. Имя и значение trigger pin устанавливаются в будущем запросе.
- Дедлайн слота включает child, ограниченный reap и обязательную атомарную запись receipt. Пример планирования для 180 с child cold wall — 10 с reap и ещё 5 с на receipt внутри абсолютного envelope слота, с отдельным ограничением проекции до начала резерва записи. Обязательный snapshot результата и reap сохраняется до необязательной проекции. После её отсечки сохраняется настоящее состояние child и отдельный статус проекции. Если запись или retry опоздали, receipt сохраняет наблюдавшийся exit/timeout, timestamps и флаг превышения дедлайна. Неподтверждённый reap закрывает запуск следующего слота. Планирование следующего слота учитывает его latest start и резерв записи.
- Синтетические проверки используют один внедрённый monotonic clock для runner, projection, reap, receipt, retry и `finish`, включая все вычисления deadline и его нарушения. Воспроизвести suite на свежей шкале около 60 с независимо от реального uptime. Нужны mismatch при согласованных payload/trailer, медленная проекция, поздний atomic receipt с сохранённым настоящим исходом, ошибка записи и retry, отсутствие reap и последний допустимый слот. Зафиксировать статусы исхода и состояния проекции отдельно. [Соседний пакет с условиями gate](REV2-S13-GEOMETRIES-TASK.md)
- Control, workflow, trigger и ledgers в этой стадии не менялись. Порядок допуска остаётся review → отдельный GO.

## Точный патч Std

Получение указанного diff из локальных объектов Git

```sh
git --no-pager -C /root/verify-rust-std-rev2-merge-invariant-w15 diff \
  --no-ext-diff --no-textconv --binary --full-index --no-color --no-renames \
  --src-prefix=a/ --dst-prefix=b/ --no-indent-heuristic --diff-algorithm=myers -U0 \
  32129c149a15fb1b60a7314e738f3cb466d076e5 59bab95385d17bb2968d1ce53bc9afffb85b3616
```

<details>
<summary>Патч между точными Std parent и commit</summary>

```diff
diff --git a/library/core/Cargo.toml b/library/core/Cargo.toml
index ba26c4cd2b6cd4df2a83746b845aedae6034980a..786d597cf9e1ad0d10ad796f7e42e645f4c08711 100644
--- a/library/core/Cargo.toml
+++ b/library/core/Cargo.toml
@@ -50,0 +51 @@ check-cfg = [
+    'cfg(kani_smallsort_rev2_merge_invariant)',
diff --git a/library/core/src/slice/sort/shared/smallsort.rs b/library/core/src/slice/sort/shared/smallsort.rs
index 0b77c3dbb3b767ba35281a2a686aa477ff1344c5..3327e43318d943b61f72d003ba7240645b1e91de 100644
--- a/library/core/src/slice/sort/shared/smallsort.rs
+++ b/library/core/src/slice/sort/shared/smallsort.rs
@@ -1021,0 +1022,22 @@ unsafe fn bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
+        #[cfg(all(kani, kani_smallsort_cal1, kani_smallsort_rev2_merge_invariant))]
+        let scratch_base = dst;
+        #[cfg(all(kani, kani_smallsort_cal1, kani_smallsort_rev2_merge_invariant))]
+        let observation = verify::rev2_merge_invariant::MergeObservation::capture(v, is_less);
+
+        #[cfg_attr(
+            all(kani, kani_smallsort_cal1, kani_smallsort_rev2_merge_invariant),
+            kani::loop_invariant(match &observation {
+                Some(state) => state.loop_head(
+                    kani::index,
+                    scratch_base.cast(),
+                    (left.cast(), right.cast()),
+                    (left_rev.cast(), right_rev.cast()),
+                    (dst.cast(), dst_rev.cast()),
+                ),
+                None => false,
+            }),
+            kani::loop_modifies(
+                &raw mut left, &raw mut right, &raw mut left_rev, &raw mut right_rev,
+                &raw mut dst, &raw mut dst_rev, ptr::slice_from_raw_parts_mut(scratch_base, len),
+            ),
+        )]
diff --git a/library/core/src/slice/sort/shared/smallsort/verify.rs b/library/core/src/slice/sort/shared/smallsort/verify.rs
index a0392eba183c930b018ebe3af4ab3849204da0ec..bafab8ddee3eecd371f0b8bfd1e94250915dfbfd 100644
--- a/library/core/src/slice/sort/shared/smallsort/verify.rs
+++ b/library/core/src/slice/sort/shared/smallsort/verify.rs
@@ -96,0 +97,2 @@ mod network;
+#[cfg(all(kani_smallsort_cal1, kani_smallsort_rev2_merge_invariant))]
+pub(super) mod rev2_merge_invariant;
diff --git a/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs b/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs
new file mode 100644
index 0000000000000000000000000000000000000000..b6dcd1a3c6ed841c522e8afb09abfab9bc1b9b16
--- /dev/null
+++ b/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_invariant.rs
@@ -0,0 +1,141 @@
+//! Opt-in loop contract for the actual even byte merge at length 32.
+
+use super::cal1_model::KeyLess;
+use super::cal1_q_merge_model::{active, numeric_order};
+use crate::kani::mem::{pointer_object, pointer_offset};
+use crate::{kani, mem::MaybeUninit, ptr, ub_checks};
+
+const HALF: usize = 16;
+const LEN: usize = 2 * HALF;
+
+pub(in crate::slice::sort::shared::smallsort) struct MergeObservation<'a> {
+    input: &'a [u8; LEN],
+    q: u8,
+    below: usize,
+}
+
+impl<'a> MergeObservation<'a> {
+    pub(in crate::slice::sort::shared::smallsort) fn capture<T, F>(
+        input: &'a [T],
+        less: &F,
+    ) -> Option<Self> {
+        if input.len() != LEN || !active::<T, F>() {
+            return None;
+        }
+        // SAFETY: `active` specializes on exactly u8 and KeyLess<u8>. The slice
+        // has LEN initialized bytes and `less` is a shared reference to that comparator.
+        let input = unsafe { &*input.as_ptr().cast::<[u8; LEN]>() };
+        let q = unsafe { &*ptr::from_ref(less).cast::<KeyLess<u8>>() }.q();
+        Some(Self { input, q, below: count_below(input, q) })
+    }
+
+    /// `scratch` is the disjoint, writable destination for LEN bytes. On a concrete
+    /// loop head the first and last `k` bytes must have been written by completed pairs.
+    pub(in crate::slice::sort::shared::smallsort) unsafe fn loop_head(
+        &self,
+        k: usize,
+        scratch: *mut u8,
+        (left, right): (*const u8, *const u8),
+        (left_rev, right_rev): (*const u8, *const u8),
+        (dst, dst_rev): (*mut u8, *mut u8),
+    ) -> bool {
+        if k > HALF
+            || byte_offset(scratch, dst) != Some(k)
+            || byte_offset(scratch, dst_rev) != Some(LEN - 1 - k)
+        {
+            return false;
+        }
+
+        let lo = self.input.as_ptr();
+        let hi = lo.wrapping_add(HALF);
+        let (Some(up_l), Some(up_r), Some(kept_l), Some(kept_r)) = (
+            byte_offset(lo, left),
+            byte_offset(hi, right),
+            byte_offset(lo, left_rev.wrapping_add(1)),
+            byte_offset(hi, right_rev.wrapping_add(1)),
+        ) else {
+            return false;
+        };
+
+        up_l <= HALF && up_r <= HALF && kept_l <= HALF && kept_r <= HALF
+            && up_l + up_r == k && kept_l + kept_r == LEN - k
+            && stable_cut(self.input, up_l, up_r) && stable_cut(self.input, kept_l, kept_r)
+            // SAFETY: test only the positions filled by the completed pairs. The
+            // loop abstraction havocs bytes and the measurement uses uninit checks OFF.
+            && unsafe { self.scratch_matches(scratch, k) }
+    }
+
+    /// Requires writable scratch storage for LEN bytes with the first and last
+    /// `k` bytes initialized, where `k <= HALF`.
+    unsafe fn scratch_matches(&self, scratch: *const u8, k: usize) -> bool {
+        for i in 0..LEN {
+            if i < k || i >= LEN - k {
+                // SAFETY: the middle gap is skipped before the typed read.
+                let byte = unsafe { scratch.add(i).read() };
+                if (byte < self.q) != (i < self.below) {
+                    return false;
+                }
+            }
+        }
+        true
+    }
+}
+
+fn count_below(input: &[u8; LEN], q: u8) -> usize {
+    let mut count = 0u8;
+    for &byte in input {
+        count += u8::from(byte < q);
+    }
+    usize::from(count)
+}
+
+fn byte_offset(base: *const u8, cursor: *const u8) -> Option<usize> {
+    // Havoc can give a cursor another object or an out-of-bounds offset. The
+    // two Kani hooks inspect metadata without dereferencing either pointer.
+    if pointer_object(base) != pointer_object(cursor) {
+        return None;
+    }
+    Some(pointer_offset(cursor).wrapping_sub(pointer_offset(base)))
+}
+
+fn stable_cut(input: &[u8; LEN], l: usize, r: usize) -> bool {
+    // Each half is already sorted by (byte, side, index); only the two
+    // cross-half boundaries between the prefix and suffix need comparison.
+    (l == 0 || r == HALF || input[l - 1] <= input[HALF + r])
+        && (r == 0 || l == HALF || input[HALF + r - 1] < input[l])
+}
+
+#[kani::proof]
+#[kani::unwind(36)]
+fn m32_actual_merge_invariant() {
+    let backing: [u8; LEN + 2] = kani::any();
+    let before = backing;
+    let q: u8 = kani::any();
+    let mut less = KeyLess::<u8>::with_q(q);
+    let mut scratch = MaybeUninit::<[u8; LEN]>::uninit();
+    let input = &backing[1..1 + LEN];
+    let dst = scratch.as_mut_ptr().cast::<u8>();
+    kani::assert(input.len() == LEN, "REV2_M32_LOOP_LENGTH");
+    kani::assert(ub_checks::can_dereference(input as *const [u8]), "REV2_M32_LOOP_SOURCE_READABLE");
+    kani::assert(
+        ub_checks::can_write(ptr::slice_from_raw_parts_mut(dst, LEN)),
+        "REV2_M32_LOOP_SCRATCH_WRITABLE",
+    );
+    kani::assert(!ub_checks::same_allocation(input.as_ptr(), dst), "REV2_M32_LOOP_DISJOINT");
+    kani::assume(numeric_order(&input[..HALF]) && numeric_order(&input[HALF..]));
+    let observation = MergeObservation::capture(input, &less).unwrap();
+
+    // SAFETY: input and destination have LEN bytes in separate allocations.
+    unsafe { super::super::bidirectional_merge(input, dst, &mut less) };
+
+    // SAFETY: normal even return has filled exactly the first and last HALF
+    // bytes in the real merge, covering the entire allocation.
+    kani::assert(unsafe { observation.scratch_matches(dst, HALF) }, "REV2_M32_LOOP_EXACT_Q_POST");
+    kani::assert(backing == before, "REV2_M32_LOOP_SOURCE_FRAME");
+    kani::assert(less.q() == q, "REV2_M32_LOOP_Q_FRAME");
+    kani::cover(q == 0, "REV2_M32_LOOP_Q_ZERO");
+    kani::cover(q == u8::MAX, "REV2_M32_LOOP_Q_MAX");
+    kani::cover(observation.below > 0 && observation.below < LEN, "REV2_M32_LOOP_Q_MIXED");
+    kani::cover(input[0] == input[HALF], "REV2_M32_LOOP_CROSS_HALF_TIE");
+    kani::cover(true, "REV2_M32_LOOP_USEFUL_RETURN");
+}
```

</details>
