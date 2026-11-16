# Аудит: внешние тексты подачи стека Kani (#3300), нарезка на PR, соответствие кода заявлениям

2026-11-16. Ответ на `BRIEF-STACK-COMMS-REVIEW-2026-11-16.md` (g0 `e3413c5bcf`). Аудит выполнен только чтением: ни прогонов, ни публикаций в upstream не было.

## 0. Сводка

1. **На #752 уже есть ревью, в брифе его нет.** 14.11 feliperodri запросил ревью Copilot; оно рекомендует изменения по двум пунктам высокой серьёзности: не включены проверки uninit / valid-value / immutable bytes, и доказательства сортировки покрывают не все требуемые длины. Ответа автора на странице нет. Сообщение организаторам должно быть ответом на это ревью в #752, а не новым текстом в #56.
2. **kani#5151 — issue того же feliperodri ровно про то, что делает стек**, с цифрами влияния. Design note нужно сократить в 3–4 раза и поставить комментарием туда, а не в старый трекер #3300. До публикации прогнать репродьюсер из #5151 на прототипе: ни один из 365 новых тестовых файлов его не повторяет.
3. **PR-01 и PR-02 сегодня не открывать.** PR-01 — 520 строк без единого end-to-end теста, плюс правки к собственному ещё не отревьюенному #5172. PR-02 — все 12 тестов ожидают SUCCESS и, по чтению кода, проходят и на `main`; единственный negative-тест удалён с объяснением, которое противоречит тестам upstream и вашему же тесту на голове 4; финальная голова не запускалась и не запушена.
4. **Нарезка повторяет историю разработки, а не проверяемость.** Четыре куска стека, судя по коду, — самостоятельные дефекты `main` (reset в automatic harness, смещения в layout, рекурсия в points-to, утечка delayed-инструментации между harness). Каждый подтверждается одним прогоном на `main`; подтверждённые стоит подавать маленькими независимыми PR прямо на `main`, а ядро (маски констант + `raw_eq`, хранение `MaybeUninit`) — после согласования дизайна.
5. **Слоп.** В текстах — «бухгалтерские» оговорки о том, чего прогон не доказывает, свой словарь и шум идентификаторов. В коде — комментарии-запреты (около половины строк комментариев против ≈10 % в соседнем коде upstream), внутренняя метка `A3`, unit-тесты, названные по свойствам, которые они не проверяют, 18 `fatal` на 436 строк, мёртвое поле, пользовательская документация на внутреннем языке.
6. **Темп.** #5172 открыт в субботу 14.11, сегодня понедельник; ноль реакции за выходные — норма. Все тексты читает один человек (feliperodri ведёт и Kani, и triage Challenge 8). Сегодня от аккаунта уже ушло три текста; ещё четыре за день сделают именно то впечатление, которого вы боитесь.

Полные предлагаемые тексты — в разделе 8. В них есть пометки `<<…>>`: туда нужно подставить результат прогона, которого у меня нет.

## 1. Что проверено и чего проверить не удалось

- Бриф и исходники текстов: дословные тексты A–D в брифе совпадают с файлами в `c2-slices/pr-texts/` и `w0-u/` построчно.
- Код: форк `Tiramisu-Cake/kani`, база `0aac16ef62`, #5172 `6fe484b300`, PR-01 `d82752c8bc`, PR-02 `932fb8395a`, PR-03…07 (исторические головы, финальное дерево `9829702c1a` совпадает с `freeze/kani-3300-c2`). Диффы PR-01 и PR-02 прочитаны целиком, PR-03 целиком, PR-04…07 — исходники и комментарии выборочно.
- Финальная голова PR-02 `05da1a7a8c` в форке отсутствует (ветка `fix/kani-3300-init-02-immutable` указывает на `932fb8395a`). Reset-исправление смотрел по `f695f653ef` (compiler diff по `FINAL.md` побайтово тот же) и по фикстурам из `uninit-ci/ch8-pr02-reset-c`.
- Upstream: `CONTRIBUTING.md`, шаблон PR, 53 последних коммита `main` с текстами squash-сообщений (то есть описаниями принятых PR).
- Страницы GitHub: kani #5172, #5151, #3300, #5179, #5181; verify-rust-std #752, #762, #56. Читались через инструмент, который пересказывает страницу, а не отдаёт её дословно, поэтому тексты #5172/#5179/#5181 оценены по структуре и содержанию, не по формулировкам.
- **Не удалось:** запустить Kani (сборки и прогонов не было, всё о поведении `main` — из чтения кода на `0aac16ef62`, помечено «по коду»); прочитать комментарий в #3762 (страница не отдала содержимое); #5104, #5117, #5072, verify-rust-std#701 не открывал.

## 2. Факты, которые меняют план

### 2.1. Ревью на #752

