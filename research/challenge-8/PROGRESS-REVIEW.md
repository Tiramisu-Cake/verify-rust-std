# Challenge 8: прогресс и контрольный пересмотр плана

Редакция 1, 11 октября 2026, Europe/Moscow. Документ подготовлен по поручению
владельца после сравнения с upstream PR. Это управленческая оценка и план
контрольного разбора; proof claims определяются исходными evidence, а полномочия —
[WORK-POLICY](WORK-POLICY.md) и конкретным действующим заданием.

**Исходный индекс готовности — 15%. Контрольное окно — по две сессии каждому
из двух proof-агентов. Текущие сессии 11 октября считаются первыми.**
После второй сессии соответствующего агента разбираем результат до назначения
третьей на тот же интерфейс. Достигнутый раньше контрольный результат позволяет
пересмотреть следующий шаг раньше.

> **Редакция 2, 23 октября 2026 — контрольный разбор и решения: [§9](#9-редакция-2--контрольный-разбор-23-октября-2026).** §1–8 сохраняют baseline 11 октября без переписывания.

## 1. Что означает процент

Это условный индекс зрелости десяти целевых доказательств: семь safety-целей R1–R7
и три sorting-контракта F1–F3 из [COMPLETION-PLAN](COMPLETION-PLAN.md).
Каждая цель имеет одинаковый вес 10% индекса. Равный вес выбран для прозрачного
учёта требований, а не как оценка одинаковой трудоёмкости.

Для каждой цели используется одна и та же шкала:

| Балл цели | Проверяемое основание |
| --- | --- |
| 0% | Нет доказательства самой целевой функции; подготовленные кандидаты, наблюдения компилятора и отдельные математические леммы учитываются отдельно |
| 25% | Есть проверка actual тела или его существенного фрагмента в ограниченном домене; существенные ветви, ресурсы или применимость ещё открыты |
| 50% | Actual целевая функция проверена целиком в полезном, но ещё ограниченном домене; проверены её зависимости и передача предпосылок. Для safety закрыты необходимые normal/panic выходы, для functionality — sortedness и сохранение вхождений |
| 75% | Самостоятельная целевая теорема доказана в полном требуемом заявленном домене; остаются перенос в итоговую конфигурацию, интеграция с callers или квалификация профиля |
| 100% | Полный домен и применимость подтверждены в итоговой совместимой source/tool/target конфигурации, proof проходит пригодную для подачи автоматизированную проверку и review |

Балл присваивается только при наличии evidence для соответствующей ступени.
Большее число fixtures, патчей, controls, коммитов или потраченных часов его
не повышает. Общие вспомогательные леммы не начисляют баллы автоматически
каждому будущему потребителю. Исторический PASS не переносится на новый профиль.

**15% не означает, что осталось 85% времени, что потрачено 15% усилий или что
вероятность получения награды равна 15%.** Это грубая управленческая шкала.
Неизвестные препятствия инструментария и композиции делают прогноз срока
ненадёжным. Веса и ступени не менять ради роста числа; изменение методики
оформлять новой редакцией с пересчётом прежнего baseline.

## 2. Исходная оценка

Основание — завершённые доказательные результаты из [E1–E5](#8-источники).
Выполняющиеся сессии не получают кредит за ожидаемый результат.

| Цель | Балл | Что уже есть / почему не следующая ступень |
| --- | ---: | --- |
| R1 — safety StableSmallSortTypeImpl::small_sort | 0% | Компоненты есть; целевое доказательство реализаций и callers не собрано |
| R2 — safety UnstableSmallSortTypeImpl::small_sort | 0% | Fallback и делегирование не собраны в целевую теорему |
| R3 — safety UnstableSmallSortFreezeTypeImpl::small_sort | 0% | General/network/fallback и специализации не покрыты целиком |
| R4 — safety swap_if_less | 25% | Actual Kani i32, фиксированные позиции 1/2; generic resources, допустимые индексы и comparator effects/panic открыты |
| R5 — safety insertion_sort_shift_left | 25% | Actual i32 для длин/offset 1..4; используется sorted-prefix premise. Независимый полный safety-домен, insert_tail и произвольная длина открыты |
| R6 — safety sort4_stable | 25% | Actual bounded Kani и native C1–C4 фрагмент; весь sort4, реальные caller premises, C5/copies и полный generic domain открыты |
| R7 — has_efficient_in_place_swap | 75% | Историческая полная isolated generic теорема на LP64, stock VeriFast 26.09; перенос в итоговый профиль/dispatch не закрыт |
| F1 — sorting-контракт StableSmallSortTypeImpl::small_sort | 0% | Нет собранного контракта actual entrypoint |
| F2 — sorting-контракт UnstableSmallSortTypeImpl::small_sort | 0% | Нет собранного контракта actual entrypoint |
| F3 — sorting-контракт UnstableSmallSortFreezeTypeImpl::small_sort | 0% | Нет собранного контракта actual entrypoint |

Расчёт: `(0 + 0 + 0 + 25 + 25 + 25 + 75 + 0 + 0 + 0) / 10 = 15%`.

На ступени 100% сейчас **0 из 10** целей в единой итоговой конфигурации.
Отдельно сохраняется полная историческая isolated теорема R7; нулевой счётчик
интеграции её не отменяет. Готовность к подаче — **нет**.

Важные активы, которые ещё не закрывают целевые entrypoints:

| Актив | Установлено | Следующая связь с actual Rust |
| --- | --- | --- |
| Сети 9/13 | Математические order/permutation и общий strict-weak-order переход | Реальный compare-exchange, память и композиция с caller |
| Merge geometry | Индексная геометрия для произвольного n >= 2 | Actual reads/copies, владение, callbacks и unwind |
| Sort4 functionality | Actual bounded sortedness, полная перестановка tagged items и stability | Полный safety-контракт и реальные callers |
| Native C1–C4 | Четыре последовательных actual сравнения, normal и direct-unwind ресурсы в ограждённом фрагменте | Вывести предпосылки из настоящего caller без исследовательского guard |
| Selected Drop | Bounded selected-method normal posts и наблюдаемый destructor binding | Реальное generated glue и cleanup из insert_tail |

## 3. Как считаем две сессии

Счётчик отдельный для `select-sort4` и `merge`: **2 + 2 = 4 agent-сессии**.
Они могут выполняться параллельно; это не четыре последовательных дня и не две
сессии на всю команду. Смена имени эксперимента, версии патча или Build не
обнуляет счётчик того же интерфейса.

Опубликованные STATUS обоих proof-агентов показывают открытое окно:

| Владелец | Сессия №1 | Сессия №2 |
| --- | --- | --- |
| select-sort4 | Начало 11.10, 22:22:51 МСК; phase SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11; стартовый checkpoint 5ffebdf53cc37b5814fa78ad3acb4081519288d8. Статус ACTIVE по E6 | Следующая отдельно разрешённая сессия той же миссии после её checkpoint |
| merge | Начало 11.10, 22:19:34 МСК; actual generated-glue qualification; стартовый checkpoint e267f9485bfe620f5570b66e63226f1d0ea6fb77. Статус ACTIVE по E7 | Следующая отдельно разрешённая сессия той же миссии после её checkpoint |

Это привязка к опубликованным карточкам, а не live-аудит наличия активного Build.
Если к моменту принятия документа окно уже закрыто, выполненная сессия всё равно
остаётся №1. Результат записывается по её итоговому checkpoint.

Часовой промежуточный отчёт не считается отдельной сессией. Review/integration
VeriFast maintainer также не расходует эти два proof-счётчика. Proof-агент
сохраняет разработку своей функции и необходимых патчей; maintainer проверяет
и интегрирует пакет по своей миссии.

Текущие deadlines, Cloud ceilings и allowlists сохраняются. Этот документ
не открывает сессию №2 и не выделяет ей бюджет. Подробности новой сессии задаются
отдельным поручением по действующим правилам. Полезный текущий Build не прерывать
ради принятия документа.

## 4. Контрольные артефакты

Это критерии оценки выбранного подхода за две сессии, а не обещание закрыть
Challenge 8 за этот срок. У каждого артефакта бинарный статус: достигнут только
при выполнении всего критерия. Частичные результаты описываются текстом.

| ID / владелец | Проверяемый артефакт | Критерий достижения | Baseline |
| --- | --- | --- | --- |
| A1 / select-sort4 | Compiler-selected binding и перенос bound | На исходном caller подтверждены обе исходные реализации, выбранный Instance, generic args/clauses и typing environment; evidence admission и отрицательные controls проходят на тех же inputs. Из настоящего threshold/guard выведен bound для helper; len + 16 доказано без supplied bound | НЕ ДОСТИГНУТ: conditional threshold32/default16 отдельно от actual transfer |
| A2 / select-sort4 | Caller → helper prefix → native C1–C4 | Из actual caller пройден исходный helper до первого sort4 callsite; source/scratch/типовые ресурсы получены из caller. Тот же consumer проверяет четыре сравнения, normal и все четыре direct-unwind выхода с полными posts. Исследовательский size guard или необоснованный nonzero не подменяет actual guard | НЕ ДОСТИГНУТ: отдельный guarded C1–C4 PASS есть, caller bridge открыт |
| B1 / merge | Проверенное compiler-generated Drop glue | Собран официальный refiner; извлечено и проверено реальное generated body, его точный вызов destructor и исходный CFG/unwind. Receiver создаётся caller, end/retirement протокол и его требуемые negatives проверены; normal CURRENT/resource/return/free/leak posts проходят | НЕ ДОСТИГНУТ: binding наблюдался, selected method PASS не доказывает glue |
| B2 / merge | Применение cleanup в actual insert_tail | В разрешённом домене actual insert_tail получает свой guard/receiver из собственных ресурсов; normal и достижимый late-panic после сдвига восстанавливают актуальный slice/resource state. Проверен реальный случай с несколькими ячейками, например структура входа [10,20,5]; supplied adapter-state не заменяет actual caller | НЕ ДОСТИГНУТ: actual cleanup и применимость к insert_tail открыты |

Порядок: A1 → A2 и B1 → B2. Ориентир первой сессии — A1/B1, второй — A2/B2.
Если первое обязательство не закрыто, второе не объявляется доказанным; оставшаяся
сессия проверяет новую конкретную гипотезу в прежних разрешённых границах.
Срок пересмотра от этого не переносится автоматически.

Для A2 остаются отдельными будущими обязательствами C5, копирования, весь sort4,
остальные callers и полный требуемый домен. B2 в конкретном разрешённом типе/
размере не доказывает generic insert_tail, R5 или fallback. Нельзя расширять
generic/ZST/kernel scope текущего задания только ради контрольного артефакта.

Итого на baseline: **0/4 контрольных артефактов полностью достигнуты**.
Их достижение может быть существенным прогрессом при неизменном общем индексе:
процент повышается только после перехода самой целевой функции на новую ступень.

## 5. Что предъявляется на разбор

Использовать существующие checkpoint, manifests и EXPERIMENT-LOG; второй
параллельный ledger или обязательная новая machine schema не нужны.

Для достигнутого артефакта дать ссылку на единый evidence-пакет:

- source/proof/infra/tool/compiler/profile identities и Build ID;
- точный domain, actual caller и источник каждой premise; оставшиеся supplied
  предпосылки перечислены;
- normal/unwind/abort posts, реально достигнутые proof stages и итоговый verdict;
- Evidence Brief, доступные hashes/identities, обязательные controls и
  source/refinement claims. Raw logs — только по separately authorized
  administrative audit;
- статус experimental profile, что проверил maintainer и что ещё не принято.

Если критерий не достигнут, равноценный результат для **решения о плане** —
минимальный воспроизводимый blocker: exact inputs, первый causal отказ,
проверенная гипотеза, исключённый вариант и следующий вариант с ценой/риском.
Такой результат полезен, но сам по себе не повышает процент proof-готовности.
Setup failure, timeout или сборка refiner не считаются доказательством функции.

## 6. Когда и как пересматриваем план

| Событие | Решение |
| --- | --- |
| A2 или B2 достигнут раньше окончания второй сессии | На безопасном checkpoint разобрать пригодность интерфейса и следующий actual consumer; ждать второй сессии ради числа не нужно |
| Вторая сессия данного proof-агента завершилась | Обязательный разбор его A1/A2 или B1/B2 до назначения третьей сессии на тот же интерфейс; другой агент не обязан ждать |
| Снят существенный caller premise или пройдено новое реальное обязательство, но артефакт ещё неполон | Зафиксировать точный прирост и оставшийся разрыв. Продолжение возможно по новому конкретному решению, без автоматического продления «ещё на две» |
| После двух сессий только новые wrappers/наблюдения/setup fixes, actual consumer не продвинулся | Пересмотреть ресурсный интерфейс или способ получения compiler evidence; подготовить минимальный reproducer и альтернативный ограниченный эксперимент вместо повторения прежнего задания |
| Обнаружено противоречие модели, ложный PASS или несовместимый профиль | Приостановить использование затронутого результата, пересчитать его балл и оценить зависимые claims; не менять исходный verdict или controls задним числом |
| Нужны новые trusted semantics, kernel/alias изменения или выход за scope | Разобрать отдельное scope/trust решение до реализации по WORK-POLICY |

Промежуточный успех не требует остановить всю разрешённую сессию: агент продолжает
внутри scope и бюджета. Пересмотр — решение о следующем вложении, а не остановка
полезного Build или автоматическая передача разработки maintainer.

После B2 ближайшая стратегическая цель остаётся
**полный actual insert_tail → arbitrary-length insertion → default/fallback**.
Для самостоятельной R5 не вводить cutoff len <= 32. После A2 — полный actual
sort4, затем sort8 с доказанным merge. Новые усиления математических сетей и
stability не становятся приоритетнее этой композиции.

На совместном разборе сверить также готовность интеграции и изменения сильных
upstream PR #694/#701. Их наличие — ориентир для покрытия, а не разрешение
импортировать чужие proof-решения. Миграция на другой инструмент не следует
автоматически из истечения двух сессий: ей нужен проверяемый feasibility-артефакт.

## 7. Обновление документа

Общую оценку обновляет reviewer/координатор после чтения checkpoint; proof-агенты
добавляют в собственный существующий отчёт номер сессии, статус A1/A2 либо B1/B2,
evidence и оставшийся blocker. Не менять чужие worktrees или ledgers.

При обновлении сохранить датированную строку истории; не переписывать baseline.
Каждое изменение балла связывать с закрытой ступенью и evidence. Новые semantic
риски могут понижать оценку. Достижение контрольного артефакта не квалифицирует
профиль и не означает upstream acceptance.

| Дата | Индекс | Артефакты | Причина |
| --- | ---: | --- | --- |
| 2026-10-11 | 15% | A1/A2/B1/B2 не достигнуты | Первая оценка по шкале v1; текущие proof-сессии считаются №1 |
| 2026-10-23 | 15% | A1/A2/B1/B2 не достигнуты | Контрольный разбор после Select R23, Merge R22, Network N4 (§9): ни одна цель не перешла на новую ступень; решения 1–6 и разовое расширенное окно |

Основной [COMPLETION-PLAN](COMPLETION-PLAN.md) сохраняет конечные требования.
Этот документ задаёт измерение и ближайшую точку решения. Принятие документа —
по [ADOPTION](ADOPTION.md), на безопасной границе; draft сам по себе не меняет
действующих proof-разрешений.

## 8. Источники

- E1 — [coverage, snapshot 72428327](https://github.com/Tiramisu-Cake/verify-rust-std/blob/72428327d733abe9fecf73738122a6e32ac4d467/research/challenge-8/coverage.md): R4–R7, bounded функциональность и ограничения.
- E2 — [native C1–C4, 11 октября](https://github.com/Tiramisu-Cake/verify-rust-std/blob/72428327d733abe9fecf73738122a6e32ac4d467/research/challenge-8/cloud-build/sort4-native-c1-bound/END-CHECKPOINT-2026-10-11-ZST-REPAIR.md): положительный фрагмент и незакрытая применимость.
- E3 — [merge checkpoint](https://github.com/Tiramisu-Cake/verify-rust-std/blob/ae9f5cf96de1d30eb762c0af3e4a47c1b77044d3/research/challenge-8/cloud-build/origin-layout/FINAL-CHECKPOINT.md): selected method, binding и ограничения glue/insert_tail.
- E4 — [геометрия merge](https://github.com/Tiramisu-Cake/verify-rust-std/blob/ae9f5cf96de1d30eb762c0af3e4a47c1b77044d3/research/challenge-8/merge/GEOMETRY-RESULTS.md).
- E5 — [математические сети](https://github.com/Tiramisu-Cake/verify-rust-std/blob/ae9f5cf96de1d30eb762c0af3e4a47c1b77044d3/research/challenge-8/networks/coverage.md).
- E6 — [select STATUS, 04c9208d](https://github.com/Tiramisu-Cake/verify-rust-std/blob/04c9208d266305b04645b26fcb858916e0f08d94/research/challenge-8/STATUS.md): идентичность первой сессии.
- E7 — [merge STATUS, de2f3f5f](https://github.com/Tiramisu-Cake/verify-rust-std/blob/de2f3f5f80c4e10488ef1024b8bba76bf476c548/research/challenge-8/STATUS.md): идентичность первой сессии, body-v4 build failure и body-v5 pending.
- E8 — [upstream #694](https://github.com/model-checking/verify-rust-std/pull/694), [#701](https://github.com/model-checking/verify-rust-std/pull/701): контекст выбора приоритетов; их PR claims не считаются нашими доказательствами.

## 9. Редакция 2 — контрольный разбор 23 октября 2026

Разбор выполнен по закрытым checkpoint Select R23 (`505aea0d`), Merge R22
(`733b6a7d`), Network N4 (`9a7a3d00`) и STATUS роли verifast (`92fb66c5`).
Обязательный разбор «после второй сессии» из §6 с 11 октября формально не
проводился; вместо него 19–23 октября расширялась автономия агентов. Эта
редакция закрывает долг и фиксирует решения владельца, принятые 23 октября.

### 9.1 Индекс и артефакты

Индекс остаётся **15%**: R4/R5/R6 — 25%, R7 — 75%, остальные — 0%. Ни одна
целевая функция не перешла на новую ступень. Контрольные артефакты A1/A2 и
B1/B2 не зафиксированы как достигнутые. Ближайшие к ступени результаты:

| Owner | Что есть (SOURCE_REPORTED, credit 0) | Первый blocker |
| --- | --- | --- |
| Select (W1/W4) | Fractional checked callee `select_unpredictable`: positive доходит до outer return и leak-check (Build `cf8405cc`); 8 fingerprint rows (`739f982d`); reviewed unbuilt кандидат 103a34 (ghost-CFG successors) | Dead-code отказ после leak-check, причина не установлена |
| Merge (W2/W3/W5) | Raw caller insert_tail: bounded exit0, 5 controls R19 совпали (`196e1b52`); exporter/decoder0, translator падает на synthetic region fixtures | Admission owned-NLL capture NEEDS_FIX (3 finding); original caller нуждается в borrow lifecycle |
| Network (W7/W8) | Exact N13 shape5 принят математически (`cbbe4b5f`), membership/missing negatives и 7 классификаторов; N9 regression | Order negative UNRUN, universal standalone timeout; W7/W8 ждут Select P2 |
| VeriFast | ManuallyDrop патч ac6a63d5, зелёный CI форка, upstream draft PR 1046 открыт 20.10 | Ответа upstream нет; новых «готовых» патчей не передано |

### 9.2 Что показал учёт

| Метрика (ledgers по 23.10) | Select | Merge | Network |
| --- | ---: | ---: | ---: |
| Окон всего / с нулём Builds | 30 / 1 | 32 / 3 | 2 / 0 |
| Builds / SUCCESS | 108 / 8 | 100 / 8 | 12 / 4 |
| Cloud-часов | 14,0 | 14,3 | 1,6 |
| Retired в окнах R16–R23 / R17–R22 / N3–N4 | 1400–3024 из 3600 | 589–3600 из 3600 | 407–1065 |
| Review-пакетов в последнем окне | 14 | 13 | ~6 |

Выводы: Cloud-бюджет не узкое место, узкое место — стена 120 минут и
церемония окна (регистрация, Brief-чтение fingerprint ~20 мин, 13–14 review на
окно). Четыре из последних 14 окон Select/Merge потеряны по процессным причинам
(Merge R19, R21; Select R18, R19); CORE от 23.10 это закрывает. Tool-цепочка
Merge ушла от stock 26.09 на 91 commit, Select накладывает proof-time overlays
translator; maintainer этой цепочки не видел — риск W10. Merge ушёл в
compiler-plumbing (owned-NLL facts в exporter) с UNESTABLISHED cross-stage
mapping — случай из §6 «пересмотреть способ получения compiler evidence».

### 9.3 Решения владельца от 23 октября

1. **Select — критический путь.** Следующее окно начинать с Build кандидата
   103a34 на тех же fingerprint rows; classifier-трек и omit-* pins — после
   чистого positive. Сразу после clean positive — mutable route P2 до
   `PUBLISHED`, затем W4.
2. **Merge — stop-loss.** Сначала три finding NEEDS_FIX без Cloud. Не более
   двух полных Cloud-циклов на owned-NLL diagnostic capture; при
   UNESTABLISHED mapping — source-level checked borrow adapter на существующей
   lifetime logic и W2 normal/unwind на raw caller.
3. **Network — один Build на order negative и universal 480, затем перенос
   R7** `has_efficient_in_place_swap` на baseline cd371e0 в stock-профиле;
   W8-подготовку не расширять до `PUBLISHED` P2.
4. **Maintainer — консолидация tool-цепочки** (Merge fork-ветки + Select
   overlays + ManuallyDrop) в одну integration-ветку форка с полным CI,
   отчётом о совместимости и trust ledger; без разработки proof-blockers.
5. **Режим окна (разовая практика).** Следующие задания всех четырёх owner'ов
   выданы без ограничения времени сессии: формальные deadlines в ledger
   (T0+4320 мин main, +60 мин closeout) нужны только tooling; окно закрывается
   по цели, бюджету или настоящей границе. Бюджеты: Select 21600 с, Merge
   14400 с, Network 10800 с; timeout 1200. Review — один раз на semantic
   candidate, не на каждый commit (CORE 2026-10-23). После этих заданий
   действует прежний default 120+30/3600, если владелец не решит иначе.
6. **Следующий разбор** — после закрытия этих заданий, не позднее 27 октября
   2026: новая строка истории, статус A1/A2/B1/B2, оценка stop-loss Merge и
   переноса R7.

Критерии ступеней §1 и веса не меняются. Индекс повышается только по evidence
закрытой ступени; расширенное окно и бюджет сами по себе его не меняют.

