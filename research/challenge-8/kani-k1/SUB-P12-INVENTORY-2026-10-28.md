# П-1/П-2 — инвентарь пакета SmallSort

Дата: 2026-10-28. Документальная сессия W3-SUB; сборки $0.
**Результат после R9: найдено 388 неиспользуемых строк, обосновано
76–89 строк сворачиваемых повторов; отдельно выделены 1 547 строк
исторических диагностик/скринингов.** При сохранении всех625 entries
прогноз SmallSort — **4 764–4 777 строк**. При отдельном согласованном
выносе диагностических семейств — условно **3 275–3 283**, с355 ordinary
и100 opt-in entries; для этого нужны новая привязка callee и состав X0.
Вне SmallSort по-прежнему предлагается отделить14 690 строк истории.
Это предложения для П-3/П-5, а не выполненное сокращение или новая
приёмка доказательств. Исправлена редакция `dee9485a` по R9 координатора;
исходные числа §2, карта §3 и numstat сохранены.

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
архива. Решения ниже предлагаемые. Таблица §2 — исходный выбор **целых файлов**;
уточнённый отбор семейств внутри них дан в §6.1/§6.3. Назначение «контроль» относится
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
| `library/core/src/slice/sort/shared/smallsort/kani_k1/uninit.rs` | 428 | диагностика / контроль / средство воспроизведения | В PR: shared helper64–77 и imports10–12 нужны ordinary assembly; остальные диагностические семейства предлагаются в исследовательскую ветку (§6.1); U-1 unsupported не proof. |
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

Сценарий §2.1 пока сохраняет все исходные625 entries и весь код девяти
файлов: это верхний исходный состав без отбора семейств. После R9
предлагается оставить отрицательные/различающие контроли (а2), а исторические
семейства (а3) вынести по §6.1. Они не объявляются неиспользуемым кодом;
меняются состав и воспроизведение пакета, что требует отдельного решения.
Все250 строк mutants остаются. Из uninit для ordinary обязательно сохранить
`uninit.rs:64–77` и imports10–12: `assembly.rs:152` вызывает
`uninit::zst_aware_less`, как и `network.rs:1605`. Точная проекция этого
отбора приведена отдельно в §6.3, не подменяет numstat55/20327.

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

Поиск выполнен по точному S_M, а не только по рабочей копии:

```sh
git grep -n -w -e k1_ins_inv -e w1_boundary_routes ac0dbbf0 -- library
git grep -n -w -e k1_bm_inv -e k1_bm_inv_full -e k1_bm_inv_count \
  -e k1_bm_inv3 -e k1_bm_inv3_sorted -e k1_bm_inv_count_l \
  -e k1_bm_inv_core -e K1BmInv ac0dbbf0 -- library
git grep -n -w -e lt_u16 -e lt_i16 ac0dbbf0 -- library
```

Все совпадения invariant chain — в merge.rs: определения, внутренние
вызовы самой цепочки, пояснения; в SS/прочих Rust-файлах внешних вызовов
и Kani attrs нет. У `k1_bm_inv3_sorted` кроме определения :464 только
**комментарий** :911. `lt_u16/lt_i16` встречаются только в определениях
:730/:734, `k1_ins_inv` — в определении network:246 и комментарии :270.
`w1_boundary_routes` — только определение merge:1431; тело :1432–1436
не вызывается ни одним source entry. X0 не даёт этим helpers собственных
entries и не содержит u16/i16 доменов dead chain. Поиск — по точным словам.

| Кандидат П-5 | Удаляемые интервалы S_M | Строк | Что остаётся |
| --- | --- | ---: | --- |
| Dead merge invariant chain | merge.rs:363–628 | 266 | Активный predicate629–640 и закрывающая impl скобка640 |
| Dead K1BmInv trait/default/overrides | merge.rs:642–720 | 79 | Пустая641; захвачена720, чтобы не оставить двойной пробел между блоками |
| Неиспользуемые comparators | merge.rs:730–737 | 8 | Пустая729 и следующий lt_i32:738; не оставлять729+737 |
| Dead boundary routes | merge.rs:1429–1437 | 9 | Вызываемые general/stable helpers и upper_routes:1419–1426 |
| Dead insertion invariant helper | network.rs:239–264 | 26 | Исполняемая C-entry266–282; она не вызывает этот helper |
| **Всего** | 266+79+8+9+26 | **388** | Все625 entries /355 O /270 C сохраняются при одном этом удалении |

Это362 строки merge +26 network. Прежние377 недосчитали два разделителя
и9 строк boundary helper. Для вариантов с последующим архивированием
семейств §6.1 это отдельный, непересекающийся вычет.

**Не удалять по данному основанию** light/quantified helpers
`k1_count_l/k1_perm_l` (merge:244–263 → :906),
`k1_merge_halves_sorted_q` (:265–275 → :896/:920), `k1_sorted_q`
(:231–242 → retained diagnostics), `k1_count_u/k1_sorted_u` и
`k1_merge_halves_sorted` (:629–640 → SS:861). После отдельного отбора
диагностик часть зависимостей изменится; это новый аудит, не уже найденный
unused-код. Возраст, происхождение и `allow(dead_code)` не доказывают
неиспользование. Историю формулировок сохранить по pin S_M.

