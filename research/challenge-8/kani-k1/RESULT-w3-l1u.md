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

## Прогон Z-1 №1

Отправлен build `9d1cb848-61a4-4702-a1cd-beb96eb71b58`,
head `522e4750`, request `w3-l1u-z1-split-01`.
Перед отправкой budget: used $19,7668, reserved $0,7760 (проект).
После отправки новый резерв этой сборки $0,9312, в пределах доли $1,60.
Фактическая стоимость и нарастающий итог будут записаны по summary:
`(wall whole run / 60 + 8) × $0,0194`.
Следующий шаг: summary, peaks, check-tooling относительно `67a4b452`,
затем локализация FAILED только разрешёнными bounded log-командами.
Ожидание: `k1g.sh watch 9d1cb848-61a4-4702-a1cd-beb96eb71b58`.

## Обновление lane для U-1

Координатор разрешил merge базы с полем `"uninit_checks": true`
(только diagnostic / gcb-e2-standard-4); Kani сам включает ghost-state.
Выполнен `git merge origin/experiment/kani-k1-base-20261024`;
lane совпадает с `f5db92cc388b839ea24f75ae66e7d801a70b45fc`.
Для U-1 и последующих сборок check-tooling использует этот BASE;
для уже отправленного Z-1 остаётся прежний BASE `67a4b452`.
Команда координатора на U-1 получена, но новый build пока не отправляется:
Z-1 ещё QUEUED (проверено `k1g.sh summary`), допускается только один
незавершённый build. Размер первого U-1 запроса будет выбран после
фактической стоимости Z-1, в пределах общего лимита агента $1,60.
U-1 остаётся свидетельством вне CI; E1 не закрывает.

## R9 ffd4250d — вердикт координатора (записан координатором при смене исполнителя)

Записано координатором: Codex-сессия W3-L1u остановлена блоком OpenAI до записи вердикта. Агент продолжает в Claude Code.

R9 по ffd4250d (независимый ревьюер). Z-1: GO_WITH_NITS как диагностика. U-1: NO_GO в текущем виде — с uninit_checks не запускать до исправлений F2 и F3.

F1 (should-fix, Z-1). z1_* не воспроизводят гармонику job 85: там вход строился через crate::array::from_fn(|_| T::w2_value()), comparator — ManuallyDrop::new(read_volatile), scratch — [const {..}; 48], длина — any_where+match; у тебя литерал [(); N], голый read_volatile, [MaybeUninit::uninit(); 48] и фиксированная длина. Если все z1_* дадут SUCCESS, причина 4 dereference-отказов останется неизвестной. Добавь в следующий запрос исходную network::w2_k16_zst_stable с expect FAILED (expect_check — по тексту dereference-проверки) и примитив z1_from_fn_unit (array::from_fn::<(),N,_>).
F2 (should-fix, U-1). В u1_network_* scratch только пишется, а копия scratch→v (smallsort.rs:369) идёт через copy_nonoverlapping, то есть побайтово; v после возврата не читается. Если uninit-checks для copy только переносит shadow-состояние, SUCCESS будет пустым. После сортировки прочитай все v[i] через read_volatile (и в u1_general тоже).
F3 (should-fix, U-1). Контроли на одиночной MaybeUninit<u64> проверяют только поддержку volatile_load. Нужны отрицательные контроли той же раскладки: после uninit_general::<8> прочитать scratch[47] (ячейки 8..47 при N=8 не пишутся) — ожидать FAILED; MaybeUninit<[u64;32]> с cast: записать 0..17, прочитать 31 — FAILED (это и есть риск union-pointee из задания); парные положительные с записью той же ячейки — SUCCESS. expect_check — по тексту uninit-проверки.
F4 (nit). harness_timeout_minutes: 1 мало: в job 85 stable-семейство заняло 171 с на 10 длин, network — OOM. На N=31/32 и network-17 жди TIMEOUT; бери 5–10 мин для этих.
F5 (nit). Для локализации N=2 добавь z1_copy_unit и z1_merge2_unit (copy_nonoverlapping::<()> и bidirectional_merge на ZST), для 2..7 — insert_tail.
F6 (nit). Отрицательный uninit-контроль без -Z uninit-checks даёт SUCCESS — не включай его в запросы без uninit_checks:true; запиши это правило в RESULT.

Вариант (А), CD-2, массивы N, covers — в порядке. Запиши вердикт в RESULT, исправь, новый REVIEW REQUEST на U-1 после F2/F3.

Незавершённая сборка на момент смены: Z-1 `9d1cb848-61a4-4702-a1cd-beb96eb71b58` (WORKING). Дождаться, прочитать summary, записать, затем исправления F1–F6.

## Смена исполнителя: Claude Code (2026-10-27)

Вердикт R9 ffd4250d (выше) принят к исполнению: Z-1 — GO_WITH_NITS как диагностика,
U-1 — NO_GO до F2/F3. С этого места записи ведёт W3-L1u в Claude Code.

## Прогон Z-1 №1 — итог: COMPILE_ERROR, гармоники не исполнялись

Build `9d1cb848-61a4-4702-a1cd-beb96eb71b58`, head `522e4750`, request
`w3-l1u-z1-split-01`, gcb-e2-standard-4. Статус сборки FAILURE, сводка
COMPILE_ERROR, Kani exit 1, все 18 гармоник NOT_RUN. Причина — моя:
`uninit.rs` не импортировал `crate::kani` (E0433 «cannot find module or
crate `kani`» на каждом `#[kani::proof]`, все error-строки лога — только E0433
в uninit.rs). Ни о ZST, ни о U-1 этот прогон ничего не говорит.
Wall whole run 0:53,36; подготовка до verify 333 с; пик kani-compiler 1,23 GiB.
check-tooling против `67a4b452`: все строки ok (пул k1-standard4, файлы lane равны базе).
Стоимость: (53,36/60 + 8) × $0,0194 = **$0,1725**. Итог W3-L1u: **$0,1725 из $1,60**.

