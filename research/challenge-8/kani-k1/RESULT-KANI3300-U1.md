# RESULT-KANI3300-U1

Статус первой попытки RUNNER_ERROR на компиляции Kani; repair 1 подготовлен к PRE-BUILD review.
Build `6f8c5b75-42e9-4b2b-bfea-95826896d247`, Cloud FAILURE, gate false, Kani exit отсутствует.
Head `5de1d66706ccbe00a15087b2c8ace509ab6bab0e`, pin `f046b70644e113be0df9c22c2e6ea44a65a57566`.
Request `kani3300-u1-native-20261111-02`, SHA-256 `1ebf6682dbe45c3effc81521014de0c4b8cc779dc75c8c14e4d6240c9a165ead`.
Patch SHA-256 `0bd59c0589757fac590f1aae00147b61fcd4bcec1151c4978699787cfc79de6c`.
Bounded summary сообщает E0599 в `check_uninit/ty_layout.rs:112` и отсутствие trait `CrateDef` для `AdtDef::def_id`.
Native report отсутствует; build stage не создал `build.ok`, prerequisite verify stage не выполнен.
`check-tooling` подтвердил pool, lane files и request/patch hashes; общий exit 1 из-за `tree=None`. Build tree identity не установлена.

Семантика подготовленного патча по исходникам и локальному preflight.
Shadow хранит один недетерминированно выбранный байт по object ID и offset.
By-value transmute проверяет shadow источника по data-byte mask T перед формированием T, включая `ManuallyDrop<T>`.
Raw-адрес сохраняет shadow; поле обновляет свою маску; пустой aggregate очищает весь слот.
Целые слоты и flat arrays переносят shadow через assign/copy и обычные MIR-вызовы.
Статический repeat поддерживает константу и отдельный локальный слот; срезы используют размер/шаг элемента.
Маска T сохраняет различие data/padding; независимые validity checks остаются обязательными.

Diffstat production 7 файлов, +548/−150; новые tests/golden 22 файла, +328.
Локально PASS для apply-check, tree identity, rustfmt и diff-check. Native проверка семантики ожидается.

| Группа | Selectors | Результат первой попытки |
|---|---|---|
| Новые positive, включая scratch 20 | 2, девять harnesses | NOT_RUN, prerequisite build failed |
| Новые negative, включая scratch[1] и volatile | 9 | NOT_RUN, prerequisite build failed |
| Существующие регрессии | 9 | NOT_RUN, prerequisite build failed |
| fixme union/slice | Исключены | NOT_RUN по заданию |

Чувствительность отрицательных тестов и отсутствие unexpected SUCCESS пока не установлены.
Unsupported scope включает произвольные/вложенные union, перекрывающиеся repeat/array aggregate, typed_swap и fn-pointer calls.
Прямой `select_unpredictable` непроверен; фикстура U7 покрывает конструирование и чтение pointer-valued слота.
Расход первой попытки $0.0675, резерв снят; elapsed 272.948 с, ledger 5 минут.
Repair 1 добавляет `use rustc_public::CrateDef`, остальные исходники и все тесты совпадают с первой попыткой.
Локальный repair commit `546bcf30379b9b2894f94b1305d5277cc5b4574c`; tree `b9c36ac5ed550e39d26e1d1d77000052e62a9bb4`.
Repair request `kani3300-u1-repair1-20261111-03`, SHA-256 `69d892414672163b0d4969c13292c0141d9b5e97ada72dd7d0221c10199062cc`.
Repair patch SHA-256 `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`.
Repair reservation $0.6750; общий максимум U1 $0.7425 при cap $0.90. Требуется GO точного repair packet.
Черновик upstream PR находится в `kani3300/u1/UPSTREAM-PR-DRAFT.md`; native validation pending.
