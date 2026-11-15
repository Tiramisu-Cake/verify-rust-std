# C controls: дизайн, всё NOT_RUN

Источник/пины: [INVENTORY](INVENTORY.md). Никаких source patches, запусков или новых
компиляторных правил эта стадия не создаёт. Имена ниже **предлагаемые**, их нет в harness list.
Исполнение, включая готовую upstream aliasing ветку, требует отдельного задания/GO и exact backend pin.

## Общий oracle

Нужно различать property frame / pointer / alias / ensures / unwinding и setup error.
Будущий receipt должен связать exact source/tool/backend/flags, PFC target и generated modifies
wrapper, реальное callback тело, retained writes, reachability каждого control site, исходный
verdict и named failed property. Имена/номера generated properties сейчас неизвестны.
Compile error, timeout, недостижимый callback, неверный stub и обычный postcondition failure
не засчитываются как обнаружение C violation. Никаких blanket expect-fail.

Два volatile writes сохраняют write-then-restore в модели; исходные значения восстанавливаются
до postcondition, затем делается volatile read через ещё живой input `&T`. Одна проверка final
equality/permutation ожидаемо этого не различает. Нельзя убирать writes оптимизацией, прятать
их за assume(false), stub_verified, canonical guard rejection либо mutation после target return.

U code anchors: `kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs:19–50,129–233`
формирует CBMC assigns и диапазон fat-pointer slice как object_upto(data,len*elem_size);
`kani-driver/src/call_goto_instrument.rs:185–201` передаёт DFCC/enforce-contract для PFC.
Это обоснование ожидаемого write-set oracle, не экспериментальная квалификация N1.

## N1 — merge source вне dst frame: `c_merge_source_write_restore`

1. Небольшой initialized **mutable backing** `[u64;2]` и отдельный MU dst2. Raw mutable
   pointer сохранить до создания shared source slice. Геометрия, alignment, initialization,
   len и disjoint requires действительного `bidirectional_merge` выполнены.
2. PFC направлен на **real `bidirectional_merge`**, frame ровно dst2, не на outer wrapper с
   более широким source frame. Callback — concrete closure с неизменяемым captured raw pointer;
   само состояние closure не писать, внешнего counter нет.
3. На первом comparison callback прочитать оба аргумента; по captured pointer записать
   `old ^ 1` в source slot, затем вернуть old. Volatile read через input reference после
   восстановления удерживает borrow живым. Сравнение вернуть lawful `<` restored values,
   чтобы не смешать frame failure с order-panic. Использовать source slot, который соответствует
   живому callback аргументу (на N2 оба input slots участвуют).
4. Только cover/no-op instrumentation, без замены алгоритма/comparator. Для lawful N2
   order-panic не нужен; если future pin требует explicit abort boundary, отдельно раскрыть его.

**Ожидается:** FAIL по записи за пределами enforced dst write set; восстановление не спасает.
Для полного alias monitor также возможен отдельный alias failure, но frame claim требует именно
проверенный frame property. Контроль дополняет existing overlap-requires negative, а не повторяет его.

**PASS:** сначала проверить body/wrapper binding, наличие обеих writes и достижимость callback.
При выполненных проверках — documented gap именно transient source write confinement на этом
tool/backend pin; не C PASS. Если binding/coverage неизвестны — INCONCLUSIVE, а не найденный alias gap.

**L1 companion:** те же disjoint src/dst и callback reads, без source writes; ожидается PASS,
cover callback/return, final source equality и initialized dst reads. Он проверяет исходную geometry,
а не arbitrary effectful callback domain.

## N2 — transient write внутри outer v frame: `c_callback_live_shared_in_outer_frame`

1. Isolated control-only wrapper с frame **ровно input v**, real
   `insertion_sort_shift_left` и real callback; initial N2 или N3, offset=1. Здесь source и
   writable outer storage — v; это не merge-source-outside-dst случай.
2. Для ясного первоначального comparison взять fixed reversed N2 `[2u8,1u8]` и raw pointer
   к tail из mutable backing до создания exclusive slice reborrow. Callback получает `a:&u8`
   на tail: прочитать `a,b`, volatile write `old^1` и restore через заранее полученный raw alias,
   затем volatile read **того же a**. Записи находятся в outer frame v; возвращать исходное `<`.
   Не получать `*mut` простым cast из самого `&u8` (так можно проверить другой lint/check).
