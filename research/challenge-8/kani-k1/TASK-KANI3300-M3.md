# KANI3300 M3 — композиция masks/transfers и интеграция (HELD до gates)

**Подготовлено координатором 2026-11-12. Сейчас НЕ активировано.** Runtime **Codex**, одна будущая стадия,
**Cloud $0**; model/integration owner 14, worker 15 возвращает findings по своим tests. Это верификация корректности, не security-работа.

## Условия старта — не подменять READY результатом CI

Начинать только после отдельного activation/handoff координатора, содержащего:

1. Exact принятую M2 source/test SHA/tree, targeted/Quick run и квалификацию normal-return/false/PFC/frame/clause boundaries.
2. Exact C1-T2 test-only commit + baseline/M1 observations: mixed operands, actual origins, retained reads и intended hole;
   почему old C1-T matched baseline, либо конкретно оставшиеся UNKNOWN и решение по blocking impact.
3. Перечень source dependencies/незакрытых blockers, immutable mask/symbol/reset bridge и рамки текущего supported domain.

Если этих pins/решений нет — STOP до clone/code/test changes, только сообщение о недостающем gate. Не выбирать вместо
них старый 5abdcf982d или latest branch head. Нельзя самостоятельно превращать документ в GO/CI dispatch.
M1 `5abdcf982da6aff65662e198af27a9c776830a89` с Quick 43222702257 — исторический accepted-input, не будущий M3 base.

## Рабочая область и интеграция

При activation записать `kani3300/m3/INPUTS.json`: source/tree/test composition/full dependencies/CI identities.
Создать отдельный clone **/root/kani-fix-3300-m3**, ветку **experiment/kani-3300-m3-composition** от exact принятой
M2-derived головы; source clones M1/M2/C1T2 не менять. Новый/dirty destination → STOP без reset/stash.
C1-T2 импортировать только test-only delta с hash validation; не переписывать его bodies/goldens и не переносить production 613
поверх принятого M2. Findings tests вернуть владельцу 15. Один владелец общих registry/relevance/model files — 14.

Прочитать M0 contract, M1 SOURCE-BINDINGS/review/actual CI, M2 qualification и C1-P CONTROL-MATRIX.
Область — композиция уже принятых механизмов, не новый memory model. Flat arrays/slices остаются поддержанными.

## Первая bounded матрица — до восьми новых selectors, existing controls переиспользовать

- Dynamic origin choice между immutable promoted и mutable stack: оба operands, legal alternatives и отдельный hole
  negative. Ни одна origin/offset/effect alternative не исчезает из join; unknown не превращается в true.
- Nonzero subrange/offset и alias/helper propagation: actual allocation/range bounds и dataflow до retained read;
  valid MU refs до intended hole read, без раннего invalid [u8] ref. Выход за bounds — отдельный validity control.
- Overwrite/reset: initialized→uninit→read FAILURE и reinitialize→legal read SUCCESS; immutable mask не reseed mutable
  destination после copy/transfer. Сохранять actual source-following false path, не требовать exact false на каждой optimistic ветви.
- Whole `[MU<T>;N]` pointer copy и flat slice view: full-extent raw copy/typed D(T) distinction, fully written/hole;
  overlap/per-element stride/count/source/destination offset. N/типы малы, domain changes/assume initializedness запрещены.

Не более восьми новых selectors первой очереди; отложенные rows перечислить, не размножать дубликаты.
Existing Some(0)/None/padding/copy-hole, compatible/conflicting descriptor unit cases, zero/nonzero/ZST, true/false Item,
PFC legal/frame/clause/abnormal controls reuse с точными bindings. Synthetic descriptor conflict не real-source repro.
Coalescing: actual requested AllocIds→returned symbol, compatible masks/extent/freeze, один seed на canonical object;
Some(0) и backend-filled None нельзя смешать. Не считать equal byte values доказательством одинакового initializedness.

## Обязательства и границы

Для каждого case: source/mask/mutability/freeze/carrier→symbol/layout→object/offset/extent→reset/seed/transition→read/property.
IDs compiler-local, public bool witness не bitmap. Registry закрыт per exported GotocCtx после всех producer passes;
seed только после reset, до первого user effect, не при ref/call/copy/overwrite. Mutable/UnsafeCell/unqualified storage не seeded.
Границы unknown/erased-only/partial/relocated watched origins, heap/foreign/realloc, by-value DST, ordinary union constant
и unpaired/intercepted calls требуют source/reached guard или остаются release blockers. Таблица exclusions не заменяет guard.
Не добавлять B3/G1/B4/T1b, новую ABI/alias premise, global true/skip или широкую cache переделку ради PASS.

Multi-harness regression сохранить: singleton/shared source/property inventory, model-local registry closure и отсутствие
межмодельного state leak. Native/CLI/source порядок не является actual codegen order. Без receipt actual order/prewarm
не заявлять matched AB/BA; записать ORDER_UNCONTROLLED и конкретный запрос координатору, без нового runner.
D0 order delta +2 SUCCESS checks сам по себе не причина .2 и не поручение K0; semantic defect/lost required check → STOP.

## Приёмка, результаты и STOP

Source repair только для воспроизведённого bounded composition defect с различающим control. Новый model/trusted premise
или незащищённый supported path → STOP/review, не замена assertions/смягчение goldens/сужение flat domain.
Статика diff --check, API/source warnings audit и разрешённая rustfmt-обёртка; bounded Luna High review semantic deltas/tests,
без вложенной делегации. Никаких локальных compiler/verifier запусков. Новые outcomes NOT_RUN до CI координатора.

g0 **kani3300/m3/**: INPUTS, `NOTES.md` (≤40 строк), `COMPOSITION-MAP.json`, `TEST-MANIFEST.json`, `REVIEW.md`,
`CI-REQUEST.md`, `RESULT-KANI3300-M3.md` (≤20 строк). Local Kani commits с exact base/deps/tree, нейтральные,
author/committer Tiramisu-Cake <igkharin@gmail.com>, без [skip ci]; Kani не пушить.
CI request — targeted composition + unchanged D0/C1/M2 and Quick; matched G1/full G2 и actual SmallSort scratch replay
остаются отдельными gates. Resource OOM/timeout не PASS, aggregate output не binding, historical runs не новый SHA.
Research [skip ci], тот же author/committer через git -c, stage только kani3300/m3/, push g0 без force;
concurrent/non-fast-forward → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow/runner edits, raw logs/archives/credentials, PR/issue/комментариев и сторонних PR links.
STOP после reviewed package, не объявлять Part 1 ready-for-review. Последняя строка: `READY <sha локального M3 Kani-кандидата>`.
