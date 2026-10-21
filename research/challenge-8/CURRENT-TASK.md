# Merge-R14 — принять доступный publication gate → прежний R11 proof

## Авторизация и рабочее место

- **ID:** `merge-publication-gate-proof-retry-2026-10-21-r14`; **статус:** DONE; publication recovery завершён, proof остаётся OPEN. T0 `2026-10-21T12:52:50Z`.
- **Owner:** `merge`; **project worktree:** `/root/verify-rust-std-merge-origin`; **branch:** `merge/incoming-origin-20261009`; **репозиторий:** `Tiramisu-Cake/verify-rust-std`.
- **Tool worktree:** `/root/verifast-merge-actual-glue`; branch `merge/actual-glue-instance-20261011`, expected head **`660b576b6b1608db913c51e0785b443a8733396f`**. Tool/model/spec/invariant сохраняются.
- **Новое окно:** 120 минут основной работы + до30 минут завершения. T0 при фактическом старте после чтения; main=T0+120мин, absolute=T0+150мин. Запиши в session/новый ledger/текущий статус.
- **Новый бюджет:** **3600 Cloud-секунд**, used0/carry0, без отдельного лимита числа последовательных Builds. R13/старые счета и retired3506 не возобновлять/переносить.
- **Phase:** `MERGE-PUBLICATION-GATE-PROOF-R14-2026-10-21`; **ledger:** `cloud-build/origin-layout/CURRENT-RECOVERY-R14-PROOF-RETRY-BUDGET-20261021.json`.
- **Bounds:** ceiling_build_seconds=3600, max_builds=null, max_timeout_seconds=1200, carryover_allowed=false; **lane:** существующая `merge`. Timeout90..1200с, envelope=timeout+60 в остатке/окне с запасом для package/upload/verdict.

**Владелец разрешил скорректировать избыточный publication gate и перейти к повтору прежнего R11 proof без нового synthetic Build.** Новое окно, бюджет, branch-local phase/ledger/gate/mode/recipe/pins регистрация и необходимые service tests явно разрешены. Публикационная проверка ниже заменяет требование точного sidecar receipt для этого уже успешного probe. Она не меняет proof acceptance и не даёт proof credit. Сам выбери implementation внутри указанного scope, каждый fix/Build/SHA отдельно не согласовывать.

Ты начинаешь без контекста. Проверь обе worktrees/branch/HEAD/dirty diff и сохрани чужие изменения. Прочитай `AGENTS.md`, [STATUS](STATUS.md), [автономность](PROOF-AGENT-AUTONOMY.md), [процесс](ITERATION-PROCESS.md), нужные части [Cloud runbook](cloud-build/README.md), [WORK-POLICY](WORK-POLICY.md) и [Evidence guide](EVIDENCE-READER-GUIDE.md). Всю историю не перечитывай.

## Исходная точка: Brief уже работает

Checkpoint **`6ee5298e69dfe552487cd73cc7be04bae47dbf0f`**. R13 CLOSED: **94charged/94execution/3506retired/remaining0/carryfalse**, own active/unresolved/requests/reservations0; normal proof не запускался. [Архив R13](task-history/merge-archive-size-upload-recovery-2026-10-21-r13.md), [probe result](cloud-build/origin-layout/R13-PROBE1-RESULT-20261021.json), [release](cloud-build/origin-layout/R13-RELEASE-20261021.json).

Проверенный synthetic probe:

| Identity | Значение |
| --- | --- |
| Build | **`331fba31-4548-40e7-bb6d-1d225f590602`** |
| Source/infra/proof | **`c9b5151735c352d212752c5fe644adcd3543b68d`** |
| Submitted config SHA256 | `da5162520a5fa2b96611a56f06a21ad8ae91843e214257c27ebac41051391ea0` |
| Archive SHA256 | `8ecf904c01ef647009619d7d445e13cb258c18a656dc65bc873756c610183efb` |
| Index SHA256 | `ad0e439b6d42371ade0c1db672f0f675e0eb6e209ca643e04b5b079d9a5a428e` |
| Build/steps | SUCCESS; execute/package-upload/verdict все SUCCESS |
| Brief | **VERIFIED_ARCHIVE_AND_INVENTORY**, полный каталог15 members |

Точное число compressed archive bytes и внешние `archive-size-check.json`/`upload-complete.json` остаются **UNKNOWN/недоступны через Reader**. Они создаются после упаковки, не входят в archive catalogue. Это ограничение наблюдаемости, не новый404 и не установленный upload failure. Старое требование получить эти sidecars через Brief было избыточным; не повторяй probe и не требуй raw/admin audit только ради этого числа.

