# REV2 · валидность на Kani main · handoff

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE` · актуальный control — **FIX1 `3ca0024524`**, tree `697dc737fe`.

## FIX1 после ревью R1

Ревью R1 дало GO_WITH_NITS без блокеров с одним исправлением до запуска. [Ревью](REV2-VALIDITY-MAIN-REVIEW.md)

- **Таймаут шага фазы B.** Шаг может стартовать задолго до своих абсолютных окон: после быстрой фазы A примерно на epoch+10 мин. При этом окна тянулись до 79:30 для list, 119:30 для слотов и 121:30 для аттестации, а шаг обрывался через 75 мин. Теперь `phase_b` ограничивает B setup как `min(b_setup_deadline, старт шага + 30 мин)`, а цепочку слотов — `min(phase_b_deadline, конец setup + 12 × 200 с)`. Финальная аттестация, как и прежде, идёт не дольше 120 с. Фаза A так же ограничена `min(phase_a_deadline, старт + 18 × 65 с)`. Верхняя граница шага B — 30:00 + 40:00 + 2:00 = 72:00, `timeout-minutes` поднят с 75 до 80. Абсолютная граница сохраняется: при самом позднем старте B на 49:30 шаг кончается до 129:30, что меньше job 140 мин.
- **Тест согласованности.** `step_budgets()` даёт бюджет каждого шага от его старта. Тест разбирает таймауты шагов и job из текста workflow без PyYAML. Он требует таймаут не меньше бюджета, с запасом 60 с для A и 300 с для B на checkout, identity с submodules и удаление scratch. План job и поздний старт B также должны укладываться в 140 мин. Прежнее значение 75 мин тест отвергает. Отдельный тест проверяет относительные окна B и сохранение более ранних абсолютных.
- **Классификация `rustup component list`.** `MissingComponents` даёт `LOCAL_COMPONENT_MISSING`, `AttestationTimeout` — `TOOLCHAIN_PROBE_TIMEOUT`, прочий сбой пробы — `TOOLCHAIN_PROBE_FAILED`. Тесты покрывают все три случая и разбор списка компонентов.
- **Без изменений.** CI-REQUEST.json `7ccf98c4…c53474`, bundle `f0ed6816…63cf`, fixture, Std overlay, roster и правила решения. Патч `caaa716bc3..3ca0024524` воспроизвёл tree `697dc737fe` во временном Git index. [Diff FIX1](/root/rev2-validity-main-review/control-fix1-from-r1.patch)
- **Проверки FIX1.** `python3 -B -m unittest discover` дал **102/102**, блок self-test с часами от 60 с — тоже 102/102. На detached review-trigger `59477c9027` прошёл `run.py pins` с внешним tree pin, затем self-test из workflow, 102/102 за 17,0 с. Checkout остался чистым, прежний tree pin `00220e7ead` отклонён. PyYAML разобрал workflow без дублей, семь shell-блоков прошли `bash -n`, `git diff --check` чист.
- **Trigger для запуска.** Review-trigger `59477c9027` содержит `[skip ci]` по правилу локальных коммитов, а такой push не запустит workflow. Координатор пересоздаёт коммит запуска с тем же tree `697dc737fe3bda41f4070ad2d65c123c5c4d615a`, единственным parent `467af9cb8d` и сообщением без `[skip ci]`. После GO variable `CH8_REV2_VALIDITY_MAIN_TRIGGER_TREE` задаётся этим tree.
- ON-positive MATCH по-прежнему не требует `read_binding=OBSERVED`. Утверждение о проверке конкретного чтения опирается на `read_binding`, чувствительность дают четыре отрицательных случая.

Локальный вердикт о совместимости Kani main `8c6dba5935` с неизменённым Std `dab03cf510`: **UNKNOWN**, установить локально нельзя. Сборка Kani, cargo, rustc, Kani и CBMC здесь не запускались, локального rustup-toolchain нет. Совместимость проверяет фаза 0 CI-пакета, фазы A и B стартуют только после её `PASS`. [Задание](REV2-VALIDITY-MAIN-IMPL-TASK.md) · [Уточнение координатора](REV2-VALIDITY-MAIN-COORD-NOTE.md)

## Статическая сверка toolchain

| Сторона | Канал | Компоненты |
| --- | --- | --- |
| Kani main `8c6dba5935` | `nightly-2026-11-23` | `llvm-tools`, `rustc-dev`, `rust-src`, `rustfmt` |
| Std `dab03cf510` | `nightly-2026-11-19` | `llvm-tools-preview`, `rustc-dev`, `rust-src`, `rustfmt` |
| Организаторский пин Std, Kani `9834c96ce9` | `nightly-2026-11-19` | — |

- `kani-driver` запускает `cargo +<RUSTUP_TOOLCHAIN времени сборки>` с `RUSTC=<собранный kani-compiler>`. Std компилируется toolchain Kani `nightly-2026-11-23`, объявление Std на это не влияет. [session.rs](https://github.com/model-checking/kani/blob/8c6dba5935e8b37a905145c57572d1b67489bae2/kani-driver/src/session.rs#L346-L348)
- Между `9834c96ce9` и `8c6dba5935` 14 коммитов. Четыре поднимают nightly 11-19 → 11-23, только первый содержит правки исходников, это предупреждения сборки. Для Std существенны новый `kani_core::kani_valid_value!(core)`, который внедряется в core, `PanicAssertHook` и `-Z inline-mir=no` для локального крейта при stubbing. Поэтому риск фазы 0 — сам core 11-19 под rustc 11-23 и новый код kani_core внутри core.
- Локальные refs upstream verify-rust-std устарели, последний канал `nightly-2026-10-23`. Совместимую с 11-23 базу локально подобрать нельзя.

## Ревизии и файлы для ревью

| Объект | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| Kani main pin | `8c6dba5935e8b37a905145c57572d1b67489bae2` | `3ae54fa78d0e7ab1fbaec728ced37cbd59127834` | `18a8d8031edfe47f3ef3d3aceea8ee40b8843f6d` |
| Std base | `dab03cf510df5c35141cde49f1368b1242f5035e` | `7fd542ad59723ff2beeacb9632fb0568e81b0655` | `1d2706e31f0cd909bd784fa43adf9a1d55be8469` |
| Std overlay 1, корни | `c7993fe252b849c462d770ddba8ac7bc95769f9e` | `88d49939084b62550e1dc3f103b0055fcb16ffcb` | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Std overlay 2, типизированные чтения | `75ab1822ac0cf10d905ecb8975c2bf0eda35c3a2` | `6e6134cd1c9a36750981a61f8fcc763013f532ad` | `c7993fe252b849c462d770ddba8ac7bc95769f9e` |
| Control R1 | `caaa716bc3856d1e6ec460a74cb22fd36e9200d6` | `00220e7ead711ba57bf64f4e07b97d360f047d49` | `0dcc435f7d3f7e73a7ae362445e385e1747cedc9` (control FIX3) |
| **Control FIX1** | `3ca002452456f9fdfe303ad01acd439960833429` | `697dc737fe3bda41f4070ad2d65c123c5c4d615a` | `caaa716bc3856d1e6ec460a74cb22fd36e9200d6` |
| Review-trigger FIX1 | `59477c90275fd5e2db710947a25e4c56cd1d2954` | `697dc737fe3bda41f4070ad2d65c123c5c4d615a` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Review-trigger R1, устарел | `24e1a7715c16c2f02ed8e273f3c0fa7e98df6d7d` | `00220e7ead711ba57bf64f4e07b97d360f047d49` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

- Worktrees: [Kani main](/root/kani-rev2-validity-main-tool-w11) и [Std base](/root/verify-rust-std-rev2-validity-base-w11) — detached на пинах. [Std](/root/verify-rust-std-rev2-validity-main-w11) — ветка `work/rev2-validity-main-std-w11`, [control](/root/kani-rev2-validity-main-control-w11) — ветка `work/rev2-validity-main-control-w11`. Triggers лежат в `local/rev2-validity-main-fix1-trigger-review` и, для R1, в `local/rev2-validity-main-trigger-review`.
- Патчи воспроизвели оба tree во временных Git index. [Std от base](/root/rev2-validity-main-review/std-overlay-from-base.patch) · [Control от FIX3](/root/rev2-validity-main-review/control-from-fix3.patch) · [Модуль корней](/root/verify-rust-std-rev2-validity-main-w11/library/core/src/slice/sort/shared/smallsort/validity_main.rs) · [Fixture](/root/kani-rev2-validity-main-control-w11/ch8-rev2-validity/validity_fixture.rs)

| Файл control | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-validity-main-control-w11/ch8-rev2-validity/CI-REQUEST.json) | `7ccf98c499d2e32e220cd971c73929bbb3152302b71892ab6f06ca4e82c53474` |
| [std-overlay.bundle](/root/kani-rev2-validity-main-control-w11/ch8-rev2-validity/std-overlay.bundle) | `f0ed681607511d1bea506094a371c9b7ac2082674595996e47d27377483a63cf` |
| [validity_fixture.rs](/root/kani-rev2-validity-main-control-w11/ch8-rev2-validity/validity_fixture.rs) | `eb9575b09117594fa57ea5c3dc64752b37f41584c232c25b476dddb6b35a1f16` |
| [ch8-q-pilot.yml](/root/kani-rev2-validity-main-control-w11/.github/workflows/ch8-q-pilot.yml), FIX1 | `7435e7014456b9afdeae2d2d09dccf6fe57789970f6a67a7c7d433f135ade3e9` |

Digest roster в `request.py` — `6a89e1e970d44938bef0bd2864d235d4f69f1e8cd46c1648adf3c7c87862deea`.

## Что принято от прежнего исполнителя

- Std-коммиты `c7993fe252` и `75ab1822ac` приняты без изменений. Fixture, roster с координатами и `native_properties.py` перенесены как есть.
- Черновик control лежал неотслеживаемым каталогом на ветке, стоявшей прямо на Kani main. В push-дереве оказались бы 16 workflow Kani. Не было trigger gate, finish/upload, тестов runner. Discovery имело 600 с на два `kani list`, а один cfg-on list в FIX3 занял 881 с. Ветка переставлена на control FIX3 `0dcc435f7d`, дерево содержит только `ch8-q-pilot.yml` и `ch8-s2.yml`. Исходный черновик сохранён для сравнения. [Черновик](/root/rev2-validity-main-review/draft-control/ch8-rev2-validity)
- В `verdict.py` исправлены два дефекта. Позитивный корень отвергал `UNREACHABLE`-проверки, которые в std неизбежны. Std-контроль требовал ровно одно validity-свойство на весь прогон, хотя внутренние чтения сортировки дают их много. Публикуется до 256 свойств, приоритет у отказов, обязательных covers и validity на координатах чтений. Привязка внутренних чтений учитывает только validity-свойства.
- `request.py` и `run.py` переписаны по схеме FIX3: отдельные шаги, окна receipt, отложенная запись, независимый tree pin. `supervisor.py`, `telemetry.py`, `native_metrics.py` и их тесты совпадают с FIX3 побайтно. Проба `kani-compiler -Vv` и procfs-witness ядра при сбое самой пробы дают `UNKNOWN`. Фатально только установленное расхождение.

## Пакет и gate

Workflow `CH8 SmallSort REV2 validity on Kani main`, одна job `ubuntu-24.04`, `timeout-minutes: 140`. Push gate прежний: `Tiramisu-Cake/kani`, событие `push`, `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt `1`, `contents: read`. После отдельного GO координатор задаёт Actions variable `CH8_REV2_VALIDITY_MAIN_TRIGGER_TREE` полным tree FIX1 `697dc737fe3bda41f4070ad2d65c123c5c4d615a`. `check_trigger` сверяет tree checkout, SHA из `after` payload и sole parent `467af9cb8d`. Пустой, отсутствующий или чужой pin даёт отказ без outputs и `artifact/`. Finalize идёт только при `trigger_admitted=true`, upload — только после успешного finalize. [Workflow](/root/kani-rev2-validity-main-control-w11/.github/workflows/ch8-q-pilot.yml) · [Gate](/root/kani-rev2-validity-main-control-w11/ch8-rev2-validity/request.py)

