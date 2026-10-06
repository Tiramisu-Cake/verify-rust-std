> Historical snapshot — superseded for current status and instructions by
> [STATUS.md](STATUS.md), [AGENTS.md](../../AGENTS.md) and
> [AGENT-RUNBOOK.md](AGENT-RUNBOOK.md). Preserved unchanged below for evidence.
> In particular, local cleanup callers later passed in run37435525052 and
> baseline normal recovery in run37437514808; latest run37441463201 failed.
> Experiments are paused. Old "next" steps here do not authorize resumption.

# Challenge 8: пересмотр плана после handoff

Дата: 6 октября 2026. Проверенная research-ветка перед этим обзором:
`e0ef921e4058404b4944aff4335f79123ed53e61`, локальный HEAD совпадал с origin.
Рабочее дерево было чистым. Последний Actions run —
[37423762729](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37423762729),
completed/failure на `b3da9a5ef53b8001e63ce511ba27ae8efce67343`.
Активных research runs нет. Код std не менялся; SHA-256 SmallSort остаётся
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.

Это read-only пересмотр исходников, сохранённых logs/artifacts и текущего
состояния GitHub, с независимыми обзорами ресурсной модели и evidence gates.
Сборки, verifiers, tests и extractors не исполнялись; workflow не запускался.
Изменения этого checkpoint только документационные. Эксперименты остаются
остановленными. Этот план уточняет порядок продолжения из
[handoff](HANDOFF-2026-10-06.md); исторические результаты там сохраняются.

## Что можно считать результатом

| Результат | Что подтверждено | Что из него не следует |
| --- | --- | --- |
| Kani swap, run37383583285 | Два harness на actual std, i32, четыре ячейки, фиксированные позиции, 5/5 covers | Generic swap, panic и все требуемые UB |
| Kani insertion, run37389298278 | Actual callee через adapter, research composition и отдельный actual outer caller; i32, длины/offsets1..4, unwind6, 15/15 covers | Произвольные длины, независимый generic safety contract или modular proof actual outer loop |
| Size helper, run37401540878 | Изолированное actual generic тело, req true, точный результат size_of(T)<=8, LP64; pinned release VeriFast26.09 | Dispatch callers и интеграция в полную core library |
| Direct Drop, run37419989766 | Actual generic тело и copy call; конкретный контракт src/dst/ONE T.own; VF/refinement0 на experimental source-derived tool | Compiler cleanup reuse, held-reference release или insertion proof |
| Insertion probe, run37417173472 | Префикс проверки до первого copy/dst update; затем failure на compiler Drop | Доказанный callee, все ранние/normal/panic exits, второе сравнение или цикл |

Из семи public safety targets только size helper имеет изолированное
generic-доказательство. Ни один из трёх итоговых sorting contracts не доказан.
25 regressions подтверждают конкретные проверки расширений; восемь HRTB cases
не являются восемью доказательствами comparator bodies. Текущий local-cleanup
profile не прошёл полный gate: caller fixtures ещё не исполнялись.

## Почему меняем порядок

Основная проблема — переход от каждого следующего локального отказа к новому
изменению verifier без законченного контракта всей функции. Цепочка уже
затрагивает parser, translator, kernel и expression bookkeeping. Зелёный
микротест и независимый code review полезны, но не доказывают soundness этой
цепочки и не устанавливают её приемлемость для challenge.

Подтверждены три конкретные границы:

1. В [extractor](extract-verifast-insertion.py) общий `COMPARISON_DEBT_POST`
   возвращает долги первого сравнения на normal/unwind. На true path recovery
   до `tail.read()` уже закрывает доступы, завершает lifetime и возвращает
   обе cells. Для итогового normal exit этот post устарел. На false return и
   первом panic recovery после `if` вообще не выполняется; требуется отдельное
   восстановление, а не объявление всех exits доказанными.
2. `held_ref` создаётся через `init_ref_readonly(..., 1/2)`, а его release в
   insertion extractor отсутствует. Штатный `aliasing.rsspec` предназначает
   readonly route для случая без interior mutability. Actual second comparator
   принимает `&tmp`; unrestricted T/F не дают такого ограничения. Возвращённая
   доля tmp также не равна всей storage cell: нужен учёт второй доли и merge
   до `StorageDead`/`UnwindResume`.
