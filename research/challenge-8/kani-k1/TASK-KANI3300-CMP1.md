# KANI3300 CMP1 — реализация compound storage (product-layout с MaybeUninit-полями) в патче Kani v2

**Выдано координатором 2026-11-11, ночной GO владельца; дизайн — CMP0 (`kani3300/cmp0/DESIGN-COMPOUND.md`, черновик
`kani3300/cmp0/TASK-DRAFT-CMP1.md` в этой ветке); обязательные правки планера —
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-CMP0-REVIEW-ANSWER.md` (п.1–7, прочитать целиком,
они имеют приоритет над черновиком).** Runtime **Codex**, одна стадия. Dispatch только после exact-packet PRE-BUILD
review/GO координатора.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-cmp**, ветка **experiment/kani-k1-kani3300cmp-20261111**.
- Kani — **новый** клон **/root/kani-fix-3300-cmp** от immutable `81dd85bfce67226e283fdd9a156932e32ece080b` (tree `c5b24f0b…`),
  ветка `fix/kani-3300-cmp`. Клоны `/root/kani-fix-3300-v2` (U3B, tmux 15), `/root/kani-fix-3300`, `/root/kani-review-3300` —
  только чтение.
- Slug **kani3300**, stage `kani3300-cmp1`, owner **k1-merge**, request `kani3300-cmp1-*`. Cap **$0.60**: одна native
  `kind: kani-tests` (work ≤ 10 мин ⇒ резерв ≈ $0.540; per-test timeout в пределах envelope). Repair — только с новым GO.
  Окно: main 420 + closeout 30. Tooling base **`3bb5445d2a`** (KT2) — перенести в эту ветку cherry-pick'ом `d483dc3719` или
  слиянием с U3-веткой, как сделал U3; lane-файлы должны совпасть с `3bb5445d2a`.
- **Реализацию начать сейчас; перед dispatch** (п.6 планера): дождаться результата U3B (`/root/verify-rust-std-kani3300-u3`,
  `kani3300/u3b/RESULT-KANI3300-U3B.md` через `git fetch` + `git show`), сверить production blobs с принятой базой U3B,
  перенести исправленный frame golden и принятые изолированные PFC-контроли; если production U3B изменился — пересобрать
  дельту. Старый 4-harness buffer-positive регрессией не считать.

## Реализация и тесты

- По DESIGN-COMPOUND + правкам планера: descriptor R/S/P (попарно не пересекаются, в пределах size, покрывают его; padding,
  нулевые extent; иначе Unsupported); порядок fieldwise transfer с overlap-guard до первого изменения shadow; P=false только
  на точных диапазонах; typed-read проверки R до назначения маски; witness coverage для whole product и нескольких аргументов.
- Изменения — только `kani-compiler/src/kani_middle/transform/check_uninit/`, `library/kani_core/src/mem_init.rs`, `tests/`.
  Без Option/enum в ghost-state, второго static, изменений SKIPPED_ITEMS. Если нужно выйти за эти рамки — стоп,
  `Координатор, вопрос`.
- Manifest ≤ 20 selectors (черновик + обязательные harness п.5 планера). Build-патч — урезанный (п.7): все production-
  изменения + только выбранные тесты с зависимостями; полный набор — в клоне; SHA/tree build-пакета и полного кандидата
  раздельно; failing selector ради лимита не удалять.
- Независимое ревью production-дельты (CMP1 − v2) до PRE-BUILD (Luna/subagent по процессу), с witness-coverage вопросами.

## Приёмка и RESULT

- PASS: positive — native PASS с require_success; negative — конкретная uninit/Unsupported-диагностика из собственного вывода
  (Failed Checks); каждый unsupported-harness — отдельный итог; нет TIMEOUT/ignored. Неожиданный SUCCESS negative — блокер,
  стоп и вопрос.
- **RESULT-KANI3300-CMP1.md** в `kani3300/cmp1/` (≤ 40 строк): identities (build tree и полный кандидат), инвариант,
  diffstat CMP1 − v2, таблица, расход, предложение для core replay U8/U9 (+U1/U2, U6).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force, без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native/native-field`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh` — можно. Никаких Actions/PR/issue.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 CMP1 ЗАВЕРШЁН**, одна стадия, затем стоп.
