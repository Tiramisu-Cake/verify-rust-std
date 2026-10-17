# Административная выборка: a7ad5ce8, 2026-10-17

Разовое поручение владельца: только Build
`a7ad5ce8-2cba-415e-8d7f-6d4ca78ef125`, owner `merge`, checkpoint `df0a29a0`,
до 60 минут, новых Builds и proof-бюджета 0. Это отдельный диагностический
результат; исходные Brief, verdicts, pins и ledger не изменяются.

Причина отказа **не установлена**. Доступные reader endpoints `/brief`,
`/index`, `/receipt` возвращают согласованные компактные отчёты processor 0.3.0.
Index: `diagnostic_complete=false`, `evidence_complete=false`, `aggregates={}`,
`cases=[]`; исполненный profile `unknown`. Source-reported missing_mandatory:
`allprooflogs/cases/*`, `allprooflogs stage logs/resource/exit files`.
Это не устанавливает, были ли эти файлы созданы и где потеряны.
Последняя завершённая исполнительная стадия, отказавшая команда, её собственный
exit status и достижение tool build/exporter/decoder/refiner/verifier неизвестны.
Run exit 1 не является установленным exit конкретной команды.

Доступного административного интерфейса ограниченной диагностики обнаружить
не удалось: `/openapi.json`, `/builds/UUID/search?q=error&limit=5&context=3`,
`/builds/UUID/diagnostics?limit=5&context=3` возвращают 404. Это факты только
о проверенных маршрутах, не доказательство отсутствия других интерфейсов.
`gcloud run services list` для существующего dispatcher account возвращает
`PERMISSION_DENIED: run.services.list`. Доступы и production не изменялись;
raw fallback не выполнялся. Новый reporting service не разрабатывался.

## Точный запрос администратору

Через существующий административный механизм обработать **на стороне сервиса**
evidence только этого UUID и вернуть компактный JSON/Markdown, максимум 16 KiB:

1. Последняя подтверждённо завершённая стадия: название, явный completion marker
   или exit receipt и источник. Отдельно первая отказавшая команда: shell/script
   path и строка, точные argv (без credentials), её exit status и источник.
2. Первое релевантное сообщение отказа: максимум 30 строк, до 10 строк до и после
   ошибки. Нужен контекст, связывающий сообщение с командой; первый error в логе
   без такой связи не считать причиной. Указать file/line или Cloud Logging
   insertId/timestamp и ссылку. При нескольких кандидатах сохранить неопределённость.
3. По каждому tool build, exporter, decoder, refiner, verifier: подтверждённый
   start/completion/exit либо UNKNOWN; NOT_RUN только при явной causal/order
   evidence. Достаточно по одному marker/receipt на стадию; не присылать полные логи.
4. Для campaign/cases сопоставить creation markers runner, точный packaged member
   manifest и выбор processor. Вернуть только relevant paths/hashes/size и
   соответствующие creation/packaging/processor сообщения. Различить «не созданы»,
   «созданы, но не упакованы», «упакованы, но не отражены processor»; иначе UNKNOWN.
   Наличие missing_mandatory в audit само по себе этого не различает.
5. Provenance: Build UUID, pinned proof/infra/tool/profile, фактически наблюдаемые
   identities отдельно, версия административного обработчика, время выборки,
   hashes прочитанных sources и URI/line references. Если нужных данных нет и
   в archive, прицельно обработать относящиеся к отказу Build setup/runner messages
   через существующий admin backend, с тем же лимитом вывода.

Исходники evidence:

- `gs://smallsort-ci-evidence-504462351565/cloud-build/a7ad5ce8-2cba-415e-8d7f-6d4ca78ef125/evidence.tar.gz`
- Archive SHA256 `936446f35abbc5239c245f31c32d64a9a6531bf9ffc194c971e9a0ce6a314a65`.
- Upload marker: тот же prefix, `upload-complete.json`.
- Derived reports: `gs://smallsort-agent-reports-504462351565/derived/v1/a7ad5ce8-2cba-415e-8d7f-6d4ca78ef125/`.
- [Build console](https://console.cloud.google.com/cloud-build/builds/a7ad5ce8-2cba-415e-8d7f-6d4ca78ef125?project=smallsort-ci).

Исходные pins: proof=infra `08b61d8162b1c01c840ed573847622a004232a05`,
tool `d928cb1d7ac60c257daa537fa65577f41135f832`, profile
`experimental-merge-first-callback-u64-v1`, profile SHA256
`300fd8a7172c1644552b43c5bfda51a7c8a620f505012abd3760772df55102e3`.
Не скачивать полные archives/logs на VPS, не менять IAM/credentials,
coordinator, production reporting, исторические verdicts и ledger.

## Исправление, проверка и следующий шаг

Без подтверждённой причины адресное исправление не подготовлено. Defect processor
также не установлен: отсутствие данных в Brief/index не доказывает ошибку parser.
Нет нового кандидата или новых execution identities. Готовность к следующему
Build заблокирована получением этой выборки; автоматический retry запрещён.
Compiler/extraction/verification и synthetic proof execution на VPS не запускались.
Изменены только документация и компактные diagnostic receipts: проверки — JSON,
сопоставление SHA256 с reader receipt, сохранность прежних tracked pins/ledger,
`git diff --check`. Synthetic service tests и независимый semantic/admission review
не применимы: исполняемый код, admission, classifier и semantics не менялись.

Счёт остаётся CLOSED, 103/960 s и 857 retired; Build limit израсходован.
B1 сохраняет только исторический bounded normal credit, новые normal/unwind
obligations и B2 не получают credit. После этой разовой попытки аудита обычные
CI результаты снова получать исключительно через `smallsort-brief BUILD_UUID`.

Компактные исходные отчёты и SHA256 provenance сохранены отдельно в
[ADMIN-AUDIT-RESULT-20261017.json](ADMIN-AUDIT-RESULT-20261017.json),
[Brief](ADMIN-AUDIT-ORIGINAL-BRIEF-20261017.md),
[index](ADMIN-AUDIT-READER-INDEX-20261017.json) и
[receipt](ADMIN-AUDIT-READER-RECEIPT-20261017.json).
