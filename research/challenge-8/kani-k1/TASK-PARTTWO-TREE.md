# PARTTWO-TREE — общее opt-in дерево трёх proof-линий на Part 1 v6

Runtime: **Claude Code**, без субагентов.
Worktree `/root/verify-rust-std-kani-parttwotree`, ветка `experiment/kani-k1-parttwotree-20261102`; slug **parttwotree**. Stable owner **k1-merge**; новая стадия,
UUIDs/request_id `parttwotree-*`, старые стадии не возобновлять. Начальная база строго
`submission/ch8-smallsort-part1-v6` @ `d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097`,
library tree `d4ec476a7a001363e58f19948c188a9c2078e370`.
Cloud cap стадии **$0.70**, ровно один inventory Build, без G2/proof Builds. Project cap $88.96,
used при постановке≈$79.74; перед GO проверить актуальные ledger/reservations/slots.
Exact-packet PRE-BUILD REVIEW/GO координатора обязателен; draft сам полномочий не выдаёт.
Ожидание `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` в фоновом Bash task Claude Code;
без Codex watch/CODEX_THREAD_ID, polling-субагентов и дополнительных сессий.

## Цель и входы

Собрать research proof-модули трёх линий в одной библиотеке поверх v6, сохранив ordinary exact202/PFC36,
и проверить совместную компиляцию/членство roots одним native cfg-on inventory. Не получать новый formal proof
credit, не делать Part 2 submission и не запускать полный CI в этой стадии.

Прочитать `/root/smallsort-pr-drafts/PART2-EVIDENCE-DRAFT.md` и соответствующие bounded RESULT/source records.
Это историческая таблица разных деревьев, не evidence одного head. Зафиксировать source commits до переноса:

| Линия / добавление | Immutable report/source tip для чтения |
|---|---|
| Stable bridge, включая N9 | `8cbb26750012c51d99266fa9fbe342519345649d`; library `77cb4c97733d24c1f03f11dc803a2a7676bfc4d5` и его prerequisite bridge |
| Length wrappers, включая WONETWO | `b21be6cd8639ba779b9badea989abe3a3e4a2c91`; library `4231462d124b8c69bfaa55dd0eb956717308f1be` |
| u8 network + N10 leaves/caller | `61cfba69c3dac0b87324d2845c1164e08222d0a6`; library `2ebda13e1445186f53a12b69a4419aafe4f17e1b` |
| u64 N9 + N13 leaf/OPEN consumer | `4b9d56c46d1be97ba981610fb0dea77e0c864f66`; library `497077c6cd14fdbcc439807c0cdc186860cb00ce`; N9 provenance `9ab925b1578b9102e3009c0ec940c5c9cc0280cb` |
| N18 / MERGESTEP / direct merge4 | `e3a778017a0e057b34d6ea910fcca9d21f7dc3a3`; library `248b2725c6cd528a6d87aa5928e362dc11e74522`; preserve prerequisite histories `7d8b21728b1ccb632d67374918bd13d2c45de116`, `97a252bea7ee68720b097ecf83d014e0b87d5f20` |

Не считать последние три строки одной линейной веткой: это независимые descendants общего NETCOMP2.
Параллельный новый U64-TEN-LEAVES **не входит** в frozen inputs этой интеграции.
Если обязательный объект/identity недоступен или не совпал, записать UNKNOWN и blocker; не подменять tip.

## Перенос и допустимые изменения

Scope под `library/core/src/slice/sort/shared/smallsort/`: opt-in `verify/bridge.rs`, `verify/wrap/wone.rs`,
`verify/network/netcomp.rs` с children netten/caller, neteighteen/mergestep/directfour,
`verify/network/u64nine.rs` с child N13; необходимые точечные registrations/dependencies в
`verify.rs`, `verify/merge.rs`, `verify/network.rs`, `verify/wrap.rs`. Сначала построить точный file/symbol
allowlist по pinned diffs; это не разрешение копировать указанные parent-файлы целиком.

Не whole-merge/cherry-pick research history поверх v6 и не заменять целиком каталог verify.
Не возвращать retired `correct.rs`, старые cfg(any()) fragments или прежние unsplit ordinary имена.
Если нужный helper раньше жил в retired source, перенести только фактическую dependency в подходящий scope,
с явным symbol/source mapping. Не восстанавливать все старые harnesses вслед за helper.
Регистрации только `#[cfg(kani_smallsort_controls)]`; сохранившиеся ordinary источники/макросы/домены v6 не менять.
Нужные именования/imports/расположение разрешено адаптировать с mapping; targets/contracts/real bodies,
ghost contexts, probes, adapters, assertions, required covers и annotations семантически сохранить.
Не создавать общий u8/u64 framework и не объединять отдельные context statics.

Runtime `shared/smallsort.rs`, generic signatures/CFG, std вне proof-модулей, workflows/tooling/runner/pin/flags
не менять. Не переносить старые workflows/requests как новые активные. Ни старые 200, ни простое сложение
branch counts не являются инвентарём интегрированного дерева. Target definitions должны предшествовать PFC.

