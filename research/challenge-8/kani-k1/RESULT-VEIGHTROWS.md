# VEIGHTROWS — PASS

Build `aa74ed5a-e1b3-4851-bf9f-094435daf711`; source `01caba2d4d7386759de16ee395518aa866cafbb4` (exact-packet GO); library `d3982a624072437d603f0f96ba974bb00ac5eb5b`, дерево побайтно совпадает.
Request `veightrows-g1-20261105-01`, SHA256 `e80d8942192e78db648f9e9c8c9471d84783ac6c8891f6be17d8bb40615e62db`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
k1-merge, diagnostic, standard4, jobs1, inventory=false, controls=false, 4 мин/корень; Cloud SUCCESS, COMPLETE, gate=true, Kani exit0; source/request/pool/check-tooling PASS.

| Корень относительно `verify::` | Status | с | Covers |
| --- | --- | ---: | --- |
| `allocationcontracts::swap_safety_u8_backing32` | SUCCESS | 31.575 | 9/9 |
| `allocationcontracts::swap_safety_u64_backing32` | SUCCESS | 35.80377 | 9/9 |
| `allocationcontracts::unstable_network_safety_u8_n32_stubbed` | SUCCESS | 104.319084 | 5/5 |
| `tailcontracts::insert_tail_safety_u64_backing17_tail1_to7` | SUCCESS | 29.476984 | 5/5 |
| `tailcontracts::insert_tail_safety_u64_backing17_tail8_to15` | SUCCESS | 61.14256 | 5/5 |

Пять корней: **262.317398 с**, failed checks 0/1213, covers **33/33**, unreachable covers 0; 28 unreachable non-cover checks не смешиваются с covers.
VEIGHTMAX `daf1045c-5454-4662-93a7-df16cfd23e00`, source `7df3f7d3d68c458185c2f42f72483c13fbe9c161`, то же дерево library: merge8 SUCCESS 86.45552 с, 5/5; sort8 SUCCESS 8.113433 с, 4/4.
Все семь перенесённых корней: **7 SUCCESS, 356.886351 с, 42/42 covers**; сумма verification time без setup/компиляции. Общий исторический FAIL VEIGHTMAX не переписан.
Inventory не запускался; прежний exact 233-name PASS сохранён как evidence на идентичной library. Прежние 226 корней не перепроверялись; новых универсальных T/F/unwinding claims нет.
Verify стартовал через 348 с после validate с бюджетом 2292 с; runner wall с компиляцией 5:34.26. Расход **$0.1755/$1.00**, reserve0; builds1/1, retries0, repairs0.
Bounded evidence: [summary](veightrows/evidence/summary.md), [report](veightrows/evidence/verification-report.json), [ledger](veightrows/RUN-LEDGER.json); warnings сохранены ограниченной выборкой.
