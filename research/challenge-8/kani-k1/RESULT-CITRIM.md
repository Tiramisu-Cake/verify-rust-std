# CITRIM — подготовлено к PRE-BUILD REVIEW; сборки не запускались
Base `4fa6151b6a`; library `d866f287bb844b788ea853d0bb2fe829ddbf7292`; owner k1-merge.
Request `citrim-g1-20261105-01`; diagnostic, standard4, jobs1, controls=false, 5 мин/часть.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; tooling base `59893bff1f` без изменений.
Время каждой новой части и суммы после: **не измерены**; G1 ждёт exact-packet GO.
До: источник TASK-CITRIM.md, Actions Ubuntu/macOS; это не исходный GCB замер.

| Исходный verify:: корень | Части | До Ubuntu/macOS, с | После, с | Исходный домен = ∪ частей |
| --- | --- | ---: | --- | --- |
| merge::general_direct_u64_n9 | _lt_lt/_lt_ge/_ge_lt/_ge_ge | 374.0/211.6 | pending | four (v0<v1,v2<v3) truth pairs |
| merge::stable_direct_u64_n9 | _lt_lt/_lt_ge/_ge_lt/_ge_ge | 237.5/172.5 | pending | same four truth pairs |
| network::dispatch_safety_stable_unstable_bytes16_n15_16_17 | N15/N16/N17 | 154.3/218.1 | pending | {15,16,17} × both routes |
| network::dispatch_safety_stable_unstable_bytes16_n32 | stable/unstable N32 | 160.1/306.1 | pending | N32 × both routes |
| network::dispatch_safety_stable_unstable_bytes17_n15_16_17 | N15/N16/N17 | 147.7/265.5 | pending | {15,16,17} × both routes |
| network::insert_tail_contract_u64_start1_tail2_to8 | tail2..5 / 6..8 | 185.1/281.5 | pending | [2,8]=[2,5]∪[6,8] |
| network::insert_tail_contract_u64_start1_tail9_to12 | tail9..10 / 11..12 | 174.6/227.8 | pending | [9,12]=[9,10]∪[11,12] |
| network::insert_tail_contract_u64_start1_tail13_to14 | tail13 / 14 | 161.7/207.4 | pending | {13,14}={13}∪{14} |
| network::network_safety_unstable_u64_n30_to32 | N30/N31/N32 | 209.5/235.5 | pending | {30,31,32}={30}∪{31}∪{32} |

Все типы, полные входы/пробы, компараторы, assertions, stubs и contract requires сохранены.
Равенство объединений: check_citrim.py + check-report.json; >= включает равные элементы.
Селекторы перечислены без пропусков/пересечений; исходные shared items и макросы идентичны.
Общие covers дублируются; каждый исходный length/tail/route cover сохранён в своей части.
Ожидается 64/64 covers; фактическая достижимость ещё не проверена.
Merge: cadical вместо default SAT solver, смысл неизменен; unwind прежний во всех частях.
Ordinary **235 = 219 - 9 + 25 (+16)**; 210 сохранённых roots и 34 opt-in идентичны.
Это source inventory; итоговый compiler inventory обязателен в G2 после отдельного GO.
Исходная сумма девяти Actions roots: **1804.5/2126.0 с**; итоговая GCB сумма неизвестна.
Общее время 235 roots неизвестно; остальные 210 в CITRIM не перепроверяются.
Пар GCB/Actions для этих исходных roots в доступных наших отчётах нет; коэффициент не измерен.
Эвристика задания 2×: 120 с GCB ≈240 с Actions; гарантии <=200 с Actions нет.
Статика, rustfmt, diff-check, request validator: PASS; локальные proof tools не запускались.
Builds 0/2, repairs 0, расход $0/$3; резерв предлагаемого G1 $2.0925 (155 мин).
Проект: used $102.1920, reserved $0; с G1 max $104.2845 <=$118.96; перепроверить при GO.
Не установлено: времена <=120 с, SUCCESS/покрытие частей, итоговый compiler inventory.
Пакет: [PREBUILD](citrim/PREBUILD-CITRIM.md), [статика](citrim/check-report.json), [ledger](citrim/RUN-LEDGER.json).
