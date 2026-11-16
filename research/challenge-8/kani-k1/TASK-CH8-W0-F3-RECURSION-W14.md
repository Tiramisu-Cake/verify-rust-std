# TASK — worker14: F3 — рекурсия в delayed-UB points-to анализе, отдельный PR на main (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Правила: STYLE-UPSTREAM-RULES.md (обязательно). Образец формы — твой F1 (`kani3300/wave0/f1-reset/`, опубликован как kani#5183).

Дефект (подтверждён на `main` 0aac16ef62, run 43882466907, тест `kani3300/wave0/confirm-main/tests/expected/uninit/recursive-delayed/`):
рекурсивная функция, достижимая из harness с delayed-UB целью, — `PointsToAnalysis::run` в `apply_regular_call_effect`
(`kani-compiler/src/kani_middle/points_to/points_to_analysis.rs`) вызывается для каждого вызова без проверки повтора,
rustc падает `has overflowed its stack` до проверки harness.

Нужно: самостоятельный коммит прямо на upstream `0aac16ef62`, минимальный: при повторном входе в функцию, которая уже
анализируется, Kani вместо падения компилятора сообщает понятную диагностику (unsupported construct / failed check на этом
вызове — выбери механизм, который уже есть на `main`, без инфраструктуры #5172 и без остальной части PR-01 стека).
Справка: в стеке это делает PR-01 `d82752c8bc` (`/root/kani-ch8-b-census-w14`, «active call cycles») — брать только
защиту от рекурсии, без contract-bodies и прочего. Если без частей #5172 корректно не выходит — STOP с объяснением.

Тест: `tests/expected/uninit/<имя>/` на основе recursive-delayed из confirm-main: рекурсивный helper, delayed-UB цель
приведением указателя (как `tests/expected/uninit/delayed-ub/delayed-ub.rs`); ожидание — диагностика рекурсии, компилятор
не падает. Плюс по возможности нерекурсивный companion, который по-прежнему проверяется.

Также: PR-TEXT.md (заголовок в духе «Report recursion in delayed UB analysis as unsupported instead of overflowing the
stack»; Testing — что тест падает на `main` переполнением стека; место под одну ссылку на CI), ветка `fix/delayed-ub-recursion`.

Бюджет CI: 2 запуска (их выполняет координатор): (1) быстрый uninit-ci на голове, (2) полный набор стандартных workflow
на финальной голове. Подготовь CI-PLAN.md (что смотреть в каждом).

Выход: локальный worktree и коммит (author Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By, без [skip ci]);
g0 `kani3300/wave0/f3-recursion/`: PR-TEXT.md, CI-PLAN.md, HANDOFF.md, коммит g0 [skip ci].
Последней строкой READY <g0> <source SHA> или STOP <причина>.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
