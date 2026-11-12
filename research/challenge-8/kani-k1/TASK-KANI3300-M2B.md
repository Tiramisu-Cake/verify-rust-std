# KANI3300 M2-B/S — immutable masks в contract Assert/ensures, worker 14

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна стадия реализации/статического review,
**Cloud $0**, локальные compiler/verifier запуски запрещены; fork CI запускает координатор.
Это верификация корректности, не security-работа.

## Вход и разделение двух блокеров

Прочитать TASK-KANI3300-M2A.md, `kani3300/m2a/` @ **ea0fbb5931f08bd1a253db9d023a24f94f365a30**,
M0 MODEL-CONTRACT и M1 SOURCE-BINDINGS. Исторические results не переписывать.
По координатору выполнены singleton probes с timeout300s и watchdog CBMC RSS>6GiB (sampling допускает overshoot):

| Source | Fork run | C03 default Assert | C04 no-assert, C05/C06 undecorated | Scalar PFC P1 legal / P2 hole |
|---|---|---|---|---|
| M1+M2 **5f7f2b7364** | **43243491671** | falseFAIL `[u8;3]` SpecArrayEq, 4s/238MB | PASS | cutoff, >6.4/8.0GiB за10–12s |
| B1I-A без M1 **6134e42dd1** | **43244391200** | falseFAIL | все falseFAIL (D0 gap) | тот же resource cutoff |
| Upstream **bf9c58e662** | **43244395728** | Unsupported | Unsupported raw ptr/unions, incompatible-layout transmute | 46s/1.4GB, FAILED frame в store_argument, unreachable load_argument и Unsupported |

C03 отличие локализует оставшийся дефект в Assert/ensures route; exact operand/mask/epoch ещё связать.
PFC resource regression присутствует **до M1**; M1 не необходим для её воспроизведения, дополнительное влияние не исключено.
Attribution к A1/A2/A3/B1I пока нет. Upstream Unsupported/frame — не semantic baseline PASS и не одинаковый executable model.
Worker15 **после завершения B3-CI/handoff** получает TASK-KANI3300-M2B-RESOURCE.md; он не меняет release source.
Два трека готовятся параллельно, модели/CI-results не смешивать. M3 HELD до обоих gates.

## Рабочая область и цель

Read-only `/root/kani-fix-3300-m2` на **5f7f2b7364135a0a8b7cfd86c43b4491a8911bac**,
tree **b2bbb7366a9fbac33398fb01be7300f83a1d27bd**, production **254ae69662b3206cd4432dae0cd44c534b1b13fb**.
Создать отдельный clone **/root/kani-fix-3300-m2b-seed**, ветку **fix/kani-3300-contract-immutable-mask** от exact5f7.
Existing/dirty destination или другой pin → STOP без reset/stash. Не rebase на новую голову, B3 или diagnostic tree.

Исправить узкий missing immutable-origin/seed bridge для generated Assert/ensures, сохранив контракт M0.
Первым шагом по C03 связать body/ensures/root site и **оба** raw_eq operands: retained MIR/check → typed origin/carrier
и Some/None mask → actual emitted symbol/object/range → reset/seed → последнее изменение witness → read.
Различить immutable RHS, out referent и generated copies. SpecArrayEq/текст `[u8;3]` сам не выбирает operand.
Если curated receipt отсутствует, запросить точечный singleton MIR/property/trace через существующий quick/probe;
до получения необходимого binding — PREPARED/BLOCKER, не предположение, что каждый FAIL лечится seeding.

Проверить исходные source anchors:

- `context/immutable_allocations.rs::prepare_immutable_allocations` читает original instance bodies;
  `codegen/operand.rs::codegen_const` наблюдает constants в emitted bodies. Установить, что видят оба пути в generated clauses,
  где сохранена/потеряна typed Freeze qualification и какие allocations реально запрошены через erased carrier.
- `compiler_interface.rs::codegen_items`: closure registry после producer/contract/quantifier passes, до snapshots/export;
  insertion **и reuse** alloc_map возвращают связанный symbol. Наличие имени/литерала в source не certificate.
- `finalize_immutable_allocations` и actual reset completions: qualified source Some/None → canonical byte layout → live
  witness. Проверить last setter/retarget/copy после reset: missing initial seed и последующая порча state — разные дефекты.

