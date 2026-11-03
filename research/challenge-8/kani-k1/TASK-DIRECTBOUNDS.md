# DIRECTBOUNDS — прямая перестановка network u8 при N10 и N13 тем же компаратором, что A9

**Выдано координатором 2026-11-03; dispatch только после exact-packet PRE-BUILD review/GO координатора.**
Runtime **Claude Code**, одна стадия, без субагентов.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-directbounds**, ветка **experiment/kani-k1-directbounds-20261103** от
  **f23d7f2354cff734880cd1b930e6ee8e56289815**: NETCOMP2 `58d464ce1ce3d3ad7e60325e3297fdf07d38db4c` (library tree
  `3b6d2a51dae08e52464f4b2b82f5168d8ba9977b`) + cherry-pick cap-коммита `e8e238db9d`.
- Slug **directbounds**, stable owner **k1-network**. Dispatch только после terminal/accounting ROUTESEF (тот же owner).
  Новые stage/ledger/UUID/request_id `directbounds-*`.
- Project cap **$93.96**, свой cap **$1.00**. **Один Build**, retry нет. Один compile-error repair — только если own spent
  + reserve ≤ cap и project ≤ cap.
- Tooling base для check-tooling: **e8e238db9d87323fa4da011a1a8b37fb76ec91c0**.
- Окно: main 120 мин + closeout 30 мин.

## Вопрос

В NETCOMP2 `network::netcomp::netcomp_direct_u8_n9` (A9, `positive9(false)`) прямо доказывает sortedness и full-value
count u8 N9: SUCCESS 242.9 с, 4/4 covers
([RESULT-NETCOMP2](research/challenge-8/kani-k1/RESULT-NETCOMP2.md)). NETTHIRTEEN N13 count дал TIMEOUT, но с другим
компаратором (function-item).

Нужны точки N10 и N13 **тем же компаратором `U8Cmp = StrictU8::CMP` (fn-pointer) и тем же default solver**. Тогда
граница прямой перестановки u8 в limitations формулируется на одном компараторе и одном solver.

## Source scope

Новый opt-in child **network::netcomp::directbounds**, файл `verify/network/netcomp/directbounds.rs`. В netcomp.rs —
только `#[cfg(kani_smallsort_controls)] mod directbounds;`. Существующие A9, `positive9`, helpers, runtime не менять.
Visibility не расширять без обоснования.

Ровно 4 roots, у всех `#[kani::proof]` и `#[kani::unwind(25)]`, без stubs, summaries и adapters:

1. **`direct_u8_n10`** — клон смысла `positive9(false)` для N10:
   - полный `any [u8; 10]`, pre copy, независимая `any u8` проба;
   - явный `let mut cmp: U8Cmp = StrictU8::CMP`, actual `<u8 as UnstableSmallSortTypeImpl>::small_sort`
     (тот же вызов, что в `run9` при composed = false — сверить по source);
   - assert sortedness + full count;
   - те же четыре post-call covers: moves, probe hit, probe miss, duplicates.
2. **`direct_u8_n13`** — то же для N13.
3. **`count_negative_u8_n10`**:
   - `[0u8; 10]`, real sort;
   - initial sortedness/count проходят, cover returned-before-corruption;
   - `v[9] = 1`: порядок сохраняется, count(0) 10→9;
   - cover check-reached **до** последнего assert;
   - FAILED только literal **`directbounds negative: count n10`**.
4. **`count_negative_u8_n13`** — то же для N13, literal **`directbounds negative: count n13`**.

Если `positive9` можно переиспользовать как generic по N без изменения A9, — так и сделать. Иначе — копия с byte-diff
в PREBUILD.

Static:
- ordinary 202 / PFC 36 неизменны;
- exact name-set delta по cfg-on/opt-in;
- rustfmt через wrapper;
- без новых warnings.

## Пакет G1

4 строки, measurement:
- gcb-e2-standard-4, controls:true, kani_jobs:1, uninit_checks:false, harness_timeout_minutes:10, default solver;
- expect: SUCCESS, SUCCESS, FAILED(literal), FAILED(literal).

TIMEOUT positive — ресурсный исход, без зачёта и без retry.

Резерв **(4×10+30)×$0.0135 = $0.945 ≤ cap $1.00**. Project ≤ 2 unfinished, ≤ 1 на k1-network.

PRE-BUILD содержит:
- semantic diff и сопоставление с A9: T, F-категория, CMP, probe, actual route по N10/N13;
- covers/literals;
- static delta, hashes;
- budget/slots.

Коммиты library/research отдельно, `[skip ci]`, push без force. Последней строкой `PRE-BUILD REVIEW <sha>`, стоп до GO.
`k1g.sh wait BUILD` в фоне.

## RESULT

**RESULT-DIRECTBOUNDS.md**, ≤ 30 строк. Таблица N9 (A9, справочно) / N10 / N13:
- status, VT, checks, covers, CBMC RSS;
- маршрут сети при каждом N.

Формулировка границы для limitations одной строкой. Без интерполяции на N11/N12.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks.
- Raw logs, archives, Cloud Logging, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Код конкурирующих PR, их ветки и diff не открывать.

Маркеры `REVIEW REQUEST <sha>` / **DIRECTBOUNDS ЗАВЕРШЁН**, одна стадия, затем стоп.
