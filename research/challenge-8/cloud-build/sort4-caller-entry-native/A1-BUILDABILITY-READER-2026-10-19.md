# Уточнение через Evidence Reader v0.8 — 2026-10-19

Build `87df47e4-002b-432c-bc87-56612136b448`, terminal FAILURE; source verdict NOT_ACCEPTED_AS_REPORTED. Это повторное чтение существующего отчёта, без нового Build. Прочитан guide редакции2026-10-19; использован `/usr/local/bin/smallsort-brief` v0.8. Первоначальные identity-token timeouts были временными; последующие адресные запросы успешны. Три дополнительных необязательных запроса P0a/OFF/R1 также завершились timeout и не использованы как evidence.

Индекс `6563b9237c999ac5f5eb2a5da7ed3a9a41566122a4c173d9756970e07e7fb51d`, archive `cfbc2d5a446e935d7e1f69abcf0ddf3f027c530500da76a701aaec04d88f2930`. Каталог763members complete;484PROJECTED,124CONTENT_BUDGET_EXCEEDED,67EMPTY_FILE,87UNSUPPORTED_FILE_TYPE,1JSON_EXCEEDS_SCAN_LIMIT. Полнота каталога не означает полноту содержимого. [Компактные наблюдения и provenance](A1-BUILDABILITY-READER-2026-10-19.json) содержат исходные file ID/path/SHA, pointers, coverage и next_offset. Полные логи/raw archives не читались и не скачивались; download_verified не устанавливался.

## Сборка и собственный receipt

