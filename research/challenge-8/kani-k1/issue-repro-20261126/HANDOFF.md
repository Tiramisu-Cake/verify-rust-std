# Issue repro перед публикацией · handoff

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE` · w11 · [Задание](TASK.md)

Push, CI, изменений Actions variables, cargo, rustc, Kani и CBMC локально не было. Результат прогона до CI неизвестен.

## Коммиты

| Что | Commit | Tree | Parent |
| --- | --- | --- | --- |
| Control, ветка `work/issue-repro-control-w11` | `cdff77be85363b6096c8945791ab4868cfe65ade` | `2a461d31bc8558ea469c6d758979dbfcf4045eab` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Review-trigger, локальный ref `local/issue-repro-trigger-review` | `844f093ad4cd0fe179122bacca4c628a2b61d7db` | `2a461d31bc8558ea469c6d758979dbfcf4045eab` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, единственный |

- **Значение `CH8_ISSUE_REPRO_TRIGGER_TREE`: `2a461d31bc8558ea469c6d758979dbfcf4045eab`.**
- Worktree control: `/root/kani-issue-repro-control-w11`, общий репозиторий `/root/kani-ch8-s4p-1-r1-control-w13`. Control основан прямо на `467af9cb8d`, поэтому дельта control = дельта trigger: `.github/workflows/ch8-q-pilot.yml` заменён, добавлен каталог `ch8-issue-repro/`. `ch8-s2.yml` не тронут, он слушает только `uninit-ci/ch8-s4p-*`.
- Автор и коммиттер — `Tiramisu-Cake <igkharin@gmail.com>`. Оба сообщения содержат `[skip ci]`, знака решётки перед цифрой нет. Боевой trigger с тем же tree и тем же parent создаёт координатор.

## Файлы

| Файл | SHA-256 |
| --- | --- |
| `ch8-issue-repro/bool_order.rs`, 447 B | `8d179be93a25454f95120c4b78ef344c7462c404eae1086f0fb7efe48623579f` |
| `ch8-issue-repro/cast.rs`, 508 B | `b2adb44dd16ef9823e0b5c33ce0b5c53908ac31c3795cf913d2d5d973606709a` |
| `ch8-issue-repro/run.py` | `ad85800b47ae0f2b8e80073ba3be6b8fec9ef64c37a6e61146e6d0ca30de6ac7` |
| `.github/workflows/ch8-q-pilot.yml` | `fdaf49b0c31978fb8c8f8a5e35d166ed0f3884c6b995bbdefa4c996dc414b9f9` |
| Черновик `ISSUE-KANI-BOOL-ORDER-DRAFT.md` на момент сверки | `e362c50d9c4d27bf6acf61460bff651b25bbbd505a1accd4ead23c8cb7d14692` |
| Черновик `ISSUE-KANI-VV-ARRAY-ELEM-CAST-DRAFT.md` на момент сверки | `8374a99aeaeee3bf9b9f18b4d5136c7d79d63b5c0a6479f2790d9d8b08b26f78` |

Оба `.rs` побайтно равны блокам кода черновиков. Блок — текст строго между единственной строкой ` ```rust ` и следующей строкой ` ``` ` плюс один завершающий перевод строки. Сверка: [check_drafts.py](check_drafts.py) `/root/kani-issue-repro-control-w11/ch8-issue-repro` → `MATCH` по обоим файлам. Если черновики правятся до публикации, сверку надо повторить: при изменении блока меняются и SHA в `run.py`, и tree.

## Job

Один job `ubuntu-24.04`, `timeout-minutes: 45`. Секретов и токенов нет, `permissions: contents: read`, все checkout с `persist-credentials: false`.

1. Job-level `if`: `Tiramisu-Cake/kani`, `push`, `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1.
2. Checkout control по `github.sha`, depth 2.
3. `run.py gate` до любого стороннего кода. Проверяется: переменная — 40 hex; repo, event и ref; attempt `1`; `HEAD == GITHUB_SHA == event.after`; `event.ref`; `deleted == false`; `repository.full_name`; родители ровно `[467af9cb8d…]`; `HEAD^{tree}` равен переменной; checkout control чистый. Квитанция `trigger.json`. Следующие шаги `run.py` перепроверяют гейт и сравнивают результат с квитанцией.
4. Checkout `model-checking/kani` по полному SHA `8c6dba5935e8b37a905145c57572d1b67489bae2`, depth 2, submodules recursive. Это шаг фазы 0 без `sources`: бандла кандидата и подмены `rust-toolchain.toml` нет.
5. `run.py tool` проверяет commit и tree `3ae54fa78d…`, detached HEAD, инициализированные submodules без дрейфа, чистое дерево, `channel = "nightly-2026-11-23"` и `CBMC_VERSION="6.11.0"`.
6. `./tool/.github/actions/setup` (`os: ubuntu-24.04`, `kani_dir: tool`). Toolchain ставится по собственному TOML Kani.
7. `cargo build-dev --release` в `tool`, как в фазе 0: тот же набор снятых `RUSTFLAGS`/`RUSTC*`/`CARGO_*`, `CARGO_BUILD_JOBS=2`. Затем `run.py tool --after-build`, untracked там не учитываются.
8. `run.py probes`, лимит шага 20 мин:
   - SHA обоих `.rs` сверяются с пином, файл копируется в свой пустой каталог на каждую команду;
   - `tool/scripts` ставится первым в `PATH`, и скрипт проверяет, что `kani` разрешается именно в `tool/scripts/kani`. argv буквально `kani <file> …` из задания, без `--unwind`, object-bits, `--verbose`, `--jobs` и `--output-format`;
   - каждая команда — отдельный процесс в своей группе. Лимиты: 300 с, у verbosity-прогона 420 с, по истечении SIGKILL группе. Записываются exit code, факт таймаута, wall-время;
   - stdout и stderr читаются целиком, а хранится префикс до 1 MiB на поток;
   - в verbosity-прогоне по всем байтам обоих потоков считаются строки с `warning: ignoring`. Первые три сохраняются целиком, но не длиннее 64 KiB, усечение помечается. Сам лог этого прогона не сохраняется;
   - версии: `kani --version`, `cbmc --version`, а в каталоге `tool` — `rustc --version --verbose` и `rustup show active-toolchain`.
