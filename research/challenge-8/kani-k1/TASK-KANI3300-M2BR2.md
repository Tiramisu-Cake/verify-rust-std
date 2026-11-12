# KANI3300 M2-B/R2 — actual type widths, DFCC touchpoints и early-Part1 bisect, worker 15

**Выдано координатором 2026-11-12; worker15 свободен.** Runtime **Codex**, одна аналитическая/подготовительная сессия,
**Cloud $0**. Никаких локальных compiler/verifier/сборок; fork CI запускает координатор.
Это верификация корректности, не security-работа.

## Вход и новый установленный интервал

Прочитать TASK-KANI3300-M2B-RESOURCE.md и `kani3300/m2br/` @ **c90cb9466dfef600b3da36dc9703660dd97a2393**,
особенно HISTORY-MAP, FRAME-BINDINGS, DIAGNOSTIC-MANIFEST и CI-REQUEST. Не повторять R01–R04/переписывать historical results.
Inputs P1/P2 остаются побайтно из M2-Aea0fbb5931; exact roots/flags/hashes закреплены ниже/в прежнем manifest.
По координатору inventory+solver, sequential, watchdog CBMC RSS>6GiB:

| Source / fork run | GOTO / properties / eloc | Symex / steps / VCC before→after simplification | Outcome |
|---|---|---|---|
| A2R **b207847932**, **43249040713** | 239KB / 160 / 239 | 0.32s / 11348 / 699→186 | >6.48GiB за9.6s, killed |
| A3R **a0a2386001**, **43249047207** | 338KB / 276 / 331 | 0.36s / 14420 / 948→192 | >6.43GiB за7.6s, killed |

P2≈P1 по сообщению координатора; точные per-case values/units/phase timestamps не выдумывать.
Upstream run43244395728 ранее46s/1.4GB, frame store_argument/unreachable load и Unsupported, не semantic PASS.
Оба новых pins тяжелы уже после reported symex/postprocess: **A3 не необходим для воспроизведения**; дополнительные эффекты
A3 не исключены. GOTO bytes/property count не ограничивают ширину/стоимость формулы. Conversion/bit-blasting — рабочая
локализация по coordinator receipt; exact entry/last milestone/CNF/SAT-start сохранить или пометить UNKNOWN.
Большой объект/array — гипотеза, не следствие одного RSS: учитывать также число/вид intermediate operations.

Worker14 owns Assert/ensures missing-binding track `kani3300/m2bs/` @45ca2e8f71; его source/tasks не менять.
Seed repair не заявлен готовым, M2 semantic и resource/frame gates открыты, M3 HELD. Этот трек — без release/model fixes.

## 1. Точечный type/size inventory из actual GOTO

Read-only source `/root/kani-fix-3300-m2` и historical git objects. В source marked MEM_INIT_STATE перед A3 имеет
6usize/2bool, после A3 11usize/4bool; встроенного массива там нет. Actual emitted layout всё равно нужно измерить.
Рассмотреть не только сам static, но reachable Layout<N>, contract captures, snapshots/havoc views, generated DFCC
write-set/helpers, CBMC object/memory backing types и temporary expressions, которые используют его адрес или значение.

Через existing authorized curated artifact interface запросить **ограниченные projections**, не полный symtab/log/archive:

1. Exact pre-DFCC symtab artifact/hash/source/input/tool identities и stage; marker→actual mangled MEM_INIT_STATE symbol,
   type/tag/typedef chain, поля/offsets/alignment/padding и sizeof bytes/bit-width. На upstream отдельно ARGUMENT_BUFFER,
   его Option/discriminant/payload и отдельный assigns membership. Не считать usize::MAX sentinel длиной массива.
2. Рекурсивно разрешённые array/vector lengths и element widths, pointers/targets, union/struct layouts и unresolved/symbolic
   extents; ranked **top20** largest declared fixed types/objects с владельцем/instance. Для Layout<N> дать **actual N**,
   тип T/instance/callsite, source sizeof(T) binding и total width. Dynamic extent — expression/range, не guessed constant.
3. Такой же targeted inventory **после DFCC**, плюс top20 widest retained SSA/equation expressions на входе Boolean conversion,
   если existing backend reporting это предоставляет: type/width/operator/location/owner, array equality/update/index,
   casts, pointer/object-whole operations. До/послеDFCC и послеsymex — разные artifacts/стадии, не один symtab.
4. Если exact SSA-expression inventory недоступен, пометить его UNKNOWN; допустимы available pre/post types и narrow
   source-bound backend query proposal. Не заменять его full equation dump, новым trace framework или выдуманным CLI.

JSON schema/CBMC options сначала проверить по source/version. Kani serializer — `cprover_bindings/src/irep/serialize.rs`
(`symbolTable`); исходные GOTO .symtab.json и backend-generated types могут иметь разные representations.
`Type::sizeof/sizeof_in_bits` не вызывать вслепую на incomplete/recursive tags: это может panic, как в B3-аудите.
Если готовится pure Python extraction/query recipe для координатора: explicit type-reference resolution, cycle/depth/record
limits, произвольная integer arithmetic, bytes/bits отдельно, **не разворачивать N элементов/не аллоцировать width-sized buffer**.
Schema/hash/synthetic snippet checks разрешены локально; compiler/GOTO executables — нет. Старые raw-access exceptions не действуют.
При отсутствии projection подготовить точный file/symbol/query request; shortage данных — AWAITING_CI, не обход интерфейса.

## 2. Где именно DFCC затрагивает private storage

