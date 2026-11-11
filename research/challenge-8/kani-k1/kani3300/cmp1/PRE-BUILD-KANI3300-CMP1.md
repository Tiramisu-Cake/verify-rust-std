# KANI3300 CMP1 — PRE-BUILD, dispatch CLOSED

Реализация и пакет подготовлены по TASK-KANI3300-CMP1, DESIGN-COMPOUND и обязательным пунктам1–7 PLANNER-CMP0-REVIEW-ANSWER. Native/core CMP1 NOT_RUN. Полного результата CMP1 и proof credit нет.

## Identities

Research worktree `/root/verify-rust-std-kani3300-cmp`, branch `experiment/kani-k1-kani3300cmp-20261111`; вход `d34f33869d`.
Новый отдельный Kani clone `/root/kani-fix-3300-cmp`, branch `fix/kani-3300-cmp`, создан от immutable `81dd85bfce67226e283fdd9a156932e32ece080b`; другие author/reviewer clones не изменялись.
Full candidate `6ef9fd72066443f7f113440ba32f77f310520a93`, tree `97159e7c2d7ce369fb7cf7fee60c58002a7a2610`.
Build subset commit `5bd2d2bf4b7702b9a6eac0051e705c01c0d4f609`, tree `a85582af9753e386075f3ee11d012b7777ac5d98`; derived local commit, canonical publication — exact research patch and tree.
Build patch SHA256 `c819f200d3f995811fe66589f8cbd0593fe05deb8a5231442efec4f87ef295ec`; full patch and SHA recorded in BUILD-PATCH-INVENTORY.json.
Request `kani3300-cmp1-20261111-01`, SHA256 `87e38d8430faa561cf7f3f22a5194346a4a128b5f28331a38588b13990e77b5a`; root request equals snapshot.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; toolchain nightly-2026-10-23; lane files byte-equal KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
KT2 cherry-pick was already present in branch ancestry; empty attempted cherry-pick was skipped, no lane modifications.

## Реализация и invariant

Descriptor вычисляет R/S/P из target field offsets/array stride, проверяет размер каждого extent, nonzero field overlap, нулевые extent, внутренний/хвостовой padding и точное непересекающееся покрытие size. Flat storage проверяет ordinary inner layout; nested MU/union/storage-enum и непредставимые формы — Unsupported. Обычный PointeeInfo::from_ty и transmute layout comparators не ослаблены.

Typed product read проверяет только R; constructor ordinary operands сохраняют исходные typed/raw/delayed checks. Aggregate destination disjoint от каждого materialized source на всём fieldwise transfer: допускаются разные direct local roots с field/constant-index projections, без Deref; same-root/indirect aggregate отклоняется до изменения shadow. Copy/Move всего direct product переносит whole-size state. P=false записывается только по точным u8-диапазонам после transfer/load; full setter R-mask поверх S не применяется. Field ordinary writes затрагивают только поле; address/drop/delayed product setters не благословляют S.

Консервативная review-граница: assignment всего product с любым destination Deref теперь явно Unsupported до transfer, в том числе Rvalue::Use. Обычные/MU field projections через reference/raw pointer сохраняют прежний путь; whole DST transfer, новые product reinterpret casts, storage enum и arbitrary unions не добавлены.

Для каждого живого false destination byte путь выбирает source byte и следует ему через copy_by_id. Полный product использует один whole-size Store/Load. Для нескольких аргументов существует путь выбора нужного Store без последующего override, затем соответствующего Load. Невыбранный аргумент на других paths может быть blessed; это не удаляет выбранный witness. Source Copy сохраняет stay-path, destination — follow-path. Return index0 сохраняет ID/offset пока объект жив. Проверки callee/caller и непереданного обратно аргумента перечислены отдельно.

CMP1−v2 production: 4files +606/−15. Ghost-state flat six usize+two bool, один MEM_INIT_STATE, SKIPPED_ITEMS и argument protocol byte-equal v2.

## Матрица и packaging

20 file selectors,71 harness roots: HARNESS-EXPECTATIONS.json — отдельные named expectations/actual NOT_RUN. Четыре standalone positive источника включены модулями в compound-cmp1-positive; сохранены все16 harnesses, assertions, covers и исходные standalone goldens в full clone. Освобождённые slots заняты обоими изолированными U3B PFC roots с uninit on/off. Ни один failing selector не удалён.