| Шаг | Что делает | Блокирует |
| --- | --- | --- |
| `pins` | Gate, frozen request, полный self-test на часах от 60 с | всё |
| `sources` | Identity base и tool с submodules, декларации toolchain, `bundle verify`, ровно один `HEAD`, unbundle без refs, цепочка commit/tree/parent, layout guard, сверка всех координат и covers с текстами источников | всё |
| `phase0` | Identity → `rustup component list --installed` для 11-23 → `cargo build-dev --release` → attestation → compile-only preflight неизменённого Std | A и B |
| `phase-a` | 18 слотов fixture | B |
| `phase-b` | Checkout overlay, cfg-on compile-only preflight, один cfg-on `kani list`, 12 слотов, финальная аттестация | — |
| `finish` | `NOT_RUN` для отсутствующих receipts, время записи receipts, `SUMMARY.json`, `index.json`, лимит 96 MiB | — |

- **Фаза 0.** Attestation записывает `rustc -Vv`, `cargo -V`, путь и SHA-256 бинарей, sysroot rustc, `kani-compiler -Vv` против идентичности rustc, CBMC/goto-cc/goto-instrument 6.11.0, Kissat и CaDiCaL внутри CBMC. Preflight — точная команда CAL2 `scripts/kani verify-std -Z unstable-options -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing --no-assert-contracts --no-codegen --only-codegen --quiet --target-dir <scratch> std/library`, окно 300 с. Сохраняются argv, cwd, env, время, результат, Cargo-witness `kani-compiler --crate-name core -Z no-codegen` с полным argv и отсутствием `--cfg=kani_rev2_validity_main`, procfs-witness argv/cwd, sysroot ядра против sysroot пина. Verifier-процессов быть не должно.
- **Классы сбоев.** `failure.class` принимает значения `LOCAL_COMPONENT_MISSING`, `KANI_BUILD`, `TOOL_ATTESTATION`, `UNCHANGED_STD_COMPILE` (rustc вышел с диагностикой), `PREFLIGHT_INFRASTRUCTURE`, `OVERLAY_COMPILE`, `OVERLAY_DISCOVERY`, `SOURCE_IDENTITY`. При сбое записываются первая диагностика с кодом, `file:line:column` из первой строки `-->` и выпуск rustc.
- **Отсутствие регистраций при выключенном cfg** установлено статически. Layout guard восстанавливает base blobs `Cargo.toml` и `smallsort.rs` побайтно снятием двух строк lint-декларации и хвоста `#[cfg(all(kani, kani_rev2_validity_main))] mod validity_main;`. Режимы файлов прежние, вложенных модулей нет. Cfg-on discovery требует ровно шесть `standard-harnesses` из `validity_main.rs` без дублей и лишних имён.

