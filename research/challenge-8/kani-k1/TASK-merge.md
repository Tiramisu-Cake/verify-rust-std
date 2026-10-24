# Задание K1-merge

Runtime: Claude Code. Владелец задания: K1-merge. Ветка `experiment/kani-k1-merge-20261024`, worktree `/root/verify-rust-std-kani-k1-merge`. Норматив — [EXPERIMENT.md](EXPERIMENT.md). Окно: фаза 1, 120 + 20 минут от T0, не больше 6 dispatch (EXPERIMENT.md §9 «Фазы и окно»). Cloud-бюджет 0, lane — CircleCI по §5.

## Цель

Получить исход цепочки general для K-1: PASS, FAIL (STOP) или INCONCLUSIVE по критерию §2. Опубликовать контракты `insert_tail` и `bidirectional_merge`, которые нужны K1-network.

## Шаги

1. **Ранняя проба old().** Один diagnostic-прогон: контракт на `insert_tail` с постусловием перестановки через `old()` и контракт `bidirectional_merge` с перестановкой без `old()`. Выяснить, компилируется ли каждый и доказывается ли на малой длине. Записать результат в RESULT как первую находку и сразу запушить, его ждёт K1-network.
   Тем же прогоном или следующим выполнить контроль предусловий R11 на своей функции. Результат записать в RESULT и запушить: от него зависит, засчитывается ли композиция у обоих агентов.
2. **Контракты callee.** `bidirectional_merge` вместе с `merge_up` и `merge_down`, если они нужны. Затем `sort4_stable`, `sort8_stable`, `insert_tail`. Каждый с `proof_for_contract` на всей области, достижимой из general при длине до 32 и scratch длины 48. Способ, развёртка или loop contract, на выбор. Сначала доказывается `bidirectional_merge`: от него зависит STOP всего K-1.
3. **Верхние гармоники.** Типы и entrypoints из §2 п. 3, символьная длина 0..=32, все перечисленные callee через `stub_verified`. Проверяются сортированность и перестановка по полному значению.
4. **Замер и вердикт.** Measurement-прогоны на `circleci-linux-large` по §5, не больше четырёх гармоник с таймаутом 10 минут в одном запросе. Review по R9. RESULT-merge.md по §8. Push.

Если контракт `bidirectional_merge` не доказывается, это STOP. Записать причину и наибольшую длину, которая укладывается в 10 минут при прямой проверке без заглушки, и закрыть задание.
