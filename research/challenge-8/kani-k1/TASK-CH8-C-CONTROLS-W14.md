# TASK — worker14: C controls N1/N2/L3/L4 — source + CI-only пакет (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

## Контекст

Твой статический пакет [ch8-c-now](kani3300/ch8-c-now/HANDOFF.md) (g0 `9a135afa3c`) принят:
STOP C для расширения claim зафиксирован корректно; controls N1/N2/L3/L4 из
[CONTROLS-DESIGN.md](kani3300/ch8-c-now/CONTROLS-DESIGN.md) координатор разрешает реализовать и
подготовить к одному CI dispatch (bucket C, cap 1–2; это будет C-01).

## Источник

Отдельная source-ветка controls **вне S** (как A1-исключение): от production std
`872d5a43380752786415bc00d2a12ce0e930cb37`, worktree `/root/verify-rust-std-ch8-c-ctl-w14`,
ветка `work/ch8-c-ctl-w14`. Разрешено: один новый test-only модуль под существующим verify cfg +
его регистрация в `verify.rs` этой ветки. `smallsort.rs` и модели не менять (это S/13/11).
Tool: upstream `0aac16ef62da9e9d5645782d458593e5d78143ba` (организаторские флаги, uninit OFF).
Если какой-то control требует правки smallsort.rs или нового compiler поведения — пометь его
NOT_IMPLEMENTED с причиной, остальные делай.

## Что сделать

1. Реализовать N1, N2, L3, L4 строго по дизайну (volatile write-then-restore, живой `&T`, без
   assume(false)/stub_verified/оптимизируемых writes). Для каждого — ожидаемый исход и oracle
   (named property/description, reachability cover), как в дизайне. Unexpected PASS у N2 =
   documented alias gap, не failure пакета.
2. CI-only control на хосте `Tiramisu-Cake/kani` по образцу S1 kani-host
   (`kani3300/ch8-s1/kani-host/`, control `36db70978a`): parent = tool 0aac, только
   `.github/workflows/` + один control каталог, stock workflows удалены; push на
   `uninit-ci/ch8-c-ctl-*`; checkout std source-коммита ветки controls из
   `Tiramisu-Cake/verify-rust-std` (перечисли, что координатор должен запушить и под каким
   `[skip ci]` именем ветки). Runner — переиспользовать reviewed S1 runner; caps 600s/root,
   6 GiB, jobs1, ≤60 мин job. Чеклист: `runner.*` только в step env, fetch-depth ≥2, sibling
   layout, path normalization от cwd, static YAML/actionlint, attempt 1.
3. Synthetic tests на error paths, независимое review, findings исправить.
4. g0 `kani3300/ch8-c-ctl/`: CI-REQUEST (std/control SHA+tree, manifest SHA256), REVIEW, HANDOFF.
   Коммиты `[skip ci]`, author `Tiramisu-Cake <igkharin@gmail.com>` в команде.
   Последней строкой: `READY <std-sha> <control-sha> <g0-sha>` или `STOP <причина>`.

## Ограничения

Без push/CI/публикаций/ledger. Без локальных cargo/rustc/Kani/CBMC. Своя alias-модель не делается.
Intake B-01 (run 43774504122) — отдельная следующая стадия, не здесь.
