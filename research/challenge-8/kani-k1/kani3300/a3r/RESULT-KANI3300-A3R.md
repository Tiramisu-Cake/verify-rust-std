# KANI3300 A3R
- Только TASK-KANI3300-A3R.md из research b9a4a9d60f; поверх Kani 585c93b2ff.
- Kani a0a2386001a15fecfe2facc2f6cd87f3dee13b60 закоммичен локально, без push.
- Устранён новый argument_count.max(1) → integer_max; branch-проверки count/written сохраняют инварианты.
- Pair-guard ограничен обычными вызовами; intrinsic shadow-values явно Unsupported, кроме no-effect Forget; pointer-модели сохранены.
- Custom MIR: 20 UnwindContinue заменены на UnwindUnreachable под обязательный panic=abort; assertions сохранены.
- Deinit: статически подтверждён только exact Call(Move(place)), snapshot всех args до reset; код reset не менялся.
- Все 587 golden-файлов и 13 harnesses/assertions fixture сохранены; STATIC-CHECKS.json, NOTES.md.
- rustfmt --config-path rustfmt.toml --check и diff --check PASS; clippy/-D warnings — source audit.
- Независимое Luna HIGH static ревью PASS: REVIEW.md; exact identities в review-final-packet/.
- Компиляция/clippy/Kani/CBMC/Miri/CI NOT_RUN; восстановление suite и отсутствие лишних failures требует CI координатора.
- Cloud $0; proof NONE; без builds/dispatch/raw evidence/Actions/PR/issue/comments/Kani push/stash; другие стадии не выполнялись.
A3R READY a0a2386001a15fecfe2facc2f6cd87f3dee13b60
