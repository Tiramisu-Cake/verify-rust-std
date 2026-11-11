# KANI3300 U3C — u1 PRE-BUILD

PREPARED; native NOT_RUN. Только отдельный exact-packet GO координатора разрешит dispatch.
Task: ../../../TASK-KANI3300-U3C.md; планер PLANNER-AFTER-U3B-ANSWER.md п.1–3,5 прочитан.

- Research branch: experiment/kani-k1-kani3300u3c-20261111; вход 385a116e6f2a81654ec19a6d17ea2010984f4251.
- Kani pin: `f046b70644e113be0df9c22c2e6ea44a65a57566`; локальная test-ветка `u3c-u1`, commit `e12d8d847b6566173446b68aab3515e09ef124e1`.
- Applied tree: `8ebcafd3e90f32fe7b5586d7a0d2f3ea6ddb360e`; patch SHA256 `c462f297d25297b69bdd0c99b520772a7906700c5886a0118e77ed83efbcc981`.
- Request: `kani3300-u3c-u1-20261111-01`; SHA256 `cce17bc34ab85fc5467689ac48403c6340cb607ea590743e96ebad0a246b2a4d`.
- Production: 7 файлов побайтно равны production 546bcf30379b9b2894f94b1305d5277cc5b4574c; прежние U1 test additions не включены.
- Tooling/pin/toolchain побайтно прежние, tooling base `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
- Production diff U1 SHA256: `c529f960ae6ae8cc1287d0006b20c30885df5208a33da9c4bed571984fce5b1d`; все file hashes — ../IDENTITIES.json.
- Fixture bundle SHA256: `e2339446d3cfd421e73b54534174768f5b311ab0f7cc2152198793bd02290438`; все 14 файлов одинаковы между пакетами.
- Diffstat 1346 <=4096 bytes; validate7, fresh pinned prepare-kani/apply/index/tree, diff-check PASS.

## Семь точных selectors (порядок исполнения)

|offset|fixture under tests/expected/uninit|exact root|uninit|
|---:|---|---|---|
|0|maybe-uninit-buffer-u3b-pfc-positive|contracted_roundtrip_harness|on|
|1|maybe-uninit-buffer-u3b-pfc-positive-no-uninit|contracted_roundtrip_harness|off|
|2|maybe-uninit-buffer-u3b-pfc-negative|contracted_uninit_read_harness|on|
|3|maybe-uninit-buffer-u3b-pfc-negative-no-uninit|contracted_uninit_read_harness|off|
|4|mu-free-u3c-pfc|write_u16_harness (proof_for_contract)|on|
|5|mu-free-u3c-pfc-no-uninit|write_u16_harness (proof_for_contract)|off|
|6|mu-free-u3c-plain|write_u16_harness (proof)|on|

Четыре исторических main.rs побайтно равны `0ab9cc703aed799f6f73d826b60281a4632ab585`.
On/off source пары отличаются только удалением `-Z uninit-checks`; тело/контракт/DFCC/exact root сохранены.
MU-free функция пишет 7 через out:&mut u16, modifies(out), ensures *out==7; один root в каждой fixture.
Plain вызывает ту же функцию с тем же контрактом/телом; меняется только proof attribute. Новые три source rustfmt PASS.

## Диагностические goldens и классификация

Все семь новых experiment goldens — `VERIFICATION:-`, require_success=false, diagnostic=`VERIFICATION:-`.
Это явно разрешённая заданием диагностика, а не correctness gate. Pinned validate отвергает false без diagnostic;
нейтральный diagnostic сохраняет штатный runner без изменения tooling и не требует конкретно SUCCESS или FAILURE.
Побайтное требование старых repro сохранено для main.rs; их experiment goldens намеренно нейтральны по п.3 задания.
Исторические U3B goldens и evidence в research и read-only v2 не изменены. Эти goldens не заменяют acceptance U3/PFC.
Unsupported/OOM могут не содержать VERIFICATION:- и дать native ERROR; это не препятствует bounded KT2 excerpt.
Native PASS не означает Kani SUCCESS. После build снять summary/native/native-field excerpt для каждого offset,
явные Failed Checks / Unsupported / Kani-reported OOM / SUCCESS и wall_s. Не выводить OOM из missing output;
missing/timeout/runner errors записывать отдельно. Off-negative SUCCESS только диагностический, без correctness credit.
Если unexpected on-negative SUCCESS — остановить дальнейший dispatch и передать координатору как blocker.

## Бюджет, полномочия, сравнение

Slug kani3300; stage kani3300-u3c; owner k1-merge; kind kani-tests; runner gcb-e2-standard-4.
Work budget5min, selector150s; reserve(5+30)*0.0135=$0.4725; две разные базы максимум $0.945 <= stage cap$0.95.
Стадия: clean Build1 завершён FAILURE/TOOL_ERROR, расход $0.1755, actual reserve0.
Предлагаемый U1 reserve $0.4725; spend+reserve=$0.6480 <=$0.95; это вторая и последняя попытка стадии. Repair не предусмотрен. Main300min + closeout30min из задания, без переноса T0.
Подготовка не регистрирует фазу и не расходует GO. Общий ledger/slots проверять штатно непосредственно перед dispatch.
Root RUN-REQUEST.json теперь побайтно равен reviewed U1 snapshot; patch/request SHA и applied tree прежние.
Clean GO не разрешает U1 dispatch. Новый exact PRE-BUILD review/GO обязателен.
Независимый bounded review обоих пакетов: PASS, Luna HIGH, candidate 0b0a3c33978b72147658422fac3424ce3255ac8f; ../REVIEW-U3C-PACKET.md.
Production U1 ранее рассмотрен в ../../u1/REVIEW-KANI3300-U1R.md; review не даёт coordinator GO.
После каждого GO/build — k1g.sh watch BUILD и конец хода. Raw evidence/локальные cargo/rustc/Kani/CBMC запрещены.
Clean Unsupported + U1 assigns не устанавливает регрессию v2; U1 SUCCESS на том же root против v2 OOM — ухудшение на fixture.
OOM на старых базах — существовавшее ограничение этих repro. Механизм buffer-in-MEM_INIT_STATE пока гипотеза;
следующий опыт выбирать после MU-free контроля, без немедленного второго marker. Итог RESULT <=30 строк после двух результатов.

## Clean result и ограничения сравнения

Clean build `87c1def4-07d7-4233-84ea-5b01eda765a2`: tool build PASS; native6 PASS/1 ERROR.
Positive-on native ERROR за162.497s; report объединяет timeout/kill/build/panic, точный trigger не сохранён в excerpt.
Нельзя выдавать этот результат за timeout или Kani-reported OOM. Negative-on содержит `VERIFICATION:- FAILED` за124.869s;
actual Failed Check UNKNOWN: neutral golden дал native PASS, а pinned KT2 не сохраняет excerpt успешного native-теста.
Targeted native-field output_excerpt возвращает unknown field; raw обход не выполнялся.
On/off MU-free PFC и plain-on дали SUCCESS (1.471/1.069/0.767s), оба MU-off repro SUCCESS (3.237/1.069s).
Все выводы и evidence identities: ../clean/POST-BUILD-OBSERVATIONS.json, ../clean/CLEAN-RESULT.md.
Это не устанавливает существовавший upstream OOM или ухудшение v2; механизм пока открыт.
U1 идёт с теми же neutral goldens/flags/roots для строгой дифференциальности; ограничение сохранения Failed Checks
для native PASS распространяется и на U1. Ни correctness credit, ни конкретный assigns/uninit класс из общего FAILED не выводить.
Изменения относительно reviewed U1 snapshot только activation root request и docs/evidence; нового semantic diff нет.