9. Upload `*.json` квитанций и `artifact/` (`SUMMARY.md`, `summary.json`, оба `.rs`, `streams/<id>.{stdout,stderr}.txt` пяти основных команд), если гейт пройден. `SUMMARY.md` дублируется в job summary.

Статус `SUMMARY.md`: `MATCH`, если все пять основных команд дали MATCH, иначе `MISMATCH`. Шаг probes при MISMATCH не падает, результат лежит в данных.

| Команда | MATCH, если |
| --- | --- |
| `kani bool_order.rs --harness bool_order_probe --exact` | exit ≠ 0, `VERIFICATION:- FAILED`, FAILURE ровно у `bool_order_probe.assertion.1` |
| `kani bool_order.rs --harness bool_order_u8_control --exact` | exit 0, `SUCCESSFUL`, FAILURE нет |
| `kani cast.rs -Z valid-value-checks --harness array_elem_cast_nonzero --exact` | exit ≠ 0, `FAILED`, ровно одна FAILURE: имя содержит `.unsupported_construct.`, Description равна тексту из задания; единственный cover — `UNREACHABLE` |
| `kani cast.rs -Z valid-value-checks --harness array_elem_cast_u8_control --exact` | exit 0, `SUCCESSFUL`, FAILURE нет |
| `kani cast.rs --harness array_elem_cast_nonzero --exact` | exit 0, `SUCCESSFUL`, FAILURE нет |
| `kani bool_order.rs --harness bool_order_probe --exact --cbmc-args --verbosity 9` | `OBSERVE`: число строк `warning: ignoring` и первые три |

Статусы cover публикуются для всех команд. По cover гейтится только cast ON. Для `bool_order_probe` черновик пишет «cover SATISFIED», но в ожидание задания это не входит, поэтому значение просто попадёт в таблицу.

## Локальные проверки

- YAML разбирается, 9 шагов, триггер `push` на `uninit-ci/ch8-q-pilot-v1`. `bash -n` проходит для всех пяти `run:`-блоков. `actionlint` на сервере нет.
- [selftest.py](selftest.py) `ch8-issue-repro/run.py` → `selftest OK`. Он проверяет:
  - парсер и судью на синтетическом regular-выводе Kani: MATCH и MISMATCH для exit, terminal, cover и текста;
  - сканер `warning: ignoring` на стыках чанков, лимит строки и лимит префикса;
  - `run_command`: exit code, раздельные потоки, таймаут с убийством группы;
  - гейт в scratch-репозитории: позитив; негатив для неверного tree, пустой переменной, attempt 2, чужого ref, другого event, чужого SHA и чужого parent;
  - экранирование `|` в Markdown.
- Сверка SHA с черновиками — `MATCH`, см. выше.

## Риски

- Формат regular-вывода (`Check N: <name>` / `- Status:` / `- Description:`) взят из прежних пакетов, на 8c6dba5935 его подтвердит только CI. Если парсер не распознает вывод, будет MISMATCH с полным stdout в артефакте, ложного MATCH не будет.
- Без `--verbose` Kani может не пропустить сообщение CBMC `warning: ignoring` в свой вывод. Тогда счётчик даст 0, и это наблюдение, а не опровержение: флаг задание не разрешает.
- Сборка на nightly-2026-11-23 этим пакетом ещё не проверялась. Фаза 0 в 45886041869 шла на 11-21: с момента старта ~280 с, из них build ~146 с. Запас в 45 мин большой.
