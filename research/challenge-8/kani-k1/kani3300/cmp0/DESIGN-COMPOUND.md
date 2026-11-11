# KANI3300 CMP0 — ограниченный product-layout
2026-11-11; Runtime Codex; Cloud $0; только статический анализ, implementation/native/core NOT_RUN, proof credit отсутствует.
Research HEAD `92d9677bb3823126d91bfdad6f53948c028cc338` (от U3B `538e907ad6`); std — это дерево.
Kani baseline `f046b70644e113be0df9c22c2e6ea44a65a57566`; исследованный v2 `81dd85bfce67226e283fdd9a156932e32ece080b`, tree `c5b24f0b0da999d1deb9758215790382fe5e3be4`.
Kani ниже прочитан только через git show immutable v2; номера относятся к нему. CMP1 обязан перепривязаться к принятому U3B patch/tree.

## Полный путь по исходнику (формы MIR ожидаемые, не measured binding)
- `library/core/src/slice/sort/shared/smallsort.rs:267`: `for offset in [0, len_div_2]` создаёт именно `[usize;2]` iterator.
- `library/core/src/array/iter.rs:63,77,80,81`: consume/copy входа → typed transmute `[usize;2]` в `[MaybeUninit<usize>;2]` → вызов new_unchecked с IndexRange → ManuallyDrop::new → aggregate IntoIter и return.
- `array/iter.rs:16,17,24,25`: IntoIter.inner: ManuallyDrop<InnerSized>; InnerSized = PolymorphicIter<[MaybeUninit<T>;N]>; InnerUnsized = PolymorphicIter<[MaybeUninit<T>]>.
- `array/iter/iter_inner.rs:35,45,59,95,96`: product `{alive: IndexRange, data: DATA}`, aggregate `Self {alive,data}`; `ops/index_range.rs:18,39`: ordinary `{start:usize,end:usize}` = 0..2, **не Range** на этом пути.
- `mem/manually_drop.rs:154,156,180,181,279,280`: transparent `{value:T}`, constructor aggregate/move/return; DerefMut — проекция `&mut self.value`; into_inner field move (:198,199) — дополнительная fixture-граница, не вызов этого пути.
- `array/iter.rs:36,251,252` → `iter_inner.rs:206,212,219`: next через reference unsize, alive.next(), Option::map, unchecked data[idx], assume_init_read; результат Option<usize> обычный, storage-result enum не требуется.
- `ops/index_range.rs:65,68,70,135`: start 0→1→2; next выдаёт Some(0), Some(1), затем None; data read семантически вынимает элемент, даже если usize:Copy.
- `array/iter.rs:344,346,349`: drop IntoIter проверяет needs_drop::<T>(); для usize=false, payload ManuallyDrop не дропается. Для T:Drop — единственный explicit ManuallyDrop::drop (`mem/manually_drop.rs:254,261`).
- `iter_inner.rs:79,82,16,19,22`: payload drop → partial_drop только data[alive]; после двух next alive=2..2, ранний drop обрабатывает лишь остаток. N=0/ZST не отменяют bookkeeping.
- Операции, которые должна покрыть CMP1: aggregate на каждом product-уровне; Copy/Move целого product; field/index projection; by-value argument/return wrappers; reference unsize/DerefMut; Drop без изменения storage-shadow.

## Где v2 останавливается и что менять
Префикс `U` = `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs`; `L` = соседний `../ty_layout.rs`; `M` = соседний `../mod.rs`.
- `L:122,132` maybe_uninit_storage/for_storage узнают только MU и плоскую array/slice MU; `L:355,361,440` recursion в struct достигает MU union и возвращает UnionAsField.
- `U:422,424,427` выдаёт Unsupported assignment product с этим layout; `M:218,244,248,252` выдаёт аналогичный pointer-layout Unsupported. U3 RESULT сообщает PolymorphicIter-family; порядок wrappers из native excerpt не установлен.
- Добавить отдельный compiler-side descriptor product: size, ordinary read-mask R, storage byte-ranges S, padding P и field offsets/array stride из target layout, не из порядка объявления/repr(C) предположений.
- Descriptor выбирать по операции, не подменять общий data_bytes_for_ty маской R: это ослабит transmute/layout compatibility. Новые произвольные product reinterpret casts — Unsupported; точный typed wrap v2 и его source checks сохраняются.
- Разрешить только sized struct products, ordinary поля и рекурсивные struct/ManuallyDrop products с MU<T>/[MU<T>;N] leaves, где T имеет поддержанный ordinary layout без union/storage; не раскрывать произвольный union.
- Новые shadow-carrying enum, arbitrary/nested union, MU<MU<T>>, unsupported layout/constant/overlapping aggregate → явный Unsupported; существующий ordinary Option<usize> и прежние v2 controls сохраняются.
- DST PolymorphicIter<[MU<T>]> используется по reference: сохранять metadata/обычный prefix, работать через проекции alive/data и существующий slice-storage путь; не вводить whole-DST by-value layout/copy и не объявлять reference coercion инициализацией payload.

