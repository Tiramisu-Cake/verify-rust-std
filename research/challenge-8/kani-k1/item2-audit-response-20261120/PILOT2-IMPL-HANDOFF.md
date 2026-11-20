# Кампания 2 q-пилота — handoff реализации

Локальный кандидат по [заданию](PILOT2-IMPL-TASK.md) и §4 [анализа кампании 1](PILOT-RUN1-ANALYSIS.md). Статические проверки и синтетические тесты пройдены. Статус `RESEARCH_ONLY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Для приёмки потребуются отдельное ревью и разрешение на запуск.

## Идентичности

| Объект | std | control |
| --- | --- | --- |
| Worktree | `/root/verify-rust-std-ch8-q-pilot-v1` | `/root/kani-ch8-q-pilot-control-v1` |
| Ветка | `experiment/ch8-q-pilot-v1` | `experiment/ch8-q-pilot-control-v1` |
| Commit | `0e9b28b293f4360b005d33583d2cf9ac06d1790b` | `301bd6465ae8f4aaec2d40baa19eb3c8624a5912` |
| Tree | `2d13d786186a96e3eeb55ff9969f63388eeee042` | `1c7d61e3d8c05fd9987d3d854716a106a3423244` |
| Единственный parent | `5544e01921d5c67c21d4ab919e8f76b43f884d92` | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` |

| Файл из коммита | SHA-256 |
| --- | --- |
| `ch8-q-pilot-control/CI-REQUEST.json` | `1269c685d33af77c86a2c7d5071d36d48eeef1d22fc4e6fb9db6bc9996a186a5` |
| `library/core/src/slice/sort/shared/smallsort/verify/sorting_q_model.rs` | `cbe0683c15e286951421c1deb192c4ab9b6a293a6740440ec334343d0daf7349` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |

## Дельта

- **std.** Один файл, +56/−36 строк. Общий сканер строит owned `u32` для span и order-stat из 17 литеральных смещений. Сканер принимает адрес проверенного span или среза и читает каждый байт под `i < len`. Сохранены порядок проверок длины, последнего адреса и fat slice, inactive dispatch, проверка q и четыре байта хвоста sort13. Order-stat строит target из `count_ones` без DP. Insert использует маску префикса для проверки монотонности и сравнивает маску результата целиком. Все биты выше активной длины нулевые.
- **Контракты и харнессы.** Файлы производственной сортировки, харнессов и контролей совпадают с parent. Харнессы передают target по ссылке и не обращаются к отдельным битам. Сохранены коды ролей, `Q_ABSENT`, covers tails 1–16 и P-5c. На пути P-5c с нулевым N17 и `q=1` запись 255 в первый байт меняет наблюдаемую маску с 0 на 1, а target равен 0.
- **Control.** Коммит создан с тем же parent, что и `0bf2794faa624e8d9adb9be1990e96beca6cd104`. Относительно этого коммита дельта содержит три значения в `CI-REQUEST.json` (+3/−3 строки) — `std_sha`, `std_tree` и SHA-256 `sorting_q_model.rs`. Сверены workflow с `GITHUB_ENV`, runner, тесты, семь корней, cfg, argv, unwind36, V34, лимиты 600 с и 6 GiB, tool pin и `event_ref=refs/heads/uninit-ci/ch8-q-pilot-v1`.

## Перебор эквивалентности

Для каждой длины `n=0..17` Python перебрал все `2^n` входных масок. Старая модель использовала булевы позиции и исходный нисходящий DP `at_least`. Новая модель использовала литеральные смещения из патча, `M(n)=(1<<n)-1` и формулы из §4 анализа.

| Проверка | Число случаев | Результат |
| --- | ---: | --- |
| Скан и order target. Булевы позиции и DP против `M(n) ^ M(n-c)`, включая нули за длиной | 262 143, из них 131 072 при `n=17` | PASS |
| Insert Pre и post. Соседние пары против `((P<<1) & M(n-1) & !P)==0`. Прежний post задаёт единственную допустимую последовательность для каждого `before`, она совпала с `before` или `(before<<1) & M(n)` в зависимости от последнего бита | 262 140 при `n=2..17`, включая все маски длины 17 | PASS |
| Отказ активного insert при `n=0,1` | 3 маски | PASS |
| Order post. Сравниваемый старым `zip` префикс каждого 17-битного target совпадает с `target & M(n)` для каждой выходной длины | 2 359 296 пар target и длины | PASS |
| Скан граничных длин 0, 1, 2, 17 и порогов 0/255 для каждого значения байта | 2 048 | PASS |

Статически при `len=0` скан не читает память, а order target равен 0. `len=1` использует только бит 0, insert отклоняет эту длину до вычисления `len-1`. При `len=2` префикс из одного бита всегда удовлетворяет проверке монотонности. При `len=17` последнее смещение равно 16, максимальная активная маска равна `0x1ffff`. При `q=0` все активные биты равны 1, при `q=255` единицы соответствуют только байтам 255. Оба постусловия сохраняют прежние сравнения длин и q там, где они входят в контракт.

## Локальные проверки

- `rustfmt --check --edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features` для изменённого файла. Использован `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt` с `LD_LIBRARY_PATH=/root/rustfmt-toolchains/nightly-2026-11-19/lib`. Код 0.
- `python3 ch8-q-pilot-control/run.py validate` в control с синтетическими GitHub metadata. Репозиторий `Tiramisu-Cake/kani`, событие `push`, ref из request, attempt 1, run ID `synthetic`, `GITHUB_SHA` равен новому control commit. Подтверждены control identities и SHA-256 выше.
- `python3 ch8-q-pilot-control/run.py check-source --std /root/verify-rust-std-ch8-q-pilot-v1 --tool /root/kani-upstream-ch8-s1`. Код 0. Подтверждены чистые checkout, std commit/tree и все шесть SHA-256 файлов std. Tool совпал с `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_run.py` из `ch8-q-pilot-control`. **9/9**. Тесты использовали временные Git checkout и подставные Python-процессы.
- `git diff --check`, точные parent, состав дельт, чистота worktree и метаданные коммитов проверены. Автор и коммитер — `Tiramisu-Cake <igkharin@gmail.com>`, сообщения с `[skip ci]`.

Компиляторы, верификаторы и CI не запускались. Коммиты остались локальными. Сборка Rust, verdicts корней, ресурсный эффект и оценка B1/B2 остаются открытыми.