## Точный roster и ожидания

Все слоты: `--exact --jobs=1 --output-format=regular --solver cadical --unwind <N> --verbose --target-dir <slot> --cbmc-args --object-bits 12`. ON отличается от OFF ровно парой `-Z valid-value-checks`, `-Z uninit-checks` не передаётся. A — `scripts/kani -Z unstable-options <fixture>`, unwind 16. B — `scripts/kani verify-std` с теми же восемью `-Z`, что в preflight, `--no-assert-contracts`, `RUSTFLAGS=--cfg=kani_rev2_validity_main`. Штатные safety/overflow/unwind checks не отключаются. CBMC-команда в выводе сверяется с OB12, solver и unwind, явное противоречие даёт `MISMATCH`.

| Фаза A, selector | Операция | OFF | ON |
| --- | --- | --- | --- |
| `copy_valid_read` | `ptr::copy` `['a','b','c']` со сдвигом 1, чтение `[2]` | SUCCESS | SUCCESS, `'b'` |
| `copy_invalid_read` | `ptr::copy` `0xD800` из выровненного `MaybeUninit<u32>`, чтение `char` | SUCCESS | один validity FAILURE, строка 41 |
| `nonoverlap_valid_read` | `copy_nonoverlapping` произвольного `char` | SUCCESS | SUCCESS, равенство |
| `nonoverlap_invalid_read` | Disjoint copy `0xD800`, чтение `char` | SUCCESS | один validity FAILURE, строка 78 |
| `copy_overwritten` | Copy `0xD800`, запись `'R'`, чтение | SUCCESS | SUCCESS, `'R'` |
| `write_bytes_zero` | `count=0`, `0xFF`, прежний `'Z'` | SUCCESS | SUCCESS, `'Z'` |
| `write_bytes_raw_only` | `count=1`, `0xFF` в `MaybeUninit<char>`, чтение только `u8` | SUCCESS | SUCCESS |
| `write_bytes_valid_read` | `count=1`, байт 0, чтение `char` | SUCCESS | SUCCESS, `'\0'` |
| `write_bytes_invalid_read` | `count=1`, `0xFF`, чтение `char` | SUCCESS | один validity FAILURE, строка 166 |

