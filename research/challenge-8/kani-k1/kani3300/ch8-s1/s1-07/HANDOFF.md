# S1-07 — runner finalization, без dispatch

Вход g0 `44ee751dcfe192f11133099f85cb65348f51c1b6`, control
`b25dd39a46ba90b167500997d546a5f2f5bd8f3b`. Локальный кандидат:
`9208b373c0a08a265fa0d7493a6529e331065271` в `/root/kani-ch8-s1-07-w13`.
Все результаты этой стадии — в данной папке. Исторические receipts/evidence/ledgers
не изменены; соседний accept-v2 принадлежит w11 и в этот пакет не включён.

Исправлены protected after snapshots до export/rich validation, независимое измерение
трёх required binaries, сохранение original execution exit/exception и отдельных
snapshot_errors. Ошибка monitor больше не обходит остановку/reap child. Rich records,
source-after и variant cleanup сохраняются при неуспехе. Missing/drift/error дают
UNKNOWN в runner и при collector replay. Версии из export отделены от измеренных hashes.

Location-only исключение согласовано в decoder/collector/group receipt: ровно два
exact ID, 17 selectors / 18 row/variant наблюдений из S1-06, unreachable / SUCCESS /
`unreachable code` / original display `library/core/src/lib.rs:0:0 in function ...`.
file/line остаются null. Иные nullable sites и изменённые поля fail-closed; полный
inventory/checks сохраняются. Само исключение не даёт admission или proof credit.

Сохранённое S1-06 inventory пересверено read-only: 9986 properties / 14 groups,
18 exact исключений. Это проверка decoder и inventory, не восстановление отсутствующих
исторических after-измерений. Отчёт — LOCATION-REPLAY.json; повтор:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/s1-07/replay_s106_locations.py
```

59 Python synthetic/service tests PASS после исправления P2; целевые metadata tests входят в эту полную проверку. Native YAML, frozen source/control/payload
pins и реальный shallow clone кандидата PASS. Control depth увеличен до4 для точной
цепочки S1-07 → b25 →40b →0aac, export/tool depth2; workflow включает test_s107.py.
Это не изменение proof domain, std/tool, 35 roots /14 groups, checks, cfg, unwind,
negative oracles или companions. Подробности — VALIDATION.json и PREFLIGHT.json.

Список w11 появился до завершения стадии и учтён: копия
W11-MISSING-FOR-S1-07.md, SHA256 закреплён в CI-REQUEST. `binding_metadata.py`
сохраняет bounded exact native `*.kani-metadata.json` (8 MiB /64 files), attrs/contract,
exact harness selector/crate refs и manifest export/rich/compile (SHA256/bytes).
Group/row/variant остаются частью ключа; originals/placeholders не заменяются.
Manifest содержит source/tool/config/variant/binary/request identities, effective cfg,
argv, original exit/exception. Capture выполняется и при отказе rich validation.
Свежий per-invocation CARGO_TARGET_DIR исключает захват stale metadata соседней группы.
Partial/invalid-UTF8 export сохраняется в compact artifact вместе с последующими
rich/receipts/metadata, но artifact остаётся INCOMPLETE. Missing/nonunique exact native selector/crate records и capture errors дают UNKNOWN,
не подменяя original failure. Required/missing binaries, phase и completion snapshot
сохраняются явно.

**Незакрытые поля:** pinned producer0aac в native KaniMetadata/HarnessMetadata не выдаёт
compiler compilation ID/DefPathHash/crate disambiguator, substituted instances/selected impl,
effective clause/expansion spans/call edges либо property→MIR origin. Эти поля помечены
UNKNOWN_NOT_EXPORTED_BY_PINNED_PRODUCER; native mangled wrapper и UUID не считаются
доказательством связей. UUID — только runner invocation, не compiler instance. Tool/std
не менялись. Для получения этих полей понадобится отдельно подготовленный exporter/tool
patch в последующей стадии; данный пакет не обещает закрытия w11 admission. Static
producer paths: kani_metadata/src/{lib,harness}.rs, kani-driver/src/{call_cargo,project,session}.rs.
Native JSON остаются после verify-std, сохранение не требует keep-temps или новых proof flags.

Независимый review Luna High — REVIEW.json; статус и exact candidate — VALIDATION.json.
CI-REQUEST.json/md описывают локальный пакет, а не разрешение запускать CI.
Qualified acceptance PENDING_OFFLINE_W11, proof credit NONE; B1/B2 credit не получен.
Ни push, ни CI, ни публикации, ни ledger, ни локальные cargo/rustc/Kani/CBMC не выполнялись;
полные raw verifier logs не читались. Следующий шаг — w11 offline gates и отдельная
авторизация полного compatible same-run S1-07; смешивать запуски или считать старые
after-снимки восстановленными нельзя.


Принятый review finding P2 на candidate723 исправлен: отсутствие native record больше
не даёт COMPLETE. Collector заново выводит exact native refs из сохранённых bytes,
проверяет их SHA/bytes и требует ровно одну запись на selected row/crate. Invalid UTF-8
native payload сохраняется base64 с исходными SHA/bytes и оставляет группу UNKNOWN.
