# `insert_tail`: ресурсный ledger и граница доказательства

Текущее состояние и разрешённый этап — [STATUS.md](STATUS.md). Эксперименты
ограниченного этапа завершены; итоговый no-go и причины описаны в
[phase report](PREPARED-PHASE-2026-10-06.md). Этот ledger не разрешает новые semantic
patches, автоматическую смену профиля или возобновление работы. Исторические
результаты ниже относятся только к указанным source/tool версиям.

6 октября 2026. Это архитектурный разбор, **не результат верификации**. Основа:
точный `insert_tail` и `CopyOnDrop::drop` в
`library/core/src/slice/sort/shared/smallsort.rs:295-309,538-577`, ghost-вставки
`extract-verifast-insertion.py`, контракт `extract-verifast-drop.py`, сохранённые
`verified/smallsort.rs`, `compiler-mir.txt` и `verifast.log` Actions run
[37417173472](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37417173472)
на SHA `3eb19991b1d8c2312d9feae535b02068335f5162`. Сохранённый MIR относится
к **этому** профилю; после изменения ghost-разметки или exporter его надо
экспортировать заново. Локально компилятор, extractor и verifier не запускались.

## Состояние, которое нужно доказать

Пусть `n>=2`, `tail=begin+(n-1)`, а `g` — индекс текущего gap. На входе нужны
`thread_token(t)`, `type_interp<T/F>`, целый корректный writable/initialized
`begin[..n]`, ровно по одному `<T>.own(t, value)` на элемент и `*is_less |-> f`
с `<F>.own(t,f)`. Указатели должны быть в одной живой области с допустимыми
границами/provenance. Вне диапазона действует frame. Safety не требует
отсортированного префикса, `Freeze`, `Copy`, чистого `FnMut` или неизменности
значений при вызове с `&T`: interior mutability разрешена. На normal и unwind
выходе целевой post возвращает **весь** initialized/owned диапазон с некоторыми
актуальными `ys`, обновлённые `F`/thread/type ресурсы и frame; все временные
ссылки, tokens и storage доли закрыты. На panic не требуется sortedness.
Равенство `ys` входному `xs`, multiset и упорядоченность относятся к отдельному
функциональному контракту с его явными premises.

Здесь `own` означает логическое право владеть `T`; `points_to`/массив
фиксируют физическую память. `ptr::read` оставляет физические байты в `tail`,
а `copy_nonoverlapping` оставляет байты в источнике. Эти дубликаты не дают
второй `<T>.own`. В позиции gap может лежать физически инициализированная
копия; её нельзя читать или уничтожать как самостоятельное владение. Для ZST
одинаковый численный адрес нескольких позиций не даёт права удвоить ресурсы;
его provenance, разделение и pointer arithmetic остаются отдельными задачами.

