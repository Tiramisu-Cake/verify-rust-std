# CASE5-2 — закрыть вопрос доверия к array-model PFC (одна диагностическая сборка)

Исполнитель: Claude Code, свежий контекст, tmux 5. Worktree `/root/verify-rust-std-kani-casefive`, та же ветка
`experiment/kani-k1-casefive-20261101`, база — текущий HEAD `8f934ca826` (итог CASE5). Cap 88.96.
Ожидание Build — `k1g.sh wait UUID` в фоне. Evidence Brief / Select-Merge к K-1 не относятся.
Владелец до утра недоступен — GO даёт координатор.

Прочитать: `RESULT-CASEFIVE.md` (весь), `casefive/`, `verify/merge/casefive.rs`, `swap_contract_fixed` и
`swap_contract_exact_array_case!` в `verify/network.rs`, `swap_profile` в `verify/merge/specfix.rs`,
`planner-casefive-g1-answer.md` в coordinator scratchpad/plan. TASK-SPECFIX запреты/логи/rustfmt действуют.

## Вопрос

CASE5 локализовал расхождение модели на pin: `ptr::read`/`ptr::copy` через указатель, выбранный
`hint::select_unpredictable`, даёт неверное значение для `[u8; M]` (u8 проходит). При этом PFC
`swap_contract_bytes17_n2` (тот же swap_if_less) проходит. Нужно установить, можно ли доверять
array-model PFC в P1 (`swap_contract_bytes16_n2`, `swap_contract_bytes17_n2`, `sort4_contract_bytes16_n4`),
и получить минимальный воспроизводимый пример.

## Матрица (opt-in в `casefive.rs`, literal `kani::assert`, unwind 180, ровно 8 rows)

Общие правила: pre-снимок ПОСЛЕ создания `v`; `taken` из `pre[b]`, `pre[a]`; ожидание проверять по
позициям a, b (при reverse не использовать oracle R0 для фиксированных (0,1)). Witness/covers
(различающийся payload, достижение вызова, обе ветви, оба порядка индексов) ставить ДО проверок; ранних
failing assert не вставлять.

1. A1 — plain (без PFC) `swap_profile::<KeyB17>` в fixture формы `swap_contract_fixed` (`array::from_fn`,
   `reverse`, `KeyB17::CMP`): bool `eq_ok` (array `==`) и `bytes_ok` (побайтно), covers, затем
   assert `eq_ok == bytes_ok`, затем assert `bytes_ok`.
2. A2 — то же, но прямой `swap_if_less` с `KeyB17::CMP` (matched raw baseline к A1).
3. P17 — PFC инструментированного двойника `swap_profile_checked::<KeyB17>`: те же requires/modifies/
   ensures, что `swap_profile`; тело — тот же настоящий `swap_if_less`, затем ВНУТРИ target независимые
   побайтные pre/post проверки transfer и сохранности предснимка. Fixture — `swap_contract_fixed`.
4. P16 — то же для `KeyB16`.
5. S4 — PFC инструментированного двойника `sort4_profile_checked::<Sort4ReadB16>`: настоящий
   `sort4_stable`, внутри target независимая побайтная проверка: каждый выход побайтно равен одному из
   входов, побайтные счёты сохраняются, ключи упорядочены. Fixture — как `sort4_contract_bytes16_n4`.
6. C1 — НЕГАТИВНЫЙ: `bad_swap_profile::<KeyB17>` с ТЕМИ ЖЕ requires/modifies/ensures; тело сохраняет
   `old_b` и пишет его в a и b (без selected-pointer операций, без UB). Witness ДО проверок: одинаковый
   ключ и заведомо различающийся неключевой байт `[1]`. Ожидается FAILED ровно на transfer ensures;
   SUCCESS при живом witness дискредитирует контрактную проверку.
7. D1 — минимальный reproducer: `x, y: [u8; 1] = any`, `v = [x, y]`, `c: bool = any`,
   `s = hint::select_unpredictable(c, v.as_mut_ptr(), v.as_mut_ptr().add(1))`,
   `kani::assert(ptr::read(s)[0] == if c { x[0] } else { y[0] })`. Если SUCCESS — минимальная форма НЕ
   воспроизведена, запущенным reproducer остаётся G2B.
8. D2 — D1 на `u8` (скалярный контроль).
Expect каждого — предсказание в PRE-BUILD REVIEW; COMPLETE не требует совпадения всех ожиданий.

## Критерий вердикта (отдельно по каждому профилю: KeyB17, KeyB16, Sort4ReadB16)

- «локальная согласованность»: все целевые проверки SUCCESS с covers обоих порядков и обеих ветвей
  (A1, A2 для KeyB17; P17/P16/S4 для своего профиля) и C1 FAILED ровно на transfer ensures. Это не
  доказывает верность моделирования настоящего тела в общем случае — так и писать.
- «model-trust OPEN»: согласованный FAILED, отсутствующие covers, compile/timeout или C1 не на ensures.
- «NOT TRUSTED»: PFC-target с внутренними побайтными проверками FAILED, а PFC без них проходил; или C1 SUCCESS.
Также ослабить в RESULT формулировку о G2C: он показал обнаружение хотя бы одного сбоя в этом
контексте, не корректность `==` для всех длин/payload/PFC-контекстов.

## Сборка (1 build, ≤ $0.75)

Kind diagnostic, controls:true, kani_jobs 1, uninit off, timeout 3 мин: 8 rows → 54 мин / $0.729.
PRE-BUILD REVIEW → GO координатора → build. Второй сборки нет. Library commit отдельно, `[skip ci]`.

## Итог

Дописать в `RESULT-CASEFIVE.md` раздел «CASE5-2» (≤ 40 строк; при необходимости сжать раздел G1):
rows, вердикт по каждому из трёх профилей по критерию выше, минимальный reproducer (запущенная форма, результат), что делать с
этими PFC в Part 1 (оставить / оставить с оговоркой / вывести из ordinary). Внешних публикаций нет.
Маркеры `REVIEW REQUEST <sha>` / `CASEFIVE-2 ЗАВЕРШЁН`.
