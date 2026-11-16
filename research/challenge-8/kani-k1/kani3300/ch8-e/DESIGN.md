# E / worker15 — static design, 2026-11-16

Статус: **STOP E для предложенного quantified-pointer ON encoding**.
Причина — явный отказ pinned frontend от quantified predicate с uninit safety checks.
Это не утверждение о невозможности всех альтернативных инвариантов. Shadow после
havoc и стоимость proof остаются UNKNOWN; ни одного proof obligation не закрыто.

## Identities и область

| Обозначение | Exact commit | Tree |
|---|---|---|
| G, g0 до этой стадии | `1038c006f9616e88e4792b025bd877674c008def` | `51477b7892ed19cb81c0142fcfe210a5e8ebc14d` |
| P, std P′ | `c5ff36ff433692140605891f646043f991db05de` | `1302063846873aa300f8bac64fe09e8a3ed1280f` |
| U, upstream Kani | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |
| S, SEL1 | `14bc57fdb99960240c4944845a3d985c8af4dcf7` | `1efb6e4dfa69d346df8e23741d11839b1932403d` |

Ниже `U:path:line`, `S:path:line`, `P:path:line` относятся именно к этим Git objects,
не к текущим working-tree строкам. Kani читался через Git в
`/root/kani-fix-ch8-w0-a1-r3-w15`; std — в g0. Компиляция P′ на U/S1-02 —
входной claim задания, здесь не переустановлен. A1-R3 intake сюда не входит.
Четыре документа — единственная область записи; без core/tool изменений и запусков.

## Что поддерживается по исходникам

| Механизм | Факт на U и предел применимости |
|---|---|
| `loop_invariant` | Base assertion, havoc/assume inductive state, step assertion; это partial correctness без termination. `U:docs/src/reference/experimental/loop-contracts.md:109`, `:146`. Поддержка syntax explicit `loop`/`while` не доказывает корректность lowering конкретного Drop/break path. |
| `loop_modifies` | Raw pointer, reference, raw fat slice; target вычисляется **до** loop, не движется вместе с hole. `U:docs/src/reference/experimental/loop-contracts.md:241`, `:303`. Raw slice lowers в `__CPROVER_object_upto(data,len*sizeof(T))`: `U:kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:28`. Можно выразить symbolic-sized frame, не создавая `&mut [T]` над hole. |
| `loop_decreases` | Реальный integer clause, не только RFC; без invariant игнорируется. `U:docs/src/reference/experimental/loop-contracts.md:367`, `:445`, `:465`; tuple caveat `:405`. Выбирать один непосредственно читаемый `usize` local. |
| Мера через pointer distance | Casts, calls, checked arithmetic могут вычисляться один раз до loop; codegen предупреждает и check должен fail. `U:kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:156`, `:208`, `:288`. Поэтому `offset_from`/helper/адресная арифметика внутри decreases не являются готовым решением. Нужен связанный с указателем verification-only счётчик. |
| Quantifiers | `usize` variable; SAT — constant bounds, symbolic bound требует поддержанного SMT, dropped quantifier должен дать FAILED. `U:docs/src/reference/experimental/quantifiers.md:72`. Указатели квантифицировать через индекс `i`, геометрию и `base.add(i)`, не через ordered pointer universe. |
| Pointer predicates и ON | Даже корректный raw dereference внутри quantified predicate несёт safety checks и отвергается с extra UB ON. Docs `U:docs/src/reference/experimental/quantifiers.md:38`; исполняющий guard `U:kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:1267`, diagnostic `:1337`. OFF тоже не даёт гарантии сохранения всех checks внутри predicate (docs `:55`). |
| Symbolic storage | Путь **есть** для primitive slices/Vec в alloc-enabled Kani: fresh symbolic length/allocation, без CAP. `U:library/kani/src/arbitrary.rs:165`, `:205`, `:236`; selection `U:kani-compiler/src/kani_middle/transform/automatic.rs:1117`, `:1301`; docs `U:docs/src/reference/experimental/autoharness.md:329`. Это не generic-T theorem. |