## Статические deliverables до Build

В новом `research/challenge-8/kani-k1/parttwotree/` подготовить:

1. Source map: каждый перенесённый target/root/helper, old commit/path/symbol → new path/symbol;
   library/source/tree hashes; отдельный список необходимых parent edits и их причин.
2. Exact expected roots manifest, ordinary/opt-in/PFC/plain, annotations/target/typed instance и cfg provenance.
   Expected cfg-on = union перенесённых sources на v6 с удалением дубликатов; вывести набор имён и hash,
   не задавать count заранее. Ordinary set equality с native MACSPLIT G1 exact202; PFC36, insert_tail5;
   сохранить v6 split names и отсутствие retired roots. `pfc_order.py` отдельно от проверки cfg/ordinary:
   его lexical heuristic не считать источником inherited cfg membership.
3. Будущую proof-матрицу: accepted positive/leaf pairs с exact domains/dependencies; expected-negative rows
   с literals/covers; OPEN/timeout/diagnostic rows отдельно. Не включать ожидаемые failures/timeouts в
   «все rows SUCCESS» gate. Не запускать эту матрицу в текущей стадии.
4. Локальную копию `PART2-EVIDENCE-DRAFT.md`: N22c обновить по RESULT-NETTEN-CALLER @61cfba69c3,
   включая controls 1/1,1/1,2/2, shared probe, asserted prefix premise и driver14.10GiB.
   Leaf reuse из f6fdbf06 оставить historical cross-Build, 469.628505s только mixed-run estimate.
   Сохранить U64-N13 PARTIAL, MERGESTEP gate FAIL и другие historical статусы/ограничения.
   После добавления записей пересчитать totals. Общий `/root/smallsort-pr-drafts` пока не перезаписывать.

Native ordinary reference: branch `experiment/kani-k1-macsplit-20261102`, report head
`71d18696613bdd6b00648a0d7b44d1cd3c6da940`, `macsplit/ordinary-expected.txt` / inventory pages;
проверить его library identity с v6. Ordinary v6 202/PFC36 не выдавать за новый native cfg-off inventory.
Static rustfmt/whitespace/source/name-set checks допустимы; локальных cargo/rustc/Kani/proofs нет.

## Единственный G1 — inventory, не measurement

Использовать существующий K-1 inventory request/preflight: kind inventory, controls:true, inventory:true,
harnesses:[], harness_timeout_minutes:20, standard4 4CPU/16GiB/swap off; те же frozen tooling
`30f77e8599`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12.
Inventory schema отличается от measurement: не добавлять jobs/uninit поля из measurement шаблона.
Существующий validator должен принять exact packet без изменения runner/schema; несоответствие — blocker,
не повод править infrastructure в этой стадии.

Резерв `(20+30)×$0.0135 = $0.675`, cap $0.70. Project≤2 queued/running/unresolved Builds,
≤1 на stable owner; параллельный u64 leaf имеет другого owner и отдельный ledger.
До GO: source map/diff/dependencies, annotation/cfg/domain matrix, expected names, pfc_order,
runtime/v6-preservation check, request/source/library/tree/pin/tooling identities и бюджет/slots.
Library/research commits отдельно, `[skip ci]`, publish reviewed packet без force.

Gate: exact identities; native cfg-on inventory compile SUCCESS; полученный полный набор имён равен
expected manifest без missing/extra; ordinary membership/provenance и v6 source preservation отдельно проверены.
Результат — **INTEGRATED + INVENTORY PASS, PROOF NOT RUN**. Ни SUCCESS inventory, ни source equivalence
не превращают исторические leaf/consumer results в formal credit нового дерева.
Compile error/OOM/timeout/name mismatch/UNKNOWN → bounded facts и остановка. Нет G2, proof retries,
highmem fallback, Actions dispatch или автоматического следующего этапа.

## Итог и общие границы

`RESULT-PARTTWO-TREE.md` ≤30 строк: reviewed/build/request/library/tree identities, expected/native counts
и set comparison, ordinary202 source check, compiler/driver/process-sum peaks, spent/reserved,
точные unresolved issues и готовая будущая proof-матрица. Передать координатору copy evidence draft.
Обычный v6 CI остаётся историей v6; новый exact-tree proof CI ещё требуется, full matrix здесь NOT_RUN.
K-1 reporting — bounded summaries/inventory pages/peaks/разрешённые targeted excerpts; Evidence Brief/Select-Merge
не относятся. Raw archives/full logs/Cloud Logging/credentials/hidden configs и competing code не читать;
исторические ledgers/results не переписывать. Нет PR/upstream/deploy/full CI.
Маркеры `REVIEW REQUEST <sha>` / `PARTTWO-TREE ЗАВЕРШЁН`; одна стадия, затем стоп.
