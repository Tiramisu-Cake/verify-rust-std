# PROF-OFF-02 — offline intake

Одна стадия выполнена от g0 `be5b5a17f8b87978778589684efa055f62d87967`.
Дефект runner исправлен; verdict Kani и acceptance разделены. Proof credit NONE.

## Exact evidence и уточнение вводных

Run `43784551069`, attempt 1, sibling `075750ca90a65792e2489041d071ba9dbb5cebdb`;
artifact `14190662926`, `ch8-prof-off-43784551069-1`.
ZIP в `/tmp/ch8-prof-off-intake-w11/artifact.zip`, вне репозиториев;
SHA256 `6b1f8ed210d93aae32b3e512565df7d6726d43660c19cb3c614f612f6b1a15e9`
совпадает с GitHub artifact digest. Читались только JSON members; logs не читались.
GitHub run conclusion: failure. Исходные receipts сохранены без изменений.

Control `741b7183b4d6e9d752c0b7951206d7257f69f951` и sibling имеют одну tree
`452b26330b97fc9b9816c28c64240bd667b2d4c0` и stock parent `0aac16ef62da9e9d5645782d458593e5d78143ba`.
SHA исходного CI-REQUEST совпадает с `job-status.json`; оба export SHA совпадают с group/row receipts.
Source и binary snapshots before/after согласованы в receipts. Это source-reported provenance,
а не независимое исполнение toolchain или доказательство связи AST/MIR/ADT.

Утверждение «все 62 UNKNOWN и SOURCE_STAGE_TARGET_MISMATCH» не подтверждается ZIP:
33 mismatch, 20 INCOMPLETE_CHECK_INVENTORY, 9 VALIDATED_OBSERVATION/EXPECTED.
Оригинальный классификатор точно воспроизвёл все 62 сохранённых export snapshots.

## Причина и исправление

Сравнение `endswith("::" + expected)` не учитывало формат Rust TokenStream:
`super :: merge :: profiles :: swap_profile` и `profiles :: merge_profile`.
Три concrete forwarder используют локальные `stable_cell`, `unstable_byte`, `freeze_noncopy` без `::`;
ещё две PFC строки используют bare `swap_if_less` (safety leaf и frame negative).
Все 33 mismatch объясняются этим дефектом: 28 spaced paths и 5 bare targets;
расхождений source file / stage / target triple / unwind не найдено.
Например, pinned `network.rs:928` задаёт `proof_for_contract(super::merge::profiles::swap_profile)`;
`swap_contract_u8_n2` экспортирует тот же path с пробелами, unwind 180.
Pinned `forwarding_contracts.rs:144` задаёт `proof_for_contract(stable_cell)`, unwind 16.

Фикс принимает корректный ASCII Rust identifier path с пробелами вокруг `::` и сравнивает terminal identifier.
Идентификаторы не склеиваются; null, wrong type, malformed и wrong-target forms отклоняются.
Это проверка profile stage; независимое разрешение qualified path и mangled contract wrapper остаётся PENDING.
Frozen paths здесь nongeneric; более широкий синтаксис не заявлен.
File normalization уже принимала relative/absolute suffix и `\\`→`/`; менять её не потребовалось.
Target `x86_64-unknown-linux-gnu`, mode/contract и resolved unwind соответствуют строкам manifest.
Oracles, inventory/cover/consumer gates, cfg, pins, budgets и caps не менялись.

## Verdict Kani и acceptance

| Группа | Kani verdict | Checks | Covers | Compile |
|---|---|---|---|---|
| group-00 | 53/53 SUCCESS | 19586 success + 1505 unreachable = 21091 | 179/179 SAT | 53.228 s |
| group-01 | 9/9 FAILURE | 2133 success + 11 failure + 205 unreachable = 2349 | 10/10 SAT | 33.197 s |

Undetermined/error/unknown/other checks отсутствуют в обеих группах.
`unsupported_constructs`: 180 и 25 записей соответственно, **все со статусом SUCCESS**.
Они не являются наблюдавшимися failing checks; неизменённый классификатор всё равно блокирует
любой непустой unsupported inventory и любой unreachable check.
Phase 1660.793 s, максимальный group RSS 4016648 KiB; per-row RSS UNKNOWN.
Original exits 0/1 относятся к группам, не отдельным строкам.

После binding fix: 53 INCOMPLETE_CHECK_INVENTORY/UNKNOWN и 9 VALIDATED_OBSERVATION/EXPECTED.
Все 62 Kani verdict соответствуют ожидаемому SUCCESS/DETECTED;
это не означает, что все acceptance gates пройдены.
EXPECTED: восемь relation rows (`lt_u8/i32/u64`, `strict_u8/u64`, `cell_i32`, `key_b16/b17`)
и `profile_bad_relation_rejected_u8`. Independent acceptance для всех PENDING; credit NONE.
Пять consumers остаются UNKNOWN/`matching_leaf_not_accepted`: их leaf не принят классификатором.
Проходить leaf gate по одному Kani SUCCESS запрещено действующим кодом.

Названные failures из exact export:

| Строка | Description |
|---|---|
| rejects_always_true | bad Freeze adapter relation rejected; bad unstable adapter relation rejected; bad stable adapter relation rejected |
| rejects_payload_corruption | full-value checker rejects payload corruption |
| rejects_swap_comparator_writing_outside_frame_u8 | Check that *var_9 is assignable |
| profile_full_value_checker_rejects_payload_change_u8 | full-value checker detects payload corruption |
| profile_wrong_f_swap_rejected_u8 | bad-profile swap transfer rejected |
| profile_wrong_f_sort4_rejected_u64 | bad-profile sort4 order rejected |
| profile_wrong_f_insert_rejected_u8 | bad-profile insert order rejected |
| profile_wrong_f_merge_rejected_u8 | bad-relation merge order rejected |
| profile_bad_relation_rejected_u8 | bad comparator-model relation rejected |

Все восемь concrete text oracles совпали без лишних failures.
Generated frame property имеет exact ID и description в RECLASSIFY.json, но manifest содержит placeholder:
независимый frame binding не установлен и oracle не заменён наблюдаемой строкой.
Остальные восемь negative rows остановлены inventory gate до admission named failures.
Каждая из 62 строк в RECLASSIFY.json содержит export member/SHA/index, binding полей,
raw verdict, oracle, check/unsupported inventory, covers, named failures и отдельный acceptance.

## Проверки и перенос

42 synthetic Python tests PASS, включая actual-format 62-row batch и сохранённые service error/timeout/partial/
missing/null/wrong-type/NOT_RUN/mismatch paths. Добавлены regression tests на spaced/local targets,
malformed identifiers и сохранение source/mode/target/unwind/inventory guards.
Payload hashes обновлены; manifest byte-identical. Независимый Luna HIGH review: GO для delta, без credit.

Общий принцип для S1/B/C: сравнивать Rust token paths с сохранением границ identifiers,
привязывать каждую строку к её exact harness entry, независимо проверять source/mode/triple/unwind.
Для full qualified source binding нормализовать обе стороны и сравнивать полный token path;
terminal-only profile check не заменяет такой binding. S1 batch уже имеет `_target_tokens` и полный source target check;
C pprime использует raw equality `exported_target != row["target"]`, поэтому переносить следует token equality,
сохраняя полный target и source checks. B ordinary-root census не требует PFC target matcher;
принцип нужен только при добавлении contract binding. Другие runners в этой стадии не изменялись.

Push/CI/публикаций/ledger/local cargo/rustc/Kani/CBMC: 0. Новые proof obligations этой стадией не закрыты.
