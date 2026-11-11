# KANI3300 U3C — дифференциальная локализация PFC + modifies + uninit OOM: чистый f046 vs патч U1 (две native-сборки)

**Выдано координатором 2026-11-11, ночной GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-AFTER-U3B-ANSWER.md`, п.1–3, 5 — прочитать).**
Runtime **Codex**, одна стадия. Каждая сборка — только после exact-packet PRE-BUILD review/GO координатора.

## Вопрос

U3B (`kani3300/u3b/RESULT-KANI3300-U3B.md`, `PFC-LIMITATION.md`): на v2 два изолированных PFC root с `modifies(out)` и
`-Z uninit-checks` → Kani-reported OOM (~50 с), без uninit → SUCCESS. Есть ли OOM на **чистом production f046** и на
**production U1** (ARGUMENT_BUFFER — отдельный static)? Гипотеза планера: в v2 весь marked static (теперь с transient
argument metadata) попадает в DFCC assigns (`codegen/contract.rs`); но причинность не установлена.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u3c**, ветка **experiment/kani-k1-kani3300u3c-20261111** (от U3B `5fcc28054e`,
  tooling base `3bb5445d2a`). Tooling, пин, toolchain не менять.
- Kani: новый временный клон **/root/kani-fix-3300-u3c** от `f046b70644`; две test-ветки: `u3c-clean` (production f046 +
  тесты) и `u3c-u1` (production U1 `546bcf3` побайтно + те же тесты). Клоны `-v2`, `-cmp`, `/root/kani-fix-3300` — только чтение.
- Slug **kani3300**, stage `kani3300-u3c`, owner **k1-merge**, requests `kani3300-u3c-clean-*`, `kani3300-u3c-u1-*`.
  Cap **$0.95** на стадию: максимум две сборки `kind: kani-tests` (по одной на базу), work budget 5 мин каждая
  (резерв $0.4725 ×2). Repair не предусмотрен. Окно: main 300 + closeout 30.

## Тесты (одинаковые в обеих сборках, побайтно)

1. Два U3B repro (`maybe-uninit-buffer-u3b-pfc-positive`, `-pfc-negative`) и их `-no-uninit` копии — **файлы побайтно как в
   полном test-коммите `0ab9cc703a`** (`/root/kani-fix-3300-v2`, только `git show`).
2. **MU-free PFC контроль** (новый, 1 root): функция пишет `u16` через `out: &mut u16`, контракт `modifies(out)` + простой
   ensures; PFC root с `-Z uninit-checks` и его копия без uninit; плюс plain (не PFC) вызов той же функции с uninit.
3. Goldens: ожидаемые исходы для чистого f046 могут быть Unsupported (union args) или assigns-отказы (U1) — **писать
   goldens не под ожидание SUCCESS, а так, чтобы любой терминальный исход был классифицируем**: предпочтительно
   positive-тесты с `require_success: false` и диагностикой не задавать (или задать нейтральную, например
   `VERIFICATION:-`), а итог по каждому root снимать через KT2 excerpt/`native-field` (Failed Checks / OOM / Unsupported).
   Обосновать в PRE-BUILD.
4. Зафиксировать production hashes, fixture hashes и applied tree каждой сборки; build-патчи — только тесты (clean) /
   production U1 + тесты (u1); diffstat ≤ 4096.

## RESULT

**RESULT-KANI3300-U3C.md** в `kani3300/u3c/` (≤ 30 строк): таблица root × {clean, U1, v2(U3B)} × {uninit on/off} с
терминальным исходом (SUCCESS / Failed Checks / Unsupported / Kani-reported OOM / время); вывод по правилам п.2 планера
(существовавшее ограничение / ухудшение v2 / причинность открыта); MU-free контроль отдельно; расход; предложение
следующего шага (без перехода сразу к второму marker).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force, без `git stash`.
- Для каждой сборки — свой пакет и `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, конец хода.
- Evidence — bounded `k1g.sh summary/native/native-field`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно. Никаких Actions/PR/issue.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U3C ЗАВЕРШЁН**, одна стадия, затем стоп.
