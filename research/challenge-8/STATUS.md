# VeriFast maintainer — F1 classifier admission repair

**F1 CLOSED в собственном reviewed classifier patch; integration BLOCKED.**
Start ed14b2de; exact runner base420188dd → fixed source SHA cb30a0a65e13…46d25.
Outcome switch проверяется до dict: ровно два valid unique returning/unwinding,
точные binders, no default/extra clauses, прежний literal False(location).

[Пакет/команды](verifast-review/drop-glue-v6-20261012/f1/README.md),
[patch](verifast-review/drop-glue-v6-20261012/f1/classifier.patch),
[tests](verifast-review/drop-glue-v6-20261012/f1/FIXED-TESTS.json),
[replay](verifast-review/drop-glue-v6-20261012/f1/REPLAY.json),
[independent GO](verifast-review/drop-glue-v6-20261012/f1/INDEPENDENT-REVIEW.md).
Старый F1 воспроизведён; fixed saved positive и 14 invalid entrypoint cases,
8 reused False/location cases проверены. Seven unchanged v6 saved cases прошли
source/caller/glue AST admission и scoped log replay. Bounded normal PASS сохраняется;
raw Cloud FAILURE/six INCONCLUSIVE не переписаны. New proof0/Cloud0.

V8/transport/receiver-end/caller development остаются у merge. I compatibility,
nine official admission/four receiver-end-retirement controls, actual insert_tail
panic cleanup, B1/B2/O23 остаются OPEN/NOT_RUN; profile NOT_ACCEPTED/NOT_FOR_INTEGRATION.
Main6e1a8e59/ACKea155143 и upstream as_mut_ptr/ManuallyDrop::new/tool I/PASS сохранены.
Исходный [immutable review](https://github.com/Tiramisu-Cake/verify-rust-std/tree/7567431a7877ede692d5d523ff4756a88a2fd239/research/challenge-8/verifast-review/drop-glue-v6-20261012) не изменён.

Собственная ветка review/verifast-drop-glue-f1-20261012; active merge files,
foreign worktrees/coordinator не тронуты; merge/upstream PR/profile adoption отсутствуют.
[Publication receipt](verifast-review/drop-glue-v6-20261012/f1/PUBLICATION.json),
[cleanup receipt](verifast-review/drop-glue-v6-20261012/f1/CLEANUP.json).

Сессия CLOSED в пределах 60 минут. Tested head35145044; publication/tree/manifest
проверены перед cleanup. Удалены только свои redundant /tmp copies/helper:
2 768 896 allocated bytes (≈2.64 MiB); active worktrees и merge-owned raw evidence сохранены.