| Граница | Физическое хранилище и ONE logical ownership | Borrows, tokens и callback |
| --- | --- | --- |
| До первого вызова | Все `n` ячеек принадлежат диапазону. `sift=tail-1`; gap нет. | Две реальные shared ссылки на `tail` и `sift` передаются `FnMut`. Долги `cmp_k`, `borrow_end_token`, `ref_initialized` и fractional access должны быть учтены. `F` остаётся принадлежащим вызывающему после normal или panic согласно `FnMut::call_mut` post. |
| Первое сравнение возвращает `false` | `tail.read` ещё не вызван; вернуть полный диапазон с актуальными значениями. | Закрыть оба доступа, завершить borrow lifetime, вернуть обе full cells и `F` **на этой ветке**. Код recovery, стоящий перед `tail.read`, здесь не исполняется. |
| Первое сравнение паникует | Движения ещё не было; нужен тот же полный диапазон и `F` в unwind post. | MIR первого вызова имеет `unwindAction=continue`; отдельного guard/cleanup блока нет. Текущая ghost-разметка возвращает лишь comparison debt, без доказанной нормализации. |
| Сравнение `true`, перед read | После закрытия сравнительных borrow вернуть полные `sift`/`tail` cells. | Текущая true-ветка закрывает обе fractional accesses, выполняет strict cut, `end_lifetime`, два `borrow_end` и `open_full_borrow_content`. Этот префикс прошёл в run37417173472. |
| `tail.read`, `tmp`, guard | `tail` становится **логическим** gap, а `tmp: ManuallyDrop<T>` держит единственный tail-own; физическая tail cell остаётся инициализированной. Guard имеет `src=&*tmp`, `dst=tail`, `len=1` и пока не владеет вторым `T`. | `held_ref=precreate_ref(&tmp)` и `init_ref_readonly(held_ref,1/2)` дают source reference/долю и остаточную долю tmp storage. Обязательны token, provenance и последующий release/merge. |
| Каждая shift | `copy_nonoverlapping(sift,dst,1)` пишет в старый gap; после `guard.dst=sift` логический gap переходит на один элемент влево. `<T>.own` sift переносится на заполненную позицию, не дублируется. Frame остальных cells сохраняется. | Проверить bounds, непересечение для ненулевого T, точный source/dst memory contract и отсутствие unwind у valid copy. Физический source остаётся инициализированным; ownership gap уже в нём. |
| Второе и последующие сравнения | Gap и held `T` сохраняются. Результат может изменить interior state `tmp` или sift; нельзя обещать старые байты/ключи без отдельного функционального условия. | `&tmp` и `&*sift` нуждаются в genuine generic share/reborrow, совместимом с `Cell`-подобным callback. И normal, и panic должны восстановить временные borrow долги; `F` возвращается изменённым. Текущий extractor не размечает это сравнение. |
| Normal break / поздняя panic | Checked actual guard Drop должен скопировать **текущее** held значение в текущий gap и вернуть ровно `n` logical owns, полный диапазон и frame. | После использования `src` вернуть всю tmp storage: release `held_ref`, merge с дополнительной долей, завершить любые borrow второго сравнения и закрыть guard/локальные storage до выхода. На panic sorting invariant не требуется. |

Точный direct Drop contract в `extract-verifast-drop.py` уже условно проверен в
run37419989766: `[f]src[..len] |-> src_values`, полный destination slice и
**одна** последовательность `foreach(src_values, own<T>)` дают точный результат
в destination, source fraction и одну последовательность own. Его
`on_unwind_ens false` оправдан лишь на доказанном valid copy domain. Контракт
не закрывает `held_ref`, не объединяет complementary tmp fraction и не означает,
что compiler cleanup вызывает доказанный method. Общая версия `len` не может
автоматически выполнять one-cell-only recovery.

## Что именно показывает MIR

Индексы ниже из сохранённого `compiler-mir.txt` с исходными строками
`verified/smallsort.rs`. Первый `FnMut::call_mut` стоит в `bb1` (строка 125),
его unwind идёт прямо наружу (`continue`); normal false путь `bb4` приходит к
`bb19 return`, normal true идёт через read/new и guard creation в `bb3/5/6/7`.
После создания guard, `bb8` выполняет copy, `bb9` обновляет `dst` и выбирает
break или новый compare; второй `FnMut::call_mut` находится в `bb13`
(строка 165). Его unwind направлен в `bb20`. Normal loop exits `bb10`/`bb16`
идут в `bb17 Drop(_18=gap_guard)`; затем `bb18` выполняет
`StorageDead(_21)`, `StorageDead(_18=guard)`, `StorageDead(_15=tmp)` и
`StorageDead(_4)` перед `bb19 return`. Cleanup `bb20` не содержит statements:
только `Drop(_18)` с `target=bb21`, `unwindAction=terminate`; `bb21` сразу
`UnwindResume`. Таким образом при поздней panic после comparator нет
исходного Rust/ghost оператора между Drop и unwind, который можно считать
уже доказанным release tmp. На normal пути отдельного оператора между Drop и
`StorageDead(tmp)` также нет. Реальная область для нужной операции —
проверенный effect/contract actual Drop или уже существующее корректное
автоматическое правило модели; такой effect пока не доказан. Строка 169 в
MIR есть closing brace, не самостоятельный вызов destructor; source-span
records нельзя считать числом вызовов. Перед созданием guard MIR также имеет
unwind края для вызовов `read/new`; их feasibility либо resource post надо
проверить, не теряя held ownership.

