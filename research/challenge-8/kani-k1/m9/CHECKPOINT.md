# M9 — итог PARTIAL, сборки завершены

Результат: `../RESULT-M9.md` (85 строк), привязки и проверки: `validation.json`.
Library commit `b2930031d889065e89054efea16f9a10a409b048`;
library tree `3c5fd2134ca7ed558976b53e1216eeedd0d6b491` заморожен G1=G2.
GO координатора принят для G1 source `578350ad3ae7d7479b7a1abcfc98647db1089eb5`.
G2 source `fe4fa2cc4f3213bb3043c9c8d172b169864f6fb8`.

G1 `06ddd32a-8b17-4b20-b3cf-3ee506400980`: Cloud FAILURE, summary COMPLETE,
gate false: G9/S9aggregate/S9const/S8const SUCCESS covers1/1;
S9nonconst TIMEOUT600, covers/checks/VT не сообщены, peak8.026878GiB.
G1 выбранные S9: aggregate434.47890s/1.599457GiB, const429.67825s/0.820843GiB.
G2 разрешён по отдельным строкам; const выбран по минимальному RSS и VT.

G2 `ed6b14d6-1cfc-4af7-81ce-6d17fd8a2e1a`: Cloud SUCCESS, summary COMPLETE,
gate true; G9/S9const/G8/S8aggregate все SUCCESS covers1/1, VT≤600.
Реальное перекрытие трёх CBMC: PID9280/9285/9290 вместе впервые в70s,
общий наблюдаемый интервал70..279s; затем PID9280/9285/9317 в285..480s.
OOM none_seen, missing0; direct memory attribution9/9 и точные requested names.
check-tooling G1/G2 PASS относительно `97fdf0a21e`; pin/toolchain/lane прежние.
G2 времена — под совместной нагрузкой, не single-harness measurements.

Личный бюджет: G1$0.5670 + G2$0.2295 = $0.7965 ≤$2.30;
builds2/2, reserved$0. Полный список UUID/request_id/source в `builds.json`.
Бюджет и полный envelope+closing reserve проверены перед обоими dispatch.
T0 07:37:33UTC, work cutoff11:07:33UTC, deadline11:37:33UTC, closing reserve30min.
Закрытие подготовлено08:44:53UTC; окно соблюдено. Оба ожидались watch+конец хода.
Новых сборок не запускать: лимит2/2 исчерпан.

Кандидаты в ordinary: G9 + S9const; aggregate S9 также SUCCESS jobs1.
Условие обеих ветвей для предложения заменить C N9 выполнено;
решение ordinary/Part2 и полный CI остаются координатору. Entries по-прежнему opt-in.
Триада N9 неполна; N8const — самостоятельный положительный результат;
исторические N8 BACKING anchors не matched с текущим SHA.
Fixture48 ≠ любой backing; механизм снижения RSS не установлен; macOS UNKNOWN.

Rustfmt exit0/≤100 колонок и source audit PASS; source fingerprint неизменен.
Compiler diagnostics G1/G2 controls cfg: новых targeted SmallSort warnings нет;
ordinary cfg только source audit, отдельной компиляции нет.
Локальные rustc/cargo/Kani/CBMC и посторонние CI не запускались.
Из library изменён только verify/merge.rs; tool/service код не менялся.
Финальная публикация — отдельный research commit с [skip ci], без force.
