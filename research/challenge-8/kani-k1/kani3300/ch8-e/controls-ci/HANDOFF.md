# E controls — одна стадия подготовки

Вход: g0 `7d8ddd22f40a64053de7de13fb23a3f3303bc07a`,
`TASK-CH8-E-CONTROLS-W15.md`; прежний design `9b73c4e316` сохраняется.

Подготовлен отдельный Kani control worktree `/root/kani-ch8-e-ctl-w15`, branch
`uninit-ci/ch8-e-ctl-w15`, с единственным parent upstream0aac. Изменены только
`.github/workflows/` и `ch8-e-control/`; stock workflows удалены. В g0 добавлен
только этот `controls-ci/` пакет. Чужие concurrent изменения не включены.

10 isolated single-file fixtures дают 20 ON/OFF invocations на каждый из двух
pins в одной matrix-run: upstream0aac и SEL1 14bc. Никакого std checkout,
verify-std, smallsort patch, новой shadow/havoc модели или unchecked init summary.
E-Q refusal проверяется exact diagnostic; false predicate — named base check.
E-S не содержит loop и отделяет uncapped storage generation/read от havoc.
E-H использует реальные записи только в объявленный live byte, фиксированный
initialized witness и aliases, false hole внутри frame, false byte и initialized
sentinel снаружи, отдельные actual write/copy companions.

Pin/source/request binding, bounded logs, JSON export и conservative
classification требуют исходные exits и complete evidence. Неожиданный assigns,
pointer/overflow failure, timeout, setup error или пропущенный root остаётся
UNKNOWN/NOT_RUN. OFF uninit reads — только OBSERVE. Cover ID ↔ source-label и
успешные named loop checks требуют runtime review; receipt не даёт proof credit.

Точные commits/trees, payload/patch hashes и counts: [CI-REQUEST.json](CI-REQUEST.json).
Ожидаемые outcomes и oracles включены в frozen `CONTROL.patch`.
Static/synthetic validation и независимое review: [REVIEW.md](REVIEW.md).

В этой стадии не выполнены push, CI, публикации, ledger операции или локальные
cargo/rustc/Kani/CBMC. Все 40 runtime invocations NOT_RUN, closed proof obligations=0,
independent proof credit=NONE. Прежний STOP E для quantified-pointer ON encoding
не снят; поведение shadow после havoc остаётся UNKNOWN до controls.

Следующий шаг принадлежит координатору: проверить frozen пакет/review и отдельно
разрешить единственный E item1 dispatch, attempt1. Preparation commit `[skip ci]`
не активирует workflow; использовать same-tree sibling без skip-ci с тем же sole
parent upstream0aac, новую branch по pattern, без child/retry. Полный worst-case
sweep не обещан: run cap75min на pin сохраняет ещё не запущенные rows как NOT_RUN.
