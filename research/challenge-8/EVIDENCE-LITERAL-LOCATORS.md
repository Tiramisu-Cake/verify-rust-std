# Literal Locators v0.10 — короткое дополнение

Команды `--locate`/`--near-position` **доступны по подтверждению владельца от 2026-10-19** в `/usr/local/bin/smallsort-brief`. Остальные запросы v0.9 сохраняются; полный [справочник v0.10](EVIDENCE-READER-REFERENCE-v010.md) нужен только для деталей.

## Команды и порядок

После Brief/Reader выбери один проверенный file ID данного Build и его SHA. Если координаты нужного фрагмента неизвестны, locate возвращает только координаты буквального текста:

```bash
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --locate 'InferredTypeExpr' --expect-sha256 "$EXPECTED_SHA256"
# ANCHOR_CODEPOINT — unicode_start ранее полученного locator того же файла/SHA
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --locate 'InferredTypeExpr' --near-position "$ANCHOR_CODEPOINT" --unit unicode-codepoint --expect-sha256 "$EXPECTED_SHA256"
```

Затем запроси один нужный безопасный фрагмент обычным `--position --unit --radius` либо `--start --end`. Это отдельный запрос со своими ограничениями и расходом общей квоты. Совпадение, ближайшее по тексту, не обязательно является enclosing AST node.

- `--locate` — **точный регистрозависимый** поиск без regex/нормализации; Reader `--search` не учитывает регистр и ищет только сохранённые очищенные наблюдения. Literal: минимум 3 печатных Unicode codepoints, максимум 160 UTF-8 байт. Переводы строк/controls и unsafe literals отвергаются; metacharacters — обычный текст, перекрывающиеся совпадения включены.
- С `--refresh --file` выбирай ровно один селектор: pointer, строки, position или locate; смешивать их нельзя. Для near дополнительно нужны `--near-position` и `--unit unicode-codepoint|utf8-byte`; `--radius` относится только к position, не к locate.
- Near anchor с0, радиус фиксирован **±4096 выбранных единиц**; byte scope расширяется до UTF-8 границ. Проверяй возвращённый `search_scope`; совпадение должно целиком попадать в него. Anchor бери из установленного locator, не угадывай и не перебирай смещения.
- До **20 locators**, в порядке источника, без pagination/total count, без текста/hex. При переполнении `truncated=true`, `complete=false`: выбери более конкретный известный literal по задаче, не реконструируй файл запросами. Уточнение literal и near тоже могут расходовать квоту.
- Поля `unicode_start`/`unicode_end_exclusive` и `utf8_byte_start`/`utf8_byte_end_exclusive` — с0, конец исключён; `line/column` — с1, LF строки/Unicode колонки, `end_line/end_column_exclusive` — исключающий конец. Сохраняй file/index/archive SHA, request ID, нормализованный selector, scope и coverage.
- `exact=true` означает точность численных координат; `complete=true` — все совпадения в указанном scope поместились. `source_absence_established=false` всегда. `NO_MATCH_IN_SEARCH_SCOPE` не означает NOT_RUN, семантическое отсутствие или отсутствие в другом файле.
- Перед поиском проверяется **весь файл**, даже при near/отсутствующем literal. `LOCATE_WITHHELD` не раскрывает координаты/число совпадений; не обходи его сменой literal/scope/окна. Длинная строка >64 KiB допускается для coordinates-only поиска, но текстовое окно всё ещё может быть `WINDOW_WITHHELD`; locator не гарантирует выдачу текста и не снимает content policy.
- Общая persistent квота **16 reserved requests на Build**, вместе со всеми v0.9 селекторами; ошибки после резервирования учитываются, одинаковые завершённые запросы кешируются. Кеш/квоту не сбрасывать, `PENDING` не ретраить циклом. Файл ≤4 MiB, request body ≤2048 байт, response ≤12000 байт; прочие archive/content bounds прежние.

Locator не разбирает AST/MIR, не связывает их узлы, не выводит receiver type/region и не устанавливает вход парсера или причину отказа. Сохраняй `SOURCE_OBSERVATIONS_NOT_PROOF`, `causal_status=UNKNOWN`, `parser_input_binding=NOT_ESTABLISHED` до отдельного подтверждения. Не делай новый proof Build ради локализации; raw logs/archives и обход WITHHELD запрещены. Сессии, pins, бюджеты и coordinator не меняются.

Готовый пример для Merge: [task queries](EVIDENCE-READER-TASK-QUERIES.md). Остальной порядок: [краткий guide](EVIDENCE-READER-GUIDE.md).
