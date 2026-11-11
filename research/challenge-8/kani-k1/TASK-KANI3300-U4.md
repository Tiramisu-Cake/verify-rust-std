# KANI3300 U4 — core replay U8/U9 (+U1/U2, U6) на Kani с патчем CMP2 (compound storage)

**Выдано координатором 2026-11-11, ночной GO владельца; состав строк — планер (`PLANNER-AFTER-U3-ANSWER.md` п.3, 5 в
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/`).** Research-ветка, в подачу не идёт. Runtime
**Codex**, одна стадия. **Dispatch только после native PASS CMP2 и exact-packet GO координатора.**

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u4**, ветка **experiment/kani-k1-kani3300u4-20261111** от U2 head `4ecdcc5930`
  (`verify/uninit_probe.rs` с 9 строками U0/U2 — **не менять**). Tooling: перенести KT2 (`3bb5445d2a`) cherry-pick'ом
  `d483dc3719` (из ветки experiment/kani-k1-kani3300u3-20261111) — lane-файлы должны совпасть с `3bb5445d2a`.
- `kani_patch` = **только production** финального кандидата CMP2 (`/root/kani-fix-3300-cmp`, ветка `fix/kani-3300-cmp`; после
  CMP2 RESULT — его принятый full candidate, сейчас `b1f0105c03`), diff от полного `f046b70644`, без тестов Kani (diffstat
  ≤ 4096). В PRE-BUILD: побайтное равенство production-секций с build-патчем CMP2. Если CMP2 сделает repair — перепривязать.
- Slug **kani3300**, stage `kani3300-u4`, owner **k1-merge**, request `kani3300-u4-*`. Cap **$0.80**: одна сборка
  `kind: diagnostic`, `uninit_checks: true`, controls on, inventory off, standard4/jobs1, `--harness-timeout 3m`.
  Строки: U1, U2, U6, U8, U9 (5 × 3 + 30 = 45 мин, резерв $0.6075). Repair — только с новым GO.
- Другие worktree/клоны не трогать (клон CMP — только чтение/`git diff` для экспорта патча).

## Ожидания

| Row | Harness (`uninit_probe::`) | Ожидание |
|---|---|---|
| U1 | `pincheck_calibration_uninit_read_u8` | FAILED именно на uninit-чтении |
| U2 | `pincheck_calibration_init_read_u8` | SUCCESS |
| U6 | `permutation_merge_u8_n4` | SUCCESS (регрессия U2) |
| U8 | `small_sort_general_with_scratch_u8_n4` | **SUCCESS**: нормальный возврат (cover), sortedness, count |
| U9 | `small_sort_general_scratch_unwritten_slot_u8_n4` | успешное чтение `scratch[3]` (covers достигнуты, отказа нет), затем **единственный** uninit-отказ на `scratch[4]` |

`expect_check` для U1/U9: `Reading from an uninitialized`. Новый Unsupported у любой строки — разобрать по bounded evidence
(KT2 excerpt + `native-field`), описать операцию и место; не объявлять SUCCESS.

## Приёмка и RESULT

- COMPLETE; binding head/request/pin + `kani_patch`/applied tree; фактический `-Z uninit-checks`; check-tooling PASS против
  `3bb5445d2a`. Ручная сверка числа отказов и covers для U1/U8/U9.
- **Blocker:** SUCCESS U9 (пропала negative sensitivity), отказ на `scratch[3]`, недостижимые covers U8/U9.
- **RESULT-KANI3300-U4.md** в `kani3300/u4/` (≤ 30 строк): таблица 5 строк (status, failed/total, covers, Failed Checks
  дословно с локацией, класс); сравнение с U2; что доказано про general scratch-путь u8/N4 под uninit-checks и что нет
  (panic stub → normal returns; только u8/N4; general-путь); расход; следующий шаг.

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force, без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native/native-field/rows`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно. Никаких Actions/PR/issue.
- Это верификация корректности стандартной библиотеки Rust инструментом Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U4 ЗАВЕРШЁН**, одна стадия, затем стоп.