| Фаза B, `slice::sort::shared::smallsort::validity_main::` | Маршрут | Unwind | ON |
| --- | --- | ---: | --- |
| `vv_swap_bool_n02` | Actual `swap_if_less` на `[bool; 2]`, covers swap/no-swap | 64 | SUCCESS |
| `vv_fallback_nonzero_n03` | Actual `small_sort_fallback`, `[NonZeroU8; 3]`, сдвиг и заполнение зазора | 64 | SUCCESS |
| `vv_stable_char_n09` | `<char as StableSmallSortTypeImpl>::small_sort`, scratch 25 × `MaybeUninit<char>`, два `sort4_stable`, вставка, нечётный merge | 96 | SUCCESS |
| `vv_stable_char_n09_corrupt` | Тот же маршрут и проверки, затем запись байтов `0xD800` в `values[0]` через `*mut u8` | 96 | один validity FAILURE, строка 111 |
| `vv_sort8_char_n08` | Actual `sort8_stable`, раздельные input, dst и scratch по 8 × `MaybeUninit<char>` | 96 | SUCCESS |
| `vv_network_nonzero_n19` | Actual `small_sort_network`, `[NonZeroU8; 19]`, половины 9+10, merge и copy-back | 96 | SUCCESS |

- Все корни — plain `#[kani::proof]` без stubs. Компараторы — функции полного порядка без паник, `panic_on_ord_violation` остаётся в реальном теле. Значения из `kani::any()`. Каждый корень проверяет порядок и сохранение числа каждого исходного значения. Наблюдение после переноса — явное чтение через сырой указатель на отдельной строке с маркером `validity-read`. Контроль и позитивный корень разделяют тело и строку чтения 111, проверки до порчи совпадают.
- Контроль проверяет наблюдаемость потребителя после actual маршрута. Внутренние чтения не проверяются отрицательными контролями. По ним публикуются нативные validity-свойства на записанных координатах `smallsort.rs`, без совпадения статус `UNKNOWN`.

