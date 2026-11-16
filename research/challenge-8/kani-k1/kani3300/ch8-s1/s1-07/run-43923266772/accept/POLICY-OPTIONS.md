# S1-07: варианты оставшихся gates — только предложение координатору

Run `43923266772`, stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`,
std `5be85699b8826e3286c0bf89efb9affefac0acb5`. Ни один вариант ниже не применён.
Текущий результат: 1/35 QUALIFIED, 34 PENDING, independent proof credit NONE.
Точные строки, ID, sites, причины и зависимости — `ACCEPT.json#/rows`,
`remaining_gate_details`, `pfc_analysis.bindings`, `unreachable_analysis.records`.

| Gate | Затронуто | Строго закрывается имеющимися stock-данными? | Правка только harness |
|---|---:|---|---|
| REQUIRED_SUCCESS_SEMANTIC_BINDING | 111 сообщений / 21 root | Нет: несколько assertions имеют один callsite и placeholder | Да, экспортируемые литералы через `kani::assert`; новый run |
| FULL_QUALIFIED_TARGET_IMPL_CONTRACT_WRAPPER_BINDING | 22 PFC roots | Частично: harness и target-definition; instance/check/wrapper/property edges отсутствуют | Не восстанавливает исходную цепочку; возможны дополнительные различающие проверки |
| UNREACHABLE: UNKNOWN_OBLIGATION_APPLICABILITY | 133 properties | Нет по текущим macro/callsite данным; отдельные sites могут закрываться точным source/domain доказательством | Частично; помеченные checks/covers помогают, но не восстанавливают origin старого property |
| UNREACHABLE: UNKNOWN_OBLIGATION_BINDING | 54 properties | Нет: safety checks внутри `active_post` не связаны с конкретным caller/ensures/canary | Частично; раздельные наблюдаемые caller checks, не исходная wrapper-цепочка |
| COMPANION_QUALIFICATION_PENDING | 8 negatives | Производный: закрыть собственные gates production companion | Сам по себе нового tool не требует; зависит от выбранного решения выше |

Совпадение file/line/harness/property ID, SAT covers и failures защищает наблюдаемые
обязательства в доверенной модели stock compiler. Оно не заменяет отсутствующую
compiler-origin связь. Для полной исходной гарантии selected-instance/expansion
binding **эквивалентного критерия только на этих stock-данных нет**. Ниже дан
минимальный наблюдаемый критерий против vacuity/ошибочной привязки, его предпосылки
и точная потеря гарантии; выбор более узкого уровня admission остаётся координатору.
Повтор того же stock run сам по себе недостающие поля не создаст.

## 1. Required success: 111 отдельных связей

**(a)** Native metadata подтверждает exact selector/crate и original source span,
но не содержит assertion IDs, expressions или expansion map. В `smoke!`,
`smoke_exact_n!`, `positive!` несколько source assertions схлопнуты в один callsite
с одинаковым placeholder. Все 111 candidate sets сохранены; номера `.assertion.N`
не означают установленный source order. Остальные 16/127 semantic bindings закрыты.

**(b)** Минимальный stock-критерий после наблюдаемой маркировки: заранее фиксированная
таблица `(group, variant, crate, harness, role, source-file/callsite, description)`;
каждой роли соответствует exact assertion ID со статусом SUCCESS в полном inventory
этого harness; отсутствующих/двойных/UNREACHABLE required assertions нет. Нужны
required covers SAT после relevant assumptions, actual call и post/frame checks,
включая N0..3 и нетривиальные cases, плюс прежние exact sole-failure negatives и
same-run companions. Это даёт защиту от подмены роли и пропущенной обязательной
проверки при доверии к stock codegen. Не даёт independent MIR/expansion provenance,
полноты domain и выбранного impl/wrapper. На текущем run все кандидаты SUCCESS —
полезное групповое наблюдение, но это ещё не bijection `role → exact ID`.
Принимать candidate-set вместо отдельных ролей — отдельное, более слабое решение.

**(c)** Да для будущего evidence: сохранить выражения, assumptions и controls, но
дать каждой обязательной проверке статический экспортируемый role label, например
`kani::assert(cond, concat!(stringify!($name), "::LEFT_CANARY"))`; для direct roots
задать отдельный литерал. Потребуется проверить, что сообщения действительно
попали в stock properties, затем зафиксировать новые exact IDs заранее для
negative oracles. Не переносить ordinal из S1-07.

