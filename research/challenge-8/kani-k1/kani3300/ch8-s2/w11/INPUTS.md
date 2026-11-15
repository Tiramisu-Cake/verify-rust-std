# S2 worker11 — вход и границы

Прямое поручение владельца, 2026-11-16: подготовка S2, без CI/push/локального
Rust toolchain; разрешены только новые verify/sorting_leaf*.rs и этот research-каталог.
CORE → RUNTIME-CODEX → S1 INPUTS/CHECKPOINT/INTERFACE и планы §§5/7 прочитаны.
Новый draft создан smallsort-session task create (файл task-draft); install не выполнялся:
он изменил бы файлы вне разрешённой области. Phase/lane/ledger не зарегистрированы.
Thread cwd=/root; команды используют explicit worktree; watcher/Cloud не активируются.

- std worktree: /root/verify-rust-std-ch8-s1-w11, work/ch8-s1-model-w11.
- S1/base: 3f469d3ba2e94d7129e66e53ea76df883ff9c946,
  tree 08c51f3cbe8c2e0d053001ca9ed9e5a67e3576c0; clean при входе.
- S1 parent #752: 872d5a43380752786415bc00d2a12ce0e930cb37.
- Kani read-only: 0aac16ef62da9e9d5645782d458593e5d78143ba,
  tree 9d8bc9312bf955ef126d32b819b3cd0ed105ed2b, detached в kani-upstream-ch8-s1.
- smallsort.rs Git blob при входе: f8000328aae720a6ae7a6e81cd5d5816fd73df8c.
- g0 при входе: c2f071425c04b0924450b90ce9830123ad1b8606; чужие untracked ch8-s1/integration и w0-a1 сохранены.

P1 не пройден. Статический S1 handoff не является compiler/body/contract proof.
S2 здесь — подготовленный source/interface, cost/qualification NOT_RUN; proof credit NONE.
Регистрация и attrs actual callee принадлежат13; следующий CI — только координатору.
Старые profile summaries используют другие F/order; их verdict не переносится на KeyLess.
