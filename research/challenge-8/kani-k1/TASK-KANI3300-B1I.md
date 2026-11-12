# KANI3300 B1I — перенос B1 в Part 1 с сохранением протокола A3

**Выдано координатором 2026-11-12, план принят.** Runtime **Codex**, одна стадия, **Cloud $0**.
Выбор владельцем direct-MU экспорта с guard либо сохранения flat storage ещё не сделан; эта стадия от выбора не зависит.
Fork Actions снова доступны. Проверка исполнением — только fork CI координатора; исполнитель ничего не запускает.

Это верификация корректности, не security-работа.

## Вход и дефект

Прочитать `AUDIT-REPORT-KANI3300-PART1-R2-RU.md` @ research `124a45e373`: блокер §2, ответы 8, 10–12.
Рабочий Kani-клон **`/root/kani-fix-3300-p1b1`**, ветка **`fix/kani-3300-p1-b1`**, исходный HEAD
**`a0a2386001a15fecfe2facc2f6cd87f3dee13b60`**. Проверить branch/HEAD/dirty diff до правок; при несовпадении STOP,
не reset/stash. Standalone B1 доступен через remote **`b1src`** (`/root/kani-fix-3300-b1`), tip
**`d5f072f2bcf61a04d84bb0e8b54115f3011252fc`**, base `bf9c58e662fd65c64381ef2ac97a6397ffc0693a` — только источник diff.
Читать точные commits; при отсутствии объекта разрешён fetch только из локального `b1src`, без переключения его ветки.

В Part 1 `visit_terminator(Call)` обходит операнды дважды при Err resolver и выходит без общего flush:
теряются Unsupported, накопленные operand checks и entry LoadArgument в блоке без statements. Delayed guard условен.
Дополнительно seed resolver и points-to могут упасть на unwrap до того, как локальная диагностика будет вставлена.
Отдельный B1 уже меняет политику MIR-backed shim; механический перенос расходится с Item-only протоколом A3.

## Что сделать

1. Перенести **эквивалентный по эффекту минимальный фикс**, сравнив B1 diff с текущей A3 реализацией:
   один `super_terminator`, сохранение каждой накопленной операции и target ровно один раз, включая Err/неподдержанный
   instance. Определить и сохранить порядок: entry loads → проверки чтений операндов → Unsupported вызова.
   Исключить повторный обход/дублирование checks; поддержанные вызовы не должны терять instrumentation.
2. Согласовать классификацию вызовов между local visitor, delayed visitor и points-to. Один владелец диагностики
   FnPtr/Virtual/unresolved call; bodyless Shim/LlvmIntrinsic/иные неподдержанные формы — явный fail-closed результат.
   Не заменять потерянную local проверку надеждой на непустые seeds. Обновление legacy diagnostic допустимо только
   с объяснением, почему сохранилось покрытие и нет лишних/пропавших свойств.
3. **Не расширять A3 transfer domain.** Сохранить общий caller/callee predicate ordinary nonforeign bodyful
   `InstanceKind::Item`; любой shim с shadow argument **или** shadow return отвергать до передачи. Не переносить
   standalone bodyful-Shim policy в обход этого guard. Для non-shadow bodyful shim согласовать анализ MIR и visitor,
   не приписывая ему парный протокол. Сохранить signature/count/index/size проверки, обязательный return0,
   snapshots до Call(Move) reset, исходный false и typed D(T); не менять mem_init ABI/fallback ради переноса.
4. Закрыть именно ранние пути, мешающие этому fail-closed результату:
   `delayed_ub/initial_target_visitor.rs` — fallible resolution вместо `Instance::resolve(...).unwrap()`;
   `points_to/points_to_analysis.rs` — не делать `body().unwrap()` у bodyless/неподдержанного callee.
   Пропуск seed/анализа допустим лишь при гарантированной local Unsupported диагностике этой формы; не моделировать
   неизвестные эффекты как безопасные. Сохранить ранее найденные targets/ops и обработку поддержанных intrinsic.
