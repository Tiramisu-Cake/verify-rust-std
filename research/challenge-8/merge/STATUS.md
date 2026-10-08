# OVERNIGHT-MERGE-26.10 — IN PROGRESS

Авторизовано владельцем 2026-10-08 до 09:30 МСК (06:30 UTC).
Собственная ветка `overnight/merge-26.10`, entry `b0af5613`.
[Фаза/дизайн/матрица](OVERNIGHT-26.10-PHASE.md). Ночной бюджет **2688/21600 hosted job seconds**;
старый merge 603/1800 (остаток 1197) сохранён отдельно. Actual merge NOT PROVEN.
Исторические STOP/design-only/CI0 ниже не ограничивают эту ночную фазу.

Последняя полная матрица: run `37707794942`, proof `b8f25c1831152660fa6b2eba667dc8d8e068d2ad`.
G2/A/B, native C/C++, ordinary normal/unwind, false-unwind и точный dead-body
negative PASS. W1: 22 positive + 5 intended negative; 9 bridge и старые Rust
проекции PASS в объединённом W1/M2/C1 профиле. Wrapping и copy — TRUSTED
primitive summaries, а не доказанные тела примитивов. Copy: 5 positive,
2 stock count controls и 6 intended negative с fail-closed mutants PASS.
Concrete ZST layout: 4 цели OPEN; 2 reentry PASS; symbolic zero-size PASS.
Полный trace OPEN: checked helper bodies PASS, применены prefix-zero леммы;
доступ к Boolean-буферам и полный main post требуют следующего запуска.
Actual up/down: exact source/export/decode/refinement PASS; полный unwind post
останавливается на восстановлении source points_to/T.own после FnMut.

Новый отдельный cleanup-профиль экспериментален, НЕ ПРИНЯТ: строгий lifetime
scope сохраняет heap, explicit outcome epilogue закрывает genuine loans.
Run `37708531700`, proof `ecf30e5e`, 70 job seconds: console build failure,
не proof rejection; missing OCaml ref dereference исправлено. Новый cleanup
patch `4968245d`, kernel `100eebae`, translator `4d25e806`.
Run `37709095965`/`a38c3796`: сборка PASS; actual unwind дошёл до return/leak,
normal-copy остановлен alignment. Synthetic cleanup normal требует ремонта
epilogue; structural admission ужесточается, профиль НЕ ПРИНЯТ.
Run `37710362525`/`30adaca5`: build/старые controls PASS; valid structural
protocol отвергнут до body. Новый patch `04137273` локализует команду без
ослабления gate; trace stock-call arity исправлена. Admission НЕ ПРИНЯТ.
Run `37711140900`/`c6210938`: exact order mismatch локализован/исправлен;
новый patch `94fe2cd6`; wrong type/k/P достигли admission gate. Trace helpers
PASS, main требует natural bounds в loop. Caller-domain bridge подготовлен.
Нет активного run. Следующий разрешённый шаг — свежая hosted сборка и полная
матрица cleanup/actual/trace, затем последовательное закрытие actual merge.

---

# MERGE-STOCK-26.10 — CLOSED; wrapping STOP

2026-10-08 Moscow. Owner-authorized stock migration completed on
sync/upstream-cd371-merge fromb9f46afc, upstreamcd371e03. No active run/draft.
**603/1800summed hosted job seconds used;1197remain**:512old+91M1,
including preparation/failures/artifacts; no reset/newbudget/transfer.

G2/A/B and all9Rust projections ACCEPTED within their unchanged conditional
domains/full posts. [Result/table](STOCK-26.10-RESULTS.md), [phase](STOCK-26.10-PHASE.md),
[profile](stock-26.10/PROFILE.md), [evidence](stock-26.10/M1-EVIDENCE.json).
ProofSHA1be9c1311faf12613145e28f95a2471dec2433fe,
[run37694164542](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37694164542),
sole expected hosted job113041515221; all7otherjobs skipped.
Full positive bodies/normal posts/export/decode/refinement/integrity/return/leak/
dead-code gates and exact intended negatives pass. No tool/spec/axiom patches.

Both exact generic const-pointer wrapping_sub/add probes UNSUPPORTED:
VF1 `No such function`, after exporter/decode/refinement0; classifiers remain
INCONCLUSIVE, not intended negatives. Wrapping properties/-1/reentry/terminal
associations NOT PROVEN; Rust read-at--1 NOT RUN/NOT ACCEPTED. Stop this direction.
No unchanged retries or new semantics authorized by spare budget.

New separate admission certificatea280e8ff...7375f admits full new SmallSort,
unchanged3bodies9/9/30active statements and new lines. Old certificate/results/
profile untouched: [pre-stock checkpoint](STATUS-PRE-STOCK-26.10.md),
[historical results](RESULTS.md). Caller audit uses actual repo Git blobs,
external references separate; public ZST routes do not close generic target.

Actual merge/Challenge NOT PROVEN. Whole merge refinement/memory/copy/ownership/
FnMut/full unwind/ZST bridge remain outside phase. Next proposed decision:
separate design-only exact wrapping support/trust/admissibility and regression
gate; no implementation or dispatch pending. Documentation-only final HEAD
is distinct from proofSHA. Original branches/main/first-agent trees untouched.
