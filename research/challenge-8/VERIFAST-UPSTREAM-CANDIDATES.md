# Кандидаты для отдельного проекта по улучшению VeriFast

Дата первичного обзора: 6 октября 2026. Источник — собственные исследования
Challenge 8 в `Tiramisu-Cake/verify-rust-std`, ветка `challenge-8/research`.
Заметка сохраняет побочные результаты для будущего самостоятельного проекта.
Создание нового репозитория, запуск экспериментов и публикация upstream PR
сейчас не выполняются. Основной план SmallSort находится в
[REASSESSMENT-2026-10-06.md](REASSESSMENT-2026-10-06.md).

## Что здесь означает разработка verifier

Помимо ghost-спецификаций actual std мы изменяли исходники самого VeriFast:
Rust spec parser, MIR translator, kernel lifetime bookkeeping и обход
выражений. Всего цепочка затрагивает четыре исходных файла VeriFast.
Она помогла пройти конкретные ограничения frontend и отдельные proof
obligations, но не дала полного generic insertion proof.

Часть изменений исправляет общий баг или добавляет полезную возможность.
Другие пока тесно связаны с выбранной ghost-разметкой SmallSort. Их следует
разделить на независимые contributions; общий успешный regression run не
доказывает soundness всех patches и не делает их готовыми к upstream.

## Версии и границы имеющихся проверок

- База исследований: VeriFast26.09, source
  `809de4596839b739dd999f9e462242c835e3af46`, Rust nightly2026-02-05.
- На момент read-only upstream обзора `master` указывал на
  `f76012fb518703b1d98e243ac4f487f16877cfcb` с nightly2026-09-25.
  Это источник для чтения, не проверенная нашими experiments версия.
- Наши patches собраны и проверялись на GitHub-hosted Actions в разных
  combined profiles. Самостоятельная проверка каждого candidate на текущем
  upstream master ещё не выполнена. Перед переносом повторно сверить HEAD,
  актуальность бага, открытые PR и совместимость toolchain/schema.