## Текущий post и его долг

`COMPARISON_DEBT_POST` в `extract-verifast-insertion.py:35-46` содержит prefix
`begin[..n-2]`, `F`, половину `lifetime_token(cmp_k)`, два `borrow_end_token`,
обе `ref_initialized` fractions/close tokens и оставшиеся `foreach` куски.
Он заявлен одинаково для normal/unwind. Это честный частичный post первого
сравнения, **не** восстановленный диапазон. На false return и первом panic
текущие ghost recovery calls после `if` не исполняются. На true пути эти долги
уже погашены до `tail.read`, поэтому пост в финале устарел: нельзя выдавать
полный normal insertion proof через этот debt post, а тем более через `ens true`.
Нужны разные proof paths, сходящиеся на одном полном публичном post.

## Граница доверия experimental verifier

| Patch/profile | Что меняет и какой gate нужен |
| --- | --- |
| `verifast-tuple-own.patch` / parser | Пробная модель tuple-2 ownership для generic ссылок; overlay был отвергнут. Canonical parser route требует проверить, что tuple owns разлагаются и собираются без нового владения. Это semantic parser boundary, не библиотечная лемма. |
| `verifast-fnmut-hrtb.patch` | Регистрирует concrete `FnOnce::Output=bool` из соответствующего rustc HRTB только при exact matching substitutions. Восемь cases проверяют matcher, не тела всех callbacks. Риск — ошибочное расширение compiler equality. |
| `verifast-end-lft-binding.patch` | Опциональный strict ранний конец ghost binding; меняет translator **и kernel** (`verifast.ml`): scope boundary, возвращение reserved half token на normal/return/goto, проверку исчезновения scoped type и rebasing outer metadata. Отрицательные fixtures полезны, но не доказывают soundness kernel change; malformed CFG ingress ещё не проверен отдельно. Необходимость cut для любой корректной proof boundary не установлена. |
| `verifast-address-taken.patch` | Добавляет пропущенное продолжение обхода после `MergeFractionsStmt` в address-taking prepass. Это локальный traversal fix; новые proof resources не выдаёт. |
| `verifast-manually-drop-ref.patch` | Для exact shared borrow raw `ManuallyDrop<T>` направляет translation через существующий `create_ref` вместо bare address. Требует настоящие `precreate_ref`/`ref_init_perm`/`ref_initialized`; release обязан быть доказан. |
| `verifast-local-drop-call.patch` | Вместо общего `drop_in_place` вызывает exact same-unit annotated actual Drop при узком ADT/impl/field match. Передаёт проверенный precondition и сохраняет normal/unwind AST; не выдаёт `CopyOnDrop.own`, `T.own` или tokens. В37435525052 полный25+body+9caller gate проходит с двумя сопутствующими frontend fixes; общая soundness/приемлемость modified verifier ещё не установлена. |
| `verifast-local-decls-first.patch` | После resumption отдельно исправляет размещение пролога: uninitialized MIR local declarations перед compiler-origin projection registrations, оба перед executable MIR. Нужен из-за addressable guard в `F: FnMut()` caller; новый ownership/kernel mechanism не вводит. Проверка других associated-type-dependent locals остаётся открытой. |
| `verifast-projection-name.patch` | После declaration fix канонизирует trait name в compiler-origin projection predicate через существующий `canonicalize_item_name`, как уже делает alias-type translation (`core::` → `std::`). Resource/kernel rules не меняет. Run37434307481 выявил fatal lookup raw FnOnce name; полный hosted gate прошёл в37435525052, но это не общий soundness result. |

