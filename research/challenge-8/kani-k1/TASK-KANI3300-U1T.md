# KANI3300 U1T — native-проверка шести regression-кандидатов ревью U1R (+ парные положительные контроли)

**Выдано координатором 2026-11-11, ночной GO владельца (общий бюджет проекта ≤ $6.40).** Research-ветка; цель —
превратить гипотезы ревью в проверенные тесты Kani, которые войдут в upstream-патч. Dispatch только после exact-packet
PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u1t**, ветка **experiment/kani-k1-kani3300u1t-20261111** от U1R head
  `0bc1a0e8d4` (tooling base `c98d7cee0d`). Tooling, пин `f046b70644`, toolchain не менять.
- Вход: патч U1 `research/challenge-8/kani-k1/kani3300/u1/kani-uninit.patch` (SHA-256 `306851ac…`), ревью
  `kani3300/u1/REVIEW-KANI3300-U1R.md`, кандидаты `kani3300/u1/review/*.rs` (6 файлов, NOT_RUN).
- Код Kani — клон автора **/root/kani-fix-3300**, ветка `fix/kani-3300` (head `546bcf3`, дерево = патч U1). Production-
  код **не менять**; добавить **только тесты** отдельным локальным коммитом `[skip ci]`. Новый патч
  `research/challenge-8/kani-k1/kani3300/u1t/kani-uninit-tests.patch` = diff клона от полного `f046b70644` (production
  U1 + все тесты U1 + новые тесты), SHA-256 в request. В PRE-BUILD показать, что production-часть побайтно равна U1.
- Slug **kani3300**, stage `kani3300-u1t`, stable owner **k1-merge**, request `kani3300-u1t-*`.
- Cap **$0.50**: одна сборка `kind: kani-tests` (work ≈ 5 мин + 30 overhead ≈ $0.4725). Repair — только если факт +
  новый резерв ≤ cap, с новым GO. Окно: main 240 + closeout 30.
- Параллельно идёт U2 (`/root/verify-rust-std-kani3300-u2`) — не трогать; `/root/kani-review-3300` не трогать.

## Тесты

1. Шесть кандидатов → `tests/expected/uninit/maybe-uninit-review-*/main.rs` + `expected` (или по соглашению каталога),
   `--edition 2021`, `-Z uninit-checks`. Каждый negative — **конкретная** uninit-диагностика (тип и, где возможно,
   harness) в golden, а не просто FAILED. Если кандидат даёт отказ в обе стороны (overlap) — две harness или явная
   проверка обеих веток в golden.
2. **Парные положительные контроли (обязательно):** для каждого кандидата — чтение соответствующего
   **инициализированного** байта/слота по той же схеме (например, overlap: прочитать заведомо записанный слот после
   копирования), должно пройти. Собрать их в один positive fixture
   `tests/expected/uninit/maybe-uninit-review-positive/` (или `tests/kani/...`) с несколькими harness,
   `require_success: true`. Иначе инструмент, помечающий всё как uninit, прошёл бы все negative.
3. Регрессия: positive `maybe-uninit-initialized`, `maybe-uninit-scratch-array` и 2–3 существующих U1-negative
   (на выбор, обосновать). Всего ≤ 20 selectors.
4. Если кандидат по коду оказывается некорректным (ожидание неверно) — исправить тест с обоснованием в PRE-BUILD; не
   подгонять ожидания под поведение патча.

## Приёмка

- PASS: применение к свежему пину (identity дерева = локальный preflight); все negative — ожидаемая uninit-диагностика из
  собственного вывода; positive — native PASS с успешным Kani exit; нет TIMEOUT/ignored.
- **Blocker корректности:** любой negative с SUCCESS (ложный SUCCESS патча) — зафиксировать минимальный случай,
  место в коде (файл:строка) и стоп: `Координатор, вопрос`. Не исправлять production в этой стадии.
- Ложный отказ на positive — тоже результат: описать, не исправлять production.

## RESULT

**RESULT-KANI3300-U1T.md** в `kani3300/u1t/`, ≤ 30 строк: identities; таблица selectors; вердикт по каждому из 6
кандидатов (подтверждён / ложный SUCCESS / ложный отказ); расход; рекомендация для upstream-патча (какие тесты включить).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]`, push без force, глобальный git config не менять, без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh` — можно. Никаких Actions/PR/issue/
  комментариев; push в model-checking/kani или Tiramisu-Cake/kani запрещён.
- Чужие PR verify-rust-std не открывать.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U1T ЗАВЕРШЁН**, одна стадия, затем стоп.
