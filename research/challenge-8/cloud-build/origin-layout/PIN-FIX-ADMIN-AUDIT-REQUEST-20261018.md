# Запрос отдельного административного аудита — новый pin-fix Build

Build `42b71cd8-7cfa-46ea-a6a6-502ed49f5b25`, owner merge.
Это запрос разрешения, не выполненный audit. Старое разрешение только для a7ad5ce8
на этот Build не переносится. Обычный workflow остаётся Brief-only.

Brief получен через smallsort-brief после terminal FAILURE. Он сообщает
VERIFIED_ARCHIVE_AND_INVENTORY, source run exit1, source evidence_complete=True,
148 verified inventory files,112text entries/chunks, remote chunk bytes unchecked.
Diagnostic status UNKNOWN/causality UNKNOWN,
NO_SUPPORTED_VERIFIED_FAILURE_DIAGNOSTIC; campaign aggregates отсутствуют.
Есть только заголовок allprooflogs/cases/selected-drop-minimal без verdict/stages.
Нельзя выводить прохождение provider validation, запуск toolchain или результат
какого-либо proof/control из этих полей, размера evidence или длительности.

## Недостающая ограниченная выборка

Разрешить отдельную service-side обработку только этого Build, <=16KiB отчёта,
без downloads полных logs/archives на VPS, без IAM/credential/reporting/coordinator
изменений. Нужны:

1. Последняя явно завершённая стадия и первая подтверждённо отказавшая команда,
   точные argv без секретов, её собственный exit status. До30 relevant строк
   диагностического контекста, file/line/source SHA256/URI. Причинность отдельно
   от первого наблюдаемого error.
2. Явные start/completion/exit receipts для provider validation, source preparation,
   tool build (exporter/decoder/translator/console/refiner), extraction, exporter,
   decoder, official refiner и verifier. Где подтверждения нет — UNKNOWN.
3. Краткий результат selected-drop-minimal и mandatory B1/helper/ordinary normal-
   unwind/admission/receiver/end/retirement/default-off gates. Уточнить, был ли
   допущен first-callback campaign; source-linked prefix/full-body и controls:
   concrete-u64 FnMut/HRTB, CURRENT false/true/first-panic resources, official
   first-Continue comparison/mutant, resource-loss/HRTB/binder/late-Cleanup controls.
   Сохранить исходные classifiers и отличать skipped/setup/intended-negative.
4. Объяснить отсутствие aggregate в Brief: файл не создан, не упакован или
   не распознан processor. Сопоставить bounded relevant inventory paths, source
   collector records и processor selection; не угадывать по пустому разделу.
5. Provenance: Build/proof/infra/tool/profile identities, версия обработчика,
   source hashes/line links. Pinned и фактически executed identities раздельно.

Proof=infra `c405641217d9b440b03ff74836a1d05983f82c3e`.
Tool `d928cb1d7ac60c257daa537fa65577f41135f832`.
Profile experimental-merge-first-callback-u64-v1, SHA256
`300fd8a7172c1644552b43c5bfda51a7c8a620f505012abd3760772df55102e3`.
Config `78b4e468f335fe8fa3601415778b8595b05ab4b3ed35755068a449f7a964eece`.
Source payload `7b2a788288a304321668f7ba88aab99117a5039cf5329cd78d8bbb8dbbc75c0b`.
[Build console](https://console.cloud.google.com/cloud-build/builds/42b71cd8-7cfa-46ea-a6a6-502ed49f5b25?project=smallsort-ci).
Evidence source prefix:
`gs://smallsort-ci-evidence-504462351565/cloud-build/42b71cd8-7cfa-46ea-a6a6-502ed49f5b25/`.

Новых Builds/retry нет. Счёт333/960,627retired; прежний103/960,857retired сохранён.
Нового normal/unwind/B1/B2 proof credit нет. B2 остаётся открытым.
