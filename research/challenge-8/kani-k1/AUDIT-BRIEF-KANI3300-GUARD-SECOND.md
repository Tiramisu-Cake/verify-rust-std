# Второй узкий аудит: KANI3300 PFC resource / fail-closed scope

**SUPERSEDED, 2026-11-13:** см. `AUDIT-BRIEF-KANI3300-PART1-R3.md` для нового аудитора.
Scope cut не выбран для реализации; G-SC HELD до ответа аудитора, G-SC-C заменён read-only инвентарём.
Ниже историческая версия, не действующая постановка.

13 ноября 2026. Это верификация корректности, не security-работа. Нужен независимый статический разбор двух вопросов ниже.
Владелец выбрал scope cut сейчас; worker15 реализует G-SC, worker14 готовит G-SC-C параллельно этому аудиту.
Новых runs/builds/патча CBMC C не одобрено. Просим findings с source/commit/координатами, без новых запусков.

## Область и материалы

Part 1 Kani #3300: MaybeUninit storage, flat arrays/slices, argument/return shadow transfer; цель — SmallSort scratch.
Основной source **4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c**; R7/R8 resource representations в него не принимаются.
Предыдущий аудит: `AUDIT-REPORT-KANI3300-PFC-RESOURCE-RU.md` @ab7509822453bbf0778da0265c67f51bc08b4755, особенно §5,7.
Brief v2: `AUDIT-BRIEF-KANI3300-PFC-RESOURCE.md` @cbf575f3aa6ec7b81f2359dd300d1426a4ee57bf (исторические RSS units исправлены аудитом).
D1-A: `kani3300/d1a/{RESULT-KANI3300-D1-A.md,DATA-ACCEPTANCE.md,MODEL-MAP.md,ATTRIBUTION.md,SSA-SUMMARY.json}`
@**15276d57238f4a70b2ea5fca9141ef047cce120c**; D1-P preparation @cedd1a7b5fd99c27baf9d9c07180ecaea5b92b97.
Проект реализации/контролей: `TASK-KANI3300-G-SC.md`, `TASK-KANI3300-G-SC-C.md`; это задания, ещё не проверенный guard patch.

## Что D1 установил и чего не установил

Run43314208878, attempt1: P1 legal singleton, R1+skip56cbc5c4a4 против R6-02b405c1f0592; P2 не выполнялся.
Exact CI sources: R1 **1d0f1d30bfcf8ce64d63716a31a0a9bd3e06c7a0**, R6 **86f9b171513de7a11eec7587bead1edc6877d950**.
129/129 файлов каждого переданного bundle совпали по hash/bytes; pre/post-DFCC и actual CBMC input различены.
Symex-only завершён: ~0.93/~0.89s, maxrss36556/39364KiB. Boolean conversion/SAT/normal verification NOT_RUN.
Kani rc101 (diagnostic parser incompatibility), top-level capture=failure/upload=PENDING сохранены отдельно; это не green gate.
Первичный parser прочитал только prefix; D1-A пересчитал весь bounded printed stream, не full typed SSA.
R1 all/ignored/retained5280/4213/1067, guards2039; R6 5865/4588/1277, guards1961; ASSERT96/115, ASSUME33/41.
Видимые byte-extract/update4/1 против9/1 — все sliced. Retained WITH0 против13; это не converter cache/стоимость.
Selected Layout0/1: Layout1 имеет один Boolean mask element (1B storage), не все operands однобайтные.
R1 state56B; R6 tracked24B + отдельный buffer32B — type/storage-derived, не measured converter widths.
R1 store saved_object_id: GOTO PC639 → retained phi PC664/SSA2016, field64bit; phi не исходная запись.
R6 frame check PC628/ASSERT629 перед buffer write PC631; отдельно allocated-set WITH PC1947/SSA722,
capacity65536 pointers при object_bits16 (source-derived estimate524288B); большой retained backing есть у дешёвого контраста.
R6 load содержит assume(false) abort paths; оба streams предупреждают о nondeterministic args saturating_add/sub.
Feasibility/faithfulness этих путей и новая semantic equivalence не установлены. R6 — исторический frameFAIL, не correct baseline.
**Offender не найден:** operand widths/unique DAG/cache/converter allocations/postponed work не измерены.
M3/full gate/PFC support claim не закрыты. Restricted Quick43257528539 исключал legal-pair/postcondition-hole.

## Схема guard и практический scope

При uninit-checks: selected PFC SimpleCheck/RecursiveCheck + reachable shadow transfer → explicit Unsupported.
Предпочтение conservative harness admission до transfer effects и дорогого DFCC; unknown reachability → отдельный Unsupported.
Обход выбранных transformed bodies: entry loads, caller Begin/Store/Move-reset, return-only Store0/normal Load0, clauses/helpers.
Ordinary/Original/ordinary Assert и no-transfer PFC должны квалифицироваться отдельно и не наследовать PFC отказ из cache.
Replace/stub_verified — отдельный mode, не получает proof credit от отклонённого PFC; его shadow semantics ещё квалифицируются.
P1 и P2 сохраняются как repro с новым scope oracle Unsupported; это не доказанные legal SUCCESS/hole uninit FAILURE.
SmallSort использует PFC; штатный runner uninit-off, совместный SPECDIAG G2 был Unsupported до reads.
Сохранение будущего compositional scratch proof этим cut не доказано; G-SC-C картирует точные roots/backings/hidden transfers.

## Приоритетные вопросы

1. Видна ли по D1 цепочкам конкретная причина или опровергаемая гипотеза? Какие выводы текстовый census не позволяет сделать?
2. Как трактовать saturating_add/sub warnings и R6 abort paths: это ограничивает только сравнение или указывает иной дефект?
3. Полна ли effect-based admission схема, включая generated clauses, return-only, recursion, setup и unresolved edges?
4. Как привязать selected Check/RecursiveCheck context и cache keys, сохранив ordinary/Assert в обоих actual codegen orders?
5. Где guard должен стоять, чтобы не оставить partial transfer и не пройти дорогой DFCC prefix? Достаточен ли harness admission?
6. Что отдельно требуется от Replace, auxiliary writes и supported frame/negative controls, чтобы cut не скрывал false SUCCESS?
7. Какие SmallSort scratch constructor/flat/slice/helper-return пути cut неизбежно исключит; какое обещание Part1 остаётся честным?
8. Достаточна ли G-SC-C матрица? Укажите конкретные пропущенные boundary cases и минимальный gate до выпуска.
Можно предложить собственную схему guard/границы; не требуется соглашаться с нашим дизайном. Новые эксперименты — только предложения.
