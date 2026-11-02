# NETTHIRTEEN (N13) — прямая проверка перестановки network N13 на настоящем маршруте

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-netthirteen`, ветка
`experiment/kani-k1-netthirteen-20261102` от N1 `dfaba49ddc`. Cap 88.96. Ожидание Build —
`research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и завершить ход. request_id с
префиксом `netthirteen-`; свой spent/reserved по своим UUID. GO даёт координатор. Evidence Brief / Select-Merge к
K-1 не относятся. Код конкурирующих PR не открывать.

Прочитать: `RESULT-NETNINE.md`, `TASK-NETNINE.md` (раздел «Уточнения»), в `verify/network.rs` — гармоники
`netnine_*` и `count_matching_values`; `small_sort_network` / `UnstableSmallSortTypeImpl` для Freeze в
`smallsort.rs`; `TASK-SPECFIX.md` (только запреты, логи, rustfmt, expect_check); `integwrapfix/pfc_order.py`.

## Вопрос

N1 прямо доказал sortedness + full-value permutation для u8 N9 (261 с, 259 MiB). Укладывается ли та же прямая
проверка для u8 N13 в 10 минут на pin? N9 ≠ N13: другая сеть и другая solver-задача, успех не гарантирован.

## Постановка (opt-in под `kani_smallsort_controls`; ordinary 200 не меняется)

1. Positive — копия N9 на N13: `[u8; 13] = any`, независимый `probe: u8 = any`, F = function item
   `strict_less::<u8>`, настоящий Unstable u8 / default-< маршрут, без stubs и assume на входе; assert sortedness
   и count(pre, probe) == count(v, probe); те же 4 covers, что у N9 positive.
2. Negative: probe=0, input=[0;13], после настоящей сортировки v[12]=1. Порядок сохраняется, count(0) 13→12;
   expected failure только literal count; cover достижения corruption перед целевым assert. Covers positive сюда
   не копировать.
3. Гармоники N9 не трогать.

## Сборка (1, резерв $0.675)

G1 measurement, controls:true, kani_jobs 1, uninit off, unwind как у N9 (или минимально необходимый для N13 —
обосновать в PRE-BUILD REVIEW), timeout 10 мин, 2 rows → (2×10+30)×0.0135 = $0.675. Один Build без повтора.
PRE-BUILD REVIEW (полный diff, pfc_order OK, ordinary 200 неизменен) → GO → build. Library commit отдельно от
research, `[skip ci]`, push без force.

## Итог

`RESULT-NETTHIRTEEN.md` ≤ 30 строк: rows/status/VT/RSS/covers/failed checks. TIMEOUT — результат о текущем
resource fit: записать cap 600 s и доступные wall/RSS (VT=UNKNOWN, если не напечатан); не сужать input/probe и не
переходить к N18 автоматически. SUCCESS не означает N18 или u64. Маркеры `REVIEW REQUEST <sha>` /
`NETTHIRTEEN ЗАВЕРШЁН`. Один этап — после итога остановиться.

## Уточнения (обязательны, приоритет над текстом выше)

- Оба задания: старые harnesses оставить без изменений, в request выбрать полные exact имена только новых строк (3 WONEDIAG / 2 NETTHIRTEEN). Не запускать весь controls-набор с унаследованными TIMEOUT/OOM/expected failures. Статически ожидать ordinary200 и cfg-on391 для WONEDIAG, ordinary200 и cfg-on386 для NETTHIRTEEN; эти counts подтверждают состав, не proofs. Не переносить ветки на MACSPLIT/v6 в рамках пилотов.
- NETTHIRTEEN: negative сохранить проверку sortedness ПОСЛЕ v[12]=1 и две достижимые covers — возврат настоящей сортировки до порчи и достижение count-check после проверки порядка. Использовать новый уникальный literal, например kani::assert(..., "netthirteen negative: full-value count preserved"), и тот же exact expect_check. Допустим только этот FAILED; sortedness/unwinding/unsupported/setup failures не засчитывать отрицательным контролем.
- NETTHIRTEEN: исходный bound25 достаточен для явных count/sortedness/duplicate loops N13; оставить его для первого прогона и сохранить unwinding assertions. Отклонение от него отдельно обосновать в PRE-BUILD REVIEW, без пробного Build/авторетрая. В RESULT фиксировать actual function-item F strict_less::<u8> и маршрут sort13_optimal → insertion с уже полным prefix13 (без вставок), без merge; не переносить описание sort9 из N1. Positive SUCCESS требует 4/4 covers; результат остаётся opt-in, с uninit checks off.
