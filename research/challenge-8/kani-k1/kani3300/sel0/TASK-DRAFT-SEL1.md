# TASK-DRAFT KANI3300 SEL1 — оператор select, Scope 1

**DRAFT, не GO/phase/dispatch.** Открыть после принятого v2 repair PASS, результата U1T и review SEL0. Координатор заново назначает Runtime, worktree/ветку, T0/окно, ledger/owner/lane, бюджет и резерв; текущий резерв $0. Ночные cap/резервы из ответов планера сюда не переносятся. В SEL0 нет ни одного запуска.

Финальную tool-base привязать к полному принятому repair SHA и опубликованному patch/tree, не к исследованному `81dd85bfce67226e283fdd9a156932e32ece080b`. Research source HEAD SEL0 — `becc9621ec6cae4669275e2c80568c18ea65b382`. Перед реализацией пересверить строки/семантику DESIGN с accepted base; сохранить pins std/toolchain/tooling/profile/config и исходные required controls.

Реализовать SelectUnpredictable только для инициализированных scalar/thin raw-data-pointer values: распознавание сигнатуры, union aliases двух arms, согласованные ptr-uninit и backend exhaustive branches. Runtime — строго if(condition), pointee shadow неизменен. Fallback codegen оставить семантически эквивалентным; обход operand/validity/delayed-UB checks сохранить. Не менять SKIPPED_ITEMS, ghost-state layout/static, общие contract flags, fnptr/vtable, прочие intrinsics, #3762 и алгоритмы std.

Для storage-result добавить явный guard с диагностикой `Kani does not support select_unpredictable with shadow-carrying storage results.` Он срабатывает до generic MaybeUninit return/buffer handling, без unpaired Store и лишних Unsupported. Scope 1 **не реализует** storage transfer. Реальный hint-wrapper даже для u8 упирается в `hint.rs:885`; это ожидаемая граница, а не приёмка U7.

`NATIVE-MANIFEST-DRAFT.json` — 19 exact selectors в schema существующего kani-tests runner: `harnesses=[]`, каждый expected selector с golden, `expect=pass` означает совпадение golden, а не VERIFICATION SUCCESS. Новые selector-файлы получают соответствующий fragment из `MICROFIXTURES.rs.txt`, общий header и нужные helpers; существующие regression-файлы брать побайтно из accepted v2, не из старого patch. Все 19 сейчас NOT_RUN. До dispatch изготовить production patch, добавить fixtures/goldens, pin/check-tooling/preflight штатным Cloud-путём и дать semantic diff/dependencies независимому Luna HIGH reviewer. Локально compiler/verifier не запускать.

| Selector suffix `uninit/select-sel1-…/main.rs` | Ожидание и обоснование по исходнику |
|---|---|
| values | SUCCESS, 2/2 covers: if-семантика intrinsics/mod.rs:749; разные arm-values, также bool/char/float. |
| pointer-initialized | SUCCESS, обе branches читают выбранные инициализированные u8; union aliases не должен давать spurious failure (instrumentation_visitor.rs:168). |
| pointer-uninit-true / pointer-uninit-false | По одному uninit u8 failure, разные positions uninit arm; selected pointee не благословляется (uninit_visitor.rs:724). |
| pointer-no-read | SUCCESS, выбор uninit/dangling pointee без deref допустим; проверяется только initialized pointer value. |
| delayed-true / delayed-false | uninit u64 failure на typed read после Pad write, по одному направлению aliases; initial_target_visitor.rs:73 + instrumentation_visitor.rs:131,198. |
| delayed-reinitialized | SUCCESS после полной u64 записи; тот же padding-cast остаётся, instrumentation setter обязан обновить state. |
| hint-scalar-guard / hint-pointer-guard | Только новый storage Unsupported, без assignable failures; реальный wrapper третий select MaybeUninit @ hint.rs:885. |
| storage-guard / partial-storage-guard | Только новый storage Unsupported, без ложного SUCCESS; selected-byte transfer не реализован, storage layout ty_layout.rs:132. |
| pfc-swap-direct | SUCCESS при узком modifies(x,y), native обе branches, нет ghost assigns; два select raw pointers, без storage-result. |
| pfc-swap-hint-guard | Только storage Unsupported, ноль instrumentation assignable failures; полный hint-путь из U7 не маскируется primitive imitation. |
| pfc-frame-negative | Пользовательская запись `*outside` обязана дать assignable failure при modifies(x,y); ghost exclusion не ослабляет frame. |
| existing v2 buffer-u3-positive / buffer-u3-frame-negative | Первый SUCCESS, второй assigns на outside, как в источнике mem_init Store/Load и существующем frame fixture. |
| existing v2 review-overwrite-copy / review-positive | Первый uninit `[u8; 2]` failure (пустой source overwrites initialized destination), второй SUCCESS; copy_by_id:130 сохраняет source witness и сбрасывает old destination path. |

Для каждого negative отчёт должен показывать реальный failed check и source location, отсутствие неожиданных failures/Unsupported/assigns, и reached read; golden-text сам по себе недостаточен. Covers/assertions и оба branch paths не удалять для прохождения. Timeout/setup/tool error не принимаются за expected negative. Два delayed negatives — обязательные controls, без них guard removal не принимается. Дополнительные excluded tests перечислить NOT_RUN.

**Core replay U7.** После native принять отдельно решение: Scope 1 сохраняет известный storage blocker, поэтому U7 нельзя считать закрытым и повторять за деньги ради того же blocker не следует. Для replay с целью SUCCESS сначала отдельным task/review разрешить узкий selected-shadow transfer `MaybeUninit<scalar/raw-data-pointer>` (DESIGN), добавить initialized/partial/Copy/Move/overwrite controls и перекалибровать manifest ≤20. Не заменять реальный hint-wrapper ручным if/primitive select в core source.

После этого финального native PASS и нового GO: отдельный diagnostic core пакет U7 (`uninit_probe::swap_contract_four_positions_u8_function_item`) плюс U1/U2 и U6 regression, прежние `-Z uninit-checks`/function-contracts, точные source/tool identities, function item, 2/5 covers из U2 не считать достаточными. U7 acceptance: normal return, все исходные assertions и все пять intended covers достигнуты, SUCCESS, ноль select Unsupported, uninit/validity failures и instrumentation assignable failures. U1 должен по-прежнему давать ожидаемый uninit u8 failure, U2/U6 — SUCCESS; все статусы сверить через Evidence Brief. Fn-pointer U4 не объявлять закрытым, U8/U9 и B2 общий theorem не входят в этот scope.

Контроль instrumentation causality: plain/PFC direct-select и реальный hint отличаются только wrapper-path; пользовательский frame-negative обязан продолжать падать. Если после accepted v2 снова есть ghost assigns или общий setup regression, сначала разобрать их по Brief, не списывать на Unsupported и не ослаблять modifies/checks. Резерв будущего native/core считать по final selectors, полным timeout+queue envelope, фактическому v2 ledger и новому окну координатора.
