# KANI3300 C1-T2 — mixed tracked/promoted controls и привязка C1-T, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна test-only/analysis preparation стадия, **Cloud $0**.
Существующий Uninit Quick запускает координатор; никаких новых runner/framework/diagnostic adapters.
Это верификация корректности, не security-работа.

**Пакет уже подготовлен:** local test c2d607d9d5fafdc44a6c5fa3d981f760e522a05a, research10b5800a8e.
Создание fixtures повторно не выполнять. Coordinator CI — по kani3300/c1t2/CI-REQUEST.md;
следующий анализ — TASK-KANI3300-C1T2A.md после нового baseline/M1 handoff, не по старым агрегатам.

## Вход и новые наблюдения

Прочитать `TASK-KANI3300-C1T.md`, `TASK-KANI3300-M1.md`, `M1-NOTICE-C1T2.md`,
`kani3300/c1t/{NOTES.md,CI-REQUEST.md,TEST-MANIFEST.json}` @ **51b86a5214**, D0-A @ **ff5cabbfca**.
По координатору Quick **43219870063**, source **28e684cbae348130d559b87e030536d8f8a3c1ff**,
workflow-only checkout **172a7cfdbc02bd784873cfb4410d9b08fe51a9f1**: expected uninit **125/1/2 ignored**,
единственный FAIL — existing maybe-uninit-initialized; все 6 C1-T selectors совпали с goldens уже до M1.
Legal SUCCESS и hole FAILURE **не объясняют** механизм checks и не являются reproducer/qualification D0 immutable RHS.
Что фактически promoted, какие checks emitted/reached и где возник hole failure — ещё не привязано.

**Уточнение старта после M1 Quick:** M1 **5abdcf982da6aff65662e198af27a9c776830a89** (production 254ae69662),
run **43222702257**, CI **05024a2112b77da6d86d29f3d272bbc74ad5df98**: по координатору fmt/build/clippy PASS,
unit immutable_allocations 5/0, kani 22/0, expected 130/0/2 ignored, ui 14/0, script 1/0; unchanged D0 legal теперь PASS.
Все immutable-masks 4 и C1-T 6 matched; для C1-T это regression, не differential. Выполнять C1-T2 сейчас:
test-only base остаётся 28e684cbae, coordinator сравнивает baseline и **этот exact M1 + тот же новый test delta**.
Не переименовывать baseline в M1 и не исправлять model/новые M2 files; воркер 14 параллельно ведёт M2 от M1.

В `/root/kani-fix-3300-c1t` проверить clean branch/source HEAD выше; создать новую ветку
**tests/kani-3300-mixed-promoted-controls** от 28e684cbae, старую ветку/шесть fixtures не менять.
При ином состоянии STOP без reset/stash. Production как **6134e42dd1c65dc980336e7d9455aba02d423edf**;
M1 `/root/kani-fix-3300-m1` не трогать. Результаты baseline и M1 не смешивать.

## 1. Восемь новых selectors в tests/expected/uninit/mixed-promoted-allocations/

S — **actual tracked stack storage/assume_init temporary**, P — **actual anonymous immutable promoted referent**,
не named Static. Эти labels — требования к последующему MIR binding, не вывод из синтаксиса.

| Пара selectors | Operands/route | Semantic expected corrected-model |
|---|---|---|
| raw-u8-stack-left / raw-u8-stack-right | raw_eq над [u8;3], S/P и P/S | оба byte checks SUCCESS, equality true |
| eq-u8-stack-left / eq-u8-stack-right | настоящий std array == над [u8;3], S/P и P/S | legal SUCCESS; retained specialization/check route установить |
| raw-mu-stack-left-legal / raw-mu-stack-right-legal | raw_eq над [MU<u8>;3], S/P и P/S, всё initialized | SUCCESS, companion для hole того же типа/origin construction |
| raw-mu-promoted-left-hole / raw-mu-promoted-right-hole | raw_eq, P(hole)/S и S/P(hole); S полностью initialized | intended P byte-read FAILURE, S check SUCCESS |

Один harness на .rs + .expected, neutral names/license/edition2021/-D warnings/uninit-checks/regular по C1-T.
Трёхбайтные direct raw_eq — против известного scalar InstSimplify; подтверждение retained intrinsic всё равно нужно.
Для == сопоставить тот же размер с direct route, а **оба unchanged D0 [u8;4] harness** оставить обязательными в CI отдельно:
они уже воспроизводят известный defect, новые inputs должны его уточнить, не заменить.

