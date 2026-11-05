# WIDEDOMAINS — G1, G2 подготовлен к review
G1 `f303fd59-fa90-4c25-a50d-8c7ab7146fea`, source `90fadd7ccf8b5bb32d04401d274a6f492b612897`.
Request `widedomains-g1-20261105-01`, SHA256 `cb5d05e2df44e9ff7969f319cc1f462a8a50ace3e3144b1944f68fc8ccb7a315`.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; k1-merge, standard4, diagnostic, controls=true, jobs=1.
Cloud FAILURE; COMPLETE, gate=false, Kani exit=1. 3 SUCCESS, 7 TIMEOUT; repairs/retries 0.
Каждый watchdog 180 с; у TIMEOUT время/число checks/covers не установлены.

| G1 корень widedomains:: | Статус | с | Failed/total | Covers |
| --- | --- | ---: | --- | --- |
| swap_safety_u8_backing32 | SUCCESS | 33.71013 | 0/234 | 9/9 |
| swap_safety_u64_backing32 | SUCCESS | 40.420055 | 0/234 | 9/9 |
| unstable_network_safety_u8_n32_stubbed | SUCCESS | 135.0917 | 0/387 | 5/5 |
| insert_tail_safety_u64_backing32_tail1_to4 | TIMEOUT | — | — | — |
| insert_tail_safety_u64_backing32_tail5_to8 | TIMEOUT | — | — | — |
| insert_tail_safety_u64_backing32_tail9_to12 | TIMEOUT | — | — | — |
| insert_tail_safety_u64_backing32_tail13_to16 | TIMEOUT | — | — | — |
| insert_tail_safety_u64_backing32_tail17_to19 | TIMEOUT | — | — | — |
| insert_tail_safety_u64_backing48_tail1_to4 | TIMEOUT | — | — | — |
| insert_tail_safety_u64_backing48_tail5_to8 | TIMEOUT | — | — | — |

| Consumer: вызовы ⊆ объединение PFC | Обоснование / credit |
| --- | --- |
| G1 u8 network N32: swap bases 0/16, a,b≤12, backing32, F=arbitrary_less::<u8> | PFC: любой start<32, a,b<32-start, включая a=b; тот же F, u8, allocation32, initialized, frame вне двух позиций. Полное совпадение; PFC+consumer SUCCESS |
| G1 network: insertion/merge | Реальные тела; verified stubs только swap; panic order-violation cut. Tail/merge PFC не используются |
| G2 insertion len1..16 starts0/16; len17..20 start0; offset1..len | Условно: четыре новых tail PFC, F=tail_less_u64, initialized backing32, start0/16, tail1..19 и start+tail<32. Все должны пройти; пока credit отсутствует |
| G2 u64 network N32 | Условно: новые swap PFC того же F/backing32 и insertion PFC len16/start0/16/offset13; insertion зависит от tail PFC. Пока credit отсутствует |
| G2 sort8: merge N8, scratch48 src32..40 → dst0..8 | Условно: новый merge PFC той же u64/F/allocation48/геометрии, только src8 initialized. Consumer запускает real sort4; пока credit отсутствует |

| Контракт: было → доказано после G1 |
| --- |
| swap_if_less: прежние backing4/9/13 → дополнительно backing32 u8/u64, произвольный interior base/позиции, F G1 |
| insert_tail: u64 backing5 tail1..4 → без расширения; все семь широких PFC TIMEOUT |
| insertion_sort_shift_left: прежние opt-in len2/3 → без расширения |
| sort4_stable: прежний u64 src4/disjoint dst4 → без расширения |
| bidirectional_merge: прежние u64 N2/4 → без расширения |

Кандидаты ordinary: три SUCCESS-корня G1 ≤200 с; добавка **209.221885 с**, без compile/setup; ordinary пока 219.
23/23 covers у SUCCESS; 79/79 по всему запросу не установлены. Allocation32 не переносится на scratch48.
Tooling/source/pool/request bindings PASS; targeted diagnostics — 7 timeout, без error/unused/widedomains matches.
G1 расход **$0.486 / $4**, reserve $0; max RSS 6960864 KiB; verify+compile wall 27:56.84.
G2: 10 новых корней, 3 мин/корень, резерв $0.81, ожидается 67/67; нужен новый exact-packet GO.
Остаются доказательства tail/insertion, merge8→16→32, general scratch48 tail1..15 (G1 tail1..8 также TIMEOUT), другие начала/initialization.
Uninit/validity/permissions/unwinding, универсальные T/F/allocations не доказаны; G2 не закрывает широкие TIMEOUT-домены.
Evidence: [G1 bounded report](widedomains/g1/verification-report.json), [G2 packet](widedomains/PREBUILD-WIDEDOMAINS-G2.md).
