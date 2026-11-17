# W15 — F4: diagnosis, minimal reproducer, main confirmation package

Все относительные пути — от `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Это верификация корректности, не security-работа. Отвечай кратко. Fresh/current pane
model, без субагентов. GO на подготовку сейчас. STOP только по реальному blocker
с evidence; объём/контекст/отсутствие старого лога не повод бросать source/repro работу.
Pins/бюджеты: `kani3300/s2-f4-coordination/INPUTS.json`; STYLE-UPSTREAM-RULES.md обязателен.

1. Почему F4 в confirm-main43882466907 не дал результата: **один compact artifact**
   `confirm-main-43882466907-1`, bounded structured F4 six-run exits/reasons/stderr
   previews из старого producer, exact argv/edition/cargo-kani/tool paths/config.
   Исходный package: `kani3300/wave0/confirm-main/`, control2e889f7571/triggerd7e0c6bea9,
   worktree/root/kani-confirm-main-w15. Полных raw logs/archives/Cloud обходов не читать.
   Если compact недоступен, зафиксировать exact missing data/UNKNOWN; causal hypothesis
   от established cause отделить, source/reproducer/package продолжить.
2. Source trace delayed_ub/mod.rs→instrumented body→transformer cache→следующий harness.
   Historical stock0aac отдельно от current upstream main: resolve/freeze exact main
   SHA read-only в own namespace, проверить что F4 path ещё присутствует. Новый
   baseline не должен включать наш compiler fix. C2/F7 можно читать как navigation,
   не считать опубликованным main или уже доказанной минимальной причиной.
3. Минимальный upstream-style fixture с shared function, singleton harnesses и shared
   compilation. Проверять property inventory/check composition/результат для каждого
   harness; aggregate exit пары не oracle. Два файла/лексические имена не доказывают
   actual compilation order — его установить из producer metadata/узкой read-only
   diagnostic, либо честно оставить order coverage UNKNOWN. Никакого MaybeUninit,
   если defect достижим проще. Пакет исправляет old invocation/setup defect так,
   чтобы uninit control и все F4 invocations реально выполнялись.
4. Main confirmation profile: predeclare defect-present/absent/INCONCLUSIVE oracles,
   legitimate initialized control и detectable uninit control, exact per-harness
   SUCCESS/FAILURE/check identities; missing/unsupported/timeout/spawn/build error
   всегда distinct UNKNOWN. Preserve native exit/signal/stderr reason even no export.
   Reuse mandatory runner service/error controls, narrow synthetic tests для six-run
   partial/failure paths, argv/environment/preflight/YAML/pins/actual shallow ancestry.

Только подготовка подтверждения: full PR CI/публикация/широкий compiler refactor и
реализация всего F7 сейчас вне стадии. Runtime claims NOT_RUN до отдельного GO.
Никаких local cargo/rustc/Kani/CBMC/rustfmt/full runner; Git/чтение/Python/static допускаются.
Изолированный source/control на exact main с shared Git objects, без build copies.
Write g0 только `kani3300/wave0/f4-confirm/` (new): DIAGNOSIS.md/json, SOURCE-TRACE,
minimal tests/patches, CI-REQUEST.json/md с explicit caps/commands/oracles/pins/hashes,
VALIDATION и HANDOFF READY_FOR_W14_REVIEW. Old confirm-main immutable.

Владелец добавил2 item1 attempts: main confirmation затем full CI будущего PR;
текущий26/28. Это **не dispatch GO**: review14 APPROVE, затем решение координатора.
Без CI/rerun/cancel/push/reservation/ledger/сообщений/PR. Stage только свои paths,
не add -A/reset/rebase. `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Финал `READY <full g0 SHA> <main SHA> <control SHA>` либо реальный STOP.
