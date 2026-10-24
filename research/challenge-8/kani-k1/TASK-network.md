# Задание K1-network

Runtime: Claude Code. Владелец задания: K1-network. Ветка `experiment/kani-k1-network-20261024`, worktree `/root/verify-rust-std-kani-k1-network`. Норматив — [EXPERIMENT.md](EXPERIMENT.md). Окно: 480 + 30 минут от фактического T0. Cloud-бюджет 0, lane — GitHub Actions по §5.

## Цель

Получить исход цепочки network для K-1: PASS, FAIL (STOP) или INCONCLUSIVE по критерию §2.

## Шаги

1. **Ранняя проба old().** Один diagnostic-прогон: контракт `swap_if_less` с постусловием compare-exchange и перестановки двух ячеек через `old()`. Выяснить, компилируется ли он и доказывается ли для `u8`. Затем прочитать первую находку K1-merge в его RESULT-merge.md на опубликованной ветке.
2. **Сети.** Контракт `swap_if_less` с `proof_for_contract` для `u8`, `i32`, `u64` при `a_pos != b_pos` в пределах SAFETY. Затем `sort9_optimal` и `sort13_optimal`: безопасность и перестановка через `stub_verified(swap_if_less)`. Сортированность на полной ширине, если укладывается, иначе на u8 по принципу 0–1 со строкой в «Редукциях».
3. **Insertion в network.** `insertion_sort_shift_left` на регионах network: длина до 16, offset 1, 9 или 13. Через контракт `insert_tail` из ветки K1-merge или напрямую.
4. **Верхние гармоники.** `UnstableSmallSortFreezeTypeImpl::small_sort` для `u8`, `i32`, `u64` при символьной длине 0..=32. Длины 0..=17 не требуют merge, их можно сделать до контракта K1-merge. Длины 18..=32 используют `bidirectional_merge` из ветки K1-merge через `stub_verified`.
5. **Замер и вердикт.** Measurement-прогоны на `ubuntu-latest`, затем на `macos-latest`. Review по R9. RESULT-network.md по §8. Push.

Если K1-merge объявил STOP по `bidirectional_merge`, длины 18..=32 закрыть нельзя. Тогда довести длины 0..=17, записать FAIL с этой причиной и закрыть задание.
