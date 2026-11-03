# PERMPROBE — дешевле сформулировать перестановку u64 N8 (index-probe, O(N²), kissat)

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-permprobe**, ветка **experiment/kani-k1-permprobe-20261103** от
  **4d0121052b630a05ce4c282849510899237ed262** (terminal PART2-POSTS8; library = v6 tree d4ec476a7a + POSTS8 child).
- Slug **permprobe**. Stable owner **k1-merge**: k1-network занят SAFETYNET. Новые stage/ledger/UUID/request_id
  `permprobe-*`. Ledger POSTS8 не возобновлять, чужие ledgers не трогать.
- Project cap **$88.96**, свой cap **$1.10**. **Один Build**, retry/G2 нет. Исключение — один compile-error
  repair с новым review/GO, если own spent + reserve ≤ cap.
- Окно: main 120 мин + closeout 30 мин, T0 при фактическом старте.

## Вопрос

POSTS8: на actual u64 N8 entry sortedness прошла за 67.8 с, а count-половина с независимой произвольной u64-пробой
дала TIMEOUT 600 ([RESULT-PART2-POSTS8.md](research/challenge-8/kani-k1/RESULT-PART2-POSTS8.md)).

Проверяем две логически эквивалентные формулировки перестановки, которые могут быть дешевле для CBMC, и влияние
solver kissat. Старый count root **не перезапускать**: на том же pin/profile он уже TIMEOUT 600. В RESULT дать ссылку,
VT считать UNKNOWN, speedup от 600 не вычислять.

## Неизменный domain

Всё как в `network::posts::partposts_count_u64_n8`:
- T=u64, exact initialized `[u64;8]=kani::any()`, все 64 бита, offset 0;
- копия pre до entry;
- function-item `super::strict_less::<u64>` (inferred `let mut cmp = ...`), actual
  `<u64 as UnstableSmallSortTypeImpl>::small_sort`;
- unwind 25 и unwinding assertions;
- **никаких stubs, PFC, verified summaries, assume на payload, уменьшения width, cuts или новых contracts.**

Старые roots, их helpers и bodies не менять, в том числе posts.rs-корни POSTS8 и parent network.rs.

## Source scope

Новый opt-in child **network::posts::perm** в файле **verify/network/posts/perm.rs**. В posts.rs — только
`#[cfg(kani_smallsort_controls)] mod perm;`. Visibility не расширять. Ровно 5 новых roots: 3 positive и 2 negative.

Ordinary 202 / PFC 36 неизменны. Static cfg-on 388→393, opt-in 186→191. Проверить exact name-set delta;
native inventory не запускать.

### Positive roots (`#[kani::proof]`, unwind 25)

1. **`perm_index_u64_n8`**:
   - `j = kani::any_where(|j: &usize| *j < 8)`;
   - `probe = pre[j]` берётся из сохранённой копии **до** сортировки;
   - после actual entry: `count(pre, probe) == count(v, probe)`, через существующий parent typed
     `count_matching_values` или локальный эквивалент без масок и casts.
2. **`perm_quadratic_u64_n8`**:
   - для каждого `i < 8`: `count(pre, pre[i]) == count(v, pre[i])` (кратности, O(N²));
   - без произвольной пробы и без `j`.

   Одного «каждое значение встречается в выходе» недостаточно: нужна кратность.
3. **`perm_index_kissat_u64_n8`**:
   - тот же общий body/helper, что у root 1;
   - единственное отличие — `#[kani::solver(kissat)]`.

   Если на пине или в образе kissat недоступен — это blocker: строку не подменять, зависимости не ставить, сообщить
   координатору.

### Метатеорема в PREBUILD (обязательно)

**Index-probe.** Пусть S — множество различных значений pre. Универсальный `j<8` проверяет
`count_post(x) = count_pre(x)` для всех `x ∈ S`. Сумма этих кратностей равна 8 = len(post), поэтому места для
посторонних значений нет. Отсюда post — перестановка pre как мультимножество. Duplicates допустимы.