3. `end_lft_binding` решает реальный конфликт нынешней ghost-разметки со
   scope-reserved половиной token. Необходимость нового kernel mechanism для
   любого корректного proof не установлена. Сначала следует проверить другую
   границу ghost lifetime и штатные share/reborrow/recovery.

Это не установленная unsoundness: review выявляет ещё не обоснованные границы
будущего доказательства. Само отсутствие ignore flags также не доказывает
полноту alias checks; baseline translator имеет mutable-reference shortcut,
который требуется включить в audit модели требуемых UB.

Дополнительно уточнён handoff: generic size helper проверялся release binary.
Экспериментальная patched-цепочка относится к generic insertion/Drop; смешивать
их trust boundaries нельзя. Approved list содержит VeriFast, но не даёт
автоматического подтверждения произвольным изменениям его семантики.

## Первый deliverable: ресурсная таблица всех путей

Это требования к следующей спецификации, пока не реализованный proof.
Safety не предполагает sorted prefix, Freeze/Copy, чистоту comparator или
сохранение ключей. Изменения interior state и состояния F должны учитываться;
возврат диапазона не означает равенство всех байтов исходному snapshot.

| Путь / граница | Что необходимо вернуть или сохранить |
| --- | --- |
| Вход | Полный initialized/owned range, type/thread ресурсы, owned F; корректные bounds и provenance |
| Первое сравнение: false return | Закрытые реальные accesses/borrows, полный диапазон и обновлённый F; gap и tmp ещё нет |
| Первое сравнение: panic | Тот же полный учёт диапазона, F и tokens на unwind; gap ещё нет |
| `tail.read` и guard creation | ONE logical ownership: held T плюс остальные cells; физические дубликаты не создают второго T.own |
| Copy и `guard.dst` update | Перемещение логического gap на одну cell; bounds, непересечение copy и корректный frame |
| Второе и последующие сравнения | Genuine generic share/reborrow tmp и sift с interior mutability; normal/panic recovery, сохранение guard и frame |
| Normal break / поздний panic | Actual Drop заполняет gap; все ссылки и доли tmp закрываются/сливаются до освобождения storage; восстановлен полный owned range и F |

Функциональный слой задаётся отдельно: сохраняемые logical keys, ordering laws,
sorted processed prefix и permutation. При panic sortedness не требуется.
ZST должен иметь отдельный анализ модели: адресное совпадение не разрешает
непроверенную арифметику `offset_from` или необоснованное разделение ресурсов.

## Исправленный порядок продолжения

1. **До новых semantic patches:** написать полный ledger и целевые normal/
   unwind posts из таблицы; сопоставить их с actual MIR cleanup order. Описать
   trust boundary каждого patch, особенно kernel cut и Drop lowering.
   Сравнить текущий маршрут со штатным borrow model и меньшим набором patches.
   Приемлемость modified verifier остаётся открытым вопросом; внешние обращения
   и tool application требуют отдельного указания владельца.
2. **После возобновления — завершить ограниченный diagnostic:** исправить
   только границы nested `match substs`, сохранив non-ADT fallback. Обновить
   строгие patch/output pins. Новый exact-SHA
   `verifast_local_drop_caller_gate`,90min: все25 regressions, actual Drop body,
   два positive callers и семь negative fixtures. Это проверка существующего
   механизма cleanup, не разрешение автоматически расширять kernel.
3. **Проверить жизнеспособность borrow boundary:** отдельный pilot для generic
   tmp/guard и повторного comparator с genuine sharing, normal/panic recovery
   и полным учётом storage. Сначала изолировать generic `ManuallyDrop<T>` →
   genuine share/reborrow → unrestricted FnMut → borrow recovery. Проверить
   Cell-подобный mutating callback и intended rejection утверждения о старом
   значении. Затем отдельным run проверить actual `&*tmp` → raw guard.src →
   copy/Drop → full storage recovery на normal/unwind.
   Общий shared borrow lifecycle — кандидат, пока не proof: `<T>.share` может
   не предоставить стабильный fractional points_to, нужный нынешнему copy
   contract. Завершение readonly access до comparator тоже лишь гипотеза:
   оно потребляет ref_initialized старого p, его ref_init_perm уже израсходован,
   а guard хранит src именно из p. Нужно доказать provenance и новое read
   permission для Drop без создания ресурсов. Предпочесть минимальный
   необходимый patch profile; каждое отклонение от baseline обосновать.
   Onecell Drop с ghost release/merge допустим как кандидат только после
   согласования ledger и checked actual body/callers. Ordering/key premises
   остаются вне safety pilot.
