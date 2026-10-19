# Select / sort4 — текущее задание

## Задание

- **ID:** `select-maybeuninit-locator-2026-10-19-r3`; **статус:** READY.
- **Owner:** `select-sort4`.
- **Worktree:** `/root/verify-rust-std-select-night`; **branch:** `research/night-select-sort4-cloud-2026-10-09`, fork `Tiramisu-Cake/verify-rust-std`.
- **Режим:** адресное чтение существующего CI evidence и подготовка законченного узкого proposal. Предыдущая proof-сессия закрыта; её T0/продление/ledger не возобновлять. Новых Cloud Builds, Cloud-бюджета или изменения shape/admission этим обновлением не разрешается.

Ты стартуешь без контекста. Проверь branch/HEAD/dirty diff, сохрани чужие изменения. Прочитай `AGENTS.md`, [краткий guide v0.10](EVIDENCE-READER-GUIDE.md), [Literal Locators](EVIDENCE-LITERAL-LOCATORS.md), затем [последний checkpoint](cloud-build/sort4-caller-entry-native/A1-PARSER-CHECKPOINT-2026-10-19.md) и [MaybeUninit proposal](cloud-build/sort4-caller-entry-native/A1-PARSER-MAYBEUNINIT-PROPOSAL-2026-10-19.md). Всю историю не перечитывай. `--locate`/`--near-position` доступны; устаревшее ожидание deployment/отдельной авторизации на них отменено владельцем.

### Точная цель

**Установить actual serialized ADT name/kind/payload в существующем D2 evidence и закончить reviewable proposal проверки MaybeUninit.** Нужны проверенные file/SHA, scope и принадлежность полей одному record, сопоставление с pinned compiler/exporter и конкретный ответ, подтверждается ли предложенный structKind→unionKind fix. Получение координат отдельно не устанавливает parser-input binding, причинность или proof credit.

Последний docs checkpoint `492b3348`; исполненный proof=infra `d246ccbcf7e851f1b3c471daf4ed7aa770e199ea`, publication `1c79c503`. Последний Build **`3fc08bb1-07cb-4aed-906d-1c53df1846b5`**. Строковый escape9362 уже исправлен; искать его заново не нужно. P0a/P1 начаты, оба INCONCLUSIVE с `MaybeUninit must retain its compiler struct ADT kind`; N-false31 NOT_RUN, A1/A2 OPEN, нового formal credit нет. Все26 source statuses уже известны:8 INTENDED_CLASSIFIED/5 INCONCLUSIVE/13 NOT_RUN; повтор этих запросов не нужен.

Pinned Rust объявляет `pub union MaybeUninit<T>`, exporter передаёт Union→unionKind. Inventory `_ty` требует structKind+void до проверки name. Поэтому один текст ошибки не устанавливает имя/вид именно отказавшего record. Предложенный двухстрочный patch ещё не активирован. Завершённая R2-сессия израсходовала945 Cloud секунд за два Builds (D2 —516), остаток2655 retired; этот счёт закрыт.

### Действия

1. Переиспользуй [D2 result](cloud-build/sort4-caller-entry-native/A1-PARSER-D2-RESULT-2026-10-19.json) и уже сохранённые Brief/Reader observations. Не выводи normal/readonly failed call нового ADT error из старой string9362 диагностики.
2. Через каталог **D2 Build** найди точные normal/readonly MIR либо уже готовый диагностический record P0a/P1. Подтверди file ID и SHA; не переноси ID/SHA другого Build без каталога. Если документированный SHA входа совпал, это provenance файла, ещё не идентификация failing call.
3. Для выбранного файла используй Literal Locators вместо ожидания новой административной проекции только из-за неизвестных координат:

```bash
smallsort-brief "$BUILD_ID" --refresh --file "$MIR_FILE_ID" --locate 'MaybeUninit' --expect-sha256 "$MIR_SHA"
# ANCHOR_CODEPOINT — unicode_start подходящего locator этого файла/SHA
smallsort-brief "$BUILD_ID" --refresh --file "$MIR_FILE_ID" --locate 'unionKind' --near-position "$ANCHOR_CODEPOINT" --unit unicode-codepoint --expect-sha256 "$MIR_SHA"
# Затем один нужный безопасный фрагмент по возвращённым координатам
smallsort-brief "$BUILD_ID" --refresh --file "$MIR_FILE_ID" --position "$RECORD_POSITION" --unit unicode-codepoint --radius 160 --expect-sha256 "$MIR_SHA"
```