**O(N²).** То же самое, развёрнуто по всем `i`.

**Итог.** Обе формулировки эквивалентны прежнему claim «для всех u64 probe count сохранён» на этом domain. «2⁶⁴ → N»
описывает только выбор пробы; входы остаются полными 64-битными, ускорение заранее неизвестно.

### Covers

Каждому positive — по 2 required covers после actual return и post-check:
- output отличается от pre (существующий `prefix_unchanged` или эквивалент);
- проверка достигнута.

Тяжёлых quantified covers не добавлять.

### Negative controls (expected FAILED только по своему literal)

Witness: P=1u64<<40, Q=1u64<<41, input `[P;8]`. Выполнить real entry. До порчи поставить root cover
returned-before-corruption. Затем `v[7]=Q`: порядок сохраняется, count(P) меняется 8→7.

4. **`perm_index_negative_u64_n8`**:
   - `j` из `any_where(<8)` над pre (все позиции = P);
   - cover check-reached ставится **до** последнего assert;
   - FAILED только literal **`permprobe negative: index count`**.
5. **`perm_quadratic_negative_u64_n8`**:
   - тот же witness, O(N²)-checker;
   - FAILED только literal **`permprobe negative: quadratic count`**.

Covers 2/2 у каждого control. Ни одного cover после failing assert и ни одного cover в helpers. Unexpected failure
(UB, unwinding, coverage, другой literal) intended-negative не засчитывать.

## Пакет G1

| Row (prefix `slice::sort::shared::smallsort::verify::network::posts::perm::`) | Expect |
|---|---|
| perm_index_u64_n8 | SUCCESS |
| perm_quadratic_u64_n8 | SUCCESS |
| perm_index_kissat_u64_n8 | SUCCESS |
| perm_index_negative_u64_n8 | FAILED (literal) |
| perm_quadratic_negative_u64_n8 | FAILED (literal) |

Профиль measurement:
- gcb-e2-standard-4 → k1-standard4, 4 CPU / 16 GiB, swap off;
- controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10;
- Kani **9461e07af7ec929f050aa4192f29363c9be07779**, nightly-2026-10-12;
- tooling **30f77e859903df14b442ff9294d4fbbd44827f20**, check-tooling против него;
- без highmem и новых request fields.

Резерв **(5×10+30)×$0.0135 = $1.080 ≤ cap $1.10**. Project ≤ 2 unfinished Builds, ≤ 1 на owner: сверить с SAFETYNET
(k1-network). Global spent + reserves ≤ $88.96.

PRE-BUILD содержит:
- semantic diff и метатеорему;
- annotations/covers/literal table;
- неизменность старых roots и ordinary set;
- static rustfmt;
- hashes source/library/tree/request/pin/tooling;
- budget/slots/deadline.

Library и research коммиты отдельно, `[skip ci]`, push без force. Последней строкой
`PRE-BUILD REVIEW <sha>`, затем стоп до GO. Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` в фоне
(run_in_background) и завершить ход.

## Gate и RESULT

Gate каждого positive отдельно:
- SUCCESS, 0 unintended failures, 2/2 covers;
- credit перестановки — только прошедшему oracle;
- controls — отдельный gate.

Если оба oracle дали TIMEOUT — STOP. Width/domain не уменьшать, второй Build не запускать. Kissat vs default
сравнивать только как один paired run (это не рейтинг solver). Отдельно указать CBMC/kissat RSS и process-sum,
если они доступны; иначе UNKNOWN.

**RESULT-PERMPROBE.md**, ≤ 35 строк:
- identities;
- таблица из 5 строк: status, VT, checks, covers, RSS;
- для справки строка POSTS8 count (TIMEOUT 600, VT UNKNOWN);
- метатеорема одной строкой;
- spent/reserved;
- вывод, какой oracle годится для v7 и для композиции.

PASS — opt-in proof того же domain, а не ordinary promotion и не generic T/F/N.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; никаких Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **PERMPROBE ЗАВЕРШЁН**, одна стадия, затем стоп.
