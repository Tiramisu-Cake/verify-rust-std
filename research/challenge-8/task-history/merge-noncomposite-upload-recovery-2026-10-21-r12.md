# Merge-R12 — non-composite upload gate → повтор R11 кандидата

## Авторизация и рабочее место

- **ID:** `merge-noncomposite-upload-recovery-2026-10-21-r12`; **статус:** CLOSED_PARTIAL_BRIEF_GATE_BLOCKED, T0 `2026-10-21T10:53:30Z`.
- **Owner:** `merge`; **project worktree:** `/root/verify-rust-std-merge-origin`; **branch:** `merge/incoming-origin-20261009` в `Tiramisu-Cake/verify-rust-std`.
- **Tool worktree:** `/root/verifast-merge-actual-glue`; branch `merge/actual-glue-instance-20261011`, expected head **`660b576b6b1608db913c51e0785b443a8733396f`**. Проверить фактический status, чужое сохранить; tool-код этим заданием не меняется.
- **Новое окно:** 120 минут основной работы + до30 минут завершения. T0 при фактическом старте после чтения; main=T0+120мин, absolute=T0+150мин. Записать в session/новый ledger/текущий статус.
- **Свежий бюджет:** **3600 Cloud-секунд**, used0/carry0; без отдельного лимита числа последовательных Builds. После main новых Builds/retries/гипотез нет.
- **Phase:** `MERGE-UPLOAD-NONCOMPOSITE-R12-2026-10-21`; **новый ledger:** `cloud-build/origin-layout/CURRENT-RECOVERY-R12-UPLOAD-BUDGET-20261021.json`.
- **Ledger bounds:** ceiling_build_seconds=3600, max_builds=null, max_timeout_seconds=1200, carryover_allowed=false. **Lane:** существующая `merge`, coordinator/owner/slots прежние; timeout90..1200с, envelope=timeout+60 в остатке и окне. Сохрани измеримый reserve на package/upload/verdict.

**Это новая авторизация на узкое исправление публикации, отдельные синтетические Cloud upload probes и, только после успешного gate ниже, повтор неизменённого proof-кандидата R11.** Время и счёт R11/one-shot retry не возобновлять. Разрешены необходимые branch-local phase/profile/recipe/entry/service-test регистрации и узкая правка генератора `package-upload` в своей копии `cloud-build/control.py`. Не менять shared live coordinator, старые phase restrictions, IAM/аккаунты/bucket policy/SDK image. Новые proof-гипотезы и изменения tool/model/spec/invariants в scope R12 не входят.

Ты начинаешь без контекста. Проверь project/tool worktrees, branch/HEAD/dirty diff, сохрани чужие изменения. Прочитай `AGENTS.md`, [STATUS](STATUS.md), [автономность](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), нужные части [Cloud runbook](cloud-build/README.md), [WORK-POLICY](WORK-POLICY.md) и [Evidence guide](EVIDENCE-READER-GUIDE.md). Сам выбирай implementation и следующие полезные проверки внутри этой узкой цели; каждого fix/Build/SHA отдельно не согласовывать.

## Исходная точка и административный диагноз

Checkpoint **`ff1091005ee02906b0546179d59ea8e8f56aaca6`**. Последний actual source **`0c1d0d7861813bcc48d765eba869d30c2658f1cc`**, Build **`484a4382-ea4f-4e1f-b5e4-363de2c61927`**; expected tool **`660b576b6b1608db913c51e0785b443a8733396f`**, profile `experimental-merge-label-storage-r11-v1`, SHA256 `eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375`. Exact proof files/patches/pins — [retry inputs](cloud-build/origin-layout/R11-RETRY-INPUTS-20261021.json); [результат](cloud-build/origin-layout/R11-RETRY-RESULT-20261021.json), [staging fix](cloud-build/origin-layout/TOOL-EVIDENCE-STAGING-20261021.md).

R11 CLOSED3024charged/3019execution/576retired; отдельный retry CLOSED790charged/790execution/270retired; remaining0/carryfalse, own active/unresolved/requests/reservations0. Ни576, ни270 секунд не доступны вновь. [Точный архив прежнего задания с отчётом](task-history/merge-label-storage-invariant-autonomous-2026-10-21-r11.md).

**Владелец передал результат отдельного административного просмотра GCP** для Build484a4382:

> Упаковка прошла. Загрузка evidence.tar.gz отказала с HTTP403: автоматически включённый parallel composite upload запросил storage.objects.get для gcloud/tmp/parallel_composite_uploads/.... Отключить этот режим через CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False в шаге публикации. IAM не расширять. Сначала проверить загрузку отдельно на синтетическом архиве сопоставимого размера.