Собственный R-only receipt последнего Build доступен: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/R-only-native-reference-receipt.json`, SHA `efb9863ffeb0efed9818d775b811d42463567b62d38d9dfb16a84697c15159fb`. Наблюдения `/build_id`, `/build_exit=0`, `/c_patch_applied=false`, `/kind=separately-built-R-only-native-reference`, `/proof_credit=false`.
R SHA `d99a5ed229533132b8292c5fc70ea93dbe261e9f76c2a0fcc6d6723e796454ca`, translator `ffacadc74de9dded1e50e9b9a71f75a905cf97c7c823427cf7044494e87d052d`, exporter source `c29d0d4692eab84257fe61036d6e41dbc11ee3ad999005df4ffb157bb8b463ad` совпадают с опубликованным кандидатом.
Console binary `7cfdceaea216eafb66db01944464a924f527af4ea2211bb2686502ebde4eb6c7`; exporter binary `07804b821fe33d865efc6674f86a4aa5d6dcfb0e0d25c4f2d39c2af37c395b62`.

Именованные stage receipts R-only `a1-R-only-native-reference-build-stage.json` (SHA `d8941be108d038908c0b73d52cf082c004147424ade3019a82e6fa8033319271`) и final-C `a1-final-schema-exporter-console-build-stage.json` (SHA `4c9dcf19e8d75e31ffcc3c6483a2c86c11e705b24476a6504c29d8dcc3a39241`) дают `/exit=0`. Reconstruction receipt SHA `bdaae57a89a1ebf91c966bfff516c08924c38f597b96659a49fd6e3a17b3cc33`: `/build_exit=0`, `/classification=A1_TOOL_BUILT_UNRUN_PROOF`, final translator `a11741f096eb2e1808cadcb8a49eeeb33117630ae6c141d0202af22b14a9b8c3`, C SHA `e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e`; final exporter/kernel/schema соответствуют pins. Final console binary `741b3995ff9b793fc0e48948bc3357efbd228a5dec74445d900e451e508bc490` отличается от R-only binary, как и ожидается для отдельного C-кандидата.

Эти конкретные записи подтверждают source-reported успешные сборки R5 и собственный свежий reference receipt; прежние D.Type/check_type/unused_mut ошибки их не блокировали. Отсутствие всех возможных предупреждений не установлено. Это не reference equality acceptance для P1 и не formal verification.

## Матрица

Источник всех поимённых status: `proof-audit.json`, SHA `81414bda84c65ced707c66e720f3c26938b4dd321e920952065807635e838769`, pointers ниже. Поиск значений INTENDED_CLASSIFIED/INCONCLUSIVE/NOT_RUN внутри этого file ID дал20явных statuses; next_offset=null для каждого такого поиска. Файл complete=false:512visited nodes, omissions CONTENT_BYTE_LIMIT290/NODE_OR_BYTE_LIMIT3/PRIVATE_OR_SANITIZED_KEY1. UNKNOWN не означает NOT_RUN. Историческая таблица2026-10-18 сохранена; это датированное уточнение.

| Строка | Source-reported status | Pointer в proof-audit.json |
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
| `R2` | UNKNOWN: status omitted from retained projection | `/case_status/R2/status` |
| `R3` | UNKNOWN: status omitted from retained projection | `/case_status/R3/status` |
| `R4` | UNKNOWN: status omitted from retained projection | `/case_status/R4/status` |
| `R5` | UNKNOWN: status omitted from retained projection | `/case_status/R5/status` |
| `R6` | UNKNOWN: status omitted from retained projection | `/case_status/R6/status` |
| `R7` | UNKNOWN: status omitted from retained projection | `/case_status/R7/status` |

Для R2 дополнительно доступны `/matrix_gate_passed=true`, `/observed_outcome=POSITIVE_INTENDED`, `/observed_stage=NONE_OBSERVED`, `/proof_credit=false`, `/provenance=fresh-final-tool-regression` под `/case_status/R2`; status отсутствует в сохранённой проекции. Из агрегата8/5/13 индивидуальный status остальных строк не подставлялся. Поиск R7 во всей проекции не дал совпадений и не устанавливает отсутствие записи в raw source.

P1: `/status=INCONCLUSIVE`, `/reason=current raw source observation missing`, `/matrix_gate_passed=false`, `/proof_credit=false`, observed stage/outcome/provenance=null. Полный native-interface/equality/refinement outcome не установлен.
N-false31: `/status=NOT_RUN`, `/matrix_gate_passed=false`, `/proof_credit=false`, reason/stage/outcome/provenance=null. Собственные body/conformance/receipt/admission/caller-assert lifecycle не подтверждены. A1/A2 остаются OPEN/NOT_ACHIEVED; нового независимо установленного B1/B2 formal credit нет.

## Оставшийся пробел и запрос владельцу

Brief по-прежнему называет P0a adapter_error: `InventoryError: decoded VfMir parse failed: invalid quoted string at byte 9362`; causality UNKNOWN. Реальный literal/field/escape не получен. Каталог P0a показывает `focus/P0a/normal-mir.txt`, SHA `3bf1b47d7e28be437c7f5288c31ad930a1219018fa1cbd035706a94e9a2e6a01`, size471894, scanned65536, CONTENT_BUDGET_EXCEEDED; адресный fragment с start1 вернул NO_DISPLAYABLE_FRAGMENT. Это не доказательство, что именно этот файл был передан парсеру: связь input path с ошибкой тоже нужна. Поиск decoded/vfmir и invalid quoted не дал сохранённых совпадений; Brief diagnostic остаётся отдельным источником.

Нужна административная повторная обработка существующего отчёта или отдельно разрешённый компактный audit: (1) поля status/reason/stage/outcome/provenance/gate/credit для R2–R7; (2) точный input path/SHA парсера и короткий literal/field/escape в районе9362 с различением Unicode index/byte offset; (3) если имеются, отдельные P1 equality/reference и N-false31 own-pair lifecycle receipts. Достаточно адресной ограниченной проекции, без нового proof Build. Новая parser-правка/Cloud-сессия этим чтением не разрешены.

Cloud расход этой операции0; закрытая сессия остаётся5Builds/2115s,16845technical headroom closed, active/unresolved none. Старые ledgers/evidence/pins/review GO не изменены.
