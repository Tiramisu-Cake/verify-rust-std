# KANI3300 M2-B/R5 — binary runtime hunk search, первая пара, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна сессия подготовки первой пары; **Cloud $0**.
Fork CI только координатора, local compiler/verifier/builds запрещены. Это верификация корректности, не security-работа.
Принят подход владельца: две дополняющие группы runtime-хунков, затем ещё два варианта по результату первой пары.
Не продолжать перебор одиночных гипотез и не готовить автоматический full matrix/bisect.

## Вход и накопленные outcomes

Прочитать `kani3300/m2br4/` @ **df374dfdaa2959a59910d6a53424298784adc0b3**, R3 ABLATION-PLAN/TYPE-AUDIT/V02.patch
и actual R4 patches A/B/C. Не переписывать historical results. По координатору все три сборки прошли; P1:

| Variant / run | Symex steps / VCC before→after | Outcome |
|---|---|---|
| A split-private-buffer, **43263641666** | 9949 / 512→120 | >6.31GiB, killed |
| B legacy-offset association, **43263648365** | 9975 / 569→120 | >6.62GiB, killed |
| C legacy fallback/control, **43263654098** | 10101 / 509→120 | >6.57GiB, killed |

V01 return-choice-only тоже heavy. Это исключает достаточность каждого проверенного изменения на данном input,
но не interactions/комбинации. **Фактический C** менял nonmatching-only else **и** count num_elts→1, оставляя R1
relative-offset expression/early return; не описывать его как один числовой литерал или не выполненный эксперимент.
V02 **48d10f9ff2a78ab0ee35e9b9c58cc28bc304ae7d**, run43258921276: весь U runtime + R1 emission,
conversion завершён,844029vars/51222776clauses, solver FAILED с capped details. Это наблюдаемый конвертируемый endpoint,
не semantic PASS. Full failure inventory/actual retained paths остаются UNKNOWN при отсутствии receipt.

U **bf9c58e662fd65c64381ef2ac97a6397ffc0693a**, R1 **1cd96e354ec45346b61c245554a50a8af8cb5ce7** — parent/count1.
Меняем только их delta **library/kani_core/src/mem_init.rs (+77/−33)**. R1 compiler/contract.rs/macros/tests/driver/toolchain
и P1 заморожены; не переносить R4 A private-assigns extension. Release/M1/M2/S3 и работа14 не затрагиваются; M3 HELD.

## 1. Полная карта хунков и согласованные половины

Source читать из exact git objects в `/root/kani-fix-3300-m2br4` или m2br3, не из dirty worktree.
Сделать **HUNK-MAP.md**: каждому U→R1 изменению дать ID, source/header/context hash, функции/типы, dependencies;
назначить Hbuf/Hcopy/GLUE/comment-only. Никаких оставшихся неучтённых исполняемых изменений.
Половины балансировать по coherent code/dependency groups, не по механическим50% строк с разрезанной функцией.

- **Hbuf — representation/capture/consume:** удаление U ARGUMENT_BUFFER/ArgumentBuffer, новые buffer fields в
  MemoryInitializationState/constructor, active-reset, store_argument и load_argument. Включает pointer→object/offset,
  mandatory return0, match/layout-check/clear и обе стороны buffer lifecycle.
- **Hcopy — transition/copy/bless:** copy/copy_by_id и bless/bless_by_id bodies/wrappers, range arithmetic,
  retarget/early return, fallback branch/span. Сюда входят совместно B/C и прочие helper-body изменения, не один старый probe.
- **GLUE — обязательная API совместимость:** R1 load_argument вызывает copy_by_id; при откате Hcopy нельзя просто удалить
  эту функцию. Retained wrappers/helpers/interfaces должны быть перечислены отдельно, не объявлены откатанными.

Базовый план первой пары (оба прямые потомки R1):

**R5-01 = U Hbuf + R1 Hcopy.** Восстановить U отдельный unmarked `ARGUMENT_BUFFER: Option<ArgumentBuffer>`
(index:usize,saved_address:*const (),layout_size:usize), U main-state fields/constructor/reset, U store/load вместе.
Copy/bless/by-ID helpers и transition semantics оставить R1. U load вызывает copy_init_state_single, который через R1
wrapper попадает в retained by-ID path. Не менять compiler и не чинить frame: pointer lifetime/отдельный unmarked buffer,
mandatory-return loss и возможный frame/Unsupported/ранний read перечислить как диагностические потери.
Этот half rollback существенно шире R4 A, где сохранялся ID-buffer и добавлялся private assigns target.

**R5-02 = R1 Hbuf + U Hcopy semantics + explicit GLUE.** R1 scalar buffer/constructor/reset/store/load/return0 неизменны.
Оставить необходимые copy_by_id/bless_by_id signatures и thin wrappers, но в by-ID transition body воспроизвести U policy:
source-match → demonic retarget с legacy `tracked_offset += to_offset-from_offset`; matched/declined → без blessing;
только nonmatching → bless_by_id(...,1); отсутствие R1 unconditional tail/early-return structure.
Не восстанавливать pointer из object ID и не хранить dangling source pointer ради вызова U copy.
Source object/range inputs передавать в тот же по смыслу U core; public model marker/signatures неизменны.
Это **адаптированный half rollback**, не byte-identical U helper: retained GLUE и изменённые overflow/false/full-span
obligations явно отметить. Нельзя назвать такую пару буквальной независимой50/50 до dependency audit.

