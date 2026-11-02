# WONETWO — фиксированные N2 PFC для трёх length-parametric обёрток W1

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-wonetwo`, ветка
`experiment/kani-k1-wonetwo-20261102` от WONEDIAG `b7a8db4a98`. Cap 88.96. Ожидание Build —
`research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и завершить ход. request_id с
префиксом `wonetwo-`; свой spent/reserved по своим UUID. GO даёт координатор. Evidence Brief / Select-Merge к K-1
не относятся. Код конкурирующих PR не открывать.

Прочитать: `RESULT-WONEDIAG.md`, `RESULT-WONE.md`, `TASK-WONEDIAG.md` (вместе с «Уточнениями»),
`verify/wrap/wone.rs` целиком, `TASK-SPECFIX.md` (только запреты, логи, rustfmt, expect_check),
`integwrapfix/pfc_order.py`.

## Вопрос

WONEDIAG доказал три обёртки (`unstable_byte_len`, `freeze_noncopy_len`, `stable_byte_len`) на фиксированном N3.
Stable Cell уже доказан на N0..3. Проходят ли те же три target на фиксированном N2?

## Постановка (opt-in внутри `wrap::wone`; ordinary 200 не меняется)

1. Ровно три новые PFC, по образцу `*_n3` из WONEDIAG: backing4, active offset1, literal len 2, без match/len
   dispatch и без `with_backing!`. Прежние T/F/CMP/probe, targets, requires/ensures/modifies и тела не менять.
   Stable u8 — весь прежний отдельный uninitialized scratch48 и whole-slice modifies; unwind16.
2. Отдельные uncontracted N2 covers (только достижимые): return, reversed, increasing, tied-distinct, duplicate,
   independent-probe hit/miss; прежний `input_frame` после возврата. SUCCESS = intended checks + все covers.
3. Старые harnesses (включая `*_n3` и ordinary N2 wrappers) не трогать; negative controls не повторять.

## Сборка (1, резерв $0.810)

G1 measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин; в request — exact имена только трёх новых
строк → (3×10+30)×0.0135 = $0.810. Один Build без повтора. PRE-BUILD REVIEW (полный diff, pfc_order OK,
ordinary 200 и cfg-on 394 статически) → GO → build. Library commit отдельно от research, `[skip ci]`, push без force.

## Итог

`RESULT-WONETWO.md` ≤ 30 строк: rows/status/VT/RSS/covers/failed checks; сводная таблица по четырём обёрткам
(Cell N0..3; три обёртки N2 и N3). Доказано только N2/N3 в этих fixtures (ключ x>>1, backing, scratch48), не N16,
не generic T/FnMut; это не замена ordinary N2 wrappers без отдельной сверки. TIMEOUT/OOM — resource outcomes;
VT=UNKNOWN, если не напечатан. Маркеры `REVIEW REQUEST <sha>` / `WONETWO ЗАВЕРШЁН`. Один этап — затем стоп.
