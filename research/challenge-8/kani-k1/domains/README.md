# Приложение к SMALLSORT-CONTRACT-DOMAINS (v5)

`pfc-inventory.tsv` — ручной реестр всех конкретных `proof_for_contract` имён в `verify/**`
на Part 1 v5 `5a3009b065` (library tree `cbe69760c8`): 35 ordinary и 2 controls;
`cfg(any())` элементов нет. Макросы раскрыты по именам вызовов. Полные паспорта доменов —
в [SMALLSORT-CONTRACT-DOMAINS.md](../SMALLSORT-CONTRACT-DOMAINS.md) (публичный, английский).

Имена относительны `slice::sort::shared::smallsort::verify::`, пути/строки —
`library/core/src/slice/sort/shared/smallsort/verify/` коммита `5a3009b065`.
В location сначала место атрибута PFC (возможно внутри macro template), затем вызов макроса.
Статус proofs берётся только из организаторского CI-запуска v5 (`<V5-KANI-RUN>`);
inventory-членство (cleanup G1 200 / G2 382) proof credit не даёт.

Статическая проверка (Python stdlib и чтение Git, без сборок/CI):

```sh
python3 research/challenge-8/kani-k1/domains/check_domains.py
```

Проверяются: library tree HEAD и `5a3009b065`; отсутствие `cfg(any())` и `correct.rs`; охват всех
18 лексических PFC sites, target, вызов и cfg-gate каждой строки; 35 ordinary имён в нативном
inventory G1 (200, совпадает с `cleanup/source-inventory.json`), 2 controls только в G2 (382);
отсутствие 72 retired v4 имён в исходниках и G2; совпадение живых v4 имён с v5; в публичном отчёте —
≤250 строк, отсутствие внутренних терминов/кодов, 22 записи доменов, имена 35 PFC и для каждой
ссылки — коммит, совпадение текста `file:line` с URL, непустая строка, а для ссылок на имя
harness/функции — что именно это имя объявлено в указанной строке. Семантику доменов скрипт не доказывает.
