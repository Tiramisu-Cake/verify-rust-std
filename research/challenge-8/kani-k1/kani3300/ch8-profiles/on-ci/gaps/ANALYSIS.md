# PROF-ON-01: A/B/C — одна аналитическая стадия

Статус: STATIC_ANALYSIS_COMPLETE; MRE и обходы NOT_RUN; proof credit NONE.
Компилятор, S/profiles, controls и ledger не изменены. WIP compiler = 0.

## Вход и границы выводов

- g0 на входе `b4c4a16f25053d93fbd573fb710762b8a1697a94`; отчёт
  `../run-43798838603/RESULT.md` из `d07f0eaa55d7eb8f813ae03d8a2271dafaaaec3f`.
- Проверяемый source P′ `9fa2f7f97760584f38738909625c064006d8a936`.
- SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7`; upstream baseline
  `0aac16ef62da9e9d5645782d458593e5d78143ba`. Исходники читались через
  `git show` этих объектов в `/root/kani-ch8-prof-on-w15`; HEAD worktree не использован как pin.
- По явному входу задания читались адресные фрагменты распакованного artifact
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/profon/art`.
  Новых скачиваний, Cloud/GCS queries и локальных запусков verifier/compiler нет.
- Artifact `receipt.json`: std/tool SHA совпадают с указанными выше;
  state `COMPLETE_WITH_UNKNOWN`, credit `NONE`; `job-status.json`:
  `PENDING_INDEPENDENT_REVIEW`. Строки ниже OBSERVED/UNKNOWN, не acceptance.
- `group-00` export identity из receipts:
  `3cbbdd70fff29dbd44c195afdd04e00d0b01227b52463520dbf99addff85af13`.
  Это записанная identity, не заново проверенная целостность export/archive.

| Случай | Строки по RESULT | Классификация |
|---|---:|---|
| A | 6 swap n2 + sort4 bytes16 + consumer b16 = 8 | Явно неподдержанный array transmute |
| B | merge consumer u8 len4 + sort4 consumer u64 = 2 | Дефект slice-havoc модели для uninitialized output; не доказанный false positive compiler |
| C | swap_safety_u8_backing4 = 1 | Неподдержанный layout function-item ZST |

Координаты ниже относятся к закреплённым git blobs. Совпадение текста property
и source объясняет механизм статически; оно не устанавливает полную MIR/trace
причинность. Минимальные примеры подготовлены, но не воспроизведены.

## A. `[MaybeUninit<T>; N] → [T; N]`

SEL1: `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs`:
`CheckUninitVisitor::visit_rvalue`, строки 1053–1073. Ветка равных длин и
`wrapper_inner(from, MaybeUninit) == Some(to)` безусловно добавляет
`MemoryInitOp::Unsupported` с точным текстом отказа. Затем
`check_uninit/mod.rs:230–232` превращает его в unsupported check.
`typed_storage_mask` (362–380) допускает обратное направление T→slot;
`maybe_uninit_transmute` (384–399) проверяет одиночный wrapper, не массив
wrappers. Расширять эти исключения без проверки всех data bytes нельзя.

Upstream baseline: тот же visitor, 541–549, содержит общий layout compatibility
gate, без специальной array-ветки SEL1. Поэтому точный SEL1 diagnostic нельзя
приписывать запуску upstream. `ty_layout` не моделирует обычный массив union
слотов как массив уже инициализированных T; равенство size/layout Rust не
означает доказанную инициализацию каждого payload с сохранением padding.

Source `library/core/src/mem/maybe_uninit.rs:1048–1056` действительно делает
`transmute_unchecked(array)`; корректность требует уже инициализированных
элементов. `library/core/src/array/mod.rs:109–113,148–158`:
`from_fn → try_from_fn → array_assume_init`.
Конкретный маршрут шести swap: `verify/network.rs:904–909`, `from_fn` для
двух `ArbitraryValue`. Для b16 маршрут другой: Kani
`library/kani_core/src/arbitrary.rs:125–130` вызывает `T::any_array`, default
27–29 использует `.map`; `.map/try_map` идут через стандартную сборку массива.
У scalar u8/u64 есть raw-array override (41–43), у `[u8;16]` как элемента — нет.
В `verify/merge.rs:150–159` и `verify/merge/profiles.rs:335–346` внешний массив
из четырёх b16 создаётся через `kani::any()`.

