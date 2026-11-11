# KANI3300 CMP2 — исправление ложного uninit на ordinary-полях контейнера IntoIter (repair CMP1)

**Выдано координатором 2026-11-11, ночной GO владельца.** Runtime **Codex**, одна стадия. Dispatch только после exact-packet
PRE-BUILD review/GO координатора.

## Факты (CMP1 build 77e4765a, bounded excerpt KT2, прочитано координатором)

- offset 0 `maybe-uninit-wrap-u3-intoiter` и offset 1 `compound-cmp1-positive`: positive падают на
  `std::ops::index_range::IndexRange::len.safety_check.1/.2` — «Reading from an uninitialized pointer of type `usize`» @
  core `ops/index_range.rs:52:51` и `:52:61` (чтение `self.end`/`self.start`). Т.е. ordinary-поле `alive: IndexRange`
  контейнера `PolymorphicIter` на пути `into_iter`/`next` считается неинициализированным — **ложный отказ** (fc=24 / 16).
- offset 6 `compound-cmp1-padding-negative`: собственные Failed Checks присутствуют — `Pad` @ main.rs:104, `u32` @ :64,
  `C<Pad>` @ :43, `*const u8` @ ptr/mod.rs:1754, `u8`; ошибка native — «required diagnostic absent» → вероятно,
  несовпадение diagnostic/golden, а не поведение. Проверить и исправить тест (ожидания не ослаблять).
- Детали: `/tmp/kani-k1-gcb/summary-77e4765a-d82a-48c8-bf2e-cb6ae2fcdc07/summary/summary.json` (bounded summary; читать
  через `k1g.sh native`/`native-field`), RESULT CMP1 `kani3300/cmp1/RESULT-KANI3300-CMP1.md`.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-cmp**, ветка **experiment/kani-k1-kani3300cmp-20261111**; клон Kani
  **/root/kani-fix-3300-cmp**, ветка `fix/kani-3300-cmp` (CMP1 завершён; продолжать от full candidate `6ef9fd7206`).
  Tooling base `3bb5445d2a`. Пин, toolchain, tooling не менять.
- Stage `kani3300-cmp2`, owner **k1-merge**, request `kani3300-cmp2-*`. Cap **$0.60**: одна native `kind: kani-tests`
  (work ≤ 10 мин, резерв ≈ $0.540). Repair — только с новым GO. Окно: main 300 + closeout 30.

## Что сделать

1. Статически найти, где теряется init-состояние R-байтов `alive` на пути `[usize;2].into_iter()` → `next()`: aggregate
   `PolymorphicIter{alive,data}` / `ManuallyDrop::new` / `IntoIter{inner}` / return из `new_unchecked`/`into_iter`, unsize в
   `&mut PolymorphicIter<[MaybeUninit<T>]>` и field projection `.alive` через DST-ссылку. Минимальный repro (≤ 20 строк) —
   positive fixture, который ловит именно этот шаг (по отдельности: aggregate+move, ManuallyDrop, unsize+projection).
2. Исправить в рамках дизайна CMP0 + правок планера (R получает typed mask ordinary-операнда после его проверок; S не
   благословляется; P=false). Не ослаблять negative: все 35 negative harness CMP1 должны сохранить свои отказы.
3. padding-negative: выровнять diagnostic/golden по фактическому выводу, сохранив требование каждого собственного отказа.
4. Независимое ревью production-дельты CMP2 − CMP1 (Luna/subagent).
5. Manifest ≤ 20: новые repro + offset 0, 1, 6 + 4–6 ключевых negative CMP1 (empty/overwrite/call/projection/layout) +
   plain-negative и review-positive. Build-патч урезанный (как CMP1).

## RESULT

**RESULT-KANI3300-CMP2.md** в `kani3300/cmp2/` (≤ 30 строк): причина (файл:строка), фикс, diffstat CMP2 − CMP1, таблица,
расход; готовность к core replay U8/U9 (+U1/U2, U6).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force, без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native/native-field`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно. Никаких Actions/PR/issue.
- Неожиданный SUCCESS negative — блокер, стоп и `Координатор, вопрос`.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 CMP2 ЗАВЕРШЁН**, одна стадия, затем стоп.
