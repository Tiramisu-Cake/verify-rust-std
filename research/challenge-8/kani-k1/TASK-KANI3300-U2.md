# KANI3300 U2 — replay строк U0 на Kani с патчем U1 + отрицательный контроль реального scratch-пути

**Выдано координатором 2026-11-11, ночной GO владельца (общий бюджет проекта ≤ $6.40), план согласован с планером.**
Research-ветка, в подачу не идёт. Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime
**Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u2**, ветка **experiment/kani-k1-kani3300u2-20261111** от U0 head
  `1f2cde2e9d` (tooling base `c98d7cee0d`; `verify/uninit_probe.rs` из U0). Tooling, пин Kani `f046b70644`, toolchain
  nightly-2026-10-23 не менять.
- `kani_patch` = **`research/challenge-8/kani-k1/kani3300/u2/kani-uninit.patch`** — побайтовая копия патча U1
  (SHA-256 `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`, U1 RESULT:
  `git show origin/experiment/kani-k1-kani3300u1-20261111:research/challenge-8/kani-k1/RESULT-KANI3300-U1.md`).
  Патч не менять.
- Slug **kani3300**, stage `kani3300-u2`, stable owner **k1-merge**, request `kani3300-u2-*`.
- Cap **$0.80**: одна сборка `kind: diagnostic`, `uninit_checks: true`, controls on, inventory off, standard4/jobs1,
  `--harness-timeout 3m`, 9 строк (9 × 3 + 30 = 57 мин, резерв $0.7695). Repair — только если факт + новый резерв ≤ cap.
  Окно: main 240 + closeout 30.
- Другие worktree (`kani3300`, `kani3300-u1`, `kani5072`, `kani5116`, `kani-traitpfc`) и клоны Kani не трогать.

## Library

Восемь существующих harness U0 в `verify/uninit_probe.rs` **не менять**. Добавить одну девятую строку:

| Row | Harness | Ожидание |
|---|---|---|
| U1 | `pincheck_calibration_uninit_read_u8` | FAILED именно на uninit-чтении |
| U2 | `pincheck_calibration_init_read_u8` | SUCCESS |
| U3 | `raw_uninit_read_sensitivity` | FAILED именно на uninit-чтении |
| U4 | `swap_contract_four_positions_u8` | прежний fn-pointer Unsupported |
| U5 | `sorted_permutation_insert_tail_u8_n2` | SUCCESS |
| U6 | `permutation_merge_u8_n4` | SUCCESS |
| U7 | `swap_contract_four_positions_u8_function_item` | прогноз планера: Unsupported на intrinsic `select_unpredictable` (`Intrinsic::from_instance` → Unimplemented); зафиксировать точную операцию и локацию |
| U8 | `small_sort_general_with_scratch_u8_n4` | SUCCESS |
| U9 | **новый** `small_sort_general_scratch_unwritten_slot_u8_n4` | ровно один uninit-отказ на втором чтении |

U9: та же геометрия, что U8 (N4, `[MaybeUninit::<u8>::uninit(); 20]`, `strict_less`, тот же panic stub). После
реального `small_sort_general_with_scratch` сначала наблюдаемое `assume_init_read` записанного `scratch[3]` (оно должно
пройти — алгоритм записал первые четыре слота; если это не так по коду, выбрать записанный слот по исходнику и
обосновать), затем наблюдаемое `assume_init_read` `scratch[4]` (никогда не записывается) → ожидаемый
`Reading from an uninitialized` на этой строке. Короткая уникальная привязка (`expect_check` + локация строки U9).
Проверить отсутствие отказа на чтении записанного слота. Core и requires не менять.

Код U9 — в том же `#![cfg(kani_smallsort_controls)]` модуле; rustfmt через обёртку
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --edition 2024 --config-path
research/challenge-8/kani-k1/codefix/rustfmt.toml`.

## Приёмка

- Сборка COMPLETE; binding: head, request, pin + `kani_patch` sha `306851ac…`, applied tree; фактический флаг
  `-Z uninit-checks` в argv; check-tooling PASS.
- Положительная половина калибровки (U2) SUCCESS; U1/U3/U9 — точные отрицательные checks с локациями (ровно ожидаемые
  отказы, ручная сверка числа отказов и covers в diagnostic gate).
- **Blocker:** SUCCESS при отключённом инструментировании, при недостижимом чтении (cover) или пропавшая negative
  sensitivity (U1/U3/U9 SUCCESS). Новый Unsupported у любой строки — разобрать по bounded evidence и описать.
- Для U4/U7 зафиксировать открытые ограничения дословно. Сравнить с U0 построчно.
- Statика: изменён только `verify/uninit_probe.rs` (+ research-файлы); rustfmt ноль diff.

## RESULT

**RESULT-KANI3300-U2.md** (в `kani3300/u2/`), ≤ 35 строк: identities; таблица 9 строк (status, failed/total, failed checks
дословно с локацией, класс); сравнение с U0; что доказано про scratch-путь при uninit-checks (и что нет: normal returns
из-за panic stub, только u8/N4, только general-путь); расход; что дальше (следующий core-пакет: u64 N4 через Stable
trait entry с function item, затем N8 — sort4).

## Коммиты, ожидание, запреты

- Library-коммит отдельно от research, все `[skip ci]`; push без force; глобальный git config не менять; без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh` summary/rows; raw logs, archives, credentials не читать; прямых GCS/storage/download/
  logging нет. Никаких локальных cargo/rustc/Kani/CBMC. Никаких Actions/PR/issue/комментариев на GitHub.
- Чужие PR verify-rust-std, их ветки и код не открывать.
- Это верификация корректности стандартной библиотеки Rust, не security-работа.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U2 ЗАВЕРШЁН**, одна стадия, затем стоп.
