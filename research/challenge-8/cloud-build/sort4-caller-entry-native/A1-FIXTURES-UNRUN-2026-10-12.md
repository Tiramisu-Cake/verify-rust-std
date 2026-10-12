# Source-derived fixtures — план UNRUN

Часть [пакета решения](A1-TRAIT-CONTRACT-REVIEW-2026-10-12.md). Никакая строка
матрицы не запускалась в этом окне. Это план изготовления в disposable Cloud
checkout после разрешения, не local extractor и не admitted summary.

## Source certificate / общий proof unit

Исходный repository checkpoint `a22282dac3765c7d9948e6edfb0ae74102a4280b`.
Хеши SmallSort/quicksort и tool pins — в основном пакете/старом manifest. При
изменении fixtures нужен новый proof/infra SHA; старый Build не проверит их.

Cloud source pair должен сохранять:

1. SmallSort trait **целиком** (18–28), включая safe prototype с method F.
2. Default impl **целиком** (30–47), включая `default`, `_scratch`, guard и
   actual insertion call; Freeze impl **целиком** (49–63), включая trait bound,
   threshold и actual helper call. Constants 16/32/48 — из исходных definitions.
3. FreezeMarker из `shared/mod.rs`, исходный Freeze declaration из marker.rs.
   Не считать research local marker эквивалентным без source provenance.
4. Unrestricted quicksort signature и начальный loop/guard/trait call/return
   (stable/quicksort.rs 15–29) без Freeze/nonzero/root len premise.
5. Helper prefix (smallsort.rs 220–254) включая len<2, len+16/abort, pointers,
   original const/length condition до первого sort4 callsite. Для full-body
   proof unit подключить все actual dependencies исходной версии; не opaque
   admitted insertion/helper/sort4 stubs.

Оригинальные версии **обоих** impl bodies и original generic small_sort call
должны присутствовать в full-source normal/readonly export inventory и refinement.
Source certificate хранит file hashes, exact spans/bytes для каждого item,
headers/default/Freeze applicability, full clauses и исходный call graph.
Ghost annotations/диагностические cuts имеют отдельный diff/inventory; full
original остаётся доступным. Не коммитить generated/extracted output.

P0 — source-derived observer исходного guard, нужен для первой узкой гипотезы:

```rust
// Signature exactly follows original unrestricted quicksort<T,F>.
// Same v/scratch/limit/left_ancestor_pivot/is_less parameters, no Freeze.
loop {
    let len = v.len();
    if len <= T::small_sort_threshold() {
        // Ghost proof assertions only: len <= 32; len + 16 <= 48.
        // DIAGNOSTIC CUT before T::small_sort, no small_sort summary consumed.
        return;
    }
    // DIAGNOSTIC CUT before non-base continuation.
    return;
}
```

Это настоящий generic **threshold trait call** и source-derived guard; не полный
original quicksort theorem. P1 сохраняет original `T::small_sort(v,scratch,is_less)`
в другом полном caller unit и проверяет interface/MIR/AST только. Нельзя отчёт
P0 выдать за proof P1. В P2 запрещён cut **перед** small_sort: source-derived
caller действительно вызывает общий trait small_sort, обе impl proofs обязательны.
Если для isolating proof имеется pinned existing `-focus`/target-function режим,
использовать его с полным source inventory и отдельным proof каждого threshold
body; **не** менять body filtering semantics. Если такого режима в pinned
профиле нет или он удаляет нужные conformance checks — checkpoint NO-GO, не
добавлять новое trusted filtering правило под видом fixtures.

## Матрица первого ограниченного Build

Каждый negative — отдельная isolated source/decoded-MIR/AST unit. Мутация source
не изменяет runtime std; source-derived positive сохраняется byte-identical.
Плохой decoded input не может получить compiler/refinement provenance: это
synthetic translator validation control, явно отдельно от compiler-derived proof.