### Symbolic storage: что ещё надо связать

`any_slice_mut_unbounded::<u8>()` использует symbolic `len`,
`len <= isize::MAX / size_of::<T>()`, `Layout::array(len.max(1))`, ненулевой fresh
allocation и `slice_validity_assume`. `len.max(1)` — отсутствие zero-byte allocation,
а не константный cap. Не заменять это `kani::vec::any_vec::<T,32>()`.

У модели **нет `core::kani` counterpart**, что явно указано в `arbitrary.rs:176`.
Применимость к actual core root на P′ требует alloc-enabled bridge и проверки exact
target binding; копия алгоритма в std harness этого не заменяет. Для `u8`
`slice_validity_assume` — no-op по validity (`U:kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:950`, `:985`),
а не доказанный must-init summary. Нужен ON legal-read control свежего symbolic
storage до loop, затем после havoc. Autoharness FnMut models возвращают arbitrary
answers, но не исполняют чтения actual comparator (`U:docs/src/reference/experimental/autoharness.md:349`);
поэтому первый профиль — собственный direct closure с чтением обоих `u8` и arbitrary bool.
Не выдавать успешно сгенерированный slice/один OFF результат за ON proof.

### Havoc и uninit shadow

Порядок U: UninitPass → IntrinsicGeneratorPass → LoopContractPass:
`U:kani-compiler/src/kani_middle/transform/mod.rs:131` (S: тот же файл `:138`).
Uninit использует assert-no-assume из-за demonic nondeterminism (`U:.../mod.rs:139`,
`S:.../mod.rs:146`). User loop assigns превращаются в CBMC targets уже в codegen
(`U:kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:260`).
Из этого нельзя вывести ни «shadow уничтожен», ни «shadow автоматически корректен»:
нужны controls на actual abstracted loop, включая shadow writes и aliases.

`can_dereference` — **не чистый assume-able init predicate**: он вызывает
`assert_is_initialized`, возвращающий true после check.
`U:library/kani_core/src/mem.rs:73`, `:252`; **те же строки на S**.
Записать его в loop invariant/ensures и затем предположить init недостаточно.
Raw slice в modifies задаёт байтовый frame, сам по себе не задаёт initializedness,
validity, ownership, padding или permission summary после havoc.

У U→S нет diff в `loop_contracts.rs`, quantifier hooks и `mem.rs`. Есть изменения
общей transform/cache инфраструктуры и uninit handling; не считать S идентичным U.
SEL1 selection fallback не снимает приведённый quantifier guard. ON сравнивать
на S с теми же roots/flags, OFF companion — на S; U/OFF — отдельная baseline строка.

## Точные состояния actual P′

Все номера ниже: `P:library/core/src/slice/sort/shared/smallsort.rs`.
Пусть `B` — base, `n` — len, `k` — логический tail index, `j` — sift index;
для non-ZST `q(i)=B.add(i)` с сохранённой provenance одной allocation.
`Live(i)` означает initialized valid live T с правом чтения; `Writable` и ownership
не следуют из одного адресного равенства. Это математические obligations,
**ещё не реализованные Kani predicates**.

