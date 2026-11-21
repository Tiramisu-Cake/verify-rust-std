# Кампания 4 q-пилота — handoff реализации

Локальный кандидат для P‑2b готов. Режим `RESEARCH_ONLY`, request `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. [Задание](PILOT4-IMPL-TASK.md) · [Сводка кампании 3](run-44844623193/SUMMARY.md)

## Идентичности

| Объект | Worktree и ветка | Commit | Tree |
| --- | --- | --- | --- |
| std | `/root/verify-rust-std-ch8-q-pilot-v1`, `experiment/ch8-q-pilot-v1` | `c59b0d2a21c84bcf9786cd2b4c4c152be23588ae` | `ebbcb987e6b312d63a2b412a6faff44b8c10ff2c` |
| Control | `/root/kani-ch8-q-pilot-control-v1`, `experiment/ch8-q-pilot-control-v4` | `9fb54361f51eda0609821b83d30411c2747b789f` | `d2764e8037e8217a165c7e18650a666965d414f4` |
| Tool | `/root/kani-upstream-ch8-s1`, detached HEAD | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

Единственный parent std — `0e9b28b293f4360b005d33583d2cf9ac06d1790b`. Control v4 создан на основе v3 `b716a7f821840292d7671ff71cd99099c333112a` с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Локальная ветка v3 по-прежнему указывает на `b716a7f821840292d7671ff71cd99099c333112a`.

| Файл | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `906ce1a2c5b9d3bd1bb27fb46bc4bfdb526d9350df85f11497dc615a13d8093b` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |
| `ch8-q-pilot-control/run.py` | `fd3fb93beb99246388a9e0e625b4161a4295f62bd7cd75d6bdf3fa4c887ce334` |
| `ch8-q-pilot-control/test_run.py` | `39ff41f1426acc7f3d24744bdc9873b3d921be3cc17839aef80bd0c676f9f42f` |
| `library/core/src/slice/sort/shared/smallsort/verify/sorting_q_pilot.rs` | `606ca66feb1ad2643d5159f859657b29696543a2e16953e526cb1b6dd4d36aa3` |

## Дельта к кампании 3

- В std изменён только `sorting_q_pilot.rs`. Добавлен P‑2b с `#[kani::proof_for_contract(sort13_optimal)]` и `#[kani::unwind(36)]`, без `stub_verified`. Он повторяет fixture, домен, assertions, covers и метки P‑2. Побайтовая сверка подтвердила, что после удаления блока P‑2b весь файл совпадает с базой.
- В `run.py` и request задан единственный корень P‑2b с селектором `slice::sort::shared::smallsort::verify::sorting_q_pilot::p2b_sort13_u8_b01_len17_q_any_actual_swaps`. Сохранены `normal` cfg, точный `argv`, unwind 36, child timeout 600 с и `refs/heads/uninit-ci/ch8-q-pilot-v1`. Request связывает новые std commit/tree и SHA-256 `sorting_q_pilot.rs`.
- Номинальный local RSS cap равен 6 GiB (`6291456` KiB), внешний cap — 12 GiB, резерв — 2 GiB. Эффективный child cap по-прежнему вычисляется как `min(local, group_cap)`. Workflow совпадает побайтно с кампанией 3.

## Локальные проверки

- `run.py validate` с синтетическими GitHub metadata (`Tiramisu-Cake/kani`, `push`, frozen ref, attempt `1`, run ID `synthetic`, `GITHUB_SHA` равен control-кандидату). Код 0, проверены control commit, tree, parent и хэши payload.
- `run.py check-source --std /root/verify-rust-std-ch8-q-pilot-v1 --tool /root/kani-upstream-ch8-s1`. Код 0, проверены чистота checkout, оба commit/tree и все шесть SHA-256 файлов std.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_run.py` из `ch8-q-pilot-control/`. Прошли 12 из 12 тестов. Проверены singleton P‑2b, отказ при дрейфе roster, cfg, argv и cap, запись номинальных и эффективных 6 GiB при достаточной памяти, срабатывание меньшего эффективного cap в синтетическом child и очистка ресурсов.
- `rustfmt --check` из `nightly-2026-11-19` с `--edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features`. Проверка блока P‑2b через stdin завершилась с кодом 0. Проверка файла целиком завершилась с кодом 1 и вывела те же семь фрагментов форматирования, что и для базовой версии.
- `git diff --check` прошёл для std и control. Автор и коммитер — `Tiramisu-Cake <igkharin@gmail.com>`. Сообщения коммитов содержат `[skip ci]` и не содержат `Co-Authored-By`.

Работа ограничилась локальными правками и проверками выше. Cargo, rustc, Kani, CBMC и CI не запускались, пушей не было. Результат формальной проверки P‑2b пока отсутствует.
