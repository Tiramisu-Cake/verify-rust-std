# Приложение к DOMAINS-v4

`pfc-inventory.tsv` — ручной реестр всех конкретных `proof_for_contract` имён,
найденных в `verify/**` на `f0ba14f97b3adea21c1c9671db6245afe7a15887`:
35 ordinary, 2 controls, 72 отключённых `cfg(any())`. Макросы раскрыты по именам
вызовов, в том числе многострочные. Полные паспорта исполненных доменов находятся
в [DOMAINS-v4.md](../DOMAINS-v4.md).

Имена относительны `slice::sort::shared::smallsort::verify::`, пути/строки —
`library/core/src/slice/sort/shared/smallsort/verify/` указанного коммита.
В location сначала указано место атрибута PFC (иногда внутри macro template),
затем конкретного вызова макроса/объявления. Для inactive строк домен описывает
оставшийся fixture или старые macro args, а не исполнимый новый Profile.
Часть отключённых вызовов имеет устаревшие сигнатуры. `legacy target` отделён
от нынешнего текста macro target. Никакого proof credit этим строкам не дано.

SUCCESS взят из предоставленного результата exact v4 run `41314097764` на двух
ОС и сопоставления с именами архива; самостоятельно в этой сессии не воспроизведён.
NOT_RUN означает отсутствие исполнения в этом ordinary v4 run. Исторические
результаты других деревьев/контрактов не импортируются.

Статическая проверка (Python stdlib и чтение Git, без сборок/CI):

```sh
python3 research/challenge-8/kani-k1/domains/check_domains.py \
  /root/ch8_changes_since_audit_2026-11-01.zip
```

Проверяются совпадение library tree, уникальность 109 имён, охват всех 37
лексических PFC sites, target/locations, 35 ordinary имён в архиве из 200,
отсутствие там controls/inactive, сверка 72 retired имён с историческим списком,
наличие 22 записей доменов и валидных строк source links в отчёте. Скрипт не
доказывает семантические утверждения и не устанавливает статус Kani по inventory.
