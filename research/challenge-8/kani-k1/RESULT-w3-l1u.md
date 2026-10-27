# W3-L1u — Z-1 и U-1, план R8

Начало: 2026-10-27 10:19 UTC. Ветка `experiment/kani-k1-uninit-20261027`.
Прочитаны обновлённый AGENTS.md, W3-RULES/TASK-w3-l1u с базы, R8,
EXPERIMENT §5b. Бюджет $1,60. Затраты W3-L1u: $0,00, сборок ещё нет.

## Z-1: исходное свидетельство и диагностика

Job 85, `net-w2-05-k16-zst-control`, SHA `8e5ebe1d`:
`w2_k16_zst_stable` ожидался SUCCESS, фактически FAILED (171,40805 с,
cover 11/11). Четыре проверки без местоположения:
`dereference failure: pointer NULL`, `pointer invalid`,
`pointer outside object bounds`, `invalid integer address`.
`w2_k16_zst_network_short` ожидался SUCCESS, фактически OUT_OF_MEMORY.
Источник: `k1.sh summary 85`, `log-grep 85` (строки 2730–2750).
Классификация пока не установлена; эти данные не доказывают UB.

Подготовлен `w3-l1u-z1-split-01`: diagnostic, 16 GB, jobs=1,
18 отдельных гармоник, таймаут 1 мин на каждую:
stable/general N=0,1,2,7,8,15,16,17,31,32;
network N=8,9,12,13,17; отдельно volatile-чтение `()`, `sort4_stable<()>`,
`swap_if_less<()>`. Все ожидаются SUCCESS, чтобы не считать неизвестный
dereference-отказ заранее ожидаемым. Нет `stub_verified`, `should_panic`.

## U-1: только подготовка

Подготовлены `u1_general_8/16/32`, `u1_network_18/32`,
`u1_initialized_control` (ожидается SUCCESS),
`u1_uninitialized_control` (ожидается FAILED только с uninit-checks).
Все пути сортировки — u64, вариант А, comparator читает оба аргумента
через `read_volatile`, затем возвращает произвольный bool.

General идёт через stable-Freeze trait с реальным scratch `[MaybeUninit<u64>;48]`.
Cover фиксирует comparator-чтение по адресу внутри этого scratch.
Network идёт через unstable trait; cover нормального возврата при N>=18
свидетельствует о прохождении scratch→v copy (`smallsort.rs:369`);
это довод по потоку управления, не отдельный instrumented load-cover.
Network 8/16 не заявлены: там `no_merge` и чтения scratch нет.

U-1 не запускается до команды координатора и появления поля запроса
для `-Z uninit-checks`. E1 не закрывается. Контроль с намеренным UB
не предназначен для итогового обычного CI-набора (R8 L1-6).

## R7: решения и ограничения

- В поле lane `agent` допустимы только `k1-merge`, `k1-network`, `coordinator`;
  используется `k1-network`, фактический владелец — W3-L1u.
- Первый прогон ограничен 18×1 мин, чтобы оставить бюджет U-1.
  TIMEOUT не будет интерпретирован как классификация FAILED.
- Единственный `assume(false)` — разрешённый R6 §2 вариант А в заглушке
  `panic_on_ord_violation`. ZST не обязан достигать этой заглушки;
  нормальный возврат покрывается в каждой Z-1 гармонике.
- Вопрос об upstream-обращении остаётся решением владельца после классификации.
- Проверка схемы Python приняла 18 гармоник; `git diff --check` чист.
  Локально Kani/rustc/cargo не запускались. Lane/runtime-код не менялись.

## Review R9

REVIEW REQUEST ffd4250d2978a7f492113f8e67bacd0967ba5336

Файлы нового кода: `library/core/src/slice/sort/shared/smallsort/kani_k1/uninit.rs`,
подключение модуля в `kani_k1.rs`. Новые шаблоны Z-1 и U-1;
вердикта GO пока нет, результаты в зачёт не заявляются.
