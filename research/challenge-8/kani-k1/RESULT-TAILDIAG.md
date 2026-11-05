# TAILDIAG — G1: tail1..15 доказан; G2 ожидает review/GO
G1 `34500433-bd3d-4784-9a26-aaf0ba3f0492`: Cloud FAILURE, summary COMPLETE, gate=false, Kani exit1.
Source `1c99acce330d708961571bd593ecc322768f690f`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Request `taildiag-g1-20261105-01`, SHA256 `ccc22fb30ac75edd682dee2aca2b175fcdc977c23c017a85802d8f0ff3037296`.
k1-network, standard4, controls=true, inventory=false, jobs1, 240 с/root; source/request/pool/tooling PASS.

| Root taildiag:: / фактор | Status | с | CBMC peak RSS KiB |
| --- | --- | ---: | ---: |
| u64_backing8_tail1_to7 | SUCCESS | 60.678856 | 2626720 |
| u64_backing12_tail1_to7 | SUCCESS | 104.20101 | 2773596 |
| u64_backing17_tail1_to7 | SUCCESS | 182.69366 | 3191176 |
| u64_backing17_tail1_to7_value_order | TIMEOUT | — | 3700652 |
| u64_backing17_tail1_to7_cadical | SUCCESS | 174.3746 | 3192512 |
| u64_backing17_tail1_to7_kissat | SUCCESS | 142.5729 | 3595144 |
| u8_backing17_tail1_to7 | SUCCESS | 38.121933 | 2294760 |
| u64_backing17_tail1_to7_no_explicit_frame | SUCCESS | 31.25227 | 2300584 |
| u64_backing17_tail8_to15 | SUCCESS | 177.43237 | 3192020 |
| u64_backing17_tail8_to15_value_order | SUCCESS | 163.57158 | 3708104 |

Все SUCCESS: checks 0/229, covers 5/5; суммарно 45/45 успешных covers, полная цель50 не установлена.
TIMEOUT: время/checks/covers неизвестны; 240 с — watchdog, не verification time. Peak — direct metadata attribution.
Контролируемые пары tail1..7: backing8/12/17 = 60.679/104.201/182.694 с; u8 на17 =38.122 с.
Самый сильный измеренный фактор — явная suffix-рамка:182.694→31.252 с (~5.85×), реальный modifies сохранён.
Гипотеза: рамка и ширина символических значений/аллокации дают основную стоимость; backing32 не перепроверен.
Kissat142.573 с, explicit cadical174.375 с; default effective solver не установлен bounded invocation-выводом.
Детерминированный порядок не улучшает надёжно:tail1..7 TIMEOUT, tail8..15 SUCCESS163.572 с; sortedness не предполагается.
Новый matched PFC-домен:u64, initialized allocation17, start0, F=taildiag::arbitrary_less::<u64>, tail1..15.
Дополнительно:u64 allocations8/12 tail1..7; u8 allocation17 tail1..7; value_less_u64 allocation17 tail8..15.
Все9 SUCCESS — кандидаты ordinary ≤200 с; consumer insertion ещё не запускался, credit ему не засчитан.
G2 предложена:tail8..15 без явной рамки и четыре matched insertion-PFC со stub_verified(insert_tail), len1..16.
Consumer сохраняет allocation17/start0/u64/F; callback-cover hook пустой только у consumer, F сохранён.
G1 verify wall23:21.87, max RSS3708104KiB; swap off, OOM none_seen. Runtime/workflows/tooling неизменны.
Расход$0.4185/$2, reserve0; repairs/retries0. Ordinary219/cfg-on263 — статика, полный lane inventory отключён.
В summary build outcome=success, Cloud metadata=FAILURE; расхождение сохранено, не заменяет gate.
Нет universal T/F, других allocations/starts, sortedness, uninit/validity/permissions/panic-unwinding theorem.
Evidence:[G1 report](taildiag/g1/verification-report.json), bounded summary/rows/peaks/tooling рядом.
