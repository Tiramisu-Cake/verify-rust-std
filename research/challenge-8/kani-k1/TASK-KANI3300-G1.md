# KANI3300 G1 — реализация: произвольный union как pointee raw-указателя (поверх части 1) + пакет native gate

**Выдано координатором 2026-11-11, GO владельца; GO планера с правками —
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-G0-REVIEW-ANSWER.md` (прочитать целиком,
п.1–7 обязательны).** Дизайн: `kani3300/g0/DESIGN-UNION-POINTEE.md`, черновик матрицы `kani3300/g0/TASK-DRAFT-G1.md`.
Runtime **Codex**, одна стадия: реализация + тесты + статические проверки + пакет сборки. **Cloud в этой стадии $0**:
стадия заканчивается на `PRE-BUILD REVIEW`, dispatch — только после ревью кандидата и GO координатора.

## Рабочее место

- Kani: новый клон **/root/kani-fix-3300-g1**, ветка `fix/kani-3300-g1` от **`657c2b245`** (финальная часть 1; production
  побайтно = c39cc1121 — проверить). Коммиты в клоне — отдельно production и тесты, автор Tiramisu-Cake через
  `-c user.name/-c user.email`, не пушить никуда.
- Research: worktree **/root/verify-rust-std-kani3300-g0** (ветка experiment/kani-k1-kani3300g0-20261111), писать только
  `research/challenge-8/kani-k1/kani3300/g1/`; коммиты `[skip ci]`, push без force.
- Пакет native gate — по образцу части 1 (`kani3300/p1/NATIVE-GATE-HANDOFF.md`, `RUN-REQUEST.json`, P1G): pin f046b70644,
  `kani_patch` = **часть 1 + G1** относительно полного f046 (не только дельта G1), проверенный applied tree, diffstat ≤ 4096
  (при превышении — reduced build patch, как раньше), tooling KT2 `3bb5445d2a`. Slug **kani3300**, stage `kani3300-g1`,
  owner **k1-merge**, request `kani3300-g1-*`, `kind: kani-tests`.
- Клоны `/root/kani-upstream-3300`, `-cmp`, `-v2` и другие worktree — только чтение.

## Обязательные правки планера (кратко; полный текст — в ответе)

1. Разделить storage extent size(U) (shadow, untyped copy) и гарантии typed transfer: typed move/argument/return/constant
   **не** сохраняют initialized padding/tail без обоснования — консервативно сбрасывать или Unsupported; preserve-mask не
   превращать в initialize-mask. Untyped `ptr::copy`/`copy_nonoverlapping` — весь extent.
2. all-ZST union (size 0) для copy/argument/return — поддержать или явно ограничить домен; thin/fat raw-pointer поля;
   guard для непокрытых volatile-операций.
3. Overlap fixtures: `[U; N]` — это G2 (запрещено); multi-slot raw-copy — через aligned raw backing без by-value
   union-container, либо явно сузить форму. Не получать SUCCESS обходом G2 guard.
4. Заморозить exact inventory: selectors с суффиксами, отдельные пути Copy/Move/ptr::read/write/unaligned/copy/write_bytes
   (или их явные отказы), флаги; для каждой negative — harness + чтение/тип + итог (отдельные fixtures, если общий golden
   не различает пары); positive — require-success. ≤ 20 selectors на пакет; если не влезает — два пакета, пересчёт бюджета.
5. Регрессии: selectors части 1 и frame golden — из переименованного набора 657c2b245; существующие union-тесты Kani.

## Приёмка стадии

- Production и тесты в клоне; статика: rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`
  (`--edition 2024`, конфиг репозитория), лицензии новых файлов, `git diff --check`; что нельзя без cargo — NOT_RUN.
- Независимое ревью кандидата (свой subagent/ревьюер, как в P1) по инвариантам G0 + правкам планера; путь к ложному SUCCESS —
  исправить до пакета.
- `kani3300/g1/`: `SEMANTIC-DIFF.md` (≤ 60 строк), `TEST-MANIFEST.json`, `RUN-REQUEST.json`, build patch + SHA-256,
  `PRE-BUILD.md` (identities, ожидание по каждому selector, cap — предложение ≤ $0.80 с резервом по формуле
  (work мин + 30) × $0.0135).
- Последней строкой `PRE-BUILD REVIEW <полный research sha>`, затем стоп. Сборку не запускать.

## Запреты

- Никаких сборок/dispatch/Cloud в этой стадии; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.

Маркеры `PRE-BUILD REVIEW <sha>` / **KANI3300 G1 ПАКЕТ ГОТОВ**, одна стадия, затем стоп.
