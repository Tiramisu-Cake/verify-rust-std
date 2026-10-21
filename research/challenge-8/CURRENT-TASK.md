# Merge-R13 — допустимый размер архива → Brief → повтор R11

## Авторизация и рабочее место

- **ID:** `merge-archive-size-upload-recovery-2026-10-21-r13`; **статус:** RUNNING, T0 `2026-10-21T12:10:26Z`.
- **Owner:** `merge`; **project worktree:** `/root/verify-rust-std-merge-origin`; **branch:** `merge/incoming-origin-20261009`; **репозиторий:** `Tiramisu-Cake/verify-rust-std`.
- **Tool worktree:** `/root/verifast-merge-actual-glue`; branch `merge/actual-glue-instance-20261011`, expected head **`660b576b6b1608db913c51e0785b443a8733396f`**. Tool/model/spec/invariant этим заданием не меняются.
- **Новое окно:** 120 минут основной работы + до30 минут завершения. T0 при фактическом старте после чтения; main=T0+120мин, absolute=T0+150мин. Запиши в session, новый ledger и текущий статус.
- **Новый бюджет:** **3600 Cloud-секунд**, used0/carry0, без отдельного лимита числа последовательных Builds. Закрытые R12/R11/retry счета не возобновлять и остатки не переносить.
- **Phase:** `MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21`; **ledger:** `cloud-build/origin-layout/CURRENT-RECOVERY-R13-UPLOAD-BUDGET-20261021.json`.
- **Bounds:** ceiling_build_seconds=3600, max_builds=null, max_timeout_seconds=1200, carryover_allowed=false. **Lane:** существующая `merge`; timeout90..1200с, envelope=timeout+60 в остатке и absolute с запасом на package/upload/verdict.

**Разрешены исправление размера synthetic probe и pre-upload size guard, отдельный Cloud probe, затем только после доступного Brief/integrity gate повтор неизменённого proof-кандидата R11.** Сам обнови branch-local phase/ledger/mode/generator/dispatcher/recipe и dependent pins с review. Каждый fix/Build/SHA в scope отдельно не согласовывать. Shared live coordinator/старые phase restrictions, IAM/аккаунты/bucket policy/SDK image/backend и лимит обработчика не менять. Новая разработка proof-кандидата не входит в R13.

Ты начинаешь без контекста. Проверь обе worktrees/branch/HEAD/dirty diff, сохрани чужое. Прочитай `AGENTS.md`, [STATUS](STATUS.md), [автономность](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), нужные части [Cloud runbook](cloud-build/README.md), [WORK-POLICY](WORK-POLICY.md) и [Evidence guide](EVIDENCE-READER-GUIDE.md). Всю историю не перечитывай.

## Baseline и новые факты от владельца

Checkpoint **`72981ed1ce289397371e2f10f3bbdd6d5be456e3`**; последний synthetic actual source **`1e33bd24e37d11cf4de4c2163be3925a6be0fbea`**, Build **`68d2fe9c-bb4b-494e-844d-1a779d8d9f41`**. R12 CLOSED: **109charged/108execution/3491retired/remaining0/carryfalse**, own active/unresolved/requests/reservations0; proof retry не запускался. [Точный архив R12](task-history/merge-noncomposite-upload-recovery-2026-10-21-r12.md), [probe result](cloud-build/origin-layout/R12-PROBE1-RESULT-20261021.json), [release](cloud-build/origin-layout/R12-RELEASE-20261021.json).

R12 уже внедрила export `CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False` внутри package-upload, fail-closed effective-policy check и финальный marker. Все3 Cloud steps SUCCESS; Reader вернул HTTP404/`report not found`, тогда как старый Select report доступен. Не повторяй расследование общей авторизации/маршрута без нового факта.

**Новая административная информация, переданная владельцем для Build68d2fe9c:**

| Поле | Значение |
| --- | --- |
| Финальный marker | Есть, создан `2026-10-21T11:17:34.761Z` |
| uploaded / prerequisite_uploader_exit_code | true /0 |
| Фактический compressed archive bytes | **537691281** |
| Лимит архива в проверенном коде обработчика | **536870912 bytes (512MiB)** |
| Превышение | **820369 bytes** |
| Отчёт v8 | Отсутствует |