### 5.2. Сворачиваемые повторы: полный уточнённый список

Каждая из указанных пар повторно просмотрена по S_M. Бюджеты считают
физический исходный текст и замену с теми же expanded именами, cfg,
типами/N/backing, checks и covers. Это проекты текста, не результат
компиляции/форматирования. Экономия макрошаблона не равна числу его
развёрнутых copies. Перенос дополнительных attrs через
`$(#[$m:meta])*` сохраняет различие real и verified-stub вариантов.

| ID | Исходные интервалы и проверенное различие | Проект замены и бюджет строк | Экономия |
| --- | --- | --- | ---: |
| D1 | network:153–174 (22) +178–200 (23) =45; тела check_perm_n/check_perm_stub_n одинаковы, только второй добавляет verified swap stub | Общий generator с forwarded attrs:25–27 строк вместо45. Stub-attrs передаются тем же вызовам; имя generated fn, input17, len n..17, два boundary covers, probe count и suffix frame сохранены. Изменения macro arguments — в существующих invocation строках; дополнительный wrapping не заявлен измеренным | **18–20** |
| D2 | network:374–397 (24) +551–575 (25) =49; band_tail добавляет только verified insert_tail | Общий band generator с attrs:26–28 строк вместо49. Сохраняются конкретный backing hi, lo..hi, все переданные covers, sort9/13 stubs и tail-stub только прежним именам | **21–23** |
| D3 | network:599–619 (21) +632–647 (16) =37; fixedt8_u64 повторяет fixed template на u64N8, добавляя tail-stub | Расширенный generator22–23 +cfg/invocation2 =24–25 вместо37; три старых fixed имени и новое invocation fixedt8 остаются с прежними attrs | **12–13** |
| D4 | merge:1582–1605 =24; ручные ветви2/3/4 повторяют существующий by_len:757–764 | Wrapper13–15 строк: прежние attrs/len, `by_len!(len, bm_len::<$t>($cmp), [2 3 4]);`, **после dispatch** три `cover(len == N, прежняя строка)`; const-N и normal-return covers сохранены | **9–11** |
| D5 | merge:1311–1330 (20) +1334–1352 (19) =39; общий merge/permutation body, но отрицательный early cover и ложный tail отличаются от положительного | Общий helper15–17 строк с callback сразу после assume_init, возвращающий исходный v; два4-строчных wrapper и8 неизменных attrs =31–33. Отрицательный callback сохраняет cover до permutation; затем тот же ложный assert, положительный — тот же final cover. Doc-строки1309–1310/1332–1333 считаются вне замены | **6–8** |
| D6 (прежний П5-B) | merge:1121–1147 =27; typed tail int/bytes | Generator и две invocations19–23; обе C-entry, unwind34, len2..16, типовой selector и covers сохраняются | **4–8** |
| D7 (прежний П5-C) | correct:18–20,148–150,181–183 =9 | Три вызова существующего merge checker:1645–1658 вместо9 строк; visibility pub(super) меняется в существующей строке | **6** |
| **Всего** | D1–D5 =66–75; D6+D7 =10–14 | Непересекающиеся исходные интервалы | **76–89** |

D4 нельзя сокращать за счёт covers перед вызовом: исходные covers
свидетельствуют normal return выбранного N. Модель13 строк без добавочных
разделителей получается из прежней оболочки с одной строкой by_len и
тремя post-call covers; поэтому прежняя грубая оценка12–14 экономии для
этого случая была бы завышена. D5 не считает31 строку тел полным исходным
объёмом: учтены8 строк attrs и сохранены разные хвосты двух проверок.

`check_sort_n` (network:83–102) почти совпадает с D1 по setup/call/frame,
но использует proof_for_contract и получает sortedness/count из ensures,
тогда как plain permutation шаблоны имеют явный count assert. Совместный
engine с разными attrs и post-check возможен; это альтернатива D1,
а не ещё один независимый вычет. В76–89 такая дополнительная свёртка
не включена. Аналогично `check_network_no_merge` (:328–357) можно
параметризовать вместе с D2, но надо передать backing17, все0..17,
его **шесть собственных cover messages** и insertion-stub вместо tail-stub.
Просто заменить его band шаблоном с «boundary length reachable» нельзя:
потеряются исходные covers. Основной проект D2 сохраняет no_merge отдельно;
для более общего engine дополнительная экономия здесь не обещается.

#### Отдельное решение о cfg

Поиск уточнил формулировку R9: **181** — все standalone строки
`#[cfg(kani_smallsort_controls)]` в merge/network (**77+104**),
а непосредственно перед macro invocations их **130 (44+86)**.
Остальные50 стоят перед прямыми proof definitions и одна — перед
`merge::w2_c5_normal_merge`. Это не181 свободно удаляемая строка.

Свёртывание cfg — **реальная экономия физических annotations**, но не
сокращение proof logic. Например, общий token/item-forwarding макрос
в kani_k1.rs перед `mod` declarations, затем по одному cfg-gated вызову
в merge/network, мог бы сохранить module scope, имена и все cfg effects.
Верхняя проектная модель:181 старых cfg →2 новых cfg +4 строки открытий/
закрытий двух вызовов +4–6 строк общего макроса, экономия **169–171**.
Она требует перегруппировать также прямые definitions/вспомогательную
функцию, сохранить macro-definition order, локальные пояснения, item attrs
и разрешение имён. Вложенный cfg-модуль менял бы qualified names и не
является эквивалентной заменой.

