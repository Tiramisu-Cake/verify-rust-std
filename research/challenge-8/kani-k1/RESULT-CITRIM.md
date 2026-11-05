# CITRIM — G1 разобрана; G2 подготовлена, не запускалась
G1 `76b1664d-a0bf-4268-92fc-3b69220d556f`, source `bc4b5c7ec7b41a317548c21bc8dabeebfb062e5a`.
Cloud FAILURE; COMPLETE, gate false, Kani exit1; 18 SUCCESS +7 TIMEOUT, не compile/setup error.
Pin `cd355b0bccd32300713bc2ce4f765dafa1510607`; tooling `59893bff1f` и standard4/SHA bindings PASS.
G1 diagnostic, jobs1, controls=false, inventory=false, 25×5 мин; source base `4fa6151b6a`.
G2 library `26d5083990bf5c5996376a061aa4a06389aa4568`; request `citrim-g2-20261105-01` ждёт GO.
До — TASK Actions Ubuntu/macOS, не GCB; после G1 — времена частей слева направо и их сумма.

| Исходный verify:: корень | До U/M, с | Части G1: время каждой; Σ, с | Исходный домен = ∪ финальных частей |
| --- | ---: | --- | --- |
| merge::general_direct_u64_n9 | 374.0/211.6 | G1: 3 TIMEOUT; lt_lt 298.004330; G2: 4 new parts pending | all four runtime c1/c2 truth pairs |
| merge::stable_direct_u64_n9 | 237.5/172.5 | G1: 4 TIMEOUT; G2: 4 new parts pending | same four truth pairs |
| network::dispatch_safety_stable_unstable_bytes16_n15_16_17 | 154.3/218.1 | 57.527676 / 63.919994 / 64.92339; Σ186.371060 | {15,16,17} × both routes |
| network::dispatch_safety_stable_unstable_bytes16_n32 | 160.1/306.1 | 108.72484 / 126.870476; Σ235.595316 | N32 × {stable,unstable} |
| network::dispatch_safety_stable_unstable_bytes17_n15_16_17 | 147.7/265.5 | 62.401028 / 70.84245 / 95.44369; Σ228.687168 | {15,16,17} × both routes |
| network::insert_tail_contract_u64_start1_tail2_to8 | 185.1/281.5 | 210.27011 / 229.83519; Σ440.10530 | [2,8]=[2,5]∪[6,8] |
| network::insert_tail_contract_u64_start1_tail9_to12 | 174.6/227.8 | 193.22226 / 199.78485; Σ393.00711 | [9,12]=[9,10]∪[11,12] |
| network::insert_tail_contract_u64_start1_tail13_to14 | 161.7/207.4 | 231.39142 / 237.20578; Σ468.59720 | {13,14}={13}∪{14} |
| network::network_safety_unstable_u64_n30_to32 | 209.5/235.5 | 112.93425 / 116.823906 / 117.06356; Σ346.821716 | {30,31,32}={30}∪{31}∪{32} |

Равенство доменов: check_citrim.py + check-report.json; все входы/пробы/T/компараторы сохранены.
G2 merge: c1=lt_u64(v1,v0), c2=lt_u64(v5,v4), false включает равные ключи; все 4 пары.
Все assertions/requires/stubs/covers сохранены; helpers после удаления split-assumes идентичны.
G1: 57/57 covers у 18 завершённых частей; 7 covers таймаутов неизвестны; 10/25 частей <=120 с.
G2: 15 проблемных частей, Kissat; unwind merge10/tail18/bytes16N32 33; assertions unwinding включены.
Цель G2 35/35 covers +29/29 от 10 неизменённых G1 частей =64/64; пока не установлена.
Ordinary **235=219-9+25 (+16)**; 210 исходных retained и 34 opt-in token-identical, tooling/runtime прежние.
Inventory compiler не запрашивался; G2 inventory=false, итоговый exact inventory передан координатору.
Full kani-list ~49 мин не помещается в 30 мин overhead при полных таймаутах; padding/tooling changes нет.
Сумма завершённых G1 **2597.189200 с**; полная сумма неизвестна из-за 7 TIMEOUT. До Actions Σ1804.5/2126.0 с.
Общее время 235 roots неизвестно; остальные 210 в CITRIM не перепроверяются.
Пар исходных GCB/Actions нет; коэффициент не измерен. Эвристика 2×: 120 с GCB≈240 с Actions, без гарантии200.
G1 runner wall 1:20:29, Cloud ~87мин; max RSS2993108 KiB, no OOM; scoped warning scan no match.
Статика/rustfmt/request/diff-check PASS; evidence consistency PASS, task acceptance пока FAIL.
Расход G1 **$1.1880**, остаток **$1.8120**; G2 резерв **$1.4175**, spent+reserve **$2.6055/$3**.
Builds1/2, repairs0; G2 max105мин должен закончиться до16:00Z, closeout16:30Z; окно не сброшено.
Не удалось G1: все merge N9, все 6 tail-частей и unstable bytes16N32 не достигли <=120 с.
Если семейство не удастся ускорить в G2 — исходный корень сохранить/восстановить и отметить blocker.
Пакет [G2](citrim/PREBUILD-CITRIM-G2.md); [G1 bounded evidence](citrim/g1-evidence/verification-report.json).
