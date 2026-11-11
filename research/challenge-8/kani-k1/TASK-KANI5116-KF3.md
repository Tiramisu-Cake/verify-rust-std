# KANI5116 KF3 — правки по внешнему аудиту: `ImplItemFn` напрямую, усиление тестов, новая ветка для PR

**Выдано координатором 2026-11-11 по указанию владельца; позиция планера —
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-5116-AUDIT-ANSWER.md` (прочитать целиком),
замечания аудитора — `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-5116-AUDIT.md`.**
Runtime **Codex**, одна стадия, Cloud **$0**, без сборок.

## Рабочее место

- Kani: клон **/root/kani-fix-5116**. Исходный кандидат — ветка `upstream-5116` = `2a3e2ae` на Kani main `bf9c58e662`
  (уже в форке — **не менять**). Сейчас checkout на локальной ветке `upstream-5116-v2` с **незакоммиченным** наброском
  координатора (3 production-файла) — не решение: можно посмотреть, но работать от чистого `2a3e2ae`
  (например, `git checkout -- <3 файла>` и `git reset --hard upstream-5116` на `upstream-5116-v2`; без `git stash`).
- Итог — ветка `upstream-5116-v2`: **ровно один коммит поверх `bf9c58e662`**, автор Tiramisu-Cake <igkharin@gmail.com>
  (`-c user.name/-c user.email`), заголовок как у 2a3e2ae, без Co-Authored-By/`[skip ci]`/внутренних стадий.
  **Не пушить** (push в форк и CI — координатор).
- Research: worktree **/root/verify-rust-std-kani5116** (ветка experiment/kani-k1-kani5116-20261110), писать только
  `research/challenge-8/kani-k1/kani5116/kf3/`; коммиты `[skip ci]`, push без force.

## Правки

1. **Production — патч аудитора побайтно:** `/root/KANI5116-use-ImplItemFn.patch` (SHA-256 начинается с `0921813bdd50693e`;
   записать полный). Это дельта поверх `2a3e2ae`; `git apply --check` на чистом `2a3e2ae` координатор проверил — OK, итог
   против main +13/−12 в `library/kani_macros/src/sysroot/contracts/{mod,bootstrap,initialize}.rs`. Применить как есть,
   **своих production-правок не делать**; набросок координатора отбросить. В RESULT показать, что production-diff
   `bf9c58e662..HEAD` = `2a3e2ae` + этот патч. Статически проверить замечания планера: guard для trait declarations без тела
   сохранён, прочие `ItemFn` не тронуты, размещение inner attrs не изменено.
2. **`tests/expected/function-contract/specialization_default_requires_fail.rs`:** добавить `--no-assert-contracts` в kani-flags;
   сохранить PFC и `stub_verified`, имя invalid-caller harness и конкретный expected `value != 0` failure.
3. **`tests/kani/FunctionContracts/specialization_default_clauses.rs`:** `forward`/`reverse` → `requires_first`/`modifies_first`
   (все PFC/stub ссылки); добавить `stub_verified` harness и для второго порядка.
4. Комментарии, повторяющие имена тестов, убрать; комментарий со ссылкой на #4908/#5135 в generic-тесте оставить.
   Ложные контракты/unreachable тела ради различения не добавлять.

## Проверки (без cargo)

- rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --check --edition 2024`
  (конфиг репозитория) для изменённых `.rs`; `git diff --check`; лицензии; grep, что `ContractFunction` исчез и `default`
  выводится в обоих путях экспансии. Статически сверить по syn 2 (версия из `Cargo.lock`), что поля `ImplItemFn`
  {attrs, vis, defaultness, sig, block} и `block: Block` совместимы со всеми использованиями `annotated_fn`
  (check/replace/assert/helpers). Что требует компиляции — NOT_RUN (проверит fork CI).
- Независимое ревью финального diff (свой ревьюер), как в KF1.

## RESULT

**RESULT-KANI5116-KF3.md** в `kani5116/kf3/` (≤ 25 строк): финальный SHA `upstream-5116-v2`, база, diffstat
(production / tests), что изменено по пунктам 1–4, проверки, ревью, что NOT_RUN. Плюс `PR-TESTING-NOTE.md` — предложенный англ. раздел Testing для PR в стиле текста аудитора
(`/root/KANI5116-PR-REVIEWED.md` — основа PR по решению владельца): новый fork CI — плейсхолдер `<run, SHA>`; прежние
19 selectors — targeted native compiletest on Linux на f046b70644 с **предыдущей** ревизией патча (negative PASS =
совпадение expected diagnostic). Если по итогам правок какие-то фразы текста аудитора стали неточными (например, про
stub для обоих порядков) — перечислить.

## Запреты

- Никаких сборок/dispatch/Cloud, локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Не пушить Kani-ветки; не трогать `upstream-5116` и `fix/default-fn-contracts-5116`. Никаких Actions/PR/issue/комментариев.
- Raw logs/archives/credentials не читать. Без `git stash`. Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <research sha>` + финальный SHA ветки Kani / **KANI5116 KF3 ЗАВЕРШЁН**, одна стадия, затем стоп.