**Решение:** в основном диапазоне76–89 эту компоновку не засчитывать;
показать отдельной альтернативой П5-H. Здесь не выбран конкретный
читаемый layout, а local cfg сейчас явно показывает opt-in каждой строки.
Не складывать169–171 с D6 автоматически: D6 сам меняет размещение cfg;
при архивировании (а3) большая часть исходных181 исчезает вместе с
семействами. Для принятого layout нужен новый net numstat, а не вычет181
или сумма перекрывающихся гипотез. Это решение о сопровождаемости,
а не утверждение, что cfg нельзя обобщить.

Таблицы exactN/C3/K8r/W3 сохраняются: здесь не считается экономией
уплотнение invocation строк. Mutant copies остаются необходимым способом
чувствительности K15. Light/unrolled/quantified helpers автоматически
не объединяются: выбранные encodings имеют собственные ограничения.
Все изменения D1–D7 требуют review и последующей Kani/П-6 проверки;
обещания ускорения solver из сокращения исходника нет.

### 5.3. Редактура назначения вместо организационной истории

| Места | Что заменить | Что сохранить в объяснении |
| --- | --- | --- |
| kani_k1.rs:1–5 | Владельцы-агенты и правила «редактирует только свой файл» | Карта модулей, ordinary vs opt-in, shared dependency uninit |
| correct.rs:1–9,41,168,201–204 | Названия этапов/ревизий/измерений как единственное объяснение | Full-width domain, exact geometry, почему caller исключён без scratch prerequisite, screening vs proof |
| merge.rs:1–27,58–62,123–124,363–371,438–439,883–911,1579–1581,1813–1817 | Phase/wave/night/job labels и неверное ATTACHED | Probe encoding, причины unrolling, normal-return/cut, настоящее состояние attrs; подробная история по pin |
| merge.rs:1305–1307 | Висячий doc описывает уже удалённую CD-1/should_panic гармонику, но прикрепляется к w1_control_a_must_fail | Удалить/перенести именно ошибочную привязку; текущая функция не использует should_panic и должна FAILED на ложном assert; provenance демонстрации остаётся в истории |
| network.rs:236–270,439–487,490–518,997–1008,1279–1282,1431–1440,1736–1737,1898–1905 | Фазы/волны как описание свойства, устаревшее имя invariant harness | Точные backing/offset группы, CD-2 и covers, отличие real/stub, why ZST unsupported |
| assembly.rs:1,125–126; smoke.rs:1–3,15; uninit.rs:1–5,42–44,60–63,269–272,351–355 | Stage/Wave/L1/job bookkeeping | Paired checks, compile limitation, отдельный U1-флаг, ZST exception и read-back purpose |

Редактура не должна скрывать происхождение кода или стирать результаты
TIMEOUT/unsupported. Экономия комментариев в диапазон ниже не включена:
цель — понятность, новая формулировка может занимать столько же строк.

## 6. Что объясняет 45,7× / 11,7×

### 6.1. Разделение ordinary, различающих контролей и истории

| Срез | Расчёт | Значение |
| --- | --- | ---: |
| Исторический полный CI | 20 508 /449 | 45,6748× ≈45,7× |
| Заданный основной S_M | 20 327 /449 | 45,2717× ≈45,3× |
| Девять SmallSort файлов | 5 241 /449 | 11,6726× ≈11,7× |
| Вне SmallSort в S_M | 15 086 /20 327 | 74,2166% |
| Вне SmallSort в историческом срезе | 15 267 /20 508 | 74,4441% |

Вне SmallSort 15 086 =14 690 исследовательских +394 предлагаемых приложений
+2 check-cfg. Исторический коэффициент отличается только181 строкой
workflow координатора. Отбор целых файлов §2 не объясняет самих5 241 строк.

Прежняя категория (а)4 328 чрезмерно объединяла свойства и снятые опыты.
После исправления dead388 и shared534 остаток **4 319** разделён ниже.
Правило построчное и непересекающееся: (б) —119 SS +15 module root и
merge:1–753 минус353 dead; (в) —точные388 §5.1; из остальных строк явно
выделены интервалы (а2)/(а3), остальное —семейства (а1). Разделители относятся
к соседнему интервалу. Это роль исходника, не proof credit и не минимально
необходимый размер. В смешанных ordinary семействах остаются71 C-entry;
они не выдаются за350 ordinary этой категории. Пять positive K15 entries
считаются в (а2) вместе с парными mutant invocations один раз.

| Категория | Что измерено | Строк | /449 |
| --- | --- | ---: | ---: |
| (а1) Семейства с ordinary entries и общий для них код | Перечисленные ниже интервалы; 350 O /71 C | 2 182 | 4,8597× |
| (а2) Различающие контроли | R11, control A, K15, C5, Drop, smoke; 5 O /29 C | 590 | 1,3140× |
| (а3) Исторические диагностики/скрининги | Перечисленные ниже отдельные семейства; 0 O /170 C | 1 547 | 3,4454× |
| (б) Общее устройство спецификаций/подключения | 119+15+(753−353); shared helpers, не вся механика generators | 534 | 1,1893× |
| (в) Исходниково неиспользуемый остаток | merge362 +network26 | 388 | 0,8641× |
| **SmallSort** | 2 182+590+1 547+534+388 | **5 241** | **11,6726×** |
| Вне SmallSort | Остальные46 файлов S_M | 15 086 | 33,5991× |
| **S_M** | 5 241+15 086 | **20 327** | **45,2717×** |

