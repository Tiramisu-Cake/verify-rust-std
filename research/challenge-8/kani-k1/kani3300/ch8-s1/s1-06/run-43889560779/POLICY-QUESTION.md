# S1-06 — вопрос координатору (решение не применено)

Текущий completeness gate сохранён: 10 групп остаются FAILED/INCOMPLETE,
26 runner rows UNKNOWN. Нового tool/control fix нет.

В heavy 16 строк содержат по одной stock property без допустимой координаты.
Ещё две такие записи — production и mutated `stable_freeze_activation`.
Все 18 имеют class `unreachable`, description `unreachable code`, status `SUCCESS`;
display location содержит `library/core/src/lib.rs:0:0 in function ...`.
Decoder корректно сохраняет display и nullable file/line, затем отказывает приёмке.
Полный inventory 9986/9986 сохранён и согласован; 9968 properties имеют sites.

Это stock assertions для MIR `TerminatorKind::Unreachable`, а не обязательные
post/frame/relation assertions или covers. В pinned compiler `0aac` это единственный
producer `PropertyClass::Unreachable`; он генерирует assert(false), затем assume(false).
См. exact excerpts и hashes в STOCK-ROLE.json. Их SUCCESS означает доказанную
недостижимость соответствующего блока в source-reported модели. Нельзя удалять
эти проверки, превращать их в assumed checks или путать class `unreachable` со
статусом `UNREACHABLE`. Конкретный MIR block и причина нулевого span не установлены.

Варианты для следующего решения координатора:

1. Сохранить обязательные положительные file/line для всех properties. Получить
   корректные source spans от producer и новые compatible same-run receipts.
2. Разрешить узкое location-only исключение для этих exact двух IDs и их same-row
   occurrences: stock class/description/status SUCCESS, original display, полное
   согласование inventory, отсутствие failures/unknown/lost properties и сохранение
   всех checks. Sites всех обязательных post/frame/relation/covers, named negative
   oracles, unsupported links и прочих properties остаются обязательными. Список
   исключений и предел assurance фиксируются в каждом receipt. Любая неизвестная
   роль/другой статус/ID продолжает fail-closed.

**Вариант 2 здесь не принят и не реализован.** Он снял бы непосредственную причину
runner completeness failure для 18 строк, но не дал бы qualified acceptance:
в 10 failed группах отсутствует same-run after fingerprint, остаются source/contract
binding, required-success mapping и разбор недостижимых обязательств. Восстановить
неизмеренный after snapshot офлайн или перенести его из прошлого run нельзя.

Ещё 8 строк light-controls имеют полные sites, но заблокированы общим group gate
и отсутствующим after snapshot. Принимать их через молчаливое деление failed group
этот пакет не разрешает. Точное состояние остальных gates — accept/ACCEPT.json.