5. Перенести подходящие standalone B1 fixtures и адаптировать их к Part 1. Отдельно подготовить различающие случаи:

   | Контроль | Что координатор должен установить в CI |
   |---|---|
   | Обычный bodyful Item, initialized/partial MU arg и return, nested/repeated calls | прежние A3 outcomes и false transfer сохранены |
   | FnPtr, erased/wrapped, global/escaped, Virtual; plain и seeded | local Unsupported независимо от запуска delayed pass, без ICE |
   | Нерезолвимый вызов — первый terminator пустого entry | LoadArgument не потерян, target emitted ровно один раз |
   | Вызов с уже накопленным uninit operand read | достигнута нужная read property до Unsupported, не только общая FAILURE |
   | Bodyless shim plain/seeded и resolution failure | нужный Unsupported вместо seed/points-to unwrap/abort |
   | Bodyful shim: shadow argument-only и shadow return-only отдельно | каждый guard достигается независимо; один не скрывает другой |

   Существующие A1/A2/A3 fixtures и goldens не ослаблять. Для нужной формы custom MIR заранее сверить API и panic=abort
   пина; не объявлять actual lowering установленным до CI. Ожидания писать по свойствам каждого harness, без выдуманных
   номеров. При substring goldens дополнить план одиночным запуском/JSON properties: один match не доказывает несколько
   checks. Исторический standalone PASS не переносить на интегрированное дерево; измеренный false SUCCESS base не заявлять.
   Seeded варианты создавать поддержанным copy/cast над обычными байтами, независимо от raw_eq seeds и решения о flat scope.
6. Статика: `git diff --check`, source audit imports/unused/`-D warnings`, сигнатуры по исходникам pinned toolchain.
   Форматировать изменённые `.rs` только разрешённой обёрткой
   `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --config-path rustfmt.toml`.
   Один независимый semantic review Luna High (без вложенной делегации); concrete findings устранить, delta вернуть
   тому же reviewer. Неизмеренные build/lowering/outcomes отметить NOT_RUN, а не PASS.

## Границы и STOP

- Не менять raw_eq checks/seeds/policy, flat admission, D(T)/layout или Move policy; не выбирать объём экспорта.
  W1-R0 читает `/root/kani-fix-3300-a1` — этот клон и standalone B1/B3 не менять.
- By-value DST, ordinary-union constants, hook/DFCC расширения, B3 backend, realloc/B4, G1 и fresh-transformer/T1b
  не реализовывать здесь. Найденную смежную проблему записать с точным source path/commit и следующим шагом.
- Если перенос требует расширить transfer domain/ABI, default true, пропустить проверку или изменить scope — STOP
  с частичным review-пакетом; не решать это за владельца. Known raw_eq legal failure a0a2386001 остаётся открытым.
- После review и передачи кандидата координатору STOP. Quick/full CI, разбор его результатов и repair — отдельная стадия.

## Результат

Kani: отдельные локальные production/test commits с нейтральными сообщениями, без `[skip ci]`, автор/committer
`Tiramisu-Cake <igkharin@gmail.com>` через `git -c user.name=... -c user.email=...`; Kani **не пушить**.
Указать parent/base/tip SHA и список перенесённых/адаптированных/неперенесённых B1 commits с причиной.

Research — **в g0** `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/b1i/`:
`NOTES.md` (≤40 строк: дизайн/границы/отличия от standalone), `TEST-MANIFEST.json` (fixture/harness, flags,
expected named properties/order, plain/seeded, состояние NOT_RUN), `REVIEW.md`, `RESULT-KANI3300-B1I.md` (≤20 строк:
exact source SHA, static checks, review, remaining blockers, handoff координатору для Uninit Quick).
Quick должен охватить fmt/build/clippy и все uninit suites плюс новые property controls; full gate части 1 здесь не закрывается.
Research commit `[skip ci]`, тот же автор/committer, stage только `kani3300/b1i/`, push g0 без force.
Не включать чужие изменения; при concurrent/non-fast-forward update — handoff координатору, без reset/stash/force.

Никаких локальных cargo/rustc/Kani/CBMC/сборок, Actions/Cloud dispatch, CI workflow изменений, PR/issue/комментариев,
raw logs/archives/credentials и ссылок на сторонние PR. Python/чтение Git/разрешённая rustfmt-обёртка — можно.
READY означает статически подготовленный кандидат, не CI PASS и не готовность Part 1 к публикации.
Последняя строка ответа: `READY <sha последнего локального коммита Kani>`. Стоп.
