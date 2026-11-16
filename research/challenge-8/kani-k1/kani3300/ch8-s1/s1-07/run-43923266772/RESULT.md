# S1-07 intake — run 43923266772

**READY для офлайн-приёмки w11; qualified acceptance PENDING, proof credit NONE.**
Вход g0 `8a3db1ad2a09ac0f64f4e599ae7711a3c58c6d11`.
Run: <https://github.com/Tiramisu-Cake/kani/actions/runs/43923266772>, attempt1,
branch `uninit-ci/ch8-s1k-i`, 14/14 jobs success.

Исполнен control `b37f6f75c5b7b77e84297cd7104f9c0868502fd4`; подготовленный
`9208b373c0a08a265fa0d7493a6529e331065271` имеет тот же tree
`b6354b703d67f7aac03742b10d8c175a8eb43d24`.
Std `5be85699b8826e3286c0bf89efb9affefac0acb5`, tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`, embedded request SHA256
`6c483ce754cd8e99c01953bf4c40a145b10529d7990aa52c28ef32c00b980cd7`.
Source/tool trees, changed-file hashes, runner payload, variants и request сверены.

Скачаны 14 compact artifacts в `artifacts/`. SHA256 каждого ZIP совпал с GitHub
до извлечения; ZIP CRC проверен, сами ZIP не сохранены. Payload/member hashes и
bytes проверены повторно; download attestations — `zip-integrity.json`.
Это GitHub structured artifacts, не Cloud evidence и не raw logs.

35/35 строк OBSERVED/RECORDED; 27 source SUCCESS и 8 source FAILURE, совпадающих
с предобъявленным DETECTED. У всех восьми — exact sole-failure oracle и source
SUCCESS production companion из этого же run. Полные inventories: 9986 stock /
9986 rich properties; 413 UNREACHABLE checks, 113 satisfied covers, 2 UNREACHABLE
covers. Все четыре replacement unions содержат N0, N1, N2, N3 этого run;
это не domain-completeness или admission credit.

Ровно 18 location-only исключений / 2 exact ID, те же `(group,selector,ID,fields)`
из S1-06. Оригинальные `file=null`, `line=null`, `lib.rs:0:0` и SUCCESS сохранены;
streaming `missing_sites` не стёрты, все они соответствуют exact exceptions.
Проверка pinned S1-07 collector/decoder: 14/14 rich groups COMPLETE. Политика
не распространяется на иные missing sites и не устанавливает MIR origin.

В каждой группе три required binaries измерены BEFORE_CHILD и
AFTER_CHILD_SHUTDOWN, snapshot_completed=true, missing=[], snapshot_errors=[],
hashes совпадают. Shutdown child подтверждён; timeout/signal отсутствуют.
Сохранены 322 native `*.kani-metadata.json` (23/group), 2 462 185 исходных bytes,
их hashes и 35 unique exact selector/crate refs в 14 разных invocation namespaces.
Export/rich/compile manifest, argv, cfg, unwind, source/variant/binary identities
проверены. Native bytes доступны внутри `binding-metadata.json`, без домысливания
compiler-instance связей.

| Group | Child exit | Elapsed, s | Sampled group RSS, KiB |
|---|---:|---:|---:|
| activation-default-u34 | 1 | 37.026 | 1927636 |
| activation-override-u34 | 1 | 49.622 | 1932992 |
| cell-u34 | 0 | 783.046 | 8134972 |
| freeze_copy_u8-n01-u34 | 0 | 55.823 | 2615112 |
| freeze_copy_u8-n23-u34 | 0 | 102.937 | 2596792 |
| freeze_default_noncopy-n01-u34 | 0 | 50.348 | 2658580 |
| freeze_default_noncopy-n23-u34 | 0 | 326.610 | 2626820 |
| light-controls-u34 | 1 | 80.220 | 2304040 |
| light-corruption-u4 | 1 | 30.401 | 1944196 |
| light-model-u5 | 0 | 43.994 | 2628024 |
| stable_freeze_u8-n01-u34 | 0 | 50.327 | 2657676 |
| stable_freeze_u8-n23-u34 | 0 | 270.281 | 2599832 |
| unstable_freeze_u8-n01-u34 | 0 | 61.206 | 2670192 |
| unstable_freeze_u8-n23-u34 | 0 | 110.024 | 2424756 |

Child exit1 соответствует ожидаемым negatives; runner завершён успешно во всех
14 jobs. Runner exit0 отдельно отмечен как вывод из pinned runner/main и job-step
conclusion. Group elapsed включает compilation; per-harness verification_time
взято из stock export. Per-root process exit/wall/RSS и отдельный compile exit
не экспортированы: UNKNOWN, group RSS им не приписан.

**Отличия от S1-06 `43889560779`:**

- Verdicts 35/35, counts 9986/9986 и все rich records по exact ID/полям совпали;
  добавленных, удалённых или изменённых properties нет. Порядок rich records
  изменился в 17 строках, порядок stock checks/unsupported lists — в 13;
  после сравнения по ID/множествам различий нет. Exact deltas сохранены в
  `COMPARISON-S1-06.json`.
- Proof request rows/groups/unions/source bindings/flags/std/tool/variants
  не изменились. Изменены control parent, payload/workflow hashes, schema,
  добавлены snapshot/location/binding capture policies и requirements pin;
  все 8 изменённых top-level полей request перечислены с обоими значениями.
- Group/rich COMPLETE: 4 → 14. Исторически отсутствовавшие after fingerprints
  для 10 групп / 26 строк теперь есть у нового invocation. Старые receipts не
  изменены. Все измеренные binary hashes совпадают также с S1-06 before hashes.
- Group elapsed sum: 2109.139 → 2051.865 s; compilation upper-bound sum:
  507.628 → 472.642 s. Все per-row verification и per-group elapsed/RSS deltas
  сохранены. Эти измерения не дают performance/proof credit.
- Native metadata и same-invocation manifests теперь сохранены. Compilation ID,
  instance/substitution/selected-impl/contract-clause/expansion/property-MIR
  bindings всё ещё UNKNOWN_NOT_EXPORTED_BY_PINNED_PRODUCER.
- В group receipts добавлено явное `effective_cfg`; argv/selectors/unwind/variant
  прежние. В global stock export изменились только `started_at` и `wall_time_s`.
  Exact значения этих deltas находятся в `collected.json.groups[].s106_comparison`.

Вход w11 — `HANDOFF.md` и `W11-INPUTS.json`. Старые 111 assertion links / 21 root
и 187 unresolved UNREACHABLE checks остаются навигацией по baseline gaps;
интейк не выполняет новую семантическую приёмку. Source claims, integrity и
collector COMPLETE не являются independent B1/B2 proof.

Валидация: `intake.py`, `VALIDATION.json`, `PROVENANCE.json`, `MANIFEST.sha256`.
Новых CI/push/публикаций/ledger, локальных cargo/rustc/Kani/CBMC и чтения полных
raw logs не было. Изменены только результаты этого intake.
