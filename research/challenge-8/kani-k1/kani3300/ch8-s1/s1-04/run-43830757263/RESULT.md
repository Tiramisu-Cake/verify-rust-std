# S1-04 intake — run 43830757263

**Все 35 выбранных harness выполнены: 27 Kani SUCCESS, 8 assertion FAILURE, 0 TIMEOUT/NOT_RUN.**
По неизменённому oracle пакета: **6 EXPECTED, 29 UNKNOWN; qualified acceptance PENDING, proof credit NONE**.
Все 14 jobs красные из-за `selected_unknown` в `runner.py:1139-1141`, а не ошибки компиляции или обрыва proof.
10 grouped Kani invocations вернули0, четыре с негативными controls —1; runner вернул1 во всех14 группах.
Все group receipts COMPLETE, stop_reason=null, snapshots before/after совпали; старый source_identity_drift не повторился.

[Run](https://github.com/Tiramisu-Cake/kani/actions/runs/43830757263), attempt1, control
`205b0e98c771a7e6c6b8ec28414494868bcca4e0`, std
`5be85699b8826e3286c0bf89efb9affefac0acb5`, stock tool
`0aac16ef62da9e9d5645782d458593e5d78143ba`.
Request SHA256 `fce0e446f1506d0aebf4afc9929075843beed69c01a626391f119e18125850b7`.
14/14 artifacts скачаны через `gh run download` в
`/root/ch8-s1-04-intake-w13/run-43830757263/artifacts/`.
Оригинальный collect.py запущен с14 terminal roots: COLLECTED_OBSERVATIONS_PENDING_REVIEW, missing_groups=[].
Внутренние per-row/setup receipts не являются самостоятельными matrix roots.

## Группы

Во всех14 compile receipts: COMPLETE / STOCK_INITIAL_EXPORT_OBSERVED.
Отдельного compiler exit code в batch нет: он **UNKNOWN**, не подставляется из driver exit.
Compile s — верхняя граница до stock initial export; driver s включает compile, instrumentation и verification.
Bounded stderr tails содержат Finished dev profile; stdout tails — результаты verification.
Таблица показывает исходный exit grouped Kani, а не exit runner.

| Группа | Compile ≤s | Driver exit | Driver s | Group RSS peak KiB |
|---|---:|---:|---:|---:|
| activation-default-u34 | 41.453 | 1 | 44.061 | 1925480 |
| activation-override-u34 | 31.509 | 1 | 47.022 | 1950596 |
| cell-u34 | 32.484 | 0 | 749.754 | 8148864 |
| freeze_copy_u8-n01-u34 | 33.491 | 0 | 57.298 | 2636312 |
| freeze_copy_u8-n23-u34 | 31.387 | 0 | 102.171 | 2652428 |
| freeze_default_noncopy-n01-u34 | 32.277 | 0 | 53.967 | 2638524 |
| freeze_default_noncopy-n23-u34 | 41.404 | 0 | 323.599 | 2649980 |
| light-controls-u34 | 30.871 | 1 | 83.369 | 2350968 |
| light-corruption-u4 | 29.889 | 1 | 30.481 | 1945796 |
| light-model-u5 | 31.841 | 0 | 41.783 | 2636348 |
| stable_freeze_u8-n01-u34 | 31.576 | 0 | 51.577 | 2664424 |
| stable_freeze_u8-n23-u34 | 44.329 | 0 | 326.347 | 2586764 |
| unstable_freeze_u8-n01-u34 | 42.417 | 0 | 64.511 | 2650904 |
| unstable_freeze_u8-n23-u34 | 32.129 | 0 | 106.441 | 2691312 |

Compile границы29.889–44.329s; сумма driver wall2082.381s, сумма verification times1409.874s.
Job wall418–1178s включает setup/build tool. Поэтому короткая длительность heavy jobs не означает NOT_RUN:
все16 exact-N cases завершились SUCCESS; N0/1 verification0.985–1.406s, N2/3 13.641–168.996s.
Cell roots356.130/349.344s. Сравнение с symbolic S1-03 >600s относится к изменённому разбиению;
не устанавливает ускорение исходного symbolic harness или общий theorem.

## Строки

E=VALIDATED_OBSERVATION/EXPECTED; I=INCOMPLETE_CHECK_INVENTORY/UNKNOWN;
S=WRONG_SOURCE_BINDING/UNKNOWN; A=NEGATIVE_ORACLE_UNBOUND/UNKNOWN;
C=COVERAGE_INCOMPLETE/UNKNOWN. VT — stock resources.verification_time_s.
F1–F8 — exact failed property IDs ниже; «—» означает checks.failure=[], не отсутствующий export.
Во всех35 timeout=false, limit600s — stock CBMC timeout, не полный root wall.
**Per-row RSS UNKNOWN**: stock export не даёт attribution; group RSS в таблице выше.
Cell group sampled peak7.771GiB при group cap12GiB не доказывает соблюдение per-root cap6GiB.

| Row | Kani verdict | VT s | Failed ID | Covers SAT/total | Oracle |
|---|---|---:|---|---:|---|
| stable_default_cell | SUCCESS | 356.130 | — | 11/11 | I |
| unstable_default_cell | SUCCESS | 349.344 | — | 11/11 | I |
| model_u8_n0_3 | SUCCESS | 1.942 | — | 6/6 | S |
| model_cell_n0_3 | SUCCESS | 2.115 | — | 6/6 | S |
| model_noncopy_n0_3 | SUCCESS | 2.015 | — | 6/6 | S |
| inactive_pairs_read_free | SUCCESS | 0.069 | — | 1/1 | I |
| activation_descending_rejected | FAILURE | 0.016 | F1 | 0/0 | E |
| activation_effectful_rejected | FAILURE | 0.015 | F2 | 0/0 | E |
| activation_unsupported_type_rejected | FAILURE | 0.017 | F3 | 0/0 | E |
| corruption_companion | SUCCESS | 0.168 | — | 1/1 | I |
| order_corruption_rejected | FAILURE | 0.066 | F4 | 0/0 | E |
| count_corruption_rejected | FAILURE | 0.103 | F5 | 0/0 | E |
| snapshot_guards_companion | SUCCESS | 5.856 | — | 1/1 | I |
| invalid_snapshot_rejected | FAILURE | 0.028 | F6 | 0/0 | E |
| stable_default_activation-legal | SUCCESS | 6.514 | — | 1/1 | I |
| stable_freeze_activation-legal | SUCCESS | 36.052 | — | 1/1 | I |
| activation-default | FAILURE | 1.792 | F7 | 0/1 | A |
| activation-override | FAILURE | 13.693 | F8 | 0/1 | A |
| ordinary-bridge | SUCCESS | 0.050 | — | 12/12 | C |
| freeze_copy_u8_n0 | SUCCESS | 1.019 | — | 2/2 | I |
| freeze_copy_u8_n1 | SUCCESS | 1.126 | — | 2/2 | I |
| freeze_copy_u8_n2 | SUCCESS | 13.641 | — | 5/5 | I |
| freeze_copy_u8_n3 | SUCCESS | 37.147 | — | 5/5 | I |
| freeze_default_noncopy_n0 | SUCCESS | 1.076 | — | 2/2 | I |
| freeze_default_noncopy_n1 | SUCCESS | 1.165 | — | 2/2 | I |
| freeze_default_noncopy_n2 | SUCCESS | 92.202 | — | 5/5 | I |
| freeze_default_noncopy_n3 | SUCCESS | 167.057 | — | 5/5 | I |
| stable_freeze_u8_n0 | SUCCESS | 0.985 | — | 2/2 | I |
| stable_freeze_u8_n1 | SUCCESS | 1.149 | — | 2/2 | I |
| stable_freeze_u8_n2 | SUCCESS | 93.608 | — | 5/5 | I |
| stable_freeze_u8_n3 | SUCCESS | 168.996 | — | 5/5 | I |
| unstable_freeze_u8_n0 | SUCCESS | 1.191 | — | 2/2 | I |
| unstable_freeze_u8_n1 | SUCCESS | 1.406 | — | 2/2 | I |
| unstable_freeze_u8_n2 | SUCCESS | 14.395 | — | 5/5 | I |
| unstable_freeze_u8_n3 | SUCCESS | 37.727 | — | 5/5 | I |

Exact failed property IDs (file/line/class/status и descriptions сохранены в ROWS.json):

- F1, activation_descending_rejected: `slice::sort::shared::smallsort::verify::sorting_model_controls::require_active::<u8, {closure@/home/runner/work/kani/kani/export/library/core/src/slice/sort/shared/smallsort/verify/sorting_model_controls.rs:100:32: 100:48}>.assertion.1`.
- F2, activation_effectful_rejected: `slice::sort::shared::smallsort::verify::sorting_model_controls::require_active::<u8, {closure@/home/runner/work/kani/kani/export/library/core/src/slice/sort/shared/smallsort/verify/sorting_model_controls.rs:106:21: 106:37}>.assertion.1`.
- F3, activation_unsupported_type_rejected: `slice::sort::shared::smallsort::verify::sorting_model_controls::require_active::<mem::maybe_uninit::MaybeUninit<u8>, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<mem::maybe_uninit::MaybeUninit<u8>>>.assertion.1`.
- F4, order_corruption_rejected: `slice::sort::shared::smallsort::verify::sorting_model_controls::order_corruption_rejected.assertion.3`.
- F5, count_corruption_rejected: `slice::sort::shared::smallsort::verify::sorting_model_controls::count_corruption_rejected.assertion.5`.
- F6, invalid_snapshot_rejected: `slice::sort::shared::smallsort::verify::sorting_model_controls::invalid_snapshot_rejected.assertion.1`.
- F7, activation-default: `<cell::Cell<u8> as slice::sort::shared::smallsort::StableSmallSortTypeImpl>::small_sort::<slice::sort::shared::smallsort::verify::sorting_model::KeyLess<cell::Cell<u8>>>::{closure#2}.assertion.1`.
- F8, activation-override: `<u8 as slice::sort::shared::smallsort::StableSmallSortTypeImpl>::small_sort::<slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>::{closure#2}.assertion.2`.

## Причины UNKNOWN и исправление

- **23 I**: blanket gate `runner.py:810-822` отвергает любой unreachable или непустой unsupported list.
  Это не proof FAILURE: у всех23 verdict SUCCESS. Для всего запуска9871 checks =9450 SUCCESS+8 FAILURE+413 UNREACHABLE;
  115 covers =113 SATISFIED+2 UNREACHABLE; 76 unsupported entries имеют status SUCCESS.
  Точные buckets/IDs сохранены. В этой стадии роли413 unreachable и76 unsupported отдельно не квалифицировались;
  нельзя убрать veto и объявить acceptance. Требуется проверка конкретных required checks и ролей exceptions.
- **3 S**: модельные функции созданы macro `positive!`: export line29 (`fn $name() {`), а manifest
  разрешает лишь строки вызовов66/67/68. Selector/crate/file/mode совпадают; source SHA
  `90105d9a3ead4ee642fdf519a51e6d218d12484c03c1a98f0704daed3db4dc70` проверен локально.
  `source-binding-fix.patch` — минимальный кандидат: добавить exact line29 с anchor, сохранить invocation anchors,
  source SHA, exact selectors и остальные gates. `git apply --check` на pinned control прошёл.
  Static replay на трёх exports: S→I/UNKNOWN;15 мутаций selector/crate/mode/file/line отвергнуты.
  Patch не применён к control и не изменяет исторический collected.json; новый control/review/CI в эту стадию не входят.
- **2 A**: false-ensures default/override реально завершились assertion FAILURE на строках smallsort.rs41/63.
  Descriptions содержат S1_ATTACHMENT_DEFAULT/OVERRIDE; exact properties F7/F8 и mutant hashes сохранены.
  Но request oracle=null, а runner явно не принимает эти variants. Это наблюдение attachment-срабатывания,
  а не заранее квалифицированный negative oracle. Обе covers UNREACHABLE после ложного ensures.
  Нельзя задним числом выдать DETECTED; следующий пакет требует независимого source/contract-wrapper binding.
- **1 C**: ordinary-bridge SUCCESS,12/12 SAT,0 unreachable/unsupported. `runner.py:828-831`
  сравнивает human-readable required_cover_messages непосредственно с property IDs в covers.satisfied.
  ID не равен message. Нужна проверенная таблица message→exact ID; число12 не заменяет её.
  Аналогичный gate возникнет у других positives после квалификации exceptions.

Шесть E — исходные exact ID/file/line/class negative controls: require_active×3,
order/count corruption и invalid snapshot. Каждый имеет ровно один требуемый assertion FAILURE;
посторонних failures нет. Это подтверждённые negative observations; helper exception qualification отдельно pending.
Все4 replacement unions INCOMPLETE_CASES по исходному oracle, eligible_for_review=false:
сырые16/16 SUCCESS не заменяют именованные success/cover bindings и квалификацию exceptions.

**Принятых положительных obligations0; independent B1 acceptance и B2/general theorem не установлены.**
Источник сообщает bounded SUCCESS для27 roots, включая16 exact-N и2 Cell actual-target PFC;
model controls сами по себе не доказывают actual sort. Все35 выбранных строк OBSERVED;
NOT_SELECTED в отдельных job receipts относится к другим partitions и исчезает при collection.
Четыре legacy symbolic roots исключены из schedule S1-04 и здесь NOT_RUN; их исходные obligations пока не закрыты union.

## Проверка и передача

`intake.py`: статический replay35/35 совпал с оригинальными parsed receipts; проверены14 exact selection sets,
export hashes, source snapshots, request pins, unchanged within-job binary fingerprints и property partitions.
Файлы ROWS.json/GROUPS.json содержат полный per-row/per-group результат;
evidence/ — exact export bytes и JSON-проекции receipts без stdout/stderr.
BOUNDED-EXCERPTS.json сохраняет только уже bounded head/tail из receipts. Raw .log файлы не открывались.
PROVENANCE.json связывает artifact IDs/GitHub metadata, hashes и команду collection.
Archive digest — только claim GitHub metadata: ZIP digest независимо не сверялся.
Координаты/hash/source snapshots не устанавливают AST/MIR/parser-input binding.

VALIDATION.json: PASS для intake и минимального patch replay. Это статическая проверка сохранённых данных;
локальные cargo/rustc/Kani/CBMC не запускались. Push/CI/публикаций/ledger не было.
Одна intake-стадия завершена; следующая — отдельное задание на qualification/runner package, без автоматического dispatch.
