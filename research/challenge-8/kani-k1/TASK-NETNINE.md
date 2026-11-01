# NETNINE (N1) — полный маршрут network N9: перестановка всего результата

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-netnine`, ветка
`experiment/kani-k1-netnine-20261102` от `e382287728` (library = v5 tree `cbe69760c8`). Cap 88.96. Ожидание Build —
`research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и завершить ход. request_id с
префиксом `netnine-`; свой spent/reserved по своим UUID. GO даёт координатор. Evidence Brief / Select-Merge к K-1
не относятся. Код конкурирующих PR не открывать.

Прочитать: `verify/network.rs` — `network_correctness_fixed` и комментарий «At N >= 9, compose…»,
`network_correctness_u8_n9`, `insertion_permutation_*`, `count_matching_values`; `small_sort_network` и
`UnstableSmallSortTypeImpl` для Freeze в `smallsort.rs`; `RESULT-C3C.md` (строки про network/insertion TIMEOUT);
`TASK-SPECFIX.md` (только запреты, логи, rustfmt, expect_check); `integwrapfix/pfc_order.py`.

## Вопрос

Сейчас при N ≥ 9 перестановка доказывается композиционно (структура network + отдельная insertion suffix
permutation), а прямой проверки full-value count всего результата на настоящем маршруте нет. Укладывается ли
прямая проверка `u8` N9 (default `<`, произвольные полные значения, независимый probe) в 10 минут на pin?

## Постановка (opt-in гармоники под `kani_smallsort_controls`; ordinary 200 не меняется)

1. Positive: `[u8; 9] = any`, `pre = v`, независимый `probe: u8 = any`, `cmp = strict_less::<u8>`, настоящий
   `<u8 as UnstableSmallSortTypeImpl>::small_sort`; assert sortedness и
   `count_matching_values(pre, probe) == count_matching_values(v, probe)`; covers: «sort moves elements»,
   «probe hits input», «probe misses input», «duplicates present». Без stubs и assume на входе.
2. Negative control: та же гармоника, после возврата `v[k] ^= 1` для фиксированного k (или witness
   `input = [p; 9]`), ожидаемый FAILED ровно на count (sortedness может сохраниться — проектировать так, чтобы
   падал только count).
3. Если positive TIMEOUT — это результат (записать VT до таймаута/RSS); не дробить по probe/значениям ради SUCCESS
   без отдельного GO. Опционально (в той же сборке, если резерв позволяет) — вариант с `probe` ограниченным
   значениями входа (`probe == v[i]` для any i) как диагностика стоимости, отдельной строкой и без зачёта.

## Сборки (1, ≤ $0.75)

G1 measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин; 2–3 rows → резерв ≤ (3×10+30)×0.0135 =
$0.81 — если 3 строки, превышение согласовать в PRE-BUILD REVIEW, иначе 2 строки ($0.675).
PRE-BUILD REVIEW (полный diff, pfc_order OK, ordinary неизменен) → GO → build. Library commit отдельно от research,
`[skip ci]`, push без force.

## Итог

`RESULT-NETNINE.md` ≤ 35 строк: гармоники, rows/status/VT/RSS/covers/failed checks, вывод: можно ли заменить
композиционный аргумент N9 прямой проверкой и что это значит для N13/N18 (оценка, не обещание). Маркеры
`REVIEW REQUEST <sha>` / `NETNINE ЗАВЕРШЁН`. Один этап — после итога остановиться.

## Уточнения (обязательны, приоритет над текстом выше)

- «Перестановка доказывается композиционно» → «есть структурный аргумент и отдельные leaf/suffix proofs; полной machine-checked композиции N9 нет». Positive — именно настоящий Unstable u8/default-< маршрут, полные any input и независимый any probe, без stubs/assume; F записать по фактическому типу strict_less::<u8>.
- Negative зафиксировать конкретно: probe=0, input=[0;9], после настоящей сортировки v[8]=1. Выход остаётся отсортирован по обычному <, count(0) меняется9→8; expected failure только count. Это узкий контроль, положительную универсальную постановку им не заменять. Не копировать сюда обязательство «sort moves»/«probe misses» от positive: в этом witness они невозможны.
- Произвольный v[k]^=1 под default-< может сломать sortedness и отсечь count assert; гарантия сохранения порядка от low-bit flip относилась к ключу x>>1. До целевого assert дать cover достижения corruption/check; expect_check должен указывать literal count, а не любой FAILED.
- Третий диагностический row сейчас убрать: 2×10+30 → $0.675, а 3×10+30 → $0.810>$0.75. PRE-BUILD GO не отменяет утверждённый cap; иной бюджет/постановка — отдельное явное изменение задания. Для первого ответа на вопрос двух строк достаточно.
- TIMEOUT фиксировать как TIMEOUT, cap600s и доступные wall/RSS; если Kani не напечатал Verification Time, VT=UNKNOWN/None, не600. Успех проверки задачи не равен успешному measurement gate при TIMEOUT; N13/N18 этим не доказаны.
- Обе ветки — opt-in и ordinary200 сохраняется. Успех W1 — проверка API/домена N0..3; переход L1 требует matching leaf geometry, принятого B2 и отдельного PRE-BUILD GO, а не автоматического расширения len.
