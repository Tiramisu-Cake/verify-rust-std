# KANI3300 X1 — export and JSON tooling cleanup (DRAFT / NOT ISSUED)

2026-11-13. Worker 15, одна будущая стадия, параллельно E1. Это верификация корректности, не security-работа.
Сейчас не выдано. После отдельной выдачи base `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`, isolated clone/branch;
Cloud $0, никаких local cargo/rustc/Kani/CBMC/Miri/builds, push/CI — координатор. Dirty/wrong base → STOP без reset/stash.

## Область

Только существующие `tests/json-handler/uninit-contract-oracles/**`, `uninit-contract-mode-boundaries/**`
и внутренние `docs/dev/kani3300-m2bs-handoff.md`, `kani3300-m2bs2-handoff.md`.
Не менять compiler/runtime, driver, `scripts/validate_json_export.py`, JSON schema, shared compiletest, fixture Rust bodies
и новые tests W14. Не реорганизовывать unrelated tests. Маркерную диагностику вместо `unwrap_or_default` здесь не делать:
она отложена координатором; сохранить честную запись этого статуса в research, без выдуманного production guard.

## Конкретная чистка

1. Удалить research URL и worker/coordinator/history/proof-credit bookkeeping из обоих README;
   оставить самодостаточное описание test purpose, режимов, ожидаемых outcomes и способа запуска.
   В mode-boundaries README сейчас есть ссылка на research `marker-modes/REQUIRED-STATE.md`; export не должен её требовать.
2. Сохранить оба внутренних handoff документа в research с происхождением, убрать их из export tree.
   Исторические commits/results не переписывать. Не удалять полезную пользовательскую документацию границ модели.
3. Упростить runner/checker: убрать дублирующую организационную metadata/постоянные receipts и неприбранные keep-temps,
   не создавать новый framework. Исторические evidence hashes/attestation можно вынести из upstream test data в research;
   actual expected roots/check rows/source binding и проверка полной failure set остаются.
   Temp cleanup с полезной диагностикой при отказе; CI-only evidence capture отдельно от regression test.
4. Не задавать искусственный процент сокращения. Предоставить before/after map: что удалено, почему это не predicate оракула,
   какие safeguards остались; если минимальная понятная версия почти не короче — объяснить, не ослаблять checker.

## Неприкосновенная семантика

- Восемь case оракулов: legal PFC/ordinary/полезные requires/ensures, lawful modifies, P2, postcondition-hole,
  user-frame violation и clause-transfer. Сохранять exact full failure multiset и требуемые useful SUCCESS rows.
- P2: две checks одного intended read допустимы как существующая instrumentation inventory; не требовать две разные UB.
  Дополнительный consequence assert разрешать только по уже точной строке/операции; не любой assert/Unsupported.
- Frame: только intended user `outside` violation; verifier-private writes не разрешать выдавать за expected user failure.
  Clause: один конкретный transmute/uninit read, не произвольный FAILED и не обязательный дубль другого слоя.
- Шесть mode roots: ordinary/SimpleCheck companions legal; actual recursive ordinary/check дают exact cycle Unsupported;
  Replace observation остаётся unclaimed. Не заменять семантику Rust predicate/assume ради упрощения.
- CC5 collector fix: cover group привязан к source, хотя generated/original copies различаются;
  хотя бы одна SATISFIED copy квалифицирует соответствующий cover, отдельная UNREACHABLE copy её не опровергает.
  Не принимать полезный check UNREACHABLE за SUCCESS и не прятать incomplete/missing/extra properties.
- Сохранять schema validation, duplicate keys/IDs, wrong root, unknown status, lost/extra failure, source/hash binding,
  prefix-only ID normalization и adversarial checker tests. Никаких substring-only failures, wildcard IDs или auto-learn goldens.

Python syntax/unit tests допустимы после выдачи, если не вызывают compiler/verifier/driver и не читают raw CI archives.
Остальная проверка — `git diff --check`, type/data-flow review и future fork CI координатора.
Если E1/M3 изменяет IDs, владелец suite получает exact delta после интеграции; обновление только review-bound,
с теми же intended operations и полным expected set, не автоматический снимок любого нового FAILED.

## Handoff

`kani3300/export-clean/`: INPUTS, EXPORT-FILE-MAP, ORACLE-INVARIANTS, REVIEW, CI-REQUEST, RESULT.
Зафиксировать source/base/tree, восемь oracle cases/шесть roots, Python-unit результаты и NOT_RUN для Kani.
CI-request сначала два JSON suites + checker negative tests, затем их включение в unchanged Quick на integrated C0.
Отклонение oracle strength/более широкий write scope/production fix → STOP, передать владельцу, не расширять X1.
Source neutral commit(s), Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push/CI/publications.
Финал после выдачи: `READY <source sha>`. Сейчас **DRAFT / NOT ISSUED**.
