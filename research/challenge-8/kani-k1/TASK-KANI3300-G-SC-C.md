# KANI3300 G-SC-C — boundary controls и SmallSort scratch map, worker 14

**Выдано координатором 2026-11-13.** Runtime Codex, одна сессия test-only подготовки, **Cloud $0**.
Это верификация корректности, не security-работа. Production guard — owner15 по TASK-KANI3300-G-SC.md.
Fork CI запускает координатор; локальные compiler/verifier/builds запрещены. Второй аудит параллельно.

## База, импорт и разделение файлов

Прочитать TASK-KANI3300-G-SC.md, аудит @ab75098224 §5–8, `kani3300/d1a/` @15276d5723,
`kani3300/m2br7c/{CONTROL-MAP.md,TEST-MANIFEST.json}` и m2br8c counterparts.
Создать `/root/kani-fix-3300-gsc-controls`, branch `tests/kani-3300-pfc-scope-controls` от
**4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c**, tree af28e22ec446b254cfa3a28b2882eafa58d5a458.
Existing/dirty destination → STOP без reset/stash; production/чужие clones только read-only.
Все integration .rs/.expected, включая scope oracle changes, принадлежат worker14. Owner15 не меняет их параллельно.

Импортировать только path-filtered test deltas (никаких source ancestors/cherry-pick R7/R8 production):
- R7-C **fe36afc4a8de2709f00524b2d3fbd6da17919728** от4f64: private-transfer-frame/{scalar-pfc-legal,lawful-modifies}.{rs,expected}.
- R8-C **e588fa6437e7904a6d10e05a983b3c381f9b52c5** от8e01eb2aff5183c53403e1d1e73e573ce28d3095:
  private-transfer-pointer/{legal,hole}.{rs,expected}; hashes и exact prefixes брать из manifest.
Эти пакеты source-ready, не доказанные результаты. R8 ordinary legal/hole смысл/источники/goldens сохранить;
R7 PFC oracle обновляется явно под новый scope. Старый тест/его исходный смысл не удалять.
Работа только в tests/expected/uninit/ (и нужной stock test directory для mixed-order/mode fixtures);
никаких runtime/compiler/library/workflow changes. Разрешён отдельный минимальный test-only .rs для SmallSort-shaped replay.

## 1. Матрица scope controls

CONTROL-MAP: root/source hash, selected mode, uninit flags, expected effect, expected result/property и обязательный binding.
Новые boundary tests не должны опираться на массивное N, сложную сортировку или скрытое расширение MU-of-flat scope.
Source oracle пока predicted; actual property IDs и parser-matcher правятся только после CI, не выдумывать observed PASS.

| Обязательство | Controls / oracle |
|---|---|
| P1/P2 | Frozen scalar-pfc-legal и transfer-qualification/postcondition-hole .rs неизменны; оба explicit Unsupported scope, без semantic proof credit |
| ordinary/PFC одного тела | Legal ordinary/Assert SUCCESS, hole ordinary intended uninit FAILURE; PFC transfer Unsupported; при uninit off прежний contract смысл отдельно |
| PFC без transfer | SimpleCheck legal SUCCESS + настоящий contract/frame negative; новый ban не срабатывает |
| return-only/entry-only | Нет MU args, но MU return0; отдельно discard/unit-return с MU arg; PFC Unsupported, ordinary смысл сохранён |
| скрытые эффекты | Transfer только в helper, requires и ensures/old/generated closure — разные cases, PFC Unsupported |
| recursion/generic | RecursiveCheck и generic monomorphization отдельно от обычных nested calls; transfer Unsupported, no-transfer positive |
| неизвестное ребро | UNKNOWN reachability не становится NO_TRANSFER; scope Unsupported, существующий B1 diagnostic/check не теряется |
| dead/unreachable путь | Зафиксировать консервативную политику: оставшийся transformed transfer может отклоняться; удалённый путь не создавать искусственно |
| Replace/stub_verified | Отдельные no-transfer/uninit-off и shadow-transfer cases, отдельная mode квалификация; Check-guard не выдаётся за Replace proof |
| multi-harness cache | Singleton ordinary/PFC + один unit ordinary→PFC/PFC→ordinary по actual codegen order; ordinary outcome неизменен |
| ordinary перенос | R8-C offset2/Move/death/false и A3 pairing/return/repeated/nested/data-padding positives/negatives остаются исходными |
| M1/S3 | raw_eq promoted/stack mixed, immutable masks и ordinary Assert ensures controls вне PFC не становятся Unsupported |

