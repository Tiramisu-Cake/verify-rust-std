# П-1/П-2 — инвентарь пакета SmallSort

Дата: 2026-10-28. Документальная сессия W3-SUB; сборки $0.
**Результат: предлагается отделить 14 690 строк исследовательского пакета;
в proof-коде найдено 377 строк неиспользуемых помощников и 10–14 строк
потенциально устранимых повторов.** Это предложения для П-3/П-5,
а не выполненное сокращение или новая приёмка доказательств.

## 1. Срез, метод и границы

- Задание: `TASK-sub-p12.md`; дополнение R8 прочитано целиком на
  `a03f8c3acbd87ed5c418a52561e69c63f57e94ea`.
- Исходник всех координат: **S_M = ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad**;
  upstream **c0bd09c354a50bf9fe4dcc7cc5f9c34503658479**.
  Метод: `git diff --numstat BASE...S_M`; считаются добавленные физические
  строки вместе с пустыми строками и комментариями. Удалений нет.
- Основной реестр: [X0](EXT-X0-BASELINE-2026-10-28.md), pin
  **661a5a1afda875d2c0273fe5847692d28931d51b**, §6.1–6.2, строки 377–1075.
  Требования и раскрытие прочитаны на **b6b480cc**, только для чтения.
  Их позднейшие длины не подменяют numstat документов S_M.
- Аудит сравнения использован только как таблицы чисел и свойств:
  `d70d85eb:research/challenge-8/CH8-PR694-AUDIT-2026-10-27.md:17–71`.
  Код, diff и ветки PR #576/#678/#694/#701 не открывались.
- Все приведённые результаты Kani — **source-reported**, взяты из X0,
  W3-REQUIREMENTS и W3-DISCLOSURE-DRAFT; независимого proof credit здесь нет.
  Source entry, SUCCESS caller и наличие контракта — разные свидетельства.
  Bounded evidence не превращается в full proof; ограниченное B4 не anylen.
- В этой сессии изменяется только этот файл. `library/`, исторические отчёты,
  реестр X0 и evidence не изменяются. Ни сборок, ни локальных proof-команд,
  ни запросов запуска/статуса CI нет. Commit и push разрешены заданием;
  внешний PR не создаётся.

