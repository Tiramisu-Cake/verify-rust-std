# `insert_tail`: ресурсный ledger и граница доказательства

6 октября 2026. Это архитектурный разбор, **не результат верификации**. Основа:
точный `insert_tail` и `CopyOnDrop::drop` в
`library/core/src/slice/sort/shared/smallsort.rs:295-309,538-577`, ghost-вставки
`extract-verifast-insertion.py`, контракт `extract-verifast-drop.py`, сохранённые
`verified/smallsort.rs`, `compiler-mir.txt` и `verifast.log` Actions run
[37417173472](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37417173472)
на SHA `3eb19991b1d8c2312d9feae535b02068335f5162`. Сохранённый MIR относится
к **этому** профилю; после изменения ghost-разметки или exporter его надо
экспортировать заново. Локально компилятор, extractor и verifier не запускались.

## Состояние, которое нужен доказать

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
| `verifast-local-drop-call.patch` | Предлагает вместо общего `drop_in_place` вызвать exact same-unit annotated actual Drop при узком ADT/impl/field match. Должен передать реальный, проверенный precondition и сохранить normal/unwind CFG; **не** выдавать `CopyOnDrop.own`, `T.own` или tokens. На текущем run37423762729 gate оборвался в HRTB regression из-за nested-match bug; body/caller gates этого профиля ещё не прошли. |

Базовый `std::ptr::drop_in_place` требует opaque `<CopyOnDrop<T>>.own`, а
private default own для guard равен `false`; его post скрывает эффект на gap.
Run37417173472 останавливается именно на этом cleanup требовании, не на
проверке actual Drop. Отсутствие `ignore` flags не означает достаточную
полноту alias/UB модели: baseline translator имеет shortcut для mutable
reference creation (`vf_mir_translator.ml`, `ignore_ref_creation` path и
`reborrow_ref_mut_implicit`); его участие в итоговом safety доказательстве
надо аудировать отдельно. Approved tool listing не подтверждает семантические
изменения verifier автоматически.

## Решение для следующего pilot

После diagnostic local-Drop gate **не расширять kernel**. Отдельный hosted
pilot должен сначала использовать baseline RustBelt `borrow`,
`share_full_borrow<T>`, `init_ref_share<T>`, `borrow_end` и существующие
`FnMut::call_mut` normal/unwind contracts в минимальном generic
`ManuallyDrop<T>` fixture. Тот же fixture должен: (1) создать genuine
shared `&T` из held T, (2) передать его unrestricted `FnMut(&T,&T)->bool`,
(3) восстановить T ownership и полную storage на обоих исходах, (4) принять
`Cell`-подобный mutating callback и отвергнуть утверждение о старом значении.
Не добавлять Freeze/Copy/purity и не предполагать стабильный snapshot. Для
baseline проверить сначала **первое** сравнение с early return/panic:
`bb1` unwind=continue делает отсутствие ghost recovery на этой ветке
самостоятельным architectural gate. Только затем добавить held/guard,
повторный comparator и one-cell actual Drop.

Минимальные профили для сравнения: pinned release baseline для fixture без
tuple/actual `FnMut` HRTB, затем только tuple parser + HRTB при необходимости
реального generic call; address-taking + ManuallyDrop ref patch только если
физическая ссылка требует их; local Drop patch только в guard pilot. Избегать
`end_lft_binding` пока нормальный block/lifetime scope не показал конкретный
token deadlock. Если обычный scope захватывает слишком много последующего
кода, сначала изменить **ghost** область/точку восстановления на том же
Rust body и проверить обе exit ветки; cut включать лишь при доказанной
необходимости и отдельном trust review.

Есть два открытых, решающих вопроса. Во-первых, стандартное
`<T>.share(k,t,p)` допускает interior mutation, но не обязано предоставить
стабильный fractional `points_to`, который нынешний `copy_nonoverlapping`
contract требует для `guard.src`. Использование readonly `init_ref_readonly`
через второй comparator не является generic решением. Во-вторых, после
callback panic в MIR нет исполняемого ghost recovery: для первого compare
это direct unwind, для позднего — immediately guard Drop. Pilot должен
показать конкретное существующее правило/контракт, восстанавливающее
borrow/token/held storage на **обоих** путях. Кандидат для поздней panic —
отдельно проверенный one-cell actual Drop contract, потребляющий genuine
source/ref tokens, закрывающий source borrow и возвращающий долю tmp до
`StorageDead`/`UnwindResume`; caller должен предоставить complementary долю
и доказать merge. Это гипотеза, не перенос уже доказанного общего Drop body.
Попытка завершить readonly access до comparator тоже лишь гипотеза:
`end_ref_readonly` потребляет `ref_initialized` старого p, его
`ref_init_perm` уже израсходован, а guard.src хранит p; новый read/provenance
для actual Drop нельзя создать утверждением.

Критерий архитектурного выбора: если baseline/minimal-profile fixture не
восстанавливает full normal **и unwind** post без нового kernel hook,
недоказанного ownership bridge или запрета interior mutation, не переносить
его в actual insertion. Сохранить диагностические milestones и проверить
более простой generic swap/sort4 boundary. Если pilot проходит, следующий
отдельный run проверяет actual `&*tmp -> guard.src -> copy/Drop -> full
storage` с точно теми же версией исходника и проверенным callee summary.