По [странице PR](https://github.com/model-checking/verify-rust-std/pull/752): 14.11 feliperodri поставил метку Challenge и запросил «сбалансированное» ревью у Copilot. Ревью вышло в тот же день с рекомендацией изменений и двумя замечаниями высокой серьёзности:

1. исключены обязательные проверки памяти — чтение неинициализированной памяти, невалидные значения, запись в immutable bytes;
2. доказательства сортировки покрывают не все требуемые длины срезов.

Инлайн-комментарии указывают на список «Not covered» в `verify.rs` и на комментарий о raw pair в `forwarding_contracts.rs`. В брифе сказано «комментариев и ревью пока нет» — это устарело; проверяется открытием страницы PR. Следствия:

- Организатор уже спросил. Двое суток без ответа на запрошенное им ревью хуже, чем любая формулировка в #56.
- Замечание 1 — прямой повод рассказать про работу в Kani: это единственное место, где стек Kani и заявка сходятся для читателя.
- Замечание 2 делает вопрос о длинах не инициативой «сузить условие», а ответом на замечание.
- Текст E (новый раздел Limitations) не нужен: в описании #752 уже есть раздел Limitations из восьми пунктов, и он написан яснее, чем E (см. 7.7).

### 2.2. kani#5151

[#5151](https://github.com/model-checking/kani/issues/5151), открыт feliperodri 11.11: «`-Z uninit-checks`: arrays of `MaybeUninit<T>` with non-trivial `T` are unsupported». Репродьюсер — `[MaybeUninit<D>; 2]`, где у `D` есть `Drop`, запись в слот 0 и `drop_in_place` на неинициализированный слот 1; Kani отвечает ошибкой про union как поле. 13.11 он же добавил измерение: на решении Challenge 2 (verify-rust-std#649) с `-Z uninit-checks` 91 из 394 harness падает на unsupported, из них 77 — из-за union в буфере (58 — массивы `MaybeUninit`, 19 — `PointerGenerator` с `MaybeUninit<[u8; N]>` внутри), остальные 14 — trait objects (#5166). Мотивирующие примеры из std: `MapWindows`, `array::IntoIter`, ArrayVec-подобный код.

Следствия:

- Это лучший возможный адрес для design note: свежий issue активного мейнтейнера с его собственной мотивацией. #3300 — давний трекер с чек-листом; видимые на странице комментарии — ранняя дискуссия о padding.
- Сейчас note открывается фразой «SmallSort needs…». Мейнтейнеру SmallSort не нужен; ему нужен #5151.
- В Limitations вашей же note стоит «struct-held arrays of `MaybeUninit` (`PolymorphicIter`)» — это `array::IntoIter`, один из его примеров. Сказать об этом надо в первых строках, а не в конце.
- **Результат его репродьюсера на прототипе неизвестен.** В `tests/expected/uninit` финального дерева нет ни одного теста с `drop_in_place`, а `impl Drop` встречается только в двух тестах из #5172. Это первое, что он запустит. Прогнать до публикации и добавить тестом.
- Сильнее любого SmallSort-replay будет его же метрика: сколько из 77 harness после стека доходят до результата. Репозиторий у вас под рукой.

### 2.3. Один читатель и ритм upstream

- feliperodri: автор #5151, коммитер Kani (в последних 53 коммитах `main` — пять его), он же метит и разбирает PR Challenge 8 (#752 14.11, #762 сегодня взял на себя). «Две аудитории» из брифа — в значительной части один человек.
- В `main` Kani 12 коммитов датированы пятницей 13.11: мейнтейнеры мержат пачками. Ваш #5153 смержен в той же пачке — у аккаунта уже есть принятый PR, вы не «новый контрибьютор».
- #5172 создан в субботу 14.11. Отсутствие реакции к понедельнику ничего не значит.
- Типичный принятый PR за последние две недели: 2–15 файлов, 50–700 строк; три крупнейших — 37 файлов / 2 533 строки, 34 / 1 860 и 41 / 1 092. Стек без #5172 — 356 файлов, +10 279 / −440. Каталог `tests/expected/uninit` вырастает с 59 до 424 файлов.
- Описания принятых PR в этой же области (#5115, #5057) длинные и структурированные, с разделами Summary / Changes / Tests / Limitations и с оговорками о неполных прогонах. Длина и структура upstream не смущают. Отличает их другое: первая фраза — видимая пользователю ошибка, есть `Resolves #N` и есть пара «на базе падает — с исправлением проходит».
- Каждому PR в компилятор CI Kani автоматически ставит метки бенчмарк-прогонов (на #5172 они стоят). Два стековых PR — это ещё два полных прогона CI на чужих раннерах для кода, который пока нельзя смержить.

### 2.4. #762 и #56

- [#762](https://github.com/model-checking/verify-rust-std/pull/762) (VeriFast, открыт сегодня) заявляет все длины и обобщённый `T` при длинном списке доверенных допущений. Упоминать его нельзя и не нужно, но он означает: комитет увидит буквальное прочтение «arbitrary valid length». Вопрос о длинах надо ставить нейтрально и быть готовыми к ответу «все».
- В [#56](https://github.com/model-checking/verify-rust-std/issues/56) другой участник уже спросил, достаточно ли длин до порогов и нужны ли доказательства `insertion_sort_shift_left` за ними. Судя по странице, ответа нет. Ваш вопрос 1 его дублирует.
- Прежний ответ организатора там же: доказательства для примитивных типов с порядком по умолчанию считаются полноценным решением, другие инструменты допустимы. Вопрос 2 из текста D («какие ещё экземпляры типов нужны?») поэтому лишний: он приглашает расширить требования, на которые уже дан выгодный вам ответ.

## 3. Соответствие кода заявлениям

### 3.1. PR-01 (`6fe484b300..d82752c8bc`: 10 файлов, +524 / −67)

| Заявление в тексте A | Что в коде | Вердикт |
|---|---|---|
| Анализ использует тела, выбранные для contract registration и discarded closures | `delayed_ub/mod.rs:97–122`: для `kani_register_contract` и замыканий с телом из одного `Unreachable` берётся тело из transformer; `points_to_analysis.rs:630–638` | Верно. В upstream это «unused closures» (`contracts.rs`, `mark_unused`); «discarded» — ваш термин |
| Циклы вызовов сообщаются «short diagnostics» | `ActiveCalls::enter_at`: до 12 кадров по 4 096 символов, unit-тест проверяет `< 51000` байт | Диагностика ограничена, не коротка. В каждом кадре `[provenance=source]` |
| Анализ останавливается, неполный граф не используется | Ошибка защёлкивается, корень получает unsupported-проверку на входе (`mod.rs:191–210`), остальные harness идут дальше | Верно |
| «Keep the existing call resolution, visit each call's operands once, and retain the checks collected for that call» | `resolve_call` меняется: новая сигнатура и `checked_body(tcx, …)` вместо `instance.body()` (`:538`). «Операнды один раз» и «сохранить проверки» сделаны в #5172, в этом диффе их нет | **Неверно дважды**: разрешение вызовов меняется, а вторая половина фразы описывает чужой дифф |
| Инициализируются «ordinary scalar and reference argument slots» | `instrumentation_visitor.rs:46–68`: любой аргумент не-union с `PointeeLayout::Sized`, если `needs_set` | Занижено: это все sized не-union параметры, включая структуры и массивы |
| «без referents и union storage» | `SetRef` на сам локал, union исключён | Верно |
| «302 regression tests passed» | Прогон 43696666260: kani 50, expected 213, ui 17, script-based-pre 3, json-handler 17, std-checks 2 | **Вводит в заблуждение умолчанием.** Это выборка: в upstream только kani ≈ 627 и expected ≈ 535 (цифры из описания #5115). В тексте B оговорка «selected» есть, в A нет |
| «9 ActiveCalls unit tests» | 9 `#[test]`, из них 4 проверяют свойства тестовой заглушки (см. 6.2) | Число верное, вес завышен |

Чего в тексте нет, а в диффе есть:

- **Правки к #5172.** Замена `instance.body()` на `checked_body` в `resolve_call` — исправление кода, добавленного в #5172 вопреки комментарию upstream в `kani_middle/mod.rs` («Use this instead of `instance.body()` wherever the body may belong to user code»). Плюс переписаны четыре комментария из #5172 в исходниках и по одной строке комментария в четырёх тестах из #5172. Ваш внутренний ревьюер это отметил («comment-only edits to inherited B1 tests»), но в PR это будет выглядеть как посторонний шум. Место этим правкам — fixup-коммит в #5172, пока его никто не ревьюил.
- Вынос `needs_set` в метод с заменой поясняющего комментария upstream (про зацикливание на графе с циклами и пример с `Vec`) на «preserve the existing terminating walk». Код перенесён без изменений — комментарий надо перенести дословно.

Главное: **PR-01 не содержит ни одного теста, который падает до него и проходит после.** Текст объясняет это тем, что тесты «need the later `MaybeUninit` storage/transfer and closure-layout slices». Это свойство написанных тестов, а не функциональности:

- Рекурсия. По коду базы защиты нет: `points_to_analysis.rs:520` на `0aac16ef62` вызывает `PointsToAnalysis::run` для каждого вызова без проверки повтора. Ожидаемо, что рекурсивная функция, достижимая из harness с delayed-UB целью, переполняет стек компилятора. Цель создаётся без `MaybeUninit` — приведением указателя к типу с другим padding, как в существующем `tests/expected/uninit/delayed-ub/delayed-ub.rs`. Если это подтвердится одним прогоном на `main`, у PR появляется точный заголовок («вместо падения компилятора — unsupported») и свой тест.
- Тела контрактов и параметры. Для каждого нужен тест на конструкциях, которые `main` уже поддерживает. Если такого теста написать нельзя — изменение ненаблюдаемо на этой голове и должно ехать в том PR, где становится наблюдаемым.

### 3.2. PR-02 (`d82752c8bc..932fb8395a`: 29 файлов, +1 058 / −32; reset-fix: ещё 1 файл компилятора и 24 файла фикстур)

| Заявление в тексте B | Что в коде | Вердикт |
|---|---|---|
| «Otherwise, a legal comparison with an initialized constant can report an uninitialized read» | На `main` `raw_eq` входит в `can_skip_intrinsic` (`uninit_visitor.rs:646` на базе); проверять операнды он начинает в PR-03 | **На этой голове неверно.** Ложное срабатывание появится только после PR-03. PR-02 — инфраструктура без наблюдаемого эффекта |
| Записываются origins анонимных аллокаций и привязываются к символам | `anonymous_allocations.rs`, `immutable_allocations.rs`, вызовы из `operand.rs`, `static_var.rs` | Верно |
| Совместимые алиасы объединяются, «only when their extent, layout and mask agree» | `Descriptor::compatible` сравнивает `allocation`, `mask`, `layout`; `mask` и `layout` всегда вычисляются из `allocation` | Верно формально; два из трёх сравнений избыточны (см. 6.3) |
| «reject incompatible descriptors» | `tcx.dcx().fatal(…)` | «Reject» — это аварийная остановка компиляции пользователя |
| Маски применяются после reset | `finalize_immutable_allocations`: после кодогенерации в тело `initialize_memory_initialization_state` перед каждым `return` вставляется по условному присваиванию на аллокацию; состояние ищется по `fn_marker`, поля — по именам | Верно, но **сам механизм в тексте не назван**. Это главное проектное решение PR, о нём мейнтейнер спросит первым |
| Reset на входе automatic harness | `ptr_uninit/mod.rs:81–88`, 7 строк в `is_harness` | Код верный. Тестами не подтверждено, что после него чтение uninit в automatic harness обнаруживается (см. 3.3) |
| Документация описывает поддерживаемые аллокации | `rust-feature-support.md:181–189`, `contracts.md:73–76` | Есть, но написана внутренним языком, а абзац в `contracts.md` вставлен посреди примера с `gcd` (см. 6.3) |

Чего в тексте нет, а в диффе есть:

- **`gcx.handle_quantifiers()` перенесён** выше снимков `pretty_name_map` / `type_map` / vtable (`compiler_interface.rs:196–204`). Это меняет порядок для всех запусков, не только с `-Z uninit-checks`. Причина понятна (маски финализируются после всей кодогенерации), но о переносе чужого прохода надо сказать самим.
- Граф points-to получает узел `MemLoc::Anonymous`, константы становятся целями delayed-UB анализа (`points_to_graph.rs`, `initial_target_visitor.rs`).
- Появляются хелперы для `MaybeUninit` (`maybe_uninit_storage`, `PointeeInfo::for_storage`), при том что текст отдельно заверяет: PR не добавляет «general `MaybeUninit` … support».

Тесты PR-02:

- Шесть тестов `immutable-descriptor-coalescing` и шесть `autoharness_entry_reset_*` — все ожидают `VERIFICATION:- SUCCESSFUL`. По коду они проходят и на `main`: чтения через ссылки не проверяются, а при образовании сырого указателя из ссылки память помечается инициализированной. Записи о baseline-прогоне этих тестов в `slice-02` я не нашёл.
- То есть тесты сторожат не пользу PR, а отказы, которые вносит сам PR: `fatal` при конфликте дескрипторов и `fatal` «reset is absent from this model».
- Этот второй `fatal` реально сработал: исходный PR-02 ронял компилятор на любом `kani autoharness -Z uninit-checks` с подходящей константой. Выборочный прогон его не увидел, потому что из `script-based-pre` в нём было 3 теста.

### 3.3. Убранная фикстура `autoharness_entry_reset_uninit_read`

Это самое слабое место подачи, и объяснение в записях не выдерживает проверки.

Что записано (`RESULT-U03.md`, `TASK-CH8-PR02-FINAL-W11.md`): фикстура дала «verification SUCCESS (exit 0) вместо ожидаемого UB», причина — «чтение padding-байта `#[repr(C)]` struct Kani не считает uninit», фикстура дефектна, удалить; обнаружение uninit-read «покрыто существующим uninit-набором».

Что этому противоречит:

1. Upstream-тест `tests/expected/uninit/access-padding-uninit/access-padding-uninit.rs` делает то же самое (локальная `#[repr(C)]` структура, `addr_of!`, чтение байта padding) и ожидает FAILED.
2. Ваш тест `tests/expected/uninit/ordinary-slots/padding.rs` на голове 4 читает байт 1 структуры `{ u8, u32 }` через `.cast::<u8>().add(1).read()` и ожидает FAILED — и принят как прошедший.
3. Запись неоднозначна. `run.sh` фикстуры заканчивается `[[ "$status" == 1 ]]`: скрипт возвращает 0 **только если Kani вернул 1**, то есть верификация провалилась, как и ожидалось. Если «exit 0» в записи — код скрипта, он противоречит слову «SUCCESS». Если это код самого Kani — см. версию (б).
4. `expected` фикстуры требует в описании проверки тип ``u8`` («…uninitialized pointer of type …»). На этой голове для `MemoryInitOp::Check` в сообщение подставляется тип указателя (`check_uninit/mod.rs:334–346`); чтение происходит внутри `core::ptr::read::<u8>`, значит в тексте был бы тип `*const u8`. Строка не совпала бы, даже если Kani всё обнаружил.

Две версии:

- **(а) Kani чтение обнаружил**, тест упал на сравнении с `expected` из-за типа в сообщении. Тогда исправление работает, а удалён единственный тест, который это доказывает, — и, по коду, единственный, который на `main` даёт SUCCESS, а после исправления FAILED.
- **(б) Kani действительно вернул SUCCESS.** Тогда reset в automatic harness не делает обнаружение рабочим, и исправление не делает того, что заявлено.

Различить их можно без нового прогона: открыть сохранённый stdout этой фикстуры в run 43783429976 и посмотреть, есть ли там `VERIFICATION:- FAILED` и какой тип в описании проверки.

В любом случае:

- Фраза «uninitialized-read detection remains covered by the existing uninitialized-memory suite» неверна по существу: существующий набор использует `#[kani::proof]`, а меняется вход automatic harness.
- Абзац про убранную фикстуру в upstream публиковать нельзя ни в одном из трёх вариантов брифа. Его надо сделать ненужным.

Попутно, по коду: на `main` `is_harness` распознаёт только атрибуты `proof` и `proof_for_contract`, у `automatic_harness` их нет. Состояние остаётся в статическом инициализаторе (`tracked_object_id: 0, tracked_offset: 0`), ни один байт не отслеживается. Если это так, `kani autoharness -Z uninit-checks` на `main` не сообщает ни об одном чтении uninit, и семистрочное исправление `is_harness` — самостоятельный, ценный и легко проверяемый PR, никак не связанный с масками.

### 3.4. Что это значит для раздела Testing

- Прогоны по отдельным головам — выборочные (≈300–460 тестов), полный `scripts/kani-regression.sh` шёл только на финальном дереве. CI upstream на каждом PR гоняет всё. Выборка уже пропустила регрессию в PR-02. До открытия любого PR — полный прогон стандартных workflow на его точной голове.
- Ссылка в тексте должна вести на прогон стандартных workflow на ветке PR, как в вашем #5153. Сейчас ссылки ведут на самодельный overlay в ветках `uninit-ci/c2-slices-0N-w15` с коммитами «CI only: qualify C2 analysis slice against exact source head». Мейнтейнер по такой странице ничего не поймёт, зато увидит внутреннюю кухню.

## 4. Нарезка

| Срез | Исходники +/− | Новые тест-файлы | Тест «до падает, после проходит» | Самостоятелен на `main` |
|---|---|---|---|---|
| #5172 (открыт) | +133 / −73 | 44 | да (в описании: шесть) | да |
| PR-01 анализ | +520 / −63 | 0 | нет | рекурсия — да; остальное — нужен тест |
| PR-02 маски + reset | +865 / −33 | 36 | нет (все SUCCESS) | reset — да; маски — без эффекта |
| PR-03 `raw_eq` + layout | +70 / −13 | 2 | один позитивный | смещения layout — да |
| PR-04 хранение и передачи | +1 125 / −308 | 190 | да | нет, это ядро |
| PR-05 замыкания | +28 / −1 | 94 | — | нет |
| PR-06 тесты и доки | 0 | 23 | — | — |
| PR-07 изоляция delayed-тел | +243 / −5 | 0 (только unit) | нет | да |

Наблюдения:

1. **Срезы вырезаны из готового дерева по принадлежности хунков**, а не написаны как изменения. Это видно по PR-01 (остаток «B1 → финальное дерево» для файлов #5172), по PR-05 (28 строк кода и 94 файла тестов к предыдущим срезам), по PR-06 (только тесты и документация). Каждый срез компилируется, но не каждый что-то доказывает сам.
2. **Тесты и документация отстают от кода на 3–5 PR.** Если принять PR-01…04 и остановиться, функциональность останется без документации и без части тестов. Тесты должны ехать с тем изменением, которое проверяют.
3. **Порядок определяется зависимостями вашего дерева, а не независимостью исправлений.** PR-07 стоит последним, хотя чинит дефект `main`: `delayed_ub/mod.rs:143` на базе пишет инструментированное тело в кеш transformer, и, по вашему же описанию PR-07, следующий harness получает чужие проверки. От `MaybeUninit` это не зависит.
4. **В PR-03 два несвязанных изменения.** Смещения для вложенных `Pat` и enum — исправление существующего кода: на базе `ty_layout.rs:337` считает data bytes pattern-типа от нуля, а не от `current_offset`. По коду это даёт неверную маску для любой структуры с `NonNull` не в нулевом смещении, без всякого `MaybeUninit`. Проверка `raw_eq` — новая функциональность, первый потребитель масок из PR-02.
5. **Объём тестов.** 321 новый тест-файл (160 кейсов, около 230 harness) на 2 850 строк кода, в том числе 36 файлов `closure-zst`. 70 файлов с `--cbmc-args --object-bits 12`, которого в этом каталоге upstream нет нигде. Каждый expected-тест — запуск Kani и CBMC в CI у всех навсегда. Мейнтейнер считает это не покрытием, а временем.

Рекомендуемая схема.

**Волна 0 — независимые исправления на `main`, по одному, без стека:**

| PR | Откуда | Размер | Тест |
|---|---|---|---|
| F1. Reset состояния в automatic harness | fix-коммит PR-02 | 7 строк | один каталог: чтение padding — FAILED, после записи — SUCCESS |
| F2. Смещения layout для вложенных pattern-типов и enum | половина PR-03 | ≈15 строк | структура с `NonNull` не в нулевом смещении, без `MaybeUninit` |
| F3. Рекурсия в delayed-UB анализе: unsupported вместо падения | часть PR-01 | ≈200 строк кода и 170 строк unit-тестов | рекурсивная функция + приведение указателя |
| F4. Delayed-инструментация не переживает harness | PR-07 | 243 строки | два harness в одном файле, результат зависит от порядка |

Для F2–F4 сначала один прогон на `main`, подтверждающий дефект. Что не подтвердилось — остаётся в стеке.

**Волна 1 — стек, после реакции на дизайн в #5151:**

1. Маски констант вместе с проверкой `raw_eq` (PR-02 без reset + вторая половина PR-03). Тогда у PR есть видимый результат: в таблице intrinsics сейчас написано, что `raw_eq` не обнаруживает uninit.
2. Тела контрактов и параметры в анализе (остаток PR-01) — с тестами, либо внутри п. 3.
3. Хранение и передача `MaybeUninit` (PR-04) со своей документацией и репродьюсером #5151 среди тестов.
4. Замыкания (PR-05), тесты из PR-06 — по своим PR.

Цена: срезы придётся пересобрать и перепрогнать. PR-03…07 всё равно ждут пересборки поверх нового PR-02, так что это одна пересборка, а не две.

Если пересборку сейчас не делать, минимум такой: F1 отдельным PR; PR-01 — только с тестами и без правок к #5172; PR-02 — после п. 3.3, с прямой фразой «сам по себе результатов не меняет».

## 5. Порядок и темп (вопрос 1)

- **Design note до PR.** `CONTRIBUTING.md` Kani прямо просит обсудить значительную работу в issue заранее. Короткий комментарий в #5151, строка-указатель в #3300.
- **Ждать реакции на #5172 перед стеком на нём — да.** PR из форка нельзя нацелить на ветку форка: PR-01 против `main` покажет 51 файл, PR-02 — около 100, одни и те же изменения #5172 в трёх местах, и любая правка #5172 по ревью потянет rebase обоих. Независимым PR волны 0 ждать не нужно.
- **Draft или ready.** Стековый PR с неслитым родителем — только Draft: он не рассылает запросы ревью. Ready — независимые PR на `main` и стековый после слияния родителя. Но Draft без тестов не лучше ready без тестов.
- **Темп.** Не больше одного нового объекта в Kani за рабочий день и не больше двух открытых PR без ревью одновременно. Пинговать #5172 раньше чем через неделю не стоит.

Последовательность:

| Когда | Что | Условие |
|---|---|---|
| Сегодня или завтра утром | Ответ на ревью в #752 (текст D) | Сверить цифры длин с описанием PR |
| Завтра | Fixup в #5172: `checked_body`, комментарии | — |
| Завтра–послезавтра | Комментарий в #5151 (текст C) + строка в #3300 | Прогнан репродьюсер #5151; желательно счёт по 77 harness |
| После разбора 3.3 | PR F1 (reset) | Negative-тест восстановлен, полный CI на голове |
| После первой реакции на #5172 или #5151 | Дальше по волне 0, затем стек | — |
| Не сейчас | Сообщение в #56, раздел Limitations в #752 | См. 7.6, 7.7 |

Ответ на ревью не стоит держать до разбора #762: он должен быть верен независимо от конкурента, а задержка ответа на запрошенное организатором ревью стоит дороже.

## 6. Слоп в коде

### 6.1. Измеримые маркеры

| | Строк комментариев в добавленном коде | Из них с отрицанием или запретом (`never`, `not`, `no`, `only`, `without`, `rather than`) |
|---|---|---|
| Upstream, `check_uninit/` и `points_to/` на базе | 553 | ≈10 % |
| #5172 | 21 | 48 % |
| PR-01 | 46 | 54 % |
| PR-02 | 52 | 44 % |
| PR-04 | 111 | 35 % |

Плотность комментариев нормальная (6–9 % строк при 12–19 % в upstream). Ненормален их жанр: они не объясняют, что делает код и зачем, а заверяют, чего он не делает. Это ответы на замечания внутреннего аудита, оставленные в исходнике. Три подвида:

- **Комментарии относительно диффа.** «Diagnostic provenance of the existing immutable override selection. This does not select an additional body or introduce an analysis fallback»; «Other bodies retain the existing analysis path»; «preserve the existing terminating walk». После слияния слово «existing» ничего не значит.
- **Запреты капсом.** «Never export an unfinished summary»; «Shared only by … ONE entry root»; «Insert … AFTER ordinary instrumentation»; в PR-04 — «Snapshot ALL argument witnesses before clearing ANY source».
- **Формула «это X, а не Y».** «This is an active stack, not a visited set or an input-independent summary cache»; «An alias edge is not an exact byte offset»; «this is not a runtime object number».

Правило для агентов: комментарий описывает код в том виде, в каком он лежит в файле, для человека, который диффа не видел. Если комментарий отвечает на вопрос «а не делает ли это ещё чего-то?» — его место в описании PR или нигде.

Словарь, которого нет в upstream (вхождения в исходниках: база → финальное дерево): `seed` 0 → 27, `witness` 0 → 13, `MU` 0 → 1. В upstream то же называется `analysis targets`, `memory initialization state`, `shadow memory`, `unused closures`.

### 6.2. PR-01

1. `points_to_analysis.rs:524` — «…does not grant them **A3** shadow transfers». Внутренняя метка стадии в doc-комментарии публичной функции. В #5172 на этом месте нормальная фраза; PR-01 её ухудшает.
2. `instrumentation_visitor.rs:50` — «Union/MU storage».
3. `instrumentation_visitor.rs:105–107` — заменён поясняющий комментарий upstream (см. 3.1).
4. Диагностика цикла: `root [provenance=source] -> frame 1: A [provenance=source] [call at f.rs:10] -> repeated: …`, «repeats active frame 1». Пользователь не знает, что такое provenance и active frame. Соседние сообщения (в том числе ваши из #5172) устроены иначе: «Kani does not support memory initialization checks across {kind}. For more information about planned support, see …/3300». Привести к этому виду: «…across recursive calls (a -> b -> a, at f.rs:10)». Происхождение тела показывать только когда оно не `Source`.
5. Unit-тесты `active_call_tests`. Настоящие: self-cycle, mutual-cycle, caller location, diamond, усечение диагностики. Четыре названы по свойствам продакшн-кода, которых не касаются:
   - `discarded_override_has_no_source_body_edges` — два `enter` и два `exit` на строковых ключах; ни override, ни тел, ни рёбер в тесте нет;
   - `exact_instance_and_body_selection_are_part_of_identity` — проверяет `#[derive(PartialEq)]` тестовой структуры, а не `AnalysisKey`;
   - `independent_roots_in_both_orders_do_not_share_errors` — в каждой итерации создаёт новый `ActiveCalls`; независимость двух свежих объектов гарантирована языком;
   - `diagnostic_uses_display_without_exposing_internal_identity` — у `K` нет ограничения `Debug`, использовать его нельзя по типам. Там же `assert!(!error.reason.contains("DefId"))` на ключе `"root"`.
   Удалить или переименовать по тому, что реально проверяется. В тексте PR не считать их поштучно.
6. Замыкание «discarded» определяется по форме тела: один блок, ноль операторов, `Unreachable`. Работает, но мейнтейнер спросит, почему не взять `unused_closures` у прохода контрактов.
7. Правки к #5172 (см. 3.1) — вынести.
8. В самом #5172 тот же жанр уже опубликован: «legacy union slot pairing», «Conservative admission guard for generated ABIs, not an expansion of the shadow model», «unproved generated ABI», «delayed-UB seeds». Раз всё равно делать fixup — вычитать и их.

### 6.3. PR-02

1. **`immutable_allocations.rs`: 18 вызовов `fatal`, три `assert`, один `panic!` на 436 строк рабочего кода.** Маски только добавляют точность: без них константа считается неинициализированной, как сейчас, — это консервативно и безопасно. Значит почти любую «невозможную» ситуацию можно обработать пропуском маски с `debug!`, а не остановкой компиляции пользователя с текстом вроде `immutable masks: noncanonical layout/lifetime for …`. Один из этих `fatal` уже сработал на реальном сценарии.
2. **Мёртвое поле.** `Descriptor.layout` всегда равно `[(0, len)]` (единственный конструктор, строка 52; в финальном дереве файл не меняется). Его сравнивают в `compatible` (68), проверяют на 348 с `fatal`, печатают в сообщении. `mask` тоже однозначно выводится из `allocation.bytes`, поэтому сравнение масок на 67 и `assert_eq!` на 252 — тавтологии. Unit-тест `incompatible_storage_never_overwrites_or_combines_qualification` вручную портит эти поля, чтобы проверить состояния, недостижимые в рабочем коде.
3. Строка 261 — `fatal(format!(…))` в одну строку длиной 533 символа с тринадцатью подстановками.
4. Unit-тест `empty_mask_has_no_seed_index_or_object_query` проверяет только, что у пустого дескриптора пустая маска; пропуск пустых масок живёт в `finalize_immutable_allocations` и не тестируется.
5. **Документация для пользователей.**
   - `contracts.md:73–76`: абзац «Whole immutable masks require the qualification described in…» вставлен между примечанием про стаббинг и «There is far more to learn about contracts». Читатель главы про контракты не знает ни одного слова из этой фразы.
   - `rust-feature-support.md:181–189`: «Qualified whole immutable promoted constants and named statics start with their exact byte masks… This whole-storage qualification is narrow… Eligible aliases and independently supported static paths can still succeed». Нужен перевод на язык пользователя (вариант ниже).
6. Имена: каталог `immutable-descriptor-coalescing`; в тестах «the whole-object origin supplies qualification», «the typed return admits a seed».
7. Шесть каталогов по четыре файла на шесть функций в `script-based-pre`. `kani autoharness` проверяет все функции файла за один запуск: один каталог, один `main.rs`, один `expected` — четыре файла вместо 24 и один запуск вместо шести.
8. Перенос `handle_quantifiers()` — не слоп, но не объявлен (см. 3.2).

Вариант абзаца для `rust-feature-support.md` (абзац из `contracts.md` убрать совсем):

```text
With `-Z uninit-checks`, constants and immutable statics start out with the
initialization state of their bytes: initialized bytes are initialized, and
padding or `MaybeUninit::uninit()` bytes are not. This applies to constants
whose type is a primitive, `str`, an array or slice of primitives, or
`MaybeUninit` storage, and that contain no pointers. Other constants are not
tracked this way, so a check that reads them may report a spurious failure.
```

### 6.4. Системно в PR-03…07 (исправить при пересборке)

- **PR-06 коммитит в пользовательскую документацию оговорку из описания PR:** в `docs/src/rust-feature-support.md` последней строкой раздела стоит «This change does not make core::slice::sort::shared::smallsort verifiable with -Z uninit-checks.» «This change» в документации продукта.
- Весь раздел Uninitialized memory и новый раздел Limitations в `contracts.md` в финальном дереве написаны тем же языком: «Kani's typed marker-dispatched backend hooks do not support by-value shadow argument or return transfers», «Observed conservative failures at these boundaries do not qualify shadow transfer in those modes», «its presence alone does not establish successful checking».
- Каталоги тестов с внутренними именами: `part1-composition`, `part1-edges` (53 файла), `root-composition`, `transfer-qualification`, `marker-hook-calls`, `private-transfer-frame`.
- `--cbmc-args --object-bits 12` в 70 тестах без объяснения.
- Комментарии PR-04 в `mem_init.rs` и `uninit_visitor.rs`: «demonic choice», «witness», «preserve mask», «protocol», «admission».
- Гигиена форка: около 230 веток, в основном `uninit-ci/*`, коммиты `[skip ci]`, в одной CI-ветке коммит с автором `root@<hostname>.vm`. На PR это не влияет, но любая ссылка из текста на прогон форка ведёт туда.

## 7. Тексты

### 7.1. Общие маркеры

| Маркер | Примеры из черновиков | Что делать |
|---|---|---|
| Оговорка о том, чего прогон не доказывает | «This is regression/unit evidence only»; «They … do not establish standalone PR-01 behavior»; «These are fork qualification results, not organizer integration evidence»; «the complete suite is not claimed to have passed on it»; «no organizer integration or independent proof credit» | Удалить. Мейнтейнер не знает, что такое organizer integration, и не подозревал вас в обратном |
| Отрицательный scope | «This change does not add general `MaybeUninit`, indirect-call, or recursion support»; «They … grant no permission to write memory or access an allocation»; «No new alias/provenance model or #3300 completion, permissions, general validity, all-T/N, panic/unwind or sorting proof is claimed» | Удалить. `Refs #3300` уже говорит, что issue не закрыт. Оставлять только ограничение, о которое пользователь споткнётся |
| Свой словарь без определений | selected bodies, discarded closures, active call cycles, argument slots, referents, seed, hole, witness, origin, descriptor, qualification, root, journal, controls | Слова upstream: contract pass, unused closures, recursion, parameters, analysis targets, memory initialization state, padding / uninitialized bytes |
| Слова процесса | qualification, candidate, retained, deferred, cumulative head 4, historical (пять раз в одной таблице), source head, receipt, credit | Удалить вместе с предложением |
| Шум идентификаторов | полные SHA головы и родителя, пять номеров прогонов, «9 existing tests remained ignored», «66 compiler unit tests», «byte-identical … including file modes» | Голову показывает GitHub. Одна ссылка на один прогон |
| Телеграф и слэши | «Six cache/two scope units and 11 invocations/18 mixed-versus-isolated comparisons»; «unwind34/34/16/8»; «object-bits12»; «body/origin/isolation controls» | Полные предложения или ничего |
| Механизм без проблемы | «compiler-produced immutable allocations need their initial byte state represented in the shadow model» | Сначала — что видел пользователь, потом — как устроено |
| «Also» | «This change also initializes…»; «It also recognizes…» | Признак двух PR в одном. Либо разделить, либо перечислить на равных |

Проверка для агентов перед сдачей внешнего текста:

1. Первое предложение описывает поведение Kani, которое можно воспроизвести командой?
2. Есть ли предложение, начинающееся с «This does not», «These are not», «No … is claimed»? Удалить и перечитать: стал ли текст хуже?
3. Каждое существительное-термин есть в документации или исходниках upstream на `main`?
4. Сколько в тексте хешей и номеров прогонов? Больше одной ссылки — лишнее.
5. Сказано ли, что падает на `main` и проходит здесь?

### 7.2. Текст A (PR-01)

| Было | Стало |
|---|---|
| Title: Analyze selected contract bodies and detect active call cycles | Delayed UB analysis: use contract-generated bodies and report recursion as unsupported |
| «…delayed analysis must use the MIR bodies selected for contract registration and discarded closures, and report call cycles without using an incomplete points-to graph» | Три пункта: что было на `main`, что стало (см. раздел 8) |
| «report cycles with short diagnostics» | «the harness fails an "unsupported" check that names the cycle» |
| «Keep the existing call resolution, visit each call's operands once, and retain the checks collected for that call» | Удалить (см. 3.1) |
| «ordinary scalar and reference argument slots» | «sized, non-union parameters» |
| «On exact source head `d82752c8…` (parent `6fe484b3…`), formatting, build, Clippy, 9 ActiveCalls unit tests and 302 regression tests passed; 9 existing tests remained ignored» | «The regression suite passed in [fork CI](…)» — после полного прогона |
| Весь второй абзац Testing про cumulative head 4 и 5 | Удалить; заменить списком собственных тестов PR |
| Раздел Limitations | Удалить. Факт «рекурсия не анализируется, а отклоняется» уже в первом пункте |

Выкинуть: раздел Limitations, оба абзаца Testing в нынешнем виде, хеши. Целевая длина — до 1 900 знаков вместе с заголовком и шаблонными строками (сейчас 2 667).

### 7.3. Текст B (PR-02)

| Было | Стало |
|---|---|
| Title: Track initialization masks for whole immutable allocations | Track initialization of immutable constant allocations |
| «Otherwise, a legal comparison with an initialized constant can report an uninitialized read» | «No existing check changes its result. The first user is #…, where `raw_eq` starts checking its operands» |
| «Record anonymous allocation origins and bind them to emitted immutable symbols» | Пункт «How» с названным механизмом |
| «Combine compatible aliases only when their extent, layout and mask agree, keeping initialized zero bytes distinct from holes; reject incompatible descriptors» | Не нужно в описании: это внутренняя консистентность, а после п. 6.3 её станет меньше |
| «skipping empty-mask queries» | Удалить |
| «Qualification of the entry-reset fix reported formatting, build and Clippy success, 66 compiler unit tests passed, 56 expected uninitialized-memory tests passed (2 ignored), and 134 function-contract tests passed (4 ignored)» | Одна ссылка на прогон на финальной голове |
| «All six retained entry-reset regressions passed: a seeded return, a seeded function with an argument, …» | Уезжает в отдельный PR (F1) |
| Третий абзац Testing (54 passed / 1 failed, убранная фикстура, «byte-identical», «not rerun») | Удалить; причина должна исчезнуть (см. 3.3) |
| «They describe initialization metadata only and grant no permission to write memory or access an allocation» | Удалить |
| «This does not resolve all of #3300 or add general `MaybeUninit`, indirect-call, or recursion support» | Удалить |

Добавить то, чего нет: механизм (патч тела reset-функции), перенос `handle_quantifiers()`, узел графа. Целевая длина — около 2 000 знаков (сейчас 3 823).

### 7.4. Testing в PR (вопрос 3)

- Один прогон, одна ссылка: стандартные workflow на ветке PR, на её текущей голове. В вашем принятом #5153 это одна фраза с четырьмя платформами — так и оставить.
- Главная строка Testing — не счётчик, а пара «тест X на `main` даёт …, здесь проходит». В #5172 она есть, в A и B её нет.
- Различие «fork vs organizer» убрать целиком. Для мейнтейнера Kani организаторов не существует.
- Зависимые доказательства с более поздних голов: либо ни слова, либо одно предложение с одной ссылкой.
- Про абзац PR-02: ни один из трёх вариантов брифа. Сначала прочитать сохранённый вывод фикстуры (бесплатно). При версии (а) — поправить `expected` (взять префикс без типа, как в ваших же `ordinary-slots`), вернуть тест и прогнать CI на финальной голове; этот прогон нужен в любом случае, потому что `05da1a7a8c` не запускался ни разу и не запушен. При версии (б) reset не подавать как исправление, пока не найдена причина.

### 7.5. Design note (вопрос 4)

- Как комментарий в #5151, а не в #3300, и не отдельным issue: сегодня от аккаунта уже ушло два issue.
- Новая структура: что отслеживается (4 пункта) → результаты (его репродьюсер, его 77 harness, полная регрессия) → чего нет (включая `array::IntoIter`) → где код и в каком порядке PR → три вопроса. Целевой объём — около 2 200 знаков вместо 7 975.
- Выкинуть целиком: таблицу SHA, «historical», раздел Evaluation and evidence, блок SmallSort-replay с unwind/object-bits, раздел «Independent sorting contracts and integration», заголовок «RFC draft».
- Код показывать одной compare-ссылкой на ветку с нейтральным именем. Сейчас дерево, на котором шла полная регрессия, доступно только как `freeze/kani-3300-c2` и как родитель CI-ветки.
- #5179 и #5181 — в списке «Not covered» простыми ссылками. #3762 к uninit не относится; упоминать его в note не нужно, он уместен в ответе на ревью #752.
- Вопросы должны быть такими, на которые можно ответить одной фразой. «Is this model and review decomposition acceptable?» и «Which body/origin/isolation controls are missing?» — не такие. Первый реальный вопрос — допустимо ли патчить сгенерированное тело `initialize_memory_initialization_state`.

### 7.6. Сообщение организаторам (вопрос 5)

- **Куда.** В #752, ответом на ревью. Утреннее решение «в #56, а не в #752» принималось в предположении, что на #752 ничего нет. В #56 сейчас не писать; если за неделю вопрос о длинах останется без ответа — короткая реплика там со ссылкой (текст D-2).
- **Одно сообщение**, три коротких части: замечание 1, замечание 2 с вопросом, версия Kani. Объём — до 2 300 знаков (в черновике 2 952 при меньшем содержании).
- **Как спросить о длинах, не сужая условие.** Не просить подтвердить своё прочтение, а разложить факты и спросить, какое из двух прочтений имеется в виду. Факты из исходника: `small_sort_network` и нестабильный general аварийно завершаются выше 32; fallback (сортировка вставками), стабильный general при достаточном scratch и `insertion_sort_shift_left` принимают любую длину; вызывающий код передаёт не больше `small_sort_threshold()`. Сейчас в D сказано «every valid caller length» — это уже вывод, выданный за прочтение.
- Нынешнее состояние #752 назвать прямо: сортировка доказана до 9 / 6 / 13, а не до 16 / 32. Фраза «we read item 2 as checking … up to 16 … up to 32» в черновике читается так, будто это уже сделано.

| Было | Стало |
|---|---|
| «we read item 2 as checking actual trait-method contracts for sortedness and multiset preservation over every valid caller length…» | Два предложения: что проверено сейчас; до чего расширяем |
| «Our proposed coverage strategy uses symbolic lengths and accounts for all six implementation bodies, including specialization and forwarding routes. Those are our coverage choices, not a claim that a particular harness count was prescribed» | Удалить |
| Вопрос 2 (route representatives, six-body accounting) | Удалить (см. 2.4) |
| Вопрос 3 (total time, worst-shard time, peak RSS, concurrency budget; «would need its own qualification») | Удалить. Времена уже есть в описании PR; если бюджет важен, организаторы скажут |
| «Could it be bumped to **clean upstream Kani `0aac16ef…`** … independently of the pending initialization series?» + абзац про nightly | «May we merge `main` and bump `tool_config/kani-version.toml` in this PR, or do you prefer the bump as a separate PR?» |
| «This requests adoption; neither the bump nor a separate safety step is reported as adopted» | Удалить |

### 7.7. Limitations для #752 (вопрос 6)

Не публиковать. Причины:

- В описании #752 уже есть Limitations: scope и write sets, trait-method contracts с номерами issue, длины, паники, классы UB, доверие к модели, ZST. Все четыре абзаца E повторяют эти пункты на языке, который комитет не поймёт: «qualified contract instances», «Verified-summary consumers», «N2 forwarding-wrapper proofs», «S1 source candidate», «N0..3 mechanism proofs are NOT_RUN», «proof credit».
- Новых фактов в E два, и оба — про эксперименты на других пинах, которые к поданному PR отношения не имеют.
- Ревью Copilot отдельно отметило список «Not covered» в `verify.rs`. Удлинять перечень ограничений в ответ на замечание «не покрыто» — худший ход.

Если хочется сохранить единственную новую мысль E, добавьте одно предложение в существующий пункт Scope:

```text
The `bidirectional_merge` contract used through `stub_verified` bounds what may be written; it does not state that the destination is initialized afterwards.
```

Описание #752 стоит обновить позже и по существу: когда сдвинется пин и появятся контракты на trait-методах, когда появится шаг с `-Z uninit-checks`.

### 7.8. Общий голос (вопрос 7)

- Опубликованные #5179 и #5181 хороши: проблема одной фразой, репродьюсер, команда, версии, ожидаемое и фактическое, контрольные варианты, место в коде. Описание #5172 по содержанию такое же, с фразой про шесть тестов, падающих на `main`. Принятый #5153 — лучший образец: два абзаца, короткий Testing со ссылкой на один прогон, `Resolves`.
- Новые A, B и особенно C написаны другим голосом — голосом журнала приёмки. Разрыв заметен: issue пишет человек, нашедший баг, а PR — отдел контроля качества.
- Строка раскрытия: в #5153 «prepared with AI assistance», в #752, #5179, #5181 — «prepared with the help of AI assistants». Оставить вторую.
- В #5153 порядок концовки: `Resolves` → раскрытие → лицензия; в черновиках — лицензия → раскрытие. Мелочь; выбрать один.
- Что поправить в опубликованном: fixup в #5172 (`checked_body`, комментарии из 6.2 п. 8); ответ на ревью в #752.

## 8. Предлагаемые тексты

Пометки `<<…>>` — результат прогона или номер, которых у меня нет. Утверждения без пометок проверены по коду; цифры в тексте D сверить с описанием #752.

### Текст A — PR-01

Для головы после доработок: добавлены end-to-end тесты, правки к #5172 перенесены в #5172, в диагностике и комментариях исправлено перечисленное в 6.2.

````text
Title: Delayed UB analysis: use contract-generated bodies and report recursion as unsupported

Refs #3300

Depends on #5172. Until it merges, this PR's diff also shows that commit; only the last commit is new.

The points-to analysis behind delayed UB instrumentation (`-Z uninit-checks`) gets three fixes.

- **Recursion.** The analysis descends into every callee and has no recursion guard, so a recursive function reachable from a harness with a delayed UB target <<what happens on main, e.g. "overflows the compiler's stack">>. The analysis now tracks the chain of calls it is inside. When a call repeats, the harness fails an "unsupported" check that names the cycle; other harnesses are unaffected.
- **Function contracts.** The analysis read source MIR, while codegen uses the bodies produced by the contract pass: `kani_register_contract` becomes a call to the selected closure, and unused contract closures become `unreachable`. The analysis now uses those bodies, so it follows aliasing through the contract closure and no longer walks the source bodies of unused closures. <<visible effect on main, one clause>>
- **Parameters.** A parameter has no assignment inside the callee, so a tracked parameter was never marked initialized<<, and reading it reported …>>. Sized, non-union parameters are now marked initialized on entry: the parameter itself, not the memory behind a pointer or reference parameter.

### Testing

- <<new tests under tests/expected/uninit/…: which fail on main and pass here>>
- Unit tests for the call-chain bookkeeping and the diagnostic text.
- The regression suite passed in [fork CI](<<run of the stock workflows on this head>>).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

Если тесты всё же не добавляются, раздел Testing сводится к одной фразе, а PR открывается только как Draft:

````text
This PR adds unit tests only. The end-to-end tests for these fixes pass `MaybeUninit` values by value, which Kani rejects until later changes; they pass on the branch that contains those changes ([run](https://github.com/Tiramisu-Cake/kani/actions/runs/43710024495)).
````

### Текст B — PR-02 (маски, без reset)

````text
Title: Track initialization of immutable constant allocations

Refs #3300

Depends on #5172 and #<<PR-01>>. Until they merge, this PR's diff also shows their commits; only the last commit is new.

With `-Z uninit-checks`, a constant is marked initialized where a raw pointer to it is formed, using the layout of its type. That cannot describe a constant that itself contains uninitialized bytes (padding, `MaybeUninit::uninit()`), and it does not apply when a check reads a constant through a reference. This PR gives each eligible immutable allocation its exact per-byte state from the start of the harness.

No existing check changes its result. The first user is #<<next PR>>, where `raw_eq` starts checking its operands; without this PR, `x == [1, 2, 3, 4]` would report the constant as uninitialized.

- **Which allocations.** Whole, immutable allocations without relocations whose type is a primitive, `str`, an array or slice of primitives, or `MaybeUninit` storage. Anything else behaves as before.
- **How.** After codegen, each such allocation adds a guarded assignment before every `return` in the generated body of `initialize_memory_initialization_state`: if the tracked byte lies in that allocation, its state comes from the allocation's mask. Feedback on this mechanism is especially welcome.
- **Points-to graph.** Anonymous allocations become nodes, so the delayed UB analysis can treat a constant as a target.
- **Ordering.** `handle_quantifiers()` now runs before the symbol-table snapshots, because the masks are finalized after all codegen.
- **Docs.** `rust-feature-support.md` lists the constants that are covered.

### Testing

- <<tests and what they show; say plainly if they also pass on main>>
- Unit tests for the allocation registry.
- The regression suite passed in [fork CI](<<run of the stock workflows on this head>>).

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

Первую фразу сверить с `uninit_visitor.rs`: обработка `Rvalue::AddressOf` и констант-указателей на static. Если маски объединяются с проверкой `raw_eq`, второй абзац заменяется на описание новой проверки, а в Testing появляется тест, падающий на `main`: `raw_eq` по значению с padding.

### Текст B-reset — отдельный PR (F1)

````text
Title: Reset memory-initialization state in automatic harnesses

`-Z uninit-checks` resets its tracking state at the start of `#[kani::proof]` and `#[kani::proof_for_contract]` harnesses, but not in harnesses generated by `kani autoharness`: `is_harness` looks only for those two attributes. In an automatic harness the state keeps its static initializer (object 0, offset 0)<<, so no byte is tracked and uninitialized reads are not reported — confirm with the test below>>.

`is_harness` now also recognises the automatic-harness intrinsic.

### Testing

`tests/script-based-pre/<<name>>` runs `kani autoharness -Z uninit-checks` on two functions. One reads a padding byte through a raw pointer: <<it verifies on main and fails with "Reading from an uninitialized pointer" here>>. The other writes the byte first and verifies.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
````

### Текст C — комментарий в kani#5151

````text
We have a prototype that makes this pattern checkable, built on top of #5172, and would like your view on the approach and on how to split it before opening more PRs.

**What it tracks.** With `-Z uninit-checks`, `MaybeUninit<T>`, `[MaybeUninit<T>; N]`, `[MaybeUninit<T>]` and `MaybeUninit<[T; N]>` get per-byte state instead of the "union as a field" error:

- typed copies and moves carry the state of `T`'s data bytes and drop padding; raw copies carry every byte;
- by-value arguments and return values carry their state across direct calls;
- constants start from the initialization mask of their allocation;
- `raw_eq` checks every byte of both operands.

**Results.** <<the reproducer from this issue on the prototype: result>>. <<of the 77 harnesses counted above, N now run to completion>>. The full regression suite passes on Linux x86_64, Linux Arm and macOS ([run](https://github.com/Tiramisu-Cake/kani/actions/runs/43665002636)).

**Not covered.** `MaybeUninit` arrays held in a struct field (as in `array::IntoIter`), `stub_verified` and `kani::recursion`, loop contracts (#5179, #5181), and calls through function pointers or trait objects, which stay unsupported as in #5172.

**Code.** [Whole diff](<<compare link to a branch at the tested tree>>): about 2,900 added lines in the compiler and `kani_core`, the rest is tests. We would send it as small PRs, each with tests that fail on `main`:

1. independent fixes found on the way: automatic harnesses never reset the initialization state; layout offsets of nested pattern types and enums; recursion in the delayed UB analysis; delayed instrumentation leaking between harnesses;
2. initialization masks for constants, together with the `raw_eq` checks;
3. `MaybeUninit` storage and transfers;
4. closure environments.

**Questions.**

1. Constants get their state by patching the generated body of `initialize_memory_initialization_state` after codegen. Is that acceptable, or is there a hook you would prefer?
2. Call transfers add state to `kani_core::mem_init` <<one clause: what is added>>. Is that the right place for it?
3. Does the split above work for you?

*Disclosure: this comment was prepared with the help of AI assistants.*
````

Первая фраза верна, только если репродьюсер из issue на прототипе работает; иначе начать с того, что именно покрыто. Пункт 1 списка PR оставить только с теми исправлениями, которые подтвердились на `main`. Строка для #3300:

````text
A design sketch and prototype for `MaybeUninit` storage under `-Z uninit-checks` is in #5151 (<<comment link>>).
````

### Текст D — ответ на ревью в verify-rust-std#752

````text
On the two review findings:

**1. Uninitialized-memory, validity and immutable-byte checks.** Agreed; the Limitations section says the same. The blocker is tool support: `-Z uninit-checks` rejects the `MaybeUninit` scratch buffers these functions use (model-checking/kani#5151), and `-Z valid-value-checks` does not support `copy_nonoverlapping` (model-checking/kani#3762). We are working on the first one upstream; model-checking/kani#5172 is the first PR. On a development build of Kani with those changes, `bidirectional_merge`, `sort4_stable` and `swap_if_less` verify at small sizes with `-Z uninit-checks` enabled, and a control that leaves one source element unwritten is rejected ([run](https://github.com/Tiramisu-Cake/kani/actions/runs/43751703000)). Once the Kani changes land we plan to add this as a separate CI step. Kani does not yet check mutation of immutable bytes, so that remains a limitation of this PR.

**2. Slice lengths.** Agreed for the sorting contracts. Memory safety is checked up to length 32. Sortedness and multiset preservation are checked up to length 9 for the general and stable sorts and 6 for the insertion-sort fallback; the networks are checked for sortedness up to 13. We are extending the sorting proofs to every length that `core` passes to `small_sort` (`small_sort_threshold()`: 16 for the fallback, 32 otherwise).

One question about the challenge text. The network sort and the unstable general sort abort above 32 elements, so their valid lengths are bounded. The insertion-sort fallback, the stable general sort (given enough scratch) and `insertion_sort_shift_left` accept any length. Does "arbitrary valid length" mean every length they are called with in `core`, or every length they accept?

**Kani version.** This branch pins Kani `cd355b0`. Kani `0aac16e` contains the fixes for model-checking/kani#4908 and model-checking/kani#5116, which let us attach contracts to the trait methods directly. May we merge `main` and bump `tool_config/kani-version.toml` in this PR, or do you prefer the bump as a separate PR?

*Disclosure: this reply was prepared with the help of AI assistants.*
````

Перед публикацией сверить: цифры 32 / 9 / 6 / 13 — с разделом Highlights описания PR; формулировку про merge, sort4 и swap — с `RESULT.md` replay 43751703000 (тот прогон шёл с дополнительным патчем для `select_unpredictable` и с замыканиями-компараторами; если это существенно, добавить «and a model for `select_unpredictable`»).

### Текст D-2 — реплика в #56, только если вопрос о длинах останется без ответа

````text
A scope question for Challenge 8, related to the one above about lengths up to the thresholds: does "arbitrary valid length" cover every length the small sorts are called with in `core` (at most `small_sort_threshold()`), or every length the fallback, the stable general sort and `insertion_sort_shift_left` accept? Details are in <<link to the #752 reply>>.
````

### Текст E

Не публиковать (см. 7.7).

### Fixup в #5172 — комментарий к новому коммиту

````text
Pushed a small follow-up: `resolve_call` now checks for a body with `checked_body`, as the note in `kani_middle/mod.rs` asks, and a few comments are reworded. No behaviour change for the tests in this PR.
````

## 9. Чек-лист перед любой публикацией

- [ ] Открыть сохранённый stdout `autoharness_entry_reset_uninit_read` из run 43783429976; выбрать версию (а) или (б) из 3.3.
- [ ] Прогнать репродьюсер #5151 на прототипе; добавить его тестом.
- [ ] Посчитать, сколько из 77 harness мейнтейнера доходят до результата (желательно).
- [ ] Один прогон на `main` для каждого кандидата волны 0: рекурсия, смещения layout, утечка delayed-тел, padding под autoharness.
- [ ] Убрать `A3`, `MU`; вернуть комментарий upstream в `needs_set`; перенести правки к #5172 в #5172.
- [ ] Переписать абзацы документации из PR-02; убрать абзац из `contracts.md`.
- [ ] Для каждого открываемого PR: запушить финальную голову, полный прогон стандартных workflow на ней, одна ссылка в тексте.
- [ ] В каждом PR есть тест, который падает на `main`; если нет — в тексте прямо сказано, что результатов он не меняет.
- [ ] Сверить цифры текста D с описанием #752.
- [ ] Перед отправкой каждого текста — пять вопросов из 7.1.
