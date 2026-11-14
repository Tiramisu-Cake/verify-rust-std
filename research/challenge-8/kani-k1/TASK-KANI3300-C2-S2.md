# KANI3300 C2-S2 — совместимые immutable descriptors (R4 F5)

2026-11-14. Worker14, одна стадия. Это верификация корректности, не security-работа.
Подготовлено для выдачи координатором; этим файлом работа не запускается. После выдачи — isolated clone
`/root/kani-fix-3300-c2-s2`, ветка `fix/kani-3300-c2-s2`. Existing destination/dirty input → STOP без reset/stash.
Локальные cargo/rustc/Kani/CBMC/Miri/builds запрещены. Cloud $0; fork CI, публикация source и dispatch — координатор.
Существующие исходные клоны/PR ветки не менять. S3–S6 и SEL1 этой стадией не начинать.

## Вход и принятый S1

- Exact base `69b13711e60a87458200833445d47488ab466344`, tree `1df668c6896eaed2b08385d307b8ddf178613c6f`,
  read-only `/root/kani-fix-3300-c2-s1`; sole parent `ba0e5cfedf31e20d18e95b50ba5dbd6946277d2c`.
- Research `90ac89e855`, `kani3300/c2-s1/{DRIFT.md,DRIFT-CHECKS.json,RESULT.md,UPSTREAM-CONFLICTS.md}`;
  `PLAN-KANI3300-C2.md` S2, аудит R4 @`f8c3266934` F5/ответ7.
- Coordinator Quick `43600410208` относится к ba0e5cfedf + CI-only overlay `ddd242820b`: build/clippy PASS,
  kani24/0, expected204/0 (2 ignored), ui17/0, script2/0, oracles/mode PASS; composition FAIL.
  69b13711e — только rustfmt repair. S1 принят владельцем; отдельный новый Quick на69 здесь не предполагается.
- Известный composition drift передан в S5, не является блокером S2: у предоставленного isolated
  ordinary_ensures_legal сохранены все227 старых checks, добавлены2 SUCCESS overflow assertions из upstream #5093;
  остальные различия — paths/locations. Это не результат всей mixed matrix и не исправление T1b.

## Цель F5 и узкая правка

`alloc_map` может объединить несколько AllocId одного неизменяемого содержимого в один emitted symbol.
Квалификация whole-object frozen origin хранится по ключу; один alias может быть qualifying, другой — нет.
Сейчас `Descriptor` equality включает `frozen`: `register` считает эту разницу конфликтом, а finalize делает fatal.
Устранить **только** этот ложный конфликт, без нового admission domain, расширения subrange/relocation support или смены seed protocol.

Write scope: `kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs` и его unit tests;
новые `tests/expected/uninit/immutable-descriptor-coalescing/**`. Иной production path допустим только с отдельной
локализованной необходимостью/review; runtime, visitor/points-to/DFCC, anonymous-origin qualification и JSON tooling не менять.

Требования к объединению:
1. Разделить physical descriptor compatibility и origin qualification. Для одного symbol сравнивать exact allocation
   (Option bytes, extent/align, mutability, provenance/relocations), mask и layout; различаться может только frozen evidence.
2. Для совместимого exact объекта объединить frozen как OR доказанных qualification facts; порядок false→true и true→false
   даёт один и тот же результат. Квалифицированный alias не должен теряться, когда первым пришёл неквалифицированный.
3. Сам qualifying fact по-прежнему требует существующего whole-object supported/Freeze origin либо exact named-static source.
   `admitted()` сохраняет immutable/no-relocations predicates. Наличие любого alias само по себе не даёт право seed.
4. OR относится **только** к qualification, не к byte masks/bytes/extent/layout. Some(0) не None. Настоящие conflicts
   с несовместимым содержимым/layout нельзя превращать в совместимые либо подменять последним descriptor.
   Существующие conflict guards не ослаблять; unrelated unqualified-conflict policy не переделывать этой стадией.
5. Existing static_source, model-local registry/seal, canonical symbol binding, target checks и reset-completion seeding
   сохраняются. Один symbol получает одну согласованную mask, без reseed на call/copy/overwrite и без mutable blessing.

