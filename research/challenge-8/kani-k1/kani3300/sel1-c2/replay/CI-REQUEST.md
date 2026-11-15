# B — подготовлено, NOT_RUN / PENDING_FREEZE

C2 B′ runner из `/root/kani-fix-3300-c2-gateb-w15` @0d6282ad1; accepted run43683557088.
Std exact70ba5befc617627073738e26cb1466bd4fb76e41; test-only package6075e7ce17179f45642c9ffe8fe09e3ec9395726.
Patch SHA256473526895d6d57a99bd356a060195745cc6aba9ee2b70fcc7ae90fecb6676f06.
Все пять patched-file hashes сверены с immutable Git objects; diff в library ограничен test files.
Production std, preconditions, comparator/oracle не меняются. PFC closures остаются настоящими closures.

Шесть exact rows в CI-REQUEST.json, sort4-closure-on ровно один раз; raw-legal парен raw-negative.
ubuntu-24.04, jobs1/max-parallel1, uninit ON, object-bits12, valid-value OFF, cfg controls ON;
организаторские flags и штатные solver/slicing/checks, включая --no-assert-contracts.
2400s/root, 60min/job, 6 serial jobs, envelope21600s/360 runner-min, без retry.
Runner сохраняет exit/signal, wait4 RSS, stdout/stderr, export, argv/environment, source/std/runtime hashes,
атомарный partial receipt до fallible postprocessing и post-run source/std validation.
Вердикт UNKNOWN до ручной проверки; raw-negative exit1 отдельно от сбоя обвязки, не автокредит.

Source coverage skeleton: старые504 paths/6 subtrees расширены SEL1 fixtures и docs до570/7;
**все** source hash values unresolved. После freeze пересоздать полный inventory, не подставить только tool SHA.
См. ROW-ORACLES.md и ../quick/REBIND.md. B запускает coordinator после принятого A на той же голове.
