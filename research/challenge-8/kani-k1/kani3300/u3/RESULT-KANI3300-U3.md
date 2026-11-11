# RESULT-KANI3300-U3 — repair 1 PRE-BUILD
Предыдущий build14dd0792-1c06-47be-b931-94f6096a664a:0/20 native PASS,20 ERROR; native acceptance отсутствует.
Repair PREPARED/NOT_RUN; dispatch только с новым exact GO. Старые evidence/ledger не переписаны.
Kani pin f046b70644e113be0df9c22c2e6ea44a65a57566; candidate `81dd85bfce67226e283fdd9a156932e32ece080b`.
Patch SHA-256 `f3f8a82c2c22798361bf51bf6186aa60cadb1de68d0aa15b15ad62d601138c1c`.
Request kani3300-u3-repair1-20261111-03 SHA-256 `2def1eb2642fe4f707dd659208c0af7ff55b2a3feba5f3ed7cc9fb99b7dcca7e`.
Tooling base `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` принят, cherry-pick d483dc3719 без изменений; будущий check-tooling против base3bb5445d2a.
Applied tree `c5b24f0b0da999d1deb9758215790382fe5e3be4` совпал с candidate; Kani pin/toolchain/lane gates прежние.
Repair vs failed v2: mem_init.rs+37/−36; tests2 files+5/−1. v2−U1: production2 files+129/−30, tests36 files+635/−0.
State:6usize+2bool, без enum/union; ty_layout обход struct по real offsets и primitive chunks оставляет padding=false.
Active guards metadata; Store пишет payload до active, forcedreturn0/nondet args; Load snapshots/copy/clear или прежний unmatched bless.
SKIPPED_ITEMS, compiler и DFCC unchanged; новое trusted setup исключение/второй marker не вводились; frames не ослаблены.
PASS static:validate20,fresh apply/tree,rustfmt36,diff-check,scope,tooling equality; KT2 Python unit/service117 PASS.
Independent Luna HIGH repair review: no static blocker; native NOT_RUN, не proof credit.
KT2 native-field старого build читается, но старые excerpts не сохраняли actual Failed Checks; ретро cause/status не установлен.
Ниже все repair selectors NOT_RUN; uninit/<selector>/main.rs, указаны только ожидаемые результаты.
| Selector | Ожидание repair |
|---|---|
| maybe-uninit-wrap-u3-positive | 7 SUCCESS incl. empty setup, scalar/array/zero/ZST/Move/Copy |
| maybe-uninit-wrap-u3-padding | FAILURE/uninit u8 padding |
| maybe-uninit-wrap-u3-source-read | FAILURE/uninit u64 typed source |
| maybe-uninit-wrap-u3-intoiter | FAILURE/Unsupported compound MU field |
| maybe-uninit-buffer-u3-positive | 4 SUCCESS plain/PFC/clause/nested/2args/return0/stale |
| maybe-uninit-buffer-u3-plain-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-pfc-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-clause-plain-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-clause-pfc-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-frame-negative | FAILURE/Check that *outside is assignable |
| maybe-uninit-buffer-u3-no-mir-unsupported | FAILURE/Unsupported arguments without MIR |
| maybe-uninit-review-positive | 7 SUCCESS incl. both overlap positives |
| maybe-uninit-review-argument-return | Failed Checks: uninit u16 |
| maybe-uninit-assume-init | FAILURE/uninit u8 |
| maybe-uninit-partial-copy | FAILURE/uninit [u8;4] |
| maybe-uninit-reset-alias | FAILURE/uninit u8 |
| maybe-uninit-review-overwrite-copy | Failed Checks: uninit [u8;2] |
| maybe-uninit-review-overlap-copy | 2 failed harnesses + Failed Checks: uninit u8 |
| maybe-uninit-review-repeat-local | Failed Checks: uninit u64 |
| maybe-uninit-review-reset-zst | Failed Checks: uninit u64 |
IntoIter expected Unsupported; его фактический следующий blocker и закрытие U8/U9 не подтверждены.
После будущей сборки: summary → check-tooling3bb5445d2a → excerpt/native-field; выписать все Failed Checks overwrite16 и обеих overlap17.
Оmitted/clipped coverage и unreachable/foreign FAILURE указать отдельно; отсутствие в excerpt не считать отсутствием свойства.
U1T padded-manually-drop и прочие U1 вне manifest NOT_RUN, полный перечень NOT-RUN.json; все5 обязательных U1T negatives сохранены.
Расход$0.108,reserve0; proposed repair$0.540,total$0.648≤cap$0.90; новый exact GO пока не получен.
После native PASS — отдельное review и отдельный diagnostic replay U1/U2,U6,U7–U9; compound/select остаются следующим scope.