## Инвариант и перенос
- R, S, P попарно не пересекаются; R — необходимые ordinary data bytes, S — полные storage extents; typed creation/write устанавливает только соответствующую data-mask, padding=false.
- Product read требует только R; перенос product не требует initialized(S). Настоящее чтение T из MU по-прежнему проверяет data-mask T; обычное поле рядом не доказывает состояние S.
- Aggregate: сначала capture всех source IDs/offsets пока живы; каждый ordinary field получает свою typed mask, каждый S-leaf — constant mask либо ровно один copy_by_id из своего operand в dest+field_offset; P=false отдельными диапазонами.
- Нельзя делать whole-object SetStorage(R,true) после переноса S: setter пишет false вне маски и уничтожит уже перенесённые witness. Whole-object Set(true) тем более недопустим; sibling ranges не трогать.
- Copy/Move whole product: capture live source/destination IDs/offsets и один whole-object transfer до mutation, затем только product P=false; R чтения сохраняются, S получает source-shadow побайтно. Для Copy сохраняются ветви source и destination, для Move — witness каждого живого destination byte; непокрытый overlap → Unsupported.
- Внутренние bytes MU копируются как storage, включая ранее явно записанные bytewise bytes; padding T остаётся false после typed T-write. Не путать это с product padding P, который никогда не blessing.
- Projection: offset = сумма target field offsets + index×stride; адрес формируется без чтения payload. Ordinary field write обновляет лишь свой диапазон; MU reset/copy не меняет sibling fields; opaque/неподдержанная проекция → Unsupported.
- `U:115,305,339,412,719` расширить recognition/assignment/address guards/projections согласованно; `M:218,230,417,614,699` разделить read-mask, typed setters и transfer-size; helper operand plumbing — `relevant_instruction.rs:110,129`.
- Особенно `U:664,679` Drop SetRef и `U:348` AddressOf Set: не благословлять compound S. `M:230` уже защищает flat storage от delayed SetRef; для product нужны fieldwise updates, без полного подавления ordinary updates/checks.
- `delayed_ub/instrumentation_visitor.rs:131,198,205`: сохранить targets/alias coverage и ordinary gets/sets; compound setters не должны перезаписать storage transfers. Проверки validity/raw deref/typed source reads не обходить.
- `U:115,67,495,508,644,698` один predicate shadow-carrying product для caller Store, callee entry Load, return Store index0 и caller Load; bodyless call без модели Unsupported до unpaired Store.
- Использовать прежний buffer whole product-size (`M:647`): Store/Load одного index, size equality, nested/two-arg coverage, stale cleanup; не Store каждого поля под одним index. Capture return object ID/offset до ухода stack slot.
- `library/kani_core/src/mem_init.rs:19,34,130,400,426`: сохранить один flat MEM_INIT_STATE (6 usize+2 bool), copy_by_id и argument protocol; без Option/enum в ghost-state, второго static, новых trusted premises и изменений SKIPPED_ITEMS.

## Проверяемые риски и передача
- Ложный SUCCESS: initialized alive благословляет пустой data; неверный reordered offset; старое destination survives empty overwrite; потерянный Copy witness; address/drop/delayed setter стирает false; stale return buffer; padding становится data.
- SEL0 DESIGN: общий U:494–524/610/871 и storage-result handling; production owner один, CMP1/SEL1 последовательно от опубликованного immutable tree. Select/intrinsic/fn-pointer scope сюда не включать.
- TASK-DRAFT-CMP1 содержит 20 native selectors и отдельный U8/U9 replay gate; все ожидания — гипотезы. Ни native acceptance, ни закрытие U8/U9, ни B1/B2 proof здесь не установлены.