Таким образом, коэффициент11,7× нельзя объяснять преимущественно большей
широтой доказанных свойств. **1 935 строк (1 547+388), 36,92% SmallSort —
исторические семейства и unused**, отдельно от534 общей спецификации,
2 182 ordinary-bearing и590 контрольных строк. Больший домен и композиция
объясняют часть объёма, но измеримый исторический слой существенен.
Сворачиваемые76–89 строк находятся внутри названных категорий, а не
прибавляются к5 241; часть этих повторов уже не понадобится при выносе (а3).

#### (а1) Точные интервалы и их смысл

Все эти интервалы предлагается **оставить в PR**. Это общий код семейств
с ordinary entries; наличие C-invocations в таком интервале не создаёт
для них новый credit и не препятствует последующему более тонкому отбору.

| Модуль | Непересекающиеся интервалы S_M | Строк |
| --- | --- | ---: |
| merge.rs | 754–785;964–1304;1353–1428;1438–1448;1535–1619;1645–1960;1975–1988;1997 | 876 |
| network.rs | 1–49;63–80;488–501;513–545;997–1011;1036–1119;1131–1177;1189–1897 | 969 |
| correct.rs | 1–74;88–169 | 156 |
| assembly.rs | 1–105;143–166 | 129 |
| smoke.rs | 1–35 | 35 |
| uninit.rs | 10–12;64–77 — imports и helper обычных stable-ZST proofs | 17 |
| **Итого** | | **2 182** |

#### (а2) Для каждого семейства: что именно различается

Все перечисленные контроли предлагается **оставить в PR** с отдельным
opt-in запуском. Проверены и источник ожидаемого FAILED, и положительная
сторона/достижимость. Результаты ниже source-reported: не новый запуск и
не самостоятельная повторная приёмка на S_M′.

| Семейство / точные интервалы | Строк | Различение, наблюдавшийся результат и источник | Предложение и зависимость |
| --- | ---: | --- | --- |
| R11: network:50–62; merge:947–962,1620–1644; correct:75–87 | 67 | Same-index swap, несортированные halves u8/u64N4, bad-prefix u8[4,0,2]. Требуется FAILED на конкретном requires при корректной memory geometry. W3-REQUIREMENTS:b6b480cc:34 /Д12 и раскрытие:127 сообщают локализованные R11; insertion —build6e32e784 | **В PR**: проверяет применимость stub preconditions; не заменяет доказательство всех requires |
| Control A: merge:1305–1352,1515–1534; network:1012–1035,1120–1130,1178–1188 | 114 | W1 merge и W2 merge false assert ↔normal/panic reachability; networkN2 false assert ↔N18 реальная merge-route reachability; quiet cut и actual K16 template после merge имеют собственные false asserts. RESULT-merge@S_M:2210–2226,3281–3294; RESULT-network@S_M:799–806,958–959,1124–1127: ожидаемые FAILED у assertions, SUCCESS/covers у парных positive. W1 run46 имел общий gate false из-за другого B-control; используется повтор47, gate true. Quiet negative проверен отдельно; его результат не выводится из соседнего имени | **В PR**: чувствительность к assertion/ord-cut и невакуумность конкретных шаблонов. Нужны прежние cut helpers/reading comparator; не приписывать should_panic текущему W1-A |
| K15: mutations:1–250; assembly:106–142; network:1898–1905 | 295 | Пять общих original/copy witnesses: swap, insert, merge_up advancement, merge multiplicity при arbitrary comparator, presorted_len; отдельный старый K10N10 mutant. Раскрытие@b6b480cc:136–159: пять positive SUCCESS/covers6/6, пять localized mutant FAILED и дополнительный K10 FAILED | **В PR**: все five mutant bodies нужны даже без собственных entries; свидетельство выбранных пар, не mutation-completeness прежнего набора |
| C5: merge:1449–1514 | 66 | Четыре операции после honest normal merge: false intrinsic assume, overflowing unchecked_add, overlap memcpy, out-of-allocation ptr.add. Раскрытие@b6b480cc:152–155 —четыре конкретных FAILED, covers1/1, без should_panic | **В PR**: фактические sensitivity checks четырёх операций; не полный UB-классификатор |
| Drop: merge:1961–1974,1998–2015 | 32 | `drop_control_a` intentionally false (:1970) ↔`drop_reachable`; duplicate-tag и extra-drop mutants различают loss/duplication и лишний destructor. RESULT-merge@S_M:1137–1138 —FAILED/SUCCESS, covers3/3; :1269–1280 —два ожидаемых FAILED с entry cover1/1 | **В PR**: normal-return counter+tags; верхние24/32 ниже —другая positive diagnostic семья, не эти контроли |
| Smoke: smoke:36–51 | 16 | `ok`: u64=true,b9=false плюс u8 x covers0/255, SUCCESS2/2; `control_must_fail`: ложное b9=true, FAILED. Раскрытие@b6b480cc:156–157; actual source:38–50 | **В PR**: negative predicate и sanity covers; X0 domain erratum сохраняется (§4.1) |
| **Итого (а2)** | **590** | | |

