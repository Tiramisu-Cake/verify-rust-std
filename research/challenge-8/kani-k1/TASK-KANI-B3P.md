# KANI B3P — один backend fix-plus-tests commit и PR-пакет после аудита

**Выдано координатором 2026-11-12, воркер 14.** Runtime **Codex**, одна стадия, **Cloud $0**, без запусков.
Прочитать `AUDIT-REPORT-KANI-B1-B3-RU.md` @ research `d1f44b300e` целиком, особенно B3 §7–12 и §13–14;
предыдущие `kani3300/b3r/{PR-DRAFT.md,PANIC-NOTE.md,REVIEW.md}` — исторические материалы, не править.
Вердикт аудитора: узкий B3 готов к отдельному review после правки описания; полная матрица не подтверждена.

Это верификация корректности, не security-работа.

## 1. Перепаковка Kani без изменения дерева

Клон **`/root/kani-fix-zst-b3`**, исходная ветка `fix/zst-union-codegen` @
**`6db3c4dabd4a368314eb8e2b71d21d1eee721593`**, ожидаемый tree
**`c9b9bafdeca616fac235574f33dad477c25ad90b`**. Сначала проверить HEAD/branch/clean status; при расхождении STOP.

Создать **новую** ветку **`fix/zst-union-codegen-v2`** от upstream base
**`bf9c58e662fd65c64381ef2ac97a6397ffc0693a`**. Если ветка уже существует, не перезаписывать — STOP с её SHA.
Перенести конечный diff старого head в один новый commit **фикс + тесты**, например restore точных трёх файлов
из `6db3c4dab` на новой ветке от base; не reset/squash/amend старую ветку. Состав строго:

- `kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs`;
- `tests/expected/zst-union-arm/main.rs`;
- `tests/expected/zst-union-arm/expected`.

Сохранить backend hunk, семь harness, assertions, goldens и расположение general expected suite побайтно.
Не добавлять workflow, uninit-checks fixture, новые controls, comments или форматирование; PR-текст — только research.
Нейтральное сообщение, например `Fix padded union codegen for zero-sized fields`, без `[skip ci]`.
Автор и committer `Tiramisu-Cake <igkharin@gmail.com>` через `git -c user.name=... -c user.email=...`.
**Не пушить Kani**, PR/issue не открывать.

Статическая приёмка: HEAD имеет единственного родителя base; `base..HEAD` содержит ровно один commit;
`git rev-parse HEAD^{tree}` совпадает с tree выше и `6db3c4dab^{tree}`; `git diff --exit-code 6db3c4dab HEAD` пуст;
`git diff --check base..HEAD` проходит, состав diff — ровно три файла. При несовпадении STOP, не менять код ради приёмки.
Это проверка идентичности дерева, не новый Kani/CBMC результат. Сохранить полный новый SHA, parent, tree и команды/исходы.

## 2. Новый PR-DRAFT.md на английском по §12 аудита

Заголовок: **`Avoid CBMC aborts when copying padded unions with zero-sized fields`**.
Описать default-check abort 134 в CBMC 6.11.0 (`simplify_utils.cpp:345`, `bits2expr`, positive element-width invariant).
Положительный padding wrapper сохраняется; zero-width **physical payload** заменяется существующим empty-unit struct,
исходный **logical arm type** остаётся для projections/indexing. Nonzero payload и no-padding/all-ZST путь не меняются.

Точный воспроизведённый fixture — `tests/expected/uninit/zst-union-arm-no-checks/main.rs` @
`dc590936c56556ecfb20fc714da06fcb13e884db`; финальный — `tests/expected/zst-union-arm/main.rs` @ `6db3c4dab`.
Дать pinned GitHub ссылки на fixture/harness и matched runs. Если оставлять короткий код, включить фактически
исполненную ZST projection либо обозначить код **illustrative, not separately run**; не выдавать его за измеренный minimum.

Scope тестов: **padded C-layout payload in C- and Rust-layout unions**, byte-array payload, containing union at offset,
aligned ZST/all-ZST controls и **typing/in-bounds projection** для indexing. Не обещать physical ZST writes,
general ABI/noinline call-return coverage, escaping-reference alignment или чтение/сохранение padding bytes.
Default-check backend fix не означает поддержку union storage под `-Z uninit-checks`, G1 или MaybeUninit transfer.