## Исправления F1–F6 (коммит этого раздела)

- Компиляция: добавлен `use crate::kani;` (как в network.rs/smoke.rs).
- F1: `z1f_stable_{2,8,16,32}` — вход job 85 на фиксированной длине:
  `crate::array::from_fn(|_| ())`, scratch `[const { MaybeUninit::uninit() }; 48]`,
  comparator `ManuallyDrop::new(read_volatile(..))`. От `w2_k16_zst_stable`
  отличается только символьной длиной (`any_where` + `match`).
  `z1_from_fn_unit_{2,32}` — только `array::from_fn::<(),N,_>` и volatile-чтение результата.
  Исходная `network::w2_k16_zst_stable` идёт в запрос с expect FAILED,
  expect_check `dereference failure`. Оговорка: в job 85 эти 4 проверки были
  без местоположения, а lane засчитывает expect_check только по проверке с
  местоположением, поэтому «expectation met» может остаться false и при FAILED;
  смотрю статус и тексты проверок, а не флаг.
- F4: таймаут гармоники 5 мин (один на запрос, так устроен lane).
- F5: `z1_copy_unit` (`copy_nonoverlapping::<()>` в scratch), `z1_merge2_unit`
  (`bidirectional_merge` на `[(); 2]`, паника нарушения порядка здесь не
  вырезана — если достижима, гармоника упадёт на ней), `z1_insert_tail_unit`.
- F2: `u1_general_*` и `u1_network_*` после сортировки читают все `v[i]`
  через `read_volatile`; scratch для general передаётся из гармоники по `&mut`.
- F3: `u1_general_8_tail_uninit` (после реальной сортировки N=8 читает
  `scratch[47]`, не записанную; ожидается FAILED) и пара
  `u1_general_8_tail_written` (та же ячейка сначала записана; SUCCESS);
  `u1_network_layout_tail_uninit` (`MaybeUninit<[u64;32]>` через cast-указатель,
  запись 0..17, чтение 31; FAILED) и пара `u1_network_layout_tail_written` (SUCCESS).
  expect_check для отрицательных — подстрока текста uninit-проверки Kani
  `Reading from an uninitialized pointer` (на pin 9461e07a:
  `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs:342`,
  «Undefined Behavior: Reading from an uninitialized pointer of type `…`»).
- F6, правило: отрицательные uninit-контроли (`u1_uninitialized_control`,
  `*_tail_uninit`) включаются только в запросы с `"uninit_checks": true`;
  без флага они дают SUCCESS и ничего не значат.

## Запрос Z-1 №2

`w3-l1u-z1-split-02`, diagnostic, 16 GB, jobs=1, таймаут 5 мин, 19 гармоник, без uninit_checks:
`network::w2_k16_zst_stable` (FAILED, `dereference failure`);
`z1_stable_{2,8,16,32}`, `z1f_stable_{2,8,16,32}`, `z1_from_fn_unit_{2,32}`,
`z1_copy_unit`, `z1_merge2_unit`, `z1_insert_tail_unit`, `z1_sort4_unit`,
`z1_swap_unit`, `z1_volatile_unit`, `z1_network_{9,17}` (все SUCCESS).
Логика деления: если `w2_k16_zst_stable` FAILED, а все `z1f_*` SUCCESS —
причина в символьной длине; если падают `z1f_*`, а `z1_stable_*` нет — во
входах job 85 (from_fn / const-scratch / ManuallyDrop), уточняет `z1_from_fn_unit`;
примитивы локализуют по функции.

R7: один таймаут на запрос; 5 мин × 19 = 95 мин — это верхняя граница
таймаутов, не ожидание. По job 85 (10 длин stable за 171 с) ожидаю
wall около 10–15 мин, ≈$0,35–0,45. Риск TIMEOUT/OOM — network-17 и N=32;
на них остаётся по 5 мин. Если фактическая стоимость оставит меньше ~$0,5,
U-1 сокращаю до длин 8 и 16 + контролей и записываю это.

U-1 код (F2/F3) входит в этот же коммит, чтобы его компиляцию проверила
сборка Z-1 №2; U-1 гармоники в запрос не включены (нет GO, нет uninit_checks).

Отправлен build `5aee04a2-8039-4cae-8160-e76a19ab9608`, head `f373880c`,
request `w3-l1u-z1-split-02`. Budget перед отправкой: used $20,0772,
reserved $2,7548 (проект); после — резерв с этой сборкой $5,1798.
Ожидание: `k1g.sh wait` фоном. check-tooling — против `f5db92cc`.

## Review R9 — U-1 после F2/F3

REVIEW REQUEST f373880ccd6344e2460caa18566eeb99f6befcf5

Новый код U-1: `uninit.rs` — `read_all`, `uninit_general(&mut scratch)`,
`u1_general_8_tail_{uninit,written}`, `u1_network_layout_tail_{uninit,written}`;
Z-1: `z1f_stable_*`, `z1_from_fn_unit_*`, `z1_copy_unit`, `z1_merge2_unit`,
`z1_insert_tail_unit`. Компиляция этого SHA проверяется сборкой `5aee04a2`.