3. PFC wrapper должен исполнять helper bodies, а не заменить insertion summary. Возможная
   более широкая raw-alias/reborrow ошибка фиксируется отдельно: вся негативная ветка намеренно
   нарушает permissions, поэтому legal companion обязан отличаться только незаконной записью.
4. N2 использует только caller storage, чтобы local-temp либо внешний counter frame failure
   не маскировал искомый случай. `modifies(v)` допускает и законные последующие shifts.

**Ожидается:** на текущем P/U без alias instrumentation frame сам по себе не различает эту
запись; ожидаемый диагностический исход — PASS с классификацией **ALIAS_GAP**, не C PASS.
На будущем отдельно квалифицированном aliasing pin правильный исход — FAIL temporal/alias
property при live reference. Это негативный Rust-сценарий независимо от stock PASS.

**Неожиданный PASS** там, где ожидается alias FAIL: при подтверждённых body/writes/reachability
документировать alias gap exact pin; не разрешать Rust-поведение. Неожиданный stock FAIL:
установить конкретную property; callback guard/frame/setup failure не доказывает temporal check.

**L2 companion:** та же backing/reborrow/callback geometry, только volatile reads; после return
callback алгоритм законно двигает/перезаписывает v. Ожидается PASS. Если он отвергнут, N2 пока
не различает temporal violation; сначала уточнить lowering/provenance/test setup.

## L3 — законное disjoint external state / UnsafeCell

Два небольших companion варианта, без незаконных source writes:

- Callback захватывает `&mut u8` отдельного counter и увеличивает его; input u8 только читает.
  Control wrapper frame явно перечисляет **v и pointee counter**, при stable route ещё scratch,
  если используется. Requires/fixture исключает пересечение counter со всеми active spans.
- Callback захватывает `&Cell<u8>` отдельного counter и пишет `Cell::set`; wrapper разрешает
  именно `counter.as_ptr()` как writable UnsafeCell storage. Не изменять обычные immutable
  bytes вокруг него, не расширять domain merge до non-Freeze input.

Оба варианта: real insertion/fallback/callback, ordinary no-assert-contracts режим внутренних
вызовов, PFC **нового outer wrapper**, explicit counter target вместо `modifies(is_less)`.
Ожидается PASS с cover изменения counter, нормального возврата и корректного input result.
Нельзя считать это квалификацией existing helper PFC: у него counter **вне** frame, и expected
FAIL там — ограниченность существующего contract, а не незаконность legal Rust программы.

Existing `helper_contracts::rejects_swap_comparator_writing_outside_frame_u8` — именно такой
frame-negative с legal effectful callback. Он не заменяет положительный L3 и не является
alias negative. Existing mutating Cell route harnesses — дополнительные input-UnsafeCell companions;
они не проверяют external captured state. Rejection L3 новым alias checker после исключения
frame/setup причин активирует STOP C «legal UnsafeCell rejected»; сейчас это NOT_RUN.

## L4 — local ManuallyDrop/ref lifetime и последующий reuse

На real `insert_tail` N3 descending input обеспечить вход в branch после первого сравнения,
создание `ManuallyDrop tmp`, callback `&tmp,&*sift`, дальнейший guard copy-back и следующую
итерацию insertion. Callback только volatile читает; не сохраняет references/raw aliases для
последующего доступа. Covers: tmp comparison, gap сдвинут, copy-back, normal return; проверка
результата/перестановки и suffix frame. Ожидается PASS, без unwind claim.

Дополнительный маленький lifetime companion: initialized local MU storage → MD value → scoped
shared read → конец borrow → разрешённая перезапись/reinitialization storage → новое shared read.
Адрес может совпадать, но старый reference после reuse не использовать. Ожидается PASS; padding
и uninitialized bytes не читать. Это companion instrumentation, не замена actual helper graph.

PASS L4 показывает разрешённость конкретной последовательности; он не доказывает temporal
enforcement без N2 и не устанавливает полную borrow inventory. FAIL lifetime после завершённого
borrow либо законного UnsafeCell/reuse требует диагностики модели; собственный Tree Borrows
здесь не разрабатывать. Все N1/N2/L1–L4 остаются DESIGN_ONLY / NOT_RUN.