4. **Завершить actual insert_tail:** ресурсно корректные no-move/normal/panic
   exits, затем generic gap invariant и убывающий variant. Diagnostic с малым
   fixture может проверять один mechanism, но итоговый domain остаётся
   unrestricted T/F и arbitrary valid n>=2. Partial debt-post не использовать
   как итоговый контракт и не заменять его на `ens true`.
5. **Перенести проверенный callee на actual outer loop:** отдельные safety и
   functional contracts, ZST, offset boundary/abort и comparator unwind.
   Затем generic swap/sort4, merge/scratch, network/general/fallback callers,
   specialization и три small_sort contracts по [coverage ledger](coverage.md).
6. **До заявления полного safety результата:** закрыть каждый required UB
   category и автоматическую интеграцию. Immutable-store gap и unsupported
   CopyNonOverlapping validity в pinned Kani остаются самостоятельными
   obligations. Дополнительные bounded runs16/32 могут измерять стоимость,
   но не решают эти проблемы и не доказывают произвольные длины.

## Критерии продолжения и смены подхода

Расширять insertion route следует после демонстрации полного normal/panic
ownership recovery в pilot и явного обоснования доверенных изменений verifier.
Green cleanup gate — необходимая проверка его механизма, но недостаточный
критерий выбора всей архитектуры.

Если для второго comparator или cleanup нужны Freeze/Copy/purity в safety,
непроверенный ownership bridge, удаление tokens либо новый kernel hook без
семантического обоснования, остановить эту ветку развития и пересмотреть
boundary. Сохранить полученные milestones. Альтернативный первый pilot —
generic swap или sort4 без lifetime cut/ManuallyDrop/Drop extensions; его успех
проверит более простой маршрут, но не решит insertion автоматически.
Новый tool или смена pin должны иметь конкретное основание и отдельный план
соответствия требованиям, а не быть способом получить green badge.

## Исправления процесса

- Разделять setup/build, frontend/export/decode, resource proof, unsupported
  check, timeout и инфраструктурный отказ. Последний run — translator bug,
  не exhaustion бюджета; увеличение времени ему не поможет.
- Разбирать новые non-exhaustive/redundant-match warnings до интерпретации
  proof results. Последние OCaml typing/match ошибки статическое review
  пропустило; review не заменяет hosted compilation/regression gate.
- Для каждого fixture заранее фиксировать expected stage, predicate и место
  отказа. Несвязанный error или авария verifier не являются intended negative.
- Связывать normal/cleanup MIR edges с проверенными contracts и whole-unit
  outcome. Счётчики trace, duplicate `note:` и freeze/unfreeze records не
  заменяют это чтение. Broken-post case сейчас проверяет failure callee отдельно;
  это не отдельный caller+invalid-summary experiment.
- При audit scope cut учесть ещё не выполненный dedicated malformed
  CFG-ingress fixture из [scope notes](verifast-end-lft-binding.md).
  12 существующих cases не закрывают этот пункт автоматически.
- Один relevant hosted experiment за раз: pushed SHA, новый dispatch, полный
  результат, компактная запись domain/checks/covers/times/next step. Не rerun
  старой версии, не speculative duplicates и не повтор green без причины.
- Локально только чтение/редактирование/git/gh и разрешённые static checks.
  Documentation-only checkpoint не требует verification run. Runtime std,
  algorithms и generic signatures сохраняются; upstream публикация отдельно.

Точный следующий шаг в текущем остановленном состоянии — ресурсный ledger и
decision review из пункта1. Первый hosted run после возобновления — corrected
local-cleanup diagnostic из пункта2, если этот механизм остаётся предметом
исследования. Во время данного обзора новых proof результатов не получено.
