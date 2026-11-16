# S1-03 intake — run 43784240498

На g0 `f7cfdcb4e7`, стадия подготовки, без dispatch. **21 exported root: 11 SUCCESS, 6 ожидаемых assert FAILURE, 4 TIMEOUT; 2 proof NOT_RUN. Qualified acceptance PENDING, proof credit NONE.** Все 23 строки сохранены; исторические receipts/classifier/ledger не изменены.

Artifact `14191164313`, SHA256 `1e1af37a587e1376a255ee220c6cb59d235ba82905ebce7d39c3df48ac7a0e69` совпадает с GitHub metadata. Sibling `8233b98c15040c7077283a1e873d0db8b2302f93`; control `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`; S′ `f22f84f316ad8ef6f3fccce86424bad927b09f78`; tool stock `0aac16ef62da9e9d5645782d458593e5d78143ba`. В scratch сохранён разрешённый task artifact, читались structured exports/receipts; log members не открывались. Копии receipts в пакете исключают stdout/stderr. Identity/hash details: `PROVENANCE.json`.

Расхождение с предварительной сводкой: terminal receipt сообщает `source_drift: source_identity_drift`, phase_elapsed **3247.012 < 4500 s**, а не исчерпание фазы. `activation-default` имеет setup UNKNOWN и no export; `activation-override` явно NOT_RUN вследствие предыдущего fatal. Обе proof-строки не выполнялись. Причина подтверждена статическим кодом и isolated git reproduction: `.strip()` у porcelain stdout удаляет первый пробел status; `[3:]` повреждает первый путь; `_run_variant` откатывает overlay и бросает исключение до записи `source_before`; finally маскирует его сравнением с отсутствующим snapshot. Production groups имеют совпавшие before/after source hashes; это не свидетельство production source drift.

| Row | Export | VT s | Covers SAT/total | U / unsupported | Классификация |
|---|---|---:|---|---|---|
| stable_default_cell | SUCCESS | 326.754 | 11/11 | 4 / 3 | SUCCESS_OBSERVATION |
| stable_freeze_u8 | TIMEOUT | 600.018 | UNAVAILABLE | 0 / 0 | TIMEOUT_NO_PROOF |
| unstable_default_cell | SUCCESS | 326.592 | 11/11 | 4 / 3 | SUCCESS_OBSERVATION |
| unstable_freeze_u8 | TIMEOUT | 600.014 | UNAVAILABLE | 0 / 0 | TIMEOUT_NO_PROOF |
| freeze_default_noncopy | TIMEOUT | 600.017 | UNAVAILABLE | 0 / 0 | TIMEOUT_NO_PROOF |
| freeze_copy_u8 | TIMEOUT | 600.014 | UNAVAILABLE | 0 / 0 | TIMEOUT_NO_PROOF |
| model_u8_n0_3 | SUCCESS | 1.841 | 6/6 | 4 / 3 | SUCCESS_OBSERVATION |
| model_cell_n0_3 | SUCCESS | 1.939 | 6/6 | 4 / 3 | SUCCESS_OBSERVATION |
| model_noncopy_n0_3 | SUCCESS | 1.874 | 6/6 | 4 / 3 | SUCCESS_OBSERVATION |
| inactive_pairs_read_free | SUCCESS | 0.067 | 1/1 | 12 / 0 | SUCCESS_OBSERVATION |
| activation_descending_rejected | FAILURE | 0.016 | 0/0 | 0 / 0 | EXPECTED_ASSERT_DETECTED |
| activation_effectful_rejected | FAILURE | 0.015 | 0/0 | 0 / 0 | EXPECTED_ASSERT_DETECTED |
| activation_unsupported_type_rejected | FAILURE | 0.017 | 0/0 | 0 / 0 | EXPECTED_ASSERT_DETECTED |
| corruption_companion | SUCCESS | 0.163 | 1/1 | 1 / 0 | SUCCESS_OBSERVATION |
| order_corruption_rejected | FAILURE | 0.062 | 0/0 | 8 / 0 | EXPECTED_ASSERT_DETECTED |
| count_corruption_rejected | FAILURE | 0.086 | 0/0 | 1 / 0 | EXPECTED_ASSERT_DETECTED |
| snapshot_guards_companion | SUCCESS | 5.415 | 1/1 | 2 / 1 | SUCCESS_OBSERVATION |
| invalid_snapshot_rejected | FAILURE | 0.027 | 0/0 | 11 / 0 | EXPECTED_ASSERT_DETECTED |
| stable_default_activation-legal | SUCCESS | 6.374 | 1/1 | 4 / 3 | SUCCESS_OBSERVATION |
| stable_freeze_activation-legal | SUCCESS | 35.368 | 1/1 | 8 / 3 | SUCCESS_OBSERVATION |
| activation-default | NO_EXPORT | — | — | — | NOT_RUN_PROOF (setup detail в ROWS.json) |
| activation-override | NO_EXPORT | — | — | — | NOT_RUN_PROOF (setup detail в ROWS.json) |
| ordinary-bridge | SUCCESS | 0.050 | 12/12 | 0 / 0 | SUCCESS_OBSERVATION |

