# Диагностика Build57ea65a3 — доступные отчёты и запрос audit

Build `57ea65a3-475e-4370-810c-19ad36803174`; исходный checkpoint `874932e8`.
Исследован точный proof/infra revision
`9678ddf631902765d7013f5ed1b9fd05159463a6`. Причина финального отказа Build
установлена: шаг verdict не принял summary с diagnostic_complete=false и
verification_accepted=false. **Первый причинный blocker исполнения A1 остаётся
UNKNOWN**. Доступные отчёты не выбирают обоснованное исправление source.

## Полученные данные

Повторно вызван `smallsort-brief BUILD_UUID`. Через тот же аутентифицированный
reader, с существующим dispatcher identity/IAM, прочитаны только
`/builds/BUILD_UUID/index` и `/builds/BUILD_UUID/receipt`. SHA256 доставленных
Brief/index совпадают с processing receipt:

- Brief: `54b9f0abcdd981e950c63656cf7d61d21db1b4a3f95d3aee4b11107c938bf153`.
- Index: `30fd8b8b7885e34fc446040be8c1b0bb0c4f2934ebb5f18c8db0be4aa5ee854b`.
- Processor0.3.0, VERIFIED_ARCHIVE_AND_INVENTORY;356 проверенных inventory files,
  2 metadata exceptions cross-checked.272 text entries/chunks индексированы;
  отдельные remote chunk bytes не проверялись processor и здесь не читались.
- Archive SHA256 из index:
  `02901f734338f175e9969c47fe59c35d369e75e2150308b06495ba6acc2e6c0f`.
- Source claims в index: run_exit_code=0, evidence_complete=true,
  text_logs_complete=true, missing_mandatory=[], failure_class="none",
  diagnostic_complete=false, verification_accepted=false.
- Index указывает actual `proof_audit_path="proof-audit.json"`, но не раскрывает
  его содержимое; cases=[], aggregates={}. Это свойства **derived index**,
  не доказательство отсутствия оригинальных records в archive.

[Brief](brief.md), [index](evidence-index.json),
[processing receipt](processing-receipt.json), [машинный отчёт](diagnostic.json).
В diagnostic.json сохранены URLs отчётов и полные SHA256 полученных файлов.
Raw archives, full verifier logs и Cloud Logging не запрашивались.

Cloud Build API использован только через read-only `builds describe`:

```text
gcloud --configuration=smallsort-ci --account=smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com --project=smallsort-ci builds describe 57ea65a3-475e-4370-810c-19ad36803174 --region=global --flatten=steps --format='json(steps.id,steps.status,steps.exitCode,steps.timing,steps.allowFailure)'
```

Отдельная projection запросила Build identity/status/times/timeout/failureInfo и
image digests. Полные args/env/logs не запрашивались. API source resource:
`projects/smallsort-ci/locations/global/builds/57ea65a3-475e-4370-810c-19ad36803174`.

| Шаг | API status | Exit | Timing UTC | Длительность |
| --- | --- | --- | --- | --- |
| execute | SUCCESS | 0* | 10:57:34.174611152 →11:02:02.278571886 | 268.104s |
| package-upload | SUCCESS | 0* | 11:02:02.278819202 →11:02:49.805659049 | 47.527s |
| verdict | FAILURE | 1, явно в API | 11:02:49.805862519 →11:02:51.312458825 | 1.507s |

\* Поле exitCode для SUCCESS шагов не передано API. Нормализованный0 выведен
из SUCCESS при отсутствии allowedExitCodes в submitted pinned recipe; это
отдельно отмечено в diagnostic.json, исходная projection сохранена без правок.
Оба первых шага имеют allowFailure=true, однако их API status именно SUCCESS.
[Steps projection](build-steps.json), [Build projection](build-metadata.json).
API failureInfo: USER_BUILD_STEP, step2 exited1. Build не TIMEOUT; timeout900s.

## Что объясняет pinned source

Ниже — выводы из source плюс reported summary, отдельно от прямых stage observations.
Полные source hashes: [source-pins.json](source-pins.json).

