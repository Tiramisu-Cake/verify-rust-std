# CAL1 · исправление после прогона 45249887979

`READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Старые и новые SHA, trees, единственные родители, SHA-256 request и bundle и привязка будущего trigger приведены в [CAL1-IMPL-HANDOFF.md](CAL1-IMPL-HANDOFF.md). Ревью `4f83c2a283` относилось к tree прогона. [Задание на исправление](CAL1-FIX-TASK.md) · [Ревью исходного пакета](CAL1-REVIEW.md)

В run 45249887979 cfg-off discovery занял 1049,23 с. Cfg-on discovery остановился через 24,64 с на `kani-compiler`, exit 1, sampled RSS 1,48 GiB. Хвост Cargo сообщает 8817 ошибок `core`, а сохранённый excerpt не содержит первичного сообщения. В исходниках `KeyLess<u8>` вручную реализует `FnOnce` и `FnMut`. Gate `fn_traits` устраняет конкретный дефект переноса. Причина полного каскада остаётся неизвестной. [Setup receipt](/root/ch8-artifacts/run-45249887979/ch8-cal1-Linux-X64-45249887979-1/setup.json) · [Компаратор](/root/verify-rust-std-cal1-w11/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs)

## Изменённые файлы

| Дерево | Файлы | Правка |
| --- | --- | --- |
| Overlay | `library/core/src/lib.rs` | Одна строка `#![cfg_attr(all(kani, kani_smallsort_cal1), feature(fn_traits))]`. |
| Control | `ch8-cal1/request.py` | Проверка точной строки, режима файла и побайтного восстановления base blob. |
| Control | `ch8-cal1/CI-REQUEST.json`, `ch8-cal1/std-overlay.bundle` | Новый overlay commit/tree, SHA-256 bundle и лимит пробы 180 с. |
| Control | `ch8-cal1/run.py`, `ch8-cal1/setup_diagnostics.py` | Ранняя компиляция, cfg-on discovery первым, ограниченные диагностические записи и ссылка из `error.json`. |
| Control | `.github/workflows/ch8-q-pilot.yml`, `ch8-cal1/test_run.py` | Имя setup-шага отражает пробу, тесты покрывают границы и ошибки. |
| g0 | `CAL1-IMPL-HANDOFF.md`, `CAL1-FIX-HANDOFF.md` | Идентичность пакета и данные для независимого ревью. |

## Ранняя проба

```text
{tool}/scripts/kani verify-std -Z unstable-options -Z function-contracts
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers
  -Z stubbing --no-assert-contracts --no-codegen --only-codegen --quiet
  --target-dir {state}/setup/overlay-compile/kani-target {std}/library
```