Разрешены необходимые узкие изменения collection/binding/placement в существующих anonymous-origin/immutable-registry/
operand/compiler-interface sites и минимальные relevance corrections **только для установленного gap**.
Сохранять independent Freeze, Mutability::Not, exact extent/layout, source mask до zero-fill, all alternatives и conflict diagnostics.
Generated clause — место наблюдения действительного typed constant, не основание считать closure/stack/capture immutable.
Seed только в завершении каждого исходного reset epoch до user effects; никакого reseed при входе в ensures/ref/call,
положительного default, OR masks, carrier-as-referent, ослабления admission или повторного blessing mutable destination.
Не чинить already-correct D0 normal setter без отдельного reproducer; false source transfer и existing checks сохранять.
Если нужен runtime ABI/protocol/DFCC rewrite, general retarget model либо неоднозначный epoch — STOP с конкретным proposal.
Worker15 resource/frame findings передаются сюда через координатора; не cherry-pick его диагностические ablations.

## Контроли, type audit и CI-request

Исходные M2 four inputs/goldens и research C03/C04/C05/C06 сохранять побайтно; запускать их targeted, не полный Quick сейчас.
До4 новых небольших selectors в **tests/expected/uninit/contract-immutable-masks/**, reuse existing controls прежде дублирования:
unchanged C03 reproducer/legal ensures; reversed operand legal, если нужен для gap; valid direct-flat MU promoted-hole
negative в ensures для каждого направления. Hole только через lawful MU/raw_eq, без раннего invalid `[u8]` reference.
Проверить intended operand read и lawful companion, не только общую FAILURE. Литерал None не должен получить true seed.
Retained array3/ensures, actual Assert mode, reset→seed→first effect обязательны; no-assert-contracts только diagnostic companion.
PFC controls остаются ресурсно не квалифицированы: не заменять их ordinary Assert и не активировать heavy suite.

**Обязательный явный TYPE-AUDIT.md:** для каждого изменённого Rust expression/API записать точные operand/result types
по pin, integer width/sign, usize/u64/u128 и references/deref; для comparison/арифметики — обе стороны,
для conversion — bounds/truncation/target justification. Не полагаться на rustfmt/Luna: B3R2 пропустил u64/usize E0308/E0277.
Отдельно проверить signatures/imports/unused/-D warnings. Статика не compilation PASS; первый CI обязан выполнить build/clippy.
Разрешены diff --check, source/hash/Python checks и ранее разрешённая rustfmt-обёртка из TASK-M1; local cargo/rustc/Kani/CBMC/Miri запрещены.
Один bounded Luna High semantic review exact delta + type audit + positive/false controls, без nested delegation.

CI-REQUEST: сначала build/fmt/clippy, затем unchanged C03–C06 и small legal/None controls, D0/mixed/immutable-masks/unit5,
один root/solver за раз; source/tool/argv/property/mask/epoch bindings, все extra failures и exact exits.
Mixed reuse: exact16 test files из принятой композиции83ceadf048 (fixed C1-T2-A7f9eec41e8), hashes и отдельный
composition request; не cherry-pick только repair поверх отсутствующих fixtures и не переносить baseline production6134.
Воспользоваться existing timeout300s/RSS watchdog с actual limits/sampling/units; cutoff — INCOMPLETE.
Полный Quick отложить до решения M2-B/R по исходным PFC heavy selectors, затем unchanged full gates отдельно.
Acceptance: C03 PASS с retained intended checks и qualified seed, C04–C06 не регрессируют, None/false/overwrite не скрыты,
нет extra failure/Unsupported/frame loss. READY до CI означает prepared candidate, не принятую модель/закрытие M2.

## Результат и STOP

g0 **kani3300/m2bs/**: `INPUTS.json`, `SOURCE-BINDINGS.md`, `TYPE-AUDIT.md`, `TEST-MANIFEST.json`, `REVIEW.md`,
`CI-REQUEST.md`, `RESULT-KANI3300-M2BS.md` (≤25 строк; established/UNKNOWN и оба gates раздельно).
Local Kani commit(s) без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, **Kani не пушить**.
Research [skip ci], тот же author/committer, stage только m2bs/, push g0 без force; concurrency → handoff без reset/stash.
Без CI/Actions/Cloud dispatch/workflow/runner edits, raw archives/full logs/credentials, PR/issue/комментариев/сторонних PR links.
После reviewed candidate STOP до CI координатора. Последняя строка: `READY <sha локального M2-B/S Kani-кандидата>`.
