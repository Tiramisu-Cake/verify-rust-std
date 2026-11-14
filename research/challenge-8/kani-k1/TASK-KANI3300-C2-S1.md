# KANI3300 C2-S1 — перенос принятого экспорта на upstream snapshot + B1

2026-11-14. Worker14, одна стадия. Это верификация корректности, не security-работа.
Подготовлено для выдачи координатором; сейчас не исполнять. После выдачи — isolated clone `/root/kani-fix-3300-c2-s1`,
ветка `fix/kani-3300-c2-s1`. Existing destination/dirty input → STOP без reset/stash. Source clones/PR ветки не менять.
Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены; Cloud $0, fork CI/push/dispatch — координатор.

## Exact входы

- Upstream U `0aac16ef62da9e9d5645782d458593e5d78143ba`, не плавающий main.
- B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012`, sole parent U; read-only `/root/kani-fix-b1-upstream`.
- Переносимый C1b `3f2c12f46e9e32899e8d84e89c65cb6483ba685a`, tree `e629978d8f0746bddf896d58a156bad2c59f14ce`,
  read-only `/root/kani-fix-3300-c1b`; original base `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`.
- Аудит R4 @`f8c3266934` F4; PLAN-KANI3300-C2.md; latest B1 source status из координаторского handoff.
  B1 по TODO подан как kani#5172, не считать его автоматически merged. Никаких изменений его public head.
Если до выдачи upstream/B1 изменились, координатор задаёт новый exact dependency pin и соответствие; worker сам не движет baseline.

## Результат этой стадии

Новый локальный C2-S1 candidate — descendant принятого B1 pin поверх U с остальной accepted C1b delta.
Нельзя просто слепо cherry-pick старый `cdb439b0a4`: B1 уже перебазирован на U, должен быть один coherent implementation
и один набор его fixtures. Сопоставить old B1/B1I-A и current B1 по production behaviour/tests, не только commit IDs.
Выбрать механический перенос (3-way patch/rebase) с явным conflict map; не переносить CI-only/research commits.
Сохранить accepted masks/runtime/A3/M1/E2/S3/CC/E1/M3 behaviour; F5–F8 этой стадией не чинить.
База12-bit heavy tests сохраняется, std/tool pins не менять. C1/C1b refs и старые receipts неизменны.

## Обязательное согласование конфликтов upstream

| Upstream изменение | Что должно остаться в новом source |
|---|---|
| `3e095c22a` / #5115 | AtomicStore выведен из check-only группы; nonvolatile сохраняет прежний pre-check, после store стоит setter true; volatile без лишнего pre-read |
| `7f89576f8` / #5152 | Source MIR body lookups через `checked_body`, в points-to, delayed targets/entry и BodyTransformation::body_ref; явные tail-call diagnostics не паника/unsafe unwrap |
| `2ec6953d9` / #5093 | Исправленные clause-depth helpers без возвращения saturating-method вызовов; Part1 не восстанавливает старые warnings |
| `0aac16ef6` / #5154 | Все новые upstream JSON tests и актуальный validator сохраняются; наши3 suites пока отдельно, S5 позже удалит только их |
| `28ef0488f` / #5138 | Актуальная upstream CI platform matrix сохраняется в export, не C1b macos-14 policy |

Для #5152 различать source lookup и уже выбранное override body: сохранять Registration/Discarded provenance и actual selected body,
не заменить contract trampoline на source panic body. B1 guarded no-body path оставляет accumulated operand checks/loads/Unsupported;
существующий guarded return допустим только при сохранённом explicit boundary, не как новый обход нужных effects.
CC1 cycle Err остаётся per-root без partial graph joins.
Все новые source-body запросы и imported overrides проверить на согласованность с checked_body и existing diagnostics.
Не подавлять компиляционные ошибки широким unwrap/default или выбором более старого тела.

## Статика и CI-request, не запуск

Передавать `INPUTS.json`: SHA/tree U/B1/C1b/candidate, actual diff map/parents, unchanged toolchain/dependencies/runtime hashes,
перечень разрешённых семантических отличий (именно upstream integrations). Проверить Rust operand types/casts/imports,
сигнатуры checked_body/Option/Result, match exhaustiveness; static review не заменяет compiler/typecheck.
`git diff --check`, duplicate-B1/fixture inventory audit; никаких авторских goldens по неисполненным результатам.

CI-REQUEST координатору: fmt/build/clippy и existing targeted Uninit/expected/ui/script, AtomicStore/volatile initialization controls,
explicit-tail-call boundary controls upstream, B1 plain/seeded pending operations, S3 ordinary/PFC/closure/cycle controls,
затем existing Linux Quick с unchanged heavy12-bit flags. В S1 не обещать нового3-platform full gate, он после полного C2.
Старые JSON inventories могут дрейфовать при переносе; такой сбой точно локализовать/передать в S5, не auto-bless и не
добавлять новые host/path normalization обходы. Другой semantic regression — STOP с source/harness/property map.
Никаких новых blanket Unsupported для fn-item, Cell<MU>, aggregates или function pointers сверх принятого поведения.

## Handoff и граница

Write scope после выдачи — isolated source port и research `kani3300/c2-s1/`; не worker15 Gate B′/SEL1 overlays и не исходные клоны.
Research: INPUTS, PORT-MAP, B1-EQUIVALENCE, UPSTREAM-CONFLICTS, REVIEW, CI-REQUEST, RESULT с раздельным static/NOT_RUN статусом.
Нейтральный local source commit(s), author/committer Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без source push.
Сохранить lineage/dependency metadata для последующей upstream нарезки; не переносить внутренний процессный текст в export.
Завершить `READY <local C2-S1 sha>`. Координатор принимает port и передаёт exact SHA worker15 как допустимую базу SEL1
после Gate B′; worker14 не начинает S2/F5 автоматически в этой сессии. Ничего не объявлять C2 release-ready.