## Правила решения

- **ON-negative MATCH.** Терминал `VERIFICATION:- FAILED`, ненулевой код. Ровно один `FAILURE` среди свойств, класс `safety_check`, описание `Undefined Behavior: Invalid value of type ...`. Location совпадает с координатой чтения по полному суффиксу пути, на этой координате ровно одно validity-свойство. Cover raw write выполнен, cover после чтения ON не требуется. Отказ на записи, `ERROR` или второй отказ дают `MISMATCH`. `UNDETERMINED` после отказа допускается и считается.
- **Позитив MATCH.** Терминал `SUCCESSFUL`, код 0. Все не-cover свойства `SUCCESS` или `UNREACHABLE`, все обязательные covers `SATISFIED`. В OFF validity-свойств нет вовсе.
- `unsupported_construct` со статусом, отличным от `UNREACHABLE`, даёт `MISMATCH`. Aggregate `SUCCESS` не считается свидетельством validity check: привязка чтения публикуется отдельно как `read_binding` (`OBSERVED`/`UNKNOWN`). Скрытая усечением привязка даёт `UNKNOWN`.
- Ресурсы оцениваются отдельно в `resource_status` (`WITHIN_LIMITS`, `OVER_LIMIT`, `CENSORED`, `UNKNOWN`) по VT ≤120 с, cold wall ≤45/180 с и group RSS ≤4 GiB. Таймаут или давление памяти дают `INCOMPLETE`. `OVER_LIMIT` при правильном исходе остаётся `MATCH`.
- **Gate B.** B стартует только если фаза 0 `PASS` и все 18 слотов A `MATCH`. Иначе все 12 слотов B получают `NOT_RUN` с причиной `PHASE_0_<stage>`, `PHASE_A_UNEXPECTED` или `B_SETUP_<stage>`. Состоявшиеся наблюдения A публикуются. `REAP_UNVERIFIED` и отказ supervisor останавливают оставшиеся слоты и финальную аттестацию.