Обход без сужения input domain: явный array literal с отдельным вызовом
генератора для каждого элемента. Без нового Copy/Clone/Freeze, без повторения
одного выбранного значения и без `from_fn`, `.map` или `collect`.

```diff
--- verify/network.rs (swap_contract_fixed)
+++ draft only
-    let mut v: [P::Elem; 2] =
-        crate::array::from_fn(|_| <P::Elem as ArbitraryValue>::arbitrary_value());
+    let mut v: [P::Elem; 2] = [
+        <P::Elem as ArbitraryValue>::arbitrary_value(),
+        <P::Elem as ArbitraryValue>::arbitrary_value(),
+    ];
--- verify/merge.rs (sort4_length_body)
+++ draft only
-    let v: [P::Elem; 4] = kani::any();
+    let v: [P::Elem; 4] = [kani::any(), kani::any(), kani::any(), kani::any()];
--- verify/merge/profiles.rs (sort4_consumer)
+++ draft only
-    let src: [P::Elem; 4] = kani::any();
+    let src: [P::Elem; 4] = [kani::any(), kani::any(), kani::any(), kani::any()];
```

Все четыре/два элемента остаются независимыми и произвольными, размер и
drop ownership сохраняются; генерация [u8;16] внутри одного элемента использует
raw-array u8 implementation. Ожидается устранение данного construct, а не
автоматический PASS: следующий blocker, включая B, может стать видимым.
Изменение самого `array_assume_init` в std или предварительная инициализация
настоящего output не нужны. MRE: `MRE-A-array-assume-init.rs`.

## B. Havoc слайса поверх uninitialized output

SEL1 `kani-compiler/src/kani_middle/transform/contracts.rs:131–173`,
`AnyModifiesPass::replace_any_modifies`: slice pointee `[T]` выбирает
`write_any_slice::<T>`. `library/kani_core/src/lib.rs:715–716`:
`(*slice).fill_with(T::any)`. В upstream baseline helper на тех же строках
идентичен. `CheckUninitVisitor::visit_place`, 953–965, ставит
`MemoryInitOp::Check` на raw-pointer Deref; `UninitInstrumenter::build_get_and_check`,
`check_uninit/mod.rs:337–427`, выбирает slice initialization check.

`fill_with` требует `&mut [T]` и присваивает существующим элементам
(`library/core/src/slice/mod.rs:4251–4257`). Это не raw initialization:
формирование такого receiver над uninitialized T недопустимо, а для Drop T
assignment ещё может уничтожить старое содержимое. Поэтому корректнее говорить
о дефекте внутренней havoc-модели, а не о доказанно ошибочной диагностике
инструментации. Ложна атрибуция UB исходному алгоритму: разрешённый output
может быть неинициализированным, и его должен инициализировать проверяемый callee.

Конкретные output: `verify/merge/profiles.rs:343–346,401–404` —
`MaybeUninit<[Elem;4]>`. Preconditions sort4/merge (`220–224,283–289`)
требуют writable destination, без initialized-destination premise;
modifies (`228,299`) передают fat slice на этот output.

Обход для sort4 с точной длиной 4: изменить только набор modifies на
эквивалентное объединение четырёх element targets, оставив requires/ensures/body:

```diff
-#[kani::modifies(ptr::slice_from_raw_parts_mut(dst, 4))]
+#[kani::modifies(
+    dst, dst.wrapping_add(1), dst.wrapping_add(2), dst.wrapping_add(3)
+)]
```

Каждый target имеет тип `*mut P::Elem` и выбирает `write_any_slim`,
`library/kani_core/src/lib.rs:723–724`, с `ptr::write(pointer, T::any())`.
Тот же диапазон, независимые произвольные valid values, те же postconditions
сохраняют корреляции через общую postcondition; outside frame не расширяется.
Это static candidate: проверка generated assigns/frame и ON execution обязательна.

