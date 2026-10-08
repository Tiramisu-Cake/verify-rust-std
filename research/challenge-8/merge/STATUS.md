# OVERNIGHT-MERGE-26.10 — IN PROGRESS

Авторизовано владельцем до 09:30 МСК 2026-10-08 (06:30 UTC).
Ветка `overnight/merge-26.10`, entry `b0af5613`.
[Фаза/дизайн/матрица](OVERNIGHT-26.10-PHASE.md).
Ночной бюджет **2894/21600 hosted job seconds**; старые **603/1800, остаток1197** отдельно.
Последний run [37711781188](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37711781188),
proof `5bbd2ef2613106fdc38bd8aeea930cf344390275`, job113099112654,206seconds.
Нет активного run. Main/upstream/ветка первого агента не изменены.

Actual `merge_up` и `merge_down`: exact source/export/decode/refinement,
полные normal/unwind body/return/leak/dead/source gates PASS впервые.
Условный домен: positive stride, различные source cells, явный C1 pointer
и destination-option domain. Arbitrary lawful FnMut effects/answers;
normal сохраняет current source T.own/F.own, копирует выбранное current значение
и двигает cursors; callback unwind сохраняет destination option, возвращает
current source/F ownership. Нет обещания entry values, duplicate T.own или SWO.
Cleanup patch94fe2cd6/kernel100eebae/translator0e450267 экспериментальны:
positive PASS;6 proof negatives и4 frontend admission controls достигли
нужных отказов, точный classifier/матрица приёмки требует свежего запуска.
Это условное доказательство actual callee; общий generic Challenge НЕ ДОКАЗАН.

G2/A/B, native C/C++, ordinary normal/unwind и старые Rust controls PASS;
W1 22positive+5negative,9pointer bridges и C1 5positive+2stock+6negative PASS.
Wrappings/copy — явно TRUSTED bounded primitive summaries. ZST4concrete
layout цели OPEN,2reentry PASS; symbolic zero size PASS.
Полный G2 pointer trace OPEN:14checked bodies, helpers PASS, main loop
требует сохранения геометрии n=2m+e; без ослабления posts.
Caller C1 domain OPEN: alignment checked lemma failed nonlinear factorization,
заменена индукцией. Two-hole owned-array dependency подготовлена, NOT RUN.
[Ресурсный дизайн](overnight/M3-RESOURCE-DESIGN.md) сохраняет
current owners и все option scratch cells на panic; Freeze snapshot/functional
bridge отдельно OPEN. Следующий шаг — fresh full hosted matrix этих зависимостей,
затем exact bidirectional и дальнейшие resource/functional/caller obligations.
Исторические STOP/design-only/CI0 ниже не ограничивают ночную авторизацию.

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
