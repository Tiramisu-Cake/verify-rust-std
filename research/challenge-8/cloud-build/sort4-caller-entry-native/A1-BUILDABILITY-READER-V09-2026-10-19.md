# Повторное чтение Evidence v0.9 — 2026-10-19

Build `87df47e4-002b-432c-bc87-56612136b448`: terminal FAILURE, source verdict NOT_ACCEPTED_AS_REPORTED. Новый guide и task-queries v0.9 прочитаны, CLI help содержит refresh/end/position. Выполнены Brief → сохранённые Reader-проекции → узкие targeted JSON refresh с expected SHA. Нет нового Build, raw/full-log чтения, изменений кода/пинов/ledger или download_verified.

## Все26 поимённых статусов

Теперь известны все26 source-reported statuses: **8INTENDED_CLASSIFIED / 5INCONCLUSIVE / 13NOT_RUN**. R2–R7 больше не UNKNOWN. Прежние датированные отчёты сохранены.

| Строка | Source-reported status | Pointer |
| --- | --- | --- |
| `OFF` | INTENDED_CLASSIFIED | `/case_status/OFF/status` |
| `P0a` | INCONCLUSIVE | `/case_status/P0a/status` |
| `P0b` | NOT_RUN | `/case_status/P0b/status` |
| `P0c` | NOT_RUN | `/case_status/P0c/status` |
| `P-dispatch` | INCONCLUSIVE | `/case_status/P-dispatch/status` |
| `P1` | INCONCLUSIVE | `/case_status/P1/status` |
| `N-binder-collapse` | NOT_RUN | `/case_status/N-binder-collapse/status` |
| `N-alpha-valid` | NOT_RUN | `/case_status/N-alpha-valid/status` |
| `N-free-region` | NOT_RUN | `/case_status/N-free-region/status` |
| `N-region-swap` | NOT_RUN | `/case_status/N-region-swap/status` |
| `N-no-F` | NOT_RUN | `/case_status/N-no-F/status` |
| `N-clauses` | NOT_RUN | `/case_status/N-clauses/status` |
| `N-default-contract` | INCONCLUSIVE | `/case_status/N-default-contract/status` |
| `N-freeze-contract` | INCONCLUSIVE | `/case_status/N-freeze-contract/status` |
| `N-false31` | NOT_RUN | `/case_status/N-false31/status` |
| `N-source` | NOT_RUN | `/case_status/N-source/status` |
| `N-binding` | NOT_RUN | `/case_status/N-binding/status` |
| `N-clause-redirect` | NOT_RUN | `/case_status/N-clause-redirect/status` |
| `N-duplicate` | NOT_RUN | `/case_status/N-duplicate/status` |
| `R1` | INTENDED_CLASSIFIED | `/case_status/R1/status` |
| `R2` | INTENDED_CLASSIFIED | `/case_status/R2/status` |
| `R3` | INTENDED_CLASSIFIED | `/case_status/R3/status` |
| `R4` | INTENDED_CLASSIFIED | `/case_status/R4/status` |
| `R5` | INTENDED_CLASSIFIED | `/case_status/R5/status` |
| `R6` | INTENDED_CLASSIFIED | `/case_status/R6/status` |
| `R7` | INTENDED_CLASSIFIED | `/case_status/R7/status` |

Для R2–R7 source сообщает matrix_gate_passed=true, proof_credit=false, provenance=fresh-final-tool-regression, reason=null. R2/R3/R7: observed_outcome=POSITIVE_INTENDED, observed_stage=NONE_OBSERVED. R4/R5/R6: NEGATIVE_INTENDED, verification. Это intended classifications регрессионных контролей, не8доказанных std теорем.

P1 остаётся INCONCLUSIVE (current raw source observation missing), N-false31 NOT_RUN; прежние gate=false/credit=false и отсутствие подтверждённых full P1 equality/reference/own-pair N-false31 lifecycle receipts сохраняются. Каталог P1 подтверждает наличие export/decode/refinement/source-support артефактов, что отдельно не подтверждает полный native interface или equality. Catalogue native-reference снова показывает собственный tool reference receipt, установленный в предыдущем чтении, не отдельный P1 equality receipt. Два catalogue false31 запроса завершились auth timeout, не используются как доказательство отсутствия. A1/A2 OPEN/NOT_ACHIEVED; нового independently established B1/B2 credit нет.

## Первый blocker и предел диагноза