#### (а3) Для каждого семейства: что отправляется в историю

Нулевая ordinary-численность сама по себе не причина исключения:
R11/control A выше остаются. Здесь основание —alternative formulation,
измерительный/ресурсный/модельный опыт либо незачтённый screening без
действующего отдельного negative distinction. Изоляция в research не
отменяет опубликованные результаты; callee prerequisites и воспроизведение
нельзя потерять. Эти зависимости —gate альтернативы §6.3, а не разрешение
просто вырезать все C-items.

| Семейство / непересекающиеся интервалы | Строк / C-entries | Статус и отличие от (а2) | Предложение, причина и зависимость |
| --- | ---: | --- | --- |
| Merge scaling/toy/plain: merge:786–946;963 | 162 /13 | Символьные/фиксированные merge2..32, toy32, plain32 и вариант sorted-only: инструментальные/attribution опыты, не intentional FAILED. R11:947–962 вычтен отдельно в (а2), поэтому здесь13, не14 C | **В исследовательскую ветку**: сохранить scaling/resource/formulation provenance. Общие spec/helpers могут остаться в PR; перенос callee results не становится новым proof |
| Drop upper24/32: merge:1989–1996 | 8 /4 | Positive count/permutation на general/stable N24/32; это не duplicate-tag/extra-drop. RESULT-merge@S_M:1395–1396 различает SUCCESS count и TIMEOUT permutation для24; не заявляется полнота32 | **В исследовательскую ветку**: дополнительные upper-domain diagnostics, не ordinary поддержка low/upper≤16 |
| E-2: merge:2016–2077 | 62 /5 | u64 insertionN16..20 всеoffset, **32GB resource**, вне ordinary CI credit; основной B4 теперь в W3 network | **В исследовательскую ветку**: дополнительное resource evidence, исходник/результаты по pin, не удалять историческую запись |
| Network alternative encodings/insertion: network:81–238;265–487 | 381 /40 | sort9/13 real/stub/01/permutation; offsets1/9/13, old invariant-named proof, tail prefix/interior. Нет deliberate FAILED; это исполняемые positive/alternative proofs. Dead helper239–264 уже вычтен в (в) | **В исследовательскую ветку** как отдельное воспроизводимое приложение; `insert_tail_net_*`, prefix/region callee evidence может быть prerequisite нынешних stubs —до выноса сохранить точную callee↔caller привязку/команды и возможность проверки на S_M′. Обычные K9s/K8r не подменяют backing/comparator этих случаев |
| Старый O1N17: network:502–512 | 11 /1 | Positive single length17, arbitrary comparator/real body; current ordinary no-merge ниже содержит каждую0..17 | **В исследовательскую ветку**: прежний разрез измерений; общий comparator488–501 и ordinary513–545 остаются |
| Network band/fixed/retry: network:546–760 | 215 /27 | Сети/insertion в разных verified-stub сочетаниях, fixed lengths и direct/permutation/retry; нет ожидаемого negative check | **В исследовательскую ветку**: альтернативы solver/instrumentation, один ordinary из прежнего488–760 остаётся в PR. D2/D3 здесь тогда не применяются повторно |
| K13/Cell: network:761–996 | 236 /6 | Начальные route/insertion/tag-permutation опыты с Cell<K13Tagged>; не source FAILED controls. Обычные O3/точныеoffset proofs —в поздних семьях | **В исследовательскую ветку**: сохранить разные property/status и связь с O3; не выдавать старые bounded positives за всё C3 |
| L2 network/screening: correct:170–230 | 61 /15 | Два networkN17 caller TIMEOUT600 и13 solver sweep entries TIMEOUT120; общие current fallback/GS/scratch templates выше остаются | **В исследовательскую ветку**: не ordinary proof credit и не negative sensitivity; сохранить объяснение отсутствующего u64 scratch prerequisite |
| ZST/U1: uninit:1–9;13–63;78–428 | 411 /59 | ZST volatile/nonvolatile/input variants и isolated model checks; U1 real-route/read-back и intended positive/negative pairs. Actual U1 unsupported, covers0, не validated distinction; таблица пар ниже | **В исследовательскую ветку** как диагностическое приложение: helper64–77/imports10–12 оставить в PR; явно сохранить unsupported/непроверенный network-sort, отдельный uninit-флаг и все source inputs для возможного supported-tool опыта |
| **Итого (а3)** | **1 547 /170** | **0 ordinary** | |

Проверка **каждой пары U1**, а не вывод по имени файла:

