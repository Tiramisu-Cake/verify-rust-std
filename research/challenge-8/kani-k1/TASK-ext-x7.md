# Черновик X0, не выдано — EXT-COVER / X7 bounded

- **Владелец:** EXT-COVER (после отдельной выдачи координатором).
- **База:** кандидат `S_M = ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad` (L1 FINAL CANDIDATE); gate выбора `S_M`/`S_M′` — EXT R2 §8 / дополнение R8 §4 на `a03f8c3acbd87ed5c418a52561e69c63f57e94ea`. Итоговая приёмка ждёт `TODO (coordinator, final CI)`; до фиксации принятого S_M работу над кодом/доказательствами не начинать. Toolchain pin: `9461e07a`; lane BASE `d5dc2c5fbf0da8210022112de12d25dce923934f`, перепроверить pin и BASE при выдаче.
- **План:** EXT R2, §5.1 X7 и §8, дополнение R8 §4 на `a03f8c3acbd87ed5c418a52561e69c63f57e94ea`; только bounded u8-порция.
- **Результат:** новый `library/core/src/slice/sort/shared/smallsort/kani_k1/ext_insertion.rs` и `RESULT-ext-cover.md`; никаких runtime-изменений. Подключение модуля, общие manifests/таблицы принадлежат интегратору. Общие контракты меняет только специально назначенный координатор.
- **Cap Cloud Build:** $2. Общий резерв X10 ($10) не использовать. Перед выдачей первой волны: `min(B_owner,B_lane) >= spent + reserved + B_finish_minimum + 18`; обещанное повышение cap не равно выданной доле.
- **Lane:** только Cloud Build `gcb-e2-standard-4`, 16 GB, runner `gcb-e2-standard-4`; `measurement`, timeout ≤600 с на entry, `kani_jobs=1`, swap выключен; не более 20 entries и сумма timeout ≤150 мин на batch. Один unfinished build. Цель по памяти около 5 GB — ориентир, не gate и не гарантия.
- **Статус:** черновик X0, не выдано. X7 — второй slot после X6; bounded пилот планируется на 1–2 отдельные чистые сессии, после X6. Кодовое задание выдаётся только после решения по П-2 дополнения R8 и фиксации выбранной базы `S_M`/`S_M′`. Запуск только после выдачи, при принятом S_M, свободном slot/доле и проверке актуальных правил lane и бюджета координатором. В выдаче указать фазу/окно и дедлайн; координатор до dispatch подтверждает slot, бюджет и общий timeout reserve.

Плановый максимум первой волны — 4 positive callers + до 3 callee entries + 2 controls = 9 entries. При 10 мин на entry и 30 мин суммарной подготовки reserve estimate равен `(90+30)*$0.0135 = $1.62` в одном measurement batch; это резерв, не прогноз успеха или фактического расхода. Любая дополнительная geometry/preflight/batch требует пересчёта с координатором до dispatch; cap$2 не увеличивать самостоятельно.

## Вход и gate базы

Сначала принять решение по П-2 дополнения R8. Если пакет сокращён/переименован/перенесён либо принята редактура общих proof-файлов, до выдачи кода X7 выполнить отдельно разрешённые П-3/П-5 и зафиксировать `S_M′`; иначе использовать `S_M`. X0 предварительно обновляется под выбранную базу: source SHA, реестр, зависимости и раскладка. Старые T/P/H/M не являются измерениями изменённого набора: до новых результатов — UNKNOWN. До решения П-2 и фиксации базы кодовую ветку/пилот не начинать; приёмка `S_M` и отдельная выдача ресурсов остаются обязательными.

## Цель и границы

Проверить ограниченное расширение корректности вставки для четырёх source-достижимых u8-клеток. До dispatch зафиксировать один чистый comparator (существующий `lt_u8` по ключу `x >> 1` либо отдельно проверенный exact comparator); смена порядка не наследует callee credit. Claim относится к этому порядку, без автоматического обобщения до default `<`. На каждой клетке caller должен подтвердить сортированность и полную перестановку именно логического региона, его frame и геометрию; используемые verified stubs должны иметь совместимые доказанные постусловия. Это частичный bounded пилот B5, не полный диапазон B5 и не доказательство общей безопасности для любой длины/offset.

Пары первой волны (внешний network `N` указан отдельно от длины insertion-региона `m`):

