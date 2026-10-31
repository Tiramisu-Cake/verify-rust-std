# RESULT SPECDIAG — F03–F05/F09 reproducer, без исправления контрактов

Статус: COMPLETE (диагностическая матрица разобрана; это не «все controls green» и не закрытые UB).
T0 2026-10-31T14:30Z (коммит задания `fb02228814`; Codex → Claude Code ~15:19Z), deadline 19:30Z.
Base `391804160e`, cap `30f77e8599` (не переписан), library commit `4da5ec5554`, library tree
`9000a3c7a0` (исходный `b10a21505b` + только cfg-off `mod specdiag;` и `verify/merge/specdiag.rs`).
Kani pin `9461e07af7`, nightly-2026-10-12; tooling = cap (`check-tooling` ok для обеих сборок).
Static: `specdiag/check_specdiag.py` PASS — projection merge.rs без объявления byte-identical,
scope, PFC/plain атрибуты, 74 уникальных literal messages, requests = manifest.

| Build | UUID / request | Флаги | Head | Своя стоимость |
|---|---|---|---|---|
| G1 | `9d441b26-1aef-4f84-945d-b76a89e40ebf` / `specdiag-g1-20261031` (sha `defddecb…`) | diagnostic, controls, jobs1, uninit off, 3 мин | `e545511968` | $0.1890 |
| G2 | `2a7afedf-9b1b-4159-93c5-4553923d0359` / `specdiag-g2-uninit-20261031` (sha `e2544e19…`) | то же + `-Z uninit-checks` | `be83a1ce27` | $0.1215 |

Итого 2 builds, $0.3105 из $2, reserved 0. Проект после: used $68.7525 / cap $88.96.
`expectation_met=false` в обеих: ниже ручной разбор по file:line, aggregate gate не переписан.

## G1 — штатный семантический профиль (20 entries)

| № | Entry | Результат | Failure / covers | Класс |
|---|---|---|---|---|
| 1 | sort4_true_f_n4 | FAILED 1/330 | `is_sorted(dst, 4, &is_less)` smallsort.rs:683; admission cover sat | logical counterexample, matcher hit |
| 2 | insert_tail_true_f_n2 | FAILED 1/372 | ensures smallsort.rs:600 (`is_sorted(begin, …)` в продолжении строки) | logical counterexample; matcher miss |
| 3 | merge_true_f_n2 | FAILED 1/431 | `is_sorted_unrolled(dst, v.len(), &is_less)` smallsort.rs:844 | logical counterexample, matcher hit |
| 4 | swap_fnmut_runtime_n2 | SUCCESS 0/77 | cover 1/1; plain: ровно 1 вызов | positive |
| 5 | swap_fnmut_contract_n2 | FAILED 2/340 | observer specdiag.rs:130 + `Check that *var_4 is assignable` mem/mod.rs:982 (`mem::replace::<u8>`); covers 4/4 | measured violation: observer и frame отдельно |
| 6 | initialized_memory_positive | SUCCESS 0/68 | 1/1 | positive |
| 7 | uninit_tail_predicate_admission | SUCCESS 0/93 | 1/1 | positive: requires-пробел воспроизведён |
| 8 | uninit_tail_actual_pfc | SUCCESS 0/395 | 2/2 | missed sensitivity (NOT_DETECTED_IN_PROFILE) |
| 9 | uninit_sort4_predicate_admission | SUCCESS 0/35 | 1/1 | positive: requires-пробел воспроизведён |
| 10 | uninit_sort4_actual_pfc | SUCCESS 0/343 | 2/2 | missed sensitivity |
| 11 | readonly_sort4_source | SUCCESS 0/99 | 1/1, значения 0,2,4,6 | positive |
| 12 | readonly_source_predicates | SUCCESS 0/29 | 1/1: can_write(static)=true | positive (геометрия, не право записи) |
| 13 | probe_t129_helper_oob | FAILED 1/95 | `pointer outside object bounds` merge.rs:70; 3/3 | measured violation (helper) |
| 14 | probe_t129_actual_contract | TIMEOUT (3 мин) | — | tool limit: UNKNOWN |
| 15 | padded_probe | SUCCESS 0/111 | 3/3 | missed sensitivity |
| 16 | padded_swap_actual_contract | SUCCESS 0/329 | 2/2 | missed sensitivity; same-binding UNKNOWN |
| 17 | raw_uninit_read_sensitivity | SUCCESS 0/16 | 3/3 (оба значения) | missed sensitivity |
| 18 | invalid_bool_sensitivity | SUCCESS 0/16 | 2/3 (какой cover не sat — terse output не даёт) | missed sensitivity |
| 19 | swap_t129_same_positive | SUCCESS 0/311 | 1/1, unwind 140 | positive |
| 20 | swap_u64_pure_pfc_positive | SUCCESS 0/311 | 1/1 | positive (pipeline активен) |

