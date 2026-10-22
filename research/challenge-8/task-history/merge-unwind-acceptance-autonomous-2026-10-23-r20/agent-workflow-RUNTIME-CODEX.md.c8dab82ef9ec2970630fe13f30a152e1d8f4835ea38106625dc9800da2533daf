# Профиль среды: Codex

Решение владельца 2026-10-22: нормативные правила SmallSort нейтральны и лежат в [CORE](CORE.md); здесь только то, что зависит от среды. Среда сессии указана в CURRENT-TASK (`Runtime`); задание без этой строки выдано до разделения и выполняется в Codex. Codex и Claude одновременно не работают.

- **Вход.** Worktree `AGENTS.md` ([AGENTS-COMPACT](/root/verify-rust-std-evidence-brief/research/challenge-8/agent-workflow/AGENTS-COMPACT.md)) → CORE → этот профиль → CURRENT-TASK → CHECKPOINT/STATUS. `CLAUDE.md` и [RUNTIME-CLAUDE](RUNTIME-CLAUDE.md) к Codex не относятся.
- **Запуск.** Новую Codex-сессию открывать с **thread cwd, равным assigned worktree**: watcher проверяет metadata сессии, `cd` внутри команды её не меняет.
- **Independent review.** GPT-6 Luna HIGH (`model="gpt-6-luna"`, `reasoning_effort="high"`, `fork_turns="none"`), без вложенной делегации и автоматической дорогой замены. На вход — пакет `smallsort-session review create` и ожидаемые candidate/spec identities.
- **Ожидание Build.** `smallsort-session watch arm|start|ack` по [WATCH](/root/verify-rust-std-evidence-brief/research/challenge-8/agent-workflow/WATCH.md): `CODEX_THREAD_ID`, exact-thread `codex queue`, goal-free thread. `wait` (Claude) не использовать.
- **Субагенты.** По `/root/.codex/AGENTS.md`; вложенная делегация только по явному поручению.
- **RTK.** `/root/.codex/RTK.md`.
