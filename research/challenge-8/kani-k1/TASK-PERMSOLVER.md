# PERMSOLVER — kissat для двух других формулировок перестановки u64 N8 (canary)

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-permsolver**, ветка **experiment/kani-k1-permsolver-20261103** от
  **a7271841047ef010fbbb2719ce01d7018b2d1cc7** (terminal PERMPROBE).
- Slug **permsolver**, stable owner **k1-merge**. Запускать только после terminal/accounting COVERCOST: это тот же
  owner. Новые stage/ledger/UUID/request_id `permsolver-*`. Чужие ledgers не трогать.
- Project cap **$88.96**, свой cap **$1.00**. **Один Build**, retry нет. Исключение — один compile-error repair с
  новым review/GO, если own spent + reserve ≤ cap.
- Окно: main 120 мин + closeout 30 мин.

## Вопрос

PERMPROBE ([RESULT-PERMPROBE.md](research/challenge-8/kani-k1/RESULT-PERMPROBE.md)) на actual u64 N8 entry:

| Формулировка | Default | Kissat |
|---|---|---|
| index-probe | TIMEOUT | SUCCESS 574 с |
| O(N²) | TIMEOUT | — |
| Произвольная u64-проба (POSTS8 `partposts_count_u64_n8`) | TIMEOUT | — |

Нужно отделить вклад solver от вклада oracle. Строим kissat-варианты двух оставшихся oracle. Канарейка: если снова
~574 с или TIMEOUT, C1 замораживаем.

## Source scope

Новый opt-in child рядом с perm: **network::posts::perm::solver**, файл **verify/network/posts/perm/solver.rs**. В
perm.rs — только `#[cfg(kani_smallsort_controls)] mod solver;`. Старые roots, тела и helpers не менять. Если нужен
общий body, вызывать существующие helpers (`quadratic_counts_preserved`, parent `count_matching_values`), не меняя их.
Visibility расширять только если без этого нельзя, и с обоснованием в PREBUILD.

Ровно 4 новых roots, у всех `#[kani::proof]`, `#[kani::unwind(25)]` и `#[kani::solver(kissat)]`:

1. **`perm_arbitrary_kissat_u64_n8`**. Тело эквивалентно POSTS8 `partposts_count_u64_n8`:
   - full any `[u64;8]`, pre copy, независимая `probe: u64 = kani::any()`;
   - function-item `strict_less::<u64>`, actual `<u64 as UnstableSmallSortTypeImpl>::small_sort`;
   - assert `count(pre, probe) == count(v, probe)`;
   - те же covers: sort moves, check reached.

   Лучше вызвать исходное тело напрямую, если оно вынесено. Если нет — копия с byte-diff в PREBUILD.
2. **`perm_quadratic_kissat_u64_n8`** — тело `perm_quadratic_u64_n8`; отличие только solver.
3. **`perm_arbitrary_kissat_negative_u64_n8`** — witness `[P;8]`, probe=P, P=1<<40, Q=1<<41:
   - actual sort, initial check;
   - cover returned-before-corruption;
   - `v[7]=Q`, sortedness assert;
   - cover check-reached **до** последнего assert;
   - FAILED только literal **`permsolver negative: arbitrary count`**.
4. **`perm_quadratic_kissat_negative_u64_n8`** — то же для O(N²); literal **`permsolver negative: quadratic count`**.

Никаких stubs, PFC, summaries, assume на payload и сужения width. Covers не ставить после failing assert.

Static: ordinary 202 / PFC 36 неизменны; cfg-on 393→397, opt-in 191→195; проверить exact name-set delta. rustfmt через
разрешённый wrapper. Неиспользуемых переменных и новых warnings не допускать.

## Пакет G1

4 строки, measurement:
- gcb-e2-standard-4, controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10;
- Kani 9461e07a, tooling 30f77e85, check-tooling;
- expect: SUCCESS, SUCCESS, FAILED(literal), FAILED(literal).

Резерв **(4×10+30)×$0.0135 = $0.945 ≤ cap $1.00**. Project ≤ 2 unfinished Builds, ≤ 1 на k1-merge; параллельно может
идти ROUTESCD (k1-network). Global spent + reserves ≤ $88.96.

PRE-BUILD содержит:
- byte-diff новых тел против исходных (отличие только solver attribute и literals controls);
- метатеорему эквивалентности (ссылка на PERMPROBE);
- covers/literals table, static delta;
- hashes и budget/slots.

Коммиты library/research отдельно, `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <sha>`, стоп до GO.
`k1g.sh wait BUILD` в фоне, завершить ход.

## Gate и RESULT

Gate positive: SUCCESS, 0 unintended failures, 2/2 covers. Controls — только свой literal, 2/2. Credit перестановки —
только прошедшему oracle. Kissat RSS и process-sum отдельно, если доступны.

**RESULT-PERMSOLVER.md**, ≤ 30 строк. Сводная таблица solver × oracle с этой строкой и историческими (PERMPROBE, POSTS8)
как references. Вывод:
- **C1 жив**, если хотя бы один oracle с kissat ≤ ~300 с GCB. Назвать его кандидатом для N9..12.
- **C1 заморожен**, если все около 574 с или TIMEOUT.

Speedup из TIMEOUT cap не выводить.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **PERMSOLVER ЗАВЕРШЁН**, одна стадия, затем стоп.