Для merge произвольной длины замена slice четырьмя элементами недопустима.
Для конкретного consumer len4 возможен отдельный bounded wrapper
`merge4_profile<P>(v: &[P::Elem;4], dst: *mut P::Elem)` с прежними
`merge_regions(v,dst) && merge_halves_sorted(v)` и двумя прежними ensures,
с четырьмя modifies targets и прямым вызовом реального `bidirectional_merge`
с тем же reading comparator. Matching leaf и consumer должны перейти вместе:

```rust
#[kani::requires(merge_regions::<P::Elem>(v, dst) && merge_halves_sorted::<P>(v))]
#[kani::modifies(dst, dst.wrapping_add(1), dst.wrapping_add(2), dst.wrapping_add(3))]
#[kani::ensures(|_| model_sorted::<P>(dst, 4))]
#[kani::ensures(|_| model_count::<P>(v.as_ptr(), 4) == model_count::<P>(dst, 4))]
unsafe fn merge4_profile<P: Profile>(v: &[P::Elem; 4], dst: *mut P::Elem)
where
    P::Elem: FreezeMarker,
{
    let mut is_less = |a: &P::Elem, b: &P::Elem| P::cmp(a, b);
    unsafe { bidirectional_merge(v, dst, &mut is_less) }
}
```

```diff
-#[kani::stub_verified(merge_profile)]
+#[kani::stub_verified(merge4_profile)]
 fn profile_merge_consumer_u8_len4() {
     // прежние probe, source, count, uninit destination, checks и covers
-    unsafe { merge_profile::<LtU8>(&src, out) };
+    unsafe { merge4_profile::<LtU8>(&src, out) };
 }
+// новый #[kani::proof_for_contract(merge4_profile)] проверяет тот же len4 domain;
+// требует отдельной qualification и binding до использования summary.
```

Так сохраняется именно len4 obligation; общий merge 2..=32 этим не закрыт.
Нельзя заменить uninit output на заполненный: это сузит domain. Нельзя убрать
stub и считать modular consumer доказанным, отключить uninit checks или подавить
property. Общего harness-only обхода для произвольной длины не установлено.
MRE: `MRE-B-slice-havoc.rs`; публичный текст: `ISSUE-DRAFT-B.md`.

## C. Function-item ZST в `FnMut::call_mut`

SEL1 `check_uninit/ty_layout.rs:193–242` (`PointeeInfo::from_ty`) вызывает
`data_bytes_for_ty`. В `FieldsShape::Arbitrary` (302–303) function item попадает
в `RigidTy::FnDef` → `UnsupportedType` (509–515), несмотря на size=0.
ZST primitive shortcut (274) относится к другому FieldsShape;
ZST closure shortcut (481–485) относится только к Closure.
`check_uninit/mod.rs:295–302` превращает ошибку layout в observed unsupported check.
Upstream baseline тоже отклоняет FnDef (`ty_layout.rs:393–400`), там не
поддержаны и closures; рекомендация closure относится именно к SEL1.

Source `verify/helper_contracts.rs:30–39`: `&mut arbitrary_less::<T>` заставляет
generic `F: FnMut` стать function-item типом; shim `FnMut::call_mut` получает
указатель на этот ZST. Это layout support gap, не свидетельство uninit данных T.

Обход: closure, делающая прямой вызов прежнего comparator. Для пары leaf/consumer
нужен один общий factory с одним closure expression, чтобы они не получили
разные F-типы. Diff-набросок:

```diff
+fn reading_comparator<T>() -> impl FnMut(&T, &T) -> bool {
+    |a, b| arbitrary_less::<T>(a, b)
+}
 fn exercise_swap<T: kani::Arbitrary + Copy + PartialEq>() {
     // все прежние inputs, a/b, assumptions и frame/coverage
-    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut arbitrary_less::<T>) };
+    let mut cmp = reading_comparator::<T>();
+    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut cmp) };
 }
```