Просто сделать строки `assert!(cond, "...")` уникальными недостаточно: они уже
различаются в source, но `codegen_panic` при невозможности извлечь const message
пишет placeholder (`kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs:233-243`).
`kani::assert` использует AssertHook (`library/kani_core/src/lib.rs:177-192`);
`extract_msg_or_err` требует извлекаемый string literal и иначе останавливает
компиляцию (`kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:65-88`).
Предложение статически обосновано; compiler/verifier здесь не запускались.

## 2. PFC: 22 selected-impl → checked_with → modifies-wrapper → property chains

**(a)** Доступны 322 native files, exact native harness refs для 35 roots. Для всех
22 PFC закрыты selector/crate/attributes/exported wrapper-symbol agreement и
уникальное membership в `contracted_functions` (function/file/harness list).
Manual producer действительно разрешает target к `def.def_id()` перед проекцией
(`kani-compiler/src/kani_middle/metadata.rs:81-95`), поэтому это больше, чем
повтор target string. Например, activation-default и activation-override связаны
с definition `<T as ...StableSmallSortTypeImpl>::small_sort` в smallsort.rs.
Но export оставляет definition name/file, а не выбранный monomorphized instance.
`kani_metadata/src/lib.rs:124-131` перечисляет поля ContractedFunction;
`kani_metadata/src/harness.rs:11-18` описывает AssignsContract symbol.
FIXME о name matching в metadata.rs:103-112 относится к **automatic** harnesses,
а не к нашим manual roots; на нём отказ в binding не основан.

Ни `checked_with` edge, ни выбранный modifies-wrapper instance, effective clauses,
ни property→clause mapping не сохранены. Opaque mangled symbol не декодируется
в доказательство этих связей. Native metadata не закрывает все четыре ребра.

**(b)** Минимум для предлагаемого **source-level bounded admission**: exact manual
native target-definition membership и harness attrs, pinned source macro/type/
trait/callsite, статический разбор специализации и всех effective clauses в
принятом cfg, тот же export/property inventory и binaries, exact именованные
caller post/frame checks, covers после actual call/return и этих checks, плюс
различающие negatives на activation/relation/frame и accepted same-run companions.
Все применимые прежние controls сохранять; недостающий различающий frame/control
нельзя объявить существующим по общему счётчику negatives. Проверка не должна
опираться на helper-name или совпадение terminal identifier.

Этот критерий защищает наблюдаемое выполнение actual source call и independently
checked caller relation/frame от vacuity/перепутанного harness. Он **не покрывает**
компиляторный выбор specialization instance, instrumentation/modifies-wrapper и
то, что проверялась именно конкретная generated contract clause. Принимать его
как полную исходную PFC-цепочку нельзя. Если координатору нужна именно эта цепочка,
нужен другой экспорт/tool; повтор stock её не даст.

**(c)** Только harness может добавить уникальные `kani::assert`/covers и точечные
mutation controls, в том числе caller frame/canaries. Можно отдельно проверить
прямой actual call обычным `#[kani::proof]` root для узкого caller statement.
Это новое evidence иной области, не восстановление исходной PFC-цепочки и не её
автоматическая замена. Самой правкой harness получить скрытые compiler edges нельзя.

## 3. UNREACHABLE applicability: 133 dependency properties

**(a)** Exact sites: `fmt/mod.rs:820` — 28; `num/uint_macros.rs:3222` — 25,
`:3224` — 25, `:3916` — 12; `ptr/const_ptr.rs:1479` — 25; `ub_checks.rs:148` — 18
(пути относительно `library/core/src/`). Native harness span не устанавливает,
из какой macro branch/caller возник каждый generated check. Current inventory
не содержит branch predicates или expansion provenance. Имена dependency/helper
не являются исключением. Возможен дальнейший точный source/domain разбор отдельного
ID; общей записи «все helper checks допустимы» данные не обосновывают.

**(b)** Минимум для каждого exact `(group,row,harness,property ID,class,description,
file,line,status)` — статическое доказательство, что конкретный check принадлежит
защитной/невыбранной ветке при данном N/type/cfg, а не required post/frame/relation
или обязательному участку; плюс role-labelled mandatory assertions SUCCESS,
post-call/useful/nontrivial SAT covers и неизменённые named negatives/companions.
При единственном source-origin такой разбор может дать ту же защиту в принятой
модели compiler. Для неоднозначного macro callsite один file/line и SAT этого не
доказывают; остаток остаётся UNKNOWN. Более слабый blanket dependency exemption
не является эквивалентным вариантом и не предлагается.