Не заменять fatal на «всегда пропустить конфликт/seed» и не выбирать новый false-positive fallback вместо bounded исправления.
Сохранить diagnostics на настоящий конфликт и ошибочные rebinding/materialization/target invariants.

## Контроли и различимость

- Minimal R4 repro без изменения смысла: `static T: [&u8;1]=[&5];` плюс direct `&5` и nested `T[0]`, legal read/equality.
  Ожидание нового кода — SUCCESS без conflicting-descriptors fatal/Unsupported. Добавить reversed discovery/use companion.
- При необходимости сделать чтения наблюдаемыми штатным direct/volatile helper, не добавляя новые casts/предпосылки;
  до proof credit установить, что реальный emitted symbol действительно имеет оба разных по qualification ключа.
  Если lowering не даёт coalescing, case NONDISCRIMINATING; это не основание расширять модель/ослаблять ожидание.
- Unit matrix непосредственно проверяет register: same-object false→true, true→false, repeated identical registration,
  оба unqualified, сохранение mask с Some(0)/None, true conflict и отсутствие overwrite после Err.
  Проверить actual representation mismatch (например bytes/mask/layout/mutability/align), а не только разницу frozen.
- Переиспользовать existing immutable-masks, mixed-promoted-allocations, contract-immutable-masks и named-static legal/hole
  controls. Mutable/unqualified/relocated origins не получают нового безусловного seed; holes остаются intended failures.
  Synthetic descriptor cases не выдавать за real-source alias/provenance proof.
- Новые expected-файлы portable, один harness на файл: useful own assertions SUCCESS, intended failure count/description,
  итоговый verdict; без host triple/nightly/std-line/full-inventory goldens. Existing expected не менять ради PASS.

F5 в аудите был source finding, не исполненный repro. CI-request должен включать различающий targeted baseline на69
с теми же новыми controls и кандидат, либо явно записать отсутствие такого baseline как UNKNOWN; старый код не получает
автоматически observed fatal. Для baseline достаточно targeted repro/unit controls, повторный полный Quick не нужен.

## Статика и CI-приёмка S2

До CI: INPUTS/candidate tree, explicit Rust operand/borrow/type audit, duplicate-symbol/ordering invariants,
`git diff --check`, bounded source review. Никаких локальных Rust tool/verifier запусков.
Координатор запускает fmt/build/clippy, `cargo test -p kani-compiler -- immutable_allocations`, новые targeted expected
и existing immutable/mixed/static/ensures controls, затем прочие suites принятого Quick с исходными per-fixture flags.
Счётчики24/204/17/2 — historical S1, не предсказание новых totals. Тяжёлые PFC сохраняют собственные object-bits12.

**Приёмка S2:** новые unit/targeted expected и остальные обязательные fmt/build/clippy/kani/expected/ui/script,
contract-oracles/mode suites проходят; нет genuine descriptor mismerge, нового payload/frame/Unsupported failure или потери checks.
**Composition JSON до S5 остаётся известным FAIL и не блокирует CI-приёмку S2.** Не менять roots.json/checker/normalization,
не bless inventory и не удалять suite. В CI-report отдельно оставить его исходный failure/exit и accepted S5-deferred status;
координатор может дать диагностическому step продолжить сбор результатов, но общий красный Quick не переименовывать в all-PASS.
Известное исключение касается только локализованного S1 inventory drift. Новый lost check/status change/payload failure
или drift вне этого объяснения → STOP с точным root/property/source map, не blanket waiver всех composition ошибок.
Если новые данные whole matrix отсутствуют — NOT_RUN/UNKNOWN для них, не утверждение227/227 для всех roots.

## Handoff / STOP

Research `kani3300/c2-s2/`: INPUTS, COMPATIBILITY-MAP, CONTROL-MANIFEST, REVIEW, CI-REQUEST, RESULT.
Отдельно обозначить source/unit-only/real-source coalescing qualification, baseline/candidate результаты и JSON S5 debt.
Нейтральный local source commit(s), author/committer Tiramisu-Cake <igkharin@gmail.com> через `git -c`, без push.
Не менять pins/upstream base/B1/SEL1 ветку, не начинать F6/F7 и не объявлять полный C2 gate пройденным.
После отдельной выдачи завершить `READY <local S2 source sha>`; CI review и переход к S3 остаются за координатором.
