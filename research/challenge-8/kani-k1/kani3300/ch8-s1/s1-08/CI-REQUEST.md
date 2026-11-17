# S1-08 — локальный кандидат для W14

Статус: **READY_FOR_REVIEW**, только подготовка, dispatch не разрешён.

- Source `99e8456d200fff1299ee5756279cddb23921dc65`, tree
  `b769b084f9982cbcb166229b29b6bd2bff136c51`, parent `5be85699b8826e3286c0bf89efb9affefac0acb5`.
- Control `9ccd882ef2460fbc97400594e7e3dfc884a4a997`, parent reviewed
  `9208b373c0a08a265fa0d7493a6529e331065271`. Tree указан в IDENTITIES.json.
- Stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`, без изменений.
- Embedded request SHA256 `a9c8f7459625cf0868735cf52f4a2b375b6e024b4fda4b45d215138c3e3fde6f`.

`CI-REQUEST.json` — полный запрос с внешним control_candidate envelope;
`EMBEDDED-CI-REQUEST.json` побайтно совпадает с control/ch8-s1-control/CI-REQUEST.json.
`ROLE-MAP.json` также побайтно совпадает с control payload. Хеши разделены без
циклической self-hash зависимости: embedded request закрепляет ROLE-MAP и payload;
внешний envelope закрепляет embedded request и control commit/tree.

127 required success bindings: 111 exact root::role labels /21 selected roots,
16 прежних exact semantic bindings, включая три complete helper instance sets.
Новые property IDs и observed S1-08 messages не назначены. Conditional N0/N1
сохранены под исходными guards; применимость отдельно указана в supplemental sites.
Required messages новых union состоят из точных пяти меток каждого из четырёх N
members; общий набор пяти логических ролей сохранён в required_success_roles.
Четыре legacy symbolic roots по-прежнему не добавлены в execution_groups.

35 rows /14 groups, порядок и max-parallel1, все 113 required covers, восемь
sole-failure negatives, companions, flags/checks/unwind/caps и budgets сохранены.
Runner изменён только в двух std pins. Decoder/export/native capture, binary-after
finalization, location exceptions и collect semantics не менялись. Ни один negative
oracle не переназначен. Обе patches применяются к новому source с прежними hashes.

Control checkout depth теперь 5: S1-08 → 9208 → b25 → 40b → stock0aac.
Export/tool depth 2; shallow regression использует настоящие file:// clones.
Workflow сохраняет existing preflight и дополнительно запускает test_s108.py.

Admission остаётся офлайн. s108_package.label_fixture — synthetic interface contract,
не classifier и не runner veto. Старый receipt и соседние accept-u/accept-pfc не менялись.
W14 review, compiler/runtime, exporter/verifier и CI — NOT_RUN; proof credit NONE.
Отдельные coordinator review/GO и compatible evidence нужны до будущего dispatch.
Push/CI/публикации/ledger/budget reservation не выполнялись.
