# KANI3300 T1a — воспроизведение: 9 roots CMP3 на той же library, что CMP4-B (одна сборка, без trace)

**Выдано координатором 2026-11-11, GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-T0-REVIEW-ANSWER.md` — прочитать целиком).**
Runtime **Codex**, одна стадия. Dispatch только после exact-packet PRE-BUILD review и GO координатора.

## Вопрос

Воспроизводится ли ложный uninit CMP3 (шаги 1–3, `IndexRange::len`, core `ops/index_range.rs:57`) в исходном наборе из 9 roots
на library tree `919cc3e2dc5fb19ea6e7f7be761914b949160a41` — том же, что в уже выполненной CMP4-B (head `c8967c5a44`,
CMP2, все шаги SUCCESS)? Это даст same-library contrast A vs B без новой сборки B.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-t0**, ветка experiment/kani-k1-kani3300t0-20261111 (от CMP4 `57bb987c6b`).
  Писать `research/challenge-8/kani-k1/kani3300/t1a/` и корневой `RUN-REQUEST.json` (по процедуре прежних стадий).
- Сначала сверить, что CMP4-B можно использовать как baseline: library tree, pin f046b70644, CMP2 production patch
  (sha `46ad585f…`) и applied tree `d356238999…`, toolchain nightly-2026-10-23, tooling KT2 `3bb5445d2a`, recipe/flags
  (uninit/controls on, inventory off, standard4/jobs1, `--harness-timeout 3m`). Расхождение — записать; если B нельзя
  надёжно сопоставить — стоп и `Координатор, вопрос` (отдельный B — только с новым GO).
- Сборка A: исходные **9 roots CMP3** (`kani3300/cmp3/`, `kani.args`/RUN-REQUEST CMP3) на этом library tree, неизменные
  CMP2/KT2/checks/таймауты. **Без** diagnostic delta, `--emit`, `--trace`, `--no-slice-formula`, новых env.
- Slug **kani3300**, stage `kani3300-t1a`, owner **k1-merge**, request `kani3300-t1a-*`, `kind: diagnostic`.
  Cap **$0.80**, резерв $0.7695 ((9×3+30) × $0.0135), одна попытка, repair не предусмотрен.
- Другие worktree/клоны не трогать (клон CMP — только чтение для экспорта/сверки патча).

## Приёмка и RESULT

- По каждому root: status, failed/total, covers, Failed Checks дословно с локацией; отдельно шаги 1–3 и калибровка U1/U2.
- Классы (п.2 планера): A FAIL на шагах 1–3 + сопоставимый B SUCCESS → same-library contrast (не механизм);
  A SUCCESS → невоспроизведение (fix не писать); controls/identity сломаны, Unsupported, timeout — отдельные исходы.
  Порядок codegen из порядка selectors не выводить.
- **RESULT-KANI3300-T1A.md** в `kani3300/t1a/` (≤ 30 строк): identities A и B, сверка B, таблица, класс, расход,
  предложение следующего шага (T1b — только предложением).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force, без `git stash`.
- Последней строкой пакета `PRE-BUILD REVIEW <полный sha>`, стоп до GO. После GO: dispatch, `k1g.sh watch BUILD`, конец хода.
- Evidence — bounded `k1g.sh summary/native/native-field/rows`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно. Никаких Actions/PR/issue.
- Это верификация корректности стандартной библиотеки Rust инструментом Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 T1A ЗАВЕРШЁН**, одна стадия, затем стоп.
