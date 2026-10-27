# W3-L1 — сборка набора, R8

Старт: 2026-10-27T10:17:26Z. Ветка `experiment/kani-k1-assembly-20261027`.
Прочитаны актуальные AGENTS.md, W3-RULES.md и TASK-w3-l1.md с базы, R8,
EXPERIMENT.md §5b и решения CD-1…CD-6. `git pull`: up-to-date.
Lane: `k1g.sh`, `gcb-e2-standard-4`; база tooling `67a4b452a932d070cf77853a3682c7998de93870`.
Доля $6,20. Расход до первого build: $0,0000. L1-7 — только по отдельной команде.

## L1-2 — has_efficient_in_place_swap

`smoke::w3_efficient_swap_c3`: одна ordinary proof, ожидается SUCCESS.
Типы: u8, u64, u128, [u8;16], [u8;17], [u8;85], [u8;86],
`#[repr(transparent)] W3SwapDrop(u8)` с Drop, Cell<i32>, ().
Ожидания соответственно: true, true, false, false, false, false, false,
true, true, true. По одному cover на тип (10).
Ledger: нет assume, any_where, заглушек или should_panic; runtime и lane не меняются.
Пока не измерено; R9 ожидается.

## R7-1 — контракт L1-3

В текущем дереве `sort4_stable` имеет безусловное ensures `k1_sorted(dst, 4, &is_less)`
(`smallsort.rs:697`). Произвольный comparator CD-2 не может удовлетворять этому
постусловию: при проверке соседней пары он снова вправе вернуть true.
Таким образом, повтор proof_for_contract с произвольным результатом требует
согласования формулировки контракта; W3-L1 не владеет атрибутами smallsort.rs.
Первый build ограничен L1-2. Это ограничение не считается PASS L1-3;
следующим шагом будет проверка допустимой формулировки в пределах задания.