В проверенном обработчике превышение вызывает `archive too large`, `NOT_PUBLISHED_INVALID_EVIDENCE`/HTTP422 без публикации Brief. Получение события и фактическая первичная production-ошибка **не подтверждены**. Не утверждай, что production trace уже прочитан. Нарушение размерного контракта самим комплектом установлено и достаточно для исправления probe. Запиши уточнение как новый owner/admin report; historical UNKNOWN/результаты R12 не переписывать. Raw audit этим не разрешён.

Причина дефекта probe: **536870912 bytes выделили под payload, хотя лимит относится ко всему готовому compressed archive**, включая остальные файлы и overhead. Source transport569696bytes/191parts — другой архив и другой лимит, не смешивать их.

## Реализация и gate

1. **Synthetic payload — 268435456 bytes (256MiB)** несжимаемых данных в Cloud. Обнови согласованно generator constants/defaults, mode card, строгие dispatcher validators, registration/profile/pins, manifest/size-contract fields и затронутые tests. В R12 число512MiB зафиксировано в нескольких местах; правка одной card даст ранний отказ. Historical R12 schema/records не restamp; новый режим явно связан с R13. Не уменьшай архив до tiny/compressible, не заменяй реальный upload локальным test.
2. **До uploads проверяй фактический размер готового `evidence.tar.gz`.** Верхний предел **536870912 bytes** относится ко всем R13 publication modes, включая normal proof retry. Для synthetic gate дополнительно требуется `effective_composite_threshold < actual_archive_bytes <= 536870912`; documented threshold157286400bytes, effective SDK value проверить отдельно. Для обычного proof нижней границы нет. Payload size/сумма исходных файлов/оценка не заменяют stat готового compressed archive. Guard должен находиться после packaging и до первой storage upload, сохранить nonzero и компактные actual/limit/threshold/source/Build поля при отказе. Oversized комплект не публиковать как complete, upload.ok и обычный upload-complete marker при отказе не создавать. Не обрезать evidence и не исключать proof inputs ради fit.
3. **Используй уже исправленный uploader.** ExportFalse должен оставаться в фактическом package-upload до всех gcloud storage вызовов. Сохрани fail-closed effective-policy check, SDK/account `smallsort-builder@smallsort-ci.iam.gserviceaccount.com`, bucket/уникальный Build prefix, create-only `--if-generation-match=0`, исходные ошибки, upload receipt ordering и marker-last. IAM/storage.objects.get и лимит обработчика не расширять. При size refusal используй существующий error path с компактной диагностикой; backend-публикация отказов — отдельная задача, не повод менять сервис в R13.
4. **До Cloud — узкие service tests и review.** Проверь согласованность256MiB во всех новых producer/consumer местах; границы archive limit−1/limit/limit+1, нижний threshold только для synthetic, overhead, неправильные/missing/null metadata, отсутствие storage calls/complete marker при отказе, success/error/partial upload propagation. Локальные tests — малые synthetic данные либо stub stat, без генерации сотен MiB и proof pipeline. Review изменённого diff/dependencies — независимый **GPT-6 Luna HIGH** (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации/дорогой замены). Не повторяй review неизменённой proof-логики; synthetic GO не Cloud acceptance.
5. **Отдельный synthetic Cloud Build через coordinator.** Штатные packager/package-upload/verdict, pinned SDK/account, нет compiler/exporter/refiner/verifier/full preparer. `proof_attempted=false`, verification_accepted=false/credit0; diagnostic completion по собственному поддерживаемому критерию. После terminal получи Brief и адресные receipt/manifest/upload-policy fields, actual archive bytes/SHA/inventory identities. Gate требует и успешной публикации, и доступного Brief с целостностью этого exact run. R12 Cloud SUCCESS не заменяет новый gate. Если новый архив допустим, но Brief снова404, зафиксируй exact size/source/config/ответ и следующий недостающий факт; не повторяй неизменённый Build, не обходи интерфейс raw/GCS/Cloud Logging.
6. **После успешного gate — прежний R11 proof.** Последний actual proof source **`0c1d0d7861813bcc48d765eba869d30c2658f1cc`**, tool **`660b576b6b1608db913c51e0785b443a8733396f`**, profile `experimental-merge-label-storage-r11-v1` SHA256 `eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375`. [Frozen inputs](cloud-build/origin-layout/R11-RETRY-INPUTS-20261021.json). R12 проверила158 прежних normal-proof files byte-equal; сохрани их и baseline tool/model/std/spec/invariant/matrix/controls. Изменения только publication/size guard и необходимая authorization/mode wiring. Перед normal Build выключи synthetic mode и проверь exact cross-mode runtime/publication closure: разрешено менять card/ledger/docs, но gate не переносится на изменённые scripts/recipe. Впиши immutable receipts/pins нового gate; closed ledger не переделывать ради mode flip. Normal proof обязан пройти тот же archive cap. После terminal отчитай конкретный body result/первый отказ и отдельно full gates/credit; новый proof blocker не даёт права менять инструмент в этом задании.

