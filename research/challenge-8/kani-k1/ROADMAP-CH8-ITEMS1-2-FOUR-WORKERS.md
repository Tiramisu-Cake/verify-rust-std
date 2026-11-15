# Сводная дорожная карта Challenge 8 — четыре воркера, два proof-профиля

2026-11-16. Предложение после аудита пункта2; **новые решения и budget — после review владельца**.
Это верификация корректности, не security-работа. Документ не выдаёт задания, не меняет принятые W0 и не запускает CI.
Источники: [пункт1 v2](PLAN-CH8-ITEM1-REMAINING-v2.md),
[пункт2 v2 с ответами R1–R9/A1–A9](PLAN-CH8-ITEM2-SORTING-v2.md),
[W0-U](TASK-CH8-W0-U.md), [W0-A1](TASK-CH8-W0-A1.md).

## 1. Стратегия и границы двух путей

**Приоритет — принимаемый функциональный результат пункта2 S1–S5:** threshold16/32, primitive/default order,
actual ensures/PFC, symbolic N и вмещающийся organizer CI. Он не ждёт слияния C2/SEL1.
Полнота всего Challenge 8 по-прежнему включает пункт1; functional result без extra-UB раскрывается как таковой.

| Кампания | Исходники и tool pin | Что в ней устанавливается |
|---|---|---|
| **S / сортировка** | Std branch от опубликованного#752 `872d5a43380752786415bc00d2a12ce0e930cb37`; clean upstream Kani `0aac16ef62da9e9d5645782d458593e5d78143ba` | Finite threshold sorting contracts, organizer flags, extra-UB OFF. Новая std verification source, отдельный exact SHA |
| **A / safety** | Принятый std70ba+6075 и тестовые overlays; SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7` | Actual scratch/issue controls с uninit ON, scale; существующий W0-A1. Не новые sorting contracts |
| **U / интеграция** | Принятый стек C2+SEL1 и подготовленные PR texts | Upstream architecture/review/pin/flags path и organizer CI gate |
| **Q / качество** | Только будущий named combined source/pin | Дополнительные type/comparator/stability/extra-UB proofs после отдельных решений |

В source/tool/flags ledger хранить campaign, contract/model version, exact root/body, T/F/геометрию и свойство.
Одинаковое имя helper не связывает результаты разных pins или PFC/Original/Replace modes.
Baseline0aac в native A1 comparison и tool pin S могут использовать один source, но tests/flags/claims разные.

## 2. Владелец каждого файла и роль каждого tmux

| Worker | Основная роль | Разрешённая область изменения |
|---|---|---|
| **11** | Sorting models, KeyLess, bounded snapshots/counts, swap/network/sort4/sort8 semantic leaves | Новые `verify/sorting_model*`, `verify/sorting_leaf*`; при согласованном refactor — `verify/merge/profiles.rs`, `network.rs`, `merge.rs`, `forwarding_contracts.rs`. Не пишет smallsort.rs |
| **13** | **Единственный интегратор smallsort.rs**; S1 real contracts, S4 entry/forwarding и std proof-tree integration | `smallsort.rs`, `verify.rs` registration в **S**, core feature/check-cfg changes при необходимости, S tool_config. Только verification attrs/plumbing, без изменения runtime алгоритма |
| **14** | Уже согласованный U; общий organizer вопрос/pin bump; CI cost/coverage/oracle inventory S | `kani3300/w0-u/`, PR-01/02/минимальный INDEX, S CI-only/reports/coverage/replace-map. Не редактирует core/model реализацию |
| **15** | W0-A1, затем merge semantic proof/invariant и safety E design/controls | A1 test-only branch/module/CI package; затем `verify/sorting_merge*`, отдельные invariant/helper/control modules и E proposal. **Не применяет core-loop patch сам** |

Для helper/loop contracts, находящихся в smallsort.rs, workers11/15 отдают integrator13 compact patch proposal
и interface/obligations; правки в файл делает только13. Нельзя одновременно править его из двух worktrees
под предлогом разных строк. Integrator не меняет чужой model API без сообщения владельцу.
Worker15 работает с новыми merge-proof modules, не меняет принадлежащий11 существующий `verify/merge.rs`.
Внешний actor, не называемый worker: **координатор** создаёт remote branches, push/CI; **владелец** публикует PR/comments.

Единственный явный registration exception: старый **A1 branch** от std6075 допускает worker15 менять там
только `verify.rs`+его новый модуль по принятому заданию. Это другой source branch; его файлы не копируются в S вслепую.
Если E требует новые core loop attrs на safety branch, их интегрирует13 отдельной сессией/патчем на named base.

## 3. Source coordination и WIP

- Один текущий интеграционный std head **S**; module branches начинаются с согласованного S SHA.
  Worker сначала фиксирует write scope/interface. Интеграция и source freeze последовательны.
- A1 source tree и frozen Kani экспорт не трогаются S изменениями. Полные clones/копии target не делать:
  отдельные worktrees, разные output dirs/caches, никаких reset/clean чужих областей.
- До решения P0 работы ниже не выданы. После GO — **одна стадия на сессию каждого worker**;
  waiting for CI допускает bounded review/docs, но не второй неоговорённый implementation project.
- Compiler WIP из пункта1 сохранён: до U1 —0 новых compiler designs; после — максимум1 named feature branch.
  Shadow/Replace architecture требует feedback/design gate либо отдельного GO. Model/annotation work в std не compiler patch.
- Общий FnPtr/vtable/SCC и собственный alias model не открываются. Новый VeriFast development закрыт.
  P1 KeyLess failure → минимальный repro/решение, а не неявная реанимация большого tool-трека.
- Prototype jobs сначала jobs1 и отдельные inputs. Одновременное число fork jobs/dispatch определяет координатор;
  четыре source workers не означают четыре тяжёлых verifier job на одном16GiB runner.
- CI-only control и source/export отделены; status UNKNOWN и failed infrastructure не превращаются в proof.
  Все receipts original exits, exact hashes, property failures, per-process и concurrent RSS, корректные единицы.

## 4. Волны и зависимости

| Волна | 11 | 13 | 14 | 15 | Gate |
|---|---|---|---|---|---|
| **0 / P0** | Design/interface KeyLess + model projection, без core writes | Проверка шести impl sites, threshold/scratch clauses, clean-pin bridge | Обновлённый W0-U: PR-01/02, design note и один вопрос организаторам | Принятый W0-A1 package; новые решения не подменяют его evidence | Владелец выбирает source/pin/scope и combined budget; ничего не запущено из этого документа |
| **S1 / P1** | Реализует model/KeyLess, activation/negative controls | Интегрирует real attrs/feature gates; same-head smoke6bodies N0..3 | Готовит bounded CI request, source/mode/contract map | Заканчивает A1 подготовку; сначала собирает merge invariant/model helper отдельно | Actual core/Kani mechanism, не native prototype |
| **S2 / P2** | sort13/swap functional probe, уточняет required summary API | Интегрирует general N32 consumer; unqualified cost prototype маркируется diagnostic | Один batch трёх cost probes, считает budget/RSS/shard risk | merge32 real-body probe + ранний CAP32 invariant; A1 runtime analysis следующей сессией после координаторского CI | Monolithic или invariant; нет доказательства consumer из недоказанных leaves |
| **S3** | Qualified swap/sort9/13, insert_tail16, sort4/8 модули/controls | Последовательно применяет helper/loop attrs из proposals, ведёт общий source SHA | Domain/contract→harness inventory, негативы и replacements review | Qualified merge2..32, topology/offset coverage и loop induction | Все используемые semantic summaries доказаны на полном claimed domain |
| **S4 / P3** | Компактные checkers/model contracts; type/shape boundary rows | Symbolic-N route/entry PFC, T2→T3 composition, normal return без panic stub | Проверяет disjoint class coverage и selected target map, готовит matched-CI arms | Review merge call-site preconditions/odd cases/frame; E safety-only spike когда есть слот/GO | Threshold-domain закрыт, shape/offset claims совпадают с roots |
| **S5 / P4** | Исправления только по конкретным findings, quality opt-in отдельно | Freeze S; review снятия старых roots/обновления #752 | Linux/macOS matched baseline/new cost и ordinary organizer inventory; публикационный пакет владельцу | Проверка negative controls/Limitations и сохранности пункт1 scope | Cost gate и review-ready update, не обещание committee acceptance |

U продолжается параллельно S. Формальные даты следующих PR C2 и их merges не подставлять в календарь S.
Новая sorting acceptance ветка использует upstream fix, не требует compiler forks C2/SEL1.
E остаётся safety-only; она не блокирует finite sorting после порогового domain.
При conflict за smallsort.rs задачи13 сериализуются; добавление работников не уменьшает этот bottleneck автоматически.

## 5. Расстановка остальных дорожек пункта1

| Дорожка | Ответственный в общей карте | Когда |
|---|---|---|
| U / PR-01/02 / #3300 | 14, публикует владелец | Сразу после review поправок W0-U; не ждать окончания sorting |
| A1 scratch/scale + exact issue packet | 15 | По принятому W0-A1; результаты не prerequisite S1, фактический dispatch приоритет согласует координатор |
| E unbounded insertion safety | 15 — invariant/control design; 13 — core integration | По возможности после bounded merge pilot или в его CI-wait окне отдельной стадией. Не объявлять geometry-only инвариант uninit proof |
| Profiles static dispatch | 11 — design/implementation; ON квалификация15 | Переиспользовать plumbing, сохраняя старые P-specific orders; отдельные instances/pins/flags/receipts. Один OFF run не ON evidence |
| B census/no-requirements gate | 14 — intake/census report; новый compiler writer назначается отдельно | После U/WIP gate и свободного CI capacity. На коротком пути пункта2 не добавляет extra flags |
| C-сейчас / RFC feedback | 14 — source/frame inventory с13; tests после GO | Не дублировать maintainer alias model, не превращать frame в temporal theorem |
| D / #5104 | 14 — coordination; конкретный diagnostic owner после GO | Не дублировать maintainer; S default-u8 profile не объявлять исправлением affected array cases |

Если P2 требует занять15 merge-индукцией на весь следующий этап, E/B/C не исчезают: они явно в очереди
пункта1, с новым сроком review. Не заставлять четырёх исполнителей одновременно держать по3–4 незавершённых проекта.
Качество `(rank,id)`/stability и широкий type argument — после S5 или отдельной owner priority, без скрытой нагрузки в CI.
Прежние profiles могут сравнивать только часть значения (например u8>>1), тогда как S KeyLess использует штатный порядок.
Это разные comparator domains. Нельзя заменить все старые orders одним KeyLess и назвать прежние claims сохранёнными;
нужны P-specific static adapters либо явный scope/replacement review.

## 6. CI budget: исходные18 сохраняются; новый запрос явно отделён

Владелец уже принял до18 fork dispatch **первой итерации пункта1**. В W0 ещё ничего не запущено.
Новый план пункта2 предлагает **до14** дополнительных dispatch. Это запрос решения P0,
не автоматическое расширение старого разрешения. Если владелец не добавляет budget, coordinator пересобирает
порядок/объём в пределах18 до новых запусков; нельзя обещать одновременно обе полные программы в прежнем лимите.

| Campaign/дорожка | Cap dispatch | Учёт |
|---|---:|---|
| U | 0–1 | Принятый пункт1 |
| A1 | 2–3 | R1/R2 + один условный reserve; текущий TASK не расширять автоматически |
| E | 3–4 | Safety-only, без функциональной induction по произвольной длине |
| Профили ON | 2–3 | Qualification migrated actual profile на safety pin |
| B | 2–3 | Один census и targeted canaries/малый fix |
| C-сейчас | 1–2 | Frame/control claims, не alias model |
| D | 0–2 | Нужный maintainer contribution |
| **Пункт1 всего** | **10–18** | Существующий принятый ceiling |
| S1 mechanism | 1–2 | Новый пункт2 proposal |
| S2 three probes / early merge | 1–2 | Новый; unqualified prototypes — diagnostic |
| S3 leaves | 3–5 | Новый; batches, не сотни per-N runs |
| S4 symbolic entries | 1–2 | Новый |
| S5 matched costs/platforms | 2–3 | Новый |
| **Пункт2 всего** | **8–14** | Требует отдельного принятия |
| **Совместный верхний envelope** | **≤32** | Только при принятии18+14; совпавшие реальные dispatch считать один раз |

Общий ledger перед dispatch: unique ID, campaign/property, std/tool/head, flags, planned job/runner/time/RSS/output,
номер стадии/остаток reserve, owner GO. Infra failure расходует попытку; rerun не бесплатный.
Если один заранее спроектированный matrix-run даёт два набора evidence, он расходует один dispatch credit,
но в report сохраняются **два разных** pin/flag/property bindings. Никакого предполагаемого «reuse минус2» в budget до факта.
Автоматический upstream PR CI и человеческое review время — отдельная зависимость, не под контролем наших14 dispatch.

Для S mandatory gates:600s/root, проектная цель≤6GiB single-root aggregate, final measured jobs2 fit16GiB;
total/shard cost не хуже matched baseline и согласованного organizer envelope.
Больше symbolic roots не спасает, если худший shard/time вырос. Quality opt-in не считается обычным PR coverage.
Трёхплатформенный full compiler Gate A для frozen C2/SEL1 не повторяется для каждой std-аннотации.

## 7. Что пересмотреть в ещё не выданных W0-U/W0-A1

Эта стадия **не переписывает** принятые TASK-файлы54f8ec7982. Ниже конкретные amendments для решения владельца;
после GO координатор выдаёт ровно согласованную редакцию, без двух противоречивых copies.

### W0-U — внести до выдачи

1. Сохранить точные heads PR-01/02 и dependency#5172, series note/disclosure, owner-only publication.
2. Один organizer message вместо отдельных U/A7 вопросов. Начать с уже опубликованного прочтения:
   threshold16/32, primitive/default order, actual ensures/PFC и выбранный symbolic-N approach;
   попросить поправить его, если требуется другой scope, а не писать, что известных ответов не существует.
3. В этом же сообщении: (a) insertion helper safety за пределами callers, (b) ожидаемая type breadth/шестьbody accounting,
   (c) допустимый time/RSS/shard budget и отдельный selected-harness uninit step, (d) **bump pin до exact upstream0aac16ef62**
   с исправлениями #4908/#5116. Ясно разделить S без extra-UB и будущий A/organizer step.
4. C2 design note в #3300 оставляет свой scope/evidence; не ставит завершение C2 серии prerequisite bump для S.
   Внешние английские тексты без чужих PR ссылок и с установленной disclosure-строкой; публикует только владелец.

### W0-A1 — сохранить содержание, уточнить scheduling/binding

1. Оставить actual-body uninit scope на SEL1 и точные #5020/#4854/#5151 controls (включая autoharness и empty Drop).
   Не заменять их чистым upstream sorting campaign или обычным count oracle.
2. Указать отдельную A1 std-ветку от70ba+6075 и narrow registration exception worker15.
   SmallSort algorithm/source функции не меняет worker15; любые будущие core attrs идут через13.
3. R1 восемь ON cases и три N32 samples — scale **пункта1**, не три R6 probes.
   Не считать N32 arbitrary-bool safety normal-return measurement ценой lawful semantic consumer.
4. Сохранить2 mandatory+1 reserve cap из18. Реальные dispatch после P0 планировать рядом с S smoke/cost jobs,
   не отдавать все CI slots A1 на основании уже подготовленного workflow.
5. На уровне документа record clean upstream0aac также используется в S, но совпадение tool source не переносит verdict.
   Новый KeyLess не подставлять в A1 без отдельной ON квалификации; существующая closure оставлена.

## 8. Единые точки решения владельца

| Gate | Решение / критерий |
|---|---|
| **P0** | Принять/поправить домен и S pin; four-worker ownership; merged U/A7 message; добавить до14 к18 или ограничить общий scope. Принятые W0 остаются незапущенными; новые S задания ещё не выданы |
| **P1** | KeyLess/core и6body mechanism подтверждены actual Kani smoke. Если нет — выбрать bounded fallback/repro, не большой новый compiler проект |
| **P2** | По R6 и merge pilot выбрать monolithic или loop contract, exact leaf domains и оставшийся CI budget |
| **P3** | Semantic leaves+symbolic entries закрыты, no ord-panic stub; coverage/geometry/probe/model map полна; Default modeled=false не спрятал дыру |
| **P4** | Organizer-compatible source/pin/CI fit, table old→new, English update#752 владельцу. Полный Challenge8 не объявлять принятым до human review и разрешения remaining пункт1 scope |

Рекомендация: дать S собственный чистый путь, W14 завершает U без архитектурного ожидания S;
W11/W13 делают model+integration, W15 — измеряемый merge bottleneck, сохраняя A1/E как отдельную safety очередь.
Так четыре работника уменьшают независимую работу, а не создают четыре конфликтующие версии smallsort.rs.