Если более буквальная компилируемая partition возможна по source, допустимо уточнить границу внутри этих двух групп;
конкретное сопоставление/GLUE rationale обязательно. Не подменять план новой memory model или runtime feature framework.
Проверить reconstruction: R1/R1 selection даёт exact R1; U/U после удаления ненужного GLUE даёт exact U runtime/V02 hash.
Наличие общего GLUE — самостоятельный оставшийся фактор, а не часть уже исключённой половины.

## 2. Отдельный clone, compile plausibility и два reviewed candidates

Создать **/root/kani-fix-3300-m2br5**, root branch **experiment/kani-3300-m2br5** от exact R1, sibling branches
**-hbuf** и **-hcopy**. Existing/dirty destination/другой pin → STOP без reset/stash; старые source clones read-only.
Подготовить только два local diagnostic commits и exact patches/trees/hashes; NOT_RELEASE_CANDIDATE, Kani не пушить.
Diff вне mem_init.rs → STOP, не исправлять compiler API/DFCC для удобства этого эксперимента.

Проверить по pinned source: все14 existing fn_marker declarations/13 model functions и normalized generic/signature
совпадают; все producer/callee арности, copy/bless/by-ID call graph, Option Clone/Copy, constructors/field references,
unsafe/static/borrow sites, reset coverage. Source grep только по committed variants; внешних dangling helper references нет.
TYPE-AUDIT: обе стороны arithmetic/comparison, usize/u64/u128, *const T/*const ()/*const u8/deref/mutability,
layout const N, type inference и conversion bounds. Слово compile-plausible не означает compilation PASS.
Учесть B3 E0308/E0277: rustfmt/Luna компилятор не заменяют; первый fork build проверяет типы/-D warnings.
GLUE не должен вводить новые assumptions/default true/индексное усечение/unchecked pointer reconstruction.
Semantic потери legacy runtime оставить видимыми; goldens/вход не менять, диагностический FAIL допустим с точным binding.
Pinned rustfmt wrapper TASK-M1, source/hash/Python/diff --check разрешены. Local cargo/rustc/Kani/CBMC/Miri/builds запрещены.
Один bounded Luna High review partition coverage/dependency closure/type audit/interpretation, без nested delegation.

## 3. Первая CI пара и решение о следующих двух

Запросить **только R5-01/P1 и R5-02/P1**, sequential inventory/build→solver через existing probe координатора.
P1 SHA256 **fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b**,
root `postcondition_reads_initialized_return`; P2/другие inputs/новые history baselines в эту пару не включать.
Actual argv/env/target/toolchain/solver/checks/unwind/object-bits/slicing/inlining одинаковы вне two manifest deltas;
templates из m2br3 CI-REQUEST. Existing timeout300s/watchdog>6GiB, sampling/overshoot/PID/raw RSS units/exit сохранить.
Для каждого: source/tree/input/patch identity, build status, GOTO/functions/props/eloc, symex steps/VCC,
conversion entry/end/time, variables/clauses если напечатаны, SAT-entry, полный bounded failure inventory/coverage.
Missing/capped data UNKNOWN; job/parser success не proof. Early frame/Unsupported/path loss — changed-obligation outcome,
не equal-obligation relief; размеры и actual retained use сравнивать отдельно от verdict. Raw logs/archives не читать/качать.

В ABLATION-PLAN дать **дерево второго шага, но не исполнять/публиковать третью/четвёртую сборку до нового handoff**:

- Только один half rollback конвертируется: subdivide его reverted group на два dependency-complete subgroups,
  сохранив прочий context и GLUE; до2 новых sibling patches после результата, не вывод «эта половина виновата» без retained-use.
- Оба конвертируются: возможны interaction либо две достаточные cut sets/потерянные paths; следующий шаг должен различать
  это с опорой на known endpoints, а не выбрать половину произвольно.
- Оба heavy при V02 конвертируемом: рассмотреть shared GLUE/связанный runtime interaction. Не исключать обе группы;
  проверить U/U-with-GLUE reconstruction и dependency map, предложить до2 различающих комбинаций по actual result.
- Build/error/неполный binding: исправить конкретную compile dependency отдельным commit и передать запрос координатору;
  не считать это отрицательным resource результатом. Идентичный уже проверенному tree/argv не отправлять повторно.

Никакой monotonicity premise для такого delta debugging. Вторую пару выбирает coordinator handoff после первой;
сейчас STOP после двух reviewed source-ready variants/CI-request. Не использовать неистраченные slots автономно.

## Результаты и границы

g0 **kani3300/m2br5/**: INPUTS.json, HUNK-MAP.md, ABLATION-PLAN.md, DIAGNOSTIC-MANIFEST.json,
TYPE-AUDIT.md, patches/, STATIC-CHECKS.json, REVIEW.md, CI-REQUEST.md, RESULT-KANI3300-M2BR5.md (≤25 строк).
Reported outcomes, source predictions и observed bindings отдельно. Конкретного production fix не заявлять до causality.
M2-B/S3 restricted Quick принят отдельно; M3/интеграция/возврат legal-pair+postcondition-hole ждут resource gate,
полезного P1/P2 и frame/false controls на актуальном кандидате. Диагностические откаты в release не cherry-pick.
Local diagnostics без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, не push.
Research [skip ci], тот же author/committer, stage только m2br5/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow/runner edits, credentials, PR/issue/комментариев/сторонних PR links.
Последняя строка после reviewed первой пары: `READY <sha research-коммита M2-B/R5>`.