Не называть m2a ordinary-singleton «PFC no-transfer» — это другой mode. Не считать nested calls RecursiveCheck.
Для Replace не задавать SUCCESS по одному наличию source contract: если shadow replacement семантика не установлена,
вернуть UNQUALIFIED/STOP release claim с конкретным gap. Нельзя использовать отклонённый PFC как доказанный verified stub.
PFC transfer negative теперь проверяет границу, не прежний payload/frame failure; добавить соответствующий negative
в оставленном ordinary/Assert или no-transfer PFC режиме, чтобы сохранить проверку настоящего user violation.
Невакуумность supported cases: useful read/write/contract site достижим, cover/observed binding не заменён ранним guard.
Unsupported cases: причина/selected context/effect связаны, отказ до Begin/Store/Move-reset/entry load/return0 и до тяжёлого пути.
Goldens не должны принимать любой FAILED/assignable/Unsupported; нужны отличимые reason/class и intended source binding.
ORACLE-CHANGES: old→new expectation, почему scope decision, сохранённый original .rs hash и companion supported control.
В legal-pair отдельно квалифицировать оба roots: aggregate FAILED от PFC не доказывает ordinary SUCCESS.

## 2. Проверка практической цели SmallSort — source map, затем CI-request

Читать текущие `library/core/src/slice/sort/shared/smallsort.rs` и verify/{merge,network,helper_contracts*} и exact refs.
История: RESULT-DIRECT.md (K-1 Merge scratch48 PFC, **uninit off**), RESULT-SPECDIAG.md G2
(PFC+uninit был, но Unsupported до reads; не положительное доказательство), tools/kani_k1.py и scripts/run-kani.sh.
Доступные материалы есть в `/root/verify-rust-std-kani-directbounds` и g0; не подменять их новым Kani pin молча.
Составить SCRATCH-ROOTS: exact repo/ref/root/file, ordinary/PFC/Replace/Assert, flags/profile, backing/prefix/tail,
constructors/returns/helpers/clauses, predicted guard reason или NO_TRANSFER completeness; current/distorical evidence отдельно.
Включить merge_scratch48_contract_u8_n9 и родственные DIRECT roots, ordinary route callers и SPECDIAG actual PFC cases;
для Select перечислить реально найденные roots/профили либо конкретный пробел, не универсальное «PFC не используется».
Учесть stable flat `[MaybeUninit<T>;48]`, general `MaybeUninit<[T;48]>`, raw/slice view constructors, helper calls/returns;
scratch tail остаётся uninit, initialized prefix читается законно, invalid whole-array assume_init ради replay запрещён.
Вложенный `MaybeUninit<[MaybeUninit<T>;N]>` — отдельный прежний scope gap, не расширять им этот этап.

Подготовить маленькие ordinary/PFC matched scratch-shaped legal/hole fixtures и source correspondence к реальным paths;
не переносить весь std sorter в standalone input и не называть маленькую модель proof реального SmallSort.
CI-REQUEST разделяет дешёвые model controls и replay exact real SmallSort roots на guard-кандидате:
разные trees/пины std library требуют явного composition recipe, data/model/scope predictions не PASS.
Где direct replay на Kani4f64 невозможен без новой std build инфраструктуры, вернуть точный gap/NOT_RUN, не строить новый runner.
Если guard режет нужный PFC scratch root — это явное сокращение практической цели для решения владельца,
не причина незаметно сделать exemption или заявить, что «существующий uninit-off CI сохранился → цель выполнена».

## Результат, review, STOP

Разрешены Git/hash/diff/Python static checks и pinned rustfmt; нет local cargo/rustc/Kani/CBMC/Miri/builds/CI/Cloud dispatch.
Статика типов/unsafe/атрибутов/compiletest directives обязательна; source review не compilation, учесть B3 урок.
Один bounded Luna High review матрицы/oracles/невакуумности/тестовой изоляции, без nested delegation.
В g0 **kani3300/gscc/**: INPUTS.json, CONTROL-MAP.md, ORACLE-CHANGES.md, SCRATCH-ROOTS.md,
TEST-MANIFEST.json (test-only patch/full parents/hashes), REVIEW.md, CI-REQUEST.md и RESULT-KANI3300-G-SC-C.md (≤30 строк).
Обозначить exact test composition для owner15; без ожидания его implementation закончить source-ready controls и handoff.
До CI NOT_COMPILED/NOT_RUN/UNKNOWN, proof credit0. Worker15/координатор применяет test-only patch на финальный guard source;
контроли проверяются на **этой** композиции, не на базовом4f64 с прежними ореклами. M3/full gate не закрываются source review.
Local test commit(s) без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, **не push**.
Research [skip ci], тот же author/committer, stage только gscc/, push g0 без force; concurrency → handoff без reset/stash.
Без raw archives/full logs/credentials, PR/issues/сторонних PR links; scripts/workflow/запуски — координатор.
Во всех будущих PR: *Disclosure: this change and description were prepared with the help of AI assistants.*
После reviewed test-only package STOP. Последняя строка: `READY <sha локального G-SC-C test-коммита>`.
