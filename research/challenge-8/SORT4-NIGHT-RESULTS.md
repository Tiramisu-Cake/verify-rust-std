# Ночная итерация sort4_stable — 7 октября 2026

**Завершена по бюджету:12/12 NEW запусков, 2697 секунд job time (44 м 57 с из 180 мин).
Активных запусков нет.** Приёмка layout использовала ровно 2/2 своих запусков,
включённых в общий предел. Исторические бюджеты не переоткрывались.
[Авторизация и границы](SORT4-NIGHT-PHASE.md), [текущий checkpoint](STATUS.md),
[полный журнал с карточками, хешами инструментов и артефактов](EXPERIMENT-LOG.md).

## Что принято

- **Layout:** полный аудит и существующая матрица N2 прошли: исходные сравнения
  профилей, 18 дополнительных случаев, 7 metadata-контролей, 10 native-пар и 31 проверка
  классификатора/SpanData. Патч не менялся: SHA256
  `d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14`.
  Это приёмка узкого экспериментального fieldless-профиля, а не доказательство
  soundness всей модели или layout для всех T.
- **[Перестановка индексов](SORT4-INDEX-LEMMA.md):** stock VeriFast доказал точные
  формулы для всех 32 комбинаций пяти независимых Boolean-ответов: индексы 0..3,
  попарная различимость и каждый исходный индекс ровно один раз. Согласованность,
  чистота и упорядоченность компаратора не требуются. N4 доказательство принято;
  N5 исправил классификацию сохранённого отрицательного результата через hosted
  replay, без повторного verifier-запуска и изменения исходного evidence.
- **[Порядок и стабильность по рангам](SORT4-ORDER-LEMMA.md):** N5 проверил схему
  пяти сравнений для произвольных неизменных целочисленных рангов (39 statements).
  При равных рангах сохраняется порядок исходных вхождений. Минимальный контроль
  переставленных средних вхождений отклонён на целевом assertion.
- **[SWO→ранги](SORT4-SWO-BRIDGE.md):** N11 проверил полный конечный перенос
  произвольного строгого слабого порядка на четыре вхождения:16 Boolean-полей,
 4 диагонали и все 64 тройки законов. Число строгих предшественников лежит 0..3;
  less эквивалентно сравнению рангов, эквивалентность — равенству рангов.
  Все восемь вспомогательных лемм и application прошли (104 statements);
  контроль ошибочного использования ID вместо ранга отклонён на assertion19.
  N9/N10 выявили последовательные арифметические hotspots; проверяемые отдельные
  леммы устранили их без изменения законов, постусловий или stock-профиля.
- **[Диапазоны выбранных ячеек](SORT4-MEMORY-OPERATIONS.md):** N8 доказал
  containment и разделение source/dst для точных выбранных индексов и dst0..3
  при произвольном неотрицательном stride, включая 0 (24 statements).
  Ошибочная граница последней ячейки отклонена на целевом assertion.
  Ранее принятое generic H_align сохранено, повторно не запускалось.

Это даёт проверенные логические и геометрические компоненты для sort4.
Разные логические индексы ZST могут иметь одинаковые адреса. Числовые диапазоны
не дают provenance, permissions, validity или доказательство реальной операции.

## Что осталось открытым

**Единая чистая SWO-композиция подготовлена, но NOT RUN.** Последний N12 остановился
до VeriFast из-за моей ошибки wiring: ветка хеширования использовала отсутствующие
sort4-swo_network-lemmas.c/-negative.c вместо файлов composition. Положительная
композиция и её новый контроль стабильности не проверялись; это не доказательство
и не опровержение леммы. Подтверждённый дефект исправлен одной строкой,
`bash -n` и `git diff --check` прошли. Hosted-перепроверка **не выполнена**:
13-й запуск превысил бы разрешённый предел. Код леммы и отрицательного контроля
сохранён как непроверенный проект; отдельные N5/N11 результаты остаются принятыми.

**[Настоящий pointer select](SORT4-SELECT-CALLEE.md) заблокирован.** N6 сохранил
всё тело MaybeUninit/DropOnPanic/трёх intrinsic selections; export/decode/refinement
и source integrity прошли. Первый причинный VF-блокер — runtime
`MaybeUninit::new`, adapter21. Выбор указателя, provenance/permissions/frame и
normal/no-unwind постусловия не доказаны. Runtime std и его generic-сигнатуры
не менялись; if-подмена, доверенная заглушка и bound T:Copy не добавлялись.

