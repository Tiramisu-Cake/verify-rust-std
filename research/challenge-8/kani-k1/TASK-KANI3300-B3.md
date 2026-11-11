# KANI3300 B3 — ZST union arm: воспроизвести CBMC abort на чистом upstream (аудит §4.1)

**Выдано координатором 2026-11-12.** Основание (только чтение): аудит `/root/verify-rust-std-kani3300-g0/research/
challenge-8/kani-k1/AUDIT-REPORT-KANI3300-RU.md` §4.1 (абзац про `d760bad`), ответ планера
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/audit/PLANNER-AUDIT-RESPONSE.md` (W2-B3), заметки
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r6/NOTES.md`, G1-фикс `d760bad` в
`/root/kani-fix-3300-g1`. Runtime **Codex**, одна стадия, **Cloud $0**; исполнение — узкий fork CI координатора.

## Контекст

В G1 CI-бисекция показала: union с arm `zst_array: [(); 2]` + `write_bytes` + typed `ptr::write(&mut dst, ptr::read(&src))`
→ **CBMC failed with status 134**. G1R6 исправил это в общем union codegen (`d760bad`: ZST payload в padded wrapper как
empty struct). Неизвестно, есть ли abort на **чистом upstream** без G1 — тогда это отдельный backend-баг/PR.

## Что сделать

1. Kani: клон **/root/kani-fix-zst-b3**, ветка `fix/zst-union-codegen` от upstream `bf9c58e662` (автор Tiramisu-Cake
   через `-c`, не пушить, нейтральные сообщения).
2. Коммит 1 — **только тесты-репро** в `tests/expected/uninit/zst-union-arm-*` (путь должен содержать `uninit`, чтобы попасть
   в узкий CI): (a) без `-Z uninit-checks`; (b) с `-Z uninit-checks`; формы: `[(); 2]` arm с typed copy, ZST с повышенным
   alignment (`#[repr(align(8))] struct Z;`), ZST arm на ненулевом offset, all-ZST union, индексация `[(); 2]`.
   Expected-файлы — по семантике (успешная верификация/ожидаемые свойства), а не «как получится».
3. Коммит 2 — перенести исправление из `d760bad` (только backend-часть: `codegen/typ.rs`, `cprover_bindings`), без G1.
   Координатор прогонит узкий CI на коммите 1 (есть ли abort на base) и на коммите 2 (исправлено ли).
4. rustfmt-обёртка `--config-path rustfmt.toml`, diff --check, clippy/`-D warnings` source audit, независимое ревью.

## Результат

`kani3300/b3/RESULT-KANI3300-B3.md` (≤ 15 строк) в этом worktree, research-коммит `[skip ci]`, push без force.
Последними строками `B3 TESTS <sha коммита 1>` и `B3 FIX <sha коммита 2>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