Обновление после resumption: nested-match bug устранён; все25 regressions и
direct actual Drop проходят в37431775757/37433028854. В37433028854 полный
raw-source normal `cleanup_one` прошёл VF/refinement0. Для selected checked
non-unwinding Drop сохранена AST unwind ветвь, но невозможный successor исключён
из structural block reconstruction; live predecessors должны сохранять cleanup.
В37434307481 declaration placement исправлен, normal caller снова прошёл,
но `cleanup_callback` остановился до body execution на неканоническом
`core::ops::FnOnce::Output_typeid`, отсутствующем в runtime спецификации;
это исторический результат. В37435525052 после канонизации projection имени
полный gate прошёл: actual body, оба callers с normal/unwind exact destination
и ONE ownership post, все7 отрицательных fixtures с intended failure. Это
закрывает локальный cleanup diagnostic, но не held-ref/full-insertion obligations.

Audit кандидата `lem_auto` recovery выявил точную baseline границу:
`verify_expr.ml:381-386` запрещает `nonghost_callers_only` для autolemmas,
а `lifetime_logic.rsspec:76-79,122-125,280-283` требует её для end_lifetime,
borrow_end и close_frac_borrow. Поэтому automatic post-recovery здесь не
доказуемо этим кандидатом. Обычная явно вызванная nonghost-only lemma может
закрывать normal путь после scope; direct Continue unwind пропускает trailing
ghost statements, а первое сравнение std ещё не имеет guard. Полный unwind
post остаётся обязательным; normal-only pilot не заменяет его.

В37437514808 baseline release26.09 проверил normal generic two-cell lifecycle:
genuine share/init → natural scope exit → явная ordinary nonghost-only lemma →
full initialized cells и текущие T.own. Оба positive VF/refinement0, actual helper
body проверен; missing token/debt и false post отвергнуты в нужных местах.
Это независимый результат без любых experimental patches. Он подтверждает
normal resource transition, но не direct first panic, held tmp или guard provenance.

Последний control37441463201 использовал отдельный `manually_drop_only` profile: pinned
translator7319d263 + только существующий ManuallyDrop-reference patch5500204a,
выход60ece6e9. Exact source diff ограничен одним translator file; parser, prelude,
kernel и прочие frontend extensions не меняются. Baseline raw ManuallyDrop
borrow пропускает create_ref по placeDoesNotNeedDrop, поэтому existing patch
нужен для actual `&*tmp`; share alone не даёт ref_initialized. Proof обязан дать
precreate/init_share и оба initialization accesses, затем вернуть full tmp storage
до перемещения T. `into_inner` не имеет pinned frontend/spec route, поэтому
контроль использует реальные ptr::read/write, без нового callee summary.
Это проверка normal tmp lifecycle; raw guard.src provenance и panic остаются
отдельными obligations. Hosted run37441463201 завершился failure: все7 cases
остановились в первом close нового recover_single до callers; positive MD
отдельно не прошёл refinement из-за unsupported RawPtr (addr_of(tmp)).
Ни новый lifecycle, ни intended negatives не доказаны. Baseline release profile
исключает новый helper, и прежний результат37437514808 остаётся в силе.
Сохранённый DRAFT-MD-RECOVERY-2026-10-06.patch не применён и не проверен:
fraction constraints и provenance сохранённого shared-derived pointer открыты.

Базовый `std::ptr::drop_in_place` требует opaque `<CopyOnDrop<T>>.own`, а
private default own для guard равен `false`; его post скрывает эффект на gap.
Run37417173472 останавливается именно на этом cleanup требовании, не на
проверке actual Drop. Отсутствие `ignore` flags не означает достаточную
полноту alias/UB модели: baseline translator имеет shortcut для mutable
reference creation (`vf_mir_translator.ml`, `ignore_ref_creation` path и
`reborrow_ref_mut_implicit`); его участие в итоговом safety доказательстве
надо аудировать отдельно. Approved tool listing не подтверждает семантические
изменения verifier автоматически.