## Окна и оценка

| Фаза | Окно | Конец от epoch |
| --- | --- | ---: |
| Checkout, deps, build, attestation, base preflight | 30:00, preflight до 300 с | 30:00 |
| A: 18 × (45 + 10 reap + 5 receipt + 5 запуск) | 19:30 | 49:30 |
| B setup: overlay preflight до 300 с + cfg-on list, также не дольше 30:00 от старта шага | 30:00 | 79:30 |
| B: 12 × (180 + 10 + 5 + 5), также не дольше 40:00 от конца setup | 40:00 | 119:30 |
| Финальная аттестация | 2:00 | 121:30 |
| Finalize + upload | 5:00 + 7:00 | 133:30 |
| Предел job | запас 6:30 | 140:00 |

- Таймауты шагов FIX1: фаза 0 — 30 мин, A — 21 мин при бюджете 19:30, B — 80 мин при бюджете 72:00, finalize — 5 мин, job — 140 мин. Самотест связывает их с бюджетами.
- Оценка задания 110–120 мин уточнена до верхней границы 133,5 мин. Причина — фактические 881 с одного cfg-on list в FIX3 (`45661535099`, setup 1183 с: build 139 с, preflight 26 с, list 881 с при 6,2 GiB) и 5 с запуска на слот. Окна абсолютны от epoch, свободное время ранних фаз переходит к поздним.
- Ожидаемая фактическая длительность при сходящихся корнях — 45–70 мин: до фазы 0 около 2,5 мин, фаза 0 около 3–5 мин, A около 3–6 мин, B setup около 15,5 мин, B 12–39 мин. Номинал группы для setup — 10 GiB, для слотов 4 GiB, резерв ОС 2 GiB. Ресурсный результат Ubuntu не закрывает критерий macOS.

## Локальные проверки