Переданные итоговые поля: **run_exit_code=1, upload_complete=false, verification_accepted=false, diagnostic_complete=false**. `evidence_complete=true` относится к локально собранному комплекту; публикация не завершена, proof acceptance не установлена. Это admin-reported evidence от владельца, не собственный raw audit агента. Нового разрешения читать raw/full logs или archives нет; исторические records с прежним UNKNOWN сохраняются, уточнение оформляется отдельной новой записью.

Read-only coordinator metadata: executeSUCCESS у оболочки; package-uploadFAILURE/exit1,09:25:09..09:29:43UTC; verdictFAILURE/exit1. Brief/catalogue404 — наблюдённая недоступность отчёта. `executeSUCCESS` не доказывает результат verifier; run_exit1 не устанавливает конкретный formal blocker. Последний доступный proof-фронтир — R11 Build5, iterationprep301/points_to_limits/dummy30none после checked Live/Dead117; initialized-value invariant кандидата ещё не получил доступного результата.

## Порядок работы и критерии принятия

1. **Узкая правка внутри Build.** Добавь в shell шага `package-upload` до всех gcloud storage загрузок:
   ```bash
   export CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False
   ```
   Это должно попасть в фактически отправленный Build config и его exact digest; настройка локального shell/Cloud Shell недостаточна. Сохрани SDK image, service account `smallsort-builder@smallsort-ci.iam.gserviceaccount.com`, bucket/prefix, `--if-generation-match=0`, исходные ошибки и последнюю публикацию `upload-complete.json`. Не добавляй `storage.objects.get`, роли, широкие retries, overwrite или иной обход.
2. **Service tests и независимый review до Cloud.** На synthetic config проверь наличие и действие export до первой и всех последующих uploads; защити receipt ordering и nonzero/upload failure. Проверь отсутствие зависимости от внешнего shell env. Используй существующие tests, добавляя лишь содержательные regressions изменённого поведения. Review текущего diff/dependencies — независимый **GPT-6 Luna HIGH** (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации/дорогой замены). Static/synthetic GO ещё не доказывает Cloud upload.
3. **Отдельный Cloud probe до proof.** В существующей lane реализуй минимальный явно bound `synthetic-upload` режим/profile, который не запускает compiler/exporter/refiner/verifier или full proof preparer. Сгенерируй синтетический архив с несжимаемым наполнением; размер сжатого архива должен быть сопоставим с проблемным и выше порога composite upload выбранного SDK. Если фактический размер недоступен через разрешённые metadata, выбери консервативный объём выше установленного порога с запасом, запиши bytes/порог/обоснование и ограничение сопоставимости. Не используй tiny/zero-filled compressible archive как доказательство устранения этого дефекта. Большие synthetic данные создавать в Cloud, в Git только generator/config/tests/компактный manifest.
4. **Проверяй тот же publication path.** Тот же SDK/account/config export, фактический `package-upload`, штатный packager, архив+inventory/SHA+metadata/text-index и финальный upload-complete marker; отдельный уникальный Build UUID/prefix, чужие/старые объекты не менять. Сохрани source/config identities, payload/archive bytes и SHA, uploader exit и stage timings. Это явно разрешённая публикация synthetic evidence из Build, не разрешение скачивать production evidence. `proof_attempted=false`, `verification_accepted=false`, proofcredit0; diagnostic/smoke status допустим только по поддерживаемому отдельному критерию, не подделывай proof acceptance ради зелёного verdict.
5. **Gate — actual publication плюс доступный Brief.** После terminal получить `smallsort-brief BUILD_UUID` и нужные bounded catalogue/manifest/receipt поля. Установить завершённую публикацию/целостность именно synthetic run, отделяя её от verification. Одна только локальная упаковка, exit execute0 или изменение env gate не закрывают. Если upload снова отказал либо Brief недоступен, сохранить точные metadata/ответ и ограничение, остановить только зависимый proof retry; не обходить интерфейс raw/GCS/download/logging. Продолжай разрешённые source/service fixes, но повторять неизменённый запуск без новой гипотезы нельзя.
6. **После успешного synthetic gate — повтор прежнего R11 proof.** В новом счёте и до main разрешён следующий useful Build с прежними tool/model/std/spec/invariant/matrix/control bytes из source0c1d0d78; изменения только в uploader, проверенной branch-local диагностической/authorization wiring и их pins. Отдельно зафиксировать proof-file hashes и доказать отсутствие semantic diff. Убедись, что synthetic mode выключен, normal merge graph/controls целиком сохранены и actual config содержит export. Не переносить synthetic PASS на proof. После terminal раздельно сообщить tool compile, конкретный verifier body result/точный отказ и полные gates/credit. Если publication исправна, proof FAILURE является полезным результатом диагностики, а не поводом снова чинить uploader. Дальнейшая разработка нового proof-кандидата остаётся следующим заданием.