## Следующий ограниченный этап и архитектурный stop

После явного возобновления разрешён только этап из [STATUS.md](STATUS.md):
изолировать bookkeeping recover_single, обосновать pointer provenance и пройти
refinement без ослабления full posts, затем проверить minimal ManuallyDrop gate.
Профили фиксированы: unchanged release26.09 и существующий manually_drop_only
с одним patch5500204a. Добавление tuple/HRTB, local Drop, scope cut или нового
AST-routing не является автоматическим следующим шагом. Любое изменение
семантики инструмента требует отдельного решения **до реализации**.

Ключевой gate — применимость к exact std, а не очередной зелёный fixture.
У первого сравнения нет узкого реального Rust block; let_lft из успешного
baseline fixture нельзя просто перенести. False return и first panic обязаны
вернуть full range/F/tokens; direct Continue пропускает trailing ghost recovery.
Новый proof-only BlockStmt/label route — лишь кандидат из
[BORROW-RECOVERY-DESIGN.md](BORROW-RECOVERY-DESIGN.md), не разрешённый fix.
Сначала показать существующий корректный маршрут на actual normal/false/panic
CFG либо остановиться с решением о новой доверенной семантике/другом подходе.

Для будущего held/guard pilot остаются два независимых вопроса. Genuine
`<T>.share` допускает interior mutation и не обещает стабильный fractional
`points_to` для `guard.src`. Readonly `init_ref_readonly` через произвольный comparator
не решает generic safety; Freeze/Copy/purity добавлять нельзя. После panic
нужны проверенные borrow/token/storage recovery **на обоих путях**, а не
comparison-debt post или утверждение о старых значениях.

Кандидат позднего восстановления — отдельно проверенный one-cell actual Drop
contract, потребляющий genuine source/ref tokens и возвращающий долю tmp;
caller должен предоставить complementary долю и доказать merge до
StorageDead/UnwindResume. Это гипотеза, не следствие проверенного общего Drop.
end_ref_readonly потребляет ref_initialized старого p, его ref_init_perm уже
израсходован, а guard.src хранит p: новый read permission/provenance нельзя
создать утверждением или заменой на численно равный pointer.

После ограниченного этапа нужен go/no-go review: source-exact full normal/unwind
recovery, domain без новых ограничений и явный trust/admissibility rationale.
Если маршрут требует новых semantic patches, недоказанного ownership bridge
или запрета interior mutation, сохранить milestones и запросить решение.
Более простой generic swap/sort4 — возможная альтернатива для обсуждения,
а не автоматически разрешённая новая работа.

## NEXT 2026-10-09 mutable one-cell guard diagnostic closeout

[Fresh evidence and boundaries](merge/overnight/guard-ownership/insertion-onecell/RESULT.md): actual guard551 is mutable, unlike general guard279; immutable tmp, shared-derived src fractions and logical held CURRENT owner are independent. New fragments supply entry tail/owner/geometry and remove Drop; neither build reaches the target FBC/copy/recovery proof. Second exact-SHA run stops at own syntax; MD controls stop unsupported address. All intended negatives remain INCONCLUSIVE. No new actual insertion obligation is closed.

First caller debt remains comparator541→CURRENT tail/sift/F/frame/closed shared borrows before read550. Actual next guard transition is copy557 then dst update558; immediate held→tail adapter is not that edge. Readonly init_ref protocol has no applicability across legal interior mutation at comparator566. Genuine share/reborrow/CURRENT and normal/unwind tmp storage cleanup are required; no Freeze/Copy/purity or ownership bridge permitted. Next recommended single task is supported source-linked MD/own admission with isolated positive and authority controls before mutable FBC. General immutable V4 fix is not a prerequisite. Session closed677Cloudseconds, no own unresolved Build; profileNOT_ACCEPTED.
