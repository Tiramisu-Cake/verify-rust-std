# KANI3300 M2-B/R4 — runtime narrowing, ≤3 variants на P1, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна диагностическая/подготовительная сессия,
**Cloud $0**. Fork CI только координатора; local compiler/verifier/builds запрещены.
Это верификация корректности, не security-работа.

## Вход и интерпретация предыдущего опыта

Прочитать `kani3300/m2br3/` @ **c70a35409b5c6447cf8c16a354157e9565edcecc**, особенно ABLATION-PLAN,
TYPE-AUDIT/patches/DIAGNOSTIC-MANIFEST и original P1 из m2a. Исторические records не переписывать.
По координатору один и тот же P1, existing watchdogRSS>6GiB:

- V01 **51fe0993de670a2c3b582ebff41f8344eca5a2b0**, run**43258912765**: 144props/eloc247,
  11504steps,572→168VCC, >6.5GiB за9.7s, killed на conversion; return-selection-only rollback недостаточен.
- V02 **48d10f9ff2a78ab0ee35e9b9c58cc28bc304ae7d**, run**43258921276**: U runtime + R1 emission,
  151props/eloc228,11396steps,536→191VCC; ConvertSSA8.46s, **844029vars/51222776clauses**,
  дошёл до solver без watchdog; FAILED, детали capped. PeakRSS/full Failed Checks UNKNOWN, semantic gate не закрыт.
- U run**43253856019**: **284883vars/17072414clauses**, ConvertSSA2.96s.
  R1/V01 не дошли до size print; их CNF size UNKNOWN, нельзя оценивать вычитанием или cap threshold.

V02 локализует различие conversion outcome в **runtime group**, но смешивает placement, pointer-vs-ID lifetime,
copy arithmetic/fallback и selection. Это ещё не конкретный hunk/эквивалентный корректный фикс.
R1 emission на U runtime имеет ≈3×variables/clauses против U при matched settings; это secondary observation,
не основание параллельно менять compiler emission или считать вклады аддитивными. V01 не исключает interactions.
Сначала запросить bounded полный список V02 failures/phase receipt через existing interface, если доступен: прежний cap
не превращать в отсутствие frame/Unsupported/UB. Никаких новых U/R1/V01/V02 solver reruns в этой очереди.

## Рабочая область и базовые инварианты

Смотреть committed objects U **bf9c58e662fd65c64381ef2ac97a6397ffc0693a** и R1
**1cd96e354ec45346b61c245554a50a8af8cb5ce7**; `/root/kani-fix-3300-m2br3` read-only, не использовать dirty files как base.
Создать отдельный clone **/root/kani-fix-3300-m2br4**, root branch **experiment/kani-3300-m2br4** от exact R1,
до3 sibling variants **-a/-b/-c**, каждый прямой потомок R1, не накопительная цепочка. Existing/dirty destination → STOP без reset/stash.
Release/M1/M2/S3 source/fixtures/ветки не менять. R1 Uninit compiler emission и model marker signatures во всех variants unchanged.
Scope — `library/kani_core/src/mem_init.rs`; для A только узкая дополнительная private-assigns registration в
`codegen_cprover_gotoc/codegen/contract.rs`, если необходима. Этот ancillary delta отдельно от runtime и его стоимость видна в manifest.
Все candidates NOT_RELEASE_CANDIDATE, no push. Public ABI/guards/assume/checks/solver/bounds не расширять.

## Три независимых различителя, сначала доказать source dependency closure

**A — placement/DFCC shape при сохранённой R1 by-ID семантике.** Перенести только пять scalar argument_buffer fields
из marked MEM_INIT_STATE в отдельный private `ARGUMENT_BUFFER` record: active/index/saved_object_id/saved_offset/layout_size.
Сохранить field types/values, constructor/reset active=false, store/load order, mandatory return0, copy_by_id/bless_by_id,
все relative-offset/fallback правила R1. Не возвращать saved raw pointer или Option-путь U.
Составить явное field-state correspondence до/после. Main tracked object/offset/value остаются в исходном marked static.
**Оба** private objects должны присутствовать в emitted DFCC assigns: отдельная однозначная static identity/marker и
explicit registration только этих объектов, без user-memory exemption. Не дублировать существующий state marker:
его uniqueness сохранять; marker parser/lookup/declared symbol/actual two lambda targets проверить по pin.
Если необходима broader marker/ABI rewrite — A BLOCKED, не маскировать его unmarked buffer/frameFAIL как comparable variant.
Цель — отличить combined whole-object/private view от copy math, не «убрать» frame checks.

**B — только association арифметики offset.** Сохранить R1 state placement, captured object/offset, source guard,
return-selection, early return после retarget и full-span fallback. В copy_by_id поменять лишь
`tracked_offset = to_offset + (tracked_offset - from_offset)` на legacy `tracked_offset += to_offset - from_offset`.
Все операнды usize; legacy subtraction может underflow при to_offset<from_offset, чего source guard не исключает.
Это diagnostic loss/новые overflow obligations, **не** заранее корректная алгебраическая оптимизация. Не добавлять assume,
wrapping/saturation/disable-checks для скрытия различия. Bind actual retained arithmetic/VCC widths/operators до вывода.

