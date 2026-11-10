# KANI3300 U1 — патч Kani: проверки инициализации для `MaybeUninit<T>` за raw pointer и transmute

**Выдано координатором 2026-11-11, GO владельца на ночную работу по kani#3300 (общий бюджет проекта ≤ $6.40).**
Research-ветка; цель — узкий патч Kani, пригодный для upstream PR. Публикаций нет. Dispatch только после
exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u1**, ветка **experiment/kani-k1-kani3300u1-20261111** (своя, отдельно
  от U0); tooling base
  `c98d7cee0d` (KT1: `kani_patch` + kind `kani-tests`, ≤ 20 selectors на запрос). Tooling, пин `f046b70644`,
  toolchain не менять.
- Код Kani — в новом локальном рабочем клоне **/root/kani-fix-3300** ровно на `f046b70644` (локальная ветка, без
  push; remote только официальный для fetch). `/root/kani-src-f046b70644` — read-only эталон. Патч для сборки:
  `research/challenge-8/kani-k1/kani3300/u1/kani-uninit.patch` = diff клона от полного `f046b70644`, **включая
  новые файлы** (commit в локальной ветке или `add -N`), SHA-256 в request.
- Slug **kani3300**, stage `kani3300-u1`, stable owner **k1-merge**, request `kani3300-u1-*`.
- Свой cap **$0.90**: одна сборка `kind: kani-tests` + не более одного repair по факту. Окно: main 420 + closeout 30.
- **Сборку не запускать до результата U0** (параллельный агент в `/root/verify-rust-std-kani3300`, ветка
  experiment/kani-k1-kani3300-20261111; читать через `git fetch` + `git show origin/<ветка>:research/challenge-8/kani-k1/RESULT-KANI3300-U0.md`): сначала
  подготовить патч и пакет, затем сверить с первым препятствием U0 и только потом PRE-BUILD. Если U0 показал другое
  препятствие — `Координатор, вопрос`.
- Worktree и ветку U0 не трогать (только читать опубликованное).

## Диагноз (статический, планер; проверь по исходникам)

- `visit_rvalue` / `CastKind::Transmute` → `tys_layout_compatible_to_size` возвращает false при union с любой
  стороны (`ptr_uninit/uninit_visitor.rs:523`, `ty_layout.rs:420`): `MaybeUninit<u8> -> u8` всегда «incompatible
  layouts», независимо от записи.
- Raw `Deref` → `build_get_and_check` отвергает `PointeeLayout::Union` (`check_uninit/mod.rs:318`); raw `Set` для
  union отвергается; отдельный guard на deref+чтение union-поля (`uninit_visitor.rs:447`); `data_bytes_for_ty`
  отвергает union при рекурсии в поля/элементы среза (`ty_layout.rs:403`).
- Shadow: object ID + offset + init bit для одного недетерминированно выбранного байта (`library/kani_core/src/mem_init.rs`);
  есть перенос для `AssignUnion`, `copy`/`copy_nonoverlapping`, аргументов верхнеуровневого union.

## Что реализовать (узко)

1. **`MaybeUninit<T> -> T` (и через `ManuallyDrop<T>`)**: вместо безусловного отказа — проверка, что data bytes `T`
   инициализированы в исходном значении; начать с T с поддерживаемой статической маской (u8, u64, простые struct с
   padding). Прочие union-transmute — прежняя диагностика.
2. **Union за raw pointer, минимум `MaybeUninit<T>`**: чтение поля `value`/`assume_init`-путь требует data bytes
   `T`; запись поля инициализирует ровно байты поля (с учётом смещения/размера); копия целого union переносит shadow
   (в т.ч. пустой/частично заполненный слот); `MaybeUninit::uninit()` поверх заполненного слота снимает
   инициализацию; срезы `[MaybeUninit<T>]` — через существующий механизм элементов. Прочие union (общий случай,
   вложенные) — остаются unsupported, явно.
3. Fn-pointer calls — **вне scope** (отдельная задача).
4. Узкий патч в `kani-compiler/src/kani_middle/transform/check_uninit/` (+ `kani_core` mem_init при необходимости).
   Ориентир 200–600 строк. Если требуется менять общий delayed-UB анализ/points-to — **стоп, `Координатор, вопрос`**.
   Стиль Kani, SPDX-заголовки в новых файлах, rustfmt по конфигу Kani (обёртка выше).

## Тесты (manifest ≤ 20 selectors)

- Новые `tests/expected/uninit/maybe-uninit-*/` (или по соглашению каталога), `--edition 2021`, `-Z uninit-checks`,
  пары positive/negative: `assume_init` без записи (FAILED на uninit-чтении) / после записи (SUCCESS); raw read
  `*const MaybeUninit<u8>` → `assume_init_read`; запись одного поля + чтение более широкого (FAILED);
  `copy_nonoverlapping` частично заполненного слота и чтение заполненной/незаполненной части; ненулевое смещение в
  срезе `[MaybeUninit<u64>]`; повторная запись `MaybeUninit::uninit()` поверх заполненного; padded T; delayed read
  через alias. Отрицательные — с конкретной ожидаемой диагностикой uninit-чтения в `.expected`, не просто FAILED.
- Регрессия существующих (выбрать, ≤ 20 вместе с новыми): `uninit/unions.rs`, `uninhabited-union-field`, `copy/…`,
  `transmute-padding`, `delayed-ub/…`, `access-padding-*`, `multiple-instrumentations.rs`. `fixme_*` — как NOT_RUN.
- Ни одного переписанного golden у существующих тестов.

## Приёмка

- PASS: патч применяется к свежему пину (identity дерева = локальный preflight); новые positive — native PASS;
  новые negative — ожидаемая uninit-диагностика из собственного вывода; существующие — штатный результат; нет
  TIMEOUT/ignored. Любой неожиданный SUCCESS отрицательного теста — **блокер корректности**, не «почти PASS».
- Статика: `git apply --check` на свежем пине, rustfmt — ноль diff, diffstat production/tests раздельно, изменений
  вне `kani-compiler/src/kani_middle/transform/check_uninit/`, `library/kani_core/` и `tests/` нет.

## RESULT

**RESULT-KANI3300-U1.md**, ≤ 45 строк: identities; суть семантики (5–8 строк, инвариант shadow); diffstat; таблица
тестов; что осталось unsupported; расход; черновик описания upstream PR (`u1/UPSTREAM-PR-DRAFT.md`, ≤ 12 строк).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]`, push без force, глобальный git config не менять, без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно. Никаких Actions/PR/issue/комментариев,
  push в model-checking/kani или Tiramisu-Cake/kani запрещён.
- Только наш код и исходники/тесты/документация Kani. Чужие PR verify-rust-std не открывать.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U1 ЗАВЕРШЁН**, одна стадия, затем стоп.
