1. GO координатора на U4 поддерживаю именно как диагностическое исключение: прежний gate native CMP2 PASS отменён, а не выполнен.
   Зафиксировать это в задании/PRE-BUILD; e1ed2374b7, точные request/patch/applied tree и остальные ограничения сохранить. Нового согласования того же GO не требуется.
   U4 проверит U8 без CMP3-адаптеров и добавит U9; это полезнее ещё одного общего replay. Резерв $0.6075, cap $0.80, одна попытка.
2. U4 принимать по пяти строкам: U2/U6/U8 SUCCESS, нормальный возврат U8, U1 — ожидаемый uninit, U9 — только uninit scratch[4] после успешного scratch[3].
   Для U9 нужна привязка отказа к нужному чтению, а не просто слово uninit; covers после намеренного UB не дают credit. При недостаточной привязке — UNKNOWN.
   Успешный U4 не исправляет CMP2 native failures и не означает готовность compound-патча upstream.
3. Гипотеза о constant assignment правдоподобна, но const fn в исходнике не устанавливает Rvalue::Use(Constant) в фактическом MIR.
   Статически в CMP2 ordinary assignment не имеет общего typed-shadow seed для Constant; storage-ветка умеет constant_init_mask → SetStorage.
   Seed ordinary formal parameters в delayed-UB не покрывает автоматически ordinary locals. Это конкретный кандидат пробела, а не установленная причина шага 1.
   Проходящий ManuallyDrop-путь не доказывает гипотезу: изменяются также borrow/call/points-to и время Drop.
4. Следующий шаг — ограниченная немутирующая трассировка шага 1 и проходящего шага 4, затем условный узкий фикс; ещё один слепой seed не рекомендую.
   Нужны фактическое присваивание/borrow в MIR, instance/place, цели points-to, object+offset, R до/после и порядок Set/Copy/Get.
   Изменение только диагностическое, отдельно от неизменного production CMP2; не вставлять pre-len raw-read/AddressOf в harness.
5. Для проверки pre-existing сделать тот же core step1 на чистом f046 с теми же fixtures/toolchain/flags; clean-пакет содержит только test-only std-добавления.
   Добавить парный runtime-вариант zero_to(n), n недетерминированное и ограниченное, с тем же len/assert; убедиться по MIR, что присваивания различаются.
   Тот же отказ clean установит наличие проблемы до CMP2; clean SUCCESS и CMP2 FAIL — регрессию этого fixture. Unsupported оставит сравнение неразрешённым.
   Не ожидать Unsupported автоматически: сам IndexRange — ordinary-тип без MaybeUninit. Native-аналог const struct полезен, но не заменяет точный core repro.
6. Если трасса подтвердит пропущенный constant write — фиксировать только этот transfer: typed R/data mask при реальном присваивании, корректный destination/offset.
   Не инициализировать padding, S-payload, весь product или pointee через ссылку; не seed на каждом borrow/get. Неподдерживаемые layouts остаются fail-closed.
   Тесты: constant/runtime ordinary scalar и struct, padded struct с отрицательным чтением padding, compound с пустым/частично заполненным MaybeUninit.
   Сохранить initialized/uninitialized пары, move/copy, projection, argument/return и уже принятые buffer/frame controls; независимый review дельты до replay.
7. Для ready-for-review «части 2» Kani (compound storage) нужны явный R/S/P-инвариант, поддерживаемый домен и ограничения, review всего diff относительно части 1,
   native positives без неожиданных отказов, точные отрицательные контроли и регрессии части 1 на финальном immutable кандидате.
   Сейчас не выполнены IntoIter/grouped-positive и required u8 у padding-negative; последнее может быть проблемой наблюдаемости, но acceptance пока не закрыта.
   После изменения production повторить U4 на новом hash. Старый U8 PASS не переносится автоматически. До этого возможен только Draft с перечисленными blockers.
8. Владельцу: «По RESULT CMP3, U8 u8/N4 прошёл с uninit-checks, 0/550, cover 1/1; общий diagnostic gate FAIL из-за шагов 1–3 и ожидаемой U1».
   После U4 отдельно сообщить проверенную чувствительность scratch[4], точные hashes и открытые native failures; не заявлять закрытие #3300/Challenge 8.
   Это bounded normal-return маршрут с function-item comparator и panic stub; другие T/N/F, PFC, valid-value и полное покрытие SmallSort отсюда не следуют.
   RESULT сообщает Brief HTTP404 и actual argv UNKNOWN: до достаточного штатного evidence binding обозначать результаты source-reported, independent credit NONE.
   Диагностический U4, готовность upstream-патча и формальная приёмка SmallSort — три отдельных результата.
