# WIDEDOMAINS — этап завершён с частичным результатом

G1 `f303fd59-fa90-4c25-a50d-8c7ab7146fea`, source `90fadd7ccf8b5bb32d04401d274a6f492b612897`.
G2 `100bfc31-d211-4e7a-be52-fc6e72ab7d69`, source `4fbe77cf46cd416fb6140a54bf6c9ffb78479d3c`.
G3 `12ded537-de07-422d-b024-35f1d3c6c22b`, source `c90719fcab98baeb2a857355effe655755a6baca`.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; k1-merge, standard4, diagnostic, controls=true, jobs1; identities/tooling PASS, runtime неизменён.
Все Cloud FAILURE, COMPLETE, gate=false, Kani exit1; watchdog G1/G2=180с, G3=240с. Скобки раскрывают все suffixes группы; полные exact-строки/hashes сохранены в отчётах.

| G / корень widedomains:: | Статус | с | Failed/total | Covers |
| --- | --- | ---: | --- | --- |
| G1 swap_safety_u8_backing32 | SUCCESS | 33.71013 | 0/234 | 9/9 |
| G1 swap_safety_u64_backing32 | SUCCESS | 40.420055 | 0/234 | 9/9 |
| G1 unstable_network_safety_u8_n32_stubbed | SUCCESS | 135.0917 | 0/387 | 5/5 |
| G1 insert_tail_safety_u64_backing32_tail{1_to4,5_to8,9_to12,13_to16,17_to19} | TIMEOUT ×5 | — | — | — |
| G1 insert_tail_safety_u64_backing48_tail{1_to4,5_to8} | TIMEOUT ×2 | — | — | — |
| G2 insert_tail_initialized_u64_backing32_tail{1_to4,5_to9,10_to14,15_to19} | TIMEOUT ×4 | — | — | — |
| G2 insertion_stubbed_u64_backing32_len{1_to16,17_to20} | TIMEOUT ×2 | — | — | — |
| G2 swap_safety_u64_backing32_tail_comparator | SUCCESS | 39.150494 | 0/224 | 9/9 |
| G2 unstable_network_safety_u64_n32_swap_insertion_stubbed | SUCCESS, credit нет | 146.68248 | 0/474 | 5/5 |
| G2 merge_safety_u64_len8_scratch48_src32_dst0 | SUCCESS | 80.85085 | 0/228 | 5/5 |
| G2 sort8_safety_u64_scratch48_src32_dst0_merge_stubbed | SUCCESS | 7.120541 | 0/269 | 4/4 |
| G3 insert_tail_probe_u64_backing32_tail{1_to4,5_to9,10_to14,15_to19} | TIMEOUT ×4 | — | — | — |
| G3 insertion_probe_u64_backing32_len{1_to16,17_to20} | TIMEOUT ×2 | — | — | — |
| G3 merge_probe_u64_len16_network_backing32 | SUCCESS | 187.27766 | 0/224 | 7/7 |
| G3 merge_probe_u64_len32_network_backing32 | TIMEOUT | — | — | — |
| G3 unstable_network_safety_u64_n32_all_helpers_stubbed | SUCCESS, credit нет | 72.3868 | 0/486 | 2/2 |
| G3 merge_probe_u64_len32_general_scratch48 | TIMEOUT | — | — | — |

| Consumer: вызовы ⊆ объединение PFC | Домен / credit |
| --- | --- |
| G1 u8 network N32: swaps s=0/16,a,b≤12 | PFC: тот же u8/F=arbitrary_less::<u8>, initialized allocation32, любой s<32,a,b<32-s, включая равные; frame вне s+a/s+b. PFC+consumer SUCCESS; insertion/merge реальные, panic cut |
| G2/G3 insertion как tail-consumer и G2 network | Нужны u64/F=tail_less_u64/initialized32, tail1..19 start0 или tail1..15 start16; insertion len1..16 starts0/16, len17..20 start0, любой offset1..len. Все части tail/insertion TIMEOUT, объединение доказанных доменов пусто: цепочка НЕ засчитана; G2 swap SUCCESS её не закрывает |
| G2 sort8: merge N8 scratch48 src32..40→dst0..8 | PFC+consumer: те же u64/F/allocation48, src8 initialized, прочее uninit, source frame; real sort4 формирует ровно источник. Пара засчитана, только первый sort8/general-N32 call site |
| G3 all-stub u64 network N32 | Swap соответствует G2 PFC; insertion len16/offset13/starts0,16 требует недоказанную tail-цепочку; merge32 требует src32→disjoint uninit dst32, но его PFC TIMEOUT. Credit нет; merge16 — другой len, general32 — другая allocation-геометрия |

- swap_if_less: backing4/9/13 → добавлены backing32 u8/u64 с произвольными interior bases/позициями, F G1; также u64/F G2.
- insert_tail: прежний u64 backing5 tail1..4 → без расширения; все 15 новых tail PFC TIMEOUT.
- insertion_sort_shift_left: прежние opt-in len2/3 → без расширения; все 4 новых insertion PFC TIMEOUT.
- sort4_stable: прежний u64 src4/disjoint dst4 → без расширения.
- bidirectional_merge: u64 N2/4 → N8 scratch48 src32/dst0 с matching sort8-consumer; N16 initialized src32-prefix16→disjoint uninit dst32, frame всех32, F G2, standalone промежуточный PFC. В network N16 merge не вызывается; N32 не доказан.

Кандидаты ordinary: [7 засчитанных корней](widedomains/ordinary-candidates.json) ≤200с, добавка **523.621430с** без compile/setup; два network-consumer conditional и исключены. Ordinary остаётся219, cfg-on283 (статика); весь модуль opt-in, CI не менялся.
30 строк: 9 SUCCESS, 21 TIMEOUT; covers у SUCCESS **55/55**, у засчитанных **48/48**; полные цели79/67/77 не установлены, TIMEOUT checks/covers/seconds неизвестны. Расход **$1.539/$4**, reserve0; builds3/3, retries/repairs0; G3 RSS5020500KiB, wall38:57.10.
Bounded-unwinding путь для insert_tail на backing32 исчерпан в рамках G1–G3. LOOPREAL проверяет loop invariant настоящего цикла/backing8/32/128 — сведения координатора, результаты не проверялись, credit не перенесён. Новых сборок не будет.
Остались tail/insertion, merge32, scratch48 tails1..15, другие начала/initialization/allocations и intermediate/odd merge lengths; нет universal T/F, uninit/validity/permissions/unwinding theorem. Evidence: [G1](widedomains/g1/verification-report.json), [G2](widedomains/g2/verification-report.json), [G3](widedomains/g3/verification-report.json), [итог](widedomains/FINAL-REPORT.json).
