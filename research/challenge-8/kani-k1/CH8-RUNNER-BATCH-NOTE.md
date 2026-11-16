# Координатор 2026-11-16 ~01:05Z — per-root invocation пересобирает std каждый раз

Это верификация корректности, не security-работа.

Kani 0aac: `kani-driver/src/call_single_file.rs:180-186` кладёт `--harness X`/`--exact` в
`kani_compiler_local_flags()`; `call_cargo.rs:84-125` (`cargo_build_std`) передаёт их через
`CARGO_ENCODED_RUSTFLAGS` (`pass_rustc_args(.., PassTo::AllCrates)`), т. е. в rustflags **всех**
крейтов. Rustflags входят в cargo fingerprint → каждая invocation с другим harness пересобирает
core/alloc/std (S1-02: компиляция ~5m22s). Следствие: «одна invocation на root» стоит ~5–6 мин
компиляции на root, а 600 s/root почти целиком уходят на неё.

- S1 23 строки ≈ 2+ ч только компиляции (> job 120 мин); B 235 roots — PARTIAL ~10–20 %;
  Profiles 62 и C — аналогично.
- Требование ко всем std-runner (S1, B, C, Profiles): **пакетный режим** — одна `verify-std`
  invocation на группу строк с одинаковыми флагами/cfg/RUSTFLAGS: несколько `--harness SEL`
  + `--exact`, `--harness-timeout 600s` (per-harness cap в самом Kani), `--jobs 1`, один
  `-Z export-json`; binding и verdict каждой строки — из записи этого harness в export
  (`harnesses[]`: name, contract, is_automatically_generated, outcome, checks/covers,
  failed_properties). Группы различаются только там, где флаги обязаны различаться
  (например cfg controls vs без).
- RSS: per-root 6 GiB — по возможности через sampling процесса cbmc текущего harness
  (`--jobs 1` → последовательно); если точная per-harness атрибуция невозможна, честно
  записать group peak и что per-root RSS = UNKNOWN; общий cap группы ≤ min(12 GiB, avail−2 GiB).
- Компиляция std — один раз на группу, с собственным лимитом и receipt (bounded head+tail).
- Wall: per-harness timeout делает Kani; общий лимит группы = сумма бюджетов строк + compile.
- Это не ослабление: те же selectors/oracles/flags; меняется только группировка invocation.