### Testing: сохранить реальные SHA и статусы

| Исторический run | Точное дерево/checkout и результат, которые нужно раскрыть |
|---|---|
| `43115481098` | Base + fixtures `dc590936c56556ecfb20fc714da06fcb13e884db`, CI checkout `f304106019f81f09a1547a52808e3fd0c59556bb`: default selector — 3 SUCCESS, 4 CBMC abort 134 |
| `43115485052` | Fix `9dddcb1134f8a55ee3a4451df9513941ca3c8fc3`, CI checkout `9ce21fcdf5306707968357ee579a35d9d8a6973b`: тот же default fixture/golden — 7/7 SUCCESS |
| `43117729467` | Final placement @ `6db3c4dabd4a368314eb8e2b71d21d1eee721593`: Ubuntu 22.04/24.04/24.04 ARM64 regression PASS, expected suite в каждом 548 passed/13 ignored; perf/LLBC/docs/benchcomp PASS; workflow **cancelled** |
| `43117729474`, `43117729608` | Отдельные format/Clippy и cargo-deny workflows @ `6db3c4dab` PASS |

В matched base четыре abort: `array_typed_copy`, `padded_typed_copy_c`, `padded_typed_copy_rust`,
`zst_arm_at_nonzero_offset`; три проходивших контроля: `aligned_zst_typed_copy`, `all_zst_union`, `zst_array_indexing`.
Quick workflows в целом **не зелёные**: flag-on selector падает до CBMC и на base, и с фиксом. Отделить selector от workflow.
У full run macOS 14 без test steps, macOS 15 Intel дошёл до setup, завершённого regression результата нет у обоих;
не приписывать причину отмены без evidence. Не писать «full CI PASS» либо «placement remains pending».

Новый squash SHA показать отдельно: **NOT_RUN; same tree as 6db3c4dab** с обоими tree IDs. Исторические runs не переименовывать
в runs нового SHA; quick wrapper содержит workflow-only изменения, его полный tree не объявлять равным source head.

### Related issues и заключительные строки

Указать **`Related to #5085`**: аналогичный CBMC invariant на другом lowering, не установленная идентичность механизма.
Отдельную flag-on compiler panic `relevant_instruction.rs:136:73` связать с **`#4854`** как triage сходного отказа:
паника воспроизведена на обоих matched trees, точные operation/operand из backtrace неизвестны; reduced PANIC-NOTE input
**NOT_RUN**. B3 её не исправляет. Ни для одного issue не использовать closes/fixes/resolves.

Закончить описание этими точными строками:

`By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.`

`*Disclosure: this change and description were prepared with AI assistance.*`

## 3. Результаты, review и STOP

В **этом t0 worktree**, `research/challenge-8/kani-k1/kani3300/b3p/`: `PR-DRAFT.md`,
`TREE-CHECK.md` (full base/old/new SHA, tree IDs, parent/count/diff checks), `REVIEW.md` и
`RESULT-KANI-B3P.md` (≤15 строк: новый локальный SHA, tree equality, draft fixes, remaining macOS/uninit limits).
Bounded независимая проверка текста и упаковки Luna High, без вложенной делегации; неизменённый semantic diff повторно
не ревьюить. Если tree изменился — STOP, а не присвоение прежнего audit/CI новому кандидату.

Research-коммит `[skip ci]`, автор/committer Tiramisu-Cake через `git -c`, stage только `kani3300/b3p/`, push t0 без force.
При concurrent/non-fast-forward — handoff координатору без reset/stash/force. Не включать чужие файлы.
Никаких локальных cargo/rustc/Kani/CBMC/Miri, сборок/тестов, CI/Actions/Cloud dispatch, raw logs/archives/credentials,
PR/issue/комментариев и ссылок на сторонние PR. CI при необходимости запускает координатор.
Не менять B1/B1I, не писать B1R3 и не начинать соседний fix; после результата STOP.
Последняя строка ответа: `READY <sha нового локального коммита Kani>`.