| Point | Инвариант / obligation |
|---|---|
| Outer head, перед guard `:667` | `1 <= offset <= k <= n`; B/end неизменны, end=q(n), tail=q(k), все элементы `[0,n)` live, writable, одна valid allocation; нет открытого hole/guard из предыдущей вставки. Логический remaining=`n-k`. Safety не требует sorted prefix. |
| Outer true edge `:670` | `k<n`, `B<tail`, весь `[0,k]` пригоден для actual insert_tail, байтовые границы/выравнивание/непереполнение; хвост `(k,n)` и outside frame сохраняются закрытым comparator profile. |
| Insert entry `:611–614` | `1<=k`, inclusive `[0,k]` live/writable. Первый comparator читает tail и k-1 **до** создания hole. False edge возвращает полностью initialized region. |
| После `tail.read()` и guard `:621–622` | `tmp: ManuallyDrop<T>` содержит вынесенный live T; src=&*tmp фиксирован и не alias storage; len=1. Логический hole=k, `sift=q(k-1)`. Нельзя читать T из hole. |
| Inner head, перед copy `:624/628` | `0<=j<k`; sift=q(j), guard.dst=q(j+1), src=&*tmp, len=1. Hole=j+1, `[0,j+1)` и `[j+2,k+1)` live; tmp live отдельно. Весь `[0,k+1)` writable. Логический rank=`j+1` в `[1,k]`. |
| После copy и dst update `:628–629` | Источник j был live; dst=j+1 valid, nonoverlap для non-ZST. Теперь hole=j и guard.dst=q(j); moved value в j+1 live. **Head relation больше не верна.** |
| Первый break `:631–632` | j=0, hole=0; guard всё ещё обязан восстановить элемент. Не предполагать inner head invariant на этой exit edge. |
| После decrement `:636`, перед comparator `:637` | j_old>0; j_new=j_old-1, hole=j_old=j_new+1. Head geometry восстановлена; comparator читает tmp и live j_new, а не hole. Если true — back-edge rank уменьшается на 1; если false — второй break с repair obligation. |
| Scope exit `:640–642` | Actual `CopyOnDrop::drop` (`:303–309`) копирует tmp в актуальный dst. После normal repair все `[0,k+1)` live; ManuallyDrop не запускает повторный Drop tmp. Unwind edge также требует repair до публикации caller state. |

Hole здесь **логическая утрата ownership**, не обязательно false shadow bit:
`ptr::read`/copy могут оставить прежние initialized bytes. Нельзя требовать
`!is_initialized(hole)` или считать физическую копию вторым owned T. Для общего T
initializedness относится к required value bytes, а не «все padding bytes true».
Начальный `u8` профиль не имеет padding и не доказывает перенос на произвольный T.

Outer invariant сохраняет suffix, который текущая вставка ещё не трогала;
inner frame — фиксированный inclusive `[B,tail]`, а не движущийся `guard.dst`.
Tmp, guard.src/len, исходные B/tail, end/len и outside allocation — stable.
Допустимы изменения locals sift/guard.dst/rank и region; comparator footprint
нужно задавать отдельно. На P′ `:382–386` и `verify.rs:36–40` уже ограничивают
contract/stub применение закрытыми comparator domains. Общий FnMut может менять
внешнее состояние/interior mutability: этот spike не получает новый generic frame theorem.

Termination относится к самим loops при завершающемся callback. Для outer —
`n-k`; для inner — `j+1` на back-edges. Прямые ghost locals и связи с pointer
нужны из-за stale-measure ограничения. Отсортированность/permutation усилить
отдельно для пункта2; не предполагать их для safety и не заменять ими init.

### ZST

Actual outer `:664–667` при `size_of::<T>()==0` имеет tail==end сразу:
**ноль итераций**, comparator и insert_tail не вызываются. Нужна отдельная
vacuous-loop строка с symbolic len/valid offset и проверкой нулевого числа calls.
Pointer distance не даёт числа ZST элементов; rank от адресов не вычислять.
Actual insert_tail ZST **вне текущего requires**: helper length возвращает 0
(`:569–580`), а requires требует >1 (`:588–599`). Не расширять его domain и не
придумывать ZST inner traversal. Отдельный direct-ZST negative — precondition
failure, не inner-loop theorem. Не добавлять runtime branch/counter.

## Решение стадии

Поддержка symbolic primitive storage в frontend установлена статически,
готовность actual core/ON пути — нет. Предложенный forall над readable ranges
попадает под явный отказ frontend с ON. Это активирует STOP E по unsupported
invariant для этого кандидата. Минимальный reproducer и план различающих
controls — [CONTROLS.md](CONTROLS.md); интегратору —
[PATCH-PROPOSAL-13.md](PATCH-PROPOSAL-13.md). Не открывать compiler-fix/новую
trusted shadow модель в этой стадии. Новая форма init-summary требует отдельного
design gate §6 и controls, а не отключения checks.