1–3: ровно один failure, целевой sortedness ensures; requires проверены `kani::assert` и
admission cover выполнен. Cover «returned» UNREACHABLE: путь обрезан assert-assume самого
ensures (после тела), а не requires. #2: описание многострочное, lane видит первую строку
`|_|`; привязка вручную по smallsort.rs:600 и `g1.extracted.txt`.
#5: cover `calls==3` достижим, observer `calls==1` нарушен — это source-bound наблюдение,
не доказательство «ровно три вызова». Frame: запись `Cell` из closure (mem::replace::<u8>)
вне `modifies` — отдельный F03 effects-результат; production modifies не трогали.

## G2 — `-Z uninit-checks` контраст (8 entries, вне CI-флагов)

| № | Результат | Failure |
|---|---|---|
| 6 | SUCCESS 0/123 | — |
| 8 | FAILED 1/529, covers 0/2 | unsupported: init-layout `[MaybeUninit<u64>;2]` specdiag.rs:176 |
| 10 | FAILED 1/517, covers 0/2 | unsupported: `[MaybeUninit<u64>;4]` specdiag.rs:216 |
| 11 | FAILED 1/193, cover 0/1 | unsupported: raw pointers + unions, core hint.rs:844 (`select_unpredictable`) |
| 15 | FAILED 1/215, covers 0/3 | unsupported: raw pointers + unions specdiag.rs:291 |
| 16 | FAILED 1/480, covers 0/2 | unsupported: `[MaybeUninit<Pad>;2]` specdiag.rs:306 |
| 17 | FAILED 1/47, covers 0/3 | unsupported: raw pointers + unions specdiag.rs:322 |
| 18 | SUCCESS 0/45 | 2/3 covers; validity checks не включены и здесь |

Все FAILED G2 — unsupported-check инструмента до целевого read (covers 0): не negative control,
не обнаружение UB. Положительный #11 тоже недоступен этому профилю через production
`select_unpredictable`. G2 PASS/FAIL не является evidence штатного uninit-off CI.

## Вердикты

- F03 **confirmed**: always-true F нарушает ordered ensures sort4/insert_tail/merge при
  выполненных requires (logical counterexample). FnMut: под контрактом observer видит не 1
  вызов, и отдельно нарушен frame `modifies` записью состояния компаратора (measured).
- F04 **confirmed (admission) / unresolved (read)**: `valid_sorted_tail` и `valid_sort4_regions`
  пропускают неинициализированные tail/source (S 7, 9); actual reads в штатном профиле
  NOT_DETECTED (8, 10), в G2 — tool limit. `can_write(static)=true` подтверждено (12).
- F05 **narrowed**: OOB `matches_value_probe` для T=129 подтверждён в helper (13); в actual
  contract use — UNKNOWN (14 TIMEOUT). `same` с T=129 проходит (19): граница 128 только у probe.
  Padding: NOT_DETECTED в G1, tool limit в G2; same/padding-binding UNKNOWN.
- F09 **confirmed как missed sensitivity**: штатный профиль не видит raw uninit read и invalid
  bool (17, 18 S); `is_initialized` = true без uninit-checks (pin kani_intrinsics.rs:213),
  `-Z valid-value-checks` не передаётся (run-kani.sh:87). `-Z uninit-checks` на pin не
  поддерживает MaybeUninit-массивы и raw-pointer/union код, включая production sort4.

Разделение: logical counterexample — 1–3; measured violation — 5 (observer, frame), 13;
missed sensitivity — 8, 10, 15, 16, 17, 18 (G1); tool limit — 14 (G1), 8/10/11/15/16/17 (G2).

Подробности: `specdiag/manifest.json`, `g1|g2.summary.md`, `g1|g2.extracted.txt` (bounded
log-grep/log-lines), `DOMAIN-AND-CALLERS.md`, `callers.tsv`, `pin-sources.tsv`.
Полные/raw логи не читались. Исправления контрактов — следующая сессия.
