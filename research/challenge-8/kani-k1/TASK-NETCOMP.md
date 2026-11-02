# NETCOMP — машинная композиция реальной сети через pair-transfer/frame/count summary

Исполнитель: Codex, свежая clean-room сессия. Worktree `/root/verify-rust-std-kani-netcomp`, ветка
`experiment/kani-k1-netcomp-20261102` от NETTHIRTEEN `23751ff775`.
Cap проекта $88.96; остаток при постановке около$11.55, не разрешение потратить его целиком.
Cap этого задания $2.50, максимум2 GCB Builds; расчёт резервов ниже. Слоты/ledger — существующий K-1 coordinator,
свой spent/reserved только по своим UUID, request_id `netcomp-*`. Каждый exact packet требует PRE-BUILD GO координатора.
Ожидание — `research/challenge-8/kani-k1/tools/k1g.sh watch UUID` с `CODEX_THREAD_ID`, затем завершить ход.
Evidence Brief / Select-Merge к K-1 не относятся. Код/ветки/diff решений конкурентов не открывать.

## Вопрос и выбранный домен

Можно ли на pin Kani `9461e07af7ec929f050aa4192f29363c9be07779` сначала для N9, затем N13 машинно получить
sortedness и full-value permutation реального `<u8 as UnstableSmallSortTypeImpl>::small_sort`, заменив только
реальные `swap_if_less` calls независимо проверенной pair/frame/count summary?

**Осознанное решение о F:** этот пилот использует новый явно фиксированный Rust-тип
`type U8Cmp = fn(&u8, &u8) -> bool`, значение — `network::StrictU8::CMP`, то есть reified `strict_less::<u8>`.
В N1/NETTHIRTEEN `let mut cmp = strict_less::<u8>` сохраняет function-item тип. Это другая мономорфизация;
их VT/успех/timeout не служат matching A/B baseline и не доказывают перенос на новый F.
Здесь в каждом leaf/caller явно `let mut cmp: U8Cmp = ...`; адаптер передаёт полученное `*is_less`,
не заменяет comparator на canonical внутри себя. Обратный перенос на прежний function-item F этим этапом
не устанавливается. Называть результат «композиция прежнего NETTHIRTEEN instance без изменений» запрещено.
Если нужен именно function-item theorem, это отдельная задача о type-compatible bridge, не тихая смена дизайна.

N9 calibration исполняет настоящий trait entry и сравнивает прямой и composed proof при одном новом F.
N13 — самостоятельный leaf и composed caller того же fn-pointer домена. Sortedness — обычный `<`,
значения целиком u8, independent arbitrary u8 probe; input без ограничений, не только ключи/0-1 inputs.
N9 проходит sort9 (25 exchanges), N13 — sort13 (45); insertion offset9/13 не делает вставок, merge не вызывается.

## Обязательное чтение

- `RESULT-NETNINE.md`, `RESULT-NETTHIRTEEN.md`, `TASK-NETTHIRTEEN.md` вместе с уточнениями.
- `verify/network.rs`: StrictU8, strict_less, count/sortedness helpers, оба direct пилота, swap_contract_u8_n9/n13.
- `smallsort.rs`: Unstable/Freeze dispatch, small_sort_network, sort9_optimal, sort13_optimal, swap_if_less.
- `verify/merge/specfix.rs`: Profile, canonical comparator, swap_geometry, pair_models/swap_transfer/swap_ordered,
  swap_profile; `TASK-SPECFIX.md` — запреты, лог-интерфейс, rustfmt/expect_check; `integwrapfix/pfc_order.py`.
- Своё прежнее доказательство механизма: `git show 8cbb267500:library/core/src/slice/sort/shared/smallsort/verify/bridge.rs`
  и `...:research/challenge-8/kani-k1/RESULT-BRIDGENINE.md`; B1/B2 — данные о merge bridge, не готовый swap theorem.