**C — fallback/control-flow при сохранённой R1 safe-offset форме.** State/by-ID capture/mandatory return и
`to_offset+(tracked_offset-from_offset)` оставить R1. В copy_by_id восстановить legacy policy: source-match + declined
demonic retarget не blessing destination; только nonmatching-source branch вызывает bless_by_id(to_obj,to_offset,1).
Не использовать dangling source pointers. Это меняет declined-follow clearing и span num_elts→1; перечислить обе потери.
Если actual P1 count всегда1, span часть no-op, но matched-source/decline часть ещё может быть различающей: установить,
какая операция реально retained. Если обе части не достигаются/упрощены одинаково, C DEFERRED, не тратить CI slot.

Для каждого: exact hunk/diff/base/tree/hash, marker/API dependency check, hypothesis/falsifier, old→new expression/type,
retained/lost obligations, ожидаемые extra failures и какую причинность результат не устанавливает.
Никаких новых arrays/масок/usize-width truncation для «лечения» ресурса. Не сужать object/offset до u32/object-bits без proof.
Если фактическая dependency делает variant composite, перечислить её; не импровизировать четвёртый вариант.

## Что измерить по функциям/типам

В RUNTIME-MAP связать copy/copy_by_id/bless/bless_by_id/store_argument/load_argument, constructor/reset и DFCC private
targets с actual retained statements/VCC/operands. Source MEM_INIT_STATE scalar, Layout<N> отдельный тип.
Запросить только bounded projections по этим instances: actual N/element storage width/sizeof T; range arithmetic,
pointer-object/offset casts, aggregate/array assignment/update/equality, dynamic indexing и count/multiplicity.
Отдельно declared width, retained expression width, post-DFCC view и Boolean encoding cost; не выводить «огромный массив» из RSS.
Для A получить оба private object extents и write-set/havoc/snapshot/assign/compare operations; для B/C actual guards и arithmetic.
Если такой projection недоступен, precise query/UNKNOWN, а не придуманные widths или full formula dump.
Existing bounded CBMC recipe/verbosity/--show-vcc из m2br3 можно переиспользовать только как non-solving diagnostic,
с explicit coverage/output cap; не менять normal solver argv. Raw archives/full logs/полные equations не читать/качать.

## CI-request и приёмка диагностики

Максимум3 runnable variants, **только P1**, по одному root/solver; P2 пока не запускать. P1 SHA256
**fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b**, root `postcondition_reads_initialized_return`.
Сначала build/type validation + inventory, затем admitted solver; для C сначала hunk applicability check.
Те же actual target/sysroot/toolchain/CBMC/solver/checks/PFC/uninit/object-bits/slicing/unwind/inlining/flags/байты input,
existing timeout300s/watchdog>6GiB. Перенести validated argv template из m2br3/CI-REQUEST, env edition2021/-Dwarnings.
Указать sampling/overshoot/RSS raw units/PID vs tree/stage exit/signal; cutoff INCOMPLETE, build failure solver NOT_RUN.
По каждому: GOTO/props/eloc; symex steps/VCC; ConvertSSA start/end/runtime; vars/clauses если напечатаны; SAT-entry отдельно;
полный bounded failure inventory с IDs/class/location и coverage/cap. Parser/job SUCCESS или просто FAILED не gate.
Изменение/потеря условий/числа retained operations не считать эквивалентным speedup, но сохранить как диагностический результат.
Ни model repair, ни M3 activation автоматически не следуют из более дешёвого варианта.

## Направление фикса, type audit и результат

**Подтверждённого узкого production fix пока нет.** Если A снимет рост при сохранённых private writes/frame/transfer paths,
рассмотреть отдельный private-buffer representation/assigns patch с field correspondence и корректным reset/epoch.
Если различает B/C — искать доказанно эквивалентное упрощение range/retarget expressions, сохраняя lifetime-safe by-ID,
correct relative-offset, full-span overwrite и false-source propagation. Legacy underflow/count1/stale-state rollback не fix.
Новая representation/ABI premise или broad CBMC patch — STOP/proposal. Сначала causality/control, затем отдельное release задание.

M2-B/S3 уже прошёл restricted Quick по координатору: candidate4f64cc617c (fix58497d98d0 + const HOLE repair),
run43257528539/CI fc3bccbfff, unit5/0,kani22/0,expected135/0/2ignored,ui14/0,script1/0;
CI-only исключил **legal-pair и postcondition-hole**. Это не тяжёлый PFC/full gate. После resource repair потребуются
интеграция с актуальной M1/M2/S3 и возврат обоих selectors + P1/P2/legal/frame/false controls; сейчас M3 HELD.

TYPE-AUDIT каждого Rust delta обязателен: operand/result/API/field types, обе стороны integer expressions,
usize/u64/u128 bounds/conversions, borrow/deref и marker completeness; учесть B3 E0308/E0277.
Pinned rustfmt/diff/hash/source/Python checks разрешены; rustfmt/Luna не compilation, local cargo/rustc/Kani/CBMC/Miri/builds нельзя.
Один bounded Luna High review field correspondence/patch dependency/type audit/lost obligations, без nested delegation.
g0 **kani3300/m2br4/**: INPUTS.json, RUNTIME-MAP.md, ABLATION-PLAN.md, DIAGNOSTIC-MANIFEST.json,
TYPE-AUDIT.md, patches/, CI-REQUEST.md, REVIEW.md, RESULT-KANI3300-M2BR4.md (≤25 строк).
Local diagnostics без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, не push.
Research [skip ci], тот же author/committer, stage только m2br4/, push g0 без force; concurrent update → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow/runner edits, credentials, PR/issue/комментариев/сторонних PR links.
После reviewed package STOP до CI координатора. Последняя строка: `READY <sha research-коммита M2-B/R4>`.