| Caller-клетка | Домен | Source-маршрут |
| --- | --- | --- |
| u8 `(m=17, offset=1)` | прямой insertion | stable или unstable public sort (`unstable/mod.rs:49–52`), обычная конфигурация, `N=17` |
| u8 `(m=20, offset=1)` | прямой insertion | stable или unstable public sort, обычная конфигурация, `N=20` |
| u8 `(m=10, offset=9)` | network | unstable small-sort, внешний `N=20`, левая половина длины 10 |
| u8 `(m=16, offset=13)` | network | unstable small-sort без merge, внешний `N=16` |

До трёх дополнительных `proof_for_contract(insert_tail)` entries. Обязательные geometries, которые нужно покрыть или обосновать как эквивалентные: (a) backing `[u8;20]`, символический `tail=1..19`, который включает callee lengths 18–20, все более короткие inclusive regions, frame suffix и network N20 left region (`tail=9`, region length10); (b) backing `[u8;16]`, network N16 tails 13..15, то есть inclusive regions lengths14..16. Старый callee harness на backing `[u8;17]` не переносится автоматически на allocation20 или allocation16. До трёх entries — ceiling для этой геометрии, не обещание, что этого достаточно: если точные backing/start domains нельзя доказать в этом лимите, пересчитать scope/cap до dispatch. Два negative controls: нарушение достижимого sorted-prefix callee-precondition (R11) и потеря/дублирование значения, которое обязан обнаружить caller. Не удалять различающий control ради cap. Не включены: u64, иные offset, правая половина N20, halves N25..32, все-offset бонус К, unbounded invariant/theorem.

## Source-проверка и геометрия

Координаты ниже — в точном source `S_M`, только в разрешённых файлах std.

- `library/core/src/slice/sort/stable/mod.rs:77–83`: в обычной конфигурации stable route выбирает insertion для `len <= 20`, вызывает `insertion_sort_shift_left(v, 1, ...)`; следовательно m17 и m20 достижимы.
- `library/core/src/slice/sort/unstable/mod.rs:38–56`: при обычной конфигурации unstable public route тоже напрямую выбирает offset 1 до 20. При `optimize_for_size`/16-bit этот route заменён heapsort и не входит в пилот.
- `library/core/src/slice/sort/shared/smallsort.rs:142–169, 180–192, 311–350`: u8 удовлетворяет small network sizing; threshold 32. Network вызывается для диапазона до порога. `small_sort_network` ставит `no_merge = len < 18`; для N10 оно передаёт весь регион длины 10, выбирает offset 9 и вызывает insertion; для N16 — весь регион, offset 13. Для внешнего N20 `len_div_2=10`, первая половина получает offset 9, затем вторая половина такой же длины. Это сеть/регион, не вызов top-level sort N10 с offset 9.
- `library/core/src/slice/sort/shared/smallsort.rs:648–689`: `insertion_sort_shift_left` ходит хвостами от offset до конца и вызывает `insert_tail` на каждом; при offset1 имеются callee-регионы длин 2..m. `insert_tail` объявлен и контрактирован на строках 601–646; его контракт требует валидный writable регион `[begin, tail]` и сортированный `[begin, tail)`, изменяет только этот регион, гарантирует sortedness и probe-count preservation.
- Для u8 network-специализация/реальная диспетчеризация: `smallsort.rs:142–169`; `small_sort_network` принимает actual `&mut [T]` как `v` и отдельно заводит output scratch `[T;32]` (`:190–192`, `:327–369`). Для N20 исходный backing `v` — `[u8;20]`, левая половина — prefix длины10; scratch32 — отдельная output allocation merge, не backing halves. Для N16 backing `v` — `[u8;16]`.
- Существующие harnesses в `library/core/src/slice/sort/shared/smallsort/kani_k1/correct.rs:10–54` доказывают actual fallback body с единственным `stub_verified(insert_tail)` при N9..16; insertion routine не stubbed. Lines 56–73 показывают `proof_for_contract` на backing `[u8;17]`, tails 1..16 и frame; lines 92–129 дают пример interior scratch geometry; lines 171–199 — actual network caller с единственным stub `insert_tail`. Геометрия контракта задана в `kani_k1/merge.rs:303–329`: same allocation, положительное расстояние, writable inclusive-регион, sorted prefix.

