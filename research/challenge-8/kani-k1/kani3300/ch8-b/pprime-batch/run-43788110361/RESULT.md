# B-02 — intake завершён

235/235 COMPLETE: **11 PASS, 224 copy Unsupported**. Из 224 failed roots **211 имеют
ровно один failure, 13 имеют два**; всего **237 failed properties**, все только
`copy_nonoverlapping` / `unsupported_construct`. Casts, other Unsupported failures,
invalid-value failures, compile/resource/not-run: 0. Это source-reported diagnostic
outcome, не новое независимое B1/B2 proof credit.

Вход g0 `4c8ad23a1b50293f4f7b42464ee6c0714431b520`. [Run 43788110361](https://github.com/Tiramisu-Cake/kani/actions/runs/43788110361),
artifact `14192030971`, attempt 1. GitHub read-only artifacts API связал run с
trigger `f601ca74cab11954fbc4deaca853513d28f254a1` и digest
`d67f61fbd18549741490e0b96843fd63f21a42eb37c7ba23d33087f6542b61f5`;
локальный ZIP (905097 bytes) совпадает. Trigger — child package
`99dbb2157bdb4f0322bcb3677f4ee51991de2f28`, оба tree
`10421f334c1a90b723dde5378678b0439f862125` (проверено git objects).
Curated binding до/после сообщает clean std P′
`c5ff36ff433692140605891f646043f991db05de` / tree `1302063846873aa300f8bac64fe09e8a3ed1280f`,
Kani `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`;
binary hashes до/после равны. Это runner receipts, не независимая compiler/MIR binding.

`TABLE.json` содержит все 235 строк, SHA256 каждого curated member, единую export
identity, исходные harness metadata, checks/covers (включая **полные unreachable
списки**), failed properties, Unsupported metadata, warnings, stubs и contract.
`intake.py` независимо сверяет manifest/request с pinned package, 235 уникальных
selectors, flags/checks, COMPLETE, partition totals, verdict/failure correspondence,
group exit и отсутствие partial buckets. Raw global export удалён runner'ом;
его hash `a5fc71f72fb752ff2c4b2458694bf6d96383a77c0a0ab957cad64fb24c887e73`
сохранён как source-reported, не перепроверен по отсутствующему файлу.
Success property IDs штатный curated формат не сохраняет — доступно число success;
полного независимого property inventory / consumed-body binding здесь нет.

Одна multi-harness invocation, jobs1, 235 exact selectors, timeout600s/root;
wall **886.908862967 s**, peak process-tree RSS **3294994432 bytes** (3.295 GB),
exit **1**, stop/signal/exception отсутствуют. Compile/preparation marker:
**84.20477207 s**, не compiler-internal timing. Per-root RSS UNKNOWN.
Workflow success означает полноту diagnostic execution, а не 235 успешных proof.

## 11 PASS и отсутствие выполнения copy

Все source references ниже относятся к std P′ `c5ff36ff43`, пути относительно
`library/core/src/slice/sort/shared/`. Объяснения — статическое сопоставление source
с receipts, не новый execution trace. У первых девяти roots copy Unsupported
properties присутствуют со статусом SUCCESS; это не поддержка выполненного copy.

| ID | root (без общего префикса) | Почему не выполняется copy |
|---:|---|---|
| 3 | `fixed_inputs::safety_stable_unit_n1` | N=1: stable general возвращается при len<2 (`smallsort.rs:228`; `verify/fixed_inputs.rs:157–175`). Другие ZST длины не PASS: нулевой размер сам по себе не снимает blanket check. |
| 28 | `helper_contracts::unstable_network_safety_u8_n13_stubbed` | swap заменён verified stub; insertion offset=13=len; len<18 исключает merge (`verify/helper_contracts.rs:78–100`; `smallsort.rs:332–354,667`). |
| 29 | `helper_contracts::unstable_network_safety_u8_n9_stubbed` | То же для offset=9=len; это stubbed consumer, не proof реального swap. |
| 50 | `merge::fallback_sorted_permutation_u8_u64_n0` | Обе u8/u64 ветви пропускают insertion при len<2 (`verify/merge.rs:398–413,537–546`; `smallsort.rs:201–204`). |
| 51 | `merge::fallback_sorted_permutation_u8_u64_n1` | То же при N=1. |
| 73 | `merge::general_stable_sorted_permutation_u64_n0` | Обе stable/general ветви возвращаются при len<2 (`verify/merge.rs:357–424`; `smallsort.rs:228`). |
| 74 | `merge::general_stable_sorted_permutation_u64_n1` | То же при N=1. |
| 75 | `merge::general_stable_sorted_permutation_u8_n0` | То же при N=0. |
| 76 | `merge::general_stable_sorted_permutation_u8_n1` | То же при N=1. |
| 226 | `smoke::predicate_efficient_swap_type_matrix` | Только size/type predicates, sort/copy не вызывается (`verify/smoke.rs:15–34`). |
| 229 | `tag_permutation::tag_types_preserve_source_routes` | Только размеры, traits и thresholds (`verify/tag_permutation.rs:71–101`). |

Два failure у ID **52–56** (`merge::fallback_sorted_permutation_u8_u64_n2`…`n6`)
и **89–96** (`merge::route_safety_all_routes_n16,n2,n3,n4,n5,n6,n7,n8`).
Каждый failure в этих строках остаётся copy Unsupported своей мономорфизации;
одна primary classification не означает единственную failed property.

**Intended invalid-value roots нет:** pinned manifest содержит `false` во всех
235 oracle fields; cfg-on canaries в census не включены. Имена safety/contract или
наличие обычных bool условий не создают intentional negative oracle.

## Причина и план B §8

В Kani 0aac `kani-compiler/src/kani_middle/transform/check_values.rs:58–64`
включает ValidValuePass через validity flag. В `:491–497`
`CopyNonOverlapping` без анализа count/pointee requirements всегда создаёт
`UnsupportedCheck`; `:121–143` вставляет проверку перед intrinsic. Подключение
assert/assume-false — `transform/mod.rs:113–128`, `transform/body.rs:512–517`.
Поэтому legal u8/u64 copy получает тот же отказ: это отсутствующая поддержка
проверки, не найденное нарушение корректности SmallSort. Failure location
std `library/core/src/ptr/mod.rs:578` — вызов intrinsic, не место compiler TODO.

Например root001 имеет ровно
`ptr::copy_nonoverlapping::<u8>.unsupported_construct.1` failure. Его восемь
unreachable checks и два unreachable covers сохранены в TABLE; последующие
assertions/covers нельзя считать проверенными. Assert/assume-false объясняет
обрезание последующего пути; не каждый unreachable в census причинно связан
именно с copy (есть обычные недостижимые panic/error ветви).

Upstream [#3762](https://github.com/model-checking/kani/issues/3762) **open**,
read-only fetch 2026-11-16, updated 2026-11-06, comments0. Он прямо обсуждает
разницу между записью invalid bytes и последующим typed use. Новый duplicate issue
не нужен; `ISSUE-DRAFT.md` — непубликованный follow-up с минимальным MRE.
В pinned source уже есть related fixture
`tests/expected/valid-value-checks/custom_niche.rs:105–120`.

Для §8.2 допустим следующий малый кандидат: явный сертификат **NoConstraints**
только для доказанно all-bit-valid integer primitive pointee; отдельно
Constraints / Unknown, отказ для Unknown/Err. `Ok([])` не универсальный сертификат:
`check_values.rs:1075–1091,1121–1140,1290–1293` содержит неодинаковые scalar и
aggregate случаи. Нельзя автоматически включать arrays, unions, enums, wrappers,
Cell, MU, references, Box или новые layouts. NoConstraints снимает только
бессодержательный отказ copy; не доказывает restrictive validity или отсутствие
delayed invalid typed reads через alias.

§8.3 producer checks — отдельный шаг: только квалифицированные initialized
typed-valid SmallSort sites, с сохранением legal raw-copy companion. Безусловный
source T-read до raw copy запрещает допустимые invalid/uninitialized bytes и
padding, поэтому не является общим исправлением #3762. Bool/char/NonZero нужны
как отдельные positive/negative families; они отсутствуют как intentional
negative controls в этих 235. Нельзя убирать validity flag или глушить Unsupported
ради PASS. При upstream design overlap или необходимости новой shadow model — STOP
и design note по §8, не расширение этого intake.

## Что извлечено и что ещё доступно без CI

| Группа | success checks | failed | unreachable checks | covers satisfied / unsatisfiable / unreachable |
|---|---:|---:|---:|---:|
| 11 PASS | 2995 | 0 | 709 | 28 / 0 / 0 |
| 224 copy Unsupported | 74520 | 237 | 6032 | 518 / 78 / 354 |

Unknown/undetermined/error/other buckets и harness warnings/truncation: 0.
Counts суммируются по harness, не являются количеством уникальных obligations.
Наличие satisfied cover у failed root не закрывает его theorem; unsatisfiable
cover не означает NOT_RUN. У 147 failed roots все текущие failures относятся
к integer primitives u8/u64/i32; у 155 есть хотя бы один такой failure.
Это приоритет для малого fast path, **не прогноз 147 PASS**: после снятия blocker
могут проявиться недостигнутые проверки. Частоты всех 17 copy-мономорфизаций
сохранены в TABLE.

Сумма source-reported harness verification times **600.034011672 s**;
самый дорогой root034 `helper_contracts_wide::unstable_network_safety_u8_n32_stubbed`
— **27.585213069 s**. В TABLE доступны сортировка cost, разбор stubs/contracts,
сопоставление reachable covers и source copy sites, а также type/layout audit
для узкого кандидата. Совпадающий export SHA/flags полезен для reconciliation,
но actual producer order и per-root RSS из него не выводятся. Повторять тот же
diagnostic census без изменения причины нецелесообразно.

Следующий шаг: подготовить малый integer NoConstraints candidate и различающие
controls, статически проверить и независимо review, согласовать scope с #3762.
**B: 2 из 3 dispatch использованы (передано координатором; ledger не изменён).**
Последний B-03 сохранять до готового reviewed candidate; предложить один
отдельно разрешённый CI пакет с целевыми controls и повтором frozen235 при
достаточном полном envelope. Если controls требуют общего delayed-validity
design, закончить design handoff без B-03. В этом intake CI не разрешён.

Validation: `intake.py` успешно пересобрал TABLE из curated JSON и pinned
manifest/request; git diff whitespace check. Только read-only source/gh и
статический Python; без cargo/rustc/Kani/CBMC, push/CI/публикаций/ledger.