Runner передаёт `RUSTFLAGS=--cfg=kani_smallsort_cal1`, `CARGO_TERM_VERBOSE=true` и отдельный свежий `CARGO_TARGET_DIR={state}/setup/overlay-compile/cargo-target`. `--quiet` отключает баннер Kani, который на этом пине запускает `cbmc --version`. Cargo продолжает печатать команду компилятора в stderr и отдавать JSON-диагностику driver. Driver печатает раскрытые ошибки rustc в stdout. [Настройка Cargo](https://doc.rust-lang.org/cargo/reference/config.html#termverbose) · [Баннер Kani](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/version.rs#L28-L85) · [Вывод диагностики](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/call_cargo.rs#L310-L341)

На пине `--no-codegen` добавляет rustc `-Z no-codegen`. `base_rustc_flags` добавляет `--cfg=kani` и читает токены `RUSTFLAGS`. `cargo_build_std` задаёт pinned `kani-compiler` как `RUSTC` и через `PassTo::AllCrates` передаёт флаги в `CARGO_ENCODED_RUSTFLAGS` для сборки `panic_abort,core,std`. [Флаги компилятора](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/call_single_file.rs#L227-L315) · [Std build](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/call_cargo.rs#L84-L139) · [Кодирование флагов](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/util.rs#L207-L237)

В rustc `65ce8611f` из аттестованного `nightly-2026-11-19` ветка `start_codegen` с `no_codegen` пропускает вызов Kani codegen. Она оставляет Cargo интерфейсные Rust-артефакты. Kani пропускает отсутствующие файлы Kani metadata рядом с `.rmeta`, поэтому новый target не даёт `std_project` моделей для линковки. После `std_project` аргумент `--only-codegen` завершает driver до `verify_project`, отбора harnesses и JSON export. Это проверяет frontend всей cfg-on `core`. Длительность и фактический compile PASS проверяются на hosted runner. Полный cfg-on `kani list --std` по-прежнему нужен для exact selector/kind. [Исходник rustc `start_codegen`](https://github.com/rust-lang/rust/blob/65ce8611f/compiler/rustc_interface/src/passes.rs) · [Отбор Kani artifacts](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/call_cargo.rs#L531-L562) · [Std project](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/project.rs#L354-L396) · [Остановка driver](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-driver/src/main.rs#L149-L175)

Порядок на каждой платформе — сборка и аттестация stock Kani, detached overlay, `OVERLAY_COMPILE_PREFLIGHT`, полный `OVERLAY_DISCOVERY` и проверка 11 корней и двух provider registrations, `BASE_DISCOVERY`, сверка списков, восстановление detached overlay, `common_ready`. Дедлайн пробы равен минимуму `now + 180 с` и setup-дедлайна. Действующие watchdog, RSS и reap охватывают пробу. Для `PASS` receipt требует exit 0, валидный sampler, полный захват, подтверждённый reap, ноль наблюдавшихся CBMC-процессов и запись `Running` с `kani-compiler`, `--crate-name core`, `--cfg=kani`, `--cfg=kani_smallsort_cal1` и `-Z no-codegen`. Процессный счётчик отражает сэмплирование. Отсечение по времени или RSS оставляет `compilation_status=UNKNOWN`. [Runner](/root/kani-cal1-control-w11/ch8-cal1/run.py:204) · [Supervisor](/root/kani-cal1-control-w11/ch8-cal1/supervisor.py)

## Диагностика и локальная валидация

- Для tool build, пробы и обоих discovery первая диагностика в каждом потоке сохраняет код, span, разметку и note/help в порядке вывода. Окно ограничено 80 строками и 16 KiB UTF-8. При отсутствии заголовка остаётся до 8 строк и 2 KiB с `prefix_fallback`. Запись указывает поток, строки, стартовый byte offset, размер прочитанного префикса и захвата и флаги усечения. Хвост Cargo ограничен 4 KiB stderr. `error.json` указывает на нужную запись в `setup.json` и включает короткий первичный заголовок, если он распознан. В выходной артефакт попадают bounded receipts. [Проекция](/root/kani-cal1-control-w11/ch8-cal1/setup_diagnostics.py)
- Ошибки ранней пробы и cfg-on списка блокируют cfg-off discovery и измерения. При Linux setup failure `common_ready` отсутствует, macOS остаётся пропущенным, `always()` публикует частичный артефакт. До измерений для слотов остаются `NOT_STARTED`, пустая проекция и неизвестные измерительные поля. [Workflow](/root/kani-cal1-control-w11/.github/workflows/ch8-q-pilot.yml) · [Тесты](/root/kani-cal1-control-w11/ch8-cal1/test_run.py)
- Прошли 43 offline-теста Python. Синтетические сценарии проверили многострочную `error[E0183]` в stdout с ANSI и каскадом, ошибку stderr, Cargo summary, ограничения строк и байтов, TIMEOUT/RSS, проверку witness, остановку перед базовым списком, возврат точного overlay и публикацию. Git-fixture проверил лишнее изменение, дублирование и отсутствие gate. Bundle воспроизведён на отдельном shallow std base с проверкой digest, tree, sole parent и layout. Синтетическое событие exact push на итоговом control прошло guard, несовпадение SHA отклонено.
- Сравнение исходников сохранило roster, OB12, solver, сценарии свойств и covers, измерительный argv, часы слотов, финальную аттестацию и upload. Прошли `git diff --check`, разбор PyYAML и `bash -n` для workflow обоих jobs. Локальная проверка состояла из Git, чтения исходников и синтетических тестов. Compile PASS исправленного overlay и результаты корней ожидают отдельного hosted запуска.
