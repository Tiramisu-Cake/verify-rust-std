# Select-R17 — actual c2 resources and sort4

Task ID: `select-actual-c2-autonomous-2026-10-21-r17`; previous task: `select-actual-lifetime-autonomous-2026-10-21-r16`.
Owner: **Select/sort4**. Phase: `SORT4-ACTUAL-C2-2026-10-21-R17`. Lane: `o26-sort4-c1-current-recovery`.

## Завершение R17 — поручение владельца 2026-10-22 (приоритетно)

Сессия R17 прервалась около 21:18Z; main `22:06:19Z` и absolute `22:36:19Z` 2026-10-21 истекли. Это поручение — **только closeout R17**: Cloud budget 0s, окно до 30 минут wall от начала работы. Новых Builds/request/submit/cancel/retry, review новых кандидатов и новых гипотез нет. Разделы Goal/Special bounds ниже — история R17, не разрешение.

Состояние, прочитанное владельцем (проверь сам, расхождение — UNKNOWN):
- S4 `27e8bfac-eb5f-4cf4-ae89-18bacd16eb90` (candidate `51c4368b`) terminal FAILURE 21:05:08Z→21:13:53Z; в **незакоммиченном** ledger accounted 525s, used1995/remaining1605, status всё ещё AUTHORIZED.
- `/root/smallsort-ci-coordination/active.json` ещё держит own reservation `dispatch-774eeb6818d045af9052d29f889c6a06` со status QUEUED.
- HEAD `a6550c20` (S5 unselected full-borrow fix + `S5-review-spec.json`) не опубликован, origin на `462539c3`; S5 review и Build не выполнены.
- CHECKPOINT ещё HANDOFF/WAITING S4; S4 evidence/Brief records не сохранены.

Шаги:
1. Проверь thread cwd/branch/HEAD/dirty; если для старого thread `01a15ffc-dbe5-7523-b5b1-d3dc37016e06` armed watcher — `watch status`, затем `stop` (Build не отменяет).
2. Один штатный own `control.py status 27e8bfac-eb5f-4cf4-ae89-18bacd16eb90` с R17 phase/ledger/state-dir `/tmp/select-r17-cloud-state`: подтверди terminal/accounting и освобождение own reservation. Live `active.json` вручную не править; при отказе — точный ответ и UNKNOWN.
3. `smallsort-brief` по S4: сохрани `S4-evidence.json`/S4-brief/observations с file/index SHA и coverage. Подтверди или уточни leak base0/1 `full_borrow` из `S5-UNSELECTED-BORROW-FIX.md`; без raw logs/archives.
4. Закрой ledger по образцу R16: CLOSED, `closed_utc`, retired 1605 (retired = remaining после accounting), carry0, closure_reason «interrupted, absolute expired». Spent/used не переписывать.
5. CHECKPOINT → CLOSED (0 remaining, active/unresolved 0): S4 claim SOURCE_REPORTED; blocker по S4 Brief; S5 `a6550c20` — artifact **unverified, unreviewed**, proof credit0; next — новая R18 (S5 review → Cloud). Обнови `assignment_sha256` под этот текст, `checkpoint validate` и `write-views`.
6. Закоммить только свои R17 файлы (ledger, CHECKPOINT/STATUS/CURRENT, task-history/select-actual-c2-r17). Чужие dirty policy docs и `A1-PACKAGING-R7-SESSION-2026-10-20.md` оставь как есть. Обычный push ветки (с `a6550c20`), проверка полного remote SHA; без force/rebase.

Готово, когда ledger CLOSED, own reservation освобождена и checkpoint опубликован — это условие `smallsort-session task install` для R18.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-select-night` on branch `research/night-select-sort4-cloud-2026-10-09`; baseline `5dde9e6e71f5d4eadbbf2e32d4c17945b831f1f5`; source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`.
Tool worktree `/root/verifast-select-sort4-c2-bind-20261010` on `challenge8/select-sort4-c2-bound-20261010` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-LIFETIME-R16-PROFILE-2026-10-21.json` SHA-256 `d68d124131d7b242afb367c20826eb29ca2ad8f500aa99f1faddfee11230bf24`. New ledger path: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json`; previous closed ledger: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-LIFETIME-2026-10-21-R16.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R17 и Builds разрешены. Автономно продвигай actual sort4 normal/unwind в рамках CORE; ближайшая цель — checked c2 resource recovery с controls и точной call-site attribution. Продолжай по миссии в оставшемся окне.

1. Repair HRTB routing for controls before Cloud: exact actual-body controls retain opt-in; unrelated helpers do not inherit it. Keep strict route guards, service failure cases, and HRTB-off contrast.
2. Bind c2 ordered operands (3,2) using fresh per-call lifetime, actual precreated refs, tuple/current-F and four-current-owner normal/direct-unwind recovery; preserve checked kernel binding. Reject wrong receiver/order/ref/index/debt/marker.
3. Advance c3–c5 and selector/copy composition when justified. After target gates pass, run required controls/mini7/fresh26 on final pins, then stable Freeze caller. Report partial progress without full-body credit.

## Special bounds

- Effective tool is the full R16 overlay/spec/profile chain, not base SHA alone. Preserve R13 limits and strict entry/exit/escape/init/leak/unwind checks; keep all5 calls/8selects/4copies.
- Tool WT contains foreign edits: use pinned Git objects; develop in project/isolated WT. Kernel resource equality may prove binding; independent receipt still attributes exact ordered calls. No address-only or assumed bridge.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Actual c2 missing precreated-ref token for base+3; required controls stopped by HRTB routing error. (verified/lib.rs:202; aliasing.rsspec:88) [Build acd8e010-16b8-4b58-9501-083cb10b595f]
Next: Fix HRTB control routing; establish actual c2 resource/recovery gate and discriminating controls.

## References

- [S5 diagnosis / next experiment](task-history/select-actual-lifetime-r16/NEXT-AFTER-S5.md)
- [Callback protocol and kernel binding qualification](task-history/select-actual-lifetime-r16/NEXT-CALLBACK-PROTOCOL.md)

## Отчёт агента

**select-actual-c2-autonomous-2026-10-21-r17 · select-sort4 · SORT4-ACTUAL-C2-2026-10-21-R17 · HANDOFF**
Updated: 2026-10-21T21:05:46.279159+00:00. Baseline source/tool/profile: `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `d68d124131d7b242afb367c20826eb29ca2ad8f500aa99f1faddfee11230bf24`.
Dates: T0 `2026-10-21T20:06:19Z`; main `2026-10-21T22:06:19Z`; absolute `2026-10-21T22:36:19Z`. Budget 3600s: 1470s spent, 0s retired, 2130s remaining including reservations.
Active Build IDs: 27e8bfac-eb5f-4cf4-ae89-18bacd16eb90; unresolved: none recorded.
Blocker: Cannot read a ghost variable in a non-pure context. [Build `85dac5bf-ff84-4215-84c4-e08943bf882a`]
Next: WAITING: S4 Build 27e8bfac-eb5f-4cf4-ae89-18bacd16eb90. Arm exact-thread watcher; on event first ack before checkpoint mutation, then Evidence Brief and exact target/control diagnostics. Existing R17 T0/account/window only, main22:06:19Z absolute22:36:19Z. No proof credit from metadata.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