**(c)** Правки harness могут убрать форматирование из диагностик через `kani::assert`,
дать отдельные literals и covers обязательным участкам, сократить неоднозначность
конкретных callsites без изменения domain/алгоритма. Это может устранить часть
`fmt`-шума; не обещает закрыть uint/ptr/UB expansion origins. Нельзя ради PASS
удалять checks или сужать assumptions. Новый run нужен только для принятого
изменения исходников; закрытые офлайн cases нового proof не требуют.

## 4. UNREACHABLE post-predicate origin: 54 properties

**(a)** Sites `sorting_model.rs:97` — 12, `:100` — 5, `:106` — 5, `:111` — 10,
`:112` — 10, `:113` — 5, `:118` — 7. Это generated bounds/overflow checks внутри
`active_post`, а не автоматически сама Boolean relation assertion. Один instance
может обслуживать target ensures, caller post, canary и model control; native
metadata не показывает, какой вызов породил property. В частности N0 не исключает
count-loop для canary длины 1. Нельзя списать все 54 как N0/dead helper.

**(b)** Минимум: заранее перечисленные отдельные target/caller/frame roles, exact
SUCCESS IDs их наблюдаемых assertions, SAT covers сразу после этих checks и
required нетривиальных cases, негативы на нарушения соответствующей relation/frame
и accepted companion. Для каждого UNREACHABLE check дополнительно нужен однозначный
source/call-path и доказательство, что bounds/overflow branch не обязательна в
данном domain. Успешный caller post с cover доказывает его наблюдаемую достижимость,
но не происхождение всех checks внутри contract wrapper. Если происхождение
не различается на stock sites/IDs, полного эквивалента исходному gate нет;
принимать только caller-level statement — отдельный уровень admission.

**(c)** Разделить caller diagnostics на уникальные assert labels и пометить covers
после relation и каждой frame/canary проверки; при необходимости использовать
отдельные явно названные harness-local функции для независимой caller проверки,
сохранив исходную модель и все checks. Это помогает наблюдаемым caller obligations,
но не экспортирует generated ensures origin. Изменять std/target/model или удалять
защитные checks в этом задании не разрешено и не выполнялось.

## 5. Companion qualification: восемь отрицательных строк

**(a)** Уже закрыты exact predeclared sole failure, отсутствие посторонних failures,
успешный production companion того же run и identity snapshots обеих сторон.
Остался только транзитивный admission companion: его точные local gates перечислены
в `rows[].remaining_gate_details.COMPANION_QUALIFICATION_PENDING`. Требование
сохраняется и для двух activation return covers после ожидаемого failure.

**(b)** Минимум и эквивалентный критерий здесь совпадают с текущим: квалифицировать
именно named companion с теми же source/tool/config/domain pins и без его local
gates. Не заменять source SUCCESS, другим run или aggregate group exit. Если
координатор выберет узкий stock admission из пунктов 1–4, companion должен пройти
тот же согласованный уровень. Сам oracle не доказывает отсутствие vacuity companion.

**(c)** Самостоятельной правки negative harness для этого gate не нужно; необходимы
решения/дополнительные проверки соответствующего production companion. После
закрытия его gates зависимость пересчитывается офлайн, без нового tool/proof run.

## Что уже закрыто и не требует пересмотра политики

14/14 same-invocation before/after fixed binary snapshots MATCH; 9986/9986 stock/rich
properties; 18 exact location-only tuples / 2 ID; 113/113 required SAT covers с
проверенным source order; 16/127 success bindings; 226 допустимых UNREACHABLE checks;
2 negative-only return covers; 76 exact successful unsupported guards; все 8 sole
failure oracles; source/tool/variant/cfg/unwind/checks. Политика не превращает
SUCCESS checks класса `unreachable` в статус UNREACHABLE и не удаляет их.
Четыре N0..3 unions остаются PENDING из-за member gates. `ordinary-bridge` QUALIFIED
только как bounded source-reported bridge observation; это не acceptance PFC или
smallsort и не B1/B2/general theorem. Per-root process exit/wall/RSS не экспортированы;
они не были proof gates и не присвоены из group measurements.

Все ссылки на producer относятся к pinned stock commit выше, проверенному локальными
Git object reads; hashes producer-файлов — `ACCEPT.json#/producer_source`.
Ни предложения, ни labels, ни новые негативы/source/tool/CI изменения здесь не применены.