S строить D0-подобно: адресуемое MaybeUninit storage, реальные initialized byte writes, затем legal assume_init для [u8;3];
для MU-array companion — реальные записи в stack storage без превращения hole в typed u8 value.
P-u8 — literal/const borrow; P-MU hole — валидный const MU-array с None byte, можно явный const item + static-lifetime borrow,
чтобы проверить отличие от C1-T inline MU constructors. **Не использовать named static**, чтобы получить старый Static path.
Const/lifetime ещё не доказывают GlobalAlloc::Memory: actual origin/mask должен быть в CI binding.
Сохранить совпадение значений legal S/P, не добавлять assume initializedness или новые side effects только ради golden PASS.
Если optimizer убрал S/P/raw_eq или изменил operand order, записать LOWERING_MISMATCH и источник, не переименовать это в coverage.

**Граница == hole:** MU arrays не имеют PartialEq. Подделывать &[u8;N]/[u8;N] над hole или вызывать assume_init на hole
ради попадания в SpecArrayEq запрещено: это более ранний validity UB. Custom PartialEq с raw_eq внутри не является
std SpecArrayEq и не закрывает этот маршрут. Если нет legal MIR способа такого hole input, строка матрицы —
NOT_APPLICABLE/validity boundary с причиной; honest hole qualification выполняется direct raw_eq на MU refs.

## 2. Почему существующие C1-T legal проходят — exact запрос, не гипотеза в golden

Подготовить в существующем Quick targeted --emit=mir/property inspection для **всех 6 unchanged C1-T** и новых mixed inputs.
Не предполагать, что inline &[MU::new(...)] действительно promoted: проверить Stack/Aggregate/GlobalAlloc::Memory/Static.
По pinned source RawEq visitor создаёт CheckAs<[u8;size]> для каждого &T; MU exemption в общем dispatcher не объясняется
одним исходным T=[MU;3], поскольку effective CheckAs pointee — [u8;3]. Это source факт, не runtime диагноз.

Для каждого legal/hole input запросить:

- actual source/tool/config/check flags и root; original/consumed MIR, retained raw_eq/== specialization/факт simplification;
- BOTH operand place/carrier/referent origins, offsets/extent, actual Some/None mask до backend zero-fill и symbol binding;
- InitialTargets, points-to successors/relevance и наличие/отсутствие delayed phase с точной причиной; empty set != init proof;
- CheckAs/get и reset/SetStorage/SetRef/copy/другой setter, source instruction и положение до чтения;
- named checks emitted/reached/status, hole failure **site/type/operand**; отделить raw_eq read от constructor/transmute/ref/validity UB.

Возможные выводы отдельно: not promoted; no retained raw_eq; checks absent/not reached; actual initializing event;
не тот operand/address; другой ранний failure; unknown/incomplete. Не заключать «есть seed» по SUCCESS или «нужный hole» по FAILURE.
Без полного relevant artifact отсутствие record не равно отсутствию операции. Если имеющегося Quick/MIR недостаточно,
дать конкретный запрос координатору и UNKNOWN; не создавать инфраструктурный проект или читать raw/full logs.

## Goldens, review и результат

Goldens corrected-model одинаковы baseline/M1: mixed legal SUCCESS, valid hole intended-read FAILURE. Новые baseline
legal **должны быть оценены как возможный reproducer**, но actual FAIL не обещать до запуска. Не менять SUCCESS на
текущий false FAILURE; initial goldens без выдуманных property IDs, observed детали добавляются только после CI.
Negative substring/общий FAILED недостаточен для acceptance; extra failures и успех other operand — отдельные bindings.

Статика diff --check, source -D warnings audit и разрешённая rustfmt-обёртка (полный путь как в C1-T).
Bounded Luna High review input validity/targeted-property masking/test contracts, без production review/вложенной делегации.
Один локальный test-only commit над 28e684cbae, author/committer Tiramisu-Cake <igkharin@gmail.com>, без [skip ci];
diff только восемь новых .rs/.expected. Kani не пушить. Old C1-T тела/goldens сохраняются для механистического сравнения.

В g0 `research/challenge-8/kani-k1/kani3300/c1t2/`: `CI-OBSERVATIONS.md`, `NOTES.md` (≤35 строк), `TEST-MANIFEST.json`,
`BINDING-QUESTIONS.md`, `CI-REQUEST.md`, `REVIEW.md`, `RESULT-KANI3300-C1T2.md` (≤20 строк).
Manifest разделяет semantic expected, reported aggregate и новый NOT_RUN; фиксирует exact source/test hashes и == hole boundary.
CI request: unchanged C1-T + mixed + original D0, baseline и exact M1+те же tests; наблюдения/repair — следующая сессия.
Research commit [skip ci], тот же author/committer, stage только kani3300/c1t2/, push g0 без force; concurrent changes →
handoff координатору без reset/stash/force/чужих m1 files. Подготовить exact commit для read-only импорта M1 owner.
Локальные cargo/rustc/Kani/CBMC/Miri, builds/Actions/Cloud dispatch/workflow/runner edits, raw archives/full logs/credentials,
PR/issue/комментарии и сторонние PR links запрещены. После подготовки STOP; не исправлять M1/model самостоятельно.
Последняя строка: `READY <sha локального test-only Kani-коммита>`.
