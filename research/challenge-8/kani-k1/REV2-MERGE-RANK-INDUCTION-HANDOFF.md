# REV2 · ранговая индукция для actual merge N32

1. **Merge 16+16 — принят независимым ревью как составное исследовательское свидетельство.** Для exact `bidirectional_merge::<u8, KeyLess<u8>>` на V34/base1 связка даёт нормальный возврат, 32 инициализированных выходных байта в числовом порядке, полное мультимножество, source/q frame и CAL1-пост. **Вся `small_sort_network` N32 — допуск открыт.** До работы над exact consumer требуется согласовать правило композиции. [Независимое ревью](REV2-MERGE-RANK-INDUCTION-REVIEW.md)
2. **`stub_verified(bidirectional_merge)` — оснований пока нет.** Нужен успешный exact `proof_for_contract(bidirectional_merge)` для совпадающего контракта и достижимого домена потребителя либо отдельно проверенный механизм передачи именно этого составного свидетельства в Replace. Текущий пост наблюдает один q за вызов. Если потребителю нужен полный байтовый пост непосредственно от Replace, контракт должен гарантировать его в каждом отдельном вызове.

`go=NOT_GRANTED`, `proof_credit=NONE`. Scope — чётный N32, exact comparator, исходник FIX3 и указанный ниже профиль. Задание g0 `7ff7c21cc6ac65e802f6c5d5e4ab6598ed255e6c`. [Задание](REV2-MERGE-RANK-INDUCTION-TASK.md) · [Решение по инвариантному маршруту](REV2-MERGE-INVARIANT-RESULTS-ANALYSIS.md#решение-и-оценка)

## Свидетельство FIX3

| Идентичность | Сверенное значение |
| --- | --- |
| GitHub Actions | Run `45661535099`, attempt 1, Ubuntu X64, слот `M32-PAIR-STEP`, singleton |
| Trigger | `8d0f94a36606df5660eaf70818c44007859e05df`, tree `8ec7f5a766154288b8b441be85f34103dc80a12e`, parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Std upstream | `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655` |
| Std FIX3 | `32129c149a15fb1b60a7314e738f3cb466d076e5`, tree `1b0cc32c571b370178e64f2b8c79773d2ce27051` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`, launcher 0.68.0 |
| Входы по GO и индексу | Request SHA-256 `b38f8f428f2d6a4a2ba736f2d763dad4087ad51d23822a8327f4edc9b1d64e06`, bundle SHA-256 `7aa0d0437634f266026920861935197ed24593a2a4582f897dbff702d1f306a6` |
| Exact selector | `slice::sort::shared::smallsort::verify::rev2_provider_cost::m32_pair_step`, `--harness … --exact`, Check `actual_pair_step`, Replace `[]` |
| Профиль | CBMC 6.11.0, CaDiCaL 3.0.0, OB12, `#[kani::unwind(36)]` и resolved unwind36, jobs=1, `--no-assert-contracts`. Memory safety, overflow, unwinding, undefined-function и assertion-reach checks ON. Uninit/validity OFF |
| Cfg | `kani_smallsort_cal1`, `kani_smallsort_cal2_merge_mask`, `kani_smallsort_rev2_provider_cost`, с той же тройкой в регистрации модуля и в RUSTFLAGS |

Локальные Git trees и SHA-256 request из trigger blob совпали с индексом. Для двух использованных членов индекса сверены длина и SHA-256. У `slots/M32-PAIR-STEP/receipt.json` это 46 729 байт и `0de6374172c70f58a11f24a25782b15e76cfd42bdc594c24f2b193ecd1fedc9a`, у производной `slots/M32-PAIR-STEP/projection.json` — 267 834 байта и `a145b13ad498cca1015b300d6e1122eb72fa61906ebb3f8bc279d1fbfdcec7a9`. В receipt и проекции regular и stock export полны. Source-reported исход `VERIFIED`, native verdict `SUCCESS`, 494 успешных checks, 15 `UNREACHABLE`, ноль отказов, 11/11 covers. Все четыре зарегистрированных unwind checks имеют `SUCCESS`. Основание для переноса включает эти результаты и сверку исходника. Диагностический run сохраняет `proof_credit=NONE`. [GO](REV2-NETWORK-PROVIDERS-FIX3-GO.md) · [Индекс](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/index.json) · [Receipt](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/slots/M32-PAIR-STEP/receipt.json) · [Проекция свойств](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/slots/M32-PAIR-STEP/projection.json)

Домен корня — произвольный инициализированный `[u8; 34]` V34, включая два внешних байта. Источник `input = &backing[1..33]` имеет две численно неубывающие половины по 16. Вторая `kani::any()` задаёт независимый `q: u8` для `KeyLess::<u8>::with_q(q)`. Отдельный живой `MaybeUninit<[u8; 32]>` даёт весь диапазон записи с выравниванием `u8` и в исходном состоянии без инициализированных ячеек. `k`, `up_left_used` и `down_left_used` произвольны при `k < 16` и обоих левых счётчиках `<= k`. Правые счётчики вычисляются отдельно как дополнения до k. Отношение между прямым и обратным разрезами в fixture свободно. Sorted halves заданы `assume` harness, числовой порядок нужен для рангового вывода. [Корень и wrapper](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:269) · [Числовой предикат](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs:122)

### Нативные anchors и их роль

Здесь `R` обозначает точный selector, `W` — тот же путь с `actual_pair_step::{closure#2}::{closure#0}` вместо `m32_pair_step`. Номера строк относятся к pinned исходнику. Статус в каждой строке ниже `SUCCESS`.

| Где | Native property и исходник | Содержание |
| --- | --- | --- |
| Fixture до вызова | `R.assertion.1–3`, `rev2_provider_cost.rs:325,329,333`, `READ_APPLICABILITY`, `WRITE_APPLICABILITY`, `DISJOINT_APPLICABILITY` | Read/write области по 32 и отсутствие пересечения. Границы счётчиков и сортировка заданы отдельно в строках 341–347 |
| Контрактный Check | `W.single_top_level_call.1` (в native ID с префиксом `core::`), строка 271. `memcpy.assigns.1–2` в builtin memcpy, строки 46–47. `ptr::copy_nonoverlapping::<u8>.precondition_instance.1–3`, `ptr/mod.rs:587` | Проверка тела `actual_pair_step` с `requires` и DFCC `modifies(scratch.wrapping_add(k), scratch.wrapping_add(31-k))`. Присваивания memcpy допустимы по write set, копии удовлетворяют disjoint/readable/writable. Общий ID охватывает достижимые экземпляры обеих копий. Факт записи в каждую цель даёт тело |
| Assert внутри Check после up | `W.assertion.7`, строка 297, `REV2_M32_PAIR_STEP_UP_CURSORS` | Точная тройка возврата up с true для `right >= left`, включая левый tie |
| Assert внутри Check после down | `W.assertion.10`, строка 307, `REV2_M32_PAIR_STEP_DOWN_CURSORS` | Точная тройка возврата down с true для `right < left`, включая правый tie |
| Assert после возврата wrapper | `R.assertion.14–15`, строки 377–378, `UP_VALUE_TIE_LEFT`, `DOWN_VALUE_TIE_RIGHT` | Полные байты min/max в `scratch[k]` и `scratch[31-k]`. Сами равенства байтов на tie не различают источник. Сторона устанавливается обновлением курсора и выбором указателя в helper |
| Assert после возврата wrapper | `R.assertion.16–17`, строки 379–380, `Q_FRAME`, `SOURCE_FRAME` | Исходный q и все 34 байта V34 сохранены |

У оригинального символа wrapper без суффикса Check обе одноимённые проверки курсоров `.assertion.7/.10` имеют `UNREACHABLE`. Опора — достижимый экземпляр Check. Контракт wrapper задаёт две допустимые цели и возвращает `()`. Равенства курсоров проверяются внутри тела, а value/frame — в harness после вызова. Эти asserts не являются `ensures` wrapper. Native anchors групп копий подтверждают свойства Check в наблюдавшейся конфигурации. Их соответствие конкретным аргументам обеих копий устанавливается по исходнику. [Правило группировки native-свойств](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md#правило-допуска)

Все covers имеют `SATISFIED`. `R.cover.1–4` на строках 381–384 покрывают отдельно left/right для up и down, `.5–7` на 385–387 — tie up, tie down и их дизъюнкцию, `.8–9` на 388–389 — `k=0/15`, `.10` на 390 — useful return после обоих value и frame asserts. Один дополнительный `FnMut::call_mut.cover.1` на `cal1_model.rs:28` имеет описание `CAL1 q actual comparator executed`. Covers показывают достижимость соответствующих условий и возврата пары. Они не утверждают, что произвольные разрезы fixture достижимы в actual цикле или что whole merge вернулся. [Нативная проекция](/root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1/slots/M32-PAIR-STEP/projection.json)

## Привязка пары к actual циклу

Обозначим `S` адрес `&v[1..33]`, `D` начало scratch. Смещения в байтах, поскольку `T=u8`. Для отрицательного смещения ниже `S-1` означает значение указателя с `wrapping_sub` и той же provenance. На входе итерации k у actual цикла формулы такие же, как в wrapper. `a,b` — число уже выбранных up позиций в левой и правой половинах, `c,d` — соответствующие числа down.

| Тройка | Курсор на входе пары k | Аргумент wrapper |
| --- | --- | --- |
| Up source L, R | `S+a`, `S+16+b` | `up_left_used=a`, `up_right_used=k-a=b` |
| Up destination | `D+k` | `scratch.add(k)` |
| Down source L, R | `S+15-c`, `S+31-d` | `down_left_used=c`, `down_right_used=k-c=d` |
| Down destination | `D+31-k` | `scratch.add(31-k)` |

`rev2_provider_cost.rs:4` импортирует `merge_up` и `merge_down` из того же модуля, где `smallsort.rs:1022–1025` вызывает их в порядке up затем down. У helper одна и та же специализация `<u8, KeyLess<u8>>` в обоих местах. `KeyLess::call_mut` сравнивает `a < b` полных байтов, не читает q, не меняет себя или source и не сохраняет ссылки. Дополнительные чтения в wrapper нужны для asserts. Actual цикл сохраняет обе возвращённые тройки и подаёт их в следующую итерацию. [Actual цикл](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort.rs:999) · [Up/down](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort.rs:861) · [KeyLess](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)

Пусть `U = [*up_right >= *up_left]`, `V = [*down_right < *down_left]`, где скобки дают 0 или 1. В up `is_l` совпадает с U, в down `is_l` совпадает с `1−V`. Up копирует выбранный байт в `D+k`, выбирая левый при U=1, и прибавляет `(U,1−U,1)` к своей тройке. Down копирует в `D+31−k`, выбирая левый при V=1, и вычитает `(V,1−V,1)` из своей тройки. Источниковые вычитания down используют `wrapping_sub`, его destination — обычный `sub`. Получаем `(a',b',c',d')=(a+U,b+1−U,c+V,d+1−V)`, а destinations `D+k+1` и `D+30−k`. Up сохраняет source и состояние компаратора, поэтому его запись не меняет операнды down.

Для переноса с пустого fixture на позднюю итерацию фиксируем одинаковые значения source, курсоры с доступом к тем же смещениям живых областей и `KeyLess` с тем же q. В каждом helper чтения — создание shared-ссылок на две текущие позиции source для сравнения и однобайтовое чтение выбранной позиции при `copy_nonoverlapping`. Destination участвует в записи и арифметике указателей. Его прежние байты, включая заполненные края, недоступны через эти чтения, поскольку области разделены. Поэтому замена состояния scratch за пределами двух новых целей не влияет на сравнения, выбранные байты, курсоры или возврат. Каждая из двух копий сохраняет состояние всех остальных ячеек, включая инициализацию и значения ранее записанных краёв.

Точный footprint следует из одного вызова `copy_nonoverlapping::<u8>(src, dst, 1)` в каждом helper, его аргументов и семантики копии. Для `k<16` обе записи внутри `D[0..32)`, `k < 31-k`, а каждый выбранный источник инициализирован, читаем и отделён от обеих целей. При нормальной записи `copy_nonoverlapping` переносит битовое представление **вместе с состоянием инициализации** источника. Так инициализируется по одному новому байту. Доступность записи и DFCC задают допустимую память, а `assume_init_read` на строке 376 потребляет уже обоснованную инициализацию. Профиль с uninit/validity OFF оставляет этот вывод за исходником. [Копия и инициализация](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/ptr/mod.rs:475) · [Проверка разделения областей](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort.rs:927)

## Индукция по рангам

Для каждой позиции исходного среза ключ `(byte, side, index)` упорядочен лексикографически. `side=0` слева и `side=1` справа, `index=0..15` внутри половины. Ключи уникальны даже для равных байтов. Обозначим `P[r]` исходную позицию ранга `r=0..31` в этом порядке. В каждой половине её порядок позиций совпадает с ограничением глобального порядка, поскольку байты в ней не убывают.

**Инвариант при входе в пару k и на границе k=16.**

- Up выбрал `P[0..k)`, то есть первые `a` и `b` позиций соответствующих половин, `a+b=k`. Down выбрал `P[32-k..32)`, то есть последние `c` и `d`, `c+d=k`. Все счётчики лежат в `0..=k`, курсоры заданы шестью формулами выше.
- Scratch инициализирован ровно на `[0,k) ∪ [32-k,32)`. Для каждого его заполненного индекса `r` записан полный исходный байт позиции `P[r]`. Source V34 и q сохраняют входные значения.

**База `k=0`.** `len=32`, `len_div_2=16`, поэтому `assume(len_div_2 != 0)` выполнен. Actual инициализация в строках 1014–1020 даёт `(S,S+16,D)` и `(S+15,S+31,D+31)`. Счётчики `a=b=c=d=0`, оба множества рангов пусты, `MaybeUninit` даёт пустое множество инициализированных ячеек. [Инициализация](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort.rs:999)

**Шаг `0 <= k < 16`.** Каждое направление отдельно потребило k, поэтому каждый из его счётчиков не превосходит k и меньше 16. Четыре source-курсора находятся в своих инициализированных половинах, все соответствующие чтения допустимы. Up выбирает минимальный ключ из двух первых позиций, ещё не выбранных up. При равных байтах он берёт левую позицию, а внутри половины курсор идёт с меньших индексов к большим. Получается минимальный среди всех оставшихся для up ключей, то есть `P[k]`. Down выбирает максимальный ключ из двух последних позиций, ещё не выбранных down. При равных байтах он берёт правую, а внутри половины курсор идёт в обратном порядке индексов. Получается `P[31-k]`. Эти ранги различны и оба в незаполненном интервале `[k,32-k)`. Для выбора разрешено прочитать кандидата, уже выбранного встречным проходом, или прочитать одну позицию обоими направлениями. Source остаётся инициализированным и неизменным, а доказанные выбранные ранги различны.

Применяем переход FIX3 к `(k,a,c)` с указанной независимостью от прежнего scratch. Две записи добавляют `P[k]` и `P[31-k]` в соответствующие позиции scratch, сохраняя старые края, V34 и q. Обновления счётчиков продвигают ровно один курсор в каждом направлении. Поэтому `a'+b'=c'+d'=k+1` и все формулы указателей выполняются для `k+1`.

**Последняя пара и выход.** Actual `0..len_div_2` даёт ровно 16 пар. При `k=15` destinations смещены на 15 и 16, поэтому up `add(1)` и down `sub(1)` дают `D+16` и `D+15`, оба в scratch. Последнее продвижение up на один байт допустимо от позиции внутри половины вплоть до её one-past-end. При `k=16` up source может достичь границы половины (`S+16` или `S+32`). Down source при `c=16` даёт `(S+15).wrapping_sub(16)=S−1`, адрес `v[0]` вне среза, а при `d=16` — `(S+31).wrapping_sub(16)=S+15`, адрес до начала правой половины. Значения получены арифметикой от исходной provenance. После последней пары эти курсоры участвуют только в `wrapping_add(1)` и сравнении. Ни один граничный указатель не разыменовывается.

При `k=16` up-префикс из 16 рангов и дополнение down-суффикса из 16 рангов — один и тот же набор `P[0..16)`. По пересечению с каждой половиной получаем `a=16-c` и `b=16-d`. Для левой половины `left_end = left_rev.wrapping_add(1) = S+16-c = S+a = left`. Для правой `right_end = right_rev.wrapping_add(1) = S+32-d = S+16+b = right`. Равенства используют указатели той же исходной аллокации. `32.is_multiple_of(2)` истинно, odd-ветка пропускается, оба сравнения order guard ложны и функция возвращается нормально. Объединение записанных краёв теперь `[0,16) ∪ [16,32)`, то есть весь scratch инициализирован. Других пишущих действий у exact чётного вызова нет. [Финальные курсоры и guard](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort.rs:1027)

**Байты и CAL1-пост.** Каждый `scratch[r]` равен исходному байту `P[r]`. Проекция уникальных позиций на байты даёт числовой порядок и то же полное мультимножество с учётом повторов. Для любого независимого q положим `B = count(input < q)`. Тогда `scratch[r] < q ⇔ r < B`, и бит `r` в Mask равен `[r >= B]`. Это ровно `((1_u64 << 32) - (1_u64 << B)) as u32`, включая `B=0` и `B=32`. Вариант Below проверяет то же условие по позициям. Здесь профиль FIX3 включает Mask, а Below следует как алгебраическое следствие по исходнику для N32. q остаётся исходным, тип и длина поддерживаются, и полностью инициализированный scratch доступен для чтения постом. Для всех порогов наблюдается одно исполнение по полным байтам, потому что компаратор q не использует. [Capture и пост](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs:144)

## Обязательства переноса

Сокращения `S.rs`, `W.rs` и `M.rs` в таблице означают pinned `smallsort.rs`, `rev2_provider_cost.rs` и `cal1_q_merge_model.rs`. Native IDs раскрыты выше.

| Обязательство | Native property или исходный фрагмент | Формула переноса | Открытая граница |
| --- | --- | --- | --- |
| Домен и применимость каждой пары | `R.assertion.1–3`, `W.rs:273–276,318–351`, `M.rs:122–129` | `a+b=c+d=k<16`, четыре читаемых позиции в двух sorted halves и два адреса в отдельном scratch по 32 | Вся сеть должна установить те же предусловия после вставок на actual call site |
| Две цели и их инициализация | `memcpy.assigns.1–2`, copy `precondition_instance.1–3`, `S.rs:883–888,916–921`, семантика `ptr::copy_nonoverlapping` | `D+k ≠ D+31-k`. Обе копии инициализируют по байту из source и сохраняют остальное состояние scratch | Uninit/validity в run OFF. Для Replace требуется установить инициализацию всех 32 байтов на его выходе |
| Up и down, tie и полные байты | `W.assertion.7/.10`, `R.assertion.14–15`, `KeyLess::call_mut`, `S.rs:1022–1025` | `U=[R_up≥L_up]`, `V=[R_down<L_down]`. Тройки ведут к `(a+U,b+1−U,c+V,d+1−V)` и след. паре destinations. Выбранные позиции `P[k]`, `P[31-k]` | У actual вызова нет wrapper-asserts. Связь тройки со следующим вызовом устанавливается исходником и индукцией |
| Source/q frame | `R.assertion.16–17`, источниковые чтения и scratch-записи в helpers, `cal1_model.rs:26–30` | `V34_k=V34_0`, `q_k=q_0` для всей последовательности. Up также сохраняет операнды down | Exact consumer дополнительно проверяет frame вне `v[1..33]` через presort, вставки и copy-back |
| Нормальный возврат и целый scratch | `S.rs:999–1045` и инвариант рангов | При `k=16` `a+c=b+d=16`. Оба guard-равенства выполняются, odd ветка минуется, `[0,16) ∪ [16,32) = [0,32)` | Useful-return cover FIX3 относится к одной паре. Для native whole merge и consumer нужны свои свидетельства |
| Полное мультимножество, порядок и q-post | Ранговый пост и `M.rs:144–211` | `out[r]=byte(P[r])`, поэтому `out[r]<q ⇔ r<count(in<q)` | Один-q `ensures` Replace передаёт только соответствующий пороговый пост |
| Перенос в сеть и контроль | `S.rs:367–426,701–769`, exact S13 опоры и исторический consumer | Левый `[1,17)` и правый `[17,33)` дают при входе merge объединение исходных мультимножеств. Полный scratch переносится в `[1,33)` | Exact consumer REV2, его witness нормального возврата и matched control общего поста открыты |
| Check → Replace | `S.rs:950–964` | Контракт и область нормального возврата, прочитанные потребителем, совпадают с проверенными для самой `bidirectional_merge` | FIX3 даёт Check для `actual_pair_step`. Нужен whole merge Check либо проверяемый мост в Replace |

## Допуск actual small_sort_network N32

Левый `sort13_optimal` получает `(base=1,len=16)`, правый — `(17,16)`. Для левого уже принят внешний перенос по длине. Для правого есть exact битовый Proof и полнобайтовый лист на той же геометрии, сцепленные пороговым переносом. Их составные посты дают порядок и полное мультимножество первых 13 байтов каждой половины, q и frame остальной V34. Эти опоры можно использовать вместе с reviewed merge как отдельные провайдеры исследовательского графа. [Левый S13](/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/REV2-S13-LEFT16-REVIEW.md) · [Правый S13](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md#приёмка-run-45688753097)

Exact consumer должен связать эти посты на одном исполнении `small_sort_network::<u8, KeyLess<u8>>(&mut v[1..33], …)` на произвольной инициализированной V34 с независимым q.

1. При `len=32` обе начальные проверки сети проходят, scratch имеет ровно 32 байта, `no_merge=false`. Проверить реальные `from_raw_parts_mut` и два региона по 16, reborrow с правильными правами доступа, S13 на префиксах `[1,14)` и `[17,30)`, сохранение хвостов и внешних байтов. При переносе S13-опор сверить активные cfg и тела с exact pin consumer.
2. После каждого S13 `insertion_sort_shift_left(region, 13, is_less)` делает три actual `insert_tail` для rel13, rel14, rel15. Слева это v[14], v[15], v[16], справа v[30], v[31], v[32]. На каждом вызове установить читаемость и порядок предшествующего префикса. Если хвост уже в порядке, тело возвращается сразу. Иначе оно сохраняет tail в `tmp`, перемещает больший суффикс на шаг вправо и через `CopyOnDrop` заполняет gap. Требуются нормальный возврат, инициализация, порядок удлинённого префикса, сохранение его мультимножества, хвоста за ним, противоположной половины, внешних байтов и q. Тогда обе полные половины в merge численно отсортированы и переставляют байты своих исходных половин.
3. Проверить actual `bidirectional_merge` на `v[1..33]` и отдельный `MaybeUninit<[u8; 32]>` stack scratch. Нужны exact disjoint/readable/writable области, прежний `KeyLess` с тем же q, применимость reviewed провайдера и нормальный возврат с полным инициализированным результатом. При использовании нативной подстановки требуется соответствующее ребро Check → Replace.
4. Привязать actual `ptr::copy_nonoverlapping(scratch_base, v_base, len)` с `len=32`. После нормального merge scratch читаем, назначение `v[1..33]` доступно для записи, области разделены. Копия передаёт все значения и инициализацию, оставляя `v[0]`, `v[33]` и q неизменными. Проверить общий observer от snapshot активного среза **до сети** к этому возврату. Если заявляется полное мультимножество сети, в соответствующей цепочке нужны полнобайтовые гарантии каждой стадии.
5. Различающий контроль должен достичь того же пути сети и copy-back, затем изменить пороговое наблюдение активного среза одним байтом и дать ожидаемый отказ именно общего поста при сохранённых q и внешнем frame. Пример из исторического маршрута использует нулевой вход, `q=1` и запись `v[1]=255` после useful return. Различение для более сильного заявленного поста должно проверять и его. Исторический bounded N32 допущен на своих пинах и OB11 в кампаниях 17A/21B/21C/22. Этот контроль и тот результат задают привязки для проверки нового consumer. [Вставки и copy-back](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort.rs:367) · [Исторический exact consumer и control](item2-audit-response-20261120/ADMISSION-N32.md#native-роли-consumer-и-контроля)

## Что требуется для Replace

Для нативного маршрута успешный `proof_for_contract(bidirectional_merge)` должен проверять actual тело и именно потребляемые `requires/modifies/ensures` для `u8/KeyLess<u8>` и достижимой V34/base1 геометрии 16+16 на согласованных Std/Kani/cfg и профиле FIX3. Exact consumer должен закрыть на call site `len>=2`, читаемость и инициализацию source, отдельный writable scratch по 32 байта, `merge_geometry` и числовой порядок половин. Общий предикат CAL1 допускает `20..=32`. Зачёт exact Check для N32 требует ограничения использования здесь достижимым `len=32` и проверенной геометрией. Для Check и Replace сверяются требования и режим активных предикатов, включая Mask в указанном профиле. Достижимость нормального возврата и наблюдений нужна на этом домене. [Аннотации actual merge](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort.rs:950) · [CAL1 геометрия](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs:96)

`modifies(ptr::slice_from_raw_parts_mut(dst, v.len()))` разрешает менять только scratch из 32 байтов. Нужны установленные frame source и памяти вне destination, неизменный q и инициализация всех 32 выходных байтов после нормального возврата, включая пригодность именно состояния после Replace к actual copy-back. Write set ограничивает допустимые записи. Факт инициализации требует проверки body и того, как Replace представляет инициализированный выход. Одного `can_dereference` в observer с uninit/validity OFF для этого вывода недостаточно. `old(merge_capture(v,is_less))` фиксирует вход и q в виде snapshot для порогового поста. Нативный Check wrapper квалифицирует только его собственный write set и проверенные экземпляры тела, а внешний вывод относится к actual исполнению. Альтернативный механизм должен проверяемо привязать те же pre, post, footprint, инициализацию и frame к подстановке `bidirectional_merge` в exact consumer, включая подтверждение выбранной реализации Replace.

Текущий `merge_q_post` достаточен для проверки соответствующего порогового наблюдения в одном вызове при исходном q и требуемом frame. Для данного q он даёт точный разрез по `<q`. Например, при входе из одних единиц и `q=1` выход из одних 255 тоже удовлетворяет этому посту. Даже числовой порядок внутри одного порогового класса из него не следует. Универсальность q в harness доказывает формулу для каждого q, но абстрактный Replace вправе выбирать свой scratch-выход для каждого q. Для полного мультимножества непосредственно после одного Replace нужен пост об одном конкретном результате для всех значений, например равенство кратностей каждого байта со входным snapshot. Если нужен и числовой порядок, добавить его явно либо установить равенство упорядоченной перестановке входа. Проверяемый эквивалент — все пороговые разрезы одновременно для того же scratch. [Пороговый snapshot и post](/root/verify-rust-std-rev2-network-providers-fix3-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs:131)

## Воспроизведение привязки

Ниже проверка Git blobs и SHA-256 двух членов индекса run `45661535099`. В примере `candidate` явно задан полным SHA FIX3 для воспроизведения исходной привязки. Для проверки переноса подставить полный SHA exact commit предполагаемого consumer из общей Std object database. Список включает исходники шагов, регистрации модуля и cfg, сравнения, обход диапазона, арифметику, примитивы памяти и адресную обвязку. При дельте нужен разбор изменившихся тел, активных атрибутов и зависимостей. Применимость требует совпадающих типов, профиля, `len=32`, доступа к двум инициализированным sorted halves V34/base1, независимого q и отдельного scratch с правом записи. Связь вызываемых тел с селектором FIX3 дана импортами, exact cfg, отсутствием Replace в строке слота и нативными anchors.

```bash
(
    set -euo pipefail
    repo=/root/verify-rust-std-rev2-network-providers-fix3-w11
    fix3=32129c149a15fb1b60a7314e738f3cb466d076e5
    candidate=32129c149a15fb1b60a7314e738f3cb466d076e5
    [[ "$candidate" =~ ^[0-9a-f]{40}$ ]]
    test "$(git -C "$repo" rev-parse --verify "$candidate^{commit}")" = "$candidate"
    test "$(git -C "$repo" rev-parse "$fix3^{tree}")" = 1b0cc32c571b370178e64f2b8c79773d2ce27051
    set -- library/core/Cargo.toml \
        library/core/src/cmp.rs library/core/src/iter/range.rs library/core/src/num/uint_macros.rs \
        library/core/src/slice/sort/shared/mod.rs library/core/src/slice/sort/shared/smallsort.rs \
        library/core/src/slice/sort/shared/smallsort/verify.rs \
        library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs \
        library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs \
        library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs \
        library/core/src/slice/mod.rs library/core/src/slice/raw.rs \
        library/core/src/mem/maybe_uninit.rs library/core/src/ub_checks.rs \
        library/core/src/ptr/{mod,const_ptr,mut_ptr}.rs library/core/src/intrinsics/mod.rs
    git -C "$repo" diff --no-ext-diff --no-textconv --exit-code "$fix3" "$candidate" -- "$@"
    git -C "$repo" ls-tree -r "$fix3" -- "$@"

    control=/root/kani-rev2-network-providers-fix3-control-w11
    tool=9834c96ce90ff57d8495416530b080dc3d52ce25
    trigger=8d0f94a36606df5660eaf70818c44007859e05df
    test "$(git -C "$control" rev-parse "$tool^{tree}")" = 938e9932cb2127239afb4f093f6302652c053398
    test "$(git -C "$control" rev-parse "$trigger^{tree}")" = 8ec7f5a766154288b8b441be85f34103dc80a12e
    request=b38f8f428f2d6a4a2ba736f2d763dad4087ad51d23822a8327f4edc9b1d64e06
    test "$(git -C "$control" show "$trigger:ch8-cal1/CI-REQUEST.json" | sha256sum)" = "$request  -"

    cd /root/ch8-artifacts/run-45661535099/ch8-rev2-provider-cost-Linux-X64-45661535099-1
    sha256sum --check <<'SHA256'
0de6374172c70f58a11f24a25782b15e76cfd42bdc594c24f2b193ecd1fedc9a  slots/M32-PAIR-STEP/receipt.json
a145b13ad498cca1015b300d6e1122eb72fa61906ebb3f8bc279d1fbfdcec7a9  slots/M32-PAIR-STEP/projection.json
SHA256
    printf 'BIND_OK %s\n' "$candidate"
)
```

Для FIX3 после списка blobs команда печатает `OK` для receipt и projection, затем `BIND_OK 32129c149a15fb1b60a7314e738f3cb466d076e5`.

## Офлайн-перебор формул

Скрипт перебирает все 23 409 пары неубывающих половин длины 16 над `{0,1,255}`. На каждом шаге он сверяет домен счётчиков, оба записанных края с отсортированными ключами позиций и пустой интервал между ними. На выходе он проверяет обе формулы разрезов и Mask/Below при q из `{0,1,2,255}`. Произвольные байты покрывает приведённая индукция. [Скрипт](check_rev2_merge_rank_induction.py)

Команда из корня g0

```bash
python3 research/challenge-8/kani-k1/check_rev2_merge_rank_induction.py
```

Ожидаемый вывод

```text
23409 pairs; all 17 cuts; both ties and opposite-side reads observed
```
