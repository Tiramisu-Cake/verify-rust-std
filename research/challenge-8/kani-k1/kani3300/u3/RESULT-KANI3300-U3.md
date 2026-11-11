# RESULT-KANI3300-U3
Repair build `45287677-98cb-4dc4-b98d-7ccae4782f5f`:17/20 native PASS,3 ERROR; TOOL_ERROR/gatefalse, приёмка U3 не выполнена.
Authorized head6308e4b9fb3dcc81584d3227a7c1701db855a643; Kani81dd85bfce67226e283fdd9a156932e32ece080b, pinf046b70644e113be0df9c22c2e6ea44a65a57566.
Patch SHA256 f3f8a82c2c22798361bf51bf6186aa60cadb1de68d0aa15b15ad62d601138c1c; request SHA256 2def1eb2642fe4f707dd659208c0af7ff55b2a3feba5f3ed7cc9fb99b7dcca7e.
Applied treec5b24f0b0da999d1deb9758215790382fe5e3be4; check-tooling against3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c PASS.
Kani build265s/compiletest17s, Kani0.68.0/CBMC6.11.0. Первоначальный build14dd0792:20 ERROR; сохранён отдельно.
(a) scalar/array/zero/ZST/padded Move/Copy positives passed; padding/source-read negatives passed. Transfer data-mask/padding=false сохранён.
(b) state6usize+2bool, без enum; active guards metadata; plain/clause controls passed. PFC body acceptance остаётся OPEN.
Empty_harness SUCCESS через native PASS --require-success + проверенный golden7/7 и exactsource binding; literal outcome excerpt не сохранён.
v2−U1 production2 files+129/−30; tests cU1T36 files+635/−0. Статика117tests/rustfmt/apply и Luna review без blockers не заменяют native acceptance.
FC — фактически сохранённая строка Failed Checks; D — только Description (не выдаётся за FC). Полные FC у17 native PASS не сохраняются producerом.
Все поля ниже прочитаны bounded native/native-field; source/coverage — repair1/SELECTOR-OBSERVATIONS.json и POST-BUILD-RESULTS.md.
Пути uninit/<selector>/main.rs; пять U1T FC — первые реальные matching строки, не исчерпывающий список.
| Offset: selector | Native | Фактические FC / доступные данные |
|---|---|---|
| 0: maybe-uninit-wrap-u3-positive | PASS | FC нет по require-success7/7; empty_harness SUCCESS (binding) |
| 1: maybe-uninit-wrap-u3-padding | PASS | D: uninit `u8`; полный FC не сохранён |
| 2: maybe-uninit-wrap-u3-source-read | PASS | D: uninit `u64`; полный FC не сохранён |
| 3: maybe-uninit-wrap-u3-intoiter | PASS | D: Unsupported PolymorphicIter<[MU<usize>;2]> field; полный FC не сохранён |
| 4: maybe-uninit-buffer-u3-positive | ERROR | FC detector0; contracted_roundtrip_harness failed; Complete3/4 SUCCESS, причина не сохранена |
| 5: maybe-uninit-buffer-u3-plain-negative | PASS | D: uninit `u16`; полный FC не сохранён |
| 6: maybe-uninit-buffer-u3-pfc-negative | ERROR | FC detector0; CBMC appears to have run out of memory (Kani report) |
| 7: maybe-uninit-buffer-u3-clause-plain-negative | PASS | D: uninit `u16`; полный FC не сохранён |
| 8: maybe-uninit-buffer-u3-clause-pfc-negative | PASS | D: uninit `u16`; полный FC не сохранён |
| 9: maybe-uninit-buffer-u3-frame-negative | ERROR | Failed Checks: Check that *var_7 is assignable; user-write line22, golden ждёт *outside |
| 10: maybe-uninit-buffer-u3-no-mir-unsupported | PASS | D: Unsupported shadow-carrying arguments without MIR; полный FC не сохранён |
| 11: maybe-uninit-review-positive | PASS | FC нет по require-success7/7 (включая overlap positives) |
| 12: maybe-uninit-review-argument-return | PASS | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u16` |
| 13: maybe-uninit-assume-init | PASS | D: uninit `u8`; полный FC не сохранён |
| 14: maybe-uninit-partial-copy | PASS | D: uninit `[u8; 4]`; полный FC не сохранён |
| 15: maybe-uninit-reset-alias | PASS | D: uninit `u8`; полный FC не сохранён |
| 16: maybe-uninit-review-overwrite-copy | PASS | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `[u8; 2]` |
| 17: maybe-uninit-review-overlap-copy | PASS | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8` (оба harness по golden FAILED) |
| 18: maybe-uninit-review-repeat-local | PASS | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64` |
| 19: maybe-uninit-review-reset-zst | PASS | Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u64` |
Frame FAILURE привязан к *outside на line22; user frame check сохранён, native ERROR — несовпадение имени в golden. Оmitted failed lines0/clipping0.
PFC-negative — Kani-reported OOM (не независимое измерение памяти); PFC-positive3/4, конкретная причина1failure UNKNOWN. Не объявлять их uninit PASS/FAIL.
Full IntoIter expected Unsupported native PASS; retained diagnostic PolymorphicIter<[MU<usize>;2]> family, полный порядок failed wrappers недоступен.
Для overlap/overwrite полные FC не сохранены; отсутствие дополнительных unreachable/foreign FAILURE не установлено. Координатору запрошены bounded списки.
Расход первый$0.1080+repair$0.1755=U3$0.2835,reserve0,cap$0.90; единственный repair использован, новых builds/patches нет.
Далее отдельный этап: полные negative-PASS FC retention, frame golden name binding, PFC resource/error isolation; сохранять empty/5U1T/user frames.
Compound U8/U9/select и diagnostic replay U1/U2,U6,U7–U9 остаются OPEN; native PASS полного U3/independent proof/upstream credit нет.
