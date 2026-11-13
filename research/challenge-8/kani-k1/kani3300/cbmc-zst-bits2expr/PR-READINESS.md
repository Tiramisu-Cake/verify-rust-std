# CBMC ZST bits2expr — готовность PR-кандидата, 2026-11-13

**GO для показа владельцу как готового к review CBMC PR-кандидата.** Не утверждаем полный upstream CI PASS.
Clean source **cd41a5c74b0c42edf4f08834b3e2808dd3344cab**, parent107a1e504cd69a2f3483717c8bcfcfa59814c557.
Один production-line fix +13 regression directories +3 util test cases, обязательный commit body есть, workflows в source delta нет.
PR source — этот clean commit, **не** CI-only91062c7dba/33235a4ef1 с удалёнными upstream workflows.

## Свидетельства

- [CI r2 43334186094](https://github.com/Tiramisu-Cake/cbmc/actions/runs/43334186094), CI-only91062c7dba9da7541c0e607a3735482e38d28d36,
  ubuntu-24.04/gcc13/CMake Release/minisat2. Baseline = develop+те же test bytes:12/13 focused FAIL с invariant, memcpy PASS.
- Fix:13/13 focused oracles (один intended negative),13 соседних directories (14 descriptors),focused unit3/3.
  Это сильное дифференциальное подтверждение one-line change, не «все13 программ VERIFIED».
- Остальные выбранные unit `[util]~[zst-bits2expr]`:205/212;7 failures в piped_process.cpp на runner без z3.
  Объяснение согласуется с source .z3 tests, но для заявления полного PASS нужен rerun с доступным z3.
- Последнее сообщение координатора: baseline owner-literal/kani-like C = ZST_ARRAY_INVARIANT, fix = VERIFIED.
  [CI-RESULT-R2.md](CI-RESULT-R2.md) ещё говорит «summary to be checked»: здесь записано позднее сообщение,
  не независимая проверка raw artifacts. Историческую запись не переписываем; final receipt может уточнить bindings.
- R1 SIGXFSZ при ar был RLIMIT_FSIZE build harness, не source regression; r2 сохраняет отсутствие build file-size cap.
  Format oracle r2 допускает empty git-clang-format diff. Исправления обвязки не входят в PR source.

## Минимальный следующий шаг

[TASK-CBMC-ZST-PRREADY.md](../../TASK-CBMC-ZST-PRREADY.md): CI-only environment repair с z3 и повтор **той же** util selection.
Source/tree/test bytes оставить cd41a5c74b. Worker15 готовит пакет; координатор пушит/запускает один workflow в форке.
Это полезное закрытие известной красной проверки перед публичной отправкой, **не условие, чтобы показать кандидата владельцу сейчас**.
Если при установленном z3 остаются failures — не списывать автоматически на окружение; вернуть конкретные assertions/statuses.

Полный regression/cbmc/ctest и macOS **не обязательны для этого показа**: focused differential + utility roundtrips обоих endian
и Linux neighbour evidence достаточны для review. Для upstream acceptance остаётся штатный PR CI/matrix; не выдаём собственный subset за него.
Новые широкие/platform runs не ставим автоматически. Kani replay B3/caseB/#5085 — отдельный integration gate для таких claims
и решения об откате Kani workaround; для корректности общего CBMC fix он не prerequisite. Kani-like C не является replay Rust/Kani.

## Дрейф develop и отправка

При чтении upstream develop уже **37a17adc07f29e1127f100debf1d8eea00532a24**, на2 commits впереди107a1e504c.
Primary compare показывает изменения только C frontend void-pointer arithmetic и соседних tests; simplify_utils.cpp не изменён,
его array >0 guard по-прежнему на месте. Current develop runtime здесь NOT_RUN; source-overlap не найден, свежий CI ему не присваивается.
Для показа сохраняем tested cd41; перед публикацией владелец проверит mergeability/base и решит о clean rebase.
Если меняется source/tree/base — зафиксировать новый SHA и провести соответствующие targeted checks, не переносить весь CI автоматически.

Issue и PR подготовлены файлами рядом; ничего не создано в GitHub. Exact-term search `bits2expr` среди CBMC issues не дал результатов
на дату чтения; это не доказательство отсутствия дублей. Владелец перепроверяет перед issue→PR.
Ориентируемся на pinned `.github/issue_template.md` и `.github/pull_request_template.md`; PR с одной bugfix feature,
tests в том же commit, без performance claims/CI-only overlay. Disclosure — новая согласованная строка.

Source/результаты независимо не запускались этой оценкой; Cloud $0. G-SC/PFC resource остаётся на своей паузе.
