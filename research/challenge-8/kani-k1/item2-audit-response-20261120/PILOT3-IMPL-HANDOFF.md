# Кампания 3 q-пилота — handoff реализации

Локальный кандидат для одиночного P-2 подготовлен. Статус `RESEARCH_ONLY`, `go=NOT_GRANTED`, `proof_credit=NONE`. [Задание](PILOT3-IMPL-TASK.md) · [Анализ кампании 2](PILOT-RUN2-ANALYSIS.md)

## Идентичности

Control worktree — `/root/kani-ch8-q-pilot-control-v1`, локальная ветка — `experiment/ch8-q-pilot-control-v3`. Кандидат кампании 2 `301bd6465ae8f4aaec2d40baa19eb3c8624a5912` сохранён на `experiment/ch8-q-pilot-control-v1`.

| Объект | Commit | Tree |
| --- | --- | --- |
| Control | `b716a7f821840292d7671ff71cd99099c333112a` | `df067af92f84d718fa18e77ee117adff2097e9d3` |
| std | `0e9b28b293f4360b005d33583d2cf9ac06d1790b` | `2d13d786186a96e3eeb55ff9969f63388eeee042` |
| Tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent control — `ba32286ee4f370593a2c9f0d8834a12d473c82d7`.

| Файл из control | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `f68c0b54fd0d3ba51ff071af03e26018e4926bab8ca61df202d6f3d2407c850c` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |

## Дельта к кампании 2

- Изменены только `run.py`, `CI-REQUEST.json` и `test_run.py` в `ch8-q-pilot-control/`. Frozen roster содержит один `slice::sort::shared::smallsort::verify::sorting_q_pilot::p2_sort13_u8_b01_len17_q_any` с `normal` cfg. Сохранены exact argv, unwind 36, child timeout 600 с, source/tool pins, контрольные определения в std и `refs/heads/uninit-ci/ch8-q-pilot-v1`. В запросе пересчитаны хэши `run.py` и `test_run.py`.
- Номинальный local RSS cap — 9 GiB (`9437184` KiB). Внешний предел — 12 GiB, резерв — 2 GiB. Runner сохраняет `A=min(MemAvailable, cgroup headroom)` при наличии замера cgroup, `group_cap=min(12 GiB, A−2 GiB)` и `effective=min(local, group_cap)`.
- В `q-pilot-raw.json` номинал записывается в `limits.local_rss_kib` и в `roots[].child.nominal_rss_cap_kib` при наличии записи child. `roots[].child.rss_cap_kib` показывает эффективный предел, переданный в `execute`. `roots[].supervisor.rss_cap_kib` показывает внешний предел по замеру supervisor. Вложенный `memory_budget.per_root_cap_kib` относится к общему stock runner, лимит P-2 берётся из полей child.
- Workflow побайтно совпадает с кампанией 2. Надпись шага `Run seven q-pilot roots` осталась исторической. Аргументы шага передают управление frozen `run.py`, который использует только P-2.

## Локальные проверки

- `python3 ch8-q-pilot-control/run.py validate` с синтетическими GitHub metadata. `Tiramisu-Cake/kani`, `push`, frozen ref, attempt `1`, run ID `synthetic`, `GITHUB_SHA` равен кандидату. Код 0, проверены commit, tree, parent и хэши payload.
- `python3 ch8-q-pilot-control/run.py check-source --std /root/verify-rust-std-ch8-q-pilot-v1 --tool /root/kani-upstream-ch8-s1`. Код 0, проверены чистота checkout, оба commit/tree и хэши шести файлов std.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_run.py` из `ch8-q-pilot-control/`. **12/12**. Проверены точный singleton, отказ при неверных root, cfg и cap, запись 9 GiB при полной доступной памяти и фактический `rss_cap` cutoff с эффективными 1024 KiB при номинальных 9 GiB. Сценарий cutoff подтвердил reap и удаление temp. Прежние сценарии последовательности, bounded collection, fallback и очистки прошли на синтетическом roster из семи корней.
- `git diff --check`, точный состав дельты к `301bd6465` и метаданные control-коммита проверены. Автор и коммитер — `Tiramisu-Cake <igkharin@gmail.com>`, в сообщении `[skip ci]`.

Cargo, rustc, Kani, CBMC и CI не запускались. Публикаций и пушей не было. Вердикт P-2 и профиль потребления памяти в кампании 3 остаются открытыми.