По actual emitted object (не только source имени) связать marker→symbol lookup→assigns lambda→enclosing SimpleCheck/
modifies wrapper→instrumented write/havoc/snapshot/assign/compare→retained expression/type width→conversion stage.
У каждого звена location/instance/artifact coordinates/exactness; frame property `*var_8` без определения var не binding.
Проверить whole-static target, адрес/extent, aliases и generated backing views: какое изменение upstream→Part1 превратило
store_argument writes из unmarked ARGUMENT_BUFFER в private exempted object и что это дало **в emitted DFCC**.
Source contract.rs byte-identical не означает одинаковые generated operations. Нужна actual операция, не догадка по modifies.
Если static и связанные types малы, гипотезу huge-static отвергнуть в измеренной форме и искать costly intermediate expansion:
Layout<N>/symbolic index, dynamic object view, array update/equality, arithmetic/conversion; перечислить точный discriminator.
Низкие192 VCC не означают низкую bit-width. Наличие большого типа без retained use в growing formula не доказывает причинность.
Upstream ранний Unsupported/frame может оставлять иной equation/path набор; не называть его скоростью эквивалентной проверки.

## 3. Exact bounded bisect request — максимум четыре source pins

Подготовить **CI-REQUEST.md** с таблицей ниже; других pins/new source ablations в этот batch не добавлять:

| Pin | Full source SHA | Зачем / запуск |
|---|---|---|
| U | **bf9c58e662fd65c64381ef2ac97a6397ffc0693a** | Existing upstream endpoint; reuse43244395728; недостающий targeted inventory, без автоматического solver rerun |
| R1 | **1cd96e354ec45346b61c245554a50a8af8cb5ce7** | Новый earliest Part1 endpoint: buffer migration, до A1; P1 inventory, затем admitted singleton solver |
| A1 | **613c188313e34e51e6a69d2c62bbd6ded2511819** | Новый A1-final endpoint: typed masks + ZST guard; тот же P1 inventory/solver |
| E | **b207847932da34ac19886c1337f5b69ace0b0843** | Existing heavy pre-A3 endpoint; reuse43249040713, targeted missing inventory, без автоматического solver rerun |

Сначала inventories; новые solver executions R1 и A1 sequential. P1 SHA256
**fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b**, root `postcondition_reads_initialized_return`.
P2 SHA256 **61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759**, root `postcondition_reads_returned_hole`.
P2 на этих же R1/A1 только после первичных результатов при отдельном admission координатора для проверки различающего
интервала; **не более4 новых solver invocations**, без retries/full matrix. Четыре source pins — лимит и для новых inventories.
Existing A3R/M1/B1I observations использовать как background, новые execution requests туда не добавлять.

Командный template/installed option validation, edition2021/-D warnings, actual proof_for_contract, -Zuninit-checks,
-Zfunction-contracts/regular/exact harness/keep-temps брать из m2br/CI-REQUEST. `--only-codegen` не включает DFCC;
для post-DFCC inventory нужен existing validated backend path. Одинаковые input bytes/target/toolchain/solver/checks/
unwind/object-bits/slicing/inlining и resource accounting; effective defaults/actual expanded argv сохранить.
Build failure или ранний Unsupported/missing path → NON_COMPARABLE, не cheap PASS; historical pins молча не чинить.
Existing timeout300s/watchdog>6GiB, sampling/overshoot/PID/process-tree/units/stage exits записать; cutoff = INCOMPLETE.
Cloud$0, fork только координатор; новый workflow/runner или unbounded automated bisect не создавать.

Интерпретация: R1 heavy → earliest tested heavy R1, исследовать U→R1 включая newly retained paths;
R1 cheap/A1 heavy → кандидат A1 interval; оба cheap при comparable paths → A1→A2/A2R interval.
Это onset brackets, не hunk causality/эквивалентность proof upstream. Не предполагать monotonicity: R1 heavy/A1 cheap,
разные widths/phase/path outcomes либо два heavy с разными mechanisms требуют отдельного объяснения.
Дополнительный pin/hunk ablation/causal repair — следующий handoff, после этого bounded package STOP.

## Результат, review и приёмка

g0 **kani3300/m2br2/**: `INPUTS.json`, `SIZE-MAP.md` (observed/derived/source-only/UNKNOWN, units), `DFCC-BINDINGS.md`,
`CI-REQUEST.md`, optional bounded extraction recipe + synthetic tests, `REVIEW.md`, `RESULT-KANI3300-M2BR2.md` (≤25 строк).
Не повторять большую историю; дать ranked suspects и конкретные discriminators. До CI — PREPARED/AWAITING_CI.
Приёмка анализа: complete narrow size/use chain либо exact missing fields; source bracket выводится только из comparable
actual outcomes. New proof credit0, seed/Part1 release не готовы. Модель, golden/assumptions/checks/user modifies не ослаблять.
Один bounded Luna High review type-resolution/query correctness и логики bisect, без nested delegation/полного seed review.
Любой Rust proposal/probe снабдить TYPE-AUDIT (все operands/result/API types, usize/u64/u128 conversions/bounds/deref),
учесть B3 E0308/E0277: rustfmt/Luna не compilation. В этой стадии production/diagnostic Rust edits не нужны и не разрешены.
Python/hash/schema/diff --check разрешены; local cargo/rustc/Kani/CBMC/Miri/builds, CI/Actions/Cloud dispatch/workflow edits запрещены.
Без raw archives/full logs/credentials, PR/issue/комментариев и сторонних PR links. Чужие файлы/branch/status не менять.
Research commit [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, stage только m2br2/, push g0 без force;
concurrency → handoff без reset/stash/force. После reviewed package STOP. Последняя строка: `READY <sha research-коммита M2-B/R2>`.
