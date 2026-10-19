# Literal Locators — актуальные правила v0.11

Читай [краткий guide](EVIDENCE-READER-GUIDE.md). v0.11 добавляет обзор/info, ручную пагинацию locators/JSON, части JSON-строк; отменяет лимит16 и прежние лексические WITHHELD. Полный источник: [guide v0.11](EVIDENCE-READER-REFERENCE-v011.md).

```bash
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --expect-sha256 "$EXPECTED_SHA"
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --locate 'AddressOf' --expect-sha256 "$EXPECTED_SHA"
# Только если ответ выдал next_offset: повтори тот же selector/index/SHA
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --locate 'AddressOf' --offset "$NEXT_OFFSET" --expect-sha256 "$EXPECTED_SHA"
# При установленном anchor: фиксированные ±4096 явно выбранных единиц
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --locate 'InferredTypeExpr' --near-position "$ANCHOR_CODEPOINT" --unit unicode-codepoint --expect-sha256 "$EXPECTED_SHA"
```

Locate — непустой literal≤160UTF-8байт, точно с учётом регистра, без regex; до20 координат на странице. Координаты `unicode_start/unicode_end_exclusive`, `utf8_byte_start/utf8_byte_end_exclusive` — с0, конец exclusive; `line/column` — с1, LF/Unicode, `end_line/end_column_exclusive` — исключающий конец. При next_offset продолжай вручную по нужным совпадениям; не придумывай offsets. Source-order/близость не определяют enclosing AST/MIR node. После locator запроси position/lines; уточняй соседний контекст по задаче, не выгружай автоматически весь файл.

Response≤12000байт; position radius1–256, lines≤12/4096UTF-8байт; слишком длинная строка даёт стартовую позицию для окна. Предел файла64MiB; overview сообщает реальные размеры/формат/доступные запросы. Near использует `--unit`, а не `--radius`. Expected SHA проверяется до чтения; сохраняй request/index/archive/file/scope/coverage и не смешивай страницы разных индексов.

Пожизненной16-квоты и старого запрета уточнения после LOCATE_WITHHELD/WINDOW_WITHHELD больше нет. Старые WITHHELD/BUILD_QUERY_BUDGET_EXCEEDED фиксируй с версиями/точным ответом и проверь текущий v0.11 путь; не переноси их на новые запросы. Environment/argv/commands читаются как данные. No-match/complete=false не означают NOT_RUN/семантическое отсутствие; exact=true относится к координатам, не к доказательству. Для JSON детей/value continuation используй основной guide. Proof Build или raw/GCS доступ ради локализации не нужны; proof scope/budget/закрытые сессии не меняются.
