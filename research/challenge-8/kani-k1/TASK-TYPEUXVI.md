# TYPEU16 — фаза B4: safety dispatch на u16 (дополнение матрицы типов)

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-typeuxvi**, ветка **experiment/kani-k1-typeuxvi-20261104** от
  **b1ff545720** (TYPESPLIT: v6 + `network::typematrix` + 12 split-roots) и уже сделанный координатором
  cherry-pick e0fda080f5 (cap 98.96, только `k1g.sh`).
- Slug **typeuxvi**, stable owner по свободному слоту (k1-network или k1-merge; указать в PRE-BUILD). Новые
  stage/ledger/UUID/request_id `typeuxvi-*`.
- Project cap **$98.96**, свой cap **$1.40**. **Один Build**, retry нет. Исключение — один compile-error repair, если
  own spent + reserve ≤ cap.
- Tooling base для check-tooling: e0fda080f5.
- Окно: main 150 + closeout 30 мин.

## Контекст

TYPEMATRIX и TYPESPLIT закрыли `(u8, u32)`, u128 и `[u8; 9]`, а u16 был отложен. u16 — это size 2, align 2, маршрут
unstable network; новое — только ширина элемента.

## Source scope

Только `verify/network/typematrix.rs`: `impl ArbitraryValue for u16` (полный `kani::any()`), const-assert на
size/align и `has_efficient_in_place_swap::<u16>()`, и 7 roots существующими локальными макросами:
- pair stable+unstable `{0,1,2,7,8}` и `{15,16,17}` (2 roots);
- unstable `{9,12,13,18}` (1 root);
- single-route stable/unstable × N31/N32 (4 roots).

Тот же произвольный читающий компаратор `volatile_reading_less`, тот же panic-stub, unwind 65, scratch 48.
Существующие roots не менять.

Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta (+7);
- rustfmt;
- без warnings.

## Пакет

7 строк, measurement, expect SUCCESS:
- gcb-e2-standard-4, controls:true, kani_jobs 1, uninit off, 10 мин/строка;
- резерв (7×10+30)×$0.0135 = **$1.350**.

PRE-BUILD: соответствие клеток, hashes, budget. Коммиты library/research отдельно, `[skip ci]`, push без force.
`PRE-BUILD REVIEW <sha>`, стоп до GO. `k1g.sh wait` в фоне.

## Gate и RESULT

**Gate root.** SUCCESS, 0 failures, все covers. TIMEOUT/FAILED — bounded facts, без retry.

**RESULT-TYPEUXVI.md**, ≤ 25 строк:
- таблица 7 строк;
- закрытые клетки u16;
- v7-кандидаты (≤ 300 с).

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **TYPEUXVI ЗАВЕРШЁН**, одна стадия, затем стоп.
