# S1-07 — локальный control-кандидат

Control `9208b373c0a08a265fa0d7493a6529e331065271` (tree `b6354b703d67f7aac03742b10d8c175a8eb43d24`), parent `b25dd39a46ba90b167500997d546a5f2f5bd8f3b`.
Worktree `/root/kani-ch8-s1-07-w13`; author Tiramisu-Cake <igkharin@gmail.com>, `[skip ci]`.

Std `5be85699b8826e3286c0bf89efb9affefac0acb5`, tool `0aac16ef62da9e9d5645782d458593e5d78143ba`; 35 roots / 14 groups,
исходные cfg/domain/unwind/checks/negative oracles/companions без изменений.
Полный запрос — CI-REQUEST.json; embedded request hash — control_candidate.embedded_request_sha256.

После остановки/reap child fixed kani-driver/kani-compiler/CBMC снимаются в finally до
export/rich validation. Original exit/exception сохраняются отдельно от snapshot_errors;
ошибка одного hash сохраняет остальные. Missing/drift/error оставляют UNKNOWN.
Source-after и variant cleanup сохранены. Collector повторно проверяет snapshots.

Location-only исключение: ровно два exact ID и известные 18 row/variant наблюдений,
class unreachable, description `unreachable code`, SUCCESS, исходный display
`library/core/src/lib.rs:0:0 in function ...`. Nullable file/line не восстанавливаются;
полная запись исключения сохраняется в properties и group receipt, collector пересверяет её.
Admission остаётся за offline w11, proof credit NONE.

Control shallow depth 4 соответствует цепочке S1-07 → b25 → 40b → 0aac;
export/tool depth 2. YAML/preflight проверяют это, workflow включает test_s107.py.

Только подготовка: push/CI/публикации/ledger не разрешены и не выполнялись.
Следующий прогон требует отдельной авторизации и полного compatible same-run пакета;
исторические after-измерения не восстановлены. Доступные native metadata и явные UNKNOWN gaps — HANDOFF.md.


Metadata по списку w11 сохранены в пределах возможностей pinned producer:
exact native kani-metadata JSON, group/row/selector/crate keys, input/config/variant/binary
и export/rich/compile manifest (SHA256/bytes), оригинальные attributes/contract/placeholder
и rich properties. Invocation UUID и свежий target-dir не заменяют compiler-instance ID.
DefPathHash, substitutions/selected impl, clause/expansion/call edges и property→MIR
producer0aac в этих JSON не выдаёт; эти bindings остаются UNKNOWN для offline w11.
Список и его digest — W11-MISSING-FOR-S1-07.md / binding_metadata_requirements_sha256.