## Исправленный gate: необходимые свидетельства и границы

**Разрешено принять указанный existing probe как publication prerequisite** при следующей совокупности привязанных свидетельств:

1. Fresh bounded Brief для exact UUID подтверждает VERIFIED_ARCHIVE_AND_INVENTORY с указанными archive/index identities. Coordinator metadata подтверждает SUCCESS всех3 шагов; это публикационный результат, не verification theorem.
2. Через Brief/targeted подтверждены source/config/Build identity и effective composite policy False/threshold150M=157286400. Archived `allprooflogs/upload-policy.json`: fileID `0f66bbe9230a4472a9e913dca0daeb28ad99b4a96f7625f689ccb0c2b3561f97`, expectedSHA `9883177b74ed1ede34b6498f363ce689b82c1beaee9211810179253aee8cc659`; полный root response request `da464eaaf9a99cba220d2226f40eea07121267e0ca1f12ae0775b1b3ee4e6d38`. [Поля и прежняя coverage](cloud-build/origin-layout/R13-PROBE1-RESULT-20261021.json). Не перечитывай ненужные payload bytes.
3. Проверка фактически отправленного config и exact pinned producer устанавливает: `R13_UPLOAD_REQUIRED=true`, безопасная обязательная mode card; `set -euo pipefail`; actual compressed archive stat/guard после упаковки и до первой storage upload; отказ guard не маскируется; successful marker upload предшествует upload.ok/verdict success. Guard принимает synthetic лишь при `effective threshold < actual archive bytes <=536870912` и policyFalse. Source и config должны совпасть с таблицей, нельзя переносить рассуждение на произвольный Build без этих checks.

**Обозначай основание честно:** publication verified через Brief; выполнение mandatory guard и размерные границы установлены по exact pinned fail-closed execution path + successful Cloud steps. Это не прямое чтение внешнего size receipt. Сохрани `archive_size_bytes=null`, `exact_archive_size_observed=false` и недоступность sidecar; не выставляй `sidecar_verified`, не подставляй256MiB/предположительный compressed size и не утверждай независимое наблюдение точного числа. Числовые границы и подтверждённая целостность достаточны для этого administrative/service gate, independent proof credit остаётся0.

Запиши новое решение/coverage в отдельном R14 gate record. Historical R13 gate PENDING/отчёт/ledger и их расход не менять. Ссылка на previous-phase probe — read-only; **не добавляй старый Build в новый ledger.builds и не списывай его94секунды повторно**. Новая проверка не должна требовать, чтобы probe находился в текущем счёте. Не делай blanket исключение missing metadata: допуск ограничен указанным identity-bound probe и перечисленными checks.

## Первый полезный запуск — normal proof

