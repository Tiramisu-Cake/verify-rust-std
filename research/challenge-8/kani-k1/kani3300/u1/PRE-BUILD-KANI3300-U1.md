# KANI3300 U1 — пакет для PRE-BUILD после U0

RESULT U0 прочитан из опубликованного head `1f2cde2e9d3cde683411c81cc692f1a3aadb6d57`, путь `research/challenge-8/kani-k1/kani3300/u0/RESULT-KANI3300-U0.md`. Сборка U0 `51f228c7-615f-4027-8bae-d68fb293e132` на head `69b3b92fc9965e3e35af4eeff80d02c650745285` дала SUCCESS U5 и семь unsupported. Подтверждённое первое препятствие U8 находится при создании массива из 20 слотов.

## Идентичность и лимиты

- Ветка `experiment/kani-k1-kani3300u1-20261111`, стадия `kani3300-u1`, владелец `k1-merge`.
- Tooling `c98d7cee0d`. Пин Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`. Локальный коммит Kani `adf74dd0dc8438127ccb8046df183bd9f1297bce`.
- SHA-256 патча `0bd59c0589757fac590f1aae00147b61fcd4bcec1151c4978699787cfc79de6c`. SHA-256 request `1ebf6682dbe45c3effc81521014de0c4b8cc779dc75c8c14e4d6240c9a165ead`.
- Дерево после применения `d17e98764d993fc39bfd617db6e3677cab619203` совпало с деревом локального коммита Kani.
- `kani3300-u1-native-20261111-02`, `kani-tests`, `harnesses: []`, 20 selectors, 20 мин на native job, 150 с на selector. Максимальная резервация с 30 мин накладных расходов равна $0.675 из cap $0.90. Расход U1 до dispatch равен $0.

## Семантика

- Объект и смещение выбирают один байт shadow. Для `MaybeUninit<T> -> T` и `-> ManuallyDrop<T>` проверка применяет маску данных T к адресу исходного операнда перед transmute. Проверки validity остаются в штатном pass.
- Получение raw-адреса слота или его поля сохраняет shadow. Запись поля обновляет маску поля по его адресу. Создание пустого слота очищает весь его размер.
- Целый слот переносит shadow при присваивании, копировании и передаче через вызов с MIR. На пути, отслеживающем исходный байт копирования, shadow переходит к соответствующему байту назначения. Старое состояние перезаписанного байта назначения исключается на остальных путях.
- Плоские массивы и срезы слотов используют размер элемента для смещений и переноса. Извлечение значения проверяет маску данных самого T.
- `Rvalue::Repeat` со статическим N поддержан для константного операнда и отдельного локального слота, в котором MIR сохранил результат конструктора. В первом случае повторяется byte mask, во втором передаются состояния байтов каждому элементу по его статическому смещению. Фикстура U8 использует точную форму `[MaybeUninit::<u8>::uninit(); 20]`.
- Произвольные и вложенные union, потенциально перекрывающиеся repeat/array aggregate, `typed_swap`, возвраты без MIR и вызовы через fn-pointer вне области патча. Общий points-to и алгоритм delayed-UB сохраняются.

## Сверка первых препятствий U0

| Путь | Препятствие U0 и обработка в патче | Фикстуры в пакете |
|---|---|---|
| U1/U2 | Безусловный отказ union-transmute заменяется проверкой shadow исходного значения по маске T | `maybe-uninit-assume-init`, `maybe-uninit-initialized` |
| U3 | Адрес слота сохраняет shadow, существующий `VolatileLoad` проверяет data bytes u8 | `maybe-uninit-volatile-read`, успешный `volatile_read_after_write` |
| U6 | Конструирование и адресация `MaybeUninit<[u8; 4]>` отслеживают слот размером 4 байта | `array_value_as_used_by_merge_output`, `maybe-uninit-partial-copy` |
| U7 | Конструирование pointer-valued `MaybeUninit` использует union aggregate и transfer состояния | `pointer_valued_slot_as_used_by_select_unpredictable` проверяет этот участок |
| U8 | Специальная обработка массива слотов и статического repeat обходит общий отказ union-as-field | `maybe-uninit-scratch-array`, `maybe-uninit-scratch-array-unwritten` |

Сам прямой вызов `core::hint::select_unpredictable(b, x, y)` остаётся непроверенным. В исходниках есть отдельный вопрос обработки его intrinsic fallback, поскольку visitor классифицирует intrinsic отдельно от обычного MIR-вызова. Дополнительная поддержка этого вызова требует отдельной проверки взаимодействия с aliasing. Положительный тест U7 в текущем пакете относится к первому union-препятствию.

## Проверки

- PASS для `validate` и `prepare-kani` на свежем checkout. Последний проверил SHA-256, выполнил `git apply --check --index` и сверил пути всех фикстур и companion-файлов.
- PASS для `git diff --check` и `rustfmt --check` на применённом дереве. Production 7 файлов, +548/−150. Новые тесты и golden 22 файла, +328. Существующие golden и tooling совпадают с базой.
- Два новых положительных selectors с девятью harnesses требуют успешный Kani exit. Scratch repro сохраняет запись `scratch[0]` и наблюдаемое чтение через `assume_init`.
- Девять новых отрицательных selectors ожидают конкретную uninit-диагностику из собственного вывода. Golden привязывают FAILURE к harness или safety property и требуют `VERIFICATION:- FAILED`. Пара scratch дополнительно читает незаписанный `scratch[1]`.
- Девять selectors покрывают штатные union, copy, padding и delayed-UB регрессии. `fixme_unions.rs` и `slices_fixme.rs` имеют статус NOT_RUN.
- Native результаты ожидаются после GO координатора для точного SHA пакета. Локально Kani, cargo, rustc и CBMC не запускались.