| ID | Input и обязательство | Expected stage / verdict |
| --- | --- | --- |
| OFF | Old exact selected positive с opt-in OFF, full normal/unwind posts | Known duplicate trait parameter frontend refusal, baseline только; не intended semantic negative |
| P0a/P0b | Actual default16 и Freeze32 threshold bodies против **одного** общего `16<=result<=32` post и всех generated native obligations этого zero-arg item | Body proof + impl conformance, VF0 для обеих; presence declaration не PASS. Это не v/scratch/F envelope small_sort |
| P0c | Unrestricted guard observer выше использует trait post; asserts len<=32 и len+16<=48 | Generic trait-call proof, arithmetic assertion/overflow checks; VF0, без supplied len bound. Caller lemma, helper guard ещё не reached |
| P-dispatch | Inspect actual translated P0c/P1 call AST and dispatch trace: callee is original `StableSmallSortTypeImpl::small_sort_threshold`/`small_sort` common prototype, full generic args/clauses; no impl DefId redirect | Positive translation/call-consumption gate before proof acceptance; certificate alone недостаточен |
| P1 | Full original trait, both impls, original generic small_sort call; method F, three input region identities, HRTB FnMut tuple/Output=bool, full generated normal/unwind posts | Export/decode/refinement + frontend well-formed AST only; small_sort/caller body NOT_PROVED, не A1 |
| N-binder-collapse | Synthetic serialized required-fn input: reuse one binder identity for distinct input positions | Identity/region validation до symbolic body; если AST duplicate spelling достигает verifier, existing duplicate check тоже должен refuse |
| N-alpha-valid | Bijective consistent rename трёх input region identities во всех types/clauses/substs | Structural representation accepted; synthetic, zero proof credit. Отличает identity validation от literal name allowlist |
| N-free-region | Input type с region не из method/outer/HRTB scope | Translation well-scopedness gate, не proof assertion |
| N-region-swap | Rewire одной reborrow/input lifetime без соответствующей clause/substitution map | Exact compiler-derived input-region/call-binding admission refusal; rename всех uses consistently само по себе не negative |
| N-no-F | Synthetic declaration drops F while inputs/FnMut/Output clauses retain it | Generic scope/arity validation; отказ до proof, не допускается исчезновение F constraints |
| N-clauses | Remove/alter HRTB FnMut argument tuple или Output=bool из certificate/MIR | Full clause/source-interface admission refusal |
| N-default-contract | Negative-only default threshold body returns 33 against common post; own mutation certificate, compiler/refinement normal | **Impl conformance/body post** failure result<=32, не source mismatch. Freeze impl unchanged; эта проверка не импортирует summary default |
| N-freeze-contract | Negative-only Freeze threshold body returns 33 against common post; distinct mutation certificate | Same intended post obligation in Freeze impl. Default unchanged |
| N-false31 | Generic threshold observer asks len<=31 on guarded path | Intended assertion31 proof failure, witness threshold32/len32 admitted by common interface; earlier failure INCONCLUSIVE |
| N-source | Unchanged positive fixture with wrong source SHA/span/callee DefId in admission certificate | Source identity refusal до translation/proof |
| N-binding | Correct source, certificate falsely maps generic trait call to one Freeze impl / wrong params / wrong method | Call-binding admission refusal; observed Instance=None не override |
| N-clause-redirect | Force legacy clause-ignoring impl specializer for the certified generic caller, with both impls retained | Actual dispatch/AST gate refuses redirect even if certificate says trait item. Нельзя PASS на generic call по default или Freeze summary |
| N-duplicate | Additional threshold definition/prototype or duplicate impl method record | Exact inventory/conformance declaration refusal; never delete original prototype |
| R1–R7 | Seven existing final-profile canonical T/MU, pointer positive, threshold body positive, wrong-pointer/raw-rights/initialized-T-cast negatives | Existing intended predicates/stages, fresh tool candidate; preserve all resource/unwind checks |

N-default-contract/N-freeze-contract deliberately go through translator body
proof using explicitly labelled **mutated source**, while N-source tests refusal
to attribute changed source to original. If the mutation is stopped only by
original-source certificate, it does not test conformance. Run these checks with
summary unavailable until both impl gates pass; focus skip cannot publish it.

Positive acceptance requires P0a/P0b/P0c and P1 shape gates, intended N-contract
and false31 failures, all admission negatives and fresh R1–R7 gates. Dump success
alone не gate. Сохранить full logs/AST/posts/source inventory и first causal
error/line; verifier diagnostic и verification invocation должны согласоваться.
Negative failure before stated predicate = INCONCLUSIVE, никогда intended PASS.

For this certified item/caller the candidate must bypass/refuse the existing
`compute_trait_impl_fn_specialisations` list (exact final assembly17189–17204),
whose resolver ignores impl clauses. Preserve common trait call in actual AST;
the no-redirect positive and forced-redirect negative test the translator itself.
This scoped dispatch change belongs to G trust review, not a classifier fix.

## Подготовленные дальнейшие обязательства — не первый Build

| ID | Обязательство | Expected stage |
| --- | --- | --- |
| P2 | Full bounded common small_sort contract, доказанный против обеих **actual** impl, включая actual insertion/helper callees; unrestricted original guard→small_sort→helper prefix | Full body/conformance/caller proof с native normal/unwind resources; only now generic method summary admitted |
| N-small-sort-pre | Одна impl candidate просит Freeze или nonzero/common extra owner, которых trait pre не даёт | Trait-pre→impl-pre conformance refusal, не silently strengthen caller |
| N-small-sort-post | Одна impl candidate теряет scratch MU/F/source owner в normal или unwind | Impl-post→trait-post resource failure соответствующего исхода |
| N-source-array | Actual generic call после deliberate leak source array authority | Intended trait-call precondition failure; frontend earlier refusal не считается negative |
| P3 | Actual helper reaches first sort4 C1–C4 prefix with opaque-MU frame and ZST-compatible source protocol | A2 full normal + four direct-unwind posts. Потребует отдельного resource/ZST решения; UNRUN |

P2 зависит от незавершённых dependencies и не объявляется дешёвым продолжением
P0. Full trait method safety и generic applicability нельзя доказать stub bodies
или resource-only mocks; такие microfixtures в будущем могут проверять только
mechanism, с отдельным именем и без source theorem credit. Ни full target posts,
ни проверки не ослабляются для получения положительного первого gate.
