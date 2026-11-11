# KANI3300 B2b — probes ready
- Только TASK-KANI3300-B2B.md из b2ab6fab6c; Cloud $0.
- Reviewed candidate: 8f09ae8085e6d2884ecee1402019491038288bc7.
- Четыре custom MIR bin: Move/Copy × read/write; прямой source place, pre-transfer raw pointer, post-return byte read.
- EXPECTATIONS.md: pinned source:line; Move прогнозируется uninit/UB, Copy сохраняет source, запись callee отдельна.
- Независимое Luna HIGH static review PASS, blockers нет: REVIEW-B2B.md; exact packet/spec сохранены.
- Static TOML/pin/29-bin/matrix/order/expectation checks и candidate git diff --check PASS.
- Компиляция, actual MIR/Miri NOT_RUN; proof credit NONE; запрещённых запусков/действий не было.
- Следующий шаг только CI координатора; B2b завершена, B3 здесь не выполнялась.
