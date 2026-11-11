GO на реализацию CMP1 в отдельном клоне от immutable `81dd85bfce67226e283fdd9a156932e32ece080b` с правками ниже. Его tree действительно `c5b24f0b…`. Native dispatch привязать к результату U3B и review финальной дельты.

1. Инвариант R/S/P и запрет whole-object Set после transfer S корректны как постановка. Добавить проверяемое условие descriptor — диапазоны попарно не пересекаются, лежат в target size и вместе покрывают его. Учитывать внутренний/хвостовой padding и нулевые extent. При непредставимой форме — Unsupported.
2. Capture адресов сам по себе не сохраняет source shadow. Для fieldwise aggregate нужен заранее обоснованный порядок с materialized operands и неперекрывающимися source/destination ranges либо атомарная семантика transfer. Guard на непокрытый runtime overlap должен сработать до первого изменения shadow. Разные MIR locals с raw projections ещё не доказывают disjointness.
3. P=false выполнять только на точных padding-диапазонах. Полный setter с частичной маской способен затереть уже перенесённый S. Для R сохранять исходные typed-read проверки перед назначением статической маски, иначе неинициализированное ordinary поле можно ошибочно благословить.
4. Сформулировать witness coverage для whole product и нескольких аргументов. Для каждого живого неинициализированного байта назначения должен существовать абстрактный путь, который его отслеживает. Благословление невыбранного аргумента на других nondeterministic paths само по себе допустимо. Нужны проверки чтения пустого поля и внутри callee, и после return, включая непереданный обратно аргумент.

5. В существующие selectors добавить следующие конкретные harness, сохранив лимит 20.

- Частичный массив пройти через настоящее unsize/reborrow в slice и reference/ManuallyDrop projection. Заполненный индекс читается, пустой даёт uninit. Полный initialized IntoIter не проверяет этот риск.
- При заполненном S сделать ordinary поле R частично неинициализированным через допустимую для теста raw padding-write, затем проверить whole-product read/copy и чтение поля. Это контроль сохранения delayed-UB покрытия ordinary bytes.
- После drop обычного поля живого product проверить соседний пустой MU slot. Сконструировать fixture без повторного drop и чтения мёртвого объекта, например с ManuallyDrop внешнего контейнера. Это проверяет поздний Drop SetRef отдельно от чтения внутри Drop.
- В layout-unsupported зафиксировать отдельный итог каждого harness — union, storage enum, MU<MU<T>> и nested union. Одна общая diagnostic не подтверждает все guards. То же правило применить к нескольким negative harness в одном selector.
- Явно проверить Some/None и payload стандартного IntoIter, варианты с пустым остатком и ранним drop. Generic ordinary marker Pad и usize оставить в заявленном домене. Поддержку storage-payload за его пределами подтверждать отдельными случаями.

6. Параллельный старт с U3B допустим при заявленном равенстве production. В TASK перенести требование accepted U3B base с момента начала реализации на момент финальной интеграции/dispatch. Работать в новом клоне, исходный author clone U3B сохраняет свои границы.

- Перед dispatch сверить production blobs с опубликованной принятой базой U3B, перенести исправленный frame golden и принятые изолированные PFC-контроли. Старый buffer-positive из четырёх harness пока содержит UNKNOWN, поэтому его нельзя автоматически считать проходимой регрессией CMP1. Использовать окончательный selector U3B с включённым uninit.
- Если U3B production изменится, пересобрать дельту CMP1 и повторно отдать её тому же reviewer. Согласованное решение о PFC-границе базы записать явно.

7. Урезанный build-patch — OK. Экспортировать все production-изменения и только выбранные новые tests с golden/auxiliary/include-зависимостями. Исходные файлы baseline сохраняются. В полном клоне держать все тесты и upstream-кандидат.

- Зафиксировать SHA/tree build-пакета и полного candidate отдельно, плюс равенство production blobs и выбранных fixtures. Доказанный subset относится к build tree. Полный набор остаётся NOT_RUN до его собственной проверки. Не удалять failing selector ради diffstat-лимита.
- Cap $0.60 подходит для одной native-попытки. При work budget 10 мин резерв $0.540, per-test timeout должен помещаться в envelope. Core replay имеет отдельный cap/GO после native и semantic review. Исполнение и результат сейчас не проверялись.
