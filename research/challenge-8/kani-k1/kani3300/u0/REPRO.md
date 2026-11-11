# Первый отказ на пути general scratch

Кандидат `scratch-array-layout.rs` содержит 18 строк, edition 2021, `-Z uninit-checks`. Он проходит rustfmt. Его выполнение в U0 не предусмотрено. На корректном инструменте ожидается SUCCESS, поскольку читается ровно записанный слот. Точное воспроизведение диагностики кандидатом остаётся непроверенным.

В U8 единственный failed check указывает на `uninit_probe.rs:177`, создание `[MaybeUninit<u8>; 20]`. Реальный вызов `small_sort_general_with_scratch` расположен на следующей строке 178. Это первое наблюдаемое препятствие данного scratch-пути до входа в сортировку. U6 независимо остановился на `MaybeUninit<[u8; 4]>::uninit()` в строке 117. Порядок записей в summary не использован для определения исполнения.

Исходники read-only эталона `/root/kani-src-f046b70644` проверены на HEAD `f046b70644e113be0df9c22c2e6ea44a65a57566` и чистый status. Все следующие пути относятся к `kani-compiler/src/kani_middle/transform/check_uninit/` этого дерева.

1. `ptr_uninit/uninit_visitor.rs:113` обрабатывает присваивание. В строках 119–128 `PointeeInfo::from_ty` вызывается для типа назначения и при `UnionAsField` добавляется `MemoryInitOp::Unsupported` с наблюдаемой диагностикой `Checking memory initialization of type … is not supported. …`.
2. `ty_layout.rs:150` обрабатывает sized тип, в строке 153 вызывает `data_bytes_for_ty`. Для массива ветка `FieldsShape::Array` в строках 196–198 рекурсивно запрашивает layout элемента `MaybeUninit<u8>`.
3. `ty_layout.rs:403` отвергает `FieldsShape::Union(_)` как `LayoutComputationError::UnionAsField(ty)`. Текст причины `Cannot determine layout for a type that contains union of type … as a field.` формируется в строках 99–101.
4. `mod.rs:162` передаёт `MemoryInitOp::Unsupported` в `inject_unsupported_check`, а строка 681 добавляет check с `unsupported_check_type`.

Эта статическая цепочка связывает совпадающие тип и текст отказа U8 с кандидатом. Bounded summary устанавливает локацию и failed check, отдельная привязка к MIR-инструкции для кандидата отсутствует.

U6 использует иной layout, `MaybeUninit<[u8; 4]>`, и сообщает `Interaction between raw pointers and unions is not yet supported.`. В `mod.rs:322` этот текст используется для чтения через union-pointer, а в `mod.rs:488` для обновления без union field. Bounded evidence U6 не различает эти ветви, причина U8 привязана к отдельной ветке layout.

U7 сохранил function-item comparator во всём пути, включая covers, и единственный отказ с тем же текстом raw pointers/unions находится в `core/src/hint.rs:844`. Эта строка создаёт `MaybeUninit::new(true_val)` внутри реального `select_unpredictable`, вызываемого `swap_if_less`. Таким образом, устранение comparator fn pointer переводит U7 к следующему unsupported в текущем пакете.

Для стадии патча U1 получены три разных препятствия MaybeUninit — array-of-union layout U8, merge output U6 и внутренняя pointer-valued union в `select_unpredictable` U7. Калибровка U1/U2 дополнительно остаётся на несовместимом transmute layout. Достижимые covers после unsupported не подтверждают чувствительность к uninit-чтению.
