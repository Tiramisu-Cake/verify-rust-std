# E-01 intake — STOP E для текущего encoding

Одна стадия `TASK-CH8-E01-INTAKE-W15.md`, вход g0
`56b4134b5a62b9fba6461afcc94afe6a41c650a3`. Выполнено только чтение artifacts,
исходников и issues; новых proof runs нет. Корректность, не security.

## Evidence и identities

[Run 43783430196](https://github.com/Tiramisu-Cake/kani/actions/runs/43783430196)
имеет conclusion success **runner**, а не proof. Head
`3219b3f220de568a69275618944dbe26bfe2917d` и подготовительный
`628ba7fd9b8d1f66d5ccd220ce6ea84bc4626027` имеют одинаковый tree
`72cbddf7e01e4bc97c11358f7189b3dcda122921` и sole parent U.

| Pin | Exact tool SHA | Artifact ID / SHA256 zip |
|---|---|---|
| U | `0aac16ef62da9e9d5645782d458593e5d78143ba` | 14188654722 / `0fd0a3c15c54f012cfa86e7a1419f572d35ea985ef7f03db220e1189f5e73c44` |
| S | `14bc57fdb99960240c4944845a3d985c8af4dcf7` | 14190061402 / `b3fd3cfb3fe98a09d70cf4c5f705cdceed12eaa76e6dd8fa4d86ad35c2018d57` |

Zip скачаны через заданный gh API только в `/tmp/ch8-e01-intake-w15/` вне repos;
SHA256 совпали с GitHub artifact digests. Анализ из zip: 40 receipts, 30 полных
exports, 10 пар bounded tails для отсутствующих exports; raw job logs и полные
`*.log` не читались. Оба `build.json` COMPLETE/exit0, before/after pins совпали;
`job-status.json` FALLBACK сохраняет run COMPLETE, missing/incomplete receipts пусты.

Проверены request SHA `5461f1814049bcc1d7071a44a0f865917e625188b259985e18e1a4baee293299`,
rows SHA `b20e030f43b3a316c20a1b4d0275c6c78c6022e48060e9fb83f556fa39ac9c86`,
все fixture hashes, tool SHA/tree, exact harness selection, dirty=false, uninit
ось и отсутствие timeout/signal/truncated export. Общие exports: Kani 0.68.0,
Rust 1.101.0-nightly (7189d39d9, 2026-10-22), CBMC 6.11.0,
`x86_64-unknown-linux-gnu`, CaDiCaL; default checks сохранены,
`--object-bits 12`, 600s/harness, jobs1, без unwind override.
Solver binary version и actual MIR opt level независимо не связаны.

[EVIDENCE.json](EVIDENCE.json) содержит artifact/member coordinates, hashes,
исходные exits, failed IDs/locations/classes, covers, warnings и классификацию
каждой строки. Это производный intake, не raw archive и не независимый proof.
Успешные check IDs/cover descriptions в export отсутствуют: covers сопоставляются
с frozen single-root source по именам/порядку, без заявления полного GOTO binding.

## Матрица против CONTROLS.md / frozen ORACLES

I=intended; X=unexpected; S=setup. Числа — export `n_properties/n_failed`, включая
covers; terse stdout считает иначе. `SUCCESS` — наблюдаемый verdict. OFF H negatives
имеют только OBSERVE oracle. Всего I=20, X=11, S=9. Setup включает достигнутый
unsupported-construct check, не только compile error.

I классифицирует наблюдение против численного oracle, не выдаёт proof acceptance:
copy/OFF сохраняет runner UNKNOWN/INCONSISTENT_SUCCESS из-за status-SUCCESS
unsupported inventory, scalar/ON сохраняет оговорку о nondet lowering.

| Pin | Root | Axis | Export / properties | Class | Причина |
|---|---|---|---|---|---|
| U | `e_q_pointer_loop` | OFF | FAILURE 3129/8 | X | Положительный base/step + 6 pointer failures; exists ignored |
| U | `e_q_pointer_loop` | ON | NO_EXPORT | I | Точный safety-check guard; compiler101, export отсутствует |
| U | `e_q_false_pointer_loop` | OFF | FAILURE 3128/8 | X | Base действительно fail, но exists ignored + pointer failures: oracle загрязнён |
| U | `e_q_false_pointer_loop` | ON | NO_EXPORT | I | Точный safety-check guard; compiler101, export отсутствует |
| U | `e_q_isolated_witness` | OFF | FAILURE 3085/7 | X | Истинный witness fail вне loop; exists ignored + 6 pointer failures |
| U | `e_q_isolated_witness` | ON | NO_EXPORT | I | Точный safety-check guard; compiler101, export отсутствует |
| U | `e_q_scalar_invariant` | OFF | SUCCESS 66/0 | I | Return cover satisfied, без warnings |
| U | `e_q_scalar_invariant` | ON | SUCCESS 94/0 | I | Return cover satisfied; 3 arity/nondet warnings, proof credit NONE |
| U | `e_s_unbounded_slice` | OFF | NO_EXPORT | S | E0425: неверный namespace API; compiler101, без export |
| U | `e_s_unbounded_slice` | ON | NO_EXPORT | S | E0425: неверный namespace API; compiler101, без export |
| U | `e_h_live_after_havoc` | OFF | SUCCESS 72/0 | I | Covers satisfied |
| U | `e_h_live_after_havoc` | ON | FAILURE 80/1 | S | Unsupported [MaybeUninit; N] layout |
| U | `e_h_hole_inside_alias` | OFF | SUCCESS 72/0 | I | Covers satisfied; OBSERVE initializedness |
| U | `e_h_hole_inside_alias` | ON | FAILURE 87/1 | S | Unsupported [MaybeUninit; N] layout |
| U | `e_h_outside_false_alias` | OFF | SUCCESS 82/0 | I | Covers satisfied; OBSERVE initializedness |
| U | `e_h_outside_false_alias` | ON | FAILURE 101/1 | S | Unsupported [MaybeUninit; N] layout |
| U | `e_h_write_makes_readable` | OFF | SUCCESS 69/0 | I | Covers satisfied |
| U | `e_h_write_makes_readable` | ON | FAILURE 79/1 | S | Unsupported union/raw-pointer |
| U | `e_h_copy_makes_readable` | OFF | SUCCESS 88/0 | I | Covers satisfied; runner INCONSISTENT_SUCCESS из-за unsupported inventory |
| U | `e_h_copy_makes_readable` | ON | FAILURE 127/1 | S | Unsupported union/raw-pointer |
| S | `e_q_pointer_loop` | OFF | FAILURE 3129/8 | X | Положительный base/step + 6 pointer failures; exists ignored |
| S | `e_q_pointer_loop` | ON | NO_EXPORT | I | Точный safety-check guard; compiler101, export отсутствует |
| S | `e_q_false_pointer_loop` | OFF | FAILURE 3128/8 | X | Base действительно fail, но exists ignored + pointer failures: oracle загрязнён |
| S | `e_q_false_pointer_loop` | ON | NO_EXPORT | I | Точный safety-check guard; compiler101, export отсутствует |
| S | `e_q_isolated_witness` | OFF | FAILURE 3085/7 | X | Истинный witness fail вне loop; exists ignored + 6 pointer failures |
| S | `e_q_isolated_witness` | ON | NO_EXPORT | I | Точный safety-check guard; compiler101, export отсутствует |
| S | `e_q_scalar_invariant` | OFF | SUCCESS 66/0 | I | Return cover satisfied, без warnings |
| S | `e_q_scalar_invariant` | ON | SUCCESS 117/0 | I | Return cover satisfied; 3 arity/nondet warnings, proof credit NONE |
| S | `e_s_unbounded_slice` | OFF | NO_EXPORT | S | E0425: неверный namespace API; compiler101, без export |
| S | `e_s_unbounded_slice` | ON | NO_EXPORT | S | E0425: неверный namespace API; compiler101, без export |
| S | `e_h_live_after_havoc` | OFF | SUCCESS 72/0 | I | Covers satisfied |
| S | `e_h_live_after_havoc` | ON | FAILURE 249/2 | X | Shadow assigns120×2 |
| S | `e_h_hole_inside_alias` | OFF | SUCCESS 72/0 | I | Covers satisfied; OBSERVE initializedness |
| S | `e_h_hole_inside_alias` | ON | FAILURE 249/4 | X | Ожидаемый uninit-read 24 + assigns120×2: mixed, не clean negative |
| S | `e_h_outside_false_alias` | OFF | SUCCESS 82/0 | I | Covers satisfied; OBSERVE initializedness |
| S | `e_h_outside_false_alias` | ON | FAILURE 267/4 | X | Ожидаемый uninit-read 34 + assigns120×2: mixed, не clean negative |
| S | `e_h_write_makes_readable` | OFF | SUCCESS 69/0 | I | Covers satisfied |
| S | `e_h_write_makes_readable` | ON | FAILURE 224/2 | X | Shadow assigns120×2 |
| S | `e_h_copy_makes_readable` | OFF | SUCCESS 88/0 | I | Covers satisfied; runner INCONSISTENT_SUCCESS из-за unsupported inventory |
| S | `e_h_copy_makes_readable` | ON | FAILURE 270/5 | X | Shadow assigns120/170/171/173/183 |

## Почему нет export

Все 6 E-Q pointer ON: `rows/<root>/on/stderr.tail.log` содержит exact diagnostic
`quantifier predicates containing safety checks are not supported with -Z valid-value-checks or -Z uninit-checks`;
stdout tail сообщает compiler exit101, receipt сохраняет driver exit1.
Это intended refusal, не NOT_RUN из-за потерянного artifact. Guard U/S:
`kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:1267-1270,1337`.

Все 4 E-S: тот же bounded stderr tail содержит E0425 на fixture:6:
`cannot find function any_slice_mut_unbounded in crate kani`; compiler101/driver1.
Это ошибка подготовки fixture, а не свидетельство отсутствия uncapped storage.
В обоих pins `library/kani/src/lib.rs:37` экспортирует **модуль** `arbitrary`,
`library/kani/src/arbitrary.rs:205-218` определяет функцию внутри него.
Следующий source-only fix: `kani::arbitrary::any_slice_mut_unbounded::<u8>()`.
После него compile, alloc-model, init и actual core binding всё ещё UNKNOWN.
Ни solver timeout, ни нехватка памяти не объясняют эти 10 отсутствий export.

## H: raw write → shadow → explicit loop assigns

Наблюдается ограниченная несовместимость **этого explicit-frame пути** с ON на S.
Глобальная несовместимость всех loop contracts с uninit-checks не установлена:
scalar/ON возвращает SUCCESS, хотя имеет отдельное предупреждение lowering.

Точные S координаты, прочитанные `git show 14bc57fd:<path>` из object DB
`/root/kani-ch8-e-ctl-w15` (не из плавающего SEL1 checkout):

1. `MRE/e_h_write_then_read.rs:13-21`: frame охватывает destination и remaining;
   `destination_ptr.write(41)` действительно внутри contract loop, затем read/assert.
2. `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs:60-74,100-138`
   включает instrumentation и harness shadow setup.
   `.../ptr_uninit/uninit_visitor.rs:450-469` переводит raw store в
   `MemoryInitOp::SetRef(value=true, After)`;
   `:538-547` переводит `copy_nonoverlapping` в `MemoryInitOp::Copy`.
   `.../check_uninit/mod.rs:307-322` направляет операции в build_set/build_copy.
3. `library/kani_core/src/mem_init.rs:18-19` — marked `MEM_INIT_STATE`;
   `:267-278` set model вызывает `MEM_INIT_STATE.set`, а `:108-120` пишет
   `self.value`. Copy model `:380-397` → copy `:127-145` → copy_by_id
   `:152-183`, записи `tracked_object_id:170`, `tracked_offset:171`, `value:173,183`.
   Это ровно file:line failed properties в S export, включая `assigns` class.
4. **Loop** frame: `kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:73-112`
   создаёт targets из пользовательских pointers, `:260-274` записывает их в
   `gcx.loop_modifies`. `.../overrides/hooks.rs:884-904` добавляет только generated
   loop locals и прикрепляет `with_loop_modifies(assigns)`. Shadow static не добавляется.
   Эти строки одинаковы в U/S. Это прямое source объяснение конфликта с helper writes;
   exact transformed GOTO/CBMC attribution в artifacts отсутствует, не исследовалось.
5. `.../codegen/contract.rs:129-233` **действительно добавляет** shadow static
   (`:142-170,230`), но в **function modifies contracts**, не в предыдущем loop пути.
   Наличие этого кода не снимает loop failure.

U останавливается раньше на исполняемом unsupported check: array roots fixture:8,
write/copy roots fixture:8, до требуемого H oracle. Соответствующий U source:
`.../check_uninit/ptr_uninit/uninit_visitor.rs:117-129`,
`.../check_uninit/ty_layout.rs:139-145,403`: union field layout отвергается.
Это source-supported limitation U, а не доказанный runtime shadow-frame failure U.

S outside negative **имеет** ожидаемые safety failures на fixture:34 через alias
и satisfied sentinel/body covers; внутри-frame negative — на fixture:24.
Оба дополнительно имеют assigns120×2. Поэтому false-bit checks наблюдались,
но intended clean negative/control matrix не закрыта. S positives live/write/copy
не имеют uninit-read failure; их blocker именно assigns. Ни потеря init после havoc,
ни корректность must-init preservation отсюда отдельно не доказаны.

## Q/OFF: истинный invariant не опровергнут

На обоих pins `rows/e_q_pointer_loop/off/stdout.tail.log` сообщает ignored **3**
existentials; isolated witness — **1**, false-loop — **3**. Экспорт предупреждает
`warning: ignoring exists`, `failure_kind=ERROR`. Положительная и ложная формы
не различены надёжно; наличие named base failure у mutant недостаточно.
Ключевой separating control: isolated positive ломается **без loop contracts**.
Ошибка frame/H не объясняет этот отказ. `[1,2]`, i∈[0,2), witness i=1 — корректны
на уровне исходной программы; pointer failures не являются установленным UB этого кода.

Source chain U/S: `library/kani_core/src/lib.rs:234-238` создаёт closure;
`.../overrides/hooks.rs:1145-1172` пытается pure predicate, иначе closure-call fallback;
`:1176-1187` строит range AND predicate для exists;
`:1301-1328` extraction/substitution и side-effect test.
Raw `p.add(i)` проходит вызовы, включая `ToISize::to_isize`
(`library/kani_core/src/models.rs:202-207`, failed location:204).
Это сложный encoding, даже при literal границах 0,2.
`kani-driver/src/call_cbmc.rs:409-433,508-515` распознаёт ignored quantifiers,
форсирует FAILURE/Error и советует SMT. Его текст про **non-constant bounds** общий:
source bounds здесь constant, так что это не установленная причина именно этой формы.
Warnings в export обрезаны до4096 chars (original около114–119k); их полные деревья
не восстанавливались. Нельзя точно установить, какой узел после lowering мешает
SAT instantiation, или назвать один compiler pass окончательно виновным.

Итог: наблюдаемое ограничение backend/quantifier encoding на этих pins, не ошибка
математического invariant и не причина расширять user frame. Z3 — кандидат следующей
отдельной калибровки, **не проверенное исправление**; известны и независимые defects
existential fallback. ON запрещён текущим guard независимо от выбора solver.

Scalar/ON U94/0, S117/0 и return cover satisfied, но в обоих exports трижды:
`is_ptr_initialized ... not enough arguments, inserting non-deterministic value`
на fixture:11:37. Это intended observed SUCCESS с существенной оговоркой, не
доказательство корректного init-инварианта или общего рабочего обхода E.

## Upstream issues — только read-only поиск

Проверено через `gh api` 2026-11-16, без comments/issues/PR публикаций.
Search в `model-checking/kani`: `quantifier pointer`, `"ignoring exists"`,
`"not enough arguments"`; для H — сочетания `"loop contracts" uninit assigns`,
`"uninit-checks" "loop_modifies"`, `"assignable" "loop_modifies"`,
`"tracked_object_id"`, `"self->value"`, MaybeUninit/union/raw pointer.
Отдельный exact issue про shadow-field loop assigns не найден; это ограниченный
результат поиска, не доказательство отсутствия дубля.

- [#4282](https://github.com/model-checking/kani/issues/4282), open: quantified
  loop invariant + ignoring forall, related, другой predicate.
- [PR #4719](https://github.com/model-checking/kani/pull/4719), closed: fail when
  backend drops quantifiers; explains conservative FAILURE, не fix E-Q.
- [#5004](https://github.com/model-checking/kani/issues/5004), open: branch extraction
  и existential fallback; [#5010](https://github.com/model-checking/kani/issues/5010),
  open: quantifier defects; [#5141](https://github.com/model-checking/kani/issues/5141),
  open: dropped checks. ON guard убирать нельзя.
- [#4796](https://github.com/model-checking/kani/issues/4796), open: loop-invariant
  calls, not-enough-arguments/nondet; related к scalar warning, injected helper иной.
- [#3300](https://github.com/model-checking/kani/issues/3300), uninit umbrella;
  [#5151](https://github.com/model-checking/kani/issues/5151), open: MaybeUninit arrays
  unsupported; связан с U limitation, не exact shadow assigns report.
- [#4906](https://github.com/model-checking/kani/issues/4906), closed: generated locals
  assigns; [#4790](https://github.com/model-checking/kani/issues/4790), open: builtin
  memcmp locals assigns. Аналогии, не подтверждённые дубли shadow-state дефекта.

[Черновик issue](MRE/ISSUE-DRAFT.md) описывает новый **candidate** defect H и честно
отделяет наблюдённый SEL1 repro от NOT_RUN primitive upstream candidate.
Нового Q issue без отделения известных limitations не предлагается публиковать.

## Решение и допустимое продолжение

**STOP E для текущей ON quantified-pointer/explicit-frame схемы**. E-Q OFF тоже
не откалиброван; E-H ON не проходит positives/clean negatives; E-S не дошёл до модели.
E-L/B/I/F/D/R/P/O/Z actual-insertion rows в E-01 не запускались и не закрыты.

В следующей отдельно разрешённой стадии можно исправить только API namespace E-S,
проверить primitive H candidate + matched no-write/OFF controls, отдельно изучить
loop shadow bookkeeping и scalar arity warning; Q — matched SMT/scalar/no-loop
калибровка с true/false predicates и всеми checks. Возможный compiler fix требует
собственного review и controls inside/outside/alias/write/copy, не просто разрешения
havoc всего shadow без сохранения relation/false bits. Не менять core/std и не
продвигать full insertion/theorem до gates. Нельзя CAP fallback, assume вместо
invariant, выключение uninit/default checks или ручное initialized=true.

Независимый proof credit NONE; B2/full proof нет; bounded control observations
не расширены до arbitrary-length или generic-T theorem. Новых CI/push/publications,
ledger/trusted-model изменений и локальных cargo/rustc/Kani/CBMC нет.
