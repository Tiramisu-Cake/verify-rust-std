# TAILDIAG — tail1..15 доказан; insertion len1..16 не засчитан
G1 `34500433-bd3d-4784-9a26-aaf0ba3f0492`, source `1c99acce330d708961571bd593ecc322768f690f`.
G2 `a5a16595-8c2e-4bf8-80bd-b7627d775ca6`, source `49420dda0b505d38d9bed8568ce602a4026b4ae4`.
Request G1 `taildiag-g1-20261105-01`, SHA256 `ccc22fb30ac75edd682dee2aca2b175fcdc977c23c017a85802d8f0ff3037296`.
Request G2 `taildiag-g2-20261105-01`, SHA256 `c7652b3bf9c2b8abc8896b894c80c228b619a3087917d55131cdcf19d261fdf7`.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; k1-network, standard4, controls=true, inventory=false, jobs1, 4 мин/root.
Оба Cloud FAILURE, summary COMPLETE, gate=false, Kani exit1; source/request/pool/check-tooling PASS.

| G / root taildiag:: (фактор указан в имени) | Status | с | CBMC peak RSS KiB |
| --- | --- | ---: | ---: |
| G1 u64_backing8_tail1_to7 | SUCCESS | 60.678856 | 2626720 |
| G1 u64_backing12_tail1_to7 | SUCCESS | 104.20101 | 2773596 |
| G1 u64_backing17_tail1_to7 | SUCCESS | 182.69366 | 3191176 |
| G1 u64_backing17_tail1_to7_value_order | TIMEOUT | — | 3700652 |
| G1 u64_backing17_tail1_to7_cadical | SUCCESS | 174.3746 | 3192512 |
| G1 u64_backing17_tail1_to7_kissat | SUCCESS | 142.5729 | 3595144 |
| G1 u8_backing17_tail1_to7 | SUCCESS | 38.121933 | 2294760 |
| G1 u64_backing17_tail1_to7_no_explicit_frame | SUCCESS | 31.25227 | 2300584 |
| G1 u64_backing17_tail8_to15 | SUCCESS | 177.43237 | 3192020 |
| G1 u64_backing17_tail8_to15_value_order | SUCCESS | 163.57158 | 3708104 |
| G2 u64_backing17_tail8_to15_no_explicit_frame | SUCCESS | 64.20818 | 2524920 |
| G2 insertion_stubbed_u64_backing17_len1_to4 | TIMEOUT | — | 1478284 |
| G2 insertion_stubbed_u64_backing17_len5_to8 | TIMEOUT | — | 1440396 |
| G2 insertion_stubbed_u64_backing17_len9_to12 | TIMEOUT | — | 1427408 |
| G2 insertion_stubbed_u64_backing17_len13_to16 | TIMEOUT | — | 1453880 |

10 SUCCESS: каждый checks 0/229 и covers 5/5; всего 50/50 успешных covers. Полная цель 75 covers не установлена.
5 TIMEOUT: время/checks/covers неизвестны; 240 с — watchdog. Все15 CBMC peaks имеют direct metadata attribution; OOM none_seen.
Главный измеренный фактор — явная suffix-рамка: tail1..7 182.694→31.252 с (~5.85×); tail8..15 177.432→64.208 с (~2.76×).
Реальный modifies сохранён. Гипотеза: рамка и ширина значений/аллокации дают основную стоимость; шум не изолирован, backing32 не перепроверен.
Итоговый insert_tail: u64, initialized allocation17, start0, F=taildiag::arbitrary_less::<u64>, tail1..15; без sortedness premise.
Все четыре matched insertion-consumers len1..4/5..8/9..12/13..16 TIMEOUT: новых insertion-доменов и credit len1..16 нет.
Ordinary: рекомендуются два no_explicit_frame PFC tail1..7 и tail8..15, 31.25227+64.20818=95.46045 с без setup; каждый ≤200 с.
Все10 SUCCESS — bounded кандидаты, список/два приоритетных: [ordinary-candidates.json](taildiag/ordinary-candidates.json); consumers исключены.
Ordinary219/cfg-on268 — статика; все15 новых корней opt-in. Runtime/workflows/tooling неизменны; source checks/rustfmt/diff-check PASS.
G1/G2 verify wall 23:21.87/19:23.62; max RSS3708104/2524920KiB; swap off. Расход $0.4185+$0.3510=$0.7695/$2, reserve0.
Две сборки, retries/repairs0; лимит primary исчерпан. Причина стоимости consumer не установлена; новых сборок не будет.
В обоих summary build outcome=success, Cloud metadata=FAILURE; расхождение сохранено. Effective default solver bounded-выводом не установлен.
Нет universal T/F, других allocations/starts, sortedness, uninit/validity/permissions/panic-unwinding theorem.
Evidence: [G1](taildiag/g1/verification-report.json), [G2](taildiag/g2/verification-report.json); bounded summary/rows/peaks/tooling рядом.