**Preflight про узкий contract:** attrs `insertion_sort_shift_left` в `smallsort.rs:653–660` — Kani contract, не runtime-проверка; они требуют `2 <= len <= 17` и offset13 для len≥13 (offset9 для 9..12). Не применять `stub_verified(insertion_sort_shift_left)` к direct `(17,1)` / `(20,1)`: этот stub contract несовместим. Но actual stable/unstable body call через insertion routine может быть доказуем без stubbing этой функции, с `--no-assert-contracts` и единственным `stub_verified(insert_tail)`, как fallback-паттерн в `correct.rs:10–54`. Поэтому сначала проверить exact direct public caller под тем же режимом и исходным контрактным набором; до этой проверки blocker не объявлять. Для direct caller сохранить exact backing `[u8;17]`/`[u8;20]`, sortedness, permutation, frame и covers с доказанным dispatch. Отдельный kernel wrapper после провала actual caller не заменяет requested entry: без actual callsite binding это частичный результат/STOP, не GO X7 и не повод расходовать оставшийся cap на копию цикла. Не использовать `assume` для маскировки нарушенного requires или недоказанного caller-prefix, не stub-ить insertion routine и не менять runtime/общий contract.

Для network entries использовать actual callsite `small_sort_network` на N20 (левая половина) и N16 (no-merge), с проверенной привязкой наблюдения/summary к выходу insertion-региона. Допустима source-mapped композиционная обёртка, вызывающая actual sort9 и actual insertion на левой части backing20 и явно доказывающая prefix premise; её claim — эта цепочка и регион, не исполнение всего outer caller. Условный harness с построенным/обоснованным assume+cover префиксом маркировать отдельно, не выдавая за доказанный caller-precondition. N10 без merge имеет тот же m10/offset9, но иной backing и не заменяет requested N20-left. Полный N20 merge/right-half proof не требуется для этой клетки; их credit не заявлять. Самостоятельно написанная sorting loop не заменяет actual callsite. Условия и layout сети должны дать covers offset 9/13 и нужной половины. Если реальная функция/контрактная цепочка не проходит — STOP или явный частичный результат, без переписывания тела сети.

## Шаги и gates

1. После решения П-2 и фиксации выбранной базы `S_M`/`S_M′` сверить, что пути, тела, dispatch thresholds, контракты, harness templates и lane не изменились. Иначе остановиться и запросить новую постановку у координатора через свой RESULT (владельцу напрямую не писать).
2. Подготовить дизайн-таблицу `тип × route × external N × m × offset × backing allocation × start × tail-domain × callee requires/ensures × caller property`. До proof проверить размеры allocations и `start + m <= allocation_len`; для interior region сохранять внешний frame. Не считать одной длины m доказательством иной геометрии.
3. На actual caller проверить четыре exact cells. Для каждого — cover достижения нужного dispatch/региона и offset; sortedness полного логического региона; равенство полного u8-мультимножества входа/выхода; неизменность памяти вне региона на границе insertion (до последующей обработки правой половины/merge). После возврата всего N20 frame левой вставки так проверять нельзя. Никаких неявных предположений о «префикс уже отсортирован»: его доказывает предыдущий actual callee либо он строится и покрывается в standalone contract harness с ясным scope.
4. Спроектировать не более трёх callee proofs `insert_tail`, вместе покрывающих backing `[u8;20]` с символическим `tail=1..19` (в том числе callee длины18..20 и network tail9 при backing20) и backing `[u8;16]` с network tails13..15 (region lengths14..16). Для каждого символического диапазона дать covers короткого/interior/max tail и completion, assert suffix frame. Подтвердить applicability `k1_tail_pre`/postconditions, fully initialised writable allocation, sorted-prefix precondition и write frame. Если покрытие backing16 не выводится из доказательства backing20 и требуется отдельный geometry harness, включить его в ceiling3. Если нужные exact backing/start domains не помещаются в три entries или cap, STOP и пересчитать scope/cap до dispatch; не обещать дополнительные entries.
5. Два controls: (a) нарушение достижимого callee sorted-prefix precondition при корректных указателях/инициализации/границах должно проявиться как отдельное R11 failure; (b) мутант потери/дублирования значения должен приводить к FAILED на заявленном caller property. Controls отдельно от положительных entries и не входят в обычный набор.
6. При выдаче сверить toolchain pin `9461e07a` и lane BASE `d5dc2c5fbf0da8210022112de12d25dce923934f`; идентичность tooling проверять штатным `check-tooling BUILD BASE` после build по процедуре W3-RULES, до dispatch сверить исходный tooling pin/дерево. Статус, slots, отмена и бюджет — через существующий Cloud Build coordinator с сохранением phase/owner/deadline/ledger. Вносить фактические wall minutes и стоимость по формуле lane `(whole-run wall minutes + 8) * $0.0135`; учитывать setup/неудачи. До dispatch координатор проверяет общий budget, slots, дедлайн, `B_lane`, timeout и money.