Ссылки на наш код закреплены на S_M:
[smallsort.rs](https://github.com/Tiramisu-Cake/verify-rust-std/blob/ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad/library/core/src/slice/sort/shared/smallsort.rs),
[дерево модулей](https://github.com/Tiramisu-Cake/verify-rust-std/tree/ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad/library/core/src/slice/sort/shared/smallsort).
Далее `merge.rs`, `network.rs`, `assembly.rs`, `correct.rs`, `mutations.rs`,
`smoke.rs`, `uninit.rs` означают файлы в
`library/core/src/slice/sort/shared/smallsort/kani_k1/`;
`kani_k1.rs` — файл непосредственно в `smallsort/`. Запись `file:line`
всегда относится к этому pin, не к будущей редакции.

## 2. П-1: все 55 файлов

«В PR» означает исходник, включая opt-in контроли, которые запускаются
отдельно от обычного положительного набора. «Отдельное приложение» —
материал рецензента с устойчивыми ссылками. «Остаётся в исследовательской
ветке» означает сохранение истории и воспроизведения по pin, а не удаление
архива. Решения ниже предлагаемые. Назначение «контроль» относится
к проверяющему доказательства коду; организационные задания — «история».

| Путь | +строк | Назначение | Предложение, причина и зависимости |
| --- | ---: | --- | --- |
| `.circleci/config.yml` | 74 | инфраструктура | Остаётся в исследовательской ветке: экспериментальная CircleCI lane, зависит от stage runner/request. |
| `AGENTS.md` | 13 | история | Остаётся в исследовательской ветке: старые инструкции worktree/исполнителей; не часть результата. |
| `CLAUDE.md` | 20 | история | Остаётся в исследовательской ветке: старые инструкции worktree/исполнителей; не часть результата. |
| `library/core/Cargo.toml` | 2 | инфраструктура / контроль | В PR: две строки check-cfg для `kani_smallsort_controls`; нужны opt-in исходникам, это не отчёт. |
| `library/core/src/slice/sort/shared/smallsort.rs` | 119 | доказательство | В PR: восемь контрактных целей и Kani-подключение; зависит от helpers merge/network, не менять runtime. |
| `library/core/src/slice/sort/shared/smallsort/kani_k1.rs` | 15 | доказательство / инфраструктура | В PR: граф модулей; ownership-комментарий заменить позднее, cfg mutations сохранить. |
| `library/core/src/slice/sort/shared/smallsort/kani_k1/assembly.rs` | 166 | доказательство / контроль | В PR: Пары оригинал/мутант и stable-ZST; зависит от mutations и `uninit::zst_aware_less`. |
| `library/core/src/slice/sort/shared/smallsort/kani_k1/correct.rs` | 230 | доказательство / контроль | В PR: 21 ordinary L2 и 18 opt-in; зависит от merge helpers и точных insert/merge prerequisites. |
| `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs` | 2077 | доказательство / контроль / диагностика | В PR: Центр спецификаций, callee/caller и Drop; удалять только обоснованные неиспользуемые части §5. |
| `library/core/src/slice/sort/shared/smallsort/kani_k1/mutations.rs` | 250 | контроль | В PR: Тела пяти мутантов нужны assembly; отсутствие собственных proof entries не делает файл ненужным. |
| `library/core/src/slice/sort/shared/smallsort/kani_k1/network.rs` | 1905 | доказательство / контроль / диагностика | В PR: Swap, сети, insertion, C3/O3 и их контроли; зависит от merge и uninit helpers. |
| `library/core/src/slice/sort/shared/smallsort/kani_k1/smoke.rs` | 51 | доказательство / контроль | В PR: Обычный C3 predicate плюс smoke/expected-fail; нужны оба режима. |
| `library/core/src/slice/sort/shared/smallsort/kani_k1/uninit.rs` | 428 | диагностика / контроль / средство воспроизведения | В PR: Сохранить: helper используется ordinary assembly; 59 diagnostics opt-in, U-1 unsupported раскрыть, не выдавать за proof. |
| `research/challenge-8/kani-k1/EXPERIMENT.md` | 216 | средство воспроизведения / история | Остаётся в исследовательской ветке: Исторический протокол lane/pin/flags; приложение обязано вынести необходимые команды и предпосылки, сохранить ссылку на протокол. |
| `research/challenge-8/kani-k1/INFRA-REVIEW.md` | 34 | отчёт / история | Остаётся в исследовательской ветке: Аудит старой инфраструктуры; не основание свойств S_M. |
| `research/challenge-8/kani-k1/NIGHT-2026-10-26.md` | 47 | история | Остаётся в исследовательской ветке: Ночное окно и полномочия; не инструкция рецензенту. |
| `research/challenge-8/kani-k1/R5-WAVE1.md` | 148 | история | Остаётся в исследовательской ветке: Правила прежней волны; её результаты цитировать по pin. |
| `research/challenge-8/kani-k1/R6-WAVE2.md` | 100 | история | Остаётся в исследовательской ветке: Процесс прежней волны; не часть proof API. |
| `research/challenge-8/kani-k1/R9-W2-NETWORK-P1-2026-10-27.md` | 35 | отчёт | Остаётся в исследовательской ветке: Review конкретного старого source; приложение ссылается на нужный вывод, не копирует весь процесс. |
| `research/challenge-8/kani-k1/REPORT-K1-2026-10-26.md` | 190 | отчёт / история | Остаётся в исследовательской ветке: Сводка ранних опытов; сохранить происхождение и resource ограничения. |
| `research/challenge-8/kani-k1/REPORT-W1-2026-10-26.md` | 115 | отчёт / история | Остаётся в исследовательской ветке: Сводка W1; точные основания доступны по pin. |
| `research/challenge-8/kani-k1/REPORT-W2-2026-10-27.md` | 194 | отчёт / история | Остаётся в исследовательской ветке: Сводка W2; итоговые claims сверяются с X0/W3, история не теряется. |
| `research/challenge-8/kani-k1/RESULT-ext.md` | 152 | отчёт / история | Остаётся в исследовательской ветке: Resource-опыты вне ordinary CI credit; ссылка для раскрытия. |
| `research/challenge-8/kani-k1/RESULT-merge.md` | 3853 | отчёт / история | Остаётся в исследовательской ветке: Полный журнал merge; приложению нужны ссылки на выбранные точные результаты. |
| `research/challenge-8/kani-k1/RESULT-network.md` | 3009 | отчёт / история | Остаётся в исследовательской ветке: Полный журнал network; сохранить структурные доводы и ревью по pin. |
| `research/challenge-8/kani-k1/RESULT-w3-l1.md` | 1970 | отчёт / история | Остаётся в исследовательской ветке: Подробные измерения/контроли/интеграция; краткий индекс в приложении ссылается сюда. |
| `research/challenge-8/kani-k1/RESULT-w3-l1u.md` | 542 | отчёт / диагностика | Остаётся в исследовательской ветке: Классификация ZST/U-1; нужна ссылка и точное раскрытие unsupported. |
| `research/challenge-8/kani-k1/RUN-REQUEST.gcb-smoke.json` | 21 | средство воспроизведения / контроль | Остаётся в исследовательской ветке: Одноразовый GCB smoke с controls; зависит от экспериментального runner/schema. |
| `research/challenge-8/kani-k1/RUN-REQUEST.json` | 23 | средство воспроизведения | Остаётся в исследовательской ветке: Только три интеграционные гармоники; не воспроизведение полного S_M. |
| `research/challenge-8/kani-k1/RUN-REQUEST.smoke.json` | 21 | средство воспроизведения / контроль | Остаётся в исследовательской ветке: Smoke-запрос lane, не положительный proof-набор. |
| `research/challenge-8/kani-k1/TASK-ext.md` | 62 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `ext`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-merge.md` | 211 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `merge`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-network.md` | 46 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `network`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-night-merge.md` | 37 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `night-merge`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-night-network.md` | 31 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `night-network`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-w1-merge.md` | 44 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `w1-merge`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-w1-network.md` | 31 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `w1-network`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-w2-merge.md` | 49 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `w2-merge`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-w2-network.md` | 56 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `w2-network`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-w3-doc.md` | 80 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `w3-doc`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-w3-l1.md` | 137 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `w3-l1`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-w3-l1u.md` | 59 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `w3-l1u`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/TASK-w3-l2.md` | 100 | история | Остаётся в исследовательской ветке: отдельное задание/полномочия этапа `w3-l2`; сохранить происхождение работ, не переносить как требования к рецензенту. |
| `research/challenge-8/kani-k1/W3-DISCLOSURE-DRAFT.md` | 237 | отчёт / средство воспроизведения | Отдельное приложение: англоязычные домены, trust ledger, controls и ограничения; сверить final CI и подготовить достаточный вход воспроизведения. |
| `research/challenge-8/kani-k1/W3-REQUIREMENTS.md` | 157 | отчёт | Отдельное приложение: таблица требований и ссылок на результаты; согласовать с X0 и final CI, не выдавать за независимую проверку. |
| `research/challenge-8/kani-k1/W3-RULES.md` | 106 | история | Остаётся в исследовательской ветке: Правила исполнителей и бюджета; не инструкция внешнему рецензенту. |
| `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` | 38 | инфраструктура | Остаётся в исследовательской ветке: Экспериментальная Cloud-конфигурация; зависит от GCB runner/пула, не штатный PR check. |
| `research/challenge-8/kani-k1/gcb/owner-setup.sh` | 101 | инфраструктура | Остаётся в исследовательской ветке: Создание ресурсов владельца; не требуется для штатного воспроизведения Kani. |
| `research/challenge-8/kani-k1/github-lane/smallsort-kani-k1.yml` | 165 | инфраструктура / средство воспроизведения | Остаётся в исследовательской ветке: Неактивный workflow-шаблон вне .github/workflows; зависит от Python runner, request и pin; включать лишь при доказанной нужде. |
| `research/challenge-8/kani-k1/tools/circleci-k1.sh` | 157 | инфраструктура | Остаётся в исследовательской ветке: CircleCI stage runner; зависит от lane/credentials, не нужен штатному PR. |
| `research/challenge-8/kani-k1/tools/gcb-k1.sh` | 192 | инфраструктура | Остаётся в исследовательской ветке: GCB stage runner; зависит от Cloud-конфигурации и project/pool. |
| `research/challenge-8/kani-k1/tools/k1.sh` | 212 | инфраструктура | Остаётся в исследовательской ветке: Диспетчер CircleCI/артефактов; история экспериментов, не proof dependency. |
| `research/challenge-8/kani-k1/tools/k1g.sh` | 264 | инфраструктура | Остаётся в исследовательской ветке: Диспетчер Kani Cloud lane; остаётся интерфейсом исторической lane, не включать ради основного PR. |
| `research/challenge-8/kani-k1/tools/kani_k1.py` | 961 | средство воспроизведения / инфраструктура | Остаётся в исследовательской ветке: Request/parser/gate/ресурсы/ledger экспериментальной lane; GH-шаблон зависит от него, штатный Kani — нет. |
| `research/challenge-8/kani-k1/tools/test_kani_k1.py` | 774 | контроль / инфраструктура | Остаётся в исследовательской ветке: Синтетические тесты runner/parser, зависят от kani_k1.py; не доказательства SmallSort. |

### 2.1. До/после по одной методике

| Состав | Файлов | +строк / −строк | Статус |
| --- | ---: | ---: | --- |
| S_M относительно upstream | 55 | 20 327 / 0 | Фактический numstat |
| Предлагаемый основной PR: 9 SmallSort + Cargo.toml | 10 | 5 243 / 0 | Проекция выбора файлов без изменения содержимого |
| Отдельное приложение: два W3-документа S_M | 2 | 394 / 0 | Проекция; не длина их поздней редакции b6b480cc |
| Остаётся в исследовательской ветке | 43 | 14 690 / 0 | Проекция; материалы сохраняются |
| PR + приложение | 12 | 5 637 / 0 | 20 327 − 14 690; сокращение пакета на 72,27% |

S_M′ не создан: фактического «после» пока нет. В П-3 нужно повторить
`git diff --numstat BASE...S_M′`, а не сравнивать `wc` с numstat.
394 строки приложения — сохранённые входные файлы, не обещание окончательной
длины: финальный документ должен содержать точный pin, команды штатного
runner, перечень ordinary и отдельный режим controls с ожидаемыми checks,
карту callee/caller и устойчивые ссылки на историю. Входные указания:
`W3-DISCLOSURE-DRAFT.md:123–159` на b6b480cc, `EXPERIMENT.md` на S_M.
Зависимости этого входа следует проверить до исключения custom tooling;
если штатного runner недостаточно, П-3 обязан добавить и посчитать минимальный
replay-компонент. Число строк нового входа здесь не выдумывается.

Выбор сохраняет весь исходный диагностический/контрольный код внутри PR,
включая 250 строк mutants и 428 строк uninit. Их исполнение отделено cfg.
Так получается проверяемый исходный состав для П-3 без молчаливой потери
отрицательных контролей. Перенос общего helper из uninit обязателен, если
позднее предлагается вынести этот файл: `assembly.rs:152` вызывает
`uninit::zst_aware_less`, как и `network.rs:1605`.

Исторический срез **49f7e73b3817db6e53da3d2cf792c2919e174d4c**:
56 файлов / +20 508. Его единственное дополнение к S_M — workflow
координатора `.github/workflows/smallsort-kani-k1.yml`, +181.
Этот 56-й файл учтён отдельно и в предлагаемую подачу не включён.

## 3. П-2: инвентарь и правила чтения карты

| Файл | Добавлено | Ordinary | Controls-cfg |
| --- | ---: | ---: | ---: |
| smallsort.rs | 119 | — | — |
| kani_k1.rs | 15 | — | — |
| merge.rs | 2 077 | 114 | 77 |
| network.rs | 1 905 | 206 | 109 |
| assembly.rs | 166 | 13 | 5 |
| correct.rs | 230 | 21 | 18 |
| mutations.rs | 250 | 0 | 0 |
| smoke.rs | 51 | 1 | 2 |
| uninit.rs | 428 | 0 | 59 |
| **Итого** | **5 241** | **355** | **270** |

Числа entries взяты из X0:390–410: 625 уникальных module/name,
177 safety +178 correctness в ordinary. Все entries наследуют `cfg(kani)`;
C означает дополнительный `kani_smallsort_controls`, O — ordinary.
270 C включают положительные диагностические и снятые опыты, а не только
negative controls. Для U-1 дополнительно нужен `-Z uninit-checks` в запросе;
cfg сам по себе его не включает. Атрибуты по тексту не пересчитываются
в доказанные свойства; target-specific `kani list` не запускался.

В таблицах ниже **O/C — число строк X0, чей Item line попадает в диапазон**,
а не число типов или всех инстанциаций const-N. Нулевые строки — helpers,
комментарии и спецификации, на которые ссылаются семьи с entries.
Полный список expanded names, точных длин и cfg остаётся в X0 §6.2;
здесь он сгруппирован по реализации, не заменён новым реестром.
Диапазоны каждого нового модуля покрывают все его строки ровно один раз;
для существующего smallsort.rs учитываются только строки добавлений.

### 3.1. smallsort.rs и kani_k1.rs

| Координаты | Строк | Семейство → свойство → домен → entries/контроли |
| --- | ---: | --- |
| smallsort.rs:380–428 | 49 | Swap: distinct, same-allocation, readable/writable, modifies двух позиций, bitwise pre-snapshot и результат сравнения; generic T/F, фактические K9s типы/allocations из X0. `swap_if_less_*`, K9s exactN; R11 same-index и K15 mutant swap. Не считать второй comparator вызов общим arbitrary-bool контрактом. |
| smallsort.rs:469–478,528–537 | 20 | sort9/sort13: sorted prefix и probe multiplicity; входной slice len9/13..17, modifies prefix9/13. X0 `sort9_*`/`sort13_*` и composition callers; callee swap/frame и R11 обязаны совпасть по типу/геометрии. |
| smallsort.rs:605–610 | 6 | insert_tail: sorted prefix, same-allocation begin/tail, inclusive modifies, sortedness + probe count. Хвостовые доказательства merge/network/L2; R11 `l2_r11_insert_tail`, K15 insert. Контракт не ограничен длиной17. |
| smallsort.rs:649–660 | 12 | insertion: len2..17, offset1/9/13 по длине, sorted prefix, whole-slice sortedness/permutation. `insertion_o*`, `insertion_inv_o1_u64`; узкий контракт несовместим с direct17/20 offset1, не усиливать caller assume. |
| smallsort.rs:693–698 | 6 | sort4: четыре чтения/записи, disjoint, sortedness/count; u64/b16 ordinary contract и arbitrary proofs, b85 timeout C. |
| smallsort.rs:750–756 | 7 | sort8: три pairwise-disjoint региона8, modifies dst и scratch; C `sort8_*`, верхние general callers. Не подменять произвольной иной allocation. |
| smallsort.rs:854–864 | 11 | Merge: len2..32, dst/frame/disjoint и sorted halves, sortedness + full-value count; O callee u8/u64 и composition GS; R11 merge и K15 consumption. `merge_up/down` собственных контрактов не имеют. |
| smallsort.rs:973–980 | 8 | cfg(kani), import и модуль; runtime вне Kani не меняется. |
| kani_k1.rs:1–15 | 15 | Module graph: merge/network/smoke/uninit/correct/assembly, mutations только C. Строки3–5 ownership-инструкции требуют замены описанием назначения; helpers uninit нужны O. |

Сумма добавлений smallsort.rs: 49+20+6+12+6+7+11+8 =119.

### 3.2. merge.rs — 2 077 строк

| Координаты (+строк) | Семейство → свойство | Типы / длины / регионы | X0 entries и зависимые контроли; O/C |
| --- | --- | --- | --- |
| `merge.rs:1–36` (+36) | Обоснование модели, imports | Probe encoding permutation; cfg/dead_code allowance | Общее основание callee/caller; не самостоятельная гармоника; **0/0** |
| `merge.rs:37–178` (+142) | Probe bytes, specialization и stateless comparator adapter | 128-byte probe, align16; целые, массивы16/85; сравнение полных байтов | Все probe proofs; light helpers остаются из-за `bm_u64_len32_plain`; **0/0** |
| `merge.rs:179–302` (+124) | Count/sortedness, light/quantified варианты и disjoint predicate | Область≤32 для unroll; произвольный полный probe; валидные initialized регионы | Контракты SS; `k1_perm_l` реально вызывается в :906; quantified helpers нужны plain C и `network::k1_ins_inv` до его удаления; **0/0** |
| `merge.rs:303–362` (+60) | Tail/sort4/sort8/dst preconditions | Inclusive begin..tail; фиксированные4/8 и len merge; no-alias/writability | R11 insertion/merge, sort4 и caller prerequisites; активная спецификация; **0/0** |
| `merge.rs:363–628` (+266) | Историческая цепочка merge invariants — **не вызывается** | Предлагались arithmetic/cursor/frame/consumption/probe формулировки≤32 | Ни одной X0 entry; «ATTACHED» в :438 устарело; доказательство неиспользования §5; **0/0** |
| `merge.rs:629–640` (+12) | **Активный** halves-sorted predicate | Две половины floor/ceil(len/2), len≤32, `k1_sorted_u` | SS:861 requires; сохранить отдельно от неиспользуемого блока; **0/0** |
| `merge.rs:641–719` (+79) | Исторический K1BmInv dispatcher — **не вызывается** | Default full; u16 trivial, i16 core-only | Только dead chain; не prerequisite ordinary или C; **0/0** |
| `merge.rs:720–753` (+34) | Чистые concrete comparators | u8/i32/u64 по x>>1; b16/b85 по первому байту; lt_u16/i16 не используются | Разные key и payload сохраняют независимость permutation; не заменять default `<` без доказательства; **0/0** |
| `merge.rs:754–785` (+32) | by_len и общие тела callee proofs | `bm_len<T,N>` exact arrays, insert_tail region до N−1 | Используют последующие callee O/C, сохранять const-N развёртку; **0/0** |
| `merge.rs:786–963` (+178) | Начальные scaling/toy/plain/R11 опыты | Merge u64 2..8/2..32 и fixed12/16/20/24/28/32; toy32; plain32; R11 len4 | `bm_u64_*`, `insert_tail_u64_upto8`, `toy_loop_contract`, `r11_control_bm_requires`; C, не новые принятые клетки; **0/14** |
| `merge.rs:964–1174` (+211) | sort4/8, typed insertion/merge contract templates и arbitrary sort4 | sort4 N4 u64/b16 O, b85 C; sort8 N8; typed tail 2..16; merge2..32 | `w3_sort4_{arbitrary,contract}_{u64,b16}`; C `sort4_*`,`sort8_*`,`insert_tail_int/bytes`,`bm_*`; R11/K15 отдельно; **4/17** |
| `merge.rs:1175–1283` (+109) | Generic top-level composition и trait route adapters | General exact arrays0..32; stable external scratch48; transparent non-Copy W1GeneralU64 | `general_*`, `general_u64_len32` C и shared bodies для GS O; verified merge prerequisite exact type/N/region; **0/5** |
| `merge.rs:1284–1534` (+251) | Arbitrary comparator safety helpers и sensitivity controls | Volatile чтение обоих аргументов; u64 и non-Copy routes; scratch48; N≤32; отдельные invalid operations | O формируются ниже; C `w1_control_a_*`, `w2_control_a_*`, четыре `w2_c5_*`; cut только ord-violation, не unwind; **0/8** |
| `merge.rs:1535–1812` (+278) | O1 exactN и callee/caller correctness instances | Safety u64 каждый N2..32, три general/trait routes; merge u8/u64 N2..16; GS/fallback выбранные точные N≤16 | `w2_a_*`, `w2p2_bm_*`, `w2p2_gs_*`, `w2p2_fallback_*`; C R11 u8/u64; cfg каждой invocation по X0; **95/16** |
| `merge.rs:1813–1837` (+25) | Разделённый fallback и extended merge | Fallback u8/u64 N8, u8 N9; merge u8 N20/24 | `w2night_fallback_u8_len8` O; остальные named night probes C; не удалять все night по названию; **1/4** |
| `merge.rs:1838–2015` (+178) | Normal-return Drop + identity permutation, два разных checks | W2NightDrop key:u64/tag:u8, padding; low2/4/8 и upper2/4/8/16 O; upper24/32 C; stable scratch48 | `w2night_drop_*_{count,perm}`; C duplicate-tag/extra-drop и reachability; счётчик не заменяет метки и не доказывает unwind; **14/8** |
| `merge.rs:2016–2077` (+62) | E-2 extended insertion safety | u64 backing exact16..20, все offset1..N через const dispatch | `ext_b4_u64_n16`…`n20` C; resource evidence вне ordinary CI; основной B4 см. network W3; **0/5** |

Итог по X0: 114 O /77 C. В `merge.rs:1723–1812` GS O:
u64 N0..12 и16, u8 N0..13 и16; GS C: u64 N13..15 и u8 N14/15.
Последние две u8 клетки добавлены ordinary именно в correct.rs, а не
переименованы в старой семье. Общая fallback O в этом блоке: N0..7,
каждое имя выбирает u8/u64; N8..16 старого объединённого варианта — C.
Отдельный u8N8 O в :1813–1837 и L2 u64N8..16/u8N9..16 дополняют
итоговый домен, не меняя старые cfg (X0:523–611).
Для GS ordinary факт наличия stub не отменяет
R4: u8 N14/15 на scratch48 опирается на явно раскрытый аналитический
перенос D-B4; это не отдельный machine proof merge на scratch48.

### 3.3. network.rs — 1 905 строк

| Координаты (+строк) | Семейство → свойство | Типы / длины / регионы | X0 entries и зависимые контроли; O/C |
| --- | --- | --- | --- |
| `network.rs:1–80` (+80) | Swap contract probes, equality/frame helpers | u8/i32/u64 backing4, любые различные a,b<4; key-order x>>1 | `swap_if_less_*` O; C `r11_control_swap_if_less_requires`; callee для verified swap stubs; **3/1** |
| `network.rs:81–235` (+155) | sort9/sort13 alternative contract/permutation encodings | Backing17, slice len9/13..17, prefix9/13 + suffix frame; u8/i32/u64; 0..3 только в 01 опытах | `sort9_*`,`sort13_*`, real/stub/01/perm C; не смешивать reduced-domain C с full-width ordinary; **0/22** |
| `network.rs:236–487` (+252) | Insertion invariant experiment, offset contracts и tail geometry | Offsets1 при2..8,9 при9..12,13 при13..17; u8/i32/u64; prefix/interior backing17 | `insertion_inv_o1_u64`,`insertion_o*`,`network_upto17_*`,`insert_tail_net_*`, prefix/region C; unused helper239–264, но control266–282 исполняется; **0/18** |
| `network.rs:488–760` (+273) | CD-2 network safety и contract/band/fixed diagnostics | u64 no-merge0..17; merge18..32 через const cases; typed selected lengths; реальные/verified-stub варианты | `w1_network_o1_nomerge_u64` O; band/fixed/direct и K9 retry C; сохранять различие tail-stub и actual tail; **1/28** |
| `network.rs:761–996` (+236) | Interior-mutable comparator и tags experiments | Cell<K13Tagged>, key/tag:u8; defaults0..16; insertion1..20 все offset; permutation subset0..4 | `k13_routes_*`,`k13_insertion_*`,`k13_safety_all`,`k13_small_permutation` C; O3 ordinary ниже, это не Cell<i32>; **0/6** |
| `network.rs:997–1278` (+282) | O1 merge safety, C3 type/route и reachability | u64 N18..32 по группам; G={0,1,2,7,8,15,16,17,31,32}, S={0,1,2,15,16}, U={8,9,12,13,17,18,31,32}; точные типы ниже | `w2_network_o1_a_*`,`w2_k16_*`, `w3_k16_i32_freeze`; C ord controls/ZST/u128-hi; не считать произвольный bool функциональной корректностью; **50/7** |
| `network.rs:1279–1545` (+267) | B4/O3 safety и exact offset groups | u64 и Cell<K13Tagged>; N1..20, const offset1..N; W3 N15..20 разбиты на группы с cover каждого offset | `w2_k11s_*`,`w2_o3s_*`,`w3_b4_*`,`w3_o3_*`; 28 paired invocations →56 O; широкие/старые варианты C; только bounded safety; **70/18** |
| `network.rs:1546–1735` (+190) | K10 sortedness/route permutation и C3 swap contract | K10 u8/u64 actual trait N0..17 с default `<`; прямой multiset только N<9; insertion suffix отдельно; K9s exact2 | `w2p2_k10_*`,`w2p2_k10_perm_*`,`w2p2_k9s_*`; u64 sortedness15..17 C, u8 sortedness16/17 не закрывает permutation; K9s ZST C; **46/8** |
| `network.rs:1736–1897` (+162) | K9s symbolic indices, K8r shifted region и O3 tags | u8/u64 exact backingN9..17; u64 backing17 start1..15, tail start+1..16 (120 регионов); Cell tags N2/3/4 | 18 swap/frame O, 15 K8r O, 3 O3 tag O; R11 swap и K15 checks чувствительности отдельно; **36/0** |
| `network.rs:1898–1905` (+8) | Мутант на существующем K10 witness | u8 exactN10; changed presorted_len | `k15_mutant_existing_k10_presorted_len` C; вызывает mutations body, не замена положительной гармоники; **0/1** |

Итог: 206 O /109 C. Точная C3 safety-матрица X0:130–143:
`u8`: stable G / unstable U; `i32`: обе trait-точки S;
`u128`, b16/b17/b85, Freeze !Copy Drop: обе G;
b86: stable G / unstable fallback S; `Cell<i32>`: обе default/fallback S.
Полный u640..32 — отдельные O1 семьи, не вывод из этой выборки.
Stable ZST ordinary вынесен в assembly: N1,2,7,8,16,17,31,32.
Остальные длины/типы не достраиваются по соседним клеткам.
K9s exact2: u8/u64/u128, b16/b17/b85/b86, W2Drop, Cell<i32>;
ZST excluded; i32 exact4 есть в раннем swap, это не i32 exactN9..17.

K10 использует настоящий `<` (`network.rs:1547`), тогда как merge/L2
`lt_u8/lt_u64` сравнивают x>>1. Поэтому общее замечание X0:412 о значении
**именно имён lt_u8/lt_u64** не распространяется на K10.
Сортированность K10 N9+ и структурная композиция перестановки — разные
основания, full-route multiset N10+ не заявляется (X0:46–69).

### 3.4. correct.rs — 230 строк

| Координаты (+строк) | Семейство → свойство | Типы / длины / регионы | X0 entries и зависимые контроли; O/C |
| --- | --- | --- | --- |
| `correct.rs:1–54` (+54) | L2 fallback helper, generator и 17 named callers | u64 N8..16 (9), u8 N9..16 (8); exact arrayN, x>>1; sortedness+полный probe count | `l2_fallback_*` O, verified insert_tail; C solver instances используют тот же generator; **17/0** |
| `correct.rs:55–87` (+33) | Tail prefix contract/frame и deliberate R11 | u8 backing17, symbolic tail1..16, region2..17, suffix frame; R11 exact [4,0,2] | `l2_insert_tail_prefix_u8` O; `l2_r11_insert_tail` C нарушает sorted prefix, не memory requires; **1/1** |
| `correct.rs:88–129` (+42) | Interior scratch tail contract/frame | Initialized backing48, start∈{0,6,7}, len5..8, весь вне-region frame; u8 O/u64 C | `l2_insert_tail_scratch_u8` O; u64 C prerequisite timeout; R11 выше не доказывает все геометрии; **1/1** |
| `correct.rs:130–169` (+40) | GS composition с real sort4, verified tail+merge | u8 exactN14/15 O; u64 N15 C; stable/general selector, stable scratch48; x>>1 | `l2_gs_u8_n14/n15` O; u64 C из-за незакрытого scratch prerequisite; preserve D-B4; **2/1** |
| `correct.rs:170–200` (+31) | Real sort13 route с verified insertion tail | u8/u64 exactN17, x>>1, whole-route sortedness/count | `l2_network_*_n17` C; TIMEOUT600, не proof credit; **0/2** |
| `correct.rs:201–230` (+30) | Solver screening invocations | Scratch u64, GS13/14, network u64 15/16/17 и u8 16/17, fallback16; точные solver по X0 | 13 `l2_sweep_*` C, TIMEOUT120 screening; не удалять вместе с prerequisite explanation; **0/13** |

Итог: 21 O /18 C. Отдельные 17 fallback entries — необходимые точные N,
а не 17 копий тела. Поддерживающие callee на backing17 и backing48
не взаимозаменяемы. GS u64 caller SUCCESS сам по себе не закрывает цепочку.

### 3.5. assembly.rs — 166 строк

| Координаты (+строк) | Семейство → свойство | Типы / длины / регионы | X0 entries и зависимые контроли; O/C |
| --- | --- | --- | --- |
| `assembly.rs:1–22` (+22) | Imports, strict volatile u8 comparator и ord cut | Пары используют initialized readable arguments; cut только panic_on_ord_violation | Общее основание пяти пар; cut без unwind evidence; **0/0** |
| `assembly.rs:23–42` (+20) | Swap и tail check helpers | u8 backing2, sorted pair + exact двухэлементная permutation | `k15_swap/insert` O ↔ `k15_mutant_swap/insert` C; одинаковый check для original/copy; **0/0** |
| `assembly.rs:43–82` (+40) | Merge_up check, count4 и arbitrary comparator | Source2,dst singleton; exact advancement и copied value; full probe u8 | `k15_merge_up` ↔ mutant C; count/arbitrary используются consumption парой; **0/0** |
| `assembly.rs:83–105` (+23) | Consumption и presorted_len witnesses | Merge u8 backing4, произвольный read-only comparator, normal-return multiplicity; network deterministic N10 с последним0 | `k15_merge_consumption/presorted_len` O ↔ соответствующие C; не весь старый набор ко всем mutations; **0/0** |
| `assembly.rs:106–142` (+37) | Один paired generator и пять invocations | Те же inputs/checks, прямые original/mutant callbacks, unwind17, ord cut | 5 O +5 C; зависит от всех пяти mutations, ordinary stubs contract-функций здесь не используются; **5/5** |
| `assembly.rs:143–166` (+24) | Stable ZST generator и восемь instances | [();N], N∈{1,2,7,8,16,17,31,32}, scratch48, ZST-aware reads | `ci_zst_stable_*` O; uses uninit helper; normal-return safety, не network ZST и не everyN; **8/0** |

Семьи helpers не суммируются повторно с invocations: 13 O /5 C всего.
Пять K15 пар показывают чувствительность **выделенных свидетелей**, а не
всего прежнего safety-набора. Источник результатов и failed checks:
`W3-DISCLOSURE-DRAFT.md:136–161` на b6b480cc.

### 3.6. mutations.rs — 250 строк

| Координаты (+строк) | Семейство → свойство | Типы / длины / регионы | X0 entries и зависимые контроли; O/C |
| --- | --- | --- | --- |
| `mutations.rs:1–39` (+39) | Swap copy: инверсия условия | Generic T/F; реально witness u8N2 | `assembly::k15_mutant_swap`; сохранять copy↔actual source correspondence; **0/0** |
| `mutations.rs:40–76` (+37) | Tail copy: начальный sift указывает на tail | Generic T/F; u8N2 | `assembly::k15_mutant_insert`; не подменять проверкой normal оригинала; **0/0** |
| `mutations.rs:77–108` (+32) | Merge_up copy: переставлены advancement источников | Generic T/F; source u8N2 →singleton output | `assembly::k15_mutant_merge_up`; проверяется tuple advancement; **0/0** |
| `mutations.rs:109–189` (+81) | Bidirectional merge copy: удалён final consumption guard | Generic Freeze T/F; u8N4 arbitrary read-only comparator | `assembly::k15_mutant_merge_consumption`; под SWO мутация может быть незаметна, arbitrary comparator существенен; **0/0** |
| `mutations.rs:190–250` (+61) | Network copy: sort9 сообщает presorted_len10 | Generic Freeze T/F; u8N10 | `assembly::k15_mutant_presorted_len` и `network::k15_mutant_existing_k10_presorted_len`; обе проверки нужны для заявленного scope; **0/0** |

Модуль подключён только C (`kani_k1.rs:14–15`), собственных entries нет.
250 строк — намеренные runtime-body копии для negative controls. Их нельзя
считать дубликатами, удаляемыми без замены mutation protocol; runtime std
не редактируется. В копиях есть повторные upstream performance-комментарии;
возможность редакторского сокращения не оценена числом без построчного проекта.

### 3.7. smoke.rs — 51 строка

| Координаты (+строк) | Семейство → свойство | Типы / длины / регионы | X0 entries и зависимые контроли; O/C |
| --- | --- | --- | --- |
| `smoke.rs:1–14` (+14) | Пояснение режима и repr-transparent Drop type | W3SwapDrop(u8), empty Drop | Служит C3 heuristic O; не доказательство корректности Drop sort; **0/0** |
| `smoke.rs:15–35` (+21) | C3 efficient-swap predicate | Десять типов: u8,u64,u128,b16,b17,b85,b86,W3SwapDrop,Cell<i32>,() | `w3_efficient_swap_c3` O; десять assert/cover, не сортировка этих типов; **1/0** |
| `smoke.rs:36–51` (+16) | Lane smoke и deliberate false predicate | ok: u64=true,b9=false, u8 symbolic x, covers0/255; negative только b9=true | `ok`,`control_must_fail` C; найдено расхождение доменов X0, см. §4; **0/2** |

### 3.8. uninit.rs — 428 строк

| Координаты (+строк) | Семейство → свойство | Типы / длины / регионы | X0 entries и зависимые контроли; O/C |
| --- | --- | --- | --- |
| `uninit.rs:1–29` (+29) | U1/ZST model disclosure, cut и volatile arbitrary comparator | Reading initialized arguments; U1 требует отдельного uninit-флага | C diagnostics; flag-off SUCCESS не uninit evidence; **0/0** |
| `uninit.rs:30–94` (+65) | ZST input/comparator variants и общий ZST-aware helper | Literal/array::from_fn, Copy/const scratch48; volatile или ptr::read для ZST; stable/network | `z1_*`,`z1f_*`,`z1n_*`; helper64–76 нужен assembly O и network K9s C; **0/0** |
| `uninit.rs:95–144` (+50) | ZST generator и 35 invocations | () stable N0/1/2/7/8/15/16/17/31/32; network8/9/12/13/17; w2-like и nonvolatile subsets по X0 | `z1_stable_*`,`z1_network_*`,`z1f_*`,`z1n_*`, from_fn2/32 C; разные модели не сливать; **0/35** |
| `uninit.rs:145–268` (+124) | Изолированные primitive/model checks | Unit read/volatile; mergeN2/3, tailN2, sort4N4, swap/copyN2, explicit ZST-aware варианты | 12 direct `z1*` C; отличают tool-model от поведения сортировки; **0/12** |
| `uninit.rs:269–330` (+62) | Scratch read-back helpers и real-route diagnostics | u64 stable scratch48 N8/16/32; networkN18/32 после scratch→v, read_all | 5 `u1_general/network_*` C; covers фактического scratch read, не просто выделения памяти; **0/5** |
| `uninit.rs:331–350` (+20) | Initialized/uninitialized scalar pair | MaybeUninit<u64> scalar, volatile read | `u1_initialized_control`,`u1_uninitialized_control` C; требуются локализованные ожидаемые checks; **0/2** |
| `uninit.rs:351–394` (+44) | General scratch-tail pair + raw-write variant | Реальный generalN8 scratch48; cell47 untouched / MaybeUninit write / raw write | 3 `u1_general_8_tail_*` C; без supported uninit pin не зачёт; **0/3** |
| `uninit.rs:395–428` (+34) | Network-layout isolated tail pair | MaybeUninit<[u64;32]> cast pointer; cells0..17 initialized, cell31 optional write | 2 `u1_network_layout_tail_*` C; это layout control, не actual network-sort proof; **0/2** |

Все59 entries C, но файл не целиком C из-за используемого общего helper.
U-1 на историческом pin unsupported до сортировки/контрольного read,
covers0; ни positive/negative pair, ни полнота E1 не установлены.
Stable ZST ordinary отделён в assembly. Network ZST не верифицирован:
при N≥18 прибавление смещения к ZST-указателю сохраняет адрес, поэтому
region loop не достигает выхода по отличию указателей (`smallsort.rs:355`).
Обычные публичные callers выходят раньше для ZST; публично достижимый
отказ здесь не заявляется. Номер внешней rust-lang issue для этого не нужен.

## 4. Сверка X0 и точные зависимости

### 4.1. Найденные расхождения и устаревшие описания

1. **X0:1004–1005**, строки `smoke::ok` и `control_must_fail`, повторяют
   описание десяти C3 типов и cover каждого типа из ordinary predicate.
   Исходник **smoke.rs:38–43** проверяет только u64 и b9, плюс u8 x и
   covers x=0/255; **smoke.rs:48–50** содержит единственный false assert b9.
   Числа X0 1 O/2 C и cfg верны; неточен домен этих двух C-строк.
   В текущей сессии X0 не исправляется; предложение П-5 — исправить metadata,
   не приписывать negative десять covers. Раскрытие b6b480cc:146–157
   соответствует исходнику и ожидаемому failed check.
2. **merge.rs:438** «ATTACHED to the loop» и **:910–911** «on the loop»
   описывают старый опыт, а не S_M. В SS:865–946 нет loop-invariant
   атрибута, исходниковый поиск не находит вызова этой цепочки (§5).
   К proof credit этих комментариев не прибавлять. Активные контракты
   используют другой helper, **merge.rs:629–640**.
3. **network.rs:266–270** честно сообщает, что attrs сняты и helper unused.
   Гармоника `insertion_inv_o1_u64` всё ещё вызывает actual insertion с
   verified tail: её нельзя считать неиспользуемой вслед за helper.
   X0 правильно учитывает эту C-entry; её имя/описание историческое.
4. **merge.rs:233** «Not used by the contracts at HEAD» верно для прямых
   sortedness clauses SS, но `k1_sorted_q` нужен retained plain diagnostics.
   Это не причина удалять helper вместе с invariant chain.

Иных расхождений состава O/C, имён и Item line в просмотренных семействах
не установлено. Это статическая сверка, не target-specific enumeration.
X0 остаётся главным реестром, а замечание к двум smoke-доменам сохранено
явно вместо молчаливого переопределения реестра.

### 4.2. Что необходимо сохранить по геометрии и модели

| Цепочка | Необходимые инстанциации / контроль | Почему нельзя свернуть домен без новой проверки |
| --- | --- | --- |
| Swap → network | K9s u8/u64 каждое backingN9..17 + любые distinct indices/frame; отдельные C3 exact2; R11 same-index | `[T;17]` не доказательство всех меньших/больших allocations; соответствие x>>1/default `<` отдельно. |
| Merge → general/stable | u8/u64 exactN callee, sorted halves, disjoint dst/frame; R11 u8/u64; scratch48 premises | GS caller PASS не заменяет callee; перенос D-B4 аналитический, другие scratch sizes не доказаны. |
| Tail → fallback/L2 | u8 backing17 tail1..16; scratch48 start0/6/7 len5..8; K8r backing17 start1..15/tails; R11 prefix | Длина активного региона, длина allocation, begin-offset и тип — разные координаты. 120 shifted regions не scratch48 lemma. |
| Insertion B4/O3 | Каждая N1..20 и все valid offset; W3 группы N15..20, cover каждого offset; u64 и Cell<K13Tagged> | 28 paired calls —56 named proofs разных comparator/type/offset domains; covers лишь крайних offset в старой семье не cover каждого. |
| K10 correctness | Exact u8/u64 N и pure `<`; sortedness отдельно от insertion-tail permutation/структуры сети | Sortedness16/17 у u8 не добавляет полную permutation; full-route multiset N10+ не заявлен. |
| Drop | Low2/4/8, upper2/4/8/16; counter **и** tags; duplicate-tag/extra-drop C | Padding исключает bytewise identity для tagged Drop; counter один не обнаруживает duplication+loss; normal-return не unwind. |
| ZST/U1 | Восемь stable O, ZST-aware helper; isolated read/model C и explicit U1 flag/controls | Volatile и nonvolatile — разные модели; unsupported и 0 covers не положительный/отрицательный proof. |

О1-А использует arbitrary read-only bool comparator с чтением обоих
аргументов; отрезается только order-violation panic через assume(false).
Это не полное no-UB, aliasing/uninit/unwind остаются раскрытыми.
Нельзя совместить такую safety-семью с proof correctness под SWO,
исключив несогласованные сравнения. Равные keys с разными полными значениями
в lt_u8/lt_u64 сохраняются. Типы C3 — представители ветвей, не generic T proof.

## 5. Неиспользуемый код, повторы и служебные комментарии

### 5.1. Источниковое доказательство неиспользования

Поиск сделан по точному S_M (не только по текущей рабочей копии):

```sh
git grep -n -w -e k1_ins_inv ac0dbbf0 -- library
git grep -n -w -e k1_bm_inv -e k1_bm_inv_full -e k1_bm_inv_count \
  -e k1_bm_inv3 -e k1_bm_inv3_sorted -e k1_bm_inv_count_l \
  -e k1_bm_inv_core -e K1BmInv ac0dbbf0 -- library
git grep -n -w -e lt_u16 -e lt_i16 ac0dbbf0 -- library
```

Все совпадения для invariant chain находятся в merge.rs: определения,
внутренние вызовы самой цепочки, пояснения. В SS и прочих Rust-файлах
внешних вызовов, включая Kani attrs, нет. Единственное упоминание
`k1_bm_inv3_sorted` кроме определения :464 — **комментарий** :911.
Для `lt_u16`/`lt_i16` совпадения только определения :730/:734.
Для `k1_ins_inv` только определение network.rs:246 и комментарий :270.
X0 не содержит u16/i16 доменов этой цепочки и не содержит отдельных
entries для этих helpers. Искались точные слова, не подстроки имён SIMD.

| Кандидат П-5 | Точные удаляемые интервалы | Арифметика | Что обязательно остаётся |
| --- | --- | ---: | --- |
| Dead merge invariant chain | merge.rs:363–628 | 266 | Активный halves-sorted helper629–640 и закрывающая impl скобка640 |
| Dead K1BmInv trait/default/overrides | merge.rs:642–719 | 78 | Все используемые type/comparator domains и K1Probe specialization |
| Неиспользуемые comparators | merge.rs:730–736 | 7 | lt_u8/i32/u64 и b16/b85; семь строк включают разделитель между двумя функциями |
| Dead insertion invariant helper | network.rs:239–264 | 26 | Исполняемая C-entry266–282 и необходимые другим потребителям helpers |
| **Всего** | Непересекающиеся интервалы | **377** | Все625 X0 entries /355 O /270 C сохраняются |

Это 351 строка merge +26 network. Размер найденного остатка не означает,
что исходный алгоритм или действующие доказательства неверны.
Удаление предлагается потому, что исходникового потребителя нет, а не
из-за возраста или агентского происхождения. Историю вариантов сохранить
по устойчивой ссылке на S_M, а не перенести заново в основной PR.

**Не удалять** `k1_count_l`/`k1_perm_l` (merge.rs:244–263 → :906),
`k1_merge_halves_sorted_q` (:265–275 → :896/:920), `k1_sorted_q`
(:231–242 → retained diagnostics), `k1_count_u`/`k1_sorted_u`
(SS clauses/callers), `k1_merge_halves_sorted` (:629–640 → SS:861).
Наличие `allow(dead_code)` само по себе не доказательство неиспользования.

### 5.2. Реальные повторы и предел оценки

| Предложение сжатия | Измеряемый исходный текст → замена | Сохраняется | Оценка экономии |
| --- | --- | --- | ---: |
| Один generator для `insert_tail_int/bytes` | merge.rs:1121–1147 =27 строк → макрос с теми же attrs/body и двумя invocations:17 строк шаблон +2–6 строк invocations/разделителей =19–23 | Оба имени, C, unwind34, len2..16, const arrays, выбор i32/u64 либо b16/b85 и endpoint covers | **4–8** |
| Общий уже существующий sortedness/count checker для L2 | correct.rs:18–20,148–150,181–183 =9 строк →3 вызова существующего merge.rs:1645–1658, visibility `pub(super)` без добавления строки | Три свойства на тех же input/output, cmp, N; covers и stubs остаются на месте | **6** |
| ExactN lists, C3/K8r/W3 instances | merge.rs:1547–1577,1723–1812; network.rs:1517–1544,1736–1854 | Имена, cfg, const-N, backing, start/offset и partition клетки | **0 засчитано**: тела уже обобщены; уплотнение строк не содержательная экономия |
| Mutant runtime copies | mutations.rs:6–250 | Привязка к оригиналу и чувствительность пяти свидетелей | **0 засчитано**: это intentional controls, не ненужные дубликаты |
| ZST models и solver sweeps | uninit.rs:30–268; correct.rs:201–230 | Разные чтения/инициализация/флаги/solver и исторические статусы | **0 засчитано**: удаление меняет состав диагностики; это отдельное решение, не свёртка логики |

Первый бюджет — проект возможного макроса, не скомпилированный результат;
27−(19..23)=4..8. Второй — ровно три замены блока3 строк вызовом1 строка:
3×(3−1)=6; общий checker уже есть. Изменятся места assertions/expansion,
поэтому предполагаемая эквивалентность требует review и последующей Kani
проверки. Никакой оценки ускорения solver из уменьшения исходника нет.
Дедупликация light/unrolled/quantified helpers не предлагается: способы
кодирования использованы различными контрактами/опытами и имеют собственные
ограничения instrumentation.

### 5.3. Редактура назначения вместо организационной истории

| Места | Что заменить | Что сохранить в объяснении |
| --- | --- | --- |
| kani_k1.rs:1–5 | Владельцы-агенты и правила «редактирует только свой файл» | Карта модулей, ordinary vs opt-in, shared dependency uninit |
| correct.rs:1–9,41,168,201–204 | Названия этапов/ревизий/измерений как единственное объяснение | Full-width domain, exact geometry, почему caller исключён без scratch prerequisite, screening vs proof |
| merge.rs:1–27,58–62,123–124,363–371,438–439,883–911,1579–1581,1813–1817 | Phase/wave/night/job labels и неверное ATTACHED | Probe encoding, причины unrolling, normal-return/cut, настоящее состояние attrs; подробная история по pin |
| network.rs:236–270,439–487,490–518,997–1008,1279–1282,1431–1440,1736–1737,1898–1905 | Фазы/волны как описание свойства, устаревшее имя invariant harness | Точные backing/offset группы, CD-2 и covers, отличие real/stub, why ZST unsupported |
| assembly.rs:1,125–126; smoke.rs:1–3,15; uninit.rs:1–5,42–44,60–63,269–272,351–355 | Stage/Wave/L1/job bookkeeping | Paired checks, compile limitation, отдельный U1-флаг, ZST exception и read-back purpose |

Редактура не должна скрывать происхождение кода или стирать результаты
TIMEOUT/unsupported. Экономия комментариев в диапазон ниже не включена:
цель — понятность, новая формулировка может занимать столько же строк.

## 6. Что объясняет 45,7× / 11,7×

### 6.1. Разделение арифметики и семантики

| Срез | Расчёт | Значение |
| --- | --- | ---: |
| Исторический полный CI | 20 508 /449 | 45,6748× ≈45,7× |
| Заданный основной S_M | 20 327 /449 | 45,2717× ≈45,3× |
| Девять SmallSort файлов | 5 241 /449 | 11,6726× ≈11,7× |
| Вне SmallSort в S_M | 15 086 /20 327 | 74,2166% |
| Вне SmallSort в историческом срезе | 15 267 /20 508 | 74,4441% |

Поэтому объяснение «только отчёты» закрывает лишь внешнюю часть. В S_M
15 086 =14 690 исследовательских +394 предлагаемых приложений +2 check-cfg.
Ни 394 строки раскрытия, ни две строки cfg не объявлены ненужными.
Разница исторического/основного коэффициента — только181 строка workflow.

Ниже **воспроизводимое распределение нашего текста по назначению**, не
попытка узнать, сколько аналогичных строк содержит чужой PR. Роли имеют
явное правило и не пересекаются; макросы и комментарии остаются в своём
интервале. Невозможно корректно поделить чужие449 строк по этим же ролям
без запрещённого просмотра кода; причинного точного вычитания здесь нет.

| Объяснение | Измеряемая часть нашего SmallSort | Строк | Доля /449 |
| --- | --- | ---: | ---: |
| (а) Реализация семейств свойств/доменов/контролей, включая их harness templates и диагностические варианты | Остальные интервалы карты после (б)/(в); это весь purposeful harness/control слой, а не утверждение о минимальности каждой строки | 4 328 | 9,6392× |
| (б) Общее устройство спецификаций и подключения | SS119 + module15 + merge.rs:1–753 за вычетом351 неиспользуемой строки | 536 | 1,1938× |
| (в) Подтверждённый неиспользуемый остаток опытов | merge351 + network26 из §5.1 | 377 | 0,8396× |
| **Итого SmallSort** | 4 328 +536 +377 | **5 241** | **11,6726×** |
| Текст вне SmallSort | Все остальные46 файлов S_M | 15 086 | 33,5991× |
| **Итого S_M** | 5 241 +15 086 | **20 327** | **45,2717×** |

(а) включает 10–14 строк прогнозируемого сокращения повторов из §5.2;
не прибавлять их к377 как уже удалённый текст. (б) — консервативная
измеримая общая часть, не вся механика внутри семейных generators.
Такое правило не выдаёт4328 строк за нижнюю границу необходимого исходника.
Оно показывает, что установленный ненужный остаток —377 строк, а не весь
длинный proof слой; дальнейшее сокращение сверх названных интервалов
требует отдельного содержательного обоснования.

### 6.2. Основания содержательной разницы

Разрешённый аудит сообщает #694: один файл/+449,25 гармоник (одна self-check),
два контракта; семь safety targets, корректный читающий comparator,
выбранные верхние длины; symbolic direct insertion1..16/offset1;
корректность general/stable i32N8, network u8N9 и несколько отдельных
клеток; нет установленных postconditions сортировки/permutation в двух
контрактах и использования verified stubs (аудит:22–24,44–55,63–71).
Это описание границ аудита, не оценка чужого кода.

Наши дополнительные оси имеют конкретные носители:

- **Свойства и comparator models:** arbitrary CD-2 safety и ord cut
  (merge.rs:1284–1534,1535–1577; network.rs:488–545,997–1069),
  mutating Cell/O3 (network.rs:761–996,1279–1545), paired Drop count+tags
  (merge.rs:1838–2015). Это разные свойства; их нельзя заменить одной
  sortedness проверкой с корректным comparator.
- **Типы/длины/регионы:** C3 G/S/U (network.rs:1092–1278), B4/O3 все
  valid offset до20 (:1283–1544), K9s exact arrays9..17 и frame
  (:1736–1804), shifted tail120 regions (:1805–1854), prefix/scratch48
  (correct.rs:55–129). Число harmonic entries не равно числу клеток,
  а constant instantiation выбран ещё и для ограничений инструмента.
- **Контрактная композиция:** восемь контрактных целей в SS:380–864,
  probe/quantified/unrolled specs (merge.rs:37–362,629–640), GS/fallback
  callers (:1645–1812, correct.rs:1–200); нужны callee prerequisites,
  frame, R11 controls, отдельный аналитический перенос D-B4.
- **Чувствительность и диагностика:** пять K15 пар (assembly.rs:23–142,
  mutations.rs:1–250), C5 (merge.rs:1463–1508), дополнительный старый
  K10 mutant (network.rs:1898–1905), smoke (smoke.rs:36–51), ZST/U1
  (uninit.rs:1–428). Часть — доказательные контроли, часть — раскрытие
  неудавшихся/unsupported опытов; вся она не считается formal proof.
- **Устранимый исторический слой:** конкретные377 строк §5.1;
  против них есть source-search, в отличие от общего предположения
  «все длинные однотипные строки — дубли».

355 ordinary против25 source entries — сравнение организации наборов,
не коэффициент силы доказательства. Некоторые наши statements шире по
перечисленным осям, но complete thresholds correctness, aliasing/uninit/
unwind, другие primitive/default-order instances остаются открытыми.
Разрешённый аудит не позволяет приписать каждому дополнительному свойству
точную долю **семантической** разницы 4792=5241−449 строк; таблица выше
честно учитывает собственный текст по явному правилу без такого домысла.

### 6.3. Остаточный объём с явными допущениями

| Сценарий предложения | Девять SmallSort файлов | С cfg Cargo (+2) | С двумя неизменёнными приложениями S_M (+394) |
| --- | ---: | ---: | ---: |
| Только выбор файлов, без proof-редактуры | 5 241 | 5 243 | 5 637 |
| Только неиспользуемые helpers §5.1 | 4 864 | 4 866 | 5 260 |
| Helpers + обе дедупликации §5.2 | 4 850–4 854 | 4 852–4 856 | 5 246–5 250 |

Защищаемый общий диапазон после **возможного** сжатия: **4 850–4 864**
строки SmallSort (примерно10,8×449), **10 файлов/4 852–4 866** исходных
добавлений с Cargo. Предполагается: все625 entries/355 O/270 C, имена,
типы/N/backing/regions/cfg, утверждения и covers сохранены; комментарии
переписаны без обещания уменьшения длины; генераторы уложились в указанный
бюджет; новый reviewer entry и сверка final CI ещё не посчитаны.
Это не измеренный diff и не гарантия Kani-equivalence/времени/памяти.
Меньший остаток сейчас не обоснован; перенести diagnostics в другой
файл — не уменьшить совокупный объём и не сохранить автоматически пути.

## 7. Предложения для П-3/П-5 — не решения

При любом изменении proof-кода, имён или состава run прежней версии
не является итоговой проверкой S_M′. После всех принятых изменений нужен
единый полный цикл П-6, в том числе4×Ubuntu (`KANI_JOBS=2`) +4×macOS,
штатный parallelism/partitioning и базовые std harmonics. Имена сохранять
полностью qualified. Ожидаемо неизменный список — не измеренная прежняя
раскладка: X0 source SHA/Item/Macro line и target-specific список следует
обновить, T/P/H/M новой базы до измерений UNKNOWN. Здесь запуски не разрешены.

| ID | Конкретное предложение / файлы | Имена, состав и партиции | Нужная последующая проверка | Риск для доказательства |
| --- | --- | --- | --- | --- |
| П3-A | Выбрать10 source файлов §2, два reviewer приложения;43 файла сохранить по pin в research | Code entries без изменений; экспериментальный coordinator workflow не часть PR | Numstat BASE...S_M′, dependency/link audit, достаточные ordinary/controls команды; применимые П6 checks на финальном пакете | Потерять replay/предпосылки при удалении инструментов; source-safe выбор условен достаточностью entry для рецензента |
| П5-A | Удалить только377 строк §5.1 из merge.rs/network.rs, исторические объяснения сохранить по S_M | Все625 имён, O/C и domains ожидаемо прежние; source locations меняются | Source search/graph, X0 refresh, Kani на итоговом source + полный8-partition цикл П6 | Ошибка границы удаления; специально сохранять merge629–640 и live light/quantified helpers |
| П5-B | Макрос двух tail proof bodies merge1121–1147, savings4–8 | `insert_tail_int/bytes`, cfg/attrs/2..16/type selection/covers прежние; new Macro line | Review статической развёртки, реестр; обе C-entry с exact pin, затем code-change П6 | Instrumentation/macro expansion может отличиться; не менять counts/состав ради компактности |
| П5-C | В correct.rs три assertion blocks заменить вызовом существующего checker merge1645–1658; helper сделать pub(super), savings6 | Все L2 имена/cfg/stubs/домены/covers прежние; assertion locations меняются | Review comparator/count semantics, Kani callers/callee цепочки на S_M′, полныйП6 | Ошибка в передаче input/output/cmp или изменение spec instrumentation; semantic equivalence пока гипотеза |
| П5-D | Переписать организационные комментарии по §5.3; только текст, включая ложный ATTACHED и invariant harness description | Имена/атрибуты/код неизменны; нет ожидаемого partition изменения; line refs обновить | Текстовый diff и ссылки/X0 coordinates; если строго comments-only, новый Kani только из-за этих слов не нужен | Стереть важный caveat/происхождение; не удалять содержательные обоснования |
| П5-E | Исправить две smoke C-domain записи X0 на actual u64/b9/u8 и b9 соответственно | 625/355/270 и исходник без изменений | Только исходниковая/текстовая сверка и правка metadata отдельным разрешённым заданием | Приписать лишние covers/типы; proof-статус не меняется |
| П3-B (не рекомендовано первым шагом) | Вынести C diagnostics/control definitions в sibling modules | Переезд меняет fully qualified paths, cfg/visibility/resolution; возможны новые partitions и выборки; uninit helper сначала выделить | Новый X0, оба cfg списка, Kani controls и полный8-partition П6; измерения старой раскладки не переносить | Потерять negative controls/shared helpers либо включить C в ordinary; экономия общего кода0 |
| П5-F (сохранить) | Не заменять exactN/backing/start/offset таблицы символическим общим proof без отдельного проекта | Имена/состав/все домены сохраняются в исходном предложении | Только source review решения сохранить; иной проект потребует Kani/нового X0/П6 | Уменьшить domain либо ухудшить solver/unwind tractability, скрыв это за меньшим числом строк |

`insertion_inv_o1_u64` предлагается **сохранить** и переописать, а не удалить
вместе с dead helper: она проверяет реальный insertionN8/offset1 с verified
tail. Соседняя `insertion_o1_u64` использует actual tail и поэтому не
тождественна по способу доказательства. Удаление17 строк control266–282
не включено ни в377, ни в прогноз: оно изменило бы состав C.

X6/X7 в этой сессии не открываются. Если предложения к общим proof-файлам
будут приняты, сначала П-3/П-5 и фиксация S_M′/X0, затем новые кодовые задания.
Полные прочие PR checks П-6 остаются отдельным поручением; успешность
восьми обычных partitions сама по себе не равна прохождению всех checks.

## 8. Воспроизводимость бумажного аудита и итог сессии

Выполнено только статически: numstat по двум pin, чтение нашего source и
разрешённых документов, группировка строк/entries, точный symbol search.
Проверены суммы55/20327,9/5241,10/5243,2/394,43/14690;
7 новых модулей покрыты непересекающимися диапазонами целиком, module root15
и added SS119 учтены отдельно; X0625=355+270 сверяется по Item line.
Для doc-only изменения — `git diff --check` и whitelist одного нового файла.
Kani/rustc/cargo/CBMC, builds/workflows и CI status polling не выполнялись.

Спорные трактовки решены в документе: 45,7× — исторический коэффициент,
X0 primary с явным smoke erratum, controls остаются исходником PR,
неисполняемый helper не равен исторически названному исполняемому control,
новый воспроизводимый reviewer entry — обязательный вход П-3, не уже
готовый результат этой сессии. Дополнения П-3/П-5 и кодовые изменения
остаются предложениями; доказательные claims не усилены.