Fixtures покрывают IntoIter Some/None/payload/empty/early-drop; product/reordered/repr(C)/ManuallyDrop/nested/generic usize и Pad; source/destination Copy; overwrite Move; callee/caller/two-argument/nonreturned/stale-return; настоящий slice unsize/reborrow; Drop::drop empty-read и живой сосед после drop ordinary field; ordinary R deinit raw padding-copy до whole-copy, field-read и product aggregate; padding после copy/call/return; zero/ZST; каждый из четырёх layout guards плюс indirect-write guard; bodyless call guard.

Для каждого отрицательного new harness golden требует собственную строку `Verification failed for - NAME` и итоговое точное число harnesses, а диагностические ожидания отдельно перечислены в HARNESS-EXPECTATIONS. Одна строка diagnostic всего файла не считается доказательством причины каждого harness. После native через bounded native/native-field нужно проверить собственные Failed Checks и source context каждого root, включая omitted_failed_check_line_count. Если retained excerpt недостаточен, итог остаётся UNKNOWN/OPEN; raw logs не читать и успешный golden-match не выдавать за полную приёмку. OOM/timeout/ignored не заменяют ожидаемую diagnostic. Unexpected SUCCESS negative — стоп и вопрос координатору.

Build patch содержит все production changes от pin и только selected fixtures/goldens + четыре module source dependencies. Каждый production/selected/dependency blob равен full candidate; baseline files сохранены. Не выбранные старые U1/U1T/partial-copy/reset/overlap/MU→T controls и standalone goldens остаются в полном клоне/full patch и NOT_RUN для CMP1. Исторические результаты не переписаны.

## Review и статические проверки

Независимый Luna HIGH semantic review: финальная production-дельта без оставшихся identified blockers; см. REVIEW-CMP1.md и REVIEW-CARRYFORWARD.json. Исправлен type-kind lifetime; indirect whole write conservatively fail-closed. Последующий test-only commit не меняет reviewed production blobs. Native/compile acceptance review не утверждает.

Штатный pinned prepare-kani на новом clean exact-pin clone PASS: apply --check --index, apply, resulting tree и наличие manifest goldens; normalized diffstat3179bytes <=4096. Отдельно validate20 PASS, rustfmt parse/format PASS, git diff --check, scope, production/fixture identities, lane equality и117 synthetic tooling tests PASS. Локальные cargo/rustc/Kani/CBMC не запускались. Raw evidence/archives/credentials не читались; Actions/PR/issues не создавались.

## U3B base gate и бюджет

Через git fetch + git show прочитан RESULT из research commit `5fcc28054e99f834db005621be0d832457a8128e`: U3B source-reports build9f964706-4b89-4340-a1ee-022aa23ecbe9, native7PASS/2ERROR; оба on-uninit PFC roots дали Kani-reported OOM, off-controls SUCCESS; full U3/PFC acceptance OPEN. Это source report, не самостоятельно установленное proof credit. Механизм/RSS UNKNOWN.

Production blobs U3B `0ab9cc703aed799f6f73d826b60281a4632ab585` равны v2; перенесены byte-equal corrected frame golden (user write line22) и все четыре isolated PFC fixtures. Старый four-root buffer-positive хранится только в полном клоне и регрессией не засчитан. CMP1 эти OOM не объявляет исправленными, selectors/ожидания не ослаблены.

Координатор, вопрос: принять ли immutable v2/U3B production как base с явно OPEN known limitation PFC/uninit для CMP1, и как допустить этот native пакет с двумя сохранёнными on-uninit selectors? Согласованного решения о base/PFC-границе пока нет; dispatch запрещён до такого решения и exact-packet GO. При изменении production базы пересобрать дельту и вернуть её тому же reviewer.

CMP1 owner k1-merge, stage kani3300-cmp1, slug kani3300; cap$0.60, spent$0/reserved$0, proposed$0.540 (=10min work+30min overhead при$0.0135/min); per-test150sec внутри600sec work envelope. Repair требует нового GO. Подготовка не регистрирует phase/резерв и не разрешает dispatch. Main420+closeout30 из задания сохраняются; новая подготовка не перезапускает окно.

После полного native acceptance отдельный core request/GO: исходные U8/U9 (+U1/U2,U6), literal uninit/function-contract flags, прежние assertions/covers/domain и source/tool identities; exact source/harness paths связать до будущего dispatch. Все core obligations сейчас OPEN/NOT_RUN.
