# KANI3300 P1 — статическая упаковка части 1 (патч v2: MaybeUninit pointee / wrap / transfer / buffer) для upstream Kani

**Выдано координатором 2026-11-11, ночной GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-AFTER-U4B-ANSWER.md` п.2, 8 и
`PLANNER-AFTER-U3-ANSWER.md` п.6).** Только статическая работа, **без сборок** (Cloud $0). Публикаций нет. Runtime **Codex**,
одна стадия.

## Объект

- Финальная v2: клон **/root/kani-fix-3300-v2**, ветка `fix/kani-3300-v2`, полный test-коммит `0ab9cc703a` (production =
  U3 repair1 `81dd85b`, плоский ghost-state). Только чтение; CMP1/CMP2 (compound storage, `/root/kani-fix-3300-cmp`) — НЕ
  включать (это часть 2).
- Новый локальный клон **/root/kani-upstream-3300** (от официального `https://github.com/model-checking/kani`), ветка
  `upstream-3300-part1`: один коммит v2 (production + отобранные тесты) поверх актуального `origin/main`; без push.
- Research-файлы — **/root/verify-rust-std-kani3300-u3**, ветка experiment/kani-k1-kani3300u3-20261111, каталог `kani3300/p1/`.

## Что сделать

1. Полный semantic diff v2 от `f046b70644` и от `origin/main`: конфликты/дрейф (если main менял `check_uninit/` или
   `kani_core/mem_init.rs` — описать и перенести аккуратно; при нетривиальном конфликте — `Координатор, вопрос`).
2. Независимое ревью инвариантов shadow / argument buffer (плоский state, return index 0, copy_by_id) / frame (DFCC assigns на
   MEM_INIT_STATE) — сабагент/Luna по процессу; findings → правки или явные ограничения.
3. Отбор тестов для upstream (≤ ~15 fixtures + goldens): только проверенные native PASS в U1/U1T/U3/U3B (перечислить build
   ID, где каждый проходил); исключить PFC-OOM пару и UNKNOWN; формат golden — устойчивый (`Failed Checks:`-форма, где
   проверка внутри core). Отформатировать все новые `.rs` rustfmt по `rustfmt.toml` Kani (обёртка
   `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`, compiler — `--edition 2024`, тесты — по
   их `compile-flags`). Новые файлы — SPDX/copyright как в Kani.
4. Черновик PR `kani3300/p1/UPSTREAM-PR-DRAFT.md` по шаблону Kani (`.github/PULL_REQUEST_TEMPLATE.md`): `Refs #3300` (не
   Resolves); поддерживаемый домен (MaybeUninit<T> за raw pointer, transmute MU→T и T→MU, массивы/срезы слотов, static
   repeat, перенос через аргументы/return), явные Unsupported (вложенные/произвольные union, compound storage, typed_swap,
   select_unpredictable, fn-pointer); **PFC ограничение точно по планеру п.8** (v2 сообщает OOM на MU-roundtrip; clean positive
   не прошёл по времени; U1-сравнение INCONSISTENT; ни «существующий upstream OOM», ни «регрессия» не установлены); проверенные
   native-результаты с SHA; строка disclosure AI-помощи; лицензионная фраза. Без упоминаний verify-rust-std PR других команд.
5. Финальный targeted native gate по manifest отобранных тестов — **подготовить пакет, не запускать** (кандидат следующей
   стадии, cap ≤ $0.80): request + build-патч (diffstat ≤ 4096) на `f046b70644` для K-1.

## Результат

`kani3300/p1/RESULT-KANI3300-P1.md` (≤ 30 строк): identities (main SHA, коммит upstream-ветки, diffstat production/tests),
итог ревью, список тестов с evidence, что вынесено в ограничения, готовность пакета native gate. Коммиты `[skip ci]`
(автор Tiramisu-Cake через `-c user.name/-c user.email`; в upstream-коммите — без `[skip ci]`, автор Tiramisu-Cake, без
Co-Authored-By), push research-ветки без force. Маркеры `REVIEW REQUEST <sha>` / **KANI3300 P1 ЗАВЕРШЁН**.

## Запреты

- Никаких сборок/dispatch/Cloud, локальных cargo/rustc/Kani/CBMC; raw logs/archives/credentials не читать.
- Push в model-checking/kani или Tiramisu-Cake/kani запрещён; Actions/PR/issue/комментарии запрещены.
- Не трогать другие worktree и клоны (только чтение). Чужие PR verify-rust-std не открывать.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