Сохрани reviewed no-follow tool-staging fix41c7c24c, правильную tool/patch composition, все строгие hashes и controls. Source payload уже был189/191parts; новая registration/generator/tests closure должна проходить полный token/config/transport fit до dispatch. Не поднимать caps и не выкидывать proof inputs ради fit; historical prose исключается из runtime closure лишь с проверкой реальных dependencies. В готовом report указать реальные compressed archive bytes и скорость/время upload, не обещать ускорения без измерений.

## Исполнение и отчёт

Авторизация R12 предполагает branch-local регистрацию нового ledger/phase/режима с review; закрытые фазы и их записи не переписывать. Каждый Build через существующий coordinator, exact committed/published source/infra SHA с проверенным полным remote SHA, source closure/config digest. Один occupied/unresolved Build на stable owner `merge`, максимум три project-wide; refusals не обходить, uncertain submit не дублировать. Envelope timeout+60 должен помещаться в бюджет и absolute с запасом; не запускать proof без времени на cold compile/controls/package/upload/verdict.

Status/ожидание объединяй в шаги≤60с с yield10–30с, выполняй независимую полезную работу, не создавай модельные возвраты от пустого polling. Через час — progress без ожидания ответа. После main никаких новых Builds/retries/гипотез; finishing — начатое, Evidence, accounting, checkpoint/push. К absolute terminal/accounted либо точные active/unresolved IDs и следующий разрешённый шаг. Остаток retire без carry. Заверши после выполненного gate и разрешённого proof retry либо конкретного blocker, не заполняй окно лишними запусками.

Evidence v0.11: Brief → catalogue/file ID → `--refresh --file ID --expect-sha256 SHA` с info/locate/position/lines/JSON pointer; нужные страницы только по server next_offset/next_value_start. [Guide](EVIDENCE-READER-GUIDE.md), [примеры](EVIDENCE-READER-TASK-QUERIES.md), `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md`. Старые16-квота/WITHHELD отменены. Сохраняй file/index/archive/request identities, exact/complete/coverage. No-match не NOT_RUN; integrity/exit0/source claims не independent B1/B2 proof. Полные/raw logs/archives/Cloud Logging/локальные raw copies и download/storage/logging обход запрещены; не выставлять download_verified, не переписывать historical evidence/ledgers. Новый admin audit отдельно.

На VPS только чтение/правки/Git/hashes/static parsing и малые isolated synthetic service tests; реальный pipeline и крупный upload probe только Cloud. Не менять tool/model/runtime std/алгоритмы/generic signatures/normal-unwind-abort/resources/provenance/checks; никакой новой allocation premise. R8 narrow scope и прочие proof ограничения сохранены в исходном кандидате. Чужие worktrees/pins/IAM/shared coordinator/backend/Actions/внешние комментарии не трогать.

Обновляй компактный STATUS и session/release/evidence records по ссылкам. Здесь **один перезаписываемый отчёт**: T0/deadlines/end; exact commits/Build UUIDs/config; hypothesis/type/result/charge; synthetic bytes/порог/границы claim; actual package/upload/Brief gate; последующий proof result отдельно; own active/unresolved/requests/reservations; spent/retired/carry; следующий blocker. История отдельно, текущий файл не наращивать. **Full target gates0/acceptedfalse/independentcredit0/B2/qualificationOPEN**, пока не получено новое применимое evidence; обслуживание само по себе статус не повышает.

## Отчёт агента

**CLOSED_PARTIAL_BRIEF_GATE_BLOCKED.** T0 `2026-10-21T10:53:30Z`, main
`12:53:30Z`, absolute `13:23:30Z`; end/report `2026-10-21T11:27:21.342060Z`.
Счёт закрыт `2026-10-21T11:26:04.678822Z`: **109charged /108execution /3491retired
/remaining0 /carryfalse**, own active/unresolved/requests/reservations0.
Прежние R11/retry счета, T0, inputs и historical UNKNOWN сохранены; admin-reported
уточнение записано [отдельно](cloud-build/origin-layout/R12-OWNER-ADMIN-REPORT-20261021.json).