Inventory/identity: все 3 exports COMPLETE, exact selection sets 15/3/3, без unmatched/duplicate roots; tool commit/dirty, source file SHA, mode, target token spelling, enabled checks и unwind сверены. `n_properties=checks.total+covers.total`; полный status partition согласован: 1843 checks = 1770 SUCCESS + 6 FAILURE + 67 UNREACHABLE; 57 covers SATISFIED. Четыре TIMEOUT имеют отсутствующий check/cover inventory: это не нулевые checks и не PASS. Stock `schema_utils.rs:744-775` строит buckets и unsupported из одного property vector; summary `failed=6` не включает четыре TIMEOUT и не заменяет строки.

Binding: `evidence/contract-symbols.json` содержит full Rust demangle всех восьми PFC symbols: exact type/trait/method/KeyLess и contract closures соответствуют source targets. Это подтверждает identity symbol, но не закрывает attachment: false-ensures variants не запущены. Export не содержит ID/location успешных required assertions или сообщений covers. Поэтому именованные success checks и независимая корреляция cover-message→ID остаются PENDING; число SAT и source macro не подменяют этот gate. `COVER-MAP.json` хранит все 101 cover obligations (включая12 count-only ordinary-bridge) с candidate ID по source order: 57 SAT, 44 unavailable у timeout roots; activation negatives требуют 0. В smoke covers стоят после actual target и caller post/canaries, включая N0..3, reverse/duplicates/ascending. Model controls не доказывают actual target.

Exceptions: `EXCEPTIONS.json` перечисляет 67 unreachable и 22 successful unsupported с exact ID по строкам. Inactive/invalid-token отсекают active_post до тела по guard; order-corruption выходит на проверке порядка до count-loop: это ожидаемые исключённые участки, не утраченные требуемые sorting assertions. N=2 legal Freeze companion исключает len>=8 sort4 branch. Индексы active_post у count/snapshot, general helper assertion4, is_valid_allocation_size, fmt и abs_diff без location/description оставлены UNKNOWN_PROPERTY_ROLE; helper exemption не применяется. Даже для разрешённых ролей полное принятие требует оставшихся binding gates. Unsupported имеют exact ID/class=unsupported_construct/status=SUCCESS: stock `codegen_unimplemented_stmt` (`codegen/assert.rs:278-297`) генерирует assert(false) перед assume(false), а schema экспортирует тот же property; это недостижимость construct в данном harness, а не поддержка reachable поведения. Непустые списки сами по себе не veto.

Negatives: `S1-04/negative-oracles.json` заранее переустанавливает oracle на **ту же исходную assert-точку**, определённую старым manifest message; ID не выбирался по случайному FAILURE. Проверены source SHA/строка/контекст, exact class/status/file/ID и единственный failure. Три activation-pair checks — require_active:95; invalid snapshot — 181; order — 141; count — 152. Все шесть EXPECTED_ASSERT_DETECTED; у order/count/invalid старый classifier не доходил до oracle из-за unreachable veto. Посторонних failures нет. Helper-role qualification сохраняется отдельно. Два actual false-ensures activation oracle НЕ привязываются задним числом: UNBOUND до pre-binding wrapper property.

`validate.py`: offline PASS; exact six oracle checks + 156 отрицательных мутаций, включая посторонний failure, неправильные ID/location/class/status, null/missing/wrong type, TIMEOUT и неправильный verdict. Это проверка пакета и детектора, не новый proof. R8 пока UNKNOWN: четыре roots превысили bar600, full root wall/RSS не сообщены; scope только bounded N0..3 fixtures и model guards до CAP32.

На scratch copy runner-fix.patch прошёл27 synthetic tests (24 baseline+3 focused regressions), включая реальный временный git porcelain/restore и сохранение первичного exception. Это не интеграция нового classifier/group plan и не запуск Kani.
