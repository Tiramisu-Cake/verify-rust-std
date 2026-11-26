# Issue repro перед публикацией · handoff

**READY_FOR_REVIEW** (FIX1) · `go=NOT_GRANTED` · `proof_credit=NONE` · w11 · [Задание](TASK.md) · [Ревью R1](REVIEW.md)

**FIX1:** control `bbead350abf9df3f73720f7829efd166ae0cc9e4`, tree `340508750522c592e977f4222f724f201890e873`, review-trigger `7032ce48d8b2cd9db3668b339e47d80c33d80301`. R1-кандидат: control `cdff77be85`, tree `2a461d31bc`. [Что исправлено](#fix1-после-ревью-r1)

Push, CI, изменений Actions variables, cargo, rustc, Kani и CBMC локально не было. Результат прогона до CI неизвестен.

## Коммиты

| Что | Commit | Tree | Parent |
| --- | --- | --- | --- |
| **Control FIX1**, ветка `work/issue-repro-control-w11` | `bbead350abf9df3f73720f7829efd166ae0cc9e4` | `340508750522c592e977f4222f724f201890e873` | R1-control `cdff77be85363b6096c8945791ab4868cfe65ade` |
| **Review-trigger FIX1**, локальный ref `local/issue-repro-trigger-review` | `7032ce48d8b2cd9db3668b339e47d80c33d80301` | `340508750522c592e977f4222f724f201890e873` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, единственный |
| Control R1 | `cdff77be85363b6096c8945791ab4868cfe65ade` | `2a461d31bc8558ea469c6d758979dbfcf4045eab` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Review-trigger R1, заменён | `844f093ad4cd0fe179122bacca4c628a2b61d7db` | `2a461d31bc8558ea469c6d758979dbfcf4045eab` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

- **Значение `CH8_ISSUE_REPRO_TRIGGER_TREE`: `340508750522c592e977f4222f724f201890e873`.** Прежнее `2a461d31bc` из R1 недействительно.
- Worktree control: `/root/kani-issue-repro-control-w11`, общий репозиторий `/root/kani-ch8-s4p-1-r1-control-w13`. R1-control основан прямо на `467af9cb8d`, FIX1 лежит поверх него. Дельта trigger от `467af9cb8d`: `.github/workflows/ch8-q-pilot.yml` заменён, добавлен каталог `ch8-issue-repro/`. `ch8-s2.yml` не тронут, он слушает только `uninit-ci/ch8-s4p-*`.
- Автор и коммиттер — `Tiramisu-Cake <igkharin@gmail.com>`. Все сообщения control и review-trigger содержат `[skip ci]`, знака решётки перед цифрой нет.
- **Боевой trigger создаёт координатор: tree `340508750522c592e977f4222f724f201890e873`, единственный parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. В его сообщении не должно быть `[skip ci]`**, иначе push не запустит workflow.

## Файлы

| Файл | SHA-256 |
| --- | --- |
| `ch8-issue-repro/bool_order.rs`, 447 B | `8d179be93a25454f95120c4b78ef344c7462c404eae1086f0fb7efe48623579f` |
| `ch8-issue-repro/cast.rs`, 508 B | `b2adb44dd16ef9823e0b5c33ce0b5c53908ac31c3795cf913d2d5d973606709a` |
| `ch8-issue-repro/run.py`, FIX1 | `b79e924f427ce9fa2bf6cd81774a7382e92e80663ea11511194628fe10415480` |
| `.github/workflows/ch8-q-pilot.yml`, FIX1 | `b67bdb1fe4af49d33ea83365512e20582ae822a284d6b85b80bf3ffb67b1823f` |
| Черновик `ISSUE-KANI-BOOL-ORDER-DRAFT.md` на момент сверки FIX1, после правки координатора | `4bd1e96d6689ab6e540d553592079ff8bd9766b749ccf5faae60a2decf66aacd` |
| Черновик `ISSUE-KANI-VV-ARRAY-ELEM-CAST-DRAFT.md` на момент сверки | `8374a99aeaeee3bf9b9f18b4d5136c7d79d63b5c0a6479f2790d9d8b08b26f78` |

Оба `.rs` побайтно равны блокам кода черновиков. Блок — текст строго между единственной строкой ` ```rust ` и следующей строкой ` ``` ` плюс один завершающий перевод строки. Сверка: [check_drafts.py](check_drafts.py) `/root/kani-issue-repro-control-w11/ch8-issue-repro` → `MATCH` по обоим файлам. Если черновики правятся до публикации, сверку надо повторить: при изменении блока меняются и SHA в `run.py`, и tree.

## Job

Один job `ubuntu-24.04`, `timeout-minutes: 45`. Секретов и токенов нет, `permissions: contents: read`, все checkout с `persist-credentials: false`.

1. Job-level `if`: `Tiramisu-Cake/kani`, `push`, `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1.
2. Checkout control по `github.sha`, depth 2.
3. `run.py gate` до любого стороннего кода. Состояние пишется в `$RUNNER_TEMP/ch8-issue-repro`, на уровне job env больше ничего, кроме переменной гейта. Проверяется: переменная — 40 hex; repo, event и ref; attempt `1`; `HEAD == GITHUB_SHA == event.after`; `event.ref`; `deleted == false`; `repository.full_name`; родители ровно `[467af9cb8d…]`; `HEAD^{tree}` равен переменной; checkout control чистый. Квитанция `trigger.json`. Следующие шаги `run.py` перепроверяют гейт и сравнивают результат с квитанцией.
4. Checkout `model-checking/kani` по полному SHA `8c6dba5935e8b37a905145c57572d1b67489bae2`, depth 2, submodules recursive. Это шаг фазы 0 без `sources`: бандла кандидата и подмены `rust-toolchain.toml` нет.
5. `run.py tool` проверяет commit и tree `3ae54fa78d…`, detached HEAD, инициализированные submodules без дрейфа, чистое дерево, `channel = "nightly-2026-11-23"` и `CBMC_VERSION="6.11.0"`.
6. `./tool/.github/actions/setup` (`os: ubuntu-24.04`, `kani_dir: tool`). Toolchain ставится по собственному TOML Kani.
7. `cargo build-dev --release` в `tool`, как в фазе 0: тот же набор снятых `RUSTFLAGS`/`RUSTC*`/`CARGO_*`, `CARGO_BUILD_JOBS=2`. Затем `run.py tool --after-build`, untracked там не учитываются.
8. `run.py probes`, лимит шага 20 мин. Сводка переписывается после каждой команды со статусом `INCOMPLETE (k of 6 run)`, поэтому при таймауте шага готовые строки остаются в артефакте:
   - SHA обоих `.rs` сверяются с пином, файл копируется в свой пустой каталог на каждую команду;
   - `tool/scripts` ставится первым в `PATH`, и скрипт проверяет, что `kani` разрешается именно в `tool/scripts/kani`. argv буквально `kani <file> …` из задания, без `--unwind`, object-bits, `--verbose`, `--jobs` и `--output-format`;
   - каждая команда — отдельный процесс в своей группе. Лимиты: 150 с, у verbosity-прогона 240 с, в сумме 990 с; запросы версий по 30 с, ещё 120 с. По истечении лимита SIGKILL группе. Записываются exit code, факт таймаута, wall-время;
   - stdout и stderr читаются целиком, а хранится префикс до 1 MiB на поток;
   - в verbosity-прогоне по всем байтам обоих потоков считаются строки с `warning: ignoring`. Первые три сохраняются целиком, но не длиннее 64 KiB, усечение помечается. Сам лог этого прогона не сохраняется;
   - версии: `kani --version`, `cbmc --version`, а в каталоге `tool` — `rustc --version --verbose` и `rustup show active-toolchain`.
9. Upload `*.json` квитанций и `artifact/` (`SUMMARY.md`, `summary.json`, оба `.rs`, `streams/<id>.{stdout,stderr}.txt` пяти основных команд), если гейт пройден. `SUMMARY.md` дублируется в job summary.

Статус `SUMMARY.md`: `MATCH`, если все пять основных команд дали MATCH, иначе `MISMATCH`. Шаг probes при MISMATCH не падает, результат лежит в данных.

| Команда | MATCH, если |
| --- | --- |
| `kani bool_order.rs --harness bool_order_probe --exact` | exit ≠ 0, `VERIFICATION:- FAILED`, FAILURE ровно у `bool_order_probe.assertion.1` |
| `kani bool_order.rs --harness bool_order_u8_control --exact` | exit 0, `SUCCESSFUL`, разобрана хотя бы одна check, FAILURE нет, cover есть и все `SATISFIED` |
| `kani cast.rs -Z valid-value-checks --harness array_elem_cast_nonzero --exact` | exit ≠ 0, `FAILED`, ровно одна FAILURE: имя содержит `.unsupported_construct.`, Description равна тексту из задания; единственный cover — `UNREACHABLE` |
| `kani cast.rs -Z valid-value-checks --harness array_elem_cast_u8_control --exact` | exit 0, `SUCCESSFUL`, разобрана хотя бы одна check, FAILURE нет, cover есть и все `SATISFIED` |
| `kani cast.rs --harness array_elem_cast_nonzero --exact` | exit 0, `SUCCESSFUL`, разобрана хотя бы одна check, FAILURE нет, cover есть и все `SATISFIED` |
| `kani bool_order.rs --harness bool_order_probe --exact --cbmc-args --verbosity 9` | `OBSERVE`: число строк `warning: ignoring` и первые три |

Статусы cover публикуются для всех команд. По cover гейтятся cast ON и три SUCCESS-команды. Для `bool_order_probe` черновик пишет «cover SATISFIED», но в ожидание задания это не входит, поэтому значение просто попадёт в таблицу.

## Локальные проверки

- YAML разбирается, в `jobs.repro.env` только `vars`-переменная, `runner.temp` остался лишь в `with:` у upload. 9 шагов, триггер `push` на `uninit-ci/ch8-q-pilot-v1`. `bash -n` проходит для всех пяти `run:`-блоков. `actionlint` на сервере нет.
- [selftest.py](selftest.py) `ch8-issue-repro/run.py` → `selftest OK` (FIX1, SHA-256 `c6471d61d92e…`). Он проверяет:
  - парсер и судью на синтетическом regular-выводе Kani: MATCH и MISMATCH для exit, terminal, cover и текста;
  - сканер `warning: ignoring` на стыках чанков, лимит строки и лимит префикса;
  - `run_command`: exit code, раздельные потоки, таймаут с убийством группы;
  - гейт в scratch-репозитории: позитив; негатив для неверного tree, пустой переменной, attempt 2, чужого ref, другого event, чужого SHA и чужого parent;
  - экранирование `|` в Markdown;
  - FIX1: SUCCESS-негативы (нет разобранных checks, cover `UNSATISFIABLE`, нет cover, второй cover `UNREACHABLE`), сумму лимитов внутри шага, промежуточную сводку `INCOMPLETE` без verbosity-строки, каталог состояния из `RUNNER_TEMP`.
- Сверка SHA с черновиками — `MATCH` и на R1, и на FIX1 (после удаления координатором фразы про `-Z valid-value-checks` из bool-черновика блоки не изменились).

## Риски

- Формат regular-вывода (`Check N: <name>` / `- Status:` / `- Description:`) взят из прежних пакетов, на 8c6dba5935 его подтвердит только CI. Если парсер не распознает вывод, будет MISMATCH с полным stdout в артефакте, ложного MATCH не будет.
- Без `--verbose` Kani может не пропустить сообщение CBMC `warning: ignoring` в свой вывод. Тогда счётчик даст 0, и это наблюдение, а не опровержение: флаг задание не разрешает.
- Сборка на nightly-2026-11-23 этим пакетом ещё не проверялась. Фаза 0 в 45886041869 шла на 11-21: с момента старта ~280 с, из них build ~146 с. Запас в 45 мин большой.

## FIX1 после ревью R1

| Пункт R1 | Исправление |
| --- | --- |
| 1, блокер: `runner.temp` в job env | Строка `ISSUE_REPRO_STATE` удалена. `run.py` берёт `Path($RUNNER_TEMP) / "ch8-issue-repro"`. Upload по-прежнему использует `${{ runner.temp }}` в `with:`, это допустимо |
| 2: SUCCESS без checks и cover | SUCCESS требует `checks > 0`, хотя бы один cover и все cover `SATISFIED` |
| 3: лимиты команд больше шага | Лимиты 5×150 + 240 = 990 с, версии 4×30 с. Итого ≤ 1110 с при шаге 1200 с, selftest проверяет это неравенство. `summary.json` и `SUMMARY.md` переписываются после каждой команды |
| 4: `[skip ci]` в боевом trigger | Записано в разделе «Коммиты» |
| 5: фраза в bool-черновике | Сделано координатором. Блоки не изменились, check_drafts — `MATCH` |
| 6: actions по тегам | Без изменений, тот же шаблон, что в прежних пакетах |

Дельта FIX1 к R1: `.github/workflows/ch8-q-pilot.yml` (−1 строка) и `ch8-issue-repro/run.py`. Файлы `.rs` не менялись.