- На pin [выбор contract mode](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/transform/contracts.rs#L565):
  Check/Replace для explicit PFC/stub_verified имеют приоритет над Assert. `--no-assert-contracts` их не выключает,
  но обычный вызов контрактной функции сам по себе не заменяет PFC и проверки premises.

## Размещение и запрещённые изменения

Новый opt-in дочерний модуль `network::netcomp` под `kani_smallsort_controls`; это даёт доступ к прежним private
StrictU8/strict_less без изменения их visibility/типов. В `network.rs` разрешена только cfg-gated регистрация модуля.
Ordinary exact200, старые harnesses/targets/controls и runtime `smallsort.rs` неизменны; MACSPLIT/v6 не интегрировать.
Никаких новых контрактов на raw generic swap_if_less: у него нет универсального pair/frame post для любого FnMut,
а на pin ранее встречался contract-closure blocker при manual stub уже контрактного raw target.
Не менять Kani pin/compiler/model, organizer workflows/flags, runner или trusted rules; локальных proof/build запусков нет.

## Механизм actual call → summary

Использовать форму уже измеренного B1/B2, но считать swap-путь новой проверяемой гипотезой:

    real trait entry → actual sort9/sort13 → raw swap_if_less<T,F>
      -- kani::stub --> same-signature adapter9/adapter13<T,F>
      → closed bridge impl только u8 / U8Cmp
      → swap_net9 / swap_net13
      -- kani::stub_verified --> independently checked summary

1. Два concrete forwarder-targets `swap_net9` и `swap_net13` с аргументами
   `(v:*mut u8, a:usize, b:usize, cmp:U8Cmp, probe:u8)`. Конкретные функции уменьшают новую generic/const-generic
   неоднозначность для metadata; внутренние pure helpers можно факторизовать.
   Их actual body делает только `let mut actual: U8Cmp = cmp; swap_if_less(v,a,b,&mut actual)`.
2. Requires: canonical received cmp; initialized readable/writable full region N, a<N, b<N, a!=b;
   корректная nonnull/aligned geometry и одна allocation. Checked leaf-domain — initialized exact `[u8;N]`,
   base offset0, arbitrary distinct indices. Это не theorem обо всех backings/offsets, допускаемых predicates.
3. Modifies только `v[a]` и `v[b]`. Ensures: pure full-u8 pair transfer по pre-state `<`, ordered post-pair,
   плюс `old(count_N(v,probe)) == count_N(v,probe)` для того же by-value probe на всём N.
   Old сохраняет scalar count и pair values, не pointer с последующим чтением post-state. Ensures не вызывают callback.
   Эта count-лемма — явный network-level conservation invariant, выведенный из настоящего helper, не assume-the-conclusion.
4. Каждый leaf PFC вызывает свой concrete forwarder на полном arbitrary `[u8;N]`, independent any probe,
   arbitrary distinct indices и canonical U8Cmp. **Ни manual stubs, ни stub_verified у leaf нет**: он исполняет
   настоящий raw helper. Проверить pair/full-count/assigns и explicit unchanged values вне выбранной пары.
   Covers — swap/no-swap, оба направления/края и interior pair, probe hit/miss; только достижимые для этого leaf.
   Старые swap_profile PFC — основание для дизайна, не автоматическая проверка новой count-леммы или другого N.
5. Адаптер имеет параметры/возврат raw swap и два generic T/F как в raw target. Closed trait dispatch по образцу
   MergeBridge реализован только для u8/U8Cmp; unsupported T/F не получают blanket/fallback impl.
   Для N9/N13 — отдельные adapters/bridge dispatch, без добавления generic N к заменяемой raw сигнатуре.
   Он передаёт **фактические** v/a/b/*is_less/probe в соответствующий forwarder.
6. Перед реальным entry caller явно присваивает dedicated proof-only context: pointer на свой exact array,
   independent probe, scalar initial count и `hits=0`. Это код присваивания/вычисления, не kani::assume.
   Context не используется runtime source; его setter вызывается вне PFC targets. Probe/base/initial-count далее readonly.
   В adapter до summary проверять literal kani::assert: actual base совпадает с зарегистрированным root,
   a/b distinct/in-range, received cmp canonical. После failed comparator guard возврат без вызова summary.
   Memory requires summary должны быть установлены из реального состояния, не assumed вручную.
7. В adapter вне contract target увеличивать только dedicated ghost hit counter; после verified forwarder
   проверить `count_N(actual_base, ctx_probe) == ctx_initial_count` — invariant после каждого реального exchange.
   Ghost counter — отдельное proof instrumentation, не часть реального helper write-set; target/summary его не пишет
   и не havocs. На возврате caller проверяет hits==25/45, probe/base/initial-count frame, canonical cmp unchanged,
   sortedness и полный independent-probe count против pre-state snapshot.
   Ни mutable trace, ни probe не должны попасть в разрешённые writes swap-summary.
8. В composed root явно обе аннотации: `stub(raw swap_if_less, adapterN)` и `stub_verified(swap_netN)`.
   Иные std helpers/сеть не заменять. Одного stub_verified на forwarder недостаточно: real network зовёт raw helper.
   Перечень25/45 actual call sites и аргументов приложить к PRE-BUILD review, сверив с исходником; source map — audit
   data, не копия сети для выполнения. Hits и binding control ниже должны показать перехват реального пути.

## Общие fixtures, covers и отрицательные контроли

A/direct и B/composed для N9 используют общий caller/oracle, exact backing9/offset0, одинаковые unrestricted inputs,
independent probe, явный U8Cmp/canonical value, unwind25, flags. В A нет stubs; в B только указанные два.
Разница — summaries и объявленное ghost instrumentation. Runtime алгоритм/схему comparator networks не копировать.
Положительный caller имеет прежние4 covers: sort moves, probe hits, probe misses, duplicates; adapter-summary-return
и complete-hit-count covers допустимы, но все required covers положительных строк должны быть SATISFIED.
Covers размещать в uncontracted caller/adapter, не в ensures/PFC target с generated closure copies.

Два negative на каждый проверяемый N:
- **Actual binding / comparator guard:** настоящий trait entry, те же B annotations и ctx, но received U8Cmp value
  `always_true_u8`. Только в этом narrow control разрешён неверный comparator. Guard расположен в том же adapter,
  который использует positive, до verified summary, с literal `netcomp canonical comparator required`.
  В этом negative не проверять sorted/count результата; требовать entry/adapter reachability и FAILED только
  на указанном guard (возможны повторения одного check при нескольких raw calls). Без перехвата raw этот guard
  не исполнился бы. Direct call contracted forwarder вместо настоящего network не считается binding control.
- **Count sensitivity:** input=[0;N], probe0; настоящий composed путь с canonical U8Cmp, hits==25/45 и его invariant
  обязаны пройти. После возврата поставить v[N-1]=1, отдельно проверить sortedness и достижение count-check;
  expected FAILED только unique literal `netcomp N9/N13 negative: full-value count preserved`. Count(0) N→N-1,
  порядок сохраняется. Positive inputs/probe этим witness не заменять.

Exact expect_check задавать реальными kani::assert literals до GO. Unsupported/unwinding/UB/geometry/root/hit/frame
failure, ERROR/OOM/TIMEOUT не засчитывать intended negative. Сохранять все unexpected checks; не маскировать exit code.

## Ступени и бюджет

Стандартный K-1 measurement, controls:true, jobs1, uninit off, timeout10min, k1-standard4, прежние flags/pin;
unwind25 и unwinding assertions. Без увеличения RAM/timeouts, новых experimental profiles или изменения validator.
Новый bound/механизм при необходимости сначала вернуть координатору с причиной, не расширять постановку самостоятельно.

**G1 / N9 calibration — ровно5 rows:**
1. No-stub PFC leaf swap_net9 на arbitrary pair/exact backing9.
2. A9 actual-entry direct, новый explicit U8Cmp, sorted/count.
3. B9 actual-entry composed, invariant/hits/sorted/count.
4. N9 actual binding wrong-cmp negative.
5. N9 post-return sorted corruption negative.
Резерв `(5×10+30)×$0.0135 = $1.080`.

G1 gate: source/request/pin/tooling identities совпадают; все3 positives SUCCESS с required covers;
оба negative FAILED только на intended checks; geometry/frame/hits корректны; ordinary200 unchanged.
Если gate выполнен, G2/N13 разрешён в рамках задания только после нового PRE-BUILD GO.
Если A9 либо другой positive TIMEOUT/OOM/FAILED/UNKNOWN — остановиться и сохранить уже установленные per-row facts;
новой постановки N13 в этом задании не начинать. Не объявлять весь этап PASS по одним controls/B.

**G2 / N13 — ровно4 rows, только после G1 gate:**
1. Новый no-stub PFC leaf swap_net13 на arbitrary pair/exact backing13.
2. B13 actual-entry composed, полный invariant/hits/sorted/count.
3. N13 actual binding wrong-cmp negative.
4. N13 post-return sorted corruption negative.
Резерв `(4×10+30)×$0.0135 = $0.945`. N9 leaf не заменяет N13 leaf.
Прямой fn-pointer N13 в этот Build не входит; прежний function-item TIMEOUT не matching timing baseline.
Не повторять его автоматически. Суммарный плановый резерв G1+G2 = **$2.025**.

Единственное альтернативное использование G2: исправление compile error G1, без смены механизма/domains/flags,
после нового review/GO; повторить те же5 rows, резерв$1.080. Тогда N13 в этом задании не запускать, даже если
исправленный N9 gate прошёл. Верхний резерв этого сценария$2.160; всегда own fact_spent + полный новый reserve
≤$2.50 и вписывается в актуальный общий ledger. После resource/semantic failure повтор не разрешён.
G3 нет. Каждый dispatch — exact имена только своего gate, не весь controls-набор с унаследованными failure/timeout.

## PRE-BUILD review и результат

До каждого GO: полный diff, domain record (T/F/value/N/backing/offset/init/frame/probe), таблица actual-call→adapter→
summary→independent leaf; ctx lifecycle/ghost-write boundary; полный список annotations каждого root;
expected failures/literals и required covers; request hash, source/library tree, pin/tooling identity, reserve/slot check.
Targets предшествуют PFC; pfc_order.py и отдельно actual target ordering/ordinary exact200. New cfg-on count вывести
из diff/статической сверки, не считать его proof. Rustfmt/whitespace; library/research commits отдельно, `[skip ci]`,
push без force. Чтение evidence — существующие bounded K-1 summaries/rows/peaks и targeted check context по runbook;
raw archives/full logs/Cloud Logging, credentials и скрытые config-файлы не читать и не скачивать.

`RESULT-NETCOMP.md` ≤45 строк: source/request/build/library identities, actual F/value и trace/binding;
таблица rows/status/VT/CBMC RSS/failed-total/unreachable/covers; gate и next-step отдельно от Cloud COMPLETE/SUCCESS.
Для G1 сравнить VT(B9)+VT(leaf9) с VT(A9); jobs1 CBMC memory — max(B,leaf), не сумма. Compiler/process-sum RSS,
whole-command wall и Build cost отдельно. Не сравнивать скорость с function-item N1 как с тем же instance.
Для G2 заявлять fit только если N13 leaf и composed proof действительно завершены, а оба controls сработали.
Без matching direct fn-pointer N13 speedup не установлен; возможен только новый composition result этого домена.
TIMEOUT — cap600s и доступные wall/RSS, VT=UNKNOWN если не напечатан, не fabricated600; OOM отдельно.

Доказано при положительном gate: machine-checked composition реального std route для перечисленного exact N,
T=u8/F=U8Cmp/canonical strict_less, initialized exact backingN/offset0, arbitrary full input/probe, matching leaf
и проверенный pair/frame/count invariant. Network-level consumer — plain composed proof с assertions;
это не PFC-контракт самих trait methods. Negative results доказывают чувствительность своих gates/oracle, не всеобщую soundness.
Не доказаны прежний function-item instance, arbitrary T/FnMut, N18/другие lengths/backings, stability ties,
initialization detection, полный alias/value-validity/unwind scope. Это opt-in research; ordinary200 и Part1/v6 claims не меняются.
Маркеры `REVIEW REQUEST <sha>` / `NETCOMP ЗАВЕРШЁН`; после последнего разрешённого gate остановиться,
зафиксировав PASS/PARTIAL/FAIL и точные открытые obligations. Иного проекта/архитектуры при blocker не начинать.
