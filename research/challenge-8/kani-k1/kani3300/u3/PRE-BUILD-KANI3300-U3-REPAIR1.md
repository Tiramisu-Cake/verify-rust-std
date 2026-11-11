# KANI3300 U3 — PRE-BUILD repair 1

Статус PREPARED, repair native NOT_RUN. Dispatch только после exact-packet GO координатора.
Решение координатора: плоский ghost-state вместо enum; SKIPPED_ITEMS не менять, отдельный static/второй marker не вводить.
Это единственный repair, разрешённый условно бюджетом; новый Build ещё не отправлен и reserve не создан.

## Exact identities и KT2

- Research branch experiment/kani-k1-kani3300u3-20261111; Kani fix/kani-3300-v2 candidate `81dd85bfce67226e283fdd9a156932e32ece080b`.
- Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; failed v2 baseline `3fd6f408e1d565ba65aaeb86c0c4ad0bbc57ab52`.
- Patch `kani3300/u3/kani-uninit-v2.patch`, SHA256 `f3f8a82c2c22798361bf51bf6186aa60cadb1de68d0aa15b15ad62d601138c1c`.
- Request `kani3300-u3-repair1-20261111-03`, SHA256 `2def1eb2642fe4f707dd659208c0af7ff55b2a3feba5f3ed7cc9fb99b7dcca7e`; root RUN-REQUEST и repair1 snapshot побайтно равны.
- Fresh applied tree `c5b24f0b0da999d1deb9758215790382fe5e3be4` совпал с деревом Kani candidate.
- **Tooling base `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`** — принят координатором из origin/experiment/kani-k1-kt2-20261111.
  Перенесён без изменений cherry-pick `d483dc371967cc5be6b0166eb506c2f4cb0179aa`; receipt635368edbe перенесён как87a11b0a9f.
  Diff всех lane/tooling/pin/toolchain файлов относительно этого base пустой. Проверка будущей сборки:
  `bash research/challenge-8/kani-k1/tools/k1g.sh check-tooling BUILD 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
- Предыдущая сборка14dd0792-1c06-47be-b931-94f6096a664a на2021b7cf35: Kani build PASS,20 native ERROR, расход$0.108.
  Исторические evidence/идентичности сохранены; [repair1/PRIOR-BUILD-OBSERVATIONS.md](repair1/PRIOR-BUILD-OBSERVATIONS.md) описывает новые bounded KT2 reads.

## Почему layout state поддержан

В library/kani_core/src/mem_init.rs:34 MemoryInitializationState — один struct: шесть usize и два bool.
В нём нет Option/enum/union, отдельного ArgumentBuffer или сохранённого raw pointer. Raw pointer на весь static теперь
имеет тот же поддержанный класс layout, независимо от того, откуда instrumentation запросит mask.
`check_uninit/ty_layout.rs:355–367` обходит AdtKind::Struct по fields_by_offset_order(), берёт реальные offsets из rustc layout
и рекурсивно добавляет data chunks по offset+current_offset. Для каждого usize/bool срабатывает FieldsShape::Primitive,
ValueRepr::Scalar(Initialized) (:219–228), размер берётся из MachineInfo; ветки enum (:258–351) и union не достигаются.
`generate_byte_mask` (:38–48) создаёт false-маску полной size_in_bytes и ставит true только в этих data chunks.
Поэтому внутренние и хвостовые padding bytes остаются false. Порядок полей/offsets/размер Self не захардкожены и не
объявляются проверенными запуском rustc. Это обоснование по исходнику алгоритма layout, не native-result/proof credit.

## Buffer protocol и сохранённые гарантии

Init reset — active=false; все metadata const-инициализированы нулями. Неактивные metadata не читаются.
Store при return0 обязателен, для аргументов прежний nondet выбор; номер, live source objectID/offset и extent
записываются до active=true. Load short-circuit active&&selected, проверяет extent и снимает numeric snapshots до transfer,
затем copy_by_id и active=false. Unmatched Load сохраняет выбранный аргумент для следующего индекса и прежний bless.
Copy/Move byte witnesses и numeric return-lifetime обоснование остаются прежними; transfer не использует мёртвый pointer.
Marked MEM_INIT_STATE и его существующий DFCC assigns target прежние; пользовательские modifies targets/флаги/checks не менялись.
Compiler/check_uninit и SKIPPED_ITEMS побайтно равны failed v2: setup НЕ получил нового trusted исключения.

## Controls и проверка

20 прежних selectors, job10min/selector150s; все пять U1T negatives требуют Failed Checks и прежние T.
Empty_harness добавлен в wrap-u3-positive (теперь7 SUCCESS); его тело пустое, compiler всё равно вставляет setup.
Сохранены review-positive7, plain/PFC/clause pairs, nested/two args/return0/stale, no-MIR и outside-modifies FAILURE.
Положительные selectors require_success=true; golden count wrap изменён6→7 только из-за нового harness.
Типизированные scalar/array conversion, padding/source-read negative, MU→T и partial-copy/reset controls сохранены.
Полный IntoIter по-прежнему expected Unsupported из-за compound MU storage; select_unpredictable не менялся.

[repair1/STATIC-CHECKS.json](repair1/STATIC-CHECKS.json): PASS validate20, fresh apply --check --index/tree identity,
rustfmt36 .rs, diff-check, allowlist, unchanged U1T sources/goldens, compiler/SKIPPED/DFCC equality, tooling equality.
Preflight diffstat4001bytes≤4096. Repair vs failed v2: production1 file+37/−36, tests2 files+5/−1.
v2 repair−U1: production2 files+129/−30, tests с U1T36 files+635/−0. Полный patch: production7 files+675/−178,
tests58 files+963/−0. Local cargo/rustc/Kani/CBMC не запускались.
KT2 unit/service suite PASS117tests (74.662s); [repair1/REVIEW-FLAT-BUFFER.md](repair1/REVIEW-FLAT-BUFFER.md): Luna HIGH no static blocker.

## Evidence после будущей сборки и бюджет

После terminal: summary → check-tooling против `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` → native/native-field.
KT2 теперь приоритизирует actual Failed Checks и regular FAILURE blocks, сохраняет diagnostic_only и все bounds.
Для overwrite offset16 и обеих overlap offset17 выписать actual Failed Checks с source/harness context; отдельно указать
unreachable/foreign failures. При omitted/clipped lines или неполной привязке отразить limitation, не выводить absence/SUCCESS.
Старый excerpt нельзя регенерировать из raw output; его неизвестные свойства repair пока не закрывает.
Расход U3$0.108, proposed reserve(10+30)×$0.0135=$0.540, total$0.648≤cap$0.90; проектный cap$6.40 сохраняется.
Нового GO на этот exact repair packet ещё нет. После native PASS — отдельное review/replay по исходному TASK.