`BUILD_ID` заполни UUID D2 выше. Literal `unionKind` известен из pinned schema/exporter; его наличие около имени не доказывает принадлежность тому же ADT. Не ищи этот ожидаемый tag как единственный допустимый ответ: при другом наблюдаемом kind сохрани его. Более точные literals бери из известного serializer syntax или показанного verified fragment. Не угадывай offsets, не обходи файл окнами. При нескольких кандидатах сохраняй неоднозначность; отдельный record не выдавай за failing record без связи с обходом/call.

4. Сверь name/kind/void payload, substitutions и окружающий type context с `_ty`, pinned schema и exporter. Если маленького безопасного фрагмента недостаточно для принадлежности полей, явно укажи недостающую связь и запроси ровно её административную проекцию. Locator не разбирает AST/MIR и не восстанавливает преобразования.
5. Допиши существующий proposal: что наблюдено, что выведено из source, минимальный diff и точные необходимые controls. Только если recognized MaybeUninit+unionKind+void подтверждён, обоснуй строгое unionKind ожидание; не предлагай struct-or-union wildcard и не ослабляй name/substitutions/Self/F/regions/source-binding/admission. При другой identity/shape отклони прежнюю гипотезу и дай конкретный следующий вариант. Не применять patch в активный candidate и не запускать его без следующего scope/session решения.
6. Если proposal уточнён содержательно, получи review нового diff/rationale: **GPT-6 Luna HIGH**, `model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации и дорогой замены. GO здесь означает готовность proposal к решению, не разрешение CI/proof credit. Локально допустимы статические проверки/patch apply и малые synthetic service tests, но не полный MIR replay/preparer/compiler/decoder/refiner/verifier.

### Ограничения и результат

Общая persistent квота16 на Build включает locators, near и последующий fragment; D2 ранее использовал7 targeted calls, фактический остаток может отличаться. До20 координат, без pagination; при truncated уточнить task-relevant literal, не перечислять offsets. Проверяй expected SHA, request/index/archive, единицы, exact/complete/search_scope. `NO_MATCH_IN_SEARCH_SCOPE` не означает NOT_RUN/отсутствие ADT. `LOCATE_WITHHELD`/`WINDOW_WITHHELD` не обходить; PENDING не ретраить циклом. Нового Build ради чтения не делать.

R/C/tool/compiler/exporter/decoder/profile и guards сохраняются по D2 manifest: profile `084a0e7fb2e11511852066b9591df4377286debaa91c24c677ff4a5c89faf006`, parser `92d4e5b336b4e6409da814523500978b56c52218a6289434b526929ae1275b27`. Runtime/contracts/domain/kernel/refiner/admission не менять. Raw/full logs/archives/Cloud Logging и локальные копии запрещены; download_verified/исторические ledgers/verdicts не переписывать. Если независимые поля не доступны, вернуть точный limitation, без угадывания и ложного закрытия P0a/P1.

Обнови компактный STATUS и существующий proposal/evidence record, а ниже **один отчёт на месте**. Commit/push docs и допустимого proposal в назначенную project branch разрешены, чужие изменения не включать. Предыдущий завершённый отчёт сохранён в [архиве R2](task-history/select-p0a-parser-compatibility-2026-10-19-r2.md). После результата закончи чтение; следующая proof-сессия требует отдельного scope/window/budget.

## Отчёт агента

- **Статус / начало / конец:** EVIDENCE_LIMITATION — LOCATE_WITHHELD; начало 2026-10-19 19:46:02 UTC; конец подготовки 2026-10-19 19:50:05 UTC; commit/push завершены в checkpoint этой записи. Зависимое чтение остановлено без обхода удержания.
- **Source/docs checkpoint:** старт `3b4945e1d7c121415ea89a689f16f2f61531b053`; исполненный proof=infra `d246ccbcf7e851f1b3c471daf4ed7aa770e199ea`, publication `1c79c5035e1bbe6c192ba656e44d0b6c5628b4f2`. Прочитаны AGENTS и guide/Locators v0.10. Proof-сессия остаётся закрытой, новых Builds 0 / Cloud 0; прежние 945 charged / 2655 retired не менялись.
- **Ход:** переиспользованы D2 checkpoint/result; свежий каталог подтвердил P0a normal MIR ID `c42b1e8e4de1ca79b3a36b0f975a70cc604ce73ca1d541a7bad8971d2d64ffc2`, SHA `3bf1b47d7e28be437c7f5288c31ad930a1219018fa1cbd035706a94e9a2e6a01`, 471894 байта. Выполнен один адресный locate; string9362 и 26 statuses повторно не запрашивались.
- **Наблюдаемый ADT:** actual name/kind/payload/substitutions/координаты/общий record/type context и failing normal/readonly call НЕ УСТАНОВЛЕНЫ. Совпадение SHA с D1 не связывает новый ADT error с прежним call. Pinned union/exporter mapping — source-derived facts, не actual record.
- **Literal Locators:** `--refresh --file <P0a ID> --locate MaybeUninit --expect-sha256 <SHA выше>`; request `55265a235d42e6f3eaa728304bd307835cfb15f1d80686d26dad925169cc75b1`; status LOCATE_WITHHELD, reason SENSITIVE_UNTRUSTED_OR_OVERSIZED_SOURCE_LINE, exact=false, results=[], координаты/search_scope/complete отсутствуют. Archive `a8012dd090949cb3002ac9fb163424e422800f11be59f8f4324b310ca72a6ea5`, index `2181683c5e59ffabd849bdb19acb6a4fa12c14dfacc769649d3bfca1cfc018fa` совпадают с каталогом. SOURCE_OBSERVATIONS_NOT_PROOF, parser_input_binding NOT_ESTABLISHED, causal_status UNKNOWN. Один новый targeted call; ранее документированы семь, фактический общий остаток неизвестен. [Сохранённые bounded observations](cloud-build/sort4-caller-entry-native/A1-PARSER-MAYBEUNINIT-LOCATOR-2026-10-19.json).
- **Решение по proposal:** НЕДОСТАТОЧНО EVIDENCE. Двухстрочный diff сохранён побайтно и НЕ АКТИВИРОВАН; strict unionKind остаётся условным предложением после подтверждения recognized identity+unionKind+void одного record. Name/void/substs/Self/F/regions/binding/admission/lifecycle gates не менялись; необходимые positive/negative controls перечислены в [proposal](cloud-build/sort4-caller-entry-native/A1-PARSER-MAYBEUNINIT-PROPOSAL-2026-10-19.md). Статический git apply --check PASS. Profile `084a0e7fb2e11511852066b9591df4377286debaa91c24c677ff4a5c89faf006` и parser `92d4e5b336b4e6409da814523500978b56c52218a6289434b526929ae1275b27` проверены и неизменны. [Luna HIGH review](cloud-build/sort4-caller-entry-native/A1-PARSER-MAYBEUNINIT-REVIEW-2026-10-19.md) — GO для готовности proposal/docs, без blocking findings; review не разрешает активацию/CI. Controls binding/admission выполняются на соответствующих высших уровнях inventory, не только `_ty`.
- **P0a/P1/N-false31/A1/A2/formal credit:** INCONCLUSIVE / INCONCLUSIVE / NOT_RUN / OPEN / OPEN; нового formal credit нет, исторические 26 результатов не переписаны. Integrity каталога/архива не означает compilation/proof acceptance; download_verified не установлен.
- **Оставшийся пробел / административный запрос:** требуется отдельно разрешённая узкая проекция существующего D2: failing ADT id.name, kind+payload, substs/type identities, enclosing type path и общие границы record, member/SHA/transforms и call/traversal binding, если они записаны. Если failing association не восстанавливается — сообщить UNKNOWN. Полный MIR/log export, новый Build и обход WITHHELD не запрашиваются. Следующая реализация требует отдельного scope/window/budget.
