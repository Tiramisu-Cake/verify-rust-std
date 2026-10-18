# Отдельный bounded admin audit запрашивается — e3252f3a

Build `e3252f3a-1034-405e-bc15-d406b79f20ed`, owner merge, terminal FAILURE.
Это запрос разрешения, не выполненный audit. Только smallsort-brief использован
для результата нового CI. Raw archives/logs/Cloud Logging не читались.

## Что Brief уже сообщает

Integrity VERIFIED_ARCHIVE_AND_INVENTORY. Source claims: runexit1,
evidence_complete=True, compiler_classification=PASS, proof_attempted=True.
Stage observations:24EXIT_NONZERO/72UNKNOWN,250candidates/96parsed/154notcaptured/
32omitted; orderNOT_ESTABLISHED,lastcompletedUNKNOWN. Показаны только4nonzero
stage receipts, включая expected negative controls, не первая причинная ошибка.
Aggregate selected-drop-minimal и checked-minimal-bridge INCONCLUSIVE/acceptedFalse;
combined-profile-smoke сообщает1casePASS. Три helper negatives и after_natural_drop_false
имеют source-classified expected rejections с location/error. Это не B2 acceptance.

## Недостающие сведения — ограниченный отчёт <=16KiB

Разрешить административную обработку только этого UUID через существующий backend:

1. Exact candidate tool/profile identity из execution/source-build receipts.
   `allprooflogs/tracked-md-build/compile-preflight.json` (если есть) и paired
   `translator-build-exit-code.txt`: успешна ли конкретно translator-build,
   какие exact sources/binaries связаны с ней? Отдельно подтвердить/опровергнуть
   прежний NON_GENERALIZABLE_TYPE_VARIABLES для нового кандидата. Вернуть только
   необходимые поля manifest/exit/identity, hashes и source links.
2. Последняя явно завершённая стадия и первая причинная failing command/classifier,
   её exit/expected-vs-observed gate. До30 relevant строк с file/line/hash/URI.
   Не считать намеренный false/resource/admission negative причиной Build FAILURE.
3. Компактные retained B1/helper/ordinary normal-unwind/generated admission/
   default-off/receiver/end/retirement результаты: expected/observed и all_matched.
   Для aggregate с UNKNOWN7 вернуть исходные классификации и конкретный unmatched
   gate; UNKNOWN в processor не подменяет source verdict.
4. Достигнут ли первый actual-comparator campaign? Concrete-u64 FnMut/HRTB,
   normalfalse/normaltrue CURRENT recovery, first Continue-panic resources,
   prefix cut/fullbody separately, official first-unwind mutant/resource/HRTB/
   binder/late-Cleanup controls: original classifications/stage receipts или
   явное отсутствие evidence. NOT_RUN только с подтверждением prerequisite/skip.
5. Coverage: почему translator receipt/154stage records/32omitted records и другие
   captured aggregates не представлены в Brief? Только relevant bounded paths и
   processor limits, без новой reporting системы/deployment и без изменения
   historical verdicts. Если это parser defect, вернуть минимальный synthetic
   reproducer и требования к корректному отображению zero/missing/classifications.

Proof=infra `59a3dcaed3f3061a551fec00fd0c503a52043405`.
Tool `52ba7e2506af993007675269111a24d15406d58b` (локальная назначенная ветка;
exact source delta передан existing14patch source closure отf76012fb).
Profile label experimental-merge-first-callback-u64-v1; exact SHA256
`84949dd9b08e6eb867b9f17b3d2149dcd41b44f219bcc369e2970bf5eca90a3f`.
Combined patch `df08af37966ef28a9667dd8b50e45afa2e14ecf9d716e78765e2233820a64bd3`.
Config `aee43b1416190a52b317cf8b63c1a185cc68a72a25c7078877cbdbad50dbed36`.
Payload `4c97ad4450ff8098bba53b429bbfd46c187d29b2ec567429b736209bb22f26e0`.
[Build console](https://console.cloud.google.com/cloud-build/builds/e3252f3a-1034-405e-bc15-d406b79f20ed?project=smallsort-ci).
Source prefix:
`gs://smallsort-ci-evidence-504462351565/cloud-build/e3252f3a-1034-405e-bc15-d406b79f20ed/`.

Не менять IAM/credentials/coordinator/production reporting. Не скачивать полные
archives/logs на VPS. Сохранить исходные Brief и classifiers/ledger/pins.
Счёт567/960 CLOSED,393retired; повторный Build в сессии запрещён.
Единственный следующий шаг — разрешить и получить эту bounded выборку;
не расширять tool patch или proof semantics по догадкам.
