# E-02 — одна стадия подготовки

Вход g0 `f04b83e085`, `TASK-CH8-E02-W15.md`. Пакет single-file без std:
E-S namespace исправлен на `kani::arbitrary::any_slice_mut_unbounded::<u8>()`,
добавлен false-value control на том же symbolic-length storage без constant CAP.
Primitive H содержит write, no-write и no-loop companions, каждый ON/OFF.
Отдельная строка сохраняет byte-exact MaybeUninit MRE из ISSUE-DRAFT E-01.
Всего 6 roots, 12 invocations/pin, 24 на прежних upstream0aac и SEL1.

No-write сохраняет raw read, frame и counter update, но не требует значения17
после havoc. Это initialized primitive control, не отрицательный uninit oracle.
No-loop отделяет обычную raw-write instrumentation от loop frame. Матрица
калибрует эти различия, но сама не устанавливает causal GOTO/shadow binding.

Для MRE SEL1 ON ожидается только diagnostic reproduction:
`Check that self->value is assignable`, class `assigns`,
`library/kani_core/src/mem_init.rs:120`; все failed properties должны совпасть,
body cover — быть satisfied. Unreachable follow-on checks разрешены только
для этого отдельного diagnostic outcome с полным учётом количества checks.
Это не positive proof. Upstream ON сохраняет desired SUCCESS; известный E-01
blocker `Interaction between raw pointers and unions is not yet supported.`
остаётся UNKNOWN и не считается upstream reproduction assigns.

`check_package.py control --repo ..` из `control/ch8-e-control` разрешается в
checkout `control`. Static path preflight и 8 regressions перенесены из Profiles
fix1. Runner default checks, caps, exact pins, source/schema/stage gates,
original exits/exceptions, bounded snapshots и NOT_RUN сохранены.

Control `79baf66106a59e6ef9bcede8000fa893a5a8509d`, tree `c07b5aded52231540eab49e2a173a57ed7b903c9`; sole parent upstream0aac.
Локальная branch `uninit-ci/ch8-e-ctl-e02-w15`, worktree `/root/kani-ch8-e02-w15`.
40 synthetic tests, YAML/actionlint1.7.7 и synthetic control-env check: PASS.
Независимое Luna HIGH review: GO_STATIC_REVIEW_ONLY, findings нет.
Точные control/review identities, payload/patch hashes и результаты проверок:
[CI-REQUEST.json](CI-REQUEST.json), [REVIEW.json](REVIEW.json),
[VALIDATION.json](VALIDATION.json), [static-audit.json](static-audit.json).
`CONTROL.patch` восстанавливает tree от upstream0aac; `control-delta.patch` —
от прежнего control628ba7fd9. `audit_static.py` проверяет обе реконструкции,
тот же reviewed tree, sole upstream parent, namespace delta и exact MRE bytes.

Стадия заканчивается готовым локальным `[skip ci]` control и g0 bundle.
Координатор выполняет публикацию/единственный dispatch отдельно, используя
same-tree sibling без skip-ci с sole parent upstream0aac, новую branch по
`uninit-ci/ch8-e-ctl-*`, attempt1, без child/retry. Подготовка не является dispatch.
Полный worst-case sweep не обещан: 75min run phase/pin может оставить NOT_RUN.

Все runtime outcomes ALL_NOT_RUN; closed proof obligations0; credit NONE.
Прежние E-01/Q/alias/copy obligations и STOP E не сняты. Новая shadow/havoc
модель не создавалась. Push, CI, публикации, ledger операции и локальные
cargo/rustc/Kani/CBMC не выполнялись; чужие файлы и historical evidence сохранены.
