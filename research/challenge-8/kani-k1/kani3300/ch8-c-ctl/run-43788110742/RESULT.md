# C-01 intake — run 43788110742

Одна стадия от g0 `d535d987b4`. C-02 подготовлен отдельно в `../c02/`; новых запусков нет.

Artifact `14190978387`, ZIP SHA256 `5988b9c653717801deefd4f020088a34dfebac1482a0a63cfa73d15c75195cae`
совпадает с GitHub digest. JSON прочитаны из scratch; raw logs не читались.
Control `64ec781bc1` и dispatch sibling `d224c83361` имеют одинаковую tree
`33e95dc779cefde33132f8e265d9588b9d905b14`; sole parent sibling — stock tool `0aac16ef62`.
Std `d073585946` на P′ `c5ff36ff43`. Control и tool — разные предусмотренные роли, расхождения pin нет.
Request SHA совпал с job-status; source/binary snapshots до/после каждой группы совпали.
Оригинальный parser воспроизвёл все 8 row exports точно. Оригинальные receipts сохранены без правок.

| Root (префикс c_controls) | Oracle | Kani | Классификация фактов |
|---|---|---|---|
| c_merge_source_write_restore | frame FAIL | FAILURE 280/2 | N1 frame diagnostic пойман; также memcmp unwind; строгий oracle UNKNOWN |
| c_merge_source_read_only | PASS | FAILURE 280/1 | Только memcmp unwind; legal companion не прошёл |
| c_callback_live_shared_in_outer_frame | stock PASS / ALIAS_GAP | SUCCESS 292/0 | N2 documented alias gap, source-reported; не разрешение Rust |
| c_callback_read_only_in_outer_frame | PASS | SUCCESS 292/0 | Expected legal companion verdict |
| c_external_mut_state | PASS | SUCCESS 274/0 | Expected external-mut verdict |
| c_external_cell_state | PASS | SUCCESS 245/0 | Expected external-Cell verdict |
| c_insert_tail_local_lifetime | PASS | SUCCESS 193/0 | Expected lifetime/copy-back verdict |
| c_local_storage_reuse | PASS | SUCCESS 30/0 | Expected ended-borrow/reuse verdict |

Group-01: compile **29.463 s** (не 28 s), exit1, 18/30 covers SAT.
Group-02: compile28.089 s, exit0, 3/3 covers SAT. Job failure.
Это verdicts экспортера; independent acceptance всех строк UNKNOWN, credit NONE.
В шести PFC receipts `CONTRACT_TARGET_BINDING_MISMATCH`; две ordinary — `INCOMPLETE_CHECK_INVENTORY`.
После исправления только source-spelling binding строгий inventory gate всё ещё закрыт:
у двух merge checks 274/275 UNDETERMINED, у остальных 2–6 UNREACHABLE;
unsupported entries у merge UNDETERMINED, у SUCCESS-строк SUCCESS, но gate запрещает любой непустой inventory.
Они не объявлены дополнительными failing properties и gate не ослаблен.

## Binding и named failures

N1: `ptr::write_volatile::<u64>.assigns.1`, class `assigns`, description
`Check that *dst is assignable`, exported location `library/core/src/ptr/mod.rs:2282`.
Pinned source там исполняет `intrinsics::volatile_store(dst, src)`.
Это frame diagnostic на merge PFC; oracle требует связь именно с callback writes `c_controls.rs:23/25`.
Такой AST/MIR/trace связи JSON не содержит: exact matcher не расширен, detection credit не принят.
Оба merge имеют ещё `memcmp.unwind.0`, class `unwind`, `<builtin-library-memcmp>:25`.
Other pointer/assert/alias failures не экспортированы как FAILURE.

Export PFC target — исходный TokenStream (`bidirectional_merge`, `callback_outer::<true/false>`,
`external_mut`, `external_cell`), а request хранит resolved qualified target без const argument.
Поэтому raw equality отвергла все шесть PFC. Profiles worker11 подтвердил тот же класс ошибки,
но для C требуется exact source spelling, включая const arguments, а не terminal-only matching.
C-02 фиксирует только выбранную merge-пару: pinned import, PFC attribute, file/line/unwind и token equality.
Mangled contracted symbol сохранён; его независимое разрешение, retained-write causality и source-label→ID
correlation остаются PENDING. Полные observed поля и координаты — `ANALYSIS.json`.

## Все 12 не-SAT covers group-01

Exact IDs/status записаны для каждого harness в `ANALYSIS.json` (включая SAT для контекста).
Разложение без потерь: **3 UNDETERMINED + 9 UNREACHABLE**:

- merge write: fixture `.cover.1` UNDETERMINED (return-side context после memcmp);
- merge read: fixture `.cover.1` и callback `{closure#0}.cover.2` UNDETERMINED;
- N2 write: три `{closure#0}.cover.1/2/3` UNREACHABLE при трёх SAT covers generated contract clone и SAT fixture return;
- N2 read: те же три original closure covers UNREACHABLE и nested clone `.cover.2` UNREACHABLE (`WRITE=false` transient-write branch);
- external mut и Cell: по одному original `{closure#0}.cover.1` UNREACHABLE; соответствующий generated clone и fixture return SAT.

Это дополнительные сгенерированные экземпляры closures и constant-false ветки, а не 12 доказанно
недостигнутых обязательных исходных labels. Exact label→ID mapping не доступен: связь по порядку/имени —
интерпретация исходника. В частности, merge-return reachability ещё не установлена;
UNDETERMINED нельзя переименовать в UNREACHABLE. Required cover gates сохранены целиком.

## C-02

Оставлена только merge-пара и прежний oracle; шесть SUCCESS-строк повторять ради unwind не нужно.
Один compile вместо трёх групп при сохранении разных bounds всех8: cap2100s против7500s.
`backing == [2,1]` сравнивает два u64:16 байт. Для byte-loop memcmp нужны16 итераций и проверка выхода,
поэтому минимальный обоснованный bound17 вместо8. Это статическое обоснование, не измеренный C-02 PASS.
Std diff — ровно два `#[kani::unwind(8)]`→`17`; алгоритмы, source assertions, writes, requires,
frames, flags, checks, oracle locations не изменены. Подтверждение достаточности на backend остаётся NOT_RUN.
C-02 не обещает credit: исправление unwind не решает source-location/strict-inventory/cover-binding ограничения.

Обновлён только unpublished `ch8-c-now/LIMITATIONS-DRAFT.md` с отдельными C-01 pins.
Push/CI/публикаций/ledger/local cargo/rustc/Kani/CBMC:0.
