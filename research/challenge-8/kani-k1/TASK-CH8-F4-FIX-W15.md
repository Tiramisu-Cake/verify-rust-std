# W15 — minimal F4 fix for a standalone upstream PR

**PREPARED_NOT_ISSUED. Этот файл готовит следующую стадию; до явной выдачи не начинать.**
Это верификация корректности, не security-работа. Отвечай кратко. Fresh/current model
и owner-enabled /fast сохранить, без субагентов. STOP только реальный blocker с
evidence, не объём/контекст. STYLE-UPSTREAM-RULES.md обязателен. Пути от
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Baseline mainfaffcee3bca2770c03bd21c3bde89cc8f6f7a14e; bounded reproduction intake
06ff67af4aa1dd8df2cdbf2eec58bf3863008748, run44177926794, compiler fix absent:
initialized singletonSUCCESS13→pairedFAILURE20 (+1uninit failure), оба cfg variants;
delayed FAILURE37 и independent uninit control валидны. Actual compilation order
UNKNOWN. Source trace/fixture в wave0/f4-confirm, review8c37ad792e. Эти факты и
intake immutable; S2 и полный C2/F7 port сюда не входят.

Цель: минимально устранить утечку delayed instrumentation через shared transformer
body/cache между harnesses в одном codegen unit. Выбрать точную границу lifetime/
restore/isolation по actual source; сохранить contract/stub transformations, target
discovery, initialized-memory checks и codegen cache consistency. C2/F7 читать как
navigation, не переносить весь стек. Не отключать delayed pass/checks и не делать
safe контроль успешным ценой потери intended uninit failure. Нового generic compiler
refactor, uninit model или полного reset всех unrelated caches не добавлять.

Новый isolated **PR source от frozen main**, compiler fix + компактный upstream
regression test. Использовать observed singleton/shared/two cfg fixture; assertion
paired initialized SUCCESS и same semantic check composition со singleton, delayed
и independent unsafe controls по-прежнему intended FAILURE на shared read.
Тест должен **на main падать, с фиксом проходить**; raw13/37 counts — наблюдения,
не универсальные fixed quotas. Не выдавать cfg order за measured compiler order.
Baseline research profile/workflow deletions/runner не копировать в upstream PR.

Stage validation: source reasoning/diff/AST/shell/static/narrow Python fixtures
доступны. Local cargo/rustc/Kani/CBMC/rustfmt/full runner запрещены. Поэтому fixed
runtime PASS остаётся NOT_RUN до отдельного разрешённого CI; не писать вымышленный
результат. Подготовить reviewer-ready patch, понятное source lifecycle объяснение,
PR-DRAFT.md по стилю upstream и CI-REQUEST на **полный стандартный CI будущего PR**,
без сокращения workflow или подмены быстрым набором. Стандартные workflows сохранить. До публикации
актуальность main проверить read-only; relevant drift → явный handoff, не silent rebase.

Write g0 только `kani3300/wave0/f4-fix/`, code/tests в isolated own worktree с shared
Git objects: exact BASE/source/tree/patch hashes, regression main-vs-fixed oracle,
static VALIDATION, PR draft, full-CI plan,HANDOFF READY_FOR_REVIEW. Новые source/tests
не публиковать. Review14 после exact READY, затем отдельный GO владельца на CI.
Последняя item1 попытка28/28 не разрешена этим заданием; текущий27/28, S2 accounting
по ledger4076 без изменений. Нет CI/rerun/cancel/push/PR/messages/reservation/ledger.
Stage exact own paths, commit --only; не add-A/reset/rebase. `[skip ci]`, author
Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0> <fix source SHA>` либо blocker.
