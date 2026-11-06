# LEANHELPERS — G1 PASS, рост времени отмечен

Build `ae8d547b-7c77-4312-bff5-fef9e64393fc`; Cloud SUCCESS, COMPLETE, gate=true, Kani exit0.
Source `1dff8cf56e8a2115b5b1091882b4f01eb223623c` — exact GO координатора.
Library `5c929ba094cef478efc350b3cd9d7b8fc73fe203`, tree `ed9d8de3a0a6ad930e69646ab6001a607971ae7b`.
Request `leanhelpers-g1-20261106-01`, SHA256 `66a7c5cbfac09d0f9468d4ae2680762c97af877d45cb21f6c3c376408b596bb5`.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; source/request/pool/check-tooling PASS относительно `59893bff1f`.
Diagnostic, standard4, jobs1, controls=true: cfg-on компиляция PASS; inventory=false.
Статика: ordinary233/cfg-on246; MUTANT13, START4, helpers51 = 68; прочие 178 token-exact.
Rustfmt --check PASS; smallsort.rs побайтно неизменён; library +65/-82 строк, net -17.

| Корень относительно verify:: | Status | с | Covers | Прежнее с | Δ |
| --- | --- | ---: | ---: | ---: | ---: |
| merge::drop_fallback_drop_count_n2 | SUCCESS | 0.8586333 | 2/2 | 0.6422159 | +33.7% |
| merge::drop_fallback_tag_permutation_n2 | SUCCESS | 1.1128453 | 2/2 | 0.6744263 | +65.0% |
| merge::sort4_arbitrary_comparator_u64_n4 | SUCCESS | 6.0442863 | 1/1 | 3.2531826 | +85.8% |
| merge::general_stable_direct_u8_n2 | SUCCESS | 4.4072623 | 2/2 | 2.8596132 | +54.1% |
| scratchgeom::stable_u64_min_scratch_n2 | SUCCESS | 3.7573495 | 2/2 | 5.838726 | -35.6% |
| merge::merge_contract_u8_n5 | SUCCESS | 52.383076 | 1/1 | 47.514442 | +10.2% |
| network::insert_tail_contract_u64_start1_tail15_to16 | SUCCESS | 263.85718 | 4/4 | 156.41757 | +68.7% |

Итого 332.4206327 с против 217.2001760 с (+53.0%); checks 0/3103, covers 14/14.
Unreachable covers0; прочие unreachable checks317 учитываются отдельно.
Baseline: шесть строк CI v8c Ubuntu; scratchgeom — наш VEIGHTINTEG standard4; covers везде прежние.
Рост >25% в 5/7: два drop дают лишь +0.216/+0.438 с; sort4 +2.791 с, general +1.548 с.
Tail +107.440 с (+68.7%) даёт 93.2% суммарного прироста; до лимита 480 с остаётся 216.143 с.
Парного before/after на этой машине нет: влияние формы кода/solver и окружения не разделено; отсутствие регрессии не заявлено.
Новых TIMEOUT нет; bounded OOM scan none_seen; CBMC max RSS 2993992 KiB, sampled total peak 3158312 KiB.
Verify wall с компиляцией 6:57.49; старт через 366 с после validate; доступный verify budget4434 с.
Targeted verify/unused scan: no match; общий warning sample достиг лимита40, не исчерпывающий.
Одна сборка, retries0/repairs0; расход $0.1890/$1.50, резерв $0.
13 controls скомпилированы, не выполнялись; compiler inventory и остальные корни не перепроверялись.
Только семь bounded diagnostic SUCCESS; полного matrix/universal-type/unwinding proof нет.
Bounded evidence и разбор: [report](leanhelpers/evidence/verification-report.json), [summary](leanhelpers/evidence/summary.md), [ledger](leanhelpers/RUN-LEDGER.json).
