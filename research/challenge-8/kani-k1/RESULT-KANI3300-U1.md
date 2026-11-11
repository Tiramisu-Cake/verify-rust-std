# RESULT-KANI3300-U1

PASS — build `d5d15c41-1c07-4f9f-a6ff-16c25fae00e1`, COMPLETE, gate true, все 20 native selectors PASS.
Head `7c0d8e84134d2e0c28031285aded2292cb2a4678`; Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`.
Request `kani3300-u1-repair1-20261111-03`, SHA-256 `69d892414672163b0d4969c13292c0141d9b5e97ada72dd7d0221c10199062cc`.
Patch SHA-256 `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`; applied tree `b9c36ac5ed550e39d26e1d1d77000052e62a9bb4` совпал с preflight.
check-tooling PASS против `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`; Kani 0.68.0, CBMC 6.11.0, nightly-2026-10-23.

Shadow хранит один недетерминированно выбранный байт по object ID и offset.
By-value transmute проверяет shadow источника по data-byte mask T перед формированием T, включая путь через `ManuallyDrop<T>`.
Raw-адрес сохраняет shadow; запись поля обновляет его маску по адресу; пустой aggregate очищает весь слот.
Целые слоты переносят shadow через assign/copy и обычные MIR-вызовы; копирование исключает старое состояние перезаписанного назначения.
Flat arrays, static repeat константы или отдельного локального слота и срезы используют размер/шаг элемента.
Маска T сохраняет data/padding; validity pass сохранён. Fixtures включают `-Z uninit-checks`.
Production 7 файлов, +548/−150; tests/golden 22 новых файла, +328. Apply-check, rustfmt и diff-check PASS; существующие golden сохранены.

Все пути таблицы относительно `tests/expected/uninit/`; результаты установлены через bounded summary/native.

| Фикстура | Native | Подтверждённый результат |
|---|---|---|
| `maybe-uninit-initialized/main.rs` | PASS | 8 SUCCESS, Kani exit 0 |
| `maybe-uninit-assume-init/main.rs` | PASS | FAILED, uninit u8 |
| `maybe-uninit-raw-read/main.rs` | PASS | FAILED, uninit *const u8 |
| `maybe-uninit-raw-address/main.rs` | PASS | FAILED, uninit *const u8 |
| `maybe-uninit-partial-write/main.rs` | PASS | FAILED, uninit (u8, u8) |
| `maybe-uninit-partial-copy/main.rs` | PASS | FAILED, uninit [u8; 4] |
| `maybe-uninit-slice-offset/main.rs` | PASS | FAILED, uninit u64 |
| `maybe-uninit-reset-alias/main.rs` | PASS | FAILED, uninit u8 |
| `maybe-uninit-scratch-array/main.rs` | PASS | 1 SUCCESS, Kani exit 0 |
| `maybe-uninit-scratch-array-unwritten/main.rs` | PASS | FAILED, uninit u8 |
| `maybe-uninit-volatile-read/main.rs` | PASS | FAILED, uninit *const u8 |
| `unions.rs` | PASS | штатный golden, uninit u32/u16/u128 |
| `uninhabited-union-field/uninhabited-union-field.rs` | PASS | штатный golden, uninit u64 |
| `copy/copy_without_padding.rs` | PASS | Kani exit 0 |
| `copy/read_after_copy.rs` | PASS | штатный golden, uninit *const u64 |
| `copy/expose_padding_via_non_byte_copy.rs` | PASS | штатный golden, uninit *const u64 |
| `transmute-padding/transmute_padding.rs` | PASS | штатный golden, incompatible layouts |
| `delayed-ub/delayed-ub.rs` | PASS | штатный golden, uninit u128/u64 |
| `access-padding-uninit/access-padding-uninit.rs` | PASS | штатный golden, uninit *const u8 |
| `multiple-instrumentations.rs` | PASS | штатный golden, uninit u128/u64 |

Все девять новых negative дали uninit-диагностику из собственного вывода и совпали с golden; unexpected SUCCESS, TIMEOUT и ignored отсутствуют. fixme union/slice NOT_RUN.
Произвольные/вложенные union, перекрывающиеся repeat/array aggregate, typed_swap и fn-pointer calls остаются unsupported. Прямой select_unpredictable непроверен; U7 fixture проверяет pointer-valued слот.
Расход $0.1755 из $0.90, резерв снят — первая попытка $0.0675, repair $0.1080. Первую E0599 исправил импорт CrateDef; успешная сборка Kani заняла 244 с, compiletest 17 с.
Черновик upstream PR находится в `kani3300/u1/UPSTREAM-PR-DRAFT.md`. Стадия завершена, пакет готов к review.
