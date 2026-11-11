# KANI3300 U1R — независимое статическое ревью

Вердикт: **SOUND** в заявленной поддерживаемой области: обоснованных контрпримеров корректности не найдено.
Это результат чтения исходников, не доказательство soundness и не подтверждение native PASS.
Дата: 2026-11-11; reviewer: Runtime Codex, не автор U1; одна стадия, Cloud $0.
Research HEAD на входе `9d7e1699d3aa66512779ec75b47ced8e70490ffb`; дополнительные коммиты после `7c0d8e8413` — документы.
Patch SHA-256 `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467` совпал.
Изолированный клон `/root/kani-review-3300`: база `f046b70644e113be0df9c22c2e6ea44a65a57566`,
после `git apply --index` дерево `b9c36ac5ed550e39d26e1d1d77000052e62a9bb4` совпало с пакетом.
Далее `V` = `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs`,
`I` = `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs`,
`L` = `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs`,
`M` = `library/kani_core/src/mem_init.rs`; все координаты относятся к патченному клону.

- Transfer сохраняет init bit при смене объекта/смещения; иначе bless охватывает весь перезаписанный dst (`M:100–126`).
  Для каждого неинициализированного выходного байта существует путь, следящий за соответствующим исходным байтом.
  При overlap/self-copy этот путь использует смещение источника до переноса; bless остальных путей не является proof credit.
- AssignUnion захватывает оба адреса и переносит shadow до изменения слота (`V:124–138`, `I:699–735`).
  Расчёт extent берёт размер всего слота/массива, для среза — размер элемента, включая padding (`L:124–142`).
- Создание union с пустым полем очищает весь слот, а не ноль байтов поля `()` (`I:548–593`).
  Запись payload использует маску самого поля (`V:397–402`); ZST обходится без чтения shadow (`M:213–214,228–229,341–342`).
- Repeat константы повторяет byte mask; Repeat локального источника и array aggregate переносят каждый элемент
  по ConstantIndex. Источник и dst должны быть разными непроецированными locals, иначе Unsupported (`V:150–213`).
- Transmute в T/ManuallyDrop<T> проверяет data-mask T по адресу исходного слота до формирования T;
  константа проверяется отдельно, неизвестная форма отказывается (`V:216–254,767–777`). Padding T не требуется.
- MIR-вызовы: номера аргументов начинаются с 1, return использует 0; Store перед Return и Load после Call
  соединяют адреса callee/caller (`V:63–79,455–468,592–605,644–651`, `M:377–411`).
  Единственный return всегда сохраняет buffer; аргументы выбираются недетерминированно, остальные получают bless.
- Raw AddressOf не инициализирует payload и не читает конечный pointee; загружаемый промежуточный указатель
  всё ещё посещается (`V:304–317,730–747`). Ссылка на payload требует CheckRef (`V:749–754`).
- Возврат слота без обычного MIR body, typed_swap слота, вложенные union и неизвестные формы assignment
  сохраняют отказ (`V:144–147,386–396,455–468,523–532`; `L:130`). Поддержка этих случаев не заявляется.
- Delayed-UB использует прежние points-to/targets: его generic SetRef для storage подавлен, чтобы не стереть transfer;
  payload-проверки остаются (`I:218–244`). ValidValuePass и его порядок неизменны (`transform/mod.rs:124–145`).

Контрпримеры: не установлены; ложный SUCCESS, ложный отказ или неожиданная Unsupported не заявляются.
Регрессионные кандидаты в `review/` (все **NOT_RUN**, flags edition 2021 / uninit-checks в каждом файле):
1. `overwrite-copy.rs` — FAILED/uninit: частичный источник поверх полностью заполненного dst, чтение второго байта.
2. `overlap-copy.rs` — FAILED/uninit в обе стороны: memmove двух слотов, включая неинициализированный источник.
3. `repeat-local.rs` — FAILED/uninit: повтор локального слота поверх заполненного массива, чтение последнего элемента.
4. `reset-zst.rs` — ZST допустим; затем FAILED/uninit: сброс заполненного u64 через raw alias.
5. `padded-manually-drop.rs` — FAILED/uninit: неполный repr(C) payload через ManuallyDrop, не чтение padding.
6. `argument-return.rs` — FAILED/uninit на выборе второго аргумента: два слота, промежуточный MIR-вызов и return 0.
Ожидаемый прогноз U1 совпадает с корректным инструментом; это тестовые гипотезы, не наблюдавшиеся результаты.

Проверки: apply/tree identity и `git diff --cached --check` PASS. Python-модель copy перебрала 13 058 случаев
для 1–6 байтов, всех init-масок, допустимых src/dst/length: каждый uninit output сохранил shadow witness.
Модель проверяет только формулу transfer, не MIR lowering, compiler binding или исполнение Kani.
Builds, cargo/rustc/Kani/CBMC, чтение raw CI evidence не выполнялись; 20/20 PASS остаётся source-reported claim.
Upstream: +548/−150 production существенно для bugfix; стоит выделить storage-recognition/transfer и снабдить
copy/argument-buffer явным инвариантом witness coverage. Сохранить negative golden и добавить overlap/два аргумента.
