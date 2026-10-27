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

R7-2: схема lane принимает только coordinator/k1-merge/k1-network; для W3-L1
используется agent=k1-merge, как идентификатор lane. Файлы lane не меняются.

REVIEW REQUEST 163cc95543b8dcc0f41a69188b70fe01e2a58360

Проверить smoke.rs: матрица типов, ожидаемые значения, десять cover.
Проверка запроса Python validate и git diff --check перед dispatch.

## Build 1 — L1-2

- request: `w3-l1-001-efficient-swap-c3`; commit `7bb4408c`.
- build: `70902589-d488-498d-9595-278e48013138`.
- `w3_efficient_swap_c3`: ожидается SUCCESS, 10/10 cover; фактический статус ещё не получен.
- measurement, timeout 10 мин; runner gcb-e2-standard-4.
- Перед dispatch budget: used $19,7668, reserved $0; после: резерв этого build $0,7760.
- Нарастающий фактический расход W3-L1: пока неизвестен; лимит $6,20.
- После уведомления: summary, peaks, check-tooling против 67a4b452;
  стоимость `(wall whole run / 60 + 8) × 0,0194`.
- Проверка запроса Python validate: accepted; git diff --check: без замечаний.

## R9 L1-2

Координатор в сессии: GO на 163cc95543b8dcc0f41a69188b70fe01e2a58360.
Зачёт после gate true build70902589. Summary/peaks/check-tooling запрошены.

## L1-3 — R7-3, разделение свойств без изменения контракта

Выбрано две гармоники на каждый тип u64/[u8;16]/[u8;85]:

- `w3_sort4_contract_{u64,b16,b85}`: proof_for_contract, прежний строгий
  comparator lt_u64/lt_b16/lt_b85, предварительно volatile читает оба полных значения.
- `w3_sort4_arbitrary_{u64,b16,b85}`: ordinary proof, comparator читает оба полных
  значения через read_volatile, затем возвращает kani::any(). Проверяется реальное
  тело и перестановка полных значений универсальным probe/count.

Ожидается SUCCESS всех шести, по одному cover нормального возврата на гармонику.
Точные исходные и отдельные выходные массивы [T;4]. Нет assume/any_where,
ручных cut, should_panic или stub_verified. В lane действует --no-assert-contracts;
ordinary proof не заявляет sortedness при произвольном comparator.
Контракт и runtime std не меняются. Для произвольного comparator свойство
безопасности/перестановки доказуемо независимо от строгого порядка; общая
формулировка proof_for_contract из задания остаётся частичной до изменения
безусловного ensures sortedness. Нельзя считать эти ordinary proofs контрактами
для произвольных comparator под stub_verified.

Редукции: входы и probe полные, ширина и значения не ограничены.
Контрактные гармоники используют строгий порядок по прежнему ключу (u64 >> 1;
первый байт массива), сохраняя произвольные остальные байты.
Граница времени 180 с — ориентир, measurement timeout 600 с. Фактические время,
пик и статус ещё не измерены.

REVIEW REQUEST ca32e652a138c649097de1ef4a6312f4080cf180

merge.rs: w3_sort4_read_args, w3_sort4_arbitrary и w3_sort4_cases.
Проверить разделение контракта/произвольного comparator, полные volatile-чтения,
универсальный probe/count и отсутствие предположения sortedness в ordinary proof.

## Build 1 — результат L1-2

`70902589-d488-498d-9595-278e48013138`: COMPLETE, gate true, measurement ok.
`smoke::w3_efficient_swap_c3`: ожидался SUCCESS, фактически SUCCESS,
0,08173547 с, failed 0/10, unreachable 0, covers 10/10.
Wall whole run 63,10 с; max RSS 1666764 KiB (kani-compiler),
суммарный sampled RSS peak 1893480 KiB (1,81 GiB), swap off, MACHINE 15,63 GiB.
Подготовка до verify 338 с. Стоимость по правилу волны:
(63,10 / 60 + 8) × $0,0194 = $0.175602.
Нарастающий расход W3-L1: $0.175602 / $6,20.
R9 GO получен. check-tooling подтвердил pool и равенство дерева lane базе;
ожидается окончание проверки привязанных SHA-256.

L1-2 check-tooling завершился с exit 0: все пять summary SHA-256 совпали
с базой 67a4b452. При R9 GO, gate true и covers10/10 L1-2 зачтён.

## Build 2 — L1-3

- request `w3-l1-002-sort4-cd2`; commit `3b4cfda2d084b66ccfb1756042440f653828c285`.
- build `9a62b6cf-b26c-41c7-a6a3-3f333f4fb402`.
- Шесть гармоник contract/arbitrary × u64/b16/b85, ожидается SUCCESS всех.
- measurement 6 × 10 мин, jobs1, gcb-e2-standard-4.
- Перед dispatch общий budget: used $19,9220, reserved $1,9400;
  после: used $19,9220, reserved $3,6860; резерв этого build $1,7460.
- Нарастающий фактический расход W3-L1 $0,175602 / $6,20;
  даже полный резерв build2 оставляет сумму в пределах доли.
- Python validate: accepted6; git diff --check без замечаний.
- После уведомления: последовательно summary, peaks, check-tooling
  (чтобы не скачивать одни артефакты одновременно), затем время/память/стоимость.
- Следующий пункт — L1-4 K9s N9..16, результат N17 сохранить.

## R9 L1-3 — GO

Координатор в сессии: GO на ca32e652a138c649097de1ef4a6312f4080cf180.
Разделение принято: proof_for_contract проверяет контракт со строгим порядком;
ordinary proof с kani::any() и чтением обоих аргументов через read_volatile
проверяет безопасность и перестановку полных значений универсальной пробой.
Заявление о сортированности sort4 относится только к строгому порядку.
При произвольном comparator заявляются только безопасность и перестановка.
Это принятая координатором формулировка L1-3; замечание R7-1 разрешено
разделением свойств без изменения контракта std.
Если [u8;85] превысит ориентир 180 с, фактическое время записывается как есть;
приёмочная граница measurement остаётся 600 с (в K-1 было 427 с).
Build9a62b6cf ещё не прочитан; зачёт — после summary/gate/check-tooling.
Новых dispatch нет, действующий watch ожидает завершения build2.
