# SCRATCHGEOM — bounded diagnostic result

Build `88af6889-68fc-48ae-9c20-9e8cfcff729d`, owner `k1-merge`; единственная разрешённая сборка.
Проверен SHA `f3a1c7c5640c4b10ed1560f751aafe6a4041facf`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Request `scratchgeom-20261104-01`, SHA256 `8d6c6e0f891f2e0a7ceacee9366114fd2eaafd126b219668d4f46cdb71996c98`.
Cloud FAILURE: компиляция успешна, summary COMPLETE, gate false, Kani exit 1; причина — TIMEOUT N17.
Diagnostic, standard4, jobs 1, timeout 10 мин/корень; controls/uninit/valid-value checks off.

| Корень `scratchgeom::` | Статус | Время, с | failed/total checks | covers |
| --- | --- | ---: | --- | --- |
| `stable_u64_min_scratch_n2` | SUCCESS | 3.8116105 | 0/411 | 2/2 |
| `stable_u64_min_scratch_n8` | SUCCESS | 240.03621 | 0/411 | 2/2 |
| `stable_u64_min_scratch_n17` | TIMEOUT | нет; лимит 600 | нет данных | нет данных |
| `stable_u64_scratch40_n8` | SUCCESS | 264.06253 | 0/411 | 2/2 |
| `stable_u64_shared_min_scratch_n8` | SUCCESS | 253.6446 | 0/441 | 2/2 |

Cfg-off inventory **207 = 202 + 5**, привязки build/head/request/Kani проверены helper; все пять новых имён присутствуют.
Inventory names SHA256 `5998a550c183293fd379bc403a471be6a07ef92f6dff5f03a3ffce7d496e94a0`; artifact SHA256 `bc2ade05f805f6dce20d0c7462f5d8542fa0f29c91053a9c6d7f2e1bf2feb846`.
Получено bounded evidence safety/полных значений: отдельный scratch N2/18, N8/24, N8/40 и общий буфер N8 + scratch24 (32 элемента).
В каждом SUCCESS достигнуты оба covers: Stable Freeze general-with-scratch и нормальный возврат после проверки значений.
Кандидат ordinary v8 по порогу <=60 с: **только `stable_u64_min_scratch_n2`**; три N8 превышают порог.
Осталось: proof N17/33 (таймаут не доказывает ошибку), ускорение N8; N32 и shared N17 не запускались.
Scope: реальные тела, произвольный читающий компаратор, cutoff panic_on_ord_violation; unwinding и проверки uninit/valid-value не установлены.
`check-tooling` PASS: pool, lane files и шесть summary hashes совпали с `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Ledger: spent **$0.8910**, reserved $0, cap $1.40; retry/repair не выполнялись. Источники: bounded k1g summary/inventory/check-tooling/budget.