| Source S_M / пара | Ожидание при поддержанном `-Z uninit-checks` | Исторический наблюдаемый исход и решение |
| --- | --- | --- |
| uninit:331–350, scalar initialized/uninitialized | SUCCESS ↔FAILED именно на чтении uninitialized scalar | RESULT-w3-l1u@S_M:418–419: оба FAILED с unsupported B, covers0/1. Это не killed negative и не successful positive; (а3), research |
| uninit:351–394, scratch47 untouched / MaybeUninit-written / raw-written | FAILED ↔SUCCESS/SUCCESS после реального generalN8 на том же scratch48 | RESULT-w3-l1u@S_M:420–422: все FAILED с unsupported A при scratch layout, covers0/4. Ни одна из трёх intended сторон не достигла нужного read; (а3), research |
| uninit:395–428, network-layout cell31 untouched/written | FAILED ↔SUCCESS при одинаковом backing32 и инициализации0..17 | RESULT-w3-l1u@S_M:423–424: оба FAILED unsupported B, covers0/2. Это isolated layout, actual network-sort с uninit-флагом не запускался; (а3), research |

В запущенных девяти U1 entries были также generalN8/N16; общий итог
unsupported по RESULT-w3-l1u:387–451. Незапущенным generalN32/network18/32
не приписывается этот run. ZST model diagnostics могут различать поведение
моделей volatile/ptr::read, но это не отрицательные контроли runtime sorting.

Перекрёстная проверка классов:

| Модуль | а1 | а2 | а3 | б | в | Сумма |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| merge.rs | 876 | 207 | 232 | 400 | 362 | 2 077 |
| network.rs | 969 | 67 | 843 | 0 | 26 | 1 905 |
| correct.rs | 156 | 13 | 61 | 0 | 0 | 230 |
| assembly.rs | 129 | 37 | 0 | 0 | 0 | 166 |
| mutations.rs | 0 | 250 | 0 | 0 | 0 | 250 |
| smoke.rs | 35 | 16 | 0 | 0 | 0 | 51 |
| uninit.rs | 17 | 0 | 411 | 0 | 0 | 428 |
| SS additions/root | 0 | 0 | 0 | 134 | 0 | 134 |
| **Итого** | **2 182** | **590** | **1 547** | **534** | **388** | **5 241** |

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
- **Устранимый исторический слой:** конкретные388 строк §5.1;
  против них есть source-search, в отличие от общего предположения
  «все длинные однотипные строки — дубли». Отдельно1 547 строк
  исторической диагностики/скринингов выделены в (а3), не в ordinary свойства.

355 ordinary против25 source entries — сравнение организации наборов,
не коэффициент силы доказательства. Некоторые наши statements шире по
перечисленным осям, но complete thresholds correctness, aliasing/uninit/
unwind, другие primitive/default-order instances остаются открытыми.
Разрешённый аудит не позволяет приписать каждому дополнительному свойству
точную долю **семантической** разницы 4792=5241−449 строк; таблица выше
честно учитывает собственный текст по явному правилу без такого домысла.

### 6.3. Остаточный объём: две разные операции

Нельзя складывать «обобщить шаблон» и «перенести содержащую его семью»
как независимые экономии. Поэтому расчёт разделён на сохранение всех
625 entries и отдельный отбор170 исторических C-entries из (а3).

| Сценарий предложения | Девять SmallSort файлов | С Cargo (+2) | С двумя неизменёнными приложениями S_M (+394) |
| --- | ---: | ---: | ---: |
| Исходный выбор файлов, без proof-редактуры | 5 241 | 5 243 | 5 637 |
| Только388 unused §5.1 | 4 853 | 4 855 | 5 249 |
| Unused +все D1–D7, **все625 entries сохранены** | **4 764–4 777** | **4 766–4 779** | **5 160–5 173** |
| Отдельный вариант: unused +вынос1 547 строк (а3), без дедупликации | 3 306 | 3 308 | 3 702 |
| Тот же вынос +(только оставшиеся) D4/D5/D6 и два блока D7 | **3 275–3 283** | **3 277–3 285** | **3 671–3 679** |

Сохранение всего состава: 5241−388−(76..89)=**4764..4777**,
примерно10,6×449. Это исправленный прогноз вместо4850..4864.
Имена/домены/covers и625=355 O+270 C предполагаются сохранёнными;
line refs и generator attrs проходят будущую сверку. Строго только
unused, без принятой дедупликации, даёт4853, а не старый4864.

Отбор (а3) —другая гипотеза: 5241−388−1547=**3306**;
в остающемся source —**455 entries (355 O+100 C)**. Исходные170 C не
объявляются failed/мёртвыми: их исполнение/публикация в основном пакете
заменяются доступным исследовательским приложением. Это требует решения
П-3 о callee binding и воспроизведении, а не автоматического вырезания.

После такого отбора D1/D2/D3 находятся в вынесенных network-опытах:
их экономию не вычитать вторично. D4 сохраняет9–11, D5 —6–8,
D6 —4–8; у D7 остаются лишь два3-строчных блока correct:18–20 и148–150,
то есть4 строки экономии (третий181–183 уже в вынесенном source).
Всего23–31, 3306−(23..31)=**3275..3283**, около7,3×449.

Последний диапазон —**условная смета отбора**, не доказательство, что
этого объёма достаточно для подачи. До применения необходимо обеспечить:

- неизменные свойства/типы/длины/regions и355 ordinary, все различающие
  R11/K15/C5/control A/Drop/smoke из (а2), stable-ZST helper/imports;
- точную callee↔caller карту для retained `stub_verified`: часть positive
  callee proofs была C в (а3). Если нужный proof/пара не воспроизводится
  на S_M′ через закреплённое приложение, его source нужно оставить в PR,
  увеличить смету на реальные строки и обновить X0. Исторический PASS
  на другой allocation/comparator не закрывает этот gate;
