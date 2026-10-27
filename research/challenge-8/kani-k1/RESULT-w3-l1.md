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

## L1-4 — K9s, подготовка

`network.rs`: helper w3_k9s_indices<T,const N>, N9..17. Добавлены
w3_k9s_{u8,u64}_n9..n16 (16 proof_for_contract). Существующие
w2night_k9s_{u8,u64}_indices17 сохранены с тем же доменом и вызывают helper N17.
Массив ровно [T;N], различные произвольные позиции a/b, явная неизменность
остальных ячеек, прежний pure comparator w2p2_strict_less<T> как в K10.
Ledger: any_where ограничивают только a<N и b<N && b!=a; covers первых/последних
и внутренних пар подтверждают выполнимость. Нет stub_verified или ручных cut.
R7-4: cover конечной позиции сети выбирает 8 при N9..12 и 12 при N13..17;
нет cover внутри константно-ложной ветки. Всегда 7 cover на гармонику.
Ожидается SUCCESS всех. Не измерено; dispatch после разбора build2.
Максимум measurement 150 минут означает не больше 15 гармоник в одном запросе:
новые16 будут проверяться более чем одним build, без превышения доли агента.

## Build 2 — результаты L1-3

`9a62b6cf-b26c-41c7-a6a3-3f333f4fb402`: COMPLETE, gate false,
Kani exit1, measurement не принят. Причина — два TIMEOUT, не найденные FAILED checks.

| Гармоника | ожидался / факт | время, с | failed/total | unreachable | covers |
|---|---|---:|---|---:|---|
| w3_sort4_contract_u64 | SUCCESS / SUCCESS | 102,3778 | 0/354 | 44 | 1/1 |
| w3_sort4_arbitrary_u64 | SUCCESS / SUCCESS | 5,507581 | 0/164 | 36 | 1/1 |
| w3_sort4_contract_b16 | SUCCESS / SUCCESS | 106,54522 | 0/532 | 47 | 1/1 |
| w3_sort4_arbitrary_b16 | SUCCESS / SUCCESS | 21,07747 | 0/408 | 39 | 1/1 |
| w3_sort4_contract_b85 | SUCCESS / TIMEOUT | лимит600 | — | — | — |
| w3_sort4_arbitrary_b85 | SUCCESS / TIMEOUT | лимит600 | — | — | — |

Wall whole run1548,45 с, max RSS2621380 KiB (cbmc); суммарный sampled RSS peak
2859116 KiB (2,73 GiB), swap off. Это пики всего build, не отдельной гармоники.
Подготовка до verify342 с. Стоимость ($1548.45/60+8)×$0,0194 = $0.655866.
Нарастающий расход W3-L1: $0.831468 / $6,20.
R9 GO на исходный код остаётся; результаты при gate false не выдаются за общий PASS.

R7-5: [u8;85] зафиксирован как TIMEOUT при600 с, превышение ориентира180 с
раскрыто. Повтор с большим timeout не назначается: не закрывает CI-критерий,
а на очередь остаётся ограниченная доля. Четыре успешные гармоники повторяются
в следующем measurement для gate true без двух b85. Их код неизменен.
В тот же запрос войдут K9s u8N9..16 и обе N17 для регрессии общего helper.
Вторая половина K9s u64N9..16 пойдёт в следующий запрос. L1-5 ещё не запускался.

REVIEW REQUEST 924e2266932032ef5d9c3b7998510de25877a3e4

network.rs: w3_k9s_indices и16 новых proof_for_contract, сохранённые N17.
Проверить точный размер, различные символьные позиции, frame, прежний comparator,
cover позиции8/12 и отсутствие unreachable cover при N<13.

Build2 check-tooling: exit0, pool/lane и все5 SHA-256 совпали с базой67a4b452.
log-grep: CBMC timed out на строках2720/2748 (arbitrary_b85/contract_b85),
без FAILED check и без времени Verification Time для этих двух гармоник.

## Build 3 — L1-3 gate и L1-4 u8

- `w3-l1-003-sort4-gate-k9s-u8`, commit `b3db35dc87c1bcf98f0a3dc05b4cff727523b0c1`.
- build `d065eab6-9c2e-4cf5-9022-67b2589d18f7`.
- Четыре sort4 u64/b16; K9s u8N9..16; обе K9s N17. Ожидается SUCCESS14/14.
- measurement14×10 мин, jobs1, gcb-e2-standard-4; Python validate accepted14.
- Budget перед dispatch: used $21,6680, reserved $3,8218; после: reserved $7,1198.
  Резерв build3 $3,2980; расход W3-L1 $0,831468 плюс этот резерв — в пределах $6,20.
- После watch: summary, peaks, check-tooling, расход. Далее K9s u64N9..16,
  затем подготовленные L1-5 N13/14/15. L1-7 не запускать без отдельной команды.

## R9 L1-4 — GO; раскрытие L1-3 b85

Координатор в сессии: GO на 924e2266932032ef5d9c3b7998510de25877a3e4.
K9s N9..16: точный массив, различные символьные позиции, frame, прежний comparator,
выполнимые cover позиции8/12; N17 сохранены под прежними именами. Зачёт по gate.

По указанию координатора обе sort4 [u8;85] (contract/arbitrary) из build2
раскрываются как предел: TIMEOUT10 мин, без установленного контрпримера.
Прежние427 с в K-1 получены с другим comparator и не заменяют этот результат.
После основной очереди, только при остатке доли $6,20, допустим подбор
#[kani::solver(...)]; сейчас дополнительных прогонов b85 не назначено.
Build3 d065eab6 ожидается установленным watch; новых dispatch нет.
