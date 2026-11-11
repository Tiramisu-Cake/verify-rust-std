# KANI3300 G1R5 — три класса отказов fork CI после G1R4

**Выдано координатором 2026-11-11.** Runtime **Codex**, одна стадия, **Cloud $0** (проверка — fork CI координатором).
`TASK-KANI3300-G1.md`, правки планера, G1R…G1R4 остаются в силе, кроме решения п.4 ниже.

## Факт (fork CI run 43072489798, ветка `kani-3300-g1-ci` @ 4a5a236d0 = G1R4 5b2265c41 + golden fix части 1)

Suite `kani` теперь PASS (аллокаторная регрессия исправлена). Suite `expected`: 3 FAILED (последующие suites не запускались).

1. **`expected/uninit/delayed-ub-unsupported-call`** (существующий upstream тест, в части 1 PASS). Harness `check_fn_ptr_call`:
   ожидается `Failed Checks: Kani does not support memory initialization checks across calls through function pointers.`
   (delayed-UB / `points_to_analysis.rs:359`), получено `Failed Checks: Kani was not able to resolve the instance of the
   function operand …FnPtr…` (`try_resolve_instance`, `ptr_uninit/uninit_visitor.rs:~1229`). Причина (проверь): в base f046
   Err-ветка `try_resolve_instance` делала `push_target(Unsupported)` и `return` **без** `self.targets.push(...)` — target
   терялся; G1 добавил `self.targets.push` (стр. ~577), Unsupported стал реальным и заслоняет delayed-UB.
2. **`g1-union-pointee-unsupported-reject_forget_union_array`**: `std::intrinsics::forget([U { wide: 1 }; 0])` →
   VERIFICATION SUCCESSFUL, exit 0; golden ждёт `reject_forget_union_array.unsupported_construct.` + FAILURE +
   `Cannot determine layout for a type that contains union of type U as a field.`
3. **`g1-union-pointee-negative`** (70 harness): 282 строк expected, отсутствуют 10:
   - `padded_typed_transfer_padding_{c,rust}`, `padded_argument_return_padding_{c,rust}`: **CBMC failed with status 134**
     (abort, вывода свойств нет) — G1-инструментация даёт GOTO, на котором CBMC падает. Других harness с 134 не видно;
     проверь по коду, какая операция в этих путях (typed union copy с padding Padded внутри `CU/RU {z: (), padded}`,
     передача/возврат через `#[inline(never)]` identity) генерирует ненормальные goto-выражения (несовпадение размеров/типов
     byte_extract/update, zero-size, pointer arithmetic на ZST и т.п.);
   - `intrinsic_forget_move_source_uninit_{c,rust}`, `field_move_projection_source_uninit_{c,rust}`,
     `field_move_constructor_source_uninit_{c,rust}`: VERIFICATION SUCCESSFUL вместо ожидаемого FAILURE;
   - итоговая строка `Complete - 0 successfully verified harnesses, 70 failures` (сейчас 6 SUCCESSFUL).

## Что сделать

1. (п.1) Сохранить поведение base для вызовов, не затрагивающих union: Unsupported по нерезолвимому callee реально
   добавлять только если аргументы/destination `transfers_shadow`/`touches_shadow`; иначе — как в base. Golden
   `delayed-ub-unsupported-call` не менять. Потерю target в base отметить в `kani3300/g1r5/NOTES.md` как отдельную находку
   (вне scope), без issue.
2. (п.2) Определить: правильно ли SUCCESS для `[U; 0]` (нет байтов) — тогда фикстура должна брать непустой массив
   (`[U; 1]`/`[U; 2]`) так, чтобы guard ty_layout действительно срабатывал; либо guard обязан срабатывать и для `[U; 0]`.
   Обосновать в NOTES.md, исправить фикстуру/golden или production.
3. (п.3, CBMC 134) Найти по исходнику причину и исправить production; если причина не устанавливается статически с
   уверенностью — минимальный изолированный тест-кандидат + 2–3 гипотезы в NOTES.md, фикстуры не удалять.
4. (п.3, move-source) **Решение координатора:** очистку moved-from source при `Operand::Move` из G1 **убрать** —
   согласованно с частью 1 (Known limitations: move не помечает источник неинициализированным, как для других типов) и
   с Miri; это снимает вопрос «строже Miri». Удалить шесть move-source harness и их строки в golden, поправить итоговую
   строку счётчика; позитивные фикстуры не ослаблять. Если удаление затрагивает инварианты парных store/load (G1R3:
   `intrinsics::forget` no-effect модель) — оставить минимально необходимое и описать в NOTES.md.
5. Статика: rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`
   (`--config-path rustfmt.toml` репозитория, edition из конфига — так проверяет CI; **все** тестовые .rs тоже), `git diff
   --check`; `-D warnings` (после удаления кода — нет ли unused); сигнатуры stable_mir.
6. Независимое ревью (свой ревьюер).

## Результат

`kani3300/g1r5/NOTES.md` (≤ 30 строк) + `RESULT-KANI3300-G1R5.md` (≤ 20 строк). Коммиты Kani в `/root/kani-fix-3300-g1`
(автор Tiramisu-Cake через `-c`, не пушить; production и тесты — отдельными коммитами, сообщения без `[skip ci]`).
Research-коммит `[skip ci]`, push без force. Последней строкой `G1R5 READY <sha последнего коммита Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