- сохранение истории/полных диагностических inputs по pin, команд ordinary
  и отдельного приложения, связанного с новым source, без переноса статусов
  TIMEOUT/unsupported в credit. Убранный callee нельзя заменить false assume;
- новый состав/qualified names/partitions и полный П-6 на итоговом source.

В основном сценарии76–89 не учитываются широкая cfg-перекомпоновка,
редактура комментариев, эффект rustfmt, возможная дальнейшая очистка
shared helpers после архивации и новые строки reviewer entry. Форматирование
может как убрать пустые строки, так и увеличить длинные строки переносами;
его net эффект **не измерен**. Ни один диапазон не является измеренным
numstat S_M′ или обещанием Kani-equivalence, времени и памяти.

## 7. Предложения для П-3/П-5 — не решения

Любое изменение proof-кода, имён/состава означает: run старой версии
не проверяет итоговый S_M′. После принятых изменений —единый полный П-6,
включая4×Ubuntu (`KANI_JOBS=2`)+4×macOS, штатные параллелизм/partitions и
базовые std entries. X0 source SHA/Item/Macro line, target-specific lists
и раскладка обновляются; T/P/H/M новой базы до измерений UNKNOWN.
Здесь ни одна из этих проверок не запускается.

| ID | Конкретное предложение / файлы | Имена, состав, partitions | Последующая проверка | Риск |
| --- | --- | --- | --- | --- |
| П3-A | Исходный выбор целых файлов §2; устойчивые приложения вместо43 файлов истории вне library | Source состав625 без изменений на этом первом уровне | Numstat BASE...S_M′, ссылки/вход воспроизведения, П-6 по фактическому влиянию | Потеря replay/предпосылок при исключении custom tooling |
| П5-A | Удалить388 строк §5.1 из merge/network, включая boundary helper и правильные разделители | Все625/355/270 и домены ожидаемо прежние, line refs меняются | Source search/graph, X0 refresh, Kani и полный П-6 на финальном source | Ошибка границ; активные merge629–640/light/helpers сохранить |
| П5-B /D6 | Макрос insert_tail_int/bytes merge1121–1147, экономия4–8 | Имена/C/unwind34/len2..16/type selection/covers прежние | Review expansion, обе C-entry, Kani/П-6 | Изменение instrumentation или типов |
| П5-C /D7 | correct три assertion blocks →existing checker merge1645–1658, visibility pub(super), экономия6; при архивации network stub —только4 | L2 имена/cfg/stubs/input-output/comparator прежние, места assertions меняются | Review semantic equivalence, callee/caller Kani и П-6 | Потеря property либо двойной вычет уже вынесенного блока |
| П5-D | Переписать комментарии §5.3; убрать ошибочную CD-1 привязку merge1305–1307 | Имена/attrs/код неизменны | Текстовый diff/ссылки; при strictly comments-only отдельный Kani из-за слов не нужен | Стереть caveat/происхождение или приписать should_panic текущему control A |
| П5-E | Исправить две smoke C-domain записи X0 по actual source | 625/355/270 и source не меняются | Только metadata/text сверка отдельным заданием | Лишние типы/covers в отчётном claim |
| П3-B (альтернатива) | Семейства (а3) из §6.1 —в research/replay приложение; оставить ordinary+а2 и shared dependencies | Убираются170 C entries, ordinary355 ожидаемо прежние; remaining455=355+100. Module-переезд/изменение полного имени требует отдельного пересчёта | Dependency closure/точные callee pairs/применимость старых результатов; обновлённый X0, оба cfg lists, доступное воспроизведение, Kani и полный П-6 | Утрата callee prerequisite либо невоспроизводимый архив. Если gate не выполнен, соответствующие proof sources остаются в PR и смета увеличивается |
| П5-F | Сохранить exactN/backing/start/offset таблицы и все их клетки; не заменять их символическим общим proof ради меньшего числа строк | Исходные имена/домены сохраняются | Текстовая сверка решения сохранить; иной проект требует Kani/нового X0/П-6 | Сокращение домена или потеря solver tractability |
| П5-G1 /D1 | Два permutation generators network153–174/178–200 →один с forwarded meta;18–20 строк | Generated names, cfg, plain proof/count/frame/covers прежние; macro name и line refs меняются | Expansion/attrs/X0, оба real/stub варианта Kani/П-6 | Stub утечёт в real case или потеряется explicit count |
| П5-G2 /D2 | Два band generators network374–397/551–575 →один с attrs;21–23 | Каждый lo/hi/backing/cover list и stub policy прежние | Те же Kani и X0/П-6; не заменять no_merge с его собственными covers | Перепутать insertion-stub/tail-stub либо изменить messages/достижимость |
| П5-G3 /D3 | fixedt8_u64 network632–647 выразить через расширенный fixed generator599–619;12–13 | Все four fixed names/N/cfg/covers, tail-stub только на прежнем имени | Review generated attrs, real/stub N8 Kani/П-6 | Дополнительный stub попадёт в обычный fixed8 |
| П5-G4 /D4 | merge1582–1605 →existing by_len с post-call covers;9–11 | Два имени u8/u64, constN2/3/4, attrs и normal-return covers прежние | Review order/covers и обе callee entries Kani/П-6 | До-call cover вместо после-call ослабит достижимость |
| П5-G5 /D5 | merge1311–1330/1334–1352 →общий control-A helper с callback, return исходного v;6–8 | Два fn имени/stub attrs; различающиеся cover/false-tail сохраняются | Оба expected FAILED/SUCCESS и локализация/covers, Kani/П-6 | Потерять отрицательную чувствительность или переместить cover за failing check |
| П5-H (отдельная альтернатива) | Свёртка181 cfg annotations §5.2, theoretical net169–171, не включена в основной прогноз | Только module-scope forwarding; сохранить все cfg effects и qualified names. Обычный вложенный модуль непригоден | Сначала конкретный layout/net подсчёт, dependency/macro order, два cfg lists, Kani/П-6 | Скрытая потеря gate/visibility; перекрытие с D6/архивацией, нечитаемая перегруппировка |
| П5-I | Привести итоговые proof-файлы к rustfmt в разрешённом будущем этапе; scope проверить по §7.1 | Имена/attrs/домены/состав ожидаемо прежние, line refs меняются; **вклад в число строк не измерен** | Применимая форматная проверка П-6; актуальный X0, общий code-change П-6 уже после всех правок | Неустановленный bootstrap scope и различный formatter output; whitespace не доказательство семантического PASS |

