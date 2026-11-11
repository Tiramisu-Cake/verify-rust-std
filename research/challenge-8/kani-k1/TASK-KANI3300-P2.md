# KANI3300 P2 — упаковка части 1 для upstream PR: имена тестов, тело коммита, rebase, статические проверки

**Выдано координатором 2026-11-11, GO владельца.** Runtime **Codex**, одна стадия. Cloud **$0**, без сборок.
Контекст: P1 (`kani3300/p1/RESULT-KANI3300-P1.md`, `UPSTREAM-PR-DRAFT.md`, `TEST-MANIFEST.json`), P1G 15/15 PASS
(`kani3300/p1/RESULT-KANI3300-P1G.md`).

## Рабочее место

- Kani: клон **/root/kani-upstream-3300**, ветка `upstream-3300-part1`, сейчас один коммит `c39cc1121` на main `bf9c58e662`.
  Ветка ещё не публиковалась — можно переписывать локально (amend/rebase), итог — **ровно один коммит** поверх main.
- Research-записи: worktree **/root/verify-rust-std-kani3300-u3** (ветка experiment/kani-k1-kani3300u3-20261111),
  писать только `research/challenge-8/kani-k1/kani3300/p2/`.
- Другие клоны/worktree не трогать.

## Что сделать

1. **Имена тестов.** В `tests/expected/uninit/` переименовать каталоги без внутренних меток (`-u3-`, `review-`, прочие
   стадийные слова): короткие описательные имена в стиле соседних тестов (`git mv`). Если имя каталога/пакета/harness
   где-то упоминается (goldens, Cargo.toml, комментарии) — поправить согласованно. Содержимое `main.rs` и `expected`
   по смыслу не менять; каждое отличие кроме переименования — перечислить и обосновать.
2. **frame-negative (~120 с).** Только оценить статически, можно ли сократить без потери проверяемого (на что именно
   уходит время). Сам тест **не менять** — предложение в RESULT.
3. **Rebase** на актуальный `origin/main` (`git fetch origin main`), если нет конфликтов в затронутых файлах; при
   конфликтах — остаться на `bf9c58e662` и записать почему. Production после rebase — побайтно та же семантика
   (показать `git range-diff` или diff production-путей до/после).
4. **Тело коммита** (англ., автор Tiramisu-Cake <igkharin@gmail.com> через `-c user.name/-c user.email`, без
   Co-Authored-By, без `[skip ci]`, без внутренних стадий/ссылок на research): заголовок прежний; 5–10 строк — что
   поддержано, что остаётся Unsupported, где тесты; `Refs #3300`.
5. **Статические проверки без cargo:** заголовки лицензии в каждом новом файле как у соседних тестов
   (`// Copyright Kani Contributors` / `// SPDX-License-Identifier: Apache-2.0 OR MIT`); rustfmt через обёртку
   `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024` для изменённых
   `.rs` (production и тесты; конфиг rustfmt репозитория учитывать); `git diff --check`; отсутствие внутренних меток
   (`u1`/`u3`/`v2`/`cmp`/`review`/smallsort/verify-rust-std) в коммите. Что проверить нельзя без cargo (clippy, build) — так и записать.

## RESULT

**RESULT-KANI3300-P2.md** в `kani3300/p2/` (≤ 30 строк): финальный SHA ветки, база (main SHA), diffstat; таблица
старое→новое имя; отличия кроме переименований; итог rebase; результаты статических проверок; текст тела коммита;
предложение по frame-negative. Research-коммит `[skip ci]` (автор Tiramisu-Cake), push research-ветки без force.

## Запреты

- **Не пушить** ветку Kani никуда (push в форк и CI делает координатор). Никаких Actions/PR/issue/комментариев.
- Никаких сборок/dispatch/Cloud, локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <research sha>` + финальный SHA ветки Kani / **KANI3300 P2 ЗАВЕРШЁН**, одна стадия, затем стоп.
