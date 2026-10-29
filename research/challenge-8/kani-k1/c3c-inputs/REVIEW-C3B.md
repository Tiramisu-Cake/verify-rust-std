# Независимое ревью library-коммитов C3b (субагент smallsort-reviewer, 2026-10-29)

Диапазон `7cb05823..96ed6f61`, только `library/`. **Решение: GO_WITH_NITS.** Домены не сужены, assertions
не потеряны, assume на выходы нет, runtime не тронут, строки ≤ 100. Компиляция/Kani/юнит-тесты лейна не
запускались.

## Исправить в C3c (обязательно)

1. **should-fix.** `verify/network.rs:352-366`: три ordinary-гармоники
   `dispatch_reachability_{stable_u8_n17, general_bytes16_n17, network_u8_n18}` проверяли только
   `cover(true, "dispatch route normal return is reachable")`. После E cover в ordinary вырезан — они стали
   дублями `dispatch_safety_*` (тот же `dispatch_safety_fixed`) и не дают заявленной в имени проверки; в
   RESULT-C3B/SOURCE-REVIEW/renamed-harnesses.tsv не отражено. Исправление: оставить в них настоящий
   `kani::cover` или перенести под `cfg(kani_smallsort_controls)` и внести в список.
2. **should-fix.** `tools/kani_k1.py:952-954`: `measurement_ok` для `kind=measurement` требует у каждой
   SUCCESS-строки `covers_total >= 1` и `covers_satisfied == covers_total`. После E почти все ordinary в
   correct/merge/network без covers → любой measurement-run с ними даёт `gate_ok=False` при PASS (в C3b не
   проявилось: все 19 запросов были `diagnostic`). Исправление: требовать covers только для `controls`
   (или явно задокументировать), с тестом.

## Мелкие

3. После route-split при `controls` один из двух covers с константным `stable` всегда UNSATISFIABLE
   (`correct.rs:180-181`, `merge.rs:847-848`) — 16 ложных пропусков в coverage-аудите. Выдавать cover только
   для фиксированного маршрута.
4. `network.rs:1199-1202`: при `Some(tail)` условие `START < tail < 17` не проверяется; сейчас все 54
   литерала верны, но ошибочный литерал тихо сделает requires vacuous. Предложение:
   `const { assert!(START < END && END < 17) }` в `insert_tail_contract_exact_case`.

## Проверено и корректно (кратко)

- D/insert_tail: start1..4 → хвосты ровно `START < t < 17` (15/14/13/12); тело, `proof_for_contract`, unwind 25
  сохранены. D/bytes16/17 n15/16/17 → 3×2 через `dispatch_safety_cases`, тело/stub/unwind 65 те же.
- B: `[11,12]` → `[11]` + `[12]`, offsets 1..N; unwind 13/14 достаточен (циклы ≤ N итераций), unwinding
  assertions не отключены.
- R: `stable = kani::any()` → две гармоники `false`/`true`; stubs, unwind 50/34, assertions те же.
- E: из ordinary уходят все covers в correct.rs (14), merge.rs (33), network.rs (54); остаются assembly (7),
  smoke (3) и witness `network.rs:557`. `proof_cover!` в ordinary раскрывается в `let _ = cond;`, предикаты
  вычисляются.
- K: `#[kani::solver(kissat)]` валиден на pin `9461e07a` (`cbmc_solver.rs`, `parse_solver`,
  `call_cbmc.rs:450` → `--external-sat-solver kissat`); Kissat ставят `install_deps.sh`, `run-kani.sh:157`
  проверяет версию.
