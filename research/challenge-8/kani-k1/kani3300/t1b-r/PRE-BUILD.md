# KANI3300 T1b-R — A2 PRE-BUILD REVIEW
Task base 5b1dc4d73262bca86913e43d1fcac7f3a3561d6d; только repair/sweep/review/пакет; Cloud этой стадии $0, phase/reserve/dispatch NOT_RUN.
Research /root/verify-rust-std-kani3300-t0, experiment/kani-k1-kani3300t0-20261111; активные requests/ledgers и пакет B не изменены.
Kani /root/kani-fix-3300-t1, diag/kani-3300-t1; commit 989f72351c2b5c5f3b5117315fc84f502e66d904, автор Tiramisu-Cake; без push.
Repair: только `let instances: Vec<Instance> = items`; patch SHA256 5a65b85f92ba35cf3fb4fc5cc293b208c7f64fa356613a5e8452146dde1abd27.
Kani pin f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23, Rust7189d39d9ce936881b8132c6addeaf3e295cd455.
Production CMP2 b1f0105c0390fb55081e3d186fa286d23867b585; patch SHA256 46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4 неизменён.
Production applied tree d356238999ab436ddc1dd7ffa845b0db214aa53e; reverse diagnostic восстанавливает его точно.
Diagnostic patch SHA256 50d6afeb245b1b48cc9847626ce9beb151750b05b37b5326e145779d19626ab8 (51847 B).
Combined patch SHA256 0e1dd370789a196cf7f7eadad4fe850910f83fd38cbf6e306394c6c247588298 (151237 B).
Expected combined applied tree 53927d9bc0ccbff8183aa91ffb6c29d1c8a74465; вычислен private Git index, компиляция NOT_RUN.
Library tree 919cc3e2dc5fb19ea6e7f7be761914b949160a41; fixture SHA256 bd6d51c7ad634644d5e8fc16b539cd84b2eedb6101d52692c4d7d0fb3545e8a6.
Tooling base3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c, extension c3468b3bd84f4a91a2ea99fa0fcea317bd98e681, tree6446f4d16bf0dad3a7e38a00347835b986694e66 — неизменны.
Tooling extension SHA256 55aeeefe592b87f46059db08c5abfb5578a58be0b3c644dda764dfecf7361de0; manifests ../t1b/TOOLING-{BINDING,FILES}.json.
Cloud recipe SHA256 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81; runner/pins hashes проверены по прежнему manifest.
A2 request kani3300-t1b-a2-20261111-01; SHA256 73903bb3f80c34492d575d40d74a4552e4e2d9a55149e578fe05dde01d55035e.
kind diagnostic, slug kani3300, stage kani3300-t1b, owner k1-merge; все 9 roots A с прежними expectations, включая cmp3_index_range_len и calibration pair.
Recipe: uninit/controls on, inventory off, gcb-e2-standard-4/jobs1; единственное разрешённое изменение recipe — harness timeout 3m → 2m.
T1a bounded summary fd4c3316: roots 0.220/1.797/1.905/1.717/1.309/3.072/33.679/0.570/0.620 s; максимум33.679s <120s (запас3.56×).
T1a whole verification119.49s, Kani build257s; источник ../t1a/evidence/fd4c3316/summary.md и HARNESS-OUTCOMES.json; это прежние измерения, новая diagnostic compile стоимость неизвестна.
A потрачено $0.081; остаток cap$0.80=$0.719. A2 (9×2+30)×$0.0135=$0.648 ≤$0.719; суммарный worst-case$0.729, остаток$0.071.
Все roots сохранены для контекстного контраста; overhead30min сохранён. Новый timeout по измерениям, не основание трактовать возможный timeout как PASS.
Effective runner argv scripts/run-kani.sh --path /workspace/src --kani-args + kani-A2.args; exact9 harnesses/-Z uninit-checks/--harness-timeout 2m/--jobs=1/terse.
RUSTFLAGS=--cfg kani_smallsort_controls; TRACE_DIR=/workspace/src/k1-out/trace; FILTER прежний из request; KANI3300_TRACE_ID=request SHA256, KANI3300_TRACE_STAGE=kani3300-t1b.
Полные validated env — EFFECTIVE-INVOCATION.json; actual compiler/rustc/CBMC argv UNKNOWN до разрешённого запуска; runtime trace/slicing/solver flags не добавлены.
Полный static sweep SWEEP.md; rustfmt9/source+text diff/API hashes/Git apply(--whitespace=error)+reverse/request/budget PASS; independent Luna HIGH compile-focused STATIC PASS (REVIEW-KANI.md).
Compilation/-D warnings/MIR-GOTO equivalence NOT_RUN; proof credit NONE; concrete object/offset/R/runtime causality UNKNOWN.
До GO координатор отдельно проверяет diag на fork CI и live budget/deadline/slots/preflight; эта стадия ничего не запускает, B требует отдельного решения.
