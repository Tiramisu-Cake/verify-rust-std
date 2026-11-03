# ZSTPROBE — откуда 4 pointer-check failures в stable ZST dispatch (диагностика + исправленный корень)

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-zstprobe**, ветка **experiment/kani-k1-zstprobe-20261103** от
  **e8e238db9d87323fa4da011a1a8b37fb76ec91c0** (v6 library + K-1 tooling + cap 93.96).
- Slug **zstprobe**, stable owner **k1-merge**. Новые stage/ledger/UUID/request_id `zstprobe-*`.
- Project cap **$93.96**, свой cap **$1.00**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Tooling base для check-tooling: e8e238db9d.
- Окно: main 120 + closeout 30 мин.

## Контекст

SAFETYGAPS
([RESULT](https://github.com/Tiramisu-Cake/verify-rust-std/blob/e6a0b17e1d1ca40f8a9c6c2337da3b82f176e603/research/challenge-8/kani-k1/RESULT-SAFETYGAPS.md)):
`network::dispatch_safety_stable_zst_n0_1_2_7_8_15_16_17_31_32` дал FAILED. Упали 4 из 391 проверок, все — набор
pointer-checks одного разыменования (NULL / invalid / outside object bounds / invalid integer address). Covers 11/11.
Terse не даёт location.

Гипотеза координатора: корень использует `volatile_reading_less::<()>` (`network.rs` около строки 239). Он делает
`ptr::read_volatile` на `&()`, а для ZST это ссылка в scratch или массив с висячим, но выровненным адресом. В проекте
уже есть `comparators::zst_aware_less`, который для ZST использует `ptr::read`, а не `read_volatile`; комментарий там
намекает на ту же проблему. Тогда это артефакт гармоники и модели Kani для volatile ZST-read, а не UB в `core`. Проверяем.

## Source scope

Новый opt-in child `network::zstprobe`, файл `verify/network/zstprobe.rs`. В `network.rs` — только
`#[cfg(kani_smallsort_controls)] mod zstprobe;`. Существующие roots, `dispatch_safety_fixed` и компараторы не менять.

Ровно 4 roots, `#[kani::proof]`:

1. **`zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32`.** Копия смысла `dispatch_safety_cases!` и
   `dispatch_safety_fixed::<(), N, true>`: тот же stub `panic_on_ord_violation → assume_order_violation`,
   unwind 65, scratch `[MaybeUninit<()>; 48]`, actual `<() as StableSmallSortTypeImpl>::small_sort`, те же covers по
   каждой длине и family end. Единственное отличие — компаратор `comparators::zst_aware_less::<()>` (возвращает
   `kani::any()`). Ожидание SUCCESS — это исправленный safety-корень ZST.
2. **`zst_stable_dispatch_volatile_n2`.** Исходный `volatile_reading_less::<()>` только при N2: локализуем по длине.
   Ожидание — неизвестно, записать наблюдение. В request expect SUCCESS. FAILED — допустимый диагностический исход, не
   ошибка стадии.
3. **`zst_read_volatile_dangling`.** Минимальный репро:
   ```
   let p = core::ptr::NonNull::<()>::dangling().as_ptr();
   unsafe { core::ptr::read_volatile(p) };
   kani::cover(true, "...");
   ```
   Ожидание по семантике Rust — SUCCESS: ZST-read через non-null aligned pointer допустим. FAILED здесь означает
   ложное срабатывание Kani.
4. **`zst_read_volatile_local`.** То же через `&()` на локальную переменную (`let x = (); read_volatile(&x)`).
   Это контроль.

Без новых stubs/assumptions сверх перечисленного. Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta;
- rustfmt;
- без warnings.

## Пакет

4 строки, **kind diagnostic** (если tooling допускает diagnostic с controls:true на standard4 — сверить с
`kani_k1.py`; иначе measurement с expect, как выше):
- gcb-e2-standard-4, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (4×10+30)×$0.0135 = **$0.945**.

Project ≤ 2 unfinished, ≤ 1 на k1-merge.

PRE-BUILD содержит:
- byte-diff root 1 против исходного (отличается только компаратор);
- semantic note по ZST: где появляются висячие ссылки (scratch, массив);
- hashes, budget.

Коммиты library/research отдельно, `[skip ci]`, push без force. `PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в
фоне.

## RESULT и классификация

**RESULT-ZSTPROBE.md**, ≤ 30 строк: таблица 4 строк — status, VT, checks, failed descriptions, covers. Для FAILED
строк — bounded `k1g.sh log-grep`.

Вывод — одна из трёх формулировок:
- (a) Kani-артефакт volatile ZST-read: 3 FAILED, 1 и 4 SUCCESS. Тогда исправленный корень 1 — кандидат.
- (b) проблема не в компараторе: 1 FAILED. Тогда стоп, классифицировать, писать координатору.
- (c) иное.

Если (a) — приложить к RESULT текст минимального репро для возможного issue в Kani. Сам issue не публиковать.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **ZSTPROBE ЗАВЕРШЁН**, одна стадия, затем стоп.
