C2 существенно усилил вывод: контекстно изменённое тело действительно доходит до GOTO emission падающего root. Это уже не только cache-hit при analysis.
1. Наблюдается цепочка writer72 → consumers130/187: один Instance/символ, hash9bae и last_writer=into_iter_next; собственные scans len у manual/index не добавляют ops.
   Значит, root-specific инструментация сохраняется в unit-shared cache и используется другими roots; их scans не заменяют её собственным вариантом тела.
   nonzero_ops=0 относится к scan уже изменённого тела из18 инструкций. Это не устанавливает результат fresh analysis исходного тела из8 инструкций.
   Это подтверждает механизм переноса. Однако одного тела недостаточно для объяснения FAIL: оно получает разные self, объекты и ранее сформированный shadow в разных callers.
   PARTIAL/187 из187 не означает полной witness coverage; сохранённая локальная цепочка пригодна, отсутствующие external witnesses не считаются отсутствующими операциями.
2. Различие callers статически видно на уровне Rust: index создаёт обычный IndexRange{start:0,end:2}, затем заимствует его;
   manual помещает тот же initialized header в PolymorphicIter с MaybeUninit payload, переносит через constructor/ManuallyDrop и deref/unsize.
   Рабочая гипотеза: product/by-value пути обеспечивают R header, а для обычного local/call-result прямого root нет соответствующего shadow write при исполнении импортированных checks.
   Seed pointer/reference bytes не является seed pointee. Одинаковые checks потому могут пройти в одном caller и отказать в другом; source-level header инициализирован в обоих.
   Но фактический Constant/Call/Aggregate MIR, Set/Copy/transfer для header, конкретные object+offset/R перед Get не сохранены. Объявлять именно constant-assignment причиной пока нельзя.
3. Сейчас Cloud $0: зафиксировать cache invariant и маленький дизайн прототипа «новый BodyTransformation на каждый root» при тех же unit/stubs/config/global passes.
   Для постоянного решения возможен pristine local cache + root overlay. Частичный reset, отключение CheckRef или общий seed вместо изоляции не подходят.
   Статический разбор может объяснить ожидаемые paths и подготовить исправление; из имеющихся hashes восстановить отсутствующий caller MIR и runtime shadow невозможно.
4. Минимальный полезный следующий Cloud — прототип fresh-transformer с ТОЧНО тремя roots C2 и неизменными library, flags, ordering algorithm и диагностикой.
   C2 служит baseline; меняется только lifetime/cache isolation. Перед запуском — review точной дельты, без исправления ordinary/constant transfer одновременно.
   Проверить actual order next→manual→index; next сохраняет собственные необходимые CheckRefs; index/manual не получают чужой last_writer; index становится SUCCESS, manual/next остаются SUCCESS.
   Сопоставить caller/local MIR hashes и фактически consumed len после собственного анализа; не принимать просто «все зелёные» при исчезновении инструментации повсюду.
   Такой результат установит причинную роль shared-cache lifetime для данного false-positive. Точная история конкретного R-byte останется отдельным уровнем объяснения.
   Если index продолжит FAIL, разделить остаточный внутриконтекстный дефект и неполную изоляцию; наблюдение C2 от этого не отменяется.
5. Резерв трёх roots по1m: (3+30)×$0.0135=$0.4455; предлагаю новый явно разрешённый pilot cap $0.50.
   При разрешённом переносе остатка $0.341 нехватка именно до резерва $0.1045; отдельная стадия/ledger определяет, можно ли его использовать. Прежний фактический расход $0.108 не заменяет резерв.
   index_range_len один в unit стоит $0.4185, но лишь убирает triggering context; похожий passing baseline уже есть в CMP4-B. Его не ставил бы обязательным промежуточным этапом.
   За дополнительные $0.027 резерва трёхрутный cache-прототип даст более прямую проверку механизма, поэтому бюджет владельца на этот pilot просить стоит после статического review.
6. Это причинный pilot, не готовность production-fix: C2 не содержит свежей calibration pair. Перед приёмкой фикса отдельно нужны uninit-positive/negative controls и native regressions, включая IntoIter/compound/padding.
   Без нового бюджета — остановиться на статическом разборе/готовом design; оставшихся $0.341 не хватает даже на один Build. Сейчас код не менять и ничего не запускать.
