# KANI3300 U3B — golden frame-negative и изоляция PFC-отказов v2 (одна native-сборка)

**Выдано координатором 2026-11-11, ночной GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-AFTER-U3-ANSWER.md`, п.1–2, 5–6).**
Runtime **Codex**, одна стадия. Dispatch только после exact-packet PRE-BUILD review/GO координатора.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u3**, ветка **experiment/kani-k1-kani3300u3-20261111** (head `0c30efc5d2`),
  tooling base **`3bb5445d2a`** (KT2). Пин, toolchain, tooling не менять.
- Kani — клон **/root/kani-fix-3300-v2**, ветка `fix/kani-3300-v2`, от **`81dd85b`** (кандидат v2, production неизменен).
  **Production-код не менять**: только тесты/goldens отдельным коммитом `[skip ci]`. Патч
  `research/challenge-8/kani-k1/kani3300/u3b/kani-uninit-v2-u3b.patch` (diff от полного `f046b70644`), SHA-256 в request;
  в PRE-BUILD показать, что production-часть побайтно равна патчу U3 repair1 (sha `f3f8a82c…`).
- Slug **kani3300**, stage `kani3300-u3b`, owner **k1-merge**, request `kani3300-u3b-*`. Cap **$0.60**: одна сборка
  `kind: kani-tests`, native work ≤ 10 мин (резерв ≈ $0.540); repair не предусмотрен (факт + резерв ≤ cap — только с новым GO).
- Другие worktree (`kani3300-sel`, `kani3300-u1*`, `kani3300-u2`, `kani5072`, `kani5116`) не трогать.

## Что сделать

1. **frame-negative:** golden — под фактическое CBMC-описание из build 45287677 (`Check that *var_7 is assignable`) с
   привязкой к пользовательской записи line 22 (файл/строка в golden, если формат позволяет); ожидание не ослаблять.
2. **Изоляция PFC:** разнести `contracted_roundtrip_harness` (из `maybe-uninit-buffer-u3-positive`) и
   `contracted_uninit_read_harness` (из `maybe-uninit-buffer-u3-pfc-negative`) в **отдельные fixtures, по одному proof root**
   (вспомогательные contract declarations сохранить, если нужны для stub_verified; root выбирать через exact harness).
   Для каждого — **контрольная копия без `-Z uninit-checks`** (то же тело/contract/DFCC). Итого 4 новых selector + исправленный
   frame-negative. Исходные 4-harness fixtures оставить в патче (NOT_RUN в этой сборке).
3. Короткий вывод: `--output-format=terse` там, где golden это позволяет, чтобы причина попала в bounded excerpt (KT2).
4. Регрессия (≤ 20 всего, лучше ≤ 10): `maybe-uninit-wrap-u3-positive` (empty_harness), одна plain-negative buffer,
   `maybe-uninit-review-positive`, один U1T negative. Остальное — NOT_RUN.
5. Ожидания: positive PFC — SUCCESS (если по факту OOM/иная причина — записать класс, не ослаблять); negative PFC —
   uninit FAILURE; контрольные копии без uninit — SUCCESS (positive) / по исходнику (negative — read uninit без uninit-checks
   может быть SUCCESS; обосновать в PRE-BUILD).

## Приёмка и RESULT

- По каждому PFC root: терминальная причина (property FAILURE с Failed Checks / Kani-reported OOM / timeout), время, всё
  доступное по памяти через KT2 (`native-field`); сравнение с контрольной копией без uninit-checks. Отсутствие строк не
  считать OOM.
- **RESULT-KANI3300-U3B.md** в `kani3300/u3b/` (≤ 30 строк): identities; таблица; классификация PFC-причин; предложение:
  ready-for-review v2 / known limitation с минимальным repro / нужен фикс.
- Неожиданный SUCCESS negative — блокер, стоп и `Координатор, вопрос`.

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force, без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native/native-field`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh` — можно. Никаких Actions/PR/issue.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U3B ЗАВЕРШЁН**, одна стадия, затем стоп.
