# B census на P′ — одна стадия, preparation only

Вход: g0 `1038c006f9616e88e4792b025bd877674c008def`,
`TASK-CH8-B-PPRIME-W14.md`. Control:
`4d7e34383a3af504a261228fdee59e6c7093e633`, parent stock Kani
`0aac16ef62da9e9d5645782d458593e5d78143ba`.
Worktree `/root/kani-ch8-b-pprime-w14`, branch `uninit-ci/ch8-b-pprime-w14`.
Полные tree/request/manifest identities: `CI-REQUEST.json`.

Std P′ `c5ff36ff433692140605891f646043f991db05de`, tree
`1302063846873aa300f8bac64fe09e8a3ed1280f`. Manifest `roots.json` побайтно
сохранён: 235 roots, historical shards 2=183 / 4=52. `root-audit.tsv` — явная
таблица старых/новых имён и source anchors: все совпадают. `SOURCE-AUDIT.json`
фиксирует SHA256 всех 16 файлов SmallSort (runtime/module map/fixtures): они
побайтно совпадают между 872d и P′. Это статическая source identity;
наблюдаемого compiler/AST/MIR binding здесь нет.

## Inventory и receipts

B runner не вызывает `kani list`, metrics/autoharness или `scripts/run-kani.sh`.
Единственный proof entry — прямой `verify-std ./library --harness SELECTOR --exact`
на каждый frozen root. Поэтому дефект глобального list из S1 здесь отсутствует.
Решение worker13 (`kani-host-list`, control `a18502a710...`) изучено;
перенос его list runner/1800s cap создал бы новую ненужную фазу и не применяется.
Фильтрация manual harnesses выполняется stock Kani в
`kani-compiler/src/kani_middle/codegen_units.rs::CodegenUnits::new` /
`determine_targets`; фактическая работоспособность на P′ остаётся NOT_RUN.

`census.py` отличается от предыдущего B control только константой STD.
Строгая классификация export, checks/covers, original exits, seeded NOT_RUN,
PARTIAL fallback, binary/source checks не менялись. Per-root 600s (включая
компиляцию) / 6GiB, две slots, verify stage 7200s, build 2100s, job210min
сохранены. Root receipts по-прежнему содержат exit/signal/exception,
elapsed/RSS и bounded 4096-byte diagnostic tail. Специальной list-фазы с её
head+tail receipt нет. Runner loss/SIGKILL может оставить seeded NOT_RUN;
это PARTIAL, а не доказанный результат. Полнота всех 235 строк не обещана.

## Host и следующий шаг

Kani-host содержит только `.github/workflows/ch8-b-census.yml`; все прочие
upstream workflows удалены только в control. Отдельный checkout
`model-checking/kani@0aac...` используется для setup/build/verification;
compiler/model/runtime patches отсутствуют. Upload ограничен curated JSON,
target/raw logs не попадают в artifact. `control.patch` — полный пакет;
`control-delta.patch` — delta против старого B control `5ee153ec2b...`.

Synthetic tests: 13 PASS (все 12 прежних сохранены), static YAML/AST/identity
checks PASS, actionlint PASS, offline source/manifest validator PASS.
Независимый review: `REVIEW.md`, итоговые identities — `review-packet-final/`.
Первоначальный packet сохранён для истории; final candidate отличается от него
только удалением нового вызова offline static_check из CI, чтобы не вводить
runtime dependency на PyYAML.

Все 235 proof rows NOT_RUN, proof credit NONE. Никаких push/CI/publication,
ledger writes или локальных cargo/rustc/Kani/CBMC. Исторический B-01 не переписан.
Координатор отдельно сверяет текущие budgets/slots/ledger и review, публикует
пакет и после GO создаёт same-tree non-skip child на census branch; attempt=1.
Этот handoff не резервирует запуск и не выдаёт dispatch authorization.
