# KANI3300 D0-PR — исправление сборки, подготовлено для CI

- Worktree: `/root/kani-fix-3300-d0`.
- Diagnostic branch: `diagnostics/kani-3300-d0-pr`.
- Parent: `955cd015649aa79be511fe1732d48fdc8535741f`.
- Diagnostic commit: `5eec235e3d0eeb99d7e432fcaef3a3135747b789`.
- Diagnostic tree: `ed095daec3cd82ef024e97c0c3951a591dfd6c39`.
- CI branch: `ci/d0-diagnostics-r3`.
- Единственный CI-only commit поверх diagnostic: `8f6d3f45eb644772369a99ddc79466c6c24c1b54`.
- Baseline остаётся `a0a2386001a15fecfe2facc2f6cd87f3dee13b60`.

Координатор сообщил: run `43206193762` на `34c0848da` остановился
на layout gate в обеих сборках; после `str(target-pointer-width)` в
`c670c5a24` run `43206693260` собрал baseline (exit 0), но candidate
получил 57 E0277: Cargo `serde_core 1.0.229` против sysroot `1.0.228`.
Это исходные сообщённые факты; артефакты/логи здесь не скачивались.

## Выбор реализации

`encoded` использует `Serialize` из sysroot `serde_core` и sysroot
`serde_json::to_string`. Cargo-зависимость JSON переименована в
`kani_serde_json` и возвращена существующим потребителям через
`extern crate kani_serde_json as serde_json`: metadata и внешние Kani-типы
сохраняют Cargo-serde. Освободившееся имя внешнего crate `serde_json`
позволяет отдельно связать sysroot JSON как `rustc_serde_json`; прямой
Cargo-зависимости `serde_core` у compiler нет. Package/version/features
Cargo JSON, Cargo.lock и library sources не меняются.

Пять Kani-типов снимков (`MutableBody`, `InsertPosition`,
`SourceInstruction`, `MemoryInitOp`, `InitRelevantInstruction`) вместо
Cargo derive получают field-only реализации sysroot `Serialize`.
Сохранены поля, их порядок, имена и индексы всех вариантов, внешнее
тегирование enum. Собственный serializer здесь не нужен: существующий
rustc_public serializer уже сохраняет opaque IDs без `Ty::Debug`.
Ручные реализации также исключают зависимость от версии приватных путей,
генерируемых Cargo derive. Простое выравнивание номера Cargo-serde
не выбирало бы непосредственно crate identity компилятора.

Используется существующий механизм `rustc_private`, как для других
sysroot crates. Статически проверен путь разрешения direct crates в
[pinned creader.rs](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_metadata/src/creader.rs):
`existing_match` требует hash, direct load использует `PathKind::Crate`.
Это проверка исходника, не подтверждение сборки нового кандидата.

Все новые sysroot aliases/impls ограничены `cprover`; fallback без
`cprover` сохранён. `enabled`, ленивые payload closures, hooks, normal
prewarm, transformer/cache и порядок запросов тела не менялись.
Новые реализации только читают существующие поля: без Debug, body
reconstruction, дополнительных compiler queries и изменений модели.

## CI и проверки

CI-only commit переносит пакет `c670c5a24`, сохраняет layout-исправление,
обновляет CANDIDATE/tree, workflow checkout и README. `run.py` — 100644.
Baseline, fixture, rustc/tool pins и остальные gates сохранены.
Добавлен синтетический регрессионный тест layout с полностью
замоканными внешними командами.

Пройдены rustfmt-обёртка для всех 18 Rust-файлов diagnostic diff,
field/variant audit пяти типов, lineage/pins/fixture/scope/TOML/Python
checks, actionlint, `git diff --check`, 48 синтетических CI-тестов.
Luna High review: конкретных блокирующих замечаний нет; см. REVIEW.md.
Точные hashes и результаты — VALIDATION.json; воспроизводимая проверка
полей — `python3 STATIC-CHECK.py /root/kani-fix-3300-d0`.

Локальные cargo/rustc/Kani/CBMC не запускались. Новая сборка, CI,
model equivalence и proof — NOT_RUN. Kani не пушился, CI не отправлялся;
сборку выполняет координатор. Исторические D0-P файлы не переписывались:
этот каталог — отдельная research-запись, публикуемая в g0 с `[skip ci]`.
STOP на D0-PR READY.
