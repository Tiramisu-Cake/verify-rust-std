# DIRECTFOUR — matching direct merge4 baseline без step substitutions

Runtime: **Claude Code**, tmux1, **без субагентов**. Worktree `/root/verify-rust-std-kani-directfour`,
ветка `experiment/kani-k1-directfour-20261102`, база MERGESTEP `97a252bea7ee68720b097ecf83d014e0b87d5f20`;
library commit `91d4d9f77a5a6e7f27b151839e6ac42114523a89`, tree `dc7c79bb9b2a779a6db2977f6142adfea835441b`.
Stable owner **k1-network**, старая MERGESTEP terminal; новая стадия/UUIDs, request_id `directfour-*`.
Cap проекта$88.96 (used при постановке≈$79.04), cap стадии **$1.10**, один плановый Build, максимум2 только
после compile error по правилам ниже. PRE-BUILD REVIEW + exact-packet GO координатора обязательны.
Ждать `research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` в фоновом Bash task Claude Code;
не Codex watch/CODEX_THREAD_ID, polling-субагенты или новые сессии. Evidence Brief/Select-Merge к K-1 не относятся.
Clean room: код/ветки/diff конкурентов не открывать.

## Вопрос и неизменный fixture

Проходит ли **direct** PFC merge_profile<StrictU8> с тем же fixture/post-oracle, на котором MERGESTEP composed
TIMEOUT600? Это диагностирует стоимость полного пакета adapters/verified steps/ledgers, не отдельного фактора.
Не доказывает fit merge18 и не является повтором stopped MERGESTEP G2.

T=u8; F=U8Cmp=fn(&u8,&u8)->bool, value StrictU8::CMP=reified strict_less::<u8>, ordinary `<`.
Source initialized any `[u8;18]`, target получает source[..4], halves2+2; destination отдельный
`MaybeUninit<[u8;32]>::uninit()`, offset0, writes/readable post-prefix4, tail4..32 uninit и не читается.
Independent probe через StrictU8::set_probe(any) до source:any. Sorted halves2 — только requires target PFC,
без ручных assumes, сортировки constructor-ом или probe/input correlation.

Read RESULT-MERGESTEP/TASK-MERGESTEP, positive root и register/check_merge4 в mergestep.rs,
merge_profile<StrictU8>/models в specfix.rs, raw bidirectional_merge/merge_up/down; TASK-SPECFIX и pfc_order.py.

## Разделение файлов и реализация

Новый child **network::netcomp::mergestep::directfour**, файл
`verify/network/netcomp/mergestep/directfour.rs`; в mergestep.rs только его регистрация после existing items.
NETTEN параллельно меняет другой parent netcomp.rs и свой child. Их файлы/worktree не трогать/не интегрировать.
Старые MERGESTEP targets/roots/helpers/controls/result не менять; no refactoring.

Добавить ровно один `directfour_merge4_u8`:
- `#[kani::proof_for_contract(...merge_profile)]`, `#[kani::unwind(34)]`.
- **Без любых manual stub/stub_verified annotations**; реальны и bidirectional_merge, и merge_up/down.
- Fixture/порядок setup скопировать точно из mergestep_composed_merge4_u8: set_probe(any), source18:any,
  pre=source18, uninit scratch32, dst+0, прежний register(&src,dst,probe,false,false), cmp:U8Cmp=StrictU8::CMP.
  register оставить для прежнего readonly-context post-check; внутри direct target он не используется.
- Вызов именно merge_profile::<StrictU8>(&src[..ACTIVE4],dst,cmp), ACTIVE4=4; не собственная копия merge.
- После return использовать неизменный parent check_merge4: source18/probe/readonly-context frame,
  sorted prefix4/full-value count. Outer destination-only modifies/ensures сохранить полностью.
- Шесть прежних post-return cover predicates: returned; src0<src2; src2<src0; src0==src2;
  independent probe hits source-prefix4; probe misses. Labels/предикаты сверить с исходным positive.
  **Только6 required covers**, без adapter-entered/failed-guard/step covers: их в direct proof graph нет.

Никаких изменения условий/типов/allocations/init/write-set/checks/pin/flags, дополнительных sentinels,
либо exact4 source/destination вместо18/32. Не добавлять bool composed=false в общий MERGESTEP helper
с недостижимыми adapter covers; старый composed root вообще не редактировать.
Runtime smallsort.rs/inline attributes/tooling/workflows/машина неизменны. Ordinary200;1 новый root → cfg404→405
статически. Новых negatives/повторов step leaves нет: targets и final oracle неизменны, сравнивается прямой путь.

## G1, gate, stop

Одна exact row, measurement/controls:true/jobs1/uninit off/600s/k1-standard4/16GiB/swap off,
unwind34/unwinding assertions, прежний Kani9461e07af7/nightly-2026-10-12/tooling/organizer flags.
Резерв `(1×10+30)×$0.0135=$0.540`. С NETTEN G1$0.675 суммарно$1.215, но разные stages/owners/ledger UUIDs.
At most2 project queued/running/unresolved Builds,≤1 на stable owner; current global ledger/оба slots проверить
перед GO. Не присваивать peer costs и не создавать обходной owner.

SUCCESS + all6 covers + identities match = direct4 PASS. TIMEOUT/OOM/FAILED/coverage/UNKNOWN — записать точный
результат и остановиться; не сужать inputs, не удалять outer post/frame и не увеличивать лимит/машину.
G2 только после compile error G1, тот же fixture/1 row/flags, новый review/GO и полный reserve$0.540;
own fact_spent+reserve≤$1.10 и global slots/ledger. Два полных резерва$1.080≤$1.10. G3 нет.
После resource/semantic/coverage failure repeat запрещён. MERGESTEP cover-fix/merge18/MERGE-COMP в этот task не входят.

PRE-BUILD: diff, annotation table (без substitutions), domain/init/old-vs-new oracle/covers comparison;
source/library/request/pin/tooling hashes; target ordering/pfc_order плюс ordinary200/cfg405 статически;
rustfmt/whitespace, reserve/slots. Library/research commits отдельно, [skip ci], push без force.
No local cargo/rustc/Kani/proof, Actions dispatch или deployment. Evidence — bounded K-1 summaries/rows/peaks/
targeted excerpts; raw archives/full logs/Cloud Logging/credentials/config не читать/скачивать. Историю не переписывать.

## Итог

RESULT-DIRECTFOUR.md ≤25 строк: reviewed/build/library/request identities; row/status/VT/CBMC RSS/checks/
unreachable/covers, gate; compiler/driver/process-sum RSS отдельно, own spent/reserved.
TIMEOUT cap600, VT UNKNOWN если не напечатан; OOM отдельно. Historical MERGESTEP TIMEOUT/failed gate не менять.
Быстрый PASS отделяет дорогой composition bundle от direct на этом fixture, но не ledgers от pointer/havoc/assigns;
TIMEOUT не позволяет приписать проблему только composition. Speedup composed не установлен, его VT UNKNOWN.
Не переносить на N18/32, другой CMP/F/backing/probe, generic T/FnMut, uninit/alias-validity/unwind или Part1/ordinary.
Маркеры REVIEW REQUEST <sha> / DIRECTFOUR ЗАВЕРШЁН; после одной стадии стоп, без следующего опыта автоматически.
