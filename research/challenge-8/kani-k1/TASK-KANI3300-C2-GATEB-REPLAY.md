# KANI3300 C2 — SmallSort replay (Gate B′ rows) on the C2 freeze

2026-11-15. Worker15, одна стадия подготовки. Это верификация корректности, не security-работа.
Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены (только Python и `git diff --check`). Cloud $0.
Push, CI-запуск и review — координатор. Без PR/issue/публикаций. Диск ~96% занят: новые клоны не делать,
только `git worktree add` от существующего Kani-клона; без копий target/артефактов.

## Вход

- C2 Gate A принят: g0 `research/challenge-8/kani-k1/kani3300/c2-gatea/ACCEPTANCE.md`.
- Kani **C2 freeze** `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`, tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`
  (fork ветка `freeze/kani-3300-c2`; локально `/root/kani-fix-3300-c2-s6`, только чтение).
- Gate B′ на C1 (образец): `kani3300/gateb-prime-result/RESULT.md` (run 43600834435), задание `TASK-KANI3300-GATEB-PRIME.md`,
  пакет `kani3300/gateb-prime/`.
  - std test-only пакет: ветка `prep/kani3300-gateb-prime` @ `01d75b8e83` (overlay `933b20a237`),
    worktree `/root/verify-rust-std-kani3300-gateb-prime` — только чтение, std-патч **не менять**;
  - Kani CI overlay: fork ветка `ci/kani3300-gateb-prime-w15` @ `0c1cc8a7d05184044d496b01f5ed41cebfde0cac`
    (поверх run4 recipe `ac49cf8f62`, source binding C1 `1658f4cad`).
- Прецедент перепривязки на другой Kani: `/root/kani-fix-3300-sel1-replay-w15` (SEL1 replay), только чтение.

Exact identities записать до правок; dirty/wrong base → STOP без reset/stash.

## Задача

Перепривязать тот же bounded replay с C1 на C2 freeze. Это не только замена SHA: `ci/replay.py`, source binding
(сейчас `c1-source-binding.json`), request/overlay manifests и PACKAGE.json связывают tree, file/subtree hashes и
контрольные суммы вложенных файлов. Пересоздать их согласованно для `ad499e41dd`/`9829702c1a`, проверить шаги
observer/setup против текущего C2 дерева (`.github/actions/setup`, scripts). Новой алгоритмической работы нет:
Kani source, std-патч, harnesses, контракты, профиль и оракулы — без изменений.

Рабочее место: `git worktree add /root/kani-fix-3300-c2-gateb-w15` от `/root/kani-fix-3300-c2-s6`, локальная ветка
`ci/kani3300-c2-gateb-w15` от `ad499e41dd` + один CI-only commit (автор Tiramisu-Cake <igkharin@gmail.com> per-command,
без Co-Authored-By). Все собственные workflow только в CI overlay; источник Kani под ним не трогать.

## Строки и профиль (решение планера, без изменений относительно C1)

Те же 3 ON строки, тот же профиль: closure comparators, PFC targets, uninit ON, object-bits 12, unwind 34/34/16,
controls cfg ON, valid-value OFF, штатные solver/slicing/checks, organizer flags включая `--no-assert-contracts`.
Runner ubuntu-24.04, последовательно, jobs1/max-parallel1, одна попытка, cap 2400 s на строку, без автоповторов.

| ID | Selector | Оракул C2 |
|---|---|---|
| `merge-raw-closure-on` | `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` | **SUCCESS**, 0 failures/Unsupported, covers 5/5 |
| `merge-profile-closure-on` | `replay_gateb_prime::merge_profile_closure_scratch48_u8_n9` | **SUCCESS**, 0 failures/Unsupported, ensures достигнуты, covers 2/2 (обе подложки) |
| `sort4-closure-on` | `helper_contracts::sort4_safety_u64` | **BOUNDARY**: ровно 1 отказ `select_unpredictable` (hint.rs), 0 comparator/layout/uninit/frame failures |

Сравнение с C1 — по смыслу и достижимости. Числа 570 / 1028 / 758 checks — ориентир, равенство не требуется;
любую потерю полезных checks/ensures/covers объяснить. sort4 SUCCESS вместо границы — не засчитывать, review.
Сохранять полные списки отказов, effective argv, tool/runtime hashes, исходные exit/signal; `receipt.outcome=UNKNOWN`
требует явного review координатором.

## Handoff / STOP

Research в g0 `research/challenge-8/kani-k1/kani3300/c2-gateb/`: INPUTS (identities до/после), REBIND-MAP (что
пересоздано и почему; diff против `0c1cc8a7d0` по файлам), ROW-ORACLES, CI-REQUEST (branch, caps, runner), VALIDATION
(Python-only тесты обвязки, проверка неизменности std-патча и Kani source по хешам), RESULT-template.
Commit в g0 с `[skip ci]`, без push. Kani CI-only commit — локально, без push.
Завершить строкой `READY <kani overlay sha> <g0 sha>`. При невозможности сохранить пакет без изменения std-патча
или Kani source — STOP с точной причиной.