Сохрани no-follow staging fix41c7c24c, все строгие hashes, старые матрицы и source correspondence. Source/config transport близок к пределу: полный token, caps и зависимую closure проверить до submit; не выкидывать runtime scripts/proof/controls и не повышать caps. Большие synthetic artifacts остаются только в Cloud, в Git — generator/config/tests/компактные receipts. Размер payload, evidence archive, source transport и Reader response имеют разные ограничения.

## Время, Evidence и отчёт

Каждый Build — exact reviewed/committed/published source/infra SHA с проверенным полным remote SHA, config digest и pinned closure; только существующий coordinator. Один occupied/unresolved Build на stable owner `merge`, максимум три project-wide. Refusals не обходить, uncertain submit не дублировать. При доступном времени продолжай разрешённые fixes; после успешного synthetic gate не завершайся до полезного normal retry, если тот помещается. Не трать остаток на Build без времени для target и публикации.

Через час — progress без ожидания ответа. Ожидание/status объединяй в шаги≤60с с yield10–30с, без пустого polling. После main новых Builds/retries/гипотез нет; до30мин finishing — начатое, Evidence, accounting, checkpoint/push. К absolute все terminal/accounted либо точные active/unresolved IDs и следующий разрешённый шаг. Остаток retire без carry; ранний stop обоснуй конкретным blocker после проверки независимых задач в этом scope.

Evidence v0.11: Brief → catalogue/file ID → `--refresh --file ID --expect-sha256 SHA` с info/locate/position/lines/JSON pointer; страницы только по server next_offset/next_value_start. [Guide](EVIDENCE-READER-GUIDE.md), [примеры](EVIDENCE-READER-TASK-QUERIES.md), `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md`. Старые16-квота/WITHHELD отменены; проверяй file/index/archive/request identities/exact/complete/coverage. No-match не NOT_RUN; integrity/exit0/source claims не independent proof. Raw/full logs/archives/Cloud Logging/локальные raw copies и download/storage/logging обход запрещены; не выставлять download_verified, не переписывать historical verdicts/ledgers. Новый admin audit отдельно.

VPS — Git/hashes/static parsing и малые isolated synthetic service tests; большие данные и реальный pipeline только Cloud. Не менять proof/model/runtime std/generic signatures/normal-unwind-abort/resources/checks или backend. Чужие worktrees/pins/shared live state/IAM/triggers/SDK/Actions/внешние комментарии не трогать. Полномочия R13 — publication recovery, не новая allocation premise/разработка proof.

Обновляй компактный STATUS и session/release/evidence records. В этом файле **один перезаписываемый отчёт**: T0/deadlines/end; commits/Build UUID/config; гипотеза/type/результат/charge; actual payload/archive/limit/threshold bytes; publication/Brief gate; normal proof result отдельно; own active/unresolved/requests/reservations; spent/retired/carry; следующий blocker. История отдельно. **Full target gates0, acceptedfalse/independentcredit0, B2/generic/qualificationOPEN**, пока новое применимое evidence не установлено; обслуживание не повышает готовность.

## Отчёт агента

T0 `2026-10-21T12:10:26Z`, main `14:10:26Z`, absolute `14:40:26Z`.
Fresh3600/used0/carryfalse; прежние R12/R11/retry CLOSED не возобновляются.
План: явно новый R13 producer256MiB + stat готового compressed archive до uploads;
service границы/metadata/error-path checks; independent Luna HIGH review;
отдельный syntheticCloud -> доступный Brief/inventory gate -> unchanged R11 normalretry.
Tool660b/profileeb61 и исходные158 normal-proof files сохраняются.
Builds0; fulltargetgates0/acceptedfalse/credit0/B2OPEN.
