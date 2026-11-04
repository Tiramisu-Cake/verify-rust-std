# LOOPINV — PRE-BUILD (Runtime: Claude Code)

Ветка `experiment/kani-k1-loopinv-20261103`, library base **e0fda080f5ea479d8f4fb801f4b42adde2b3259f**, задание 171f883fcb.
Library-коммит **3e07b5d1ef490c92441f40c39882a110769c0fa4** (3 файла, +116/−0; после него library не менялась).
Tooling: cherry-pick owner-exception **b1242ef7faccd9b4778d40be8967c764e439d5e4** → `30bd475d86` (только pathspec
guard в `gcb-k1.sh`). **check-tooling base = b1242ef7fa**: lane-файлы (k1g.sh LANE_PATHS) HEAD vs b1242ef7fa — diff пуст.
Research-коммит — тот, что указан в маркере PRE-BUILD REVIEW.

## Guard: блокер ревизии 1 снят (владелец, вариант 1, 2026-11-04)

Ревизия 1 (f278667653): guard `gcb-k1.sh` отвергал `kani_smallsort_controls` в `smallsort.rs` — `static-check-prebuild.json`
сохранён как есть. После cherry-pick guard исключает `:!library/core/src/slice/sort/shared/smallsort.rs`.
`check_loopinv.py` теперь читает pathspec guard из `gcb-k1.sh` на HEAD и повторяет его: совпадений **нет**
(`static-check-prebuild-r2.json`: `lane_stray_controls_guard: []`, `lane_files_differ_from_tooling_base: []`, errors []).
Source не менялся (sha256 трёх файлов те же). Обход guard не использовался.

## Изменение `smallsort.rs` (единственное; runtime не меняется)

```diff
@@ -590,6 +590,18 @@ pub fn insertion_sort_shift_left<T, F: FnMut(&T, &T) -> bool>(
         let mut tail = v_base.add(offset);
+        #[cfg_attr(
+            all(kani, kani_smallsort_controls),
+            crate::kani::loop_invariant(
+                mem::size_of::<T>() == 0
+                    || (crate::ub_checks::same_allocation(v_base, tail)
+                        && crate::ub_checks::same_allocation(v_base, v_end)
+                        && v_base.addr() < tail.addr()
+                        && tail.addr() <= v_end.addr()
+                        && (tail.addr() - v_base.addr()) % mem::size_of::<T>() == 0)
+            ),
+            crate::kani::loop_modifies(&tail, ptr::slice_from_raw_parts(v_base, len))
+        )]
         while tail != v_end {
```

- Путь `crate::kani::…` вместо `use crate::kani` — чтобы изменение в файле было одно (core: `kani_lib!(core)` даёт
  `pub use kani_core::*`, макросы loop_contracts там же). `.addr()` вместо `as usize`: core `deny(implicit_provenance_casts)`.
  Форма совпадает с уже проверяемым инвариантом `slice/iter.rs:189` (same_allocation + addr ≤ + `% size`).
- **Инвариант (только safety):** одна аллокация; `v_base < tail ≤ v_end` (строго: offset ≥ 1 — нужно `insert_tail`,
  `tail.sub(1)`); tail на границе элемента (выравнивание для `read`/`copy`). Вычитание защищено `v_base < tail`
  (short-circuit), `%` — дизъюнктом ZST. ZST: `tail == v_base == v_end`, цикл не входит, инвариант тривиален.
  Base: `tail = v_base + offset·size`, `1 ≤ offset ≤ len`. Step: guard `tail != v_end` ⇒ `tail + size ≤ v_end`.
  Sortedness/permutation не утверждаются.
- **`loop_modifies` нужен и обоснован:** Kani loop-contracts.md Limitation 2 — inference по alias analysis «пропускает
  цели, записанные вызванными функциями»; здесь все записи — внутри `insert_tail`, а Build один. Записи итерации:
  `tail` (локал); `insert_tail` пишет только `begin..=tail` (copy_nonoverlapping sift→gap и drop `CopyOnDrop` в
  `dst ∈ [begin, tail]`), это ⊂ `v[0..len]` = `slice_from_raw_parts(v_base, len)`; `tmp/gap_guard/sift` — локалы
  callee (DFCC пускает их сам); read-only компаратор ничего не пишет. Тот же приём (явный slice + функция с записями
  в теле) уже работает на пине в `slice/mod.rs:1035`. Summary/contract `insert_tail` не подставляется: вызывается
  реальное тело, его внутренний цикл разворачивается (`unwind(5)`, N=2 ⇒ ≤ 1 итерация, unwinding assertions вкл.).

