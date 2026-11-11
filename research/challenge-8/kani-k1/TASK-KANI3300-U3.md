# KANI3300 U3 — патч Kani v2: `T → MaybeUninit<T>` (в т.ч. массивы, `IntoIter`) и изоляция assigns-отказов argument buffer

**Выдано координатором 2026-11-11, ночной GO владельца (общий бюджет проекта ≤ $6.40); дизайн — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-U3-ANSWER.md`, прочитать целиком).**
Research-ветка; цель — расширение патча U1, пригодное для upstream. Dispatch только после exact-packet PRE-BUILD
review/GO координатора. Runtime **Codex**, одна стадия. Это native-пакет; повтор на verify-std (diagnostic) — отдельная
следующая стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani3300-u3**, ветка **experiment/kani-k1-kani3300u3-20261111** от U1R head `0bc1a0e8d4`
  (tooling base `c98d7cee0d`). Tooling, пин `f046b70644`, toolchain не менять.
- Код Kani — **новый** локальный клон **/root/kani-fix-3300-v2** от `/root/kani-fix-3300` на коммите **`546bcf3`** (= патч U1,
  sha 306851ac…), своя ветка `fix/kani-3300-v2`; клон `/root/kani-fix-3300` (идёт U1T) и `/root/kani-review-3300` не трогать.
  Патч `research/challenge-8/kani-k1/kani3300/u3/kani-uninit-v2.patch` = diff от полного `f046b70644` (production + все тесты,
  включая новые файлы), SHA-256 в request.
- Slug **kani3300**, stage `kani3300-u3`, stable owner **k1-merge**, request `kani3300-u3-*`.
- Cap **$0.90**: одна сборка `kind: kani-tests` (work ≤ 10 мин ⇒ резерв ≈ $0.540) + не более одного repair по факту
  (факт + новый резерв ≤ cap, новый GO). Окно: main 420 + closeout 30.
- **Dispatch только после результата U1T** (`/root/verify-rust-std-kani3300-u1t`, ветка experiment/kani-k1-kani3300u1t-20261111,
  `kani3300/u1t/RESULT-KANI3300-U1T.md` — читать через `git fetch` + `git show`). Если U1T нашёл ложный SUCCESS — его
  исправление становится первым пунктом U3 (`Координатор, вопрос` с предложением). Тесты U1T (14 файлов, клон
  `/root/kani-fix-3300` коммит `647109c`) перенести в v2 как есть (cherry-pick или копия), ожидания не менять.

## Контекст (U2, `/root/verify-rust-std-kani3300-u2` @ 4ecdcc5930, `kani3300/u2/RESULT-KANI3300-U2.md`)

- U8/U9 blocker @ `core/src/array/iter.rs:77` (`IntoIter::new`, `[T;N]` → `[MaybeUninit<T>;N]`, из `for offset in
  [0, len_div_2]` smallsort.rs:267): «Transmuting between types of incompatible layouts» + «Kani does not support this
  assignment to MaybeUninit storage».
- U7: «Check that *var_9 / *var_17 is assignable» @ `library/kani_core/src/mem_init.rs:382`, `:404` (запись/очистка
  глобального ARGUMENT_BUFFER патча U1) в `proof_for_contract` с узким `modifies` + `select_unpredictable` Unimplemented.

## Что реализовать

**(a) `T → MaybeUninit<T>` и `[T; N] → [MaybeUninit<T>; N]`** (совпадение T/N и размера, узкое распознавание): matcher
transmute и обработчик назначения согласованно выполняют **один** перенос shadow по маске T (data bytes и padding — по
корректной маске, **без** blanket initialization всего destination); типизированное чтение источника сохраняет свои
проверки; Copy — свидетельства источника и назначения; Move — покрытие каждого неинициализированного байта в живом
назначении. Общая обработка assignment не должна затем перезаписать результат или выдать прежний Unsupported.
Полный `IntoIterator::into_iter([usize; 2])` дальше упаковывает данные в `InnerSized`/`PolymorphicIter`/`ManuallyDrop`
(struct с массивом `MaybeUninit`). **Составные storage-формы с полями в этой стадии НЕ реализовывать**: native fixture
с полным IntoIter должен показать следующее препятствие (ожидание — явный Unsupported, не ложный SUCCESS) — это
результат стадии, а не провал.

**(b) assigns-отказы ARGUMENT_BUFFER:** минимальные repro — одинаковый `MaybeUninit` round-trip через аргумент/return в
обычном proof и в `proof_for_contract` обёртки с узким `modifies`, без select и прочих Unsupported; отдельно — clause
контракта, внутри которого создаётся и читается `MaybeUninit`. Исправить ghost-instrumentation так, чтобы positive
проходили без assigns failures, **не ослабляя** пользовательские frame checks и общие флаги контрактов. Обязательный
контроль: пользовательская функция пишет за пределы `modifies` → по-прежнему assigns-отказ. Проверить парность
Store/Load, вложенные вызовы, два аргумента, return index 0, очистку stale buffer, вызовы без MIR body (shadow-carrying
вызов без подтверждённой модели — Unsupported). Lifetime адреса return place — обосновать в PRE-BUILD.
Если исправление (b) требует менять общий DFCC/contracts-код вне `check_uninit/` и `kani_core/src/mem_init.rs` —
**стоп, `Координатор, вопрос`** с причиной.

**(c) `select_unpredictable` — вне scope** (следующий подэтап; остаётся Unsupported).

## Тесты (manifest ≤ 20 selectors)

- (a): scalar conversion; точный `[usize; 2]`; нулевая длина/ZST; padded source с отрицательным чтением padding; Copy и
  Move; полный `IntoIter` (ожидаемое наблюдаемое поведение — по факту, с конкретной диагностикой). Сохранить отрицательные
  `MaybeUninit<T> → T` и `partial-copy`/`reset` regression.
- (b): plain/PFC и clause-пары; argument/return и nested-call positive/negative; пользовательское нарушение frame.
- U1T: перенести; в manifest — компактный набор (positive review + 2–3 negative), остальные — NOT_RUN с перечнем.
- Negative — конкретная диагностика в golden и request; positive — `require_success: true`. Golden существующих тестов
  Kani не переписывать.

## Приёмка

- PASS: применение к свежему пину; новые positive — native PASS; negative — ожидаемая диагностика из собственного вывода;
  контроль frame-нарушения — assigns-отказ сохранён; нет TIMEOUT/ignored. Неожиданный SUCCESS negative — блокер.
- Статика: `git apply --check` на свежем пине, rustfmt ноль diff, diffstat production/tests, изменения только в
  `kani-compiler/src/kani_middle/transform/check_uninit/`, `library/kani_core/src/mem_init.rs`, `tests/`.
- После native PASS новый production diff (v2 − U1) передаётся на независимое ревью (отдельная стадия координатора).

## RESULT

**RESULT-KANI3300-U3.md** в `kani3300/u3/`, ≤ 45 строк: identities; семантика (a)/(b) кратко с инвариантами; что показал
полный IntoIter (следующее препятствие); diffstat v2 − U1; таблица тестов; расход; предложение scope следующего шага
(составные storage-формы для U8/U9, select) и состав diagnostic replay (U1/U2, U6, U7–U9).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]`, push без force, глобальный git config не менять, без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native`; raw logs, archives, credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh` — можно. Никаких Actions/PR/issue/
  комментариев; push в model-checking/kani или Tiramisu-Cake/kani запрещён.
- Чужие PR verify-rust-std не открывать.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 U3 ЗАВЕРШЁН**, одна стадия, затем стоп.