В остальных matching leaf/consumer call sites также использовать этот factory
с тем же T. `arbitrary_less` (9–18) по-прежнему выполняет оба volatile reads,
оборачивает дубликаты в ManuallyDrop и выбирает новый arbitrary bool на каждый
вызов; covers/stub coverage hook не меняются. Не заменять comparator на `<`
или constant и не добавлять bounds. Старое proof credit для function-item F
новому closure F не переносится. `fn` pointer не выбран: это другой layout и
indirect-call obligation; он не гарантирует устранения uninit support gaps.
MRE и closure comparison: `MRE-C-function-item.rs` (оба NOT_RUN).

## Upstream поиск: только чтение, 2026-11-16

Использованы `gh search issues/prs --repo model-checking/kani ... --limit 20
--json number,title,url,state` (оба состояния), затем адресные `gh issue/pr view`.
C2/#5151 и PolymorphicIter не исследовались заново. Ниже результат ограниченного
поиска, не утверждение, что issue/PR точно отсутствует.

| Gap | Точные запросы (issues и PRs, если не уточнено) | Вывод |
|---|---|---|
| A | `array_assume_init`; `uninitialized transmute`; `"MaybeUninit" "array"` | Прямого нового match не найдено. Известный #5151 исключён из анализа. [PR #3338](https://github.com/model-checking/kani/pull/3338) — общий padding/transmute gate, не поддержка array_assume_init |
| B | `write_any_slice`; `"write_any_slice" "uninit"` (PRs); `"uninitialized" "modifies"` (issues); `"initialization" "slice"` (PRs) | Прямого match на uninitialized output нет. [#3682](https://github.com/model-checking/kani/issues/3682) и [merged PR #4749](https://github.com/model-checking/kani/pull/4749) про прежний doubled-slice resolution crash; это другая ошибка |
| C | `uninit ZST`; `"FnDef" "uninit"` (issues); `"FnDef" "layout"` (PRs); `"zero-sized" "uninit"` (issues); `"zero-sized" "initialization"` (PRs); `"unsupported type" "fn"` (issues) | Прямого match не найдено. [merged PR #4899](https://github.com/model-checking/kani/pull/4899) исправляет primitive ZST panic, не FnDef arbitrary-fields layout |

Дополнительно проверен [open PR #5113](https://github.com/model-checking/kani/pull/5113):
missing MIR для cross-crate constructor в delayed UB, не FnDef byte-layout gate.
Публичный draft B оставлен непубликованным; runtime reproduction на baseline
пока UNKNOWN. Ничто из этих ссылок не означает, что будущий upstream HEAD проверен.

## Адресные наблюдения artifact

| Row / stdout.log | Строки / failed property | SHA256 локального файла |
|---|---|---|
| swap_contract_u8_n2 | 1098–1101: array_assume_init::<2>.unsupported_construct.1 | `e8d1a7084f46a978d2bea816fde8077cb1497912305a01e28f9740aa3934c1e7` |
| profile_merge_consumer_u8_len4 | 2435–2438: write_any_slice::<u8>.safety_check.1 | `8351fde5c58420080291dcfa1957f4be8b914dd88a9f52f655ece89f4c870efa` |
| profile_sort4_consumer_u64 | 304–307: write_any_slice::<u64>.safety_check.1 | `f676c8dab35f282777eb43af151c3196960864d7ea33bb1b99de6515a2e77181` |
| swap_safety_u8_backing4 | 302–305: FnMut::call_mut.unsupported_construct.1 | `cd59199b4d02cb0d26fae71412bc240bb33c410db148f605935fe4ab42c9ae73` |

Artifact B location печатается как `library/core/src/lib.rs:357:1` (macro
expansion), а helper body в закреплённом kani_core расположен на 716.
Смешивать эти координаты нельзя. Local file hashes идентифицируют прочитанные
данные, не подтверждают archive inventory или parser-input binding.

## Следующая отдельная стадия

Сначала разрешённое воспроизведение MRE с точными tool/source identities и
controls: initialized destination, thin-target variant и настоящий uninit-read
negative. Затем отдельный review/qualification source candidate A/C и точных
B wrappers. Для B нельзя заявлять compiler false positive без этой проверки.
Никакой Build, push, публикация issue или изменение ledger этим документом
не разрешены. Independent B1/B2 proof credit: NONE.
