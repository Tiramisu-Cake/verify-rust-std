# W13 — S2/P2: три cost probes, один пакет

Все относительные пути — от `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Это верификация корректности, не security-работа. Отвечай кратко. GO на подготовку
получен сейчас: прежнее ожидание Codex reset отменено. Fresh session/current pane model,
без субагентов. STOP только по реальному blocker с evidence; объём/контекст не blocker.
Exact общие pins/бюджеты/границы: `kani3300/s2-f4-coordination/INPUTS.json`.

Новый isolated std от accepted99e; stock Kani0aac неизменён. Ты единственный writer
S2 source/verification attrs/registration/control. W11 независимо пишет offline merge
pilot, его не ждать и не копировать незаконченный материал. Frozen S1 не менять.
Scope — PLAN-CH8-ITEM2-SORTING-v2.md §5: u8/default KeyLess, без ord-panic stub:

1. Actual bidirectional_merge32, отсортированные halves, sortedness+full-value count.
2. Actual sort13 consumer с semantic swap summaries.
3. Actual general32 consumer с semantic summaries используемых helpers.

Для каждого stub перечислить actual callee/T/F/offset/allocation/init/frame/probe domain
и qualification source. Недоказанные2/3 summaries — явно opt-in DIAGNOSTIC_ASSUMED,
без formal proof credit, отдельный expected inventory. Safety/frame-only summary не
считать semantic proof. Все assumptions должны быть satisfiable: нужны exact useful
return/nonvacuity и negative corruption/weak-summary controls. Полный invariant/leaf
proof сейчас не prerequisite этого cost-пакета. Runtime sorting algorithm не менять.

Один future workflow, предпочтительно1serial job/max-parallel1. Начальные hard caps
как S1:600s/root, compile900s, group12GiB/headroom2GiB;1200s cell profile не переносить.
Посчитать group/phase/job/output/cleanup envelope и общий max runner-min; не увеличивать
старые потолки180min/job и8100s/phase. R8 ≤6GiB/root — cost target для измерения,
не подмена aggregate/group RSS. При timeout сохранять UNKNOWN и оставшиеся probes.
Измерить body/model/checker/summary, driver/backend/aggregate RSS/wall в доступных
границах; неэкспортируемую фазу UNKNOWN, group metrics не выдавать за per-root.

Reuse reviewed runner/decoder/capture/snapshots и mandatory service/error-path controls.
Согласовать actual argv/request/parser/oracles/cfg/source/tool/variant identities;
missing RESULTS/partial/timeout не превращать в PASS. Payload/YAML/actual shallow
ancestry/preflight и узкие synthetic process/error/selection tests обязательны.
Никаких local cargo/rustc/Kani/CBMC/rustfmt/full runner/solver experiments.

Write g0 только `kani3300/ch8-s2/batch/`; isolated source/control worktrees с shared
Git objects, без копирования build/target. Выход CI-REQUEST.json/md, source/control
patches и exact pins/hashes, qualification/assumption map, измеряемые поля/caps,
static VALIDATION и HANDOFF READY_FOR_W14_REVIEW. Source/tool originals immutable.
По READY coordinator выдаст14 exact commit review. Dispatch только отдельный GO
координатора после APPROVE: S2 next charge10/14, сейчас9/14; ledger не менять.
Без push/CI/rerun/cancel/reservation/публикаций/nested agents. Stage только свои пути,
не add -A/reset/rebase. `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Финал `READY <full g0 SHA> <source SHA> <control SHA>` либо реальный STOP.
