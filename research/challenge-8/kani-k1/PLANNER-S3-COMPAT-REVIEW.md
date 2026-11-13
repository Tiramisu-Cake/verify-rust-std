# S3 / contract compatibility — planner review

2026-11-13. Это верификация корректности, не security-работа. Только source/curated findings review;
код/CI/сборки не менялись, raw artifacts не читались, TASK не выдан.
Вход: g0 `d992c289a1a0000ea5a46b2d26e5f0385d55e327`, `kani3300/mode-findings/FINDINGS.md`;
C2 Kani `fef9e0f38c0c645027f20223a562c7008969d9a9`, S3 `58497d98d085a5144a70c358205c0e46318feeb6`.

## Что принимаю и где граница доказанного

Ordinary/Assert и SimpleCheck — **блокер Part1**, не ограничение только незаявленных Replace/Recursive.
Quick и8 JSON PASS остаются фактами своего набора, но этот набор не проверял открывшиеся пути.
Нельзя компенсировать regression новой общей оговоркой «контракты с captures не поддержаны»: verify-std использует их.

Разбор worker14 убедителен: S3 подключает реальную registration trampoline; points-to recursively вызывает run,
runtime REENTRY/depth не ограничивает статический обход обеих ветвей. Но конкретный crash stack не получен:
это сильная source diagnosis, не полный backtrace. Проверка повторной active-instance должна дать воспроизводимый cycle path.
В bool/&bool case source и saved model показывают checks и отсутствие setters; конкретный runtime witness/last write ещё UNKNOWN.
Upstream уже содержит ограничение layout/nonrecursive traversal, но достижимость именно этих дефектов изменилась с S3;
тезис «это upstream» не снимает regression с Part1. Matched S3 ablation полезен как контроль экспозиции, не как готовый fix.

У Replace **5 failures**, а не1. Два u8 payload checks нельзя объявить ложными по аналогии с bool:
unsafe ensures читает результат, который Replace перед assumption мог havoc-нуть в MU::uninit().
Этот predicate не тотален на havoc domain. Сохранить наблюдение отдельно, без переноса PASS требования ordinary на Replace.

## Выбор: ограниченный (б), а не общий SCC сейчас

1. Сохранить связь анализа с реальными nonrecursive generated bodies.
2. На реально обнаруженном interprocedural cycle — explicit Unsupported этого root, без compiler crash.
   Ни silent cutoff/пустого summary, ни graph с отброшенной рекурсивной ветвью. Recursive mode пока не квалифицировать.
   Полный SCC/fixed-point algorithm нужен для поддержки таких циклов, но не для простого устранения crash.
   Если новый Unsupported затрагивает заявленный ordinary/Assert путь, это всё ещё release blocker, не «режим не заявлен».
3. Восстановить shadow обычных scalar/ref **storage slots** и корректных aggregate/capture copies.
   Это не «поставить true всему входу»: нужны фактическое происхождение значения, data-byte mask, padding и normal edges.
   Reference slot bytes не равны referent; MU/union false и протокол A3 сохраняются.
4. Добавить layout обычных closure captures как struct: actual monomorphized upvars + rustc offsets/order + recursive masks.
   Captured refs/scalars обязательны для найденных ordinary cases. Вложенные MU/union по значению не превращать в all-true:
   сохранять существующее явное ограничение, если нет отдельной корректной transfer-mask модели.

Сначала изучить конкретные missing setters на entry/aggregate-copy/normal-return, не лечить все три события одним blanket seed.
Нельзя считать любой созданный compiler environment полностью инициализированным вместе с payload за его указателями.
Новые проверки false preservation и no-extra-failures — часть приёмки, не последующий optional regression.

## Почему не (а) или (в) в предложенном простом виде

Gate «нет MU/union transfer в сигнатуре/ветви → не заходить в trampoline» не доказывает её нерелевантность:
S3 понадобился для generated alias/normal-return setters и full-extent raw_eq в обычном Assert.
Отсутствие transfer не заменяет summary capture→upvar/return/alias effects. Такое сужение требует отдельного soundness аргумента.
Точечный normal-return setter/registration summary можно рассмотреть, только если он сохраняет эти эффекты и все исходные S3 controls;
на имеющихся данных готового меньшего корректного summary нет. Простое исключение bool/receiver/generated bodies из tracking запрещено.

Голый откат S3 возвращает его исходные ложные uninit failures и теряет нужные edges; зелёный старый набор этого не исправляет.
Откат с полноценной альтернативой — отдельный кандидат, обязанный пройти C03/ensures left/right holes/legal-pair/P1/P2,
а не способ выпустить Part1 с вновь открытым raw_eq blocker. Не смешивать этот redesign с локальными fixes.

## Порядок и STOP

Три последовательные сессии в одном draft-плане: **CC1 cycle containment → CC2 slot/copy correctness → CC3 upvar layout**.
CC1 не разблокирует Part1: bool/capture cases остаются BLOCKED до CC2+CC3. Для CC2 закрытие может быть частичным по layout,
но entry/mask evidence проверяется отдельно; PASS ordinary/SimpleCheck обязателен на финальной композиции.
Новые независимые regressions не должны зависеть от неподдержанного nonzero closure layout для проверки scalar-entry ошибки.
После fixes — original companions (bool true/false), capture-free companions, matched poisoned payloads, captures by ref/value,
все8 сильных oracle roots и mixed-root orders; затем один Quick на общей голове и последующие M3/full/platform gates.
До принятия cycle limitation нужен инвентарь representative verify-std roots: исключение RecursiveCheck не исключает
обычную рекурсию внутри Assert/SimpleCheck. Для нужного ordinary цикла потребуется отдельный sound summary/SCC,
либо явное решение владельца о границе; CC1 сам такого сужения не разрешает.
Object-bits12 сохраняется; H1 matrix/SCC/CBMC optimizer/G-SC не возобновлять.
При необходимости broader type/protocol changes или общего SCC — STOP с конкретной причиной и отдельным решением.

TASK: `TASK-KANI3300-S3-COMPAT-draft.md`, **NOT ISSUED**. Публикация текущего Part1 до исправления ordinary regressions — NO-GO.