`/first_blocker` теперь доступен целиком: case_id=P0a,event=adapter_error,execution_started=true,stage=source-constructor,error=`InventoryError: decoded VfMir parse failed: invalid quoted string at byte 9362`.
`/observation_details/P0a` также complete=true: adapter_error тот же,execution_started=true,failed_stage=source-constructor,not_run=false,proof_credit=false. Таким образом, P0a реально начат по source claim; его ошибка не должна трактоваться как NOT_RUN.

Оба узких поддерева не содержат parser input path/hash/field, traceback или literal. Targeted возвращает parser_input_binding=NOT_ESTABLISHED и causal_status=UNKNOWN. Source-only проверка pinned a1-focus-backend.py:390–394 и a1-compiler-inventory.py:873–877 показывает чтение normal/readonly MIR и последовательные parse calls, но общий exception не указывает, какой из двух вызовов отказал. Подтверждённой связи конкретного файла и позиции9362 нет. Поэтому позиционный запрос к normal-mir.txt не выполнялся: координата Python str не переносилась на предположительный файл. Реальный literal/escape/decoder error по-прежнему не установлен; synthetic escape не используется как диагноз. Grammar/parser не менялись.

Остался конкретный административный запрос: установить parser input path/SHA и преобразование, вызов normal или readonly, затем дать узкий literal/field/escape9362 с Unicode/UTF-8 координатами и имеющимся decoder error. После установления binding допустим адресный position refresh; новый proof Build ради отчётности не нужен. Запрос R2–R7 из предыдущего отчёта удовлетворён и больше не требуется.

## Provenance, точность и квота

Файл всех новых targeted наблюдений: `proof-audit.json`, file ID `cc20cf422e3f3828330adb99a0a55222711961bbb855f3b12dfc360c537a3e96`, SHA `81414bda84c65ced707c66e720f3c26938b4dd321e920952065807635e838769`. Index `6563b9237c999ac5f5eb2a5da7ed3a9a41566122a4c173d9756970e07e7fb51d`, archive `cfbc2d5a446e935d7e1f69abcf0ddf3f027c530500da76a701aaec04d88f2930` совпадают с v0.8 наблюдениями20строк.

Все8targeted ответов status=OK,complete=true,exact=false,representation=SANITIZED_JSON_OBSERVATIONS,omissions={}. Complete относится только к выбранному поддереву, не proof и не всему файлу. [Машинный отчёт](A1-BUILDABILITY-READER-V09-2026-10-19.json) сохраняет селекторы/request IDs/provenance/ограничения и все26статусов. Для прежних20строк источники сохранены в [v0.8 observations](A1-BUILDABILITY-READER-2026-10-19.json), тот же source/index SHA.

| Selector | Request ID |
| --- | --- |
| `/first_blocker` | `1d93914a8d283d02377d69aae8eae44bc8fa3f3efda8112d5de586fecca30c5f` |
| `/observation_details/P0a` | `d5f80c8b7bc1cbb449a778c17827fbadd335cd26fc703b7909fc0e7d261bee5e` |
| `/case_status/R2` | `8f8856ba2a5c660f7018126b9403e10adeea14519df9f8ade04ac4b8a17d1416` |
| `/case_status/R3` | `d4c81535a0cf58e719b906beb2e4cd2ca14d3952bc709136028fe34ff43a7c86` |
| `/case_status/R4` | `555f55a858a39322d9c62417a2c890cb4f67966ef6458d0ac9988c7687014417` |
| `/case_status/R5` | `0f5913c5a7aae7dcc8078800def84b7c0421b4e4c80e80504ac5c1f1333f9dbf` |
| `/case_status/R6` | `198b0494b39a1f13a1f6b9661e0e4d228cbd44849b144c41f7a370727c970bff` |
| `/case_status/R7` | `637a61b9dc3ab9329ec7d51ac85a9b0d8675026dc8546bf339045a330b3ab454` |

Отправлены8разных targeted запросов, каждый один раз, без пагинации/соседних окон/выгрузки файла; фактический остаток общей16-квоты не выводится из числа calls, кеш/резервирования клиентом не менялись. Reader предварительно дал NO_DISPLAYABLE_FRAGMENT для first_blocker и observation_details/P0a, ранее для R2 и теперь для R3–R5; попытка Reader R6 завершилась auth timeout, R7 ранее не находился глобальным поиском. Успешные targeted ответы отдельно проверены. Auth failures не превращались в NOT_RUN/absence.

Собственные R-only/final-C successful stage receipts и свежий R-only tool reference receipt остаются установленными по предыдущему чтению. Compile buildability не означает proof acceptance. Cloud расход чтения0; закрытая сессия5Builds/2115s и16845closed technical headroom без изменений.
