# Приложение к SMALLSORT-CONTRACT-DOMAINS (v6)

`pfc-inventory.tsv` — ручной реестр всех конкретных `proof_for_contract` имён в `verify/**`
на Part 1 v6 `d6b8caf7fe0ef3ef5a7f21549a26de58d26ea097`
(parent `c0bd09c354a50bf9fe4dcc7cc5f9c34503658479`, library tree
`d4ec476a7a001363e58f19948c188a9c2078e370`): 38 entries — 36 ordinary и 2 controls;
`cfg(any())` элементов нет. Макросы раскрыты по именам вызовов. Полные паспорта доменов —
в [SMALLSORT-CONTRACT-DOMAINS.md](../SMALLSORT-CONTRACT-DOMAINS.md) (публичный, английский).

Имена относительны `slice::sort::shared::smallsort::verify::`, пути/строки —
`library/core/src/slice/sort/shared/smallsort/verify/` целевого коммита `d6b8caf7fe`.
В location сначала место атрибута PFC (возможно внутри macro template), затем вызов макроса.
Источники читаются через `git show d6b8caf7fe:path`; HEAD документационного worktree сохраняет
library v5 `cbe69760c8166d49acf1171c46185dfa3d58b270` и не объявляется исходниками v6.
Между v5 и v6 в library изменился только `verify/network.rs`.

Статус proofs берётся из организаторского [CI-запуска v6](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/41404150041):
Ubuntu и macOS autoharness — все 202 SmallSort harnesses SUCCESSFUL с первой попытки.
Inventory-членство proof credit не даёт. Новые сборки и CI здесь не запускаются.

Нативный ordinary inventory — [macsplit/g1.inventory-pages.txt](../macsplit/g1.inventory-pages.txt),
202 имени, exact с [ordinary-expected.txt](../macsplit/ordinary-expected.txt), build
`cbce904f-449c-4fe7-bb75-c14b1f70fbec`. Его head `71d18696613bdd6b00648a0d7b44d1cd3c6da940`
имеет тот же library tree `d4ec476a7a001363e58f19948c188a9c2078e370`, что и целевой v6 pin;
эта связь проверяется чтением Git. Cfg-on inventory v6 нативно не собирался.
Статический cfg-on set = `(native_v5_cfg_on − old2) ∪ new4`, 384 имени (382 + 2);
182 opt-in имени не изменились. Явные замены:

- `network::dispatch_safety_stable_unstable_bytes17_n32` →
  `network::dispatch_safety_stable_bytes17_n32`, `network::dispatch_safety_unstable_bytes17_n32`;
- `network::insert_tail_contract_u64_start1_tail13_to16` →
  `network::insert_tail_contract_u64_start1_tail13_to14`, `network::insert_tail_contract_u64_start1_tail15_to16`.

Для живого PFC-набора v4→v6 применяется только вторая замена. Разбиения invocation не добавляют
семантический домен или lexical PFC attribute site: сохраняются 22 domain records и 18 lexical sites.
Ordinary family counts: swap 14, sort4 2, insert_tail 5, merge 12, wrappers 3.
Домен LtU64 begin1, tail 2..16 объединяет четыре harnesses (2..8, 9..12, 13..14, 15..16).

Статическая проверка (Python stdlib и чтение Git, без сборок/CI):

```sh
python3 research/challenge-8/kani-k1/domains/check_domains.py
```

Проверяются: identity целевого PIN и inventory-head, отдельно от HEAD; отсутствие `cfg(any())`
и `correct.rs`; охват всех lexical PFC sites, target, invocation и cfg-gate каждой TSV-строки;
36 ordinary PFC имён в native ordinary 202, 2 controls в статически выведенном cfg-on 384;
полное равенство преобразованных наборов и source/cfg provenance; отсутствие 72 retired v4 имён
в исходниках и inventory; равенство живых v4 имён с v6 после явного mapping. В публичном отчёте —
≤250 строк, отсутствие внутренних терминов/кодов, 22 записи доменов, имена 36 ordinary PFC и
для каждой ссылки — коммит, совпадение текста `file:line` с URL, непустая строка, а для ссылок
на имя harness/функции — что именно это имя объявлено в указанной строке.
Семантику доменов и успешность proofs скрипт не доказывает.
