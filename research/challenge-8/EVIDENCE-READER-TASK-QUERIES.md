# SmallSort Evidence v0.11 — адресные примеры для Select / Merge

Сначала [краткий guide](EVIDENCE-READER-GUIDE.md). Метаданные ниже взяты из сохранённых bounded observations, а не из нового чтения исходных файлов. Проверь текущий каталог/индекс; не смешивай Builds. Старые WITHHELD/16-квота больше не запрещают эти запросы. Proof scope/закрытые сессии и их бюджеты сохраняются.

## Select: actual MaybeUninit record в D2

Build `3fc08bb1-07cb-4aed-906d-1c53df1846b5`, P0a normal MIR. String9362 уже исправлен; новый ADT error не устанавливает failing normal/readonly call. Ранее locate был удержан v0.10; теперь продолжай через v0.11:

```bash
BUILD_ID='3fc08bb1-07cb-4aed-906d-1c53df1846b5'
FILE_ID='c42b1e8e4de1ca79b3a36b0f975a70cc604ce73ca1d541a7bad8971d2d64ffc2'
EXPECTED_SHA='3bf1b47d7e28be437c7f5288c31ad930a1219018fa1cbd035706a94e9a2e6a01'
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --expect-sha256 "$EXPECTED_SHA"
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --locate 'MaybeUninit' --expect-sha256 "$EXPECTED_SHA"
```

По нужному locator прочитай position/lines, соседний контекст и при необходимости следующую страницу с выданным next_offset. Нужны name/kind/payload/substitutions одного record и связь с enclosing type/call; близость `MaybeUninit` и `unionKind` этого не доказывает. Не выдавай выбранный record за failing record без traversal/call binding. При необходимости читай относящиеся JSON fields/argv как данные. Реализация shape fix остаётся отдельным scope decision; старые26 statuses не запрашивай повторно без причины.

## Merge: недостающие locals/body/cast связи в prefix MIR

Уже наблюдены AST895 и MIR target region='<erased>, mutable slice_u64, kind.pointerCoercion=void. Полные source locals/array3/body binding и metadata construction ещё не установлены. Прежний BUILD_QUERY_BUDGET_EXCEEDED относится к старому пути, не к v0.11:

```bash
BUILD_ID='5f668cd9-fb34-4570-ad1c-4b97abbb36d0'
FILE_ID='7decbe12be84eeb9ce03066a786554e0d80548f8d6e82b2b8a00d6e6ae15c179'
EXPECTED_SHA='70be7daa815fd80ad8f921b1da2984e3cc64d258a7a0c625d59958b82518723c'
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --expect-sha256 "$EXPECTED_SHA"
```

Переиспользуй сохранённые locator positions и cast fragments, затем уточняй соседний context/известный serializer literal/JSON pointer по данным. Не повторяй весь поиск source214. Metadata/provenance gate остаётся открытым; локализация не разрешает lifetime/model patch.

## Merge: actual fullbody guard AST

Это **другой Build/файл**, не prefix AST. Прежнее лексическое удержание снято новой политикой:

```bash
BUILD_ID='c78529d0-f18b-4d13-9060-6517cde03cd5'
FILE_ID='7d457f18b4648275ca0a94b68859d4f392f468bfe2b5d791e28d96b664fe6209'
EXPECTED_SHA='2757ca2a479947a06f44a78647545d78a8f37739c146bdf227819287f709748a'
smallsort-brief "$BUILD_ID" --refresh --file "$FILE_ID" --locate 'verified/lib.rs(207,49-52)' --expect-sha256 "$EXPECTED_SHA"
```

Прочитай нужный узел и контекст; нужны AddressOf operand/type, preceding MergeFractionsStmt и tmp storage classification. При нескольких совпадениях уточни привязку, не выбирай ближайшее как enclosing node автоматически. Проверка existing continuation defect и его causal applicability раздельны. Новые Builds/trusted semantics этим файлом не разрешаются.

## Продолжения

Для locator/JSON-контейнера повторяй **тот же запрос** с `--offset "$NEXT_OFFSET"`, полученным из ответа. Для длинной JSON-строки — тот же `--pointer` с `--value-start "$NEXT_VALUE_START"`, без --offset. Не вычисляй offsets и не загружай автоматически все страницы. Если вновь получен старый WITHHELD/BUILD_QUERY_BUDGET_EXCEEDED, сохрани версию/точный ответ и проверь актуальный targeted v0.11 путь; не угадывай значения и не меняй backend/cache/IAM.