- Generic size-helper проверен release VeriFast; generic insertion/Drop
  использовали source-derived experimental build. См.
  [handoff](HANDOFF-2026-10-06.md) и [run log](README.md#run-log).

## Кандидаты и приоритеты

| Кандидат | Общая польза | Текущий статус / приоритет |
| --- | --- | --- |
| Address-taking после merge_fractions | Исправление остановки обхода оставшихся statements | Первый кандидат для небольшого bugfix PR |
| HRTB FnMut::Output | Instantiation реального compiler-origin higher-ranked associated-type равенства | Полезный frontend candidate; узкий matcher требует доработки |
| Tuple ownership | Владение tuple из владения его fields | Полезная возможность; hardcoded tuple2 требует согласования общей модели |
| Tracked ManuallyDrop reference | Reference initialization вместо неверно выбранного bare-address shortcut | Воспроизводимое ограничение; нужно определить общий принцип исправления |
| Local Drop call | Использование checked actual destructor contract при MIR cleanup | Исследовательский prototype; полный caller gate ещё не прошёл |
| Early ghost lifetime cut | Завершение локального ghost lifetime до внешней Rust brace | Semantic extension kernel; сначала архитектурное обоснование |

## 1. Первый кандидат: продолжение address-taking обхода

Patch: [verifast-address-taken.patch](verifast-address-taken.patch).
Контекст: [address notes](verifast-address-taken.md).
В `src/verify_expr.ml`, функция `stmt_mark_addr_taken`, ветка
`MergeFractionsStmt` вызывает `ass_mark_addr_taken`, но не вызывает
`cont locals`. Поэтому обход не замечает взятие адреса local после
`merge_fractions`, и local не получает обычную addressable storage модель.
Наше исправление добавляет ровно `cont locals`; новых ownership/lifetime
правил оно не вводит.

На просмотренном upstream HEAD эта ветка всё ещё без continuation:
[исходник на точном SHA](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/verify_expr.ml#L1556).
Это результат чтения кода, не отдельный before/after run на master.

В [37415731049](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37415731049)
scalar positive после merge проверен с exact result7. ManuallyDrop case
остановился на следующей reference-initialization obligation; оставшийся
negative case первоначальной address suite не был выполнен.
Позднее combined profile с отдельным tracked-reference patch прошёл пять
reference fixtures в
[37417173472](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37417173472).
Эти результаты не заменяют standalone regression suite для одного address fix.

Первый переносимый deliverable: минимальный reproducer без SmallSort и прочих
patches, failure на baseline, pass после одной строки исправления, проверка
отказа чтения без permission и соответствующая upstream suite. За основу
reproducer можно взять scalar case из
[verifast-address-regressions.rs](verifast-address-regressions.rs).
Расположение теста и язык выбрать по принятой upstream практике.

## 2. Frontend candidates для последующих отдельных contributions

**HRTB.** [Patch](verifast-fnmut-hrtb.patch) и
[notes/fixtures](verifast-fnmut-hrtb.md) связывают compiler-origin
`for<'a,'b> FnOnce::Output=bool` с конкретным `FnMut::call_mut`.
Штатный translator отбрасывал projection predicates с bound regions.
Наш matcher узко принимает два shared references одного generic T,
Boolean output и совпадающие ghost/method lifetimes; содержит диагностические
`CHALLENGE8_*` traces. Все восемь matcher guards прошли в
[37410979109](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410979109).
Они намеренно не имеют callback ownership и завершаются ожидаемыми errors:
это проверки guards, не восемь successful callback proofs.
До upstream нужны самостоятельный positive proof, guards от ложных равенств,
обоснование instantiation/scoping и выбор между общим механизмом и честно
ограниченной поддержкой. Учесть изменения projection handling в новом master;
не переносить patch механически и убрать проектные traces из итогового fix.

**Tuple ownership.** [Patch](verifast-tuple-own.patch) и
[notes](verifast-tuple-parser.md) делают own canonical tuple2 прозрачным:
`T1.own(t, v.0) &*& T2.own(t, v.1)`. Это позволило собрать actual FnMut Args
из двух owned references. Сейчас parser узнаёт точное имя `std_tuple_2_`
и имена parameters `T1,T2`; это специализированный experiment.
До переноса нужны standalone generic close/open tests, non-Copy fields,
согласованность own/share/full_borrow_content и unchanged behavior других
tuples/structs. Предложенные в notes tuple1/3/4 regressions не считать уже
выполненными. Общую форму поддержки tuples сначала согласовать с моделью.

**ManuallyDrop references.** [Patch](verifast-manually-drop-ref.patch) и
[notes](verifast-manually-drop-ref.md) направляют immutable shared reference
к exact ManuallyDrop place через обычный `create_ref`, когда no-drop shortcut
раньше выдавал bare address без нужного `ref_initialized`.
В37417173472 прошли два scalar/i32 positives и три negatives: missing
precreation, initialization и read permission. Actual generic insertion
продвинулся до guard/first shift, но whole function не доказана.
До переноса нужны независимый reproducer и решение, является ли exact-type
исключение правильной общей границей. Generic interior mutability и полный
normal/unwind reference lifecycle текущими i32 fixtures не установлены.

## 3. Исследовательские extensions, пока не готовые fixes

**Local Drop.** [Patch](verifast-local-drop-call.patch) и
[caller gate](verifast-drop-caller-gate.md) переводят bare-local MIR Drop
в вызов annotated actual method в том же unit. Ограничения включают один
generic parameter и три trivial fields src/dst/len; projected places
остаются на baseline. В37423762729 новый код упал в HRTB regression из-за
нашего nested-match bug. Caller fixtures не запускались. Исправление этого
bug исправит наш prototype, а не существующий upstream код.
До contribution нужны полный gate, normal/cleanup CFG evidence, проверка
callee/caller contract integrity и общий design для destructor/field glue.
Отдельный actual Drop body proof37419989766 не доказывает этот lowering.

**Early lifetime cut.** [Patch](verifast-end-lft-binding.patch) и
[notes](verifast-end-lft-binding.md) меняют translator и kernel: сокращают
scope локального ghost lifetime, возвращают reserved token fraction,
проверяют escapes и восстанавливают type-bound metadata.
Двенадцать scope fixtures прошли на combined profile; dedicated malformed
CFG-ingress fixture остаётся непроверенным. Нужны обоснование soundness,
разбор каждого exit/CFG case и сравнение с вариантом штатного borrow model.
Не выдавать необходимость cut для нашей разметки за необходимость для всех
корректных proofs. Перенос как обычного bugfix сейчас преждевременен.

## Как выделить отдельный проект

1. Начать с address-taking fix; один candidate, один owner, один hosted
   experiment за раз. Подготовить отдельную ветку от актуального VeriFast.
2. Переносить каждый patch вместе с минимальным reproducer, expected
   before/after result, границами поддержки и проверяемыми negative cases.
   Не переносить общую SmallSort proof chain как единую feature.
3. Для каждой версии сохранять base/source SHA, toolchain, patch и binary
   hashes, полные logs, suite outcome и время сборки отдельно от verification.
   Source/build failure, verifier crash и посторонний error не считать
   intended negative result.
4. Выполнять standalone positive/negative checks и релевантную upstream suite
   на GitHub-hosted runners. На сервере по-прежнему только чтение, editing,
   git/gh и разрешённые static checks; build/test/verifier запуск запрещён.
5. Только после готового проверенного candidate переходить к upstream PR.
   Внешние публикации требуют отдельного указания владельца.

Новый проект должен сохранять разделение общих bugfixes, ограниченных frontend
features и semantic kernel extensions. Принятие отдельного исправления
upstream уменьшит объём нашего experimental fork, но само по себе не закроет
Challenge 8 и не подтвердит оставшиеся patches.