`insertion_inv_o1_u64` не unused: исполняет реальный insertionN8/offset1
с verified tail. Вариант «сохранить все625» оставляет её и переописывает;
в варианте П3-B она относится к историческим positive experiments и может
быть вынесена с ними после callee gate. Она не тождественна соседнему
actual-tail `insertion_o1_u64` по способу доказательства.

### 7.1. Что установлено о форматной проверке

Проверен **только существующий в репозитории source**, без rustfmt/rustc,
без checkout/fetch внешнего Rust. В S_M `.github/workflows/rustc.yml:20–35`
задаёт Ubuntu/macOS и вызывает `scripts/check_rustc.sh`. Скрипт :46–48
получает commit из `rustc --version` (здесь не выполнялся), :69–78 загружает
внешний Rust и submodules, :81–84 заменяет **весь library**, включая
`library/core`, его локальной копией. В полученном внешнем дереве :87–89
выполняется configure, а **:106** —`./x fmt --check` без path аргумента
(:104 в этом pin —комментарий). Ни скрипт, ни workflow здесь не запускались.

В этом checkout на S_M нет корневого rustfmt.toml/.rustfmt.toml и нет
`src/bootstrap`. Найдены лишь конфигурации nested stdarch/compiler-builtins;
они не устанавливают traversal/skip правила для `library/core`.
**Установлено:** изменённый core копируется в проверяемое внешнее дерево и
workflow содержит format gate. **Не установлено:** выберет ли именно
загружаемый bootstrap formatter все core/Kani child modules и с какими
skip/max_width правилами. Отсутствие конфигурации здесь не означает
неприменимость; окончательный scope и outcome остаются проверкой П-6.

Статический подсчёт S_M подтверждает9 runs из≥2 пустых строк, то есть
**11 лишних blank lines** при норме одна: merge1353–1354,1411–1414,
1427–1428,1438–1439 (6 лишних); network1067–1068,1176–1177,1653–1654,
1659–1660,1896–1897 (5). Это точнее, чем называть11 отдельными runs.
В merge21 строка, в network29 строк длиннее100 символов; например
network:1760 имеет104 символа. Это признаки для форматного review,
**не вывод о конкретном rustfmt failure**: formatter не запускался,
активный внешний конфиг не установлен. Удаление unused/архивация уже
может поглотить часть этих строк; отдельно11 не вычитается из §6.3.

X6/X7 не открываются. Принятые правки общих proof-файлов выполняются
до фиксации S_M′/X0 и выдачи дальнейших кодовых заданий. Полные прочие
PR checks П-6 —отдельное поручение; обычные8 partitions не заменяют их.

## 8. Проверка бумажной правки R9

В этой сессии изменён только этот документ. Статически проверены:

- все55 путей/20327 добавлений, исходный выбор10/5243 +2/394 +43/14690;
- непересекающееся построчное разбиение5 241 =2182+590+1547+534+388,
  включая обновлённые границы и единственное определение boundary helper;
- распределение625 X0 entries по Item line: (а1)350 O/71 C,
  (а2)5 O/29 C, (а3)0 O/170 C; hypothetical remaining355 O/100 C;
- все пары из R9, бюджеты их замены и отсутствие двойного вычета при
  альтернативном архивировании; standalone cfg77+104 и их130/50/1 видов;
- source workflow/script и отсутствие локальной bootstrap-конфигурации;
  форматирование/его net effect не измерены;
- `git diff --check` и whitelist только SUB-P12-INVENTORY-2026-10-28.md.

Kani/rustc/cargo/CBMC/rustfmt, builds/workflows, CI status polling и внешние
PR/comments не выполнялись; `library/` и документы X0/W3 не изменены.
Commit/push —в прежнюю ветку без force. Все доказательные результаты
остаются source-reported с исходными пределами; предложения не объявлены
выполненным П-3/П-5 или новым proof credit.