**Memory/resource interface открыт.** Существующие copy-спецификации требуют
инициализированный destination и не обеспечивают нужный raw-scratch переход.
Обязательства reference creation/copy, optional bytes и padding отделены от
alignment arithmetic. Чистого operation-level отрицательного alignment-контроля
здесь нет; ручной assertion не выдан за автоматическое обнаружение UB.
Остаются actual T/callback correspondence, законные эффекты FnMut, сохранение
ключей для функционального применения и все пять полных panic/resource постов.
Общий safety-домен по-прежнему включает ZST, non-Copy, non-Freeze, raw scratch и
эффекты/паники компаратора. Фиксированный порядок и сохранение ключей относятся
только к функциональному результату. Полный Rust sort4 контракт **не доказан**.

## Следующие решения владельца

1. При желании завершить чистую композицию: отдельно разрешить новый небольшой
   stock-бюджет/этап для exact-SHA проверки исправленного swo_network harness,
   полного permutation+sorted/stable поста и адресного отрицательного контроля.
2. Для actual callee: сначала рассмотреть source-linked проверяемую возможность
   для MaybeUninit::new/union ownership. После неё отдельно проверять реальные
   intrinsics и DropOnPanic; историческая цепочка патчей не подключалась.
3. Для scratch: рассмотреть контракт raw destination/copy и ownership bridge,
   учитывающий optional bytes, padding/validity, сохранение source/frame и одного
   eventual owner. Это проект будущего этапа, без trusted implementation;
   нужны rationale, trust/admissibility review и regression gate до изменений.

RAPx CLOSED/NO-GO; B/C NOT RUN. Новых инструментов, axioms, assumed summaries,
изменений модели/prelude/refinement или внешней публикации не было.

## Запуски и состояние ветки

Все 12 запусков были ручными и GitHub-hosted, по одному relevant run одновременно.
Все неудачные запуски включены. Официальный stock VeriFast26.09/source809de459,
nightly2026-02-05/targetx86_64 и отдельный точный layout-профиль заморожены.

| Запуск | Actions / полный source SHA | Job, с | Результат |
| --- | --- | ---: | --- |
| N1 | [37547307118](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37547307118), 6bbd25a240ff4d2966c2dcdfed5d79936bc0638f |145| Ремонт harness; ошибка аннотации C++ |
| N2 | [37547890530](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37547890530), 3f5c9e3126a6db0599f1b989f03146e143342d04 |154| Полная матрица и аудит layout приняты |
| N3 | [37548195599](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37548195599), 03e23cbf56ff3d9e7d79923a0a1d8f15e88fe879 |23| Ошибка синтаксиса ghost include/block |
| N4 | [37548475221](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37548475221), fa74d92a120cc6990e5f65b94b31e72f2fb50d2f |44| Индексная лемма PASS; классификатор negative исправлен через replay |
| N5 | [37548811698](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37548811698), 6a12b4e39621eb057712f9084b809f86da6c9b77 |41| Порядок/стабильность по рангам и saved replay приняты |
| N6 | [37549040942](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549040942), aed1d970acb656cd29149241bf6720198895adac |32| Первый блокер actual callee: MaybeUninit::new |
| N7 | [37549385441](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549385441), b288370f1a1e6b34c26ef63764c73be2ced452c9 |40| Ошибка арифметического шага; адресный negative принят |
| N8 | [37549955948](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549955948), 9b25c410f6f69bdf5649aabf98481501824cec1e |27| Полная скалярная лемма диапазонов принята |
| N9 | [37550139106](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37550139106), 4d7aebcea01c58472e7ef03c4c1611a12d3c673d |1810| Таймаут равенства сумм; bridge не доказан, negative NOT RUN |
| N10 | [37553115842](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37553115842), 3ea303b682b63da3237a3d543ce3229b48c2848b |323| Равенство исправлено; таймаут строгого сравнения сумм |
| N11 | [37553933186](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37553933186), 3c3f0f338559675c5b4ce0859126bbedf8d9495c |30| Полный SWO→ранги мост и адресный negative приняты |
| N12 | [37554258065](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37554258065), 1803ad0be54a41d97059ad28a0400a7cf851aed3 |28| Harness: неверные имена файлов; verifier/композиция/negative NOT RUN |

N9 имел configured limit30 мин, но upload/cleanup добавили 10 с: фактические 1810 с
целиком учтены. После этого введены 120 с резерва внутри job cap и 300 с на ghost fixture;
таймауты остаются INCONCLUSIVE, зависимый negative отмечается NOT RUN.

Ветка `challenge-8/research`, репозиторий `Tiramisu-Cake/verify-rust-std`:
завершённые изменения и closeout отправлены; точный финальный commit — текущий HEAD.
Последний source SHA эксперимента указан в N12; исправление harness/closeout не
является proof run. Main `4771dd9894b28312edf40e16d6398628beaf498f` содержит только
минимальное расширение ручных workflow inputs, без слияния research history.
Логи, артефакты и generated std/build output не закоммичены; сервер использовался
только для редактирования/оркестрации. Новые эксперименты этим закрытым этапом
не разрешены. Отдельных незакоммиченных proof-драфтов не оставлено.
