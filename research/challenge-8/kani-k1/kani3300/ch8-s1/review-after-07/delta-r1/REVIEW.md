W14 delta-review по task `6437eae7c85936886dd109d8a2080b237e1f8968`.

**Composer APPROVE. Repaired package APPROVE. W14-S108-01 CLOSED на fixed pins.**
Новых concrete findings нет. Original review и old candidate verdict не изменены.
Это readiness для передачи координатору к GO, **не dispatch GO** и не admission.
S1-08 compiler/exporter/verifier/full runner/CI NOT_RUN; independent/B1/B2 credit NONE.

Exact reviewed inputs:

| Объект | Commit |
|---|---|
| composer accept-v3 | `0a97c61cce9f6fca1acc9ab35509e314012b7bfa` |
| s1-08-r1 package | `d5dcb0fa5db210116101f440048a4f1fae7c2d20` |
| fixed control | `7c41333f9bfcfd7eb4e0ede7bd316443090c9025` |
| unchanged source | `99e8456d200fff1299ee5756279cddb23921dc65` |
| stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` |

Embedded request SHA256
`77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e`.
Source tree `b769b084f9982cbcb166229b29b6bd2bff136c51`; fixed control tree
`7ba8030690596cb491d1ae4f44e32805aa25931e`.

**Закрытие W14-S108-01.** Независимо извлечены declaration spans из named roots
в pinned source99e: descending `95:32–95:48`, effectful `101:21–101:37`, текст
обоих — `|a: &u8, b: &u8|`; columns one-based, end exclusive. Fixed IDs содержат
эти spans. Source helper/type/path и `.assertion.1` сохранены; assertion по-прежнему
`enabled::<T,F>()` в source90. Изменились только coordinate substrings двух IDs.
Все остальные поля двух rows и полные другие шесть negative rows/oracles совпадают
с old9ccd. FAILURE/DETECTED, sole-failure и companion semantics сохранены.

На неизменённом `negative_oracle.matches` synthetic failure с новым ID принимается
fixed oracle; cross-match со старым oracle и обратный cross-match отклоняются.
Это static/synthetic закрытие дефекта ожиданий, не наблюдение новых runtime IDs.
Pinned producer сохраняет полную instance identity, как установлено исходным review.

Новая `oracle_source.validate` проверяет все восемь oracles по canonical whole-file
hashes, assertion expressions/contexts и полным ID templates. Closure span берётся
из выбранной source function; замена только request/hash/ID не заменяет canonical
source pins. Прочитан полный checker и tests: старые строки100/106, неверные columns,
path/ordinal и coherent source/hash/context/ID shifts отклоняются ниже внешних
payload hash gates. Source fixtures побайтно равны actual pinned Git blobs;
negative overlays применены к actual source в temporary Git indexes и сверены
whole-file hashes. Четыре новые regression tests независимо повторены — PASS.

Полный diff old9ccd→fixed7c413 ограничен восемью paths: два ID + schema/payload/path
inventory, canonical oracle manifest, два exact source fixtures, checker/regressions,
добавление test_s108r1 в четыре preflight steps и соответствующая preflight-проверка.
Runner/matcher/decoder/collector/native capture/final snapshots/location policy/
caps/checks/flags/domain не менялись. Admission в runner не добавлен. Direct parent
обоих controls —9208; это siblings, depth5/2/2 сохраняется. Read-only control
preflight на actual committed tree с synthetic GitHub context — PASS, dispatch NOT_RUN.

Package manifest/payload/producer hashes, request/envelope/ROLE-MAP mirrors и все
три patch reconstructions проверены: source, full control от9208 и review delta
от9ccd воспроизводят exact trees. ROLE-MAP прежний:127 bindings =111 future labels
+16 preserved semantic bindings;35 rows/14 groups/113 covers неизменны. Old8ea/9ccd
и reviewed U/PFC files побайтно совпадают со своими commits. Полный независимый
аудит исходной assertion equivalence и U/PFC не повторялся; штатный static package
preflight повторил свой bounded token check при проверке readiness. Исходные
conclusions применимы к неизменённым pins.

**Composition gates.** Проверены actual code, immutable admission inputs и новая
композиция; READY/counts автора не использованы как основание. Admission inputs
только old accept, U16e36 и PFC013f. S1-08 ROLE-MAP/labels не читаются composer и не
переписывают старые messages/IDs задним числом; S1-07 остаётся source5be, где прежние
closure coordinates100/106 корректны.

Все187 UNKNOWN U row/property keys покрыты ровно один раз с exact group/harness,
source/variant/request/evidence hashes и pointers в reviewed U. Все22 PFC chains
потреблены в своих rows; source/impl/native/wrapper/clauses/frame и negative-oracle
edges не заменены одним raw-symbol pair. Record pointers/hashes независимо сверены.
Остальные gates, исходные property statuses/sites, oracles, snapshots, exceptions,
unsupported/native inventories,16 exact success bindings и113 covers сохранены.
Унаследованные226 allowed U checks/2 negative covers не переписаны.

Квалификация независимо вычислена из local gates и named companion dependencies:
14/35 rows,8 qualified companions,0/4 unions. Все111 success roles на21 rows остаются
PENDING. Least fixed point не даёт credit циклам, отсутствующим/чужим/unqualified
companions; union требует все exact N0..3 members и прежние success/cover requirements.
Итоговый admission PENDING, `CI_GO=false`. Нет hard-coded QUALIFIED по ожидаемому
агрегату и нет independent compiler/AST/MIR, B1/B2 или общего sorting theorem credit.

Pure `compose()` дважды воспроизвёл exact committed ACCEPT.json. Все27 новых composer
tests выполнены с independently pinned structured inputs вместо upstream `load()`:
потеря/подмена U/PFC edges, source/hash/status/namespace mismatches, сохранение role
gate, companion propagation/cycles и pending unions — PASS ниже hash gates.
Полный CLI load не повторялся: он повторяет уже reviewed upstream replays и читает
compressed evidence payloads.138 structured manifest files сверены по SHA256/Git;
для14 archive references проверена неизменность Git tree entries без чтения contents.
Нового archive-integrity/proof credit не присвоено.

Reproducer: `PYTHONDONTWRITEBYTECODE=1 python3 validate_delta_review.py`.
Результаты/точные hashes/anchors: [VALIDATION.json](VALIDATION.json).