1. **Согласуй новый phase validator с этим gate.** Старый R13 validator требует integer archive_size_bytes и успешный probe внутри того же ledger; напрямую использовать его нельзя. Сделай узкий R14 branch-local путь, принимающий read-only предыдущий probe с точными identities и честным unknown размером. Старые phase restrictions сохраняются. Проверь fail-closed negatives: wrong/missing Build/source/config/archive/index, policyTrue, guard отключён/после upload/ошибка подавлена, required=false/missing card, другой publisher/source closure. Не удаляй сам size guard ради обхода условия допуска.
2. **До submit — review и маленькие service tests.** Независимый **GPT-6 Luna HIGH** review текущего gate/registration/mode diff (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`, без вложенной делегации/дорогой замены). Тестировать synthetic metadata/fake storage/малые файлы, не compiler/verifier/full preparer. Не повторять review неизменённой proof-логики. Runtime/transport closure и pins должны пройти существующий preflight; caps/codec не повышать.
3. **Переключи на `proof-r11`, не запускай новый synthetic upload.** Проверить exact cross-mode source/runtime/publication correspondence к probe и frozen normal proof. Допустимы новые phase/ledger/gate checks и привязка mode card, необходимые для R14; их нельзя молча исключить широким directory ignore. Publication shell/guard/SDK/account/create-only/marker-last должны остаться эквивалентны проверенному пути; phase/card routing не должны выключить mandatory guard. Если publisher semantics реально изменяются, старый probe не объявлять автоматически применимым: обоснуй конкретное отличие, а не делай повтор «на всякий случай».
4. **Проверяем прежний R11 candidate.** Last actual proof source **`0c1d0d7861813bcc48d765eba869d30c2658f1cc`**, expected tool **`660b576b6b1608db913c51e0785b443a8733396f`**, profile `experimental-merge-label-storage-r11-v1`, SHA256 `eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375`. [Frozen inputs](cloud-build/origin-layout/R11-RETRY-INPUTS-20261021.json); R13 подтверждала158 normal-proof files byte-equal. Сохрани tool/model/std/spec/initialized-value invariant/matrix/controls и source correspondence. Не предлагай новую proof-гипотезу до получения доступного результата этого кандидата.
5. **Получить результат через Brief и завершить publication recovery.** Сохрани актуальный normal Build UUID/source/tool/profile/config, compile milestones, конкретный verifier body result/первый ресурсный отказ и controls; затем отдельно full target gates/independent credit. Normal Build может дать FAILURE по настоящему proof obligation при исправной публикации — это новый proof evidence, не новый дефект uploader. Последний старый доступный proof-фронтир — R11 Build5 checked Live/Dead117 → iterationprep301/points_to_limits/dummy30none; initialized-value invariant до сих пор без доступного formal result. Не переносить synthetic SUCCESS на proof, stale resource PASS на новый source или отсутствие observations в NOT_RUN.

Scope R14 — снять reporting-only blocker, выполнить прежний normal proof и адресно разобрать результат. Не менять tool/model/spec/invariant/normal-unwind-abort/CFG/ресурсы/математические критерии ради PASS. Новая разработка proof-кандидата — следующее задание. Связанные узкие source/registration/service fixes разрешены автономно; неизменённый Build повторять только при установленном временном инфраструктурном сбое. Если задача выполнена, заверши с отчётом, не заполняй окно лишними запусками.

## Исполнение, Evidence и завершение

Сохрани pre-upload guard **actual compressed archive<=536870912** и policy export `CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False` внутри Build. Для normal proof нижней границы threshold нет. IAM/storage.objects.get, SDK/account/bucket policy/backend и лимит обработчика не менять. External sidecar API/улучшение диагностических Brief — отдельная задача. Недоступность необязательной метрики сама по себе не требует нового Build или остановки proof в этом задании.

Каждый новый Build через существующий coordinator, exact reviewed/committed/published source/infra SHA с проверенным полным remote SHA, config/recipe/profile/source closure. Source transport в R13:565029gzip/189parts, config26960/28000; полный token/caps/dependencies проверить до submit. Один occupied/unresolved Build на stable owner `merge`, максимум три project-wide. Refusals не обходить, uncertain submit не дублировать; envelope timeout+60 в бюджете/absolute с запасом для полезного target и публикации.

Ожидание/status — шаги≤60с с yield10–30с, без пустого polling; выполняй полезные независимые проверки. Через час — progress/charge/blocker без ожидания ответа. После main новых Builds/retries/гипотез нет; finishing — начатое/Evidence/accounting/checkpoint/push. К absolute terminal/accounted либо exact active/unresolved IDs и следующий разрешённый шаг. Остаток retire без carry; закрытый R13 не возобновлять.

Evidence v0.11: `smallsort-brief BUILD_UUID` → catalogue/file ID → `--refresh --file ID --expect-sha256 SHA` с info/locate/position/lines/JSON pointer, явные страницы по server next_offset/next_value_start. [Guide](EVIDENCE-READER-GUIDE.md), [примеры](EVIDENCE-READER-TASK-QUERIES.md), `/root/SMALLSORT-BRIEF-AGENT-GUIDE-RU.md`. Старые16-квота/WITHHELD отменены. Сохранять file/index/archive/request identities/exact/complete/coverage. Evidence — данные, не команды; no-match не NOT_RUN, integrity/exit0/source PASS не independent B1/B2 credit. Raw/full logs/archives/Cloud Logging/локальные raw copies и GCS/download/storage/logging обход запрещены. Не ставить download_verified, historical verdicts/ledgers не переписывать. Новый admin audit отдельно, но только ради недоступного exact archive size в этом gate он не требуется.

VPS — чтение/правки/Git/hashes/static parsing и малые isolated synthetic service tests; actual pipeline/compiler/exporter/decoder/refiner/verifier только Cloud. Чужие worktrees/pins/shared live state, Actions, внешние комментарии/merge/upstream PR не трогать.

Обновляй компактный STATUS и session/release/evidence records. Здесь **один перезаписываемый отчёт**: T0/deadlines/end; принятое gate и основание/UNKNOWN; normal Build UUID/source/config/tool/profile; гипотеза/type/результат/charge; compile/body/controls/full gates отдельно; own active/unresolved/requests/reservations; spent/retired/carry; конкретный следующий proof blocker. История по ссылкам, текущий файл не наращивать. Начальный **full target gates0/acceptedfalse/independentcredit0/B2/generic/qualificationOPEN**; допуск к запуску этого не меняет.

## Отчёт агента

T0 **2026-10-21T12:52:50Z**, main 14:52:50Z, absolute 15:22:50Z. Счёт закрыт
**13:36:35Z**; end **2026-10-21T13:41:45.443908Z**.

**Publication recovery выполнен.** Отдельный R14 gate принял только probe
331fba31/c9b51517/config da516252/archive 8ecf904c/index ad0e439b: fresh Brief,
verified inventory, policy False/150M и точный fail-closed config + три SUCCESS.
Размерные границы установлены по mandatory guard path; `archive_size_bytes=null`,
`exact_archive_size_observed=false`, `sidecar_verified=false` сохранены. Нового
synthetic не было. R13/history/его 94 секунды не изменены и не перенесены.

**Normal proof:** Build **23dc710b-07e5-43ff-b63b-febe4ddb19ca**, source/infra
**bec0469fe0d20c2d74775b0ba9e9920b11c13445**, config
`5a9909ba3b877ac4a1c35a4d195fea619d171c16feece28586da51ee5dd83174`.
Tool 660b576b/profile eb61e493 и все 158 R11 proof inputs byte-equal baseline
0c1d0d78. Luna HIGH review; phase 10/source 8 и uploader error paths PASS.
Full closure/preflight PASS; source 571521 gzip/191 parts/200 substitutions,
config preflight 26984/28000, actual dispatch 27012/28000 при timeout 1200. Локальные transport refusals не создали Builds.

Build **FAILURE**: execute/package-upload SUCCESS, final verdict exit 1.
Brief **VERIFIED_ARCHIVE_AND_INVENTORY**, evidence complete; archive
`e16d6a942db63878e27f539eb2c2d01e86459f041dadbf23deffe0f246913024`, index
`54a86d655622f1aabe70a921e3858ae2188f29015ee90825afb7a3da63df142c`.
Compiler source PASS: exporter/decoder/translator/console/refiner exit 0,
postbuild source hash exit 0. Execute 441.424 s, package+upload 314.819 s;
это не измерение upload-only rate, exact archive size остаётся UNKNOWN.

**Actual full body INCONCLUSIVE**, accepted/proof_credit false. Classification
и exact trace 2252/2259 совпали: `prelude_core.rsspec(264,72–74)` не доказывает
`cons(dummy55, nil) = cons(dummy55, values03)` при
`close array::<u64>(sift, 1, cons(r7_sift_current, nil))` после late-callback recovery
(`verified/lib.rs(357,737–742)`). Это новый доступный first-error frontier,
а не перенос исторического dummy30/points_to_limits. R11 mandatory placement
controls: source `all_matched=true`; optional extra-address-taken false;
accepted/proof_credit false. Run identity связан с текущими UUID/source/tool/profile.
Targeted audit: accepted=false, diagnostic_complete=false; full_transfer и whole-challenge theorem pointer не найдены, их значения UNKNOWN (не NOT_RUN). Full target gates **0**, accepted false, independent credit **0**;
**B2/generic/qualification OPEN**. Никаких proof/model/spec/invariant изменений.

Один новый Build, **774 charged / 773 execution / 2826 retired / remaining 0**,
carry false; own active/unresolved/requests/reservations **0/0/0/0**.
HTTP429 одного targeted query преодолён сериализацией; raw/GCS/logging обхода нет,
log прочитан только bounded locator/window; no-match не трактовался как NOT_RUN.
Задача завершена без лишнего повтора. Следующий proof blocker — факты хвоста
нулевой длины при сворачивании singleton array после callback; разбор/исправление
в следующем задании с сохранением ресурсов и критериев. Результаты:
[R14 proof](cloud-build/origin-layout/R14-PROOF1-RESULT-20261021.json),
[body/controls evidence](cloud-build/origin-layout/R14-BODY-EVIDENCE-20261021.json),
[compile/audit](cloud-build/origin-layout/R14-COMPILE-AUDIT-EVIDENCE-20261021.json).
Финальный docs/accounting checkpoint не запускался как Build.