| Build / type / hypothesis | Exact inputs | Результат | charged / execution |
| --- | --- | --- | --- |
| `68d2fe9c-bb4b-494e-844d-1a779d8d9f41` / setup / отключить automatic composite upload на крупном synthetic archive | infra=proof `1e33bd24e37d11cf4de4c2163be3925a6be0fbea`, config `fd11a8ee39a0238d8c9d67e6857350beb77e66bdaeee617212097a925a40b621` | Cloud SUCCESS; mandatory Brief gate BLOCKED, proof retry не запущен | 109 /108 |

Create/start/finish: `11:15:48.871429551Z` / `11:15:49.627491780Z` /
`11:17:36.947706Z`; timeout600/envelope660, dispatch
`dispatch-d86995870fdd42abae8e252efa055cc4`. Remote fullSHA проверен до submit.
Coordinator metadata: execute/package-upload/verdict все SUCCESS; интервалы
31.644/72.066/1.007с соответственно. Package-upload завершён с успешным статусом
(явный API exitCode отсутствует, protobuf default0); это не независимая проверка архива.

**Реализовано и проверено:** export
`CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False` в начале фактического
package-upload, до всех gcloud вызовов. Effective SDK policy проверяется fail-closed;
SDK/account/bucket/create-only flags/ошибки/final-marker ordering сохранены, IAM не менялся.
Фактический digest config и export перепроверены. Synthetic route использует
штатный packager/upload/verdict; mode card исключает proof pipeline.

Payload задан **536870912 bytes (512MiB)**, `os.urandom` в Cloud; documented
composite threshold **157286400 bytes (150MiB)**. Historical archive size неизвестен:
это проверка size-trigger class с >3x запасом, не доказанный равный размер.
**Реальные payload/archive bytes, archive SHA, effective threshold, upload-only
seconds/rate не получены через Reader:** они сохраняются в manifest/policy/marker,
но недоступны; не заменяем их плановыми512MiB или полными72.066с package-upload.

Brief2 и catalogue2 вернули `Reader report or query route is unavailable (HTTP 404)`;
последний запрос catalogue `manifest.json` — `2026-10-21T11:24:54.469844Z`,
более7мин после terminal. File/index/archive/request identities поэтому UNKNOWN.
Нет independently verified upload-complete/inventory/archive gate; `synthetic_upload_gate=null`.
**Proof retry BLOCKED по пункту5 задания**, не запускался; без новой гипотезы
повторять SUCCESS probe нельзя. Raw/full-log/GCS/download обходов и нового admin audit не было.
Запрошено уточнение процедуры индексации; ответа на момент отчёта нет.

Локально: phase8 tests, generator/dispatcher7, actual generated upload shell с
fake storage и tiny packager (success + query/archive/chunks/final-marker failures
и wrong-effective fail-closed), source-preflight3 группы — PASS. Независимый
Luna HIGH review GO. Full preflight: **158** прежних normal-proof файлов побайтно
совпадают с0c1d0d78; tool660b576b/profileeb61/19patch/pins/normal graph сохранены.
Будущий mode flip связан точной эквивалентностью182 runtime/publication Git objects
(type/mode/blob) и recipe, с исключением только явных mutable card/ledger/Markdown.

Full source/config transport fit PASS: **569696gzip/759596base64/191parts** —
это source payload, **не размер evidence archive**;200 substitutions,
maxarg4298bytes, config26388/28000bytes. Локальный oversized candidate194parts
не отправлялся. Из runtime closure исключена только неиспользуемая historical
проза и новый standalone local preflight service test; всё сохранено в Git,
ни один исходный proof/control/pin/script из158 не удалён, caps/codec прежние.

**Следующий blocker:** доступный Brief/каталог этого UUID и связанные receipts,
чтобы установить bytes/SHA/effective setting и закрыть publication/integrity gate.
Cloud SUCCESS не перенесён на proof. Compile/verifier body/full gates нового R11
retry **NOT_RUN_BY_R12_GATE**; последний доступный proof-фронтир — прежний R11 Build5.
Обслуживание продвинулось до успешных Cloud publication steps, proof-прироста0;
**full target gates0/acceptedfalse/independentcredit0/B2/qualificationOPEN**.
Wall-clock/ожидание не приравнивались к active agent time; retired/reserve не расход.

[Точный probe result](cloud-build/origin-layout/R12-PROBE1-RESULT-20261021.json) ·
[Session](cloud-build/origin-layout/R12-SESSION-20261021.md) ·
[Design](cloud-build/origin-layout/R12-UPLOAD-DESIGN-20261021.md) ·
[Release](cloud-build/origin-layout/R12-RELEASE-20261021.json) ·
[Reader coverage](cloud-build/origin-layout/R12-READER-COVERAGE-20261021.md).