## Roots (opt-in child `network::loopinv`, `verify/network/loopinv.rs`; в `network.rs` только `#[cfg(kani_smallsort_controls)] mod loopinv;`)

| # | Root | Тело | Covers (не-вакуумность) | Ожидание |
|---|---|---|---|---|
| 1 | `loopinv_insertion_u64_n2_offset1` | actual `insertion_sort_shift_left`, `[u64;2]` any, offset 1, read-only fn-item компаратор (volatile reads, `kani::any()`) | компаратор в абстрактном шаге; возврат после цикла (2) | SUCCESS |
| 2 | `loopinv_copy_true` | копия пролога+цикла (generic T), тот же инвариант/modifies, тело `tail.write(tail.read())` | тело шага; возврат (2) | SUCCESS |
| 3 | `loopinv_copy_false_control` | та же копия + конъюнкт `tail − v_base == size` (верен на входе, ломается первым шагом) | тело шага (1) | FAILED: `Check invariant after step for loop` |

Cover в компараторе root 1 достижим только в индуктивном шаге (тело цикла после havoc+assume) — он показывает, что
инвариант не вакуумен. Root 3 без cover после цикла: при ложном инварианте выход недостижим. Ручной вердикт root 3:
FAILED ровно на `loop_invariant_step` (описание + location `network/loopinv.rs`), base SUCCESS, других failed нет.

## Static (`loopinv/check_loopinv.py` → `static-check-prebuild-r2.json` на 30bd475d86, exit 0)

- ordinary 202 = base (sha256 `d5d55502…`), PFC-набор = base (статический счётчик атрибутов: 38 на обоих; 36 — цифра
  компиляторного inventory, метод иной; критерий — идентичность множества, sha `932af885…`).
- cfg-gate: `smallsort.rs` без атрибута == base байт-в-байт ⇒ без `kani_smallsort_controls` ordinary-код не меняется.
- name-set controls 384 → 387: ровно +3 loopinv roots, −0. rustfmt `--check --edition 2024` (fmtcfg) — exit 0 по
  трём файлам. Warnings: новых импортов без использования нет; компиляцию проверит только Build.
- **Побочный эффект (в ветке):** при controls:true атрибут действует во всём крейте ⇒ каждый root (ordinary и opt-in),
  достигающий `insertion_sort_shift_left` (small_sort-маршруты `smallsort.rs:44/201/349`, insertion_* в network/merge),
  получает абстракцию цикла; функциональные (sorted/count) roots там станут FAILED. Ветку нельзя использовать для
  controls-измерений других roots; в submission такой атрибут не переносить без отдельного решения.

## Request / hashes / budget

- `loopinv/request.json` == `RUN-REQUEST.json`, sha256 `0f084bc65dc00f70ed66ab56eaf9cce49422e0e3522cfd2165a9fa600e719492`;
  `loopinv-e2-diag-outer-loop-20261103`, k1-merge, diagnostic, gcb-e2-standard-4, controls true, jobs 1, uninit false,
  10 мин/строка; валиден `kani_k1.validate_request`.
- Source sha256: smallsort.rs `dd65d61e…620c`, network.rs `19ce3f33…5497`, loopinv.rs `bccbee50…2099` (полные — в JSON).
- Budget (`budget-prebuild-r2.txt`, 2026-11-04T07:40Z): used $91.9725, reserved $0, 211 builds; reserve
  (3×10+30)×$0.0135 = **$0.810**; после dispatch ≤ $92.78 ≤ cap $98.96; own spent $0 + $0.810 ≤ own cap $0.90.
  Slots: unfinished 0 (≤2 project / ≤1 k1-merge).
  Compile-repair возможен только если own spent + $0.810 ≤ $0.90, т. е. первый Build стоит ≤ $0.09 (≈ 6.7 мин).
- Риски: компиляция атрибута в core на пине; DFCC + внутренний цикл `insert_tail`; старый OOM. Любой из них —
  отдельный непринятый исход с bounded log-grep, без повторов.