После завершения каждого build получить **`smallsort-brief BUILD_UUID`** —
default authoritative interface CI evidence по действующему AGENTS;
это правило имеет приоритет перед историческими инструкциями W3-RULES/плана.
Проверять source/tool/profile, expected/actual, covers, ресурсы и review
по Brief. Если Brief отсутствует/неполон/недостаточен, записать limitation,
не выводить proof acceptance и не переходить к raw evidence. Для
административного audit необходимо отдельное явное разрешение. Не скачивать
raw GCS archives, полные verifier/Cloud Logging logs; не выполнять
`control.py download`, `gcloud storage cp`, `gcloud logging read` или
`gcloud builds log`. `VERIFIED_ARCHIVE_AND_INVENTORY` подтверждает целостность,
не formal verification. Не выставлять `download_verified` по Brief, не
менять исторические evidence/ledger. Source-reported claims, независимо
установленный credit, B1 bounded и B2 full proof различать.

### GO

- Gate маршрута пройден: четыре requested regions подтверждены actual source; тип/offset/геометрия и caller-boundary проверены, а контрактные preconditions совместимы. Direct public caller body проверен без stubbing insertion_sort_shift_left; stub только insert_tail.
- Не более трёх callee entries покрывают backing20 с tails1..19/короткие prefixes/frame и network N20 region10, а также backing16 с tails13..15/regions14..16; иначе GO запрещён без нового scope/cap.
- Все запущенные positive entries получили SUCCESS ≤600 с, все cover выполнены; каждый требуемый sortedness/permutation/frame oracle и каждый используемый callee contract проверен. Для credit именно actual caller требуется его действительный dispatch path, не только wrapper.
- Оба controls дают ожидаемое различающее поведение; отчёт точно отделяет положительные свойства от контроля и указывает каждый домен.
- Смета в $2, lane лимитах и подтверждённом общем бюджете; нет незакрытого build.

### STOP / NO-GO

Немедленно остановить расширение данного направления, записать выводы и не тратить следующую порцию, если: S_M не принят/изменился; source-route недостижим в обычном cfg; выбранный caller/stub contract несовместим (узкий attrs insertion routine сам по себе не блокирует actual body с `--no-assert-contracts`); backing allocation / provenance / sorted-prefix precondition не доказаны; трёх callee entries недостаточно для длин18/19/20 плюс network backing/interior geometry; stub применяет непроверенное или несовместимое ensures; любой control не различает мутант/нарушение; entry TIMEOUT/FAIL/cover missing; память или общий лимит lane недостаточны; сумма с подготовкой/повторами может выйти за cap$2. Не ослаблять oracle, не переносить credit между типами, длинами, offset, halves или cfg. Провал одной клетки не скрывает результат остальных; после STOP следующие entries — NOT_RUN.

## Критерий завершения и передача

Передать координатору собственный `RESULT-ext-cover.md` с точным source SHA, toolchain pin, lane BASE/check-tooling, шаблонными SHA/review request при изменении harness, listing positive/negative/NOT_RUN, entry status/time/cost, source route и backing geometry, controls, gates и точной границей credit. Отдельно указать остаточные blockers direct callers и callee geometry. X7 не закрывает all-offset B5, общий B4 any-length, u64, весь диапазон до20 либо непроверенные cells из X0. Новый шаблон требует `REVIEW REQUEST <полный SHA>`; доказательный зачёт — только после обязательного GO/review. После выданного этапа завершить строкой `X7 ЗАВЕРШЁН` в RESULT и остановиться. Этот черновик не запускает сессию, сборку или бюджет.
