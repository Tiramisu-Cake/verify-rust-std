# WIDEDOMAINS — G1/G2 разобраны, G3 ожидает review

G1 `f303fd59-fa90-4c25-a50d-8c7ab7146fea`, source `90fadd7ccf8b5bb32d04401d274a6f492b612897`, request `widedomains-g1-20261105-01`. G2 `100bfc31-d211-4e7a-be52-fc6e72ab7d69`, source `4fbe77cf46cd416fb6140a54bf6c9ffb78479d3c`, request `widedomains-g2-20261105-01`.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; k1-merge, standard4, diagnostic, controls=true, jobs=1; bindings/tooling PASS.
Оба Cloud FAILURE, COMPLETE, gate=false, Kani exit1; watchdog180 с. У TIMEOUT время/checks/covers не установлены.

| G / корень widedomains:: | Статус | с | Failed/total | Covers |
| --- | --- | ---: | --- | --- |
| G1 swap_safety_u8_backing32 | SUCCESS | 33.71013 | 0/234 | 9/9 |
| G1 swap_safety_u64_backing32 | SUCCESS | 40.420055 | 0/234 | 9/9 |
| G1 unstable_network_safety_u8_n32_stubbed | SUCCESS | 135.0917 | 0/387 | 5/5 |
| G1 insert_tail_safety_u64_backing32_tail1_to4 | TIMEOUT | — | — | — |
| G1 insert_tail_safety_u64_backing32_tail5_to8 | TIMEOUT | — | — | — |
| G1 insert_tail_safety_u64_backing32_tail9_to12 | TIMEOUT | — | — | — |
| G1 insert_tail_safety_u64_backing32_tail13_to16 | TIMEOUT | — | — | — |
| G1 insert_tail_safety_u64_backing32_tail17_to19 | TIMEOUT | — | — | — |
| G1 insert_tail_safety_u64_backing48_tail1_to4 | TIMEOUT | — | — | — |
| G1 insert_tail_safety_u64_backing48_tail5_to8 | TIMEOUT | — | — | — |
| G2 insert_tail_initialized_u64_backing32_tail1_to4 | TIMEOUT | — | — | — |
| G2 insert_tail_initialized_u64_backing32_tail5_to9 | TIMEOUT | — | — | — |
| G2 insert_tail_initialized_u64_backing32_tail10_to14 | TIMEOUT | — | — | — |
| G2 insert_tail_initialized_u64_backing32_tail15_to19 | TIMEOUT | — | — | — |
| G2 insertion_stubbed_u64_backing32_len1_to16 | TIMEOUT | — | — | — |
| G2 insertion_stubbed_u64_backing32_len17_to20 | TIMEOUT | — | — | — |
| G2 swap_safety_u64_backing32_tail_comparator | SUCCESS | 39.150494 | 0/224 | 9/9 |
| G2 unstable_network_safety_u64_n32_swap_insertion_stubbed | SUCCESS, цепочка не засчитана | 146.68248 | 0/474 | 5/5 |
| G2 merge_safety_u64_len8_scratch48_src32_dst0 | SUCCESS | 80.85085 | 0/228 | 5/5 |
| G2 sort8_safety_u64_scratch48_src32_dst0_merge_stubbed | SUCCESS | 7.120541 | 0/269 | 4/4 |

| Consumer: вызовы ⊆ объединение PFC | Домен / credit |
| --- | --- |
| G1 u8 network N32 swaps s=0/16,a,b≤12 | PFC: u8, initialized backing32, F=arbitrary_less::<u8>, любой s<32,a,b<32-s, frame вне s+a/s+b. PFC+consumer SUCCESS; insertion/merge реальные, panic cut |
| G2 u64 network N32 | Swap PFC того же F=tail_less_u64 и backing32 SUCCESS; четыре tail и два insertion TIMEOUT. Вся цепочка НЕ засчитана; consumer не unconditional ordinary-кандидат |
| G2 sort8 merge N8 scratch48 src32..40→dst0..8 | PFC+consumer: те же u64/F/allocation48, только src8 initialized, прочее uninit; frame src8. Real sort4 формирует ровно этот источник; пара засчитана |
| G3 insertion/network, пока pending | Те же u64/F/initialized32, tail1..19 start0 или tail1..15 start16; insertion len1..16 starts0/16, len17..20 start0, любой offset1..len. Нужны все tail/insertion PFC; network32 дополнительно требует G2 swap и G3 merge32 |
| G3 merge, пока pending | Network: initialized src32→disjoint uninit dst32, N16 промежуточный PFC, N32 реальный consumer. General32: initialized scratch48 src0..32→initialized dst32, frame всех48; standalone PFC без general-consumer |

- swap_if_less: backing4/9/13 → добавлены backing32 u8/u64, произвольные bases/positions, F G1; также u64/F G2.
- insert_tail: u64 backing5 tail1..4 → без расширения: G1/G2 широкие части TIMEOUT.
- insertion_sort_shift_left: прежние opt-in len2/3 → без расширения; sort4_stable: прежний u64 src4/disjoint dst4 → без расширения.
- bidirectional_merge: прежние u64 N2/4 → дополнительно N8, u64/F G2, scratch48 src32/dst0, точная initialization/frame.

Кандидаты ordinary: 6 засчитанных SUCCESS-корней ≤200 с, добавка **336.343770 с**, без compile/setup; G2 network 146.68248 с отдельно conditional; ordinary пока219. Covers SUCCESS: G1 23/23, G2 23/23; 79/79 и 67/67 по полным запросам не установлены. Расход **$0.918/$4**, reserve0; repairs/retries0; G2 maxRSS4113984KiB, wall24:45.44.
G3: 10 новых корней, 4 мин/корень, 77 covers, резерв$0.945; probe-frame вместо полного сравнения, tail-часть принимается лишь ≤200с; нужен новый GO. Остались scratch48 tails1..15, прочие начала/initialization/allocations и промежуточные/нечётные merge lengths.
Нет universal T/F, uninit/validity/permissions/unwinding proof. Evidence/полные hashes: [G1](widedomains/g1/verification-report.json), [G2](widedomains/g2/verification-report.json); [G3 packet](widedomains/PREBUILD-WIDEDOMAINS-G3.md).