- [control.py:L182–190](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9678ddf631902765d7013f5ed1b9fd05159463a6/research/challenge-8/cloud-build/control.py#L182)
  сохраняет внутренний status в run-exit.txt, а execute wrapper возвращает0.
  Поэтому SUCCESS execute сам по себе не доказывает успех compiler/verifier.
  Index дополнительно сообщает именно внутренний run_exit0.
- [control.py:L194–223](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9678ddf631902765d7013f5ed1b9fd05159463a6/research/challenge-8/cloud-build/control.py#L194)
  делает package/upload под set-e, создаёт upload.ok после загрузки; verdict
  возвращает1 при ложном acceptance predicate и2 при исключении чтения summary.
  Успешный package-upload плюс оба false flags объясняют наблюдаемый verdict1.
  Следовательно, отказ самого upload или исключение verdict parsing здесь не
  установлены и несовместимы с этими API/source facts.
- [package-evidence.py:L274–334](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9678ddf631902765d7013f5ed1b9fd05159463a6/research/challenge-8/cloud-build/package-evidence.py#L274)
  отделяет completeness от accepted/diagnostic_complete. Для non-smoke
  evidence_complete=true требует хотя бы один файл под allprooflogs/cases/,
  распознанный audit с bool accepted и stage artifacts. Это **source-based
  следствие reported claim**, без списка конкретных case/stage files.
- [run-o26-refresh.sh:L741–748](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9678ddf631902765d7013f5ed1b9fd05159463a6/research/challenge-8/cloud-build/run-o26-refresh.sh#L741)
  запускает A1 entry stage, копирует diagnostic-audit.json в root proof-audit.json,
  затем выходит0. Если исполнялся этот точный flow, reported run0 означает
  завершение adapter и копирования audit. Это **условный control-flow вывод**,
  а не непосредственно прочитанный runtime stage marker или proof result.
- [a1-runner.py:L1820](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9678ddf631902765d7013f5ed1b9fd05159463a6/research/challenge-8/cloud-build/sort4-caller-entry-native/a1-runner.py#L1820)
  перехватывает tool reconstruction/stage exceptions и сохраняет отказ в audit.
  [Финализация:L2392](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9678ddf631902765d7013f5ed1b9fd05159463a6/research/challenge-8/cloud-build/sort4-caller-entry-native/a1-runner.py#L2392)
  вычисляет diagnostic_complete только из всей матрицы и возвращает result;
  [a1-entry.py:L75](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9678ddf631902765d7013f5ed1b9fd05159463a6/research/challenge-8/cloud-build/sort4-caller-entry-native/a1-entry.py#L75)
  не превращает отрицательный diagnostic в process exit. Поэтому run0 совместим
  с пойманной ранней ошибкой, NOT_RUN строками и классификационным отказом.
- verification_accepted=false и accepted=false заданы runner явно и сохраняются
  даже для диагностического threshold/interface эксперимента; успешная матрица
  могла бы пропустить Build через diagnostic_complete=true. Следовательно,
  NOT_ACCEPTED_AS_REPORTED не является отдельным доказательством body failure.
- [package-evidence.py:L350](https://github.com/Tiramisu-Cake/verify-rust-std/blob/9678ddf631902765d7013f5ed1b9fd05159463a6/research/challenge-8/cloud-build/package-evidence.py#L350)
  присваивает всем прочим non-stock/non-constructor lanes статический label
  tool_profile.scope="no proof tools executed". Этот index label **не подтверждает**,
  что compiler/verifier не запускались в A1.

Source preflight был транспортным: Git identities/closure/bytes, profile/helper
hashes, config bounds и inert plan. Он не исполнял Cloud setup, compiler,
extraction или verifier. Общая source-preflight/overlay ветка run-o26-refresh.sh
для этой lane пропускается (L219). Source review/preflight не закрывает runtime
ошибку и не доказывает, что новый A1 record формат раскрывается processor0.3.0.

## Provider hypothesis и оставшиеся варианты

Pinned provider.py SHA256:
`771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616`.
Он совпадает с inline provider pin в run-proof.sh и найденными constants других
provider adapters revision. Актуальная lane идёт через recipe dispatch; ветка
stock/constructor с inline проверкой и общие O26 overlay/preflight проверки не
являются её A1 provider-pin gate. В transported recipe Python/shell closure
не найдено PROVIDER_SHA constant, требующего другой SHA. **Конкретного stale pin,
как в merge, здесь не обнаружено**. Произвольную runtime provider/env ошибку это
не исключает; её надо связать с фактическим command/stage result.

Подтверждённо исключены глобальный900s timeout как Build status, отказ upload
как terminal step cause и verdict read-exception/exit2. Unhandled setup/entry
refusals с nonzero status до возврата A1 несовместимы с reported run0 при exact
pinned flow; это ограничение гипотез по source, не независимо прочитанные stages.
Не исключены пойманный tool reconstruction/build failure, export/decode/refinement
или compiler identity отказ, P1/native-reference mismatch, body/conformance или
receipt/caller отказ, deadline внутри отдельного stage, immutable-input/classifier/
A1Admission mismatch. Возможна потеря проекции A1 records в index. Ни одна из
этих причин не выбирается по elapsed time, размеру archive или числу файлов.

## Подтверждённость целей

P1 compiler identities/full native subtree comparison: UNKNOWN.
Все26 фактических per-row outcomes остаются UNKNOWN; не присваиваются ни PASS,
ни intended negative, ни NOT_RUN только из-за отсутствия строк в index:

```text
OFF P0a P0b P0c P-dispatch P1
N-binder-collapse N-alpha-valid N-free-region N-region-swap N-no-F N-clauses
N-default-contract N-freeze-contract N-false31 N-source N-binding
N-clause-redirect N-duplicate R1 R2 R3 R4 R5 R6 R7
```

N-false31: собственные default/Freeze body+conformance, собственный receipt,
threshold32/len32 admission и достижение caller len<=31 — каждый UNKNOWN.
Непосредственно подтверждены только Build step completion/failure и названные
source claims/index integrity. Целостность архива не даёт formal credit.

## Точный следующий шаг

[ADMIN-AUDIT-REQUEST](ADMIN-AUDIT-REQUEST.md) ограничивает результат16384 UTF-8
байтами, суммарный raw context30 строками, и требует first causal error,
command/status, last confirmed stage, original case/aggregate/marker presence
и проверяемые member SHA256/ссылки. Сам запрос не разрешает raw audit.

Без этого результата минимальный source fix не обоснован. Production pins,
verdict predicates, исторический ledger/checkpoint и proof credit не изменены.
Новые Builds/compiler/verifier не запускались; закрытый CI account не открывался.
