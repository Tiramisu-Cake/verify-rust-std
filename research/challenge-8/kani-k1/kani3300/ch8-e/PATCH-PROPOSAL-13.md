# Proposal для integrator13 — не применён

Base: std P′ `c5ff36ff433692140605891f646043f991db05de`.
Source: `library/core/src/slice/sort/shared/smallsort.rs`.
**HOLD:** сначала разрешить ON invariant blocker и symbolic core-storage binding
из [DESIGN.md](DESIGN.md). Ниже interface/точки вставки, не compile-ready patch.
E_outer/E_inner обозначают obligations из DESIGN, готовых функций с такими именами нет.

## Минимальные изменения после gate

1. До outer while (`:667`) добавить cfg(kani) ghost local `e_outer_remaining = len-offset`.
   Invariant связывает его с real tail: `tail=q(len-e_outer_remaining)`,
   `0<=e_outer_remaining<=len-offset`, plus full live/writable region и provenance.
   Добавить loop attrs: invariant; explicit modifies fixed raw slice `(v_base,len)`,
   `&tail`, `&e_outer_remaining`; decreases **`e_outer_remaining`**.
   После actual `tail=tail.add(1)` (`:673`) decrement ghost на 1. Runtime CFG,
   pointer increment, abort и signature сохранить; все ghost statements только cfg(kani).

2. После создания tmp/guard (`:622`), до inner loop (`:624`), добавить cfg(kani)
   ghost `e_inner_remaining=k`, где k — checked inclusive region length minus 1.
   `insert_tail_contract_len(begin,tail)-1` допустим лишь при уже установленном
   requires, не как новый assumption. На head `sift=q(e_inner_remaining-1)`,
   guard.dst=q(e_inner_remaining), `1<=e_inner_remaining<=k`; src=&*tmp и len=1.
   Использовать head E_inner из DESIGN, не `can_dereference` как предполагаемую init summary.

3. Inner explicit modifies: фиксированный raw slice `(begin,k+1)`, `&sift`,
   pointer к **полю** `gap_guard.dst`, `&e_inner_remaining`.
   Src/len guard и tmp не включать: invariant сохраняет их, comparator профиль
   не пишет в tmp/внешние captures. Не давать всему guard writable frame ради PASS.
   Decreases — непосредственно `e_inner_remaining`.
   После actual `sift=sift.sub(1)` (`:636`) decrement ghost на 1; оба break
   и copy/dst update остаются на местах. На break head invariant не утверждать:
   проверять отдельный repair-state predicate для actual dst.

4. Сразу после inner loop, до выхода scope tmp/guard (`между :640 и :641`),
   verification-only assertions устанавливают live(tmp), src/len, writable(dst),
   live region кроме dst. После actual Drop (`:642`, за пределами его scope)
   assertion устанавливает fully initialized live `[begin,tail]` и outside frame.
   Это доказательные assertions, не assumed postconditions и не stub Drop.
   Проверить, что macro lowering не теряет break cleanup. Unwind repair — отдельный
   actual comparator-panic control без panic stub; normal-return-only summary не
   расширять на unwind/abort. Если pin не моделирует unwind, записать NOT_ESTABLISHED.

Форма attrs (схема; undefined predicates намеренно не выдаются за код):

```text
#[cfg_attr(kani, kani::loop_invariant(E_outer(...)))]
#[cfg_attr(kani, kani::loop_modifies(raw_slice(v_base,len), &tail, &e_outer_remaining))]
#[cfg_attr(kani, kani::loop_decreases(e_outer_remaining))]
while tail != v_end { /* original body + cfg(kani) ghost decrement */ }

#[cfg_attr(kani, kani::loop_invariant(E_inner(...)))]
#[cfg_attr(kani, kani::loop_modifies(raw_slice(begin,k+1), &sift,
                                  raw_ptr_to(gap_guard.dst), &e_inner_remaining))]
#[cfg_attr(kani, kani::loop_decreases(e_inner_remaining))]
loop { /* original body + cfg(kani) ghost decrement after sift.sub(1) */ }
```

`raw_slice` здесь означает `ptr::slice_from_raw_parts_mut`, без построения
`&mut [T]` над hole. Не использовать slice read на inclusive region до repair.
Не брать modifies только на initial guard.dst: targets вычисляются при entry и
не описывают последующее движение hole. Прямое `loop_decreases(offset_from(...))`
не предлагать: pinned codegen может заморозить меру до loop.

## Contracts / composition

Существующие requires/modifies `insert_tail` (`:588–605`) и insertion (`:646–647`)
не ослаблять. Новая post-repair init summary пока **не определена** в допустимом
assume-able API: `ensures(can_dereference(...))` не решает demonic shadow проблему.
Сначала PFC actual inner body + repair, затем совместимый caller; не применять
`stub_verified(insert_tail)` на symbolic domain по bounded старым roots.
Outer pilot сначала actual callee + оба loop contracts; при composition менять mode
только после квалификации summary на тех же T/F/geometry/tool/checks.

Первые roots: non-ZST `u8`, direct reading arbitrary-bool comparator; отдельный `u64`
companion не даёт generic credit. Не добавлять Copy/Freeze bound в actual функции.
ZST outer: entry invariant должен допускать немедленный zero-iteration exit;
non-ZST pointer-rank predicate ограждается size branch **в specification**.
Никаких runtime изменений ради ZST и расширения insert_tail precondition.

Integrator13 отдельно владеет регистрацией нового opt-in E verify module в verify.rs
и нужными cfg/feature gates. Worker15 сейчас отдаёт лишь документы. Для actual
core root alloc model отсутствует; source-preserving bridge/проверка generated
target должны быть выбраны до реализации, не копировать тело алгоритма в harness.

Acceptance: exact source/tool hashes; runtime diff отсутствует; checked base/step,
frame/decreases/repair, все negatives различают нужную причину, ON shadow controls
и uncapped storage binding проходят. Затем новая стадия fallback defaults/threshold
callers; sortedness/permutation и generic callback frame сюда не включены.
