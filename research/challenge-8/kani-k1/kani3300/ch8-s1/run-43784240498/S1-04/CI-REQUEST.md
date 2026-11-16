# S1-04 proposal — OWNER REQUIRED, no dispatch

Control **—**: это reviewable proposal в g0, не опубликованный/исполняемый control. Exact base identities и все23 строки сохранены в `CI-REQUEST.json`; stock runner намеренно отвергает его schema/status. Нельзя переименовать его READY и отправить без реализации/проверок/review.

Подготовлено: шесть exact-ID/location assert oracles в `negative-oracles.json`, fail-closed детектор `negative_oracle.py`, новый explicit group order (light→activation→Cell→heavy singletons), concrete `runner-fix.patch` для потери porcelain-пробела и маскирования exceptions. Патч не применён к control. Его применимость проверяется offline; 27 synthetic runner checks (24 baseline+3 regression) прошли на scratch copy; интеграция classifier/grouping и её полные service tests ещё нужны. Это не обещание, что source drift — единственный runner defect.

Снижение стоимости в этом предложении — раннее исполнение controls/activation и изоляция тяжёлых строк. Численное уменьшение solver cost не установлено. Unwind34, checks, domains и root600 caps сохраняются. Fixed-N split и lower unwind описаны как следующий source experiment в `../COST.md`, не выданы за готовый proof.

Два false-ensures actual activation oracle остаются UNBOUND: runtime placeholder запрещено использовать как wildcard. До запуска требуется source/compiler-level pre-binding exact target wrapper false-ensures property ID/location на том же pin; сторонние failures и failed unwinding отклонять. Включение экспортера named successful property/cover locations необходимо для строгой квалификации; сохранены PENDING gates.

От владельца: новое разрешение S1-04 сверх исчерпанного S1 cap3, конкретный общий/постадийный budget/window и coordinator allocation; решение об отдельном exact-N source candidate. Перед dispatch нужны committed tool/control/source pins, полный CI payload manifest, integration/error-path tests, независимый review и envelope fit. Исходные ledger/окно не расширялись. Ни push, ни CI, ни публикации, ни ledger actions в этой стадии не было.