- `rustfmt --check` назначенным `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt` с `use_small_heuristics=Max`: `validity_main.rs` и `smallsort.rs` с `--edition 2024 --config skip_children=true,reorder_modules=false`, fixture с `--edition 2021`. `git diff --check` прошёл для Std и control.
- **Видимость и пути новых имён Rust** сверены по исходникам без компиляции. `swap_if_less`, `small_sort_fallback`, `small_sort_network` и `sort8_stable` — приватные элементы `smallsort`, видимые дочернему `validity_main`. `StableSmallSortTypeImpl` имеет `pub(crate)`. Специализация `T: FreezeMarker` выбирается для `char`, ограничение `FreezeMarker` выполнено для `char` и `NonZeroU8`. `crate::kani` существует при `cfg(kani)`, модуль требует `all(kani, kani_rev2_validity_main)`. `kani::cover(bool, &str)` и `Arbitrary` для `bool`, `char`, `NonZeroU8` и массивов есть в `kani_core` пина. `crate::hint::black_box`, `crate::num::NonZeroU8`, `crate::mem::{MaybeUninit, size_of}` и `char::MIN` есть в core base. Приватный `#[cfg(kani)] mod verify` без `#[unstable]` уже есть в `array/ascii.rs:51`. Сигнатура `sort8_stable(v_base, dst, scratch_base, is_less)` совпадает с вызовом. Длины 9 и 19 проходят ветки sort4 и sort9 + вставка.
- Bundle на shallow-импорте base: `git bundle verify`, один prereq `dab03cf510`, один `HEAD` `75ab1822ac`, unbundle без refs, layout guard, сверка всех координат и covers, чистый checkout.
- Python 3.12.3, `python3 -B -m unittest discover -q` — **99/99**. На detached trigger `24e1a7715c` выполнен `run.py pins` с синтетическим push и внешним tree pin, затем блок self-test из workflow с часами от 60 с — **99/99** за 13,6 с. Checkout остался чистым, чужой pin отклонён. PyYAML разобрал workflow без дублей ключей, семь shell-блоков прошли `bash -n`. На том же trigger без фазы 0 `phase-a` и `finish` выдали 30 receipts `NOT_RUN` и `index.json`.
- Синтетические тесты покрывают: мутации frozen request, digest fixture, устаревшие координаты, повтор cover; argv ON/OFF; gate по tree, payload, ref, attempt и sole parent; точное discovery; часы и latest start; gate 0 → A → B; отказ на записи; `unsupported_construct`; validity в OFF; CBMC с OB11 или `--no-pointer-check`; `TIMEOUT` → `INCOMPLETE`; VT 150 с → `OVER_LIMIT`; остановку после `REAP_UNVERIFIED`; дедлайн проекции; отложенную запись receipt; cfg/sysroot/witness preflight; первую диагностику с `file:line`; классы сбоев фазы 0.

Cargo, rustc, сборка Kani, Kani, CBMC и Miri локально не запускались. Push, CI, gh-запусков и публикаций не было. Коммиты с `[skip ci]`, автор и коммиттер `Tiramisu-Cake <igkharin@gmail.com>`.

## Ограничения и UNKNOWN

- Совместимость, фактические версии, sysroot, argv ядра, discovery, свойства и ресурсы — `UNKNOWN` до фазы 0 и последующих фаз. Формат нативного вывода и класс validity-свойств взяты из исходников пина и его ожидаемых тестов `copies.expected` и `write_bytes.expected`.
- Модель Kani 5205 отслеживает одно недетерминированно выбранное значение байта на harness. Ограничения по layout, проекциям элементов среза и дискриминантам агрегатных enum остаются. Совместный ON uninit/validity, Check/Replace с havoc, паника компаратора, полные матрицы длин и допуск pr752 вне этой диагностики.

## Минимальный следующий пакет при блокере

- **`UNCHANGED_STD_COMPILE`.** Передать первую диагностику с `file:line` и выпуском rustc. Отдельным решением выбрать одно из двух. Первое — синхронизировать Std с upstream verify-rust-std на toolchain `nightly-2026-11-23` и минимальной дельтой library и `rust-toolchain.toml`, затем повторить фазу 0. Второе — пакет только A, где фаза 0 сокращена до сборки и attestation. Это решение координатора, потому что оно меняет правило «A после полной фазы 0».
- **`KANI_BUILD`, `TOOL_ATTESTATION` или `LOCAL_COMPONENT_MISSING`.** Исправить обвязку и повторить без изменений Std.
- **`PHASE_A_UNEXPECTED`.** Разобрать наблюдения A. Отказ на записи, недостижимое или ненайденное чтение передать reproducer сопровождающему 5205 до любой Std-фазы.
