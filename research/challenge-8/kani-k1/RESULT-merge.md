# RESULT K1-merge

Агент: K1-merge (фазы 1–6: Claude Code, Opus 5.5; фазы 7–9: Codex). Ветка `experiment/kani-k1-merge-20261024`. Норматив — [EXPERIMENT.md](EXPERIMENT.md), задание — [TASK-merge.md](TASK-merge.md).

## Ночь 2026-10-27

T0: 2026-10-26T20:49:12Z (`date -u`, UTC системных часов).

- Очередь: K-10 с GS N2, затем K-12a, затем K-14r.
- Новые dispatch до 2026-10-27T05:00:00Z; CircleCI, один job за раз,
  ожидание через `k1.sh watch`. База не вливается, lane не меняется.
- Передача: jobs 110/115 измерены; job 117 без summary, Kani не измерен.
  Первым повторяется пакет fallback N0/1 и GS u64/u8 N2 с новым request_id.
- Норматив NIGHT/TASK-night/R6-WAVE2/R5-WAVE1 прочитан с базовой ветки;
  check-tooling `9de80e0bec13896bb35a5e04e771448d9fe3931b`.

### N-D1 (R7): повтор K-10 GS N2

Повтор job 117 без изменения кода: `w2-merge-night-f01-gs2-001`,
fallback N0/1 (u64/u8), GS N2 по обоим типам; 4×10 мин, SUCCESS.
Proof N2..4 и R11 — job 110; ledger П2 без изменений. Review П2 ожидается.
Ночной dispatch 1; предшествующие попытки П2 6/40 (включая preflight отказ).
T0 уточнён по первому фактическому выводу `date -u` (20:49:12Z);
предыдущая запись 20:49:28Z была временем подготовки записи.

### Ночной preflight HTTP 429

Первый dispatch `b9f0566b` остановился на `git fetch` HTTP 429,
до обращения к CircleCI; job не создан. Push до этого прошёл.
Повтор — после паузы не менее 5 минут, без изменения запроса/гармоник.
Ночных preflight отказов 1; успешных ночных dispatch пока 0.

### Ночной job 129 — K-10 fallback N0/1, GS N2

Request `w2-merge-night-f01-gs2-001`, head `616fe21ec7d6f9ca3be4328efa9c9bf4876e383d`.
Успешный dispatch после паузы 5+ минут; ночных dispatch 1,
preflight отказов 1. Все четыре гармоники expected SUCCESS; статусы Kani,
время, память, covers, gate и check-tooling ожидают завершения.
Следующий шаг: `k1.sh summary 129` и check-tooling против `9de80e0b`.

REVIEW REQUEST 616fe21ec7d6f9ca3be4328efa9c9bf4876e383d

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код П2 `cd284852`, без изменений),
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`.
Открытый R9 П2: proof/R11 job 110 и GS N0/1 job 115;
job 129 пока без результата. Независимый зачёт не заявлен.

### Job 129 — измерения K-10

Head `616fe21ec7d6f9ca3be4328efa9c9bf4876e383d`, COMPLETE;
gate true, expectation met true, measurement ok true, Kani exit 0.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1813028 KiB, wall с компиляцией 49.84 с;
cgroup peak 1.93 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_fallback_len0` | SUCCESS / SUCCESS | 0.2016723 | 0/422 | 156 | 2/2 |
| `w2p2_fallback_len1` | SUCCESS / SUCCESS | 0.5887717 | 0/422 | 142 | 2/2 |
| `w2p2_gs_u64_len2` | SUCCESS / SUCCESS | 3.4337528 | 0/642 | 111 | 2/2 |
| `w2p2_gs_u8_len2` | SUCCESS / SUCCESS | 2.9606674 | 0/635 | 113 | 2/2 |

Полные counts covers сверены отдельно от gate. Fallback: cover каждого
типа; GS: D/S. Сортированность и перестановка по полной произвольной пробе;
R9 П2 ожидается, независимый зачёт не заявлен.

### N-D2 (R7): следующая ступень K-10

`w2-merge-night-f23-gs3-002`: fallback N2/3, GS u64/u8 N3;
4×10 мин, все expected SUCCESS. Код/ledger П2 без изменений.
Proof слияния N2..4 и R11 — job 110. После dispatch ночных jobs 2,
preflight отказов 1; суммарно с П2 до ночи: 7 jobs, 2 preflight отказа.

### Job 130 — K-10 fallback N2/3, GS N3

Request `w2-merge-night-f23-gs3-002`,
head `925dc59647aed14053f35cc327ee100d911763db`, COMPLETE;
gate true, expectation met true, measurement ok true, Kani exit 0.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1814572 KiB, wall с компиляцией 54.97 с;
cgroup peak 1.93 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_fallback_len2` | SUCCESS / SUCCESS | 1.510673 | 0/422 | 130 | 2/2 |
| `w2p2_fallback_len3` | SUCCESS / SUCCESS | 2.5104809 | 0/422 | 128 | 2/2 |
| `w2p2_gs_u64_len3` | SUCCESS / SUCCESS | 5.438099 | 0/642 | 109 | 2/2 |
| `w2p2_gs_u8_len3` | SUCCESS / SUCCESS | 4.3603926 | 0/635 | 111 | 2/2 |

Полные counts covers сверены отдельно от gate (fallback: оба типа;
GS: D/S). R9 П2 ожидается; независимый зачёт не заявлен.

REVIEW REQUEST 925dc59647aed14053f35cc327ee100d911763db

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код П2 `cd284852`, без изменений),
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: jobs 110/115/129/130,
summary и check-tooling ok каждого измеренного job.

### N-D3 (R7): K-10 GS N4 и fallback N4/5

`w2-merge-night-f45-gs4-003`: GS N4 u64/u8 и fallback N4/5,
4×10 мин, все expected SUCCESS. Fallback не использует заглушки;
GS N4 опирается на proof/R11 job 110. Код и ledger П2 без изменений.
После этого пакета — proof слияния N5/6 обоих типов до GS N5+.
После dispatch ночных jobs 3, preflight отказов 1;
с П2 до ночи: 8 jobs, 2 preflight отказа, 10/40 консервативных попыток.

### Job 131 — RUNNER_ERROR, checkout HTTP 429

Request `w2-merge-night-f45-gs4-003`,
head `1e3e89d0bfcf38dea76fecef7174dd57bc4e1c28`, CircleCI failed.
`k1.sh summary 131`: нет summary artifact. Lane-файлы совпадают с
`9de80e0bec13896bb35a5e04e771448d9fe3931b`; полный check-tooling
не завершён: нет summary.json. Kani status/time, память, covers и gate
отсутствуют, результатов четырём гармоникам не приписываю.

Read-only metadata CircleCI: 21:02:02.034Z–21:02:04.326Z, 2292 мс;
`Checkout code` failed за 835 мс. Ограниченная выборка ошибок checkout:
`remote: This request was rate-limited due to too many requests`,
`fatal: unable to access ... The requested URL returned error: 429`.
Это отказ checkout до Kani, не FAILED свойства и не ресурсный предел.
Первый metadata URL вернул 404; корректный project slug прочитан без
изменения lane, verifier-логи не использовались.

### N-D4 (R7): повтор после checkout 429

Код и набор четырёх гармоник сохраняются. Новый request
`w2-merge-night-f45-gs4-retry-004`, ожидания SUCCESS,
повтор dispatch не раньше 21:07:05Z (5 минут после отказа checkout).
Следующий 429 — пауза 10 минут, затем 15 минут по NIGHT.
После повтора ночных jobs 4, preflight отказов 1;
с П2 до ночи: 9 jobs, 2 preflight отказа, 11/40 консервативных попыток.

### R9 K-10 — GO_WITH_NITS (сообщение координатора)

Review набора `cd284852..1e3e89d0` — **GO_WITH_NITS**.
Проверены реальные тела insert_tail/sort4/sort8/insertion, перестановка
по произвольной пробе и R11 job 110. Прежние записи «R9 П2 ожидается»
остаются историческими; этот вердикт закрывает ожидание review кода.

**N-D5 (R7, R4): учёт доказанных длин обязателен.**
`stub_verified(bidirectional_merge)` сам не ограничивает вызов длинами,
на которых измерен proof контракта. Поэтому GS N засчитывается только
после измеренного `proof_for_contract` bm N **для обоих типов u64/u8**
в том же наборе коммитов. Для N16 обязательны также bm N8 обоих типов
(вложенный вызов из sort8_stable). Новые строки засчитываются после
проверки времени, gate, полных covers и check-tooling. SUCCESS GS сам
по себе не заменяет эти prerequisites. Таблица обновляется после jobs.

| GS N | Нужные длины bm и типы | Job proof_for_contract bm | Job GS / состояние |
|---:|---|---|---|
| 0 | слияние не вызывается | не требуется | 115, SUCCESS |
| 1 | слияние не вызывается | не требуется | 115, SUCCESS |
| 2 | 2, u64 и u8 | 110, SUCCESS обоих типов | 129, SUCCESS |
| 3 | 3, u64 и u8 | 110, SUCCESS обоих типов | 130, SUCCESS |
| 4 | 4, u64 и u8 | 110, SUCCESS обоих типов | 132, SUCCESS; 131 без измерений |
| 5 | 5, u64 и u8 | 136, SUCCESS обоих типов | 137, SUCCESS |
| 6 | 6, u64 и u8 | 136, SUCCESS обоих типов | 137, SUCCESS |
| 7 | 7, u64 и u8 | 140, SUCCESS обоих типов | 142, SUCCESS |
| 8 | 8, u64 и u8 | 140, SUCCESS обоих типов | 142, SUCCESS |
| 9 | 9, u64 и u8 | 149, SUCCESS обоих типов | 151, SUCCESS |
| 10 | 10, u64 и u8 | 151, SUCCESS обоих типов | 153, SUCCESS |
| 11 | 11, u64 и u8 | u8: 153; u64: 156; SUCCESS обоих | 158, SUCCESS |
| 12 | 12, u64 и u8 | 156, SUCCESS обоих типов | 158, SUCCESS |
| 13 | 13, u64 и u8 | 160, SUCCESS обоих типов | u8: 167 SUCCESS; u64: 161 TIMEOUT |
| 14 | 14, u64 и u8 | 160, SUCCESS обоих типов | 161: TIMEOUT обоих типов |
| 15 | 15, u64 и u8 | 165, SUCCESS обоих типов | 166: TIMEOUT обоих типов |
| 16 | 8 и 16, каждый u64 и u8 | 8: 140; 16: 165; SUCCESS обоих типов | 167, SUCCESS обоих типов |

**Ограничение R11:** job 110 проверяет только намеренное нарушение
клаузы `halves_sorted`; это не отрицательный контроль всех остальных
предусловий и не контроль области доказанных длин контракта.

#### Редукции

u8 засчитывается отдельно и не подменяет более широкие типы;
значения u64/u8 не ограничены, порядок по ключу `x >> 1` раскрыт в П2-D3.

Job 132: request `w2-merge-night-f45-gs4-retry-004`, head `b2346c5c`;
watch уже зарегистрирован. Новых dispatch и опроса состояния в ответ
на review не выполнялось. Следующий пакет после чтения job 132 —
proof bm N5/6 u64/u8, до GS N5+.

### Job 132 — K-10 GS N4, fallback N4/5

Request `w2-merge-night-f45-gs4-retry-004`,
head `b2346c5ce6a31cf7ffe92aa111bc1d89e5a74efb`, COMPLETE;
gate true, expectation met true, measurement ok true, Kani exit 0.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1812004 KiB, wall с компиляцией 55.21 с;
cgroup peak 1.92 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len4` | SUCCESS / SUCCESS | 7.232015 | 0/642 | 107 | 2/2 |
| `w2p2_gs_u8_len4` | SUCCESS / SUCCESS | 5.079927 | 0/635 | 109 | 2/2 |
| `w2p2_fallback_len4` | SUCCESS / SUCCESS | 3.3350081 | 0/422 | 126 | 2/2 |
| `w2p2_fallback_len5` | SUCCESS / SUCCESS | 6.260906 | 0/422 | 124 | 2/2 |

Полные counts covers сверены отдельно от gate. GS N4 имеет proof bm N4
обоих типов в job 110. R9 GO_WITH_NITS учтён в N-D5 и таблице.
Текущее измеренное покрытие K-10: GS u64/u8 N0..4, fallback u64/u8 N0..5;
строгий порядок по `x >> 1`, сортированность и перестановка по пробе.

### N-D6 (R7): prerequisites bm N5/6

`w2-merge-night-bm56-005`: четыре proof_for_contract bm N5/6,
каждая длина отдельно для u64/u8, expected SUCCESS, 4×10 мин.
Тела слияния реальные, ручных/verified stubs в этих proofs нет.
Предусловия предполагает proof_for_contract; normal-return cover
в `bm_len` обязателен у каждой гармоники. Код и ledger П2 без изменений.
До измерения обоих типов на длине N GS N5/6 не засчитывается.
После dispatch ночных jobs 5, preflight отказов 1;
с П2 до ночи: 10 jobs, 2 preflight отказа, 12/40 консервативных попыток.

### Job 134 — RUNNER_ERROR, checkout HTTP 429

Request `w2-merge-night-bm56-005`,
head `e4e6c98db789ec2c6a5526169e3159e5dea47ac2`, CircleCI failed.
`k1.sh summary 134`: нет summary artifact. Lane-файлы совпадают с
`9de80e0bec13896bb35a5e04e771448d9fe3931b`; полный check-tooling
не завершён: нет summary.json. Kani status/time, память, covers и gate
отсутствуют. Proof bm N5/6 обоих типов не измерены.

Read-only metadata CircleCI: 21:11:25.244Z–21:11:27.319Z, 2075 мс;
`Checkout code` failed за 620 мс. Ограниченная выборка ошибок checkout:
`remote: This request was rate-limited due to too many requests`,
`fatal: unable to access ... The requested URL returned error: 429`.
Это отказ до Kani, не FAILED контракта и не ресурсный предел.

### N-D7 (R7): повтор bm N5/6 после 10 минут

Сохраняю четыре proof_for_contract, код и ожидания SUCCESS.
Новый request `w2-merge-night-bm56-retry-006`.
По N-D4 следующий повтор после checkout 429 — с паузой не менее
10 минут: dispatch не раньше 21:21:28Z; следующий 429 потребует 15 минут.
Таблица R4 остаётся без proof job для N5/6; GS N5/6 не засчитываются.
После повтора ночных jobs 6, preflight отказов 1;
с П2 до ночи: 11 jobs, 2 preflight отказа, 13/40 консервативных попыток.

### Job 136 — proof bm N5/6 u64/u8

Request `w2-merge-night-bm56-retry-006`,
head `829960b8379c08d8c10ec94281e7158238a3cadf`, COMPLETE;
gate true, expectation met true, measurement ok true, Kani exit 0.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1752248 KiB, wall с компиляцией 282.22 с;
cgroup peak 1.86 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_bm_u64_len5` | SUCCESS / SUCCESS | 49.41238 | 0/442 | 100 | 1/1 |
| `w2p2_bm_u8_len5` | SUCCESS / SUCCESS | 45.19346 | 0/435 | 102 | 1/1 |
| `w2p2_bm_u64_len6` | SUCCESS / SUCCESS | 76.06198 | 0/442 | 98 | 1/1 |
| `w2p2_bm_u8_len6` | SUCCESS / SUCCESS | 59.05908 | 0/435 | 100 | 1/1 |

Полные covers normal-return сверены отдельно от gate, 1/1 у каждой
гармоники. Для N5 и N6 измерен контракт формулировки 1 обоих типов;
таблица R4 обновлена. GS на этих длинах ещё не измерен.

REVIEW REQUEST 829960b8379c08d8c10ec94281e7158238a3cadf

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код П2 без изменений, R9 GO_WITH_NITS),
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`.
Evidence: job 136 summary и check-tooling ok; prerequisites N5/6.

### N-D8 (R7): GS N5/6 после proof обоих типов

`w2-merge-night-gs56-007`: GS N5/6 отдельно u64/u8,
4×10 мин, expected SUCCESS. Stub только bidirectional_merge;
proof bm нужных длин обоих типов — job 136, R11 — job 110.
Код и ledger П2 без изменений. После dispatch ночных jobs 7,
preflight отказов 1; с П2 до ночи: 12 jobs, 2 preflight отказа,
14/40 консервативных попыток.

### Job 137 — GS N5/6 u64/u8

Request `w2-merge-night-gs56-007`,
head `e0bea0a3cd6ee6acf4040c923bd8993c63d3c3e3`, COMPLETE;
gate true, expectation met true, measurement ok true, Kani exit 0.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1871484 KiB, wall с компиляцией 93.97 с;
cgroup peak 2.03 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len5` | SUCCESS / SUCCESS | 12.706135 | 0/642 | 105 | 2/2 |
| `w2p2_gs_u8_len5` | SUCCESS / SUCCESS | 10.152405 | 0/635 | 107 | 2/2 |
| `w2p2_gs_u64_len6` | SUCCESS / SUCCESS | 18.840271 | 0/642 | 103 | 2/2 |
| `w2p2_gs_u8_len6` | SUCCESS / SUCCESS | 11.272275 | 0/635 | 105 | 2/2 |

Полные covers D/S сверены отдельно от gate. Proof bm N5/6 обоих типов —
job 136, R11 halves_sorted — job 110. Таблица R4 обновлена.
Измеренное покрытие K-10: GS u64/u8 N0..6, fallback u64/u8 N0..5.

### N-D9 (R7): prerequisites bm N7/8

`w2-merge-night-bm78-008`: четыре proof_for_contract bm N7/8,
отдельно u64/u8, expected SUCCESS, 4×10 мин; реальные тела слияния.
Код/ledger П2 без изменений, cover normal-return у каждой гармоники.
Proof N8 будет также prerequisite вложенного sort8_stable для GS N16.
Далее GS N7/8 обоих типов, затем fallback N6..9; длины выше текущего
покрытия заранее не засчитываются.
После dispatch ночных jobs 8, preflight отказов 1;
с П2 до ночи: 13 jobs, 2 preflight отказа, 15/40 консервативных попыток.

### N-D10 (R7): preflight HTTP 429 перед bm N7/8

Push `ebd3ccf4deefc2baa00aa71a6c2d39835d144c2e` прошёл; dispatch
`w2-merge-night-bm78-008` остановился на `git fetch`:
`RPC failed; HTTP 429`, `fatal: expected flush after ref listing`.
Обращения к CircleCI не было, job не создан, новых измерений нет.
Успешных ночных dispatch остаётся 7; ночных preflight отказов 2.
С П2 до ночи: 12 jobs, 3 preflight отказа, 15/40 попыток.

По N-D7 следующий повтор — через 15 минут. Отсчёт после фиксации
отказа: 2026-10-26T21:32:33Z;
новый dispatch не раньше 2026-10-26T21:47:33Z.
Набор гармоник и request_id сохраняю: исходный dispatch не создал job.
Следующая успешная попытка даст ночной job 8; с П2 до ночи —
13 jobs и 3 preflight отказа, 16/40 попыток.

### Job 140 — w2-merge-night-bm78-008

Head `d276514ab911e4b1e55294fa2761735522218ea0`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 1750164 KiB; wall с компиляцией 6:46.01.
Cgroup peak 2.05 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_bm_u64_len7` | SUCCESS / SUCCESS | 80.273415 | 0/442 | 96 | 1/1 |
| `w2p2_bm_u8_len7` | SUCCESS / SUCCESS | 68.49588 | 0/435 | 98 | 1/1 |
| `w2p2_bm_u64_len8` | SUCCESS / SUCCESS | 111.31704 | 0/442 | 94 | 1/1 |
| `w2p2_bm_u8_len8` | SUCCESS / SUCCESS | 89.60976 | 0/435 | 96 | 1/1 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные covers normal-return сверены отдельно от gate: 1/1 у каждой
гармоники. R4: N7 и N8 обоих типов измерены; таблица обновлена.
В строке GS N16 учтён proof bm N8 (job 140), bm N16 ещё не измерен.

### N-D11 (R7): GS N7/8

`w2-merge-night-gs78-009`: GS N7/8 отдельно u64/u8,
4×10 мин, expected SUCCESS; stub только bidirectional_merge.
Prerequisites обоих типов: bm N7/8 job 140, R11 halves_sorted job 110.
Код/ledger П2 без изменений. После GS N7/8 следующий пакет fallback N6..9.
После dispatch ночных jobs 9, preflight отказов 2;
с П2 до ночи: 14 jobs, 3 preflight отказа, 17/40 консервативных попыток.

### N-D12 (R7): preflight HTTP 429 перед GS N7/8

Push `14fc03b8` прошёл, dispatch `w2-merge-night-gs78-009`
остановился на `git fetch`: `RPC failed; HTTP 429`,
`fatal: expected flush after ref listing`. CircleCI job не создан.
Следующий dispatch после паузы 15 минут; отсчёт
2026-10-26T21:58:31Z, не раньше
2026-10-26T22:13:31Z.
Request_id и четыре гармоники сохраняются, код не меняется.
Ночных jobs остаётся 8, preflight отказов 3;
с П2 до ночи: 13 jobs, 4 preflight отказа, 17/40 попыток.
После успешного повтора: ночных jobs 9, суммарно 14 jobs,
4 preflight отказа и 18/40 попыток.

### Job 142 — w2-merge-night-gs78-009

Head `f31aca68ad36304e61aaef155bcfcc00b085f5ca`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 1864360 KiB; wall с компиляцией 2:39.77.
Cgroup peak 1.99 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len7` | SUCCESS / SUCCESS | 26.606129 | 0/642 | 101 | 2/2 |
| `w2p2_gs_u8_len7` | SUCCESS / SUCCESS | 15.950234 | 0/635 | 103 | 2/2 |
| `w2p2_gs_u64_len8` | SUCCESS / SUCCESS | 50.360867 | 0/642 | 97 | 2/2 |
| `w2p2_gs_u8_len8` | SUCCESS / SUCCESS | 22.257156 | 0/635 | 99 | 2/2 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные covers D/S сверены отдельно от gate: 2/2 у каждой гармоники.
R4: bm N7/8 обоих типов — job 140; R11 halves_sorted — job 110.
Таблица R4 обновлена. Измеренное покрытие K-10: GS u64/u8 N0..8,
fallback u64/u8 N0..5.

### N-D13 (R7): fallback N6..9

`w2-merge-night-f6to9-010`: четыре фиксированные длины fallback N6..9,
в каждой независимо выбирается u64/u8, expected SUCCESS, 4×10 мин.
Сортированность и перестановка по полной произвольной пробе;
реальные тела, без stubs. Код/ledger П2 без изменений.
После этого пакета — bm N9/10 обоих типов перед GS N9/10.
После dispatch ночных jobs 10, preflight отказов 3;
с П2 до ночи: 15 jobs, 4 preflight отказа, 19/40 консервативных попыток.

### Job 143 — fallback N6/7 SUCCESS, N8/9 TIMEOUT

Request `w2-merge-night-f6to9-010`,
head `7f726aaf1a2d4a80f944ae207eb0100f48ef9aaa`, COMPLETE;
gate false, expectation met false, measurement ok false, Kani exit 1.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1776192 KiB, wall с компиляцией 1374.91 с;
cgroup peak 1.89 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_fallback_len6` | SUCCESS / SUCCESS | 23.930975 | 0/422 | 122 | 2/2 |
| `w2p2_fallback_len7` | SUCCESS / SUCCESS | 109.05798 | 0/422 | 120 | 2/2 |
| `w2p2_fallback_len8` | SUCCESS / TIMEOUT | нет, лимит 600 с | нет | нет | нет |
| `w2p2_fallback_len9` | SUCCESS / TIMEOUT | нет, лимит 600 с | нет | нет | нет |

Полные covers N6/7 сверены отдельно: 2/2 (оба типа) у каждой гармоники.
Из-за общего gate false N6/7 пока только измеренные SUCCESS, без зачёта
пакета; повторятся в запросе без ожидаемых ресурсных отказов.
N8/9 — кандидаты расширенного слоя в объединённом виде u64/u8;
это не FAILED свойства. Индивидуальные память и Verification Time
таймаутов не измерены; приведён пик всего run с компиляцией.

### N-D14 (R7): разделить fallback N8 по типам

По П2-D5 делю combined N8 на две отдельные гармоники u64/u8,
с прежним helper, реальным телом, полной пробой и без редукции значений.
В каждой ожидается один normal-return cover. Добавлены только macro
`w2night_fallback_typed` и две инстанциации в своём merge.rs;
контракты/runtime/lane не меняются. Объединённая N9 пока не повторяется;
следующая длина по каждому типу выбирается после N8.

Следующий `w2-merge-night-bm9-f8typed-011`: proof bm N9 обоих типов
и две fallback N8, expected SUCCESS, 4×10 мин. GS N9 ждёт proof обоих
типов; fallback N6/7 ждут gate true в отдельном успешном пакете.
После dispatch ночных jobs 11, preflight отказов 3;
с П2 до ночи: 16 jobs, 4 preflight отказа, 20/40 консервативных попыток.

REVIEW REQUEST 92d4edd8291fc18acb8ef87599d4ebce801c5f2f

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`.
Изменение: typed fallback N8 отдельно u64/u8; прежний helper и свойства.
Evidence исходного пакета: job 143 summary и check-tooling ok;
измерения новых гармоник ожидаются в следующем job.

### Job 147 — bm N9 и fallback N8 по типам

Request `w2-merge-night-bm9-f8typed-011`,
head `6a4408ee9da5d3d5610ff0cdd847349821bd108f`, COMPLETE;
gate false, expectation met false, measurement ok false, Kani exit 1.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1727672 KiB, wall с компиляцией 1025.10 с;
cgroup peak 2.25 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_bm_u64_len9` | SUCCESS / SUCCESS | 115.29242 | 0/442 | 92 | 1/1 |
| `w2p2_bm_u8_len9` | SUCCESS / SUCCESS | 94.85038 | 0/435 | 94 | 1/1 |
| `w2night_fallback_u64_len8` | SUCCESS / TIMEOUT | нет, лимит 600 с | нет | нет | нет |
| `w2night_fallback_u8_len8` | SUCCESS / SUCCESS | 170.4768 | 0/244 | 62 | 1/1 |

Полные covers SUCCESS-строк сверены отдельно от gate: 1/1 у каждой.
Из-за общего gate false эти строки пока только измеренные SUCCESS,
без зачёта пакета. Таблица R4 N9 отмечает необходимость повторного gate.
R9 новых typed гармоник `92d4edd8` ожидается.

### N-D15 (R7): граница fallback u64 и подтверждающий пакет

Отдельная fallback u64 N8 остаётся TIMEOUT 600 с: кандидат расширенного
слоя (job 147), без нового прогона u64 N8+ в основном слое.
Это ресурсная граница измерения, не утверждение о невозможности
доказать большие длины. Fallback u8 N8 измерен SUCCESS 170.4768 с;
он повторится для gate true, затем u8 N9 — отдельной ступенью.

Сначала `w2-merge-night-bm9-f67-confirm-012`: bm N9 обоих типов
и fallback N6/7 (оба типа), четыре ранее успешные проверки,
expected SUCCESS, 4×10 мин. Цель — gate true для proof R4 N9 и
fallback N6/7 без соседней неуложившейся гармоники. Код не меняется,
новых assume/stub или редукций нет; все тела реальные.
После dispatch ночных jobs 12, preflight отказов 3;
с П2 до ночи: 17 jobs, 4 preflight отказа, 21/40 консервативных попыток.

### N-D16 (R7): ошибка validate перед job 148

Локальный validate запроса `w2-merge-night-bm9-f67-confirm-012`
вернул `REQUEST_INVALID: purpose must be one non-empty line of at most
300 characters`. Командная последовательность без `set -e` ошибочно
продолжила commit/push и dispatch; создан job 148 на `f7eef50d`.
Это ошибка подготовки запроса, не измерение Kani. Результат job 148
будет прочитан через summary; до него нового dispatch нет.

Исправление: purpose сокращён до допустимой строки, новый request_id
`w2-merge-night-bm9-f67-confirm-retry-013`; набор гармоник не меняется.
Все последующие validate/commit/push запускаются с `set -e`.
Следующий dispatch только после завершения job 148.
Ночных jobs фактически 12 (включая job 148), preflight отказов 3;
с П2 до ночи: 17 jobs, 4 preflight отказа, 21/40 попыток.
После исправленного dispatch: ночных jobs 13, суммарно 18 jobs,
4 preflight отказа, 22/40 попытки.

### Job 148 — REQUEST_INVALID, Kani не запускался

Head `f7eef50d981212303533141bdbfee5c20342ffb8`.
Summary: REQUEST_INVALID, build skipped, gate false,
expectation met false, measurement ok None, Kani exit None.
Проверок/гармоник, Verification Time и памяти нет; memcap MISSING.
Точная причина: `purpose must be one non-empty line of at most 300
characters`, запрос отклонён до запуска Kani. check-tooling ok против
`9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Исправленный запрос `w2-merge-night-bm9-f67-confirm-retry-013`
прошёл validate; запускается после прочтения этой сводки.

### Job 149 — w2-merge-night-bm9-f67-confirm-retry-013

Head `43f3911ca976de0fb62b72b1e2d9219c893a6042`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 1769432 KiB; wall с компиляцией 6:14.99.
Cgroup peak 2.27 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_bm_u64_len9` | SUCCESS / SUCCESS | 110.170074 | 0/442 | 92 | 1/1 |
| `w2p2_bm_u8_len9` | SUCCESS / SUCCESS | 90.03052 | 0/435 | 94 | 1/1 |
| `w2p2_fallback_len6` | SUCCESS / SUCCESS | 23.419857 | 0/422 | 122 | 2/2 |
| `w2p2_fallback_len7` | SUCCESS / SUCCESS | 108.76454 | 0/422 | 120 | 2/2 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные counts сверены отдельно от gate: bm N9 — 1/1 обоих типов;
fallback N6/7 — 2/2 каждой длины. Подтверждены ранее успешные строки
jobs 143/147 в отдельном пакете с gate true. Таблица R4 N9 обновлена.
Текущий зачёт K-10: GS u64/u8 N0..8; fallback u64/u8 N0..7.
Typed fallback u8 N8 из job 147 пока без gate true и R9 `92d4edd8`.

### N-D17 (R7): GS N9 и prerequisites bm N10

`w2-merge-night-gs9-bm10-014`: GS N9 u64/u8 с verified stub merge,
proof bm N10 u64/u8 с реальным телом; все expected SUCCESS, 4×10 мин.
R4 для GS N9: bm N9 обоих типов job 149, R11 halves_sorted job 110.
До proof N10 обоих типов GS N10 не запускается. Код/ledger без изменений.
После dispatch ночных jobs 14, preflight отказов 3;
с П2 до ночи: 19 jobs, 4 preflight отказа, 23/40 консервативных попыток.

### Job 151 — w2-merge-night-gs9-bm10-014

Head `513c611a43a58dddd9eaf4448efd73c75a665e8d`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 1798332 KiB; wall с компиляцией 6:40.41.
Cgroup peak 2.95 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len9` | SUCCESS / SUCCESS | 57.384148 | 0/642 | 95 | 2/2 |
| `w2p2_gs_u8_len9` | SUCCESS / SUCCESS | 27.243406 | 0/635 | 97 | 2/2 |
| `w2p2_bm_u64_len10` | SUCCESS / SUCCESS | 148.02586 | 0/442 | 90 | 1/1 |
| `w2p2_bm_u8_len10` | SUCCESS / SUCCESS | 120.920876 | 0/435 | 92 | 1/1 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные counts сверены отдельно от gate: GS N9 — 2/2 обоих типов;
bm N10 — 1/1 обоих типов. Таблица R4 обновлена; GS N9 опирается на
proof bm N9 job 149. Текущий зачёт K-10: GS u64/u8 N0..9,
fallback u64/u8 N0..7. Typed fallback u8 N8 ждёт gate true и R9.

### N-D18 (R7): GS N10 и подтверждение fallback u8 N8

`w2-merge-night-gs10-f8u8-bm11u8-015`: GS N10 u64/u8;
повтор успешной typed fallback u8 N8 из job 147 для gate true;
proof bm u8 N11 как следующая R4 prerequisite. Все expected SUCCESS,
4×10 мин. R4 GS N10: proof bm N10 обоих типов job 151;
R11 halves_sorted job 110. До proof bm N11 обоих типов GS N11 нет.
Код и ledger без изменений; R9 typed fallback `92d4edd8` ожидается.
После dispatch ночных jobs 15, preflight отказов 3;
с П2 до ночи: 20 jobs, 4 preflight отказа, 24/40 консервативных попытки.

### Job 153 — w2-merge-night-gs10-f8u8-bm11u8-015

Head `5ba8ea87f652f855e079f7f13751bed3c14e6e51`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 1802620 KiB; wall с компиляцией 7:50.27.
Cgroup peak 3.05 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len10` | SUCCESS / SUCCESS | 96.23121 | 0/642 | 93 | 2/2 |
| `w2p2_gs_u8_len10` | SUCCESS / SUCCESS | 41.09707 | 0/635 | 95 | 2/2 |
| `w2night_fallback_u8_len8` | SUCCESS / SUCCESS | 166.67104 | 0/244 | 62 | 1/1 |
| `w2p2_bm_u8_len11` | SUCCESS / SUCCESS | 123.60547 | 0/435 | 90 | 1/1 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные counts сверены отдельно от gate: GS N10 — 2/2 каждого типа;
typed fallback u8 N8 и bm u8 N11 — 1/1 каждый.
Таблица R4 обновлена. GS N10 опирается на proof bm N10 обоих типов job 151.
Fallback u8 N8 теперь имеет gate true; R9 кода `92d4edd8` ещё ожидается,
поэтому независимый зачёт typed N8 пока не заявлен.
Текущий зачёт GS u64/u8 N0..10, fallback u64/u8 N0..7;
дополнительно измерен с gate true fallback u8 N8.

### N-D19 (R7): завершить prerequisites bm N11/12

`w2-merge-night-bm11u64-bm12-016`: bm u64 N11 и bm N12 u64/u8,
три proof_for_contract с реальным телом, expected SUCCESS, 3×10 мин.
Bm u8 N11 уже измерен job 153. До успешных proofs обоих типов
на соответствующей длине GS N11/12 не засчитываются.
Код и ledger без изменений; следующий пакет — GS N11/12 обоих типов.
После dispatch ночных jobs 16, preflight отказов 3;
с П2 до ночи: 21 jobs, 4 preflight отказа, 25/40 консервативных попыток.

### Job 156 — w2-merge-night-bm11u64-bm12-016

Head `47208500185f7f6266107f6cbcc67cbd2b6307cf`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 2134252 KiB; wall с компиляцией 9:27.36.
Cgroup peak 3.18 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_bm_u64_len11` | SUCCESS / SUCCESS | 161.11435 | 0/442 | 88 | 1/1 |
| `w2p2_bm_u64_len12` | SUCCESS / SUCCESS | 198.20973 | 0/442 | 86 | 1/1 |
| `w2p2_bm_u8_len12` | SUCCESS / SUCCESS | 163.2861 | 0/435 | 88 | 1/1 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные covers normal-return сверены отдельно от gate: 1/1 у каждой.
Таблица R4 обновлена: N11 обоих типов (u8 job 153, u64 job 156),
N12 обоих типов (job 156). Bm u64 N12: 198.20973 с >180 с,
но <600 с; по CD-6 цель 180 с — ориентир, measurement основного слоя.
Гармоника уже фиксирована по длине и типу. macOS здесь не измерен.

### N-D20 (R7): GS N11/12 после обоих proofs

`w2-merge-night-gs11to12-017`: GS N11/12 отдельно u64/u8,
expected SUCCESS, 4×10 мин. Verified stub только bidirectional_merge;
R4 N11: proofs jobs 153/156, N12: job 156; R11 halves_sorted job 110.
Код/ledger без изменений; следующий пакет — proof bm N13/14 обоих типов.
После dispatch ночных jobs 17, preflight отказов 3;
с П2 до ночи: 22 jobs, 4 preflight отказа, 26/40 консервативных попыток.

### Job 158 — w2-merge-night-gs11to12-017

Head `7144cac5063999a8fd8055911bbd8c8664d940ea`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 2139796 KiB; wall с компиляцией 10:58.94.
Cgroup peak 3.16 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len11` | SUCCESS / SUCCESS | 167.2745 | 0/642 | 91 | 2/2 |
| `w2p2_gs_u8_len11` | SUCCESS / SUCCESS | 53.684166 | 0/635 | 93 | 2/2 |
| `w2p2_gs_u64_len12` | SUCCESS / SUCCESS | 256.761 | 0/642 | 89 | 2/2 |
| `w2p2_gs_u8_len12` | SUCCESS / SUCCESS | 138.90129 | 0/635 | 91 | 2/2 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные covers D/S сверены отдельно от gate: 2/2 каждой гармоники.
R4: bm N11 jobs 153/156, bm N12 job 156, оба типа; таблица обновлена.
GS u64 N12: 256.761 с >180 с, но <600 с, основной слой по CD-6;
macOS здесь не измерен. Зачёт GS u64/u8 N0..12, fallback u64/u8 N0..7;
fallback u8 N8 имеет gate true job 153, R9 typed-кода ещё ожидается.

### N-D21 (R7): prerequisites bm N13/14

`w2-merge-night-bm13to14-018`: четыре proof_for_contract bm N13/14,
каждая длина отдельно u64/u8, expected SUCCESS, 4×10 мин.
Тела реальные, код/ledger без изменений. До успешного proof обоих типов
на соответствующей длине GS N13/14 не засчитываются.
Следующий пакет — GS N13/14 обоих типов.
После dispatch ночных jobs 18, preflight отказов 3;
с П2 до ночи: 23 jobs, 4 preflight отказа, 27/40 консервативных попыток.

### Job 160 — w2-merge-night-bm13to14-018

Head `b73d031114d08780734ca233f98416f58e7dc220`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 2490172 KiB; wall с компиляцией 16:54.29.
Cgroup peak 3.74 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_bm_u64_len13` | SUCCESS / SUCCESS | 230.07814 | 0/442 | 84 | 1/1 |
| `w2p2_bm_u8_len13` | SUCCESS / SUCCESS | 175.57376 | 0/435 | 86 | 1/1 |
| `w2p2_bm_u64_len14` | SUCCESS / SUCCESS | 350.00134 | 0/442 | 82 | 1/1 |
| `w2p2_bm_u8_len14` | SUCCESS / SUCCESS | 210.344 | 0/435 | 84 | 1/1 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные normal-return covers сверены отдельно от gate: 1/1 каждой.
Таблица R4: bm N13/14 обоих типов — job 160. Времена 230.07814,
350.00134 и 210.344 с превышают ориентир 180 с, но все <600 с;
по CD-6 основной слой. Гармоники уже фиксированы по длине и типу.

### N-D22 (R7): GS N13/14

`w2-merge-night-gs13to14-019`: четыре GS N13/14, отдельно u64/u8,
expected SUCCESS, 4×10 мин. Verified stub только bidirectional_merge;
R4 — bm N13/14 обоих типов job 160, R11 halves_sorted job 110.
Код/ledger без изменений. Следующий пакет — proof bm N15/16 обоих типов.
После dispatch ночных jobs 19, preflight отказов 3;
с П2 до ночи: 24 jobs, 4 preflight отказа, 28/40 консервативных попыток.

### Job 161 — GS N13/14, ресурсные границы

Request `w2-merge-night-gs13to14-019`,
head `a5ac8e5a6c15e95756ec202f902ff6655c8c87bb`, COMPLETE;
gate false, expectation met false, measurement ok false, Kani exit 1.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1999524 KiB, wall с компиляцией 2012.24 с;
cgroup peak 3.25 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len13` | SUCCESS / TIMEOUT | нет, лимит 600 с | нет | нет | нет |
| `w2p2_gs_u8_len13` | SUCCESS / SUCCESS | 170.73291 | 0/635 | 89 | 2/2 |
| `w2p2_gs_u64_len14` | SUCCESS / TIMEOUT | нет, лимит 600 с | нет | нет | нет |
| `w2p2_gs_u8_len14` | SUCCESS / TIMEOUT | нет, лимит 600 с | нет | нет | нет |

Полные covers u8 N13 сверены отдельно от gate: 2/2 D/S. Общий gate false,
поэтому u8 N13 пока измеренный SUCCESS без зачёта пакета; повторится
отдельно от ресурсных отказов. Остальные три — кандидаты расширенного
слоя, не FAILED свойств. Память таймаутов индивидуально не измерена;
приведён пик всего run с компиляцией. Таблица R4 обновлена.

### N-D23 (R7): продолжить к порогу 16

`w2-merge-night-bm15to16-020`: proof bm N15/16 обоих типов,
expected SUCCESS, 4×10 мин, реальные тела; код/ledger без изменений.
После proofs — GS N15/16. N16 имеет другую ветку presort (sort8),
поэтому TIMEOUT на N13/14 не переношу на неё. Для GS N16 дополнительно
нужен bm N8 обоих типов: job 140 уже есть.

По NIGHT таймауты N13/14 передаются кандидатами расширенного слоя.
Разделение GS по D/S — допустимая альтернатива; в этой очереди отложено
ради измерения порога N16, оставшейся fallback u8 и задач K-12a/K-14r.
Длины без измерений не объявляются ресурсно непроходимыми.
После dispatch ночных jobs 20, preflight отказов 3;
с П2 до ночи: 25 jobs, 4 preflight отказа, 29/40 консервативных попыток.

### Job 165 — w2-merge-night-bm15to16-020

Head `de7f36c2a58dbe15fe04e781ff8b99babf13218e`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 2895656 KiB; wall с компиляцией 24:20.67.
Cgroup peak 4.09 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_bm_u64_len15` | SUCCESS / SUCCESS | 365.36026 | 0/442 | 80 | 1/1 |
| `w2p2_bm_u8_len15` | SUCCESS / SUCCESS | 229.3018 | 0/435 | 82 | 1/1 |
| `w2p2_bm_u64_len16` | SUCCESS / SUCCESS | 549.5681 | 0/442 | 78 | 1/1 |
| `w2p2_bm_u8_len16` | SUCCESS / SUCCESS | 268.76114 | 0/435 | 80 | 1/1 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные normal-return covers сверены отдельно от gate: 1/1 каждой.
Все времена <600 с, основной слой по CD-6; максимум u64 N16 549.5681 с.
MacOS не измерен. Таблица R4 обновлена: bm N15/16 обоих типов job 165,
дополнительный bm N8 для GS N16 job 140.
Итого prerequisites bm N2..16 обоих типов измерены в текущем наборе
коммитов; это не переносит зачёт на ещё не прошедшие GS длины.

### N-D24 (R7): GS N15/16

`w2-merge-night-gs15to16-021`: GS N15/16 отдельно u64/u8,
expected SUCCESS, 4×10 мин. Verified stub только bidirectional_merge.
R4 N15: bm N15 обоих типов job 165; N16: bm N16 job 165 и bm N8 job 140,
каждая длина обоих типов. R11 halves_sorted job 110.
Код/ledger без изменений. После этого — подтверждение успешных строк
из пакетов с gate false, последняя ступень fallback u8, затем K-12a.
После dispatch ночных jobs 21, preflight отказов 3;
с П2 до ночи: 26 jobs, 4 preflight отказа, 30/40 консервативных попыток.

### Job 166 — GS N15 TIMEOUT, GS N16 SUCCESS

Request `w2-merge-night-gs15to16-021`,
head `e94ce24e75ae4fe6c932f672f743b4721d52122b`, COMPLETE;
gate false, expectation met false, measurement ok false, Kani exit 1.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 3516064 KiB, wall с компиляцией 1552.72 с;
cgroup peak 5.89 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len15` | SUCCESS / TIMEOUT | нет, лимит 600 с | нет | нет | нет |
| `w2p2_gs_u8_len15` | SUCCESS / TIMEOUT | нет, лимит 600 с | нет | нет | нет |
| `w2p2_gs_u64_len16` | SUCCESS / SUCCESS | 218.22272 | 0/642 | 74 | 2/2 |
| `w2p2_gs_u8_len16` | SUCCESS / SUCCESS | 91.0657 | 0/635 | 76 | 2/2 |

Полные covers GS N16 сверены отдельно от gate: 2/2 D/S каждого типа.
Общий gate false; N16 пока измеренный SUCCESS без зачёта пакета.
GS N15 обоих типов — кандидаты расширенного слоя, не FAILED свойств.
Пик приведён для всего run с компиляцией, индивидуальных пиков нет.
Таблица R4 обновлена. Отличие результата N16 от N13..15 подтверждает,
что ресурсные выводы нельзя переносить через порог presort.

### N-D25 (R7): подтвердить успешные GS перед закрытием K-10

`w2-merge-night-gs13u8-gs16-confirm-022`: GS u8 N13 (job 161 SUCCESS)
и GS N16 u64/u8 (job 166 SUCCESS), expected SUCCESS, 3×10 мин.
R4 N13: bm N13 обоих типов job 160; N16: bm N16 job 165 и bm N8 job 140,
обе длины обоих типов. R11 halves_sorted job 110; код/ledger без изменений.
Ресурсные отказы в этот пакет не включаются. После него fallback u8 N9
проверяется отдельным job, чтобы её возможный таймаут не отменил gate GS.
Затем K-10 закрывается по измеренным длинам и кандидатам расширенного слоя,
следующая задача очереди — K-12a.
После dispatch ночных jobs 22, preflight отказов 3;
с П2 до ночи: 27 jobs, 4 preflight отказа, 31/40 консервативных попытка.

### Job 167 — w2-merge-night-gs13u8-gs16-confirm-022

Head `e9a75bf034dc27271a19f81181ac90f6f00ce1e7`, COMPLETE.
- gate: True; expectation met: True; measurement ok: True; Kani exit 0
Run: max RSS 3452460 KiB; wall с компиляцией 9:09.84.
Cgroup peak 5.27 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u8_len13` | SUCCESS / SUCCESS | 182.7535 | 0/635 | 89 | 2/2 |
| `w2p2_gs_u64_len16` | SUCCESS / SUCCESS | 228.04008 | 0/642 | 74 | 2/2 |
| `w2p2_gs_u8_len16` | SUCCESS / SUCCESS | 92.90118 | 0/635 | 76 | 2/2 |

check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полные covers D/S сверены отдельно от gate: 2/2 каждой гармоники.
Успешные строки jobs 161/166 подтверждены с gate true; таблица R4
обновлена. GS u64: N0..12 и N16; GS u8: N0..13 и N16.
Промежуточные TIMEOUT не закрываются успешной точкой N16.
R4 N13: bm обоих типов job 160; N16: bm N16 job 165 и bm N8 job 140.
Времена >180 с принимаются по CD-6 как основной слой <600 с;
macOS здесь не измерен.

### N-D26 (R7): fallback u8 N9 отдельной гармоникой

`w2-merge-night-f9u8-023`: одна typed fallback u8 N9,
expected SUCCESS, 10 мин. Добавлена одна инстанциация прежнего macro
в merge.rs; helper, реальное тело, полные значения и проба сохранены.
Новых assume/stub и редукций нет, ожидается один normal-return cover.
N8 u8 имеет SUCCESS с gate true в job 153; R9 typed-кода ещё ожидается.
При TIMEOUT N9 — кандидат расширенного слоя, рост fallback u8 прекращается
и K-10 закрывается по измеренным границам; при SUCCESS следующая длина.
После dispatch ночных jobs 23, preflight отказов 3;
с П2 до ночи: 28 jobs, 4 preflight отказа, 32/40 консервативных попытки.

REVIEW REQUEST 88aba4470ce8565f4d6f3a4e1e4c0e45da21fd42

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`.
Typed fallback macro и инстанциации N8 u64/u8, N9 u8.
Предыдущий запрос кода `92d4edd8` остаётся без полученного вердикта.
Evidence: job 147 (u64 N8 TIMEOUT, u8 N8 SUCCESS при gate false),
job 153 (u8 N8 SUCCESS, gate true), summaries и check-tooling ok.
Новая N9 u8 ещё не измерена; код helper/контрактов/runtime не менялся.

### R9 typed fallback — GO (сообщение координатора)

Review `92d4edd8` и `88aba447` — **GO**, замечаний нет.
`w2night_fallback_typed` — одна ветка проверенного шаблона
`w2p2_fallback_fixed`: тот же helper `w2p2_fallback_len`, unwind(34),
свойства и реальное тело без изменений. Принят как экземпляр шаблона.

Fallback u8 N8 засчитан: job 153 SUCCESS, cover 1/1, gate true,
check-tooling ok. Fallback u8 N9 будет засчитан только после gate true
и остальных критериев завершённого job 168. Fallback u64 N8 TIMEOUT
job 147 остаётся кандидатом расширенного слоя.
Исторические записи ожидания R9 закрыты этим вердиктом.
Текущий зачёт fallback: u64 N0..7, u8 N0..8.
GS: u64 N0..12 и N16; u8 N0..13 и N16.
Job 168 под ранее зарегистрированным watch; новых dispatch и опроса
состояния в ответ на review не выполнялось. Очередь продолжается
после его уведомления: оставшийся K-10, затем K-12a и K-14r.

### Job 168 — fallback u8 N9 TIMEOUT

Request `w2-merge-night-f9u8-023`,
head `6cbb74043f5cdb3a77deaa6056cf3d44f2ad9521`, COMPLETE;
expected SUCCESS / actual TIMEOUT, лимит 600 с.
Gate false, expectation met false, measurement ok false, Kani exit 1.
Verification Time, checks и covers не получены.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1608012 KiB, wall с компиляцией 639.77 с;
cgroup peak 1.81 GiB, ENFORCED 13 GiB, OOM 0, swap off.
Одна гармоника: пик run — верхняя оценка, включает компиляцию.
Typed fallback u8 N9 — кандидат расширенного слоя; рост прекращён.

### Итог ночного K-10

| Маршрут | Тип | SUCCESS с gate true, covers и check-tooling ok | TIMEOUT 600 с | Не измерено отдельно |
|---|---|---|---|---|
| general D / stable-Freeze S | u64 | N0..12 и N16 | N13/14 job 161, N15 job 166 | — |
| general D / stable-Freeze S | u8 | N0..13 и N16 | N14 job 161, N15 job 166 | — |
| fallback | u64 | N0..7 | typed N8 job 147 | typed N9..16 |
| fallback | u8 | N0..8 | typed N9 job 168 | typed N10..16 |

Combined fallback N8/9 (оба типа в одной гармонике) TIMEOUT job 143
также остаются кандидатами расширенного слоя. Новых FAILED свойств
не было. Пропуски и таймауты не закрываются успешной точкой N16.
Bm proof_for_contract формулировки 1: все N2..16 обоих типов измерены
в том же наборе коммитов; таблица GS → bm → job выше сохраняет R4,
включая bm N8 для GS N16. R11 job 110 проверяет только halves_sorted.
R9 GS-кода — GO_WITH_NITS, typed fallback — GO (оба вердикта записаны).

Свойства: сортированность по строгому слабому порядку `x >> 1` и
перестановка полных значений по одной произвольной пробе. Значения
u64/u8 не редуцированы; u8 не заменяет более широкие типы. General
вызывается напрямую, stable-Freeze через trait со scratch 48.
Публичный unstable entrypoint u64/u8 выбирает network (другой агент).
Кредит ограничен фиксированными длинами и инстанциациями; macOS,
uninit/aliasing/reference-validity/unwind здесь не проверялись.

K-10 ночной очереди завершён по измеренным границам; Cloud Build
агент не запускал. Следующая задача по NIGHT — K-12a.

### N-D27 (R7): K-12a, реальные bm u8 N20/24

Добавлены две инстанциации прежнего `w2p2_bm_fixed` с N20 и N24:
proof_for_contract с реальным телом bidirectional_merge, без stubs.
Контракт формулировки 1 проверяет сортированность и перестановку по пробе;
requires предполагает proof_for_contract, normal-return cover в bm_len.
Полные символические u8 и прежний lt_u8, unwind(34), helpers шириной 32.
Контракты/runtime/lane не меняются, новых assume или редукций нет.

Прогоны отдельно: один diagnostic ×30 минут на job, чтобы соблюдать
потолок 40 минут таймаутов на запрос. Первый
`w2-merge-night-k12a-u8n20-024`, expected SUCCESS. Затем N24 независимо
от исхода N20. Время/память записываются как диагностические данные,
формальный зачёт основного слоя по этим jobs не заявляется.
После dispatch ночных jobs 24, preflight отказов 3;
с П2 до ночи: 29 jobs, 4 preflight отказа, 33/40 консервативных попытки.

REVIEW REQUEST b8849eefd9be4a9169ad904edd2c15e9244c2501

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`.
K-12a: две инстанциации прежнего proof_for_contract template, N20/24 u8;
только diagnostic, новых утверждений proof credit нет. Итог K-10 выше
опирается на уже проверенный код и указанные jobs/gates/covers.

### R9 K-12a — GO (сообщение координатора)

Review `b8849eef` — **GO**. K-12a N20/24 — экземпляры проверенного
`w2p2_bm_fixed`: proof_for_contract, unwind(34) достаточен для N24,
в bm_len нет ограничения N<=16. Diagnostic и отсутствие proof credit
подтверждены reviewer.

Условия этой серии: **u8, CircleCI circleci-linux-large, cgroup 13 GiB,
таймаут 30 минут на гармонику, kind diagnostic**. Время и память
фиксируются как данные, без зачёта основного слоя.
Для контекста только по сообщению координатора: WX-ext измеряет
**u64 на GCB 32 GB**; N20 SUCCESS за 3461 с, N24 измеряется.
Это другой тип и lane; данные WX-ext здесь самостоятельно не проверены
и не заменяют собственные K-12a измерения u8.
Job 169 (u8 N20) под watch; новых dispatch и опроса состояния
в ответ на review не выполнялось. После него — u8 N24 тем же lane.

### Job 169 — w2-merge-night-k12a-u8n20-024

Head `eae6349f8763743b8314aa6690b4ed7e5a85abfc`, COMPLETE.
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
Run: max RSS 2990232 KiB; wall с компиляцией 9:33.29.
Cgroup peak 4.72 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2night_k12a_bm_u8_len20` | SUCCESS / SUCCESS | 528.8255 | 0/435 | 72 | 1/1 |

Условия: **u8, CircleCI circleci-linux-large, cgroup 13 GiB,
kind diagnostic, таймаут 30 минут**. Реальное тело слияния, без stubs.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полный normal-return cover сверён отдельно от gate: 1/1.
Сортированность и перестановка контракта: 0/435 failed checks.
528.8255 с <600 с, но kind diagnostic / measurement ok None:
это диагностические данные, proof credit основного слоя не заявляется.
Одна гармоника: max RSS run 2990232 KiB (2.85 GiB), cgroup peak 4.72 GiB;
обе оценки включают компиляцию, не отдельный пик verifier.

### N-D28 (R7): K-12a u8 N24

`w2-merge-night-k12a-u8n24-025`: одна гармоника N24,
expected SUCCESS, diagnostic 30 минут. Тот же проверенный шаблон,
реальное тело bm, формулировка 1, полные u8, без новых assume/stub.
R9 `b8849eef` — GO. Условия u8/CircleCI/13 GiB сохранены;
следом K-14r по ночной очереди. Никакого переноса u8 на u64/GCB нет.
После dispatch ночных jobs 25, preflight отказов 3;
с П2 до ночи: 30 jobs, 4 preflight отказа, 34/40 консервативных попытки.

### Job 170 — w2-merge-night-k12a-u8n24-025

Head `f5b0403b846800ddda5a1816c01de2509a4e1b94`, COMPLETE.
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
Run: max RSS 3607404 KiB; wall с компиляцией 18:00.38.
Cgroup peak 5.62 GiB; ENFORCED, limit 13.00 GiB; OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2night_k12a_bm_u8_len24` | SUCCESS / SUCCESS | 1040.0021 | 0/435 | 64 | 1/1 |

Условия: **u8, CircleCI circleci-linux-large, cgroup 13 GiB,
kind diagnostic, таймаут 30 минут**. check-tooling ok против
`9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Полный normal-return cover сверён: 1/1; 0/435 failed checks.
1040.0021 с >600 с, но <1800 с; diagnostic, measurement ok None,
proof credit основного слоя не заявляется.
Одна гармоника: max RSS 3607404 KiB (3.44 GiB), cgroup peak 5.62 GiB;
оба пика включают компиляцию, не отдельный пик verifier.

### Итог K-12a — диагностические данные

| u8 / CircleCI 13 GiB | Job | actual | Verification Time, с | max RSS run, KiB | cgroup peak run | cover |
|---|---:|---|---:|---:|---|---|
| реальное bm N20 | 169 | SUCCESS | 528.8255 | 2990232 | 4.72 GiB | 1/1 |
| реальное bm N24 | 170 | SUCCESS | 1040.0021 | 3607404 | 5.62 GiB | 1/1 |

Оба gate true, check-tooling ok; R9 шаблонов GO. Kind diagnostic,
данные без proof credit. Сортированность и перестановка формулировки 1,
полные символические u8, порядок x >> 1, без stubs. Это не переносится
на u64; сообщение о WX-ext u64/GCB 32 GB приведено отдельно выше.
K-12a завершён, следующая задача очереди — K-14r.

### N-D29 (R7): K-14r, модель и порядок

Тип `W2NightDrop`: full u64 key, уникальный u8 tag, non-Copy, Freeze.
Массив ровно N создаётся from_fn: теги 0..N по одному, ключи kani::any().
N фиксирована в гармонике, 2..32; unwind(34). Счётчик Drop — отдельный
static usize, сброс перед созданием массива, увеличение в каждом Drop.
Comparator читает volatile key/tag обоих аргументов, затем kani::any();
копий Drop-значения comparator не создаёт. Все тела сортировки реальные.

Гармоники count: сортировка, явный mem::drop массива, assert count==N.
Отдельные гармоники perm: одна независимая произвольная u8-проба тега
до сортировки; после неё кратность равна 1 для пробы в 0..N, иначе 0.
Проба без assume охватывает все теги, в том числе вне входа. В perm нет
assert счётчика Drop. Padding типа не читается спецификацией.

Нижние маршруты: независимый bool до сортировки выбирает fallback или
insertion(offset=1). Префикс длины 1 не требует ограничения comparator.
Верхние: такой же bool выбирает прямой general или stable-Freeze trait,
scratch 48. Два normal-return cover на каждую длину/свойство.
Сначала fallback/insertion N2, N4, N8; потом general/stable N2, N4, N8,
и N16/24/32 по результатам. Непрошедшая ступень раскрывается.

**Ledger K-14r:** no stub_verified. Ручные stubs заменяют только
panic_on_ord_violation: верхние используют прежний w1_abort_ord_violation
(cover + assume(false)), нижние — w2night_drop_abort_quiet (assume(false),
без cover), допустимый CD-5 на маршрутах без слияния. Отдельная reachability
на том же Drop-типе и N2 верхних использует покрывающий stub.
Других assume/any_where нет. Обоснование среза — -Cpanic=abort.
Заявление только о путях без паники; unwind/CopyOnDrop на раскрутке,
uninit и полная reference validity не проверяются.

**Редукции K-14r:** ключи u64 не ограничены. Identity tags — именно
уникальные 0..N, представимые в u8 при N<=32; это модель уникальных тегов,
не уменьшение области ключей. Произвольная u8-проба без ограничения.

Первый пакет `w2-merge-night-k14-controls-low2-026`, 4×10 мин:
assertion-контроль варианта A (expected FAILED, точный текст),
reachability на Drop-типе (SUCCESS), нижние N2 count/perm (SUCCESS).
Control/reachability вызывают upper N2 только для контроля механизма;
наращивание верхних результатов начнётся после нижних N2/4/8.
До зелёного контроля и R9 новые результаты K-14r не засчитываются.
После dispatch ночных jobs 26, preflight отказов 3;
с П2 до ночи: 31 jobs, 4 preflight отказа, 35/40 консервативных попыток.

REVIEW REQUEST 9402a0e28400c42ce9f1b133dd1fa2b3cbb57f63

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`.
K-14r: Drop-тип, читающий произвольный comparator, отдельные count/perm,
ручной stub только panic_on_ord_violation, контролирующие гармоники.
Первое измерение ожидается; локальные rustc/cargo/Kani не запускались.
K-12a job 170: summary и check-tooling ok, только diagnostic-данные.

### Job 171 — K-14r, статусы совпали, gate false по covers

Request `w2-merge-night-k14-controls-low2-026`,
head `65b73c5ba56668ced90ca3f9b364adb94c1bb3a2`, COMPLETE;
gate false, expectation met true, measurement ok false, Kani exit 1.
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1780984 KiB, wall с компиляцией 45.86 с;
cgroup peak 1.90 GiB, ENFORCED 13 GiB, OOM 0, swap off.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable checks | cover |
|---|---|---:|---|---:|---|
| `w2night_drop_control_a` | FAILED / FAILED | 1.6734229 | 1/462 | 9 | 3/5 |
| `w2night_drop_reachable` | SUCCESS / SUCCESS | 1.4613928 | 0/461 | 9 | 3/5 |
| `w2night_drop_low2_count` | SUCCESS / SUCCESS | 0.44831762 | 0/461 | 17 | 2/4 |
| `w2night_drop_low2_perm` | SUCCESS / SUCCESS | 0.570156 | 0/461 | 16 | 2/4 |

Единственный failed check контроля: `assertion failed:
drop_control_value != drop_control_value` @ `kani_k1/merge.rs:1970`.
Контроль FAILED намеренный, других failed checks нет. Covers normal-return
и среза достигнуты, но Kani также учёл два covers противоположного
семейства под const UPPER. Ограниченный log-grep: строки 2722/2736/2748/2760
подтверждают по два unreachable cover в каждой гармонике. Gate false,
ни одна строка пакета пока не засчитана; независимый R9 ожидается.

### N-D30 (R7): covers в конкретных обёртках

Helper возвращает уже выбранный alternate bool; covers перенесены в
макрос-обёртку. Две ветки macro для literal false/true выпускают только
два covers своего семейства. В контрольной гармонике те же два верхних
covers стоят явно. Тела сортировки, входы, comparator, свойства и stubs
не меняются; новых assume/редукций нет.

Повтор `w2-merge-night-k14-controls-low2-retry-027`: те же четыре
гармоники, FAILED/SUCCESS/SUCCESS/SUCCESS, 4×10 мин. Ожидаются полные
covers: 3/3 у control/reachable (включая covering stub), 2/2 у low2.
По сообщению координатора R9 `9402a0e2` принят независимым reviewer;
следующая правка covers передаётся как актуальный SHA того же review.
Измерения продолжаются до вердикта, зачёт только после GO.
После dispatch ночных jobs 27, preflight отказов 3;
с П2 до ночи: 32 jobs, 4 preflight отказа, 36/40 консервативных попыток.

REVIEW REQUEST 806adda80ebbac90c749f54f04fa880d78ac67ec

Актуализация K-14r review `9402a0e2`. Файлы:
`library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`.
Правка только размещения route covers и возврата route selector из helper;
сортировка, свойства, входы и manual stubs прежние. Evidence job 171:
summary/check-tooling ok, gate false по двум unreachable covers на строку.
Новый measurement повторяет тот же набор контролей и low2.

## Фаза 9

- Агент: K1-merge, Codex. Вход: `63c4b9af`, находка 10 фазы 8.
- T0: 2026-10-26T02:31:16Z (UTC системных часов; `date -u`).
- T0+180 (новые dispatch не запускать): 2026-10-26T05:31:16Z.
- T0+210 (конец отчёта): 2026-10-26T06:01:16Z.
- Лимиты: ≤2 dispatch, строго последовательно; Q8 только после чтения Q7. Одна гармоника ×30 мин, `resource`, `gcb-e2-highmem-4`; timeout сборки 60 мин.
- Перед каждым dispatch отдельный `k1g.sh budget`: used + reserved + 60 ≤330 минут пула. При превышении или отказе dispatch новых прогонов нет. Начальный ориентир used=237; потолок инструмента 370 не заменяет лимит фазы.
- Lane-база `31c890b11a7677f04d979f31f1b3c921ee48fd13`; lane/runtime не менять. Ожидание — `k1g.sh watch`, затем конец turn без опроса/goal.
- Resource не даёт PASS/measurement, вердикт K-1 не меняется. STOP заморожен: 1 из 3 (2 из 3 при учёте job 41/42), около 138 из 180 минут; R9 не требуется.

### Журнал решений фазы 9

- **P9-D1 (R7).** Проверить гипотезу ширины Q7: A (`5edf162c`), полный инвариант, фиксированная N=8, ширина помощников 8. Инвентаризировать все развёртки и пути контракта/инварианта, обрезать только ширину с сохранением логики на len≤8. Нужное сужение domain контракта обосновать отдельно до dispatch. Альтернатива — менять только константу без литеральных списков — не проверяет гипотезу и может нарушить соответствие ширины и покрытия. Q8 не готовить и не отправлять до результатов Q7; в конце восстановить `library/` к `84a2d5f4`.

- **P9-D2 (R7, domain).** Явное `requires(v.len() >= 2 && v.len() <= 32)` в `smallsort.rs` не менять: следующее существующее requires `k1_merge_halves_sorted_q(v, ...)` уже начинается с `len <= K1_UNROLL && ...`. При ширине 8 совокупность requires допускает только 2..=8; на len>8 ложна до обращения к предикатам сортированности. Поэтому нет допустимого по контракту входа len>8 с усечённым счётчиком; отдельное сужение первой клаузы не требуется. `k1_bm_inv_core` также уже возвращает None при len>K1_UNROLL. На len≤8 обе проверки границы сохраняют значение. Альтернатива — явно заменить 32 на 8 — была бы избыточна и добавила бы изменение контракта сверх необходимого. Это диагностика области ≤8, не контракт для general до 32.

- **P9-D3 (точный diff и эквивалентность Q7).** База proof-файлов — `5edf162c`. В `merge.rs`: (1) `K1_UNROLL: 32→8`; (2) в `CopyOnDrop::k1_count_u`, `k1_count_l`, `k1_bm_inv_count_l` литеральный список `step!(0 … 31)` заменён на `step!(0 … 7)`; (3) в `k1_sorted_u` список `step!(1 … 31)` заменён на `step!(1 … 7)`; (4) `bm_u64_len32` переименована в `bm_u64_len8`, единственный вызов в ней `bm_len::<u64, _, 32>` заменён на `bm_len::<u64, _, 8>`, proof_for_contract и unwind(34) сохранены. `smallsort.rs` точно совпадает с A: контракт и полный `k1_bm_inv3` не переписаны. Других текстовых изменений proof-файлов нет. Вызовы через изменённую константу: `k1_sorted_q` теперь квантифицирует `1..8`; `k1_merge_halves_sorted_q`, `k1_merge_halves_sorted` и `k1_bm_inv_core` используют прежние проверки границы с шириной 8. Косвенно те же count/perm и inv3 получают ограниченную развёртку.

- **Обоснование сохранения логики:** на len≤8 все удалённые `step` с i≥8 в count/count_l/invariant count были под `i<len` и не исполнялись; в sorted_u удалённые проверки тоже под `i<len`; в sorted_q удалённые i≥8 давали истинный `i>=len`. Оставшиеся выражения, порядок сравнений/загрузок/сумм и остальные части инварианта не меняются. Четыре списка — все элементные развёртки `step!` в A. Не обрезать `is_probe::words!(0 … 15)`, `PROBE_BYTES=128`, `K1Probe` и байтовые смещения [u8;85]: они кодируют полное значение одного элемента, а не длину региона. Остальные гармоники и их списки длин сохранены, не запускаются. Символьные u64 и probe без редукции домена значений; единственные сужения — ширина и фиксированная длина, раскрыты здесь. Проверка — статический diff/покрытие списков и lane validate; локальные rustc/cargo/Kani не запускались (R6).

- **P9-D4 (R7, Q8 после прочтения Q7).** Следовать варианту (б): ширина8 снова упала в goto-instrument около30 GiB, гипотеза не подтверждена; Q8 не отправлять. Альтернатива — измерить ширину16 при доступном бюджете — противоречит явному условию фазы. Бюджет закрытия used252/reserved0 допускал бы 312≤330, поэтому причиной отказа от Q8 является результат Q7, а не денежный лимит. Не превращать два оборванных пика в утверждение, что ширина никогда не влияет на память.

### Журнал прогонов фазы 9

| Прогон | request_id | Состояние | SHA / Build id | Статус |
|---|---|---|---|---|
| Q7 | merge-p9-width8-028 | A `5edf162c`, width=8 / N=8, полный инвариант; P9-D2/D3 | `412d183b53fe13ab3c1fb4a687f999a0e185e8c8` / `6f4b253e-c3bd-4c47-9099-5e682ddb46c2` | Cloud Build FAILURE; summary TOOL_ERROR / NOT_RUN, gate false; goto-instrument SIGKILL; check-tooling ok; перед dispatch budget: 237+0+60=297 ≤330 |

### Ресурсные данные фазы 9

Источник — `k1g.sh summary`, `peaks` и bounded `log-grep` завершённой Q7. Пики команд — VmHWM, выборки каждые 2 с; `first_s`–`last_s` отсчитываются от старта проверки и не являются точным CPU-временем. `check-tooling` — **ok** против `31c890b11a7677f04d979f31f1b3c921ee48fd13`: pool `k1-highmem4`, SHA из записи Cloud Build совпадает с таблицей, файлы lane и пять хешей сводки совпадают с базой.

| Прогон | kani-compiler | goto-instrument | cbmc | time -v / Verification Time / подготовка |
|---|---|---|---|---|
| Q7, width=8 / N=8 | 1 608 584 KiB (1,53 GiB), 0–62 с | 32 034 368 KiB (30,55 GiB, >16 GB), 66–436 с | не достигнут; NOT_RUN | max RSS **32 189 220 KiB (30,70 GiB)**; wall 441,41 с; Verification Time отсутствует; проверка началась через 376 с после validate |

`time -v` выше крупнейшего пика команды (рост между выборками); по правилу lane это истинный пик одиночного процесса. Sampler: 221 выборка, elapsed=441 с, sum RSS peak 32 040 496 KiB. Swap=0, cgroup-лимита и kernel OOM-счётчика в resource-lane нет. Gate=false, expectation_met=false, measurement_ok=None; SUCCESS, выполненных covers и нового proof credit нет.

### Находка 11: ширина 8 не устранила блокер

- **Q7:** инструментация полного `k1_bm_inv3` не проходит и при ширине 8 / N=8: `goto-instrument` достиг 30,55 GiB и завершился по SIGKILL. Наблюдаемый интервал 66–436 с — около 370 с; полного времени успешной инструментации нет. Bounded `log-grep` 2848–2850 показывает инструментацию `bidirectional_merge`, предупреждение «transformed loops will not be unwound after applying loop contracts», затем signal 9. SIGKILL при таком пике согласуется с исчерпанием памяти, но отдельного kernel OOM-подтверждения нет; сохраняется статус TOOL_ERROR / NOT_RUN из сводки.
- **Гипотеза координатора:** не подтверждена этим прогоном. На той же N=8 ширина 32 в Q6 фазы 8 дала 30,53 GiB / SIGKILL; ширина 8 в Q7 — 30,55 GiB / SIGKILL. Снижение только ширины всех четырёх развёрток и зависимого квантора не позволило пройти инструментацию и не дало точки ≤16 GB. Оба прогона остановлены около предела машины: сравнение не доказывает равенство их неограниченных пиков или отсутствие влияния ширины на размер программы. Причина оставшейся стоимости внутри DFCC/контракта не локализована.
- **Q2 фазы 7:** для полного инварианта по-прежнему не измерено, доказывает ли CBMC контракт и за какое время: до CBMC не дошло и на ширине 8. Нет Verification Time и результата covers. Контроль Q4 с тривиальным инвариантом остаётся отдельной точкой, дошедшей до CBMC с TIMEOUT; он не доказывает полный инвариант.
- **Q8:** не запускался по условию задания, решение P9-D4. Ширина 16 / N16 не измерена. Вариантов с новой формулировкой, изменённым логическим содержанием, другой версией Kani или шириной меньше 8 в этой фазе нет.

### Объединённые измерения фаз 7–9

В таблице обычные proof B/C — отдельные контроли, не `proof_for_contract`. Пики — измеренные значения команд, а не оценка памяти успешного доказательства. Полный инвариант и один и тот же контракт/счётчик сохранены на точках A, Q5, Q6, Q7 в пределах указанной ширины.

| Ширина / N | Состояние и источник | Пик goto-instrument | Исход CBMC |
|---|---|---|---|
| 8 / 8 | полный инвариант, Q7 фазы 9, `412d183b` | 30,55 GiB, SIGKILL | не достигнут, NOT_RUN |
| 32 / 8 | полный инвариант, Q6 фазы 8, `526a062c` | 30,53 GiB, SIGKILL | не достигнут, NOT_RUN |
| 32 / 16 | полный инвариант, Q5 фазы 8, `5c9f0aa8` | 30,62 GiB, SIGKILL | не достигнут, NOT_RUN |
| 32 / 32 | полный инвариант, A фазы 7, `3f68815f` | 30,55 GiB, SIGKILL | не достигнут, NOT_RUN |
| 32 / 32 | тривиальный инвариант, Q4 фазы 8, `934c133d` | 26,18 GiB, прошёл | TIMEOUT 30 мин; пик 30,63 GiB |
| 32 / 32 | обычная proof, loop-атрибуты на цикле, B фазы 7, `c05d7eeb` | 1,21 GiB, прошёл | TIMEOUT 60 мин; пик 0,24 GiB |
| 32 / 32 | обычная proof без loop-атрибутов, C фазы 7, `059c0fdd` | не зарегистрирован в выборках; не измерен | TIMEOUT 60 мин; пик 2,74 GiB |

**Строка для владельца: «уменьшение ширины не помогает: пик ~30 GiB и на ширине 8».** Уточнение: не помогло пройти инструментацию на измеренной машине; закон роста полного пика по ширине не установлен. Это не вердикт K-1. macOS: не измерено, проверяется на этапе подачи.

### Завершение и передача

- Выполнен **1/2 dispatch**, одна гармоника ×30 мин. Q8 не запускался, активных сборок и непрочитанных результатов нет. Досрочное закрытие — сработало заданное условие остановки после Q7 (ширина8 снова упала около30 GiB), а не исчерпание бюджета или окна.
- Перед Q7 отдельный `k1g.sh budget`: **237+0+60=297 ≤330**. Итоговый budget: **10 сборок проекта; used 252, reserved 0 минут пула**, не более ~$6,58. На фазу 9 приходится 15 минут по округлённому ledger (252−237). Потолок владельца не менялся.
- Resource не даёт PASS/measurement, вердикт K-1 не меняется. STOP заморожен: 1 из 3 (2 из 3 при учёте job 41/42), около 138 из 180 минут. R9 не нужен и не запускался. Диагностика ширины не засчитана как новая формулировка или принятая proof; домен значений u64/probe не редуцировался.
- **Восстановление D20/D22:** оба proof-файла `library/core/src/slice/sort/shared/smallsort.rs` и `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs` возвращены точно к `84a2d5f4`; `git diff --exit-code 84a2d5f4 -- library/` — чисто. Ширина32, формулировка1, loop-атрибута нет, прежние помощники и гармоники сохранены. Коммит восстановления: `32cc2190664e62fdb29c526b749017ee63fac2aa`. Runtime/lane не менялись, K1-network не тронут.
- `RUN-REQUEST.json` сохранён как отправленный запрос Q7; evidence относится к SHA Q7, а не к восстановленному HEAD. Временной bm_u64_len8 после восстановления нет; запрос не предназначен для нового dispatch. Новых доказательств контрактов insert_tail/bidirectional_merge нет; ограничения F1 сохраняются.
- Следующий шаг координатора: передать владельцу находку11 — отрицательный диагностический результат ширины8 и незакрытый Q2. Остаточный ресурс/окно не открывает новых прогонов; следующая работа только по новому заданию. Никаких запросов владельцу не требуется.

**ФАЗА 9 ЗАВЕРШЕНА** — 2026-10-26T02:52:45Z. Отчёт и восстановление опубликованы в собственной ветке до T0+210. Активных сборок нет, Q8 не запускался. Дальнейшая работа только по следующему заданию координатора.

## Фаза 8

- Агент: K1-merge, Codex. Вход: `33315b6e`, находка 9 фазы 7.
- T0: 2026-10-26T01:03:45Z (UTC системных часов; `date -u`).
- T0+240 (новые dispatch не запускать): 2026-10-26T05:03:45Z.
- T0+270 (конец отчёта): 2026-10-26T05:33:45Z.
- Лимиты: ≤3 dispatch; одна гармоника ×30 мин, `resource`, `gcb-e2-highmem-4`; timeout сборки 60 мин; ≤2 незавершённых сборок.
- **Бюджет фазы:** непосредственно перед каждым dispatch `k1g.sh budget`, разрешено только при used + reserved + 60 ≤330 минут пула. При превышении или отказе dispatch новых прогонов нет, фазу закрыть. Потолок инструмента 370 не заменяет этот лимит.
- Lane-база: `31c890b11a7677f04d979f31f1b3c921ee48fd13`; файлы lane не менять. Ожидание — `k1g.sh watch`, затем конец turn без опроса/goal.
- Resource не даёт PASS/measurement, вердикт K-1 не меняется. STOP заморожен: 1 из 3 (2 из 3 при учёте job 41/42), около 138 из 180 минут. R9 не требуется.

### Журнал решений фазы 8

- **P8-D1 (R7).** Начать с Q4 (job 35, `094c3287`, тривиальный инвариант, N=32) и Q5 (A фазы 7 / job 36, `5edf162c`, полный инвариант, N=16); разрешённая пара параллельных сборок. Альтернатива — последовательные прогоны; параллельность сокращает ожидание независимых вопросов без расширения числа сборок. Бюджет проверять отдельно перед каждым dispatch. Q6 выбрать только после обоих результатов. Длину менять исключительно в гармонике, контракты/инвариант/счётчик/runtime не менять. В конце восстановить proof-файлы точно к `84a2d5f4`.

- **P8-D2 (R7, точный diff Q5).** В исходном состоянии A (`5edf162c`) уже есть `#[kani::proof_for_contract(...bidirectional_merge)] #[kani::unwind(34)] fn bm_u64_len16() { bm_len::<u64, _, 16>(lt_u64); }`. Выбрать эту существующую гармонику в RUN-REQUEST вместо `bm_u64_len32`; diff `library/` относительно A — пустой. Это требуемый N=16 без изменения контракта, полного инварианта, счётчика, `K1_UNROLL=32` и runtime; unwind(34) остаётся достаточным. Альтернатива — переименовать/изменить N32-гармонику; существующая N16 даёт ту же проверку без лишнего source diff. Границы предположений не меняются.

- **P8-D3 (R7, Q6 по результатам Q4/Q5).** Выбран вариант (б), полный инвариант A на N=8: Q5 N=16 упал в инструментации. N=24 не выбран (предназначен для случая, когда N=16 дошло до CBMC); остановка без третьей точки не выбрана, пока бюджет допускает разрешённый N=8. Точный diff `library/` относительно `5edf162c`: только в `merge.rs` функция `bm_u64_len32` переименована в `bm_u64_len8`, вызов `bm_len::<u64, _, 32>` заменён на `bm_len::<u64, _, 8>`. Сохраняются proof_for_contract, unwind(34), общий bm_len с cover, остальные гармоники, K1_UNROLL=32, контракт функции, k1_bm_inv3, счётчик и runtime. Символьную bm_u64_upto8 не использовать: нужна одна фиксированная длина, а не 2..=8. Новая формулировка не вводится. Локальная validate отвергла первый текст purpose (длиннее 300 символов); текст сокращён до лимита схемы, dispatch до исправления не выполнялся.

- **P8-D4 (R7, формулировка итога).** Строку варианта 2 задания ограничить полным инвариантом и измеренными N=8/16/32; сразу указать исключение Q4 с тривиальным инвариантом, дошедшим до CBMC. Альтернатива — строка без уточнения — противоречила бы Q4. Варианты «контракт доказывается» и «память определяется инвариантом, а не механизмом» не поддержаны данными, их не использовать.

### Журнал прогонов фазы 8

| Прогон | request_id | Состояние | SHA / Build id | Статус |
|---|---|---|---|---|
| Q4 | merge-p8-trivial32-025 | job 35 `094c3287`, N=32, тривиальный инвариант | `934c133d3b8572efc8307881f2dc0eb24cd25885` / `c99da0b6-a7c2-4bc6-97ef-6548d02d6202` | Cloud Build FAILURE; summary COMPLETE, gate false; TIMEOUT 30 мин; check-tooling ok против `31c890b1`; перед dispatch budget: 164+0+60=224 ≤330 |
| Q5 | merge-p8-full16-026 | A фазы 7 / job 36 `5edf162c`, существующая bm_u64_len16, полный инвариант | `5c9f0aa8ab98691612e038ca5f26de36744f25d8` / `04646686-9c90-457e-9b34-3c605c64033a` | Cloud Build FAILURE; summary TOOL_ERROR, gate false; NOT_RUN; goto-instrument SIGKILL; check-tooling ok; перед dispatch budget: 164+60+60=284 ≤330 |
| Q6 | merge-p8-full8-027 | A `5edf162c`, полный инвариант, только гармоника N=8 | `526a062c65b4150f5747aa7b27a94a3a7d1c5461` / `d3be58f3-4b51-416d-b358-9f8dc06d2022` | Cloud Build FAILURE; summary TOOL_ERROR, gate false; NOT_RUN; goto-instrument SIGKILL; check-tooling ok; перед dispatch budget: 224+0+60=284 ≤330 |

### Ресурсные данные фазы 8

Пики — VmHWM по выборкам каждые 2 с; интервалы — `first_s`–`last_s` от старта проверки, не точные времена выполнения. Во всех прогонах Verification Time отсутствует, gate false, measurement_ok=None; formal proof credit не получен. У Q4/Q5/Q6 `time -v` выше крупнейшего пика команды: по правилу lane это истинный пик одиночного процесса. Swap выключен, лимита cgroup и счётчика OOM-kill в этом lane нет.

| Прогон | kani-compiler | goto-instrument | cbmc | time -v / Verification Time / прочее |
|---|---|---|---|---|
| Q4 | 1 609 784 KiB (1,54 GiB), 2–60 с | 27 448 424 KiB (26,18 GiB, >16 GB), 62–533 с | 32 118 604 KiB (30,63 GiB, >16 GB), 537–1108 с | max RSS 32 119 116 KiB (30,63 GiB), выше выборок: истинный пик одиночного процесса по правилу lane; Verification Time отсутствует (TIMEOUT); wall 2341,62 с; старт проверки через 349 с после validate; swap=0 |
| Q5 | 1 616 540 KiB (1,54 GiB), 2–64 с | 32 106 792 KiB (30,62 GiB, >16 GB), 66–392 с | не достигнут, NOT_RUN | max RSS 32 175 464 KiB (30,68 GiB), выше выборок: истинный пик одиночного процесса; Verification Time отсутствует; wall 396,70 с; старт проверки через 377 с; swap=0 |
| Q6 | 1 617 140 KiB (1,54 GiB), 0–58 с | 32 008 132 KiB (30,53 GiB, >16 GB), 60–377 с | не достигнут, NOT_RUN | max RSS 32 174 836 KiB (30,68 GiB); Verification Time отсутствует; wall 381,29 с; старт проверки через 327 с; swap=0 |

### Находка 10: атрибуция и уменьшение длины

- **Q4:** тривиальный инвариант на N=32 позволил пройти `goto-instrument` и начать CBMC, но инструментация всё равно требует десятки GiB: 26,18 GiB против наблюдавшихся 30,55 GiB (SIGKILL) полного инварианта A фазы 7. Пик без содержательного `k1_bm_inv3` уже превышает 16 GB; замена только содержания инварианта не устранила бы этот ресурсный барьер. Содержание влияет на измеренное поведение (A не прошёл, Q4 прошёл); утверждать, что оно вовсе не влияет на память, нельзя. Как именно делится стоимость между счётчиком, контрактом функции и механизмом loop contract, этим сравнением не установлено.
- CBMC в Q4 запущен, сводка COMPLETE/TIMEOUT 30 мин, gate false; SUCCESS и covers не получены. Bounded `log-grep` (2716, 2719–2720): проверка `bm_u64_len32`, VERIFICATION FAILED, CBMC timed out. Предупреждения о трансформации в доступном успешном выводе инструментации нет. Привязка: `_SHA` `934c133d3b8572efc8307881f2dc0eb24cd25885`, private pool и все lane-хеши соответствуют заданию (check-tooling ok).
- **Ограничение временных данных Q4:** sampler сообщает 556 выборок за elapsed=2341 с, а последняя выборка CBMC — 1108 с. Поэтому интервал CBMC 537–1108 с нельзя считать полным временем до TIMEOUT; ни непрерывность выборок, ни причина неполного покрытия времени не установлены. Статус TIMEOUT взят из сводки и локализованной строки Kani, не выведен из выборок. SIGKILL/OOM в CBMC сводка не сообщает; подменять TIMEOUT на OOM нельзя.
- **Q5:** N=16 с тем же полным инвариантом и счётчиком не доходит до CBMC: goto-instrument 30,62 GiB, SIGKILL, summary TOOL_ERROR / гармоника NOT_RUN. Наблюдаемый интервал инструментации 66–392 с (около 326 с); полного успешного времени нет. Bounded log-grep 2813–2815: инструментация bidirectional_merge, предупреждение transformed loops после применения loop contracts, затем signal 9. Привязка `_SHA` `5c9f0aa8ab98691612e038ca5f26de36744f25d8`, pool и lane-хеши — check-tooling ok. Q2 фазы 7 для полного инварианта всё ещё без ответа о CBMC, даже на N=16. Одинаковые пики около предела машины на N=16/32 не дают полного профиля роста: оба прогона оборваны, истинный требуемый пик неизвестен.
- **Q6:** N=8 с полным инвариантом также не доходит до CBMC: goto-instrument 30,53 GiB, SIGKILL, summary TOOL_ERROR / NOT_RUN. Наблюдаемый интервал 60–377 с (около 317 с). Bounded log-grep 2827–2829: инструментация bidirectional_merge, предупреждение о преобразованных циклах после loop contracts, затем signal 9. Привязка `_SHA` `526a062c65b4150f5747aa7b27a94a3a7d1c5461`, pool и lane-хеши — check-tooling ok. Ни одна из трёх фиксированных длин полного инварианта не дала результата CBMC.
- **Граница и ограничения:** положительная точка ≤16 GB не найдена. На N=8,16,32 получены оборванные по SIGKILL прогоны с пиком около предела машины; из них нельзя вывести ни точный требуемый пик, ни закон роста по длине, ни отсутствие зависимости от длины. `K1_UNROLL=32`, контракт и инвариант оставались неизменными по заданию. Сужение их границ, N<8, N=24, другая версия Kani или новая формулировка не проверялись. Прогонов больше нет. Наблюдение Q4 исключает объяснение десятков GiB только содержанием полного инварианта, но не изолирует отдельную стоимость счётчика/контракта/loop contract.

| Длина / состояние | Пик goto-instrument | Исход CBMC |
|---|---|---|
| N=8, полный инвариант, Q6 | 30,53 GiB, SIGKILL; весь процесс time -v 30,68 GiB | не достигнут, NOT_RUN |
| N=16, полный инвариант, Q5 | 30,62 GiB, SIGKILL; весь процесс time -v 30,68 GiB | не достигнут, NOT_RUN |
| N=32, полный инвариант, A фазы 7 (`929ef63e-58d2-4838-8a42-c5465d96797a`, `3f68815f`) | 30,55 GiB, SIGKILL; весь процесс time -v 30,69 GiB | не достигнут, NOT_RUN |
| N=32, тривиальный инвариант, Q4 | 26,18 GiB, прошёл | TIMEOUT 30 мин; пик 30,63 GiB |

**Строка для владельца: «контракт не доходит до CBMC ни на одной измеренной длине» — для полного инварианта формулировки 3, N=8,16,32.** Для тривиального инварианта есть отдельное исключение Q4: N=32 доходит до CBMC, но при инструментации >16 GB и с TIMEOUT. Контракт с полным инвариантом не доказан ни на одной измеренной длине; формулировка строки «память определяется инвариантом, а не механизмом контракта» данными Q4 не подтверждена. Это итог ресурсной фазы, не новый вердикт K-1. macOS: не измерено, проверяется на этапе подачи.

### Завершение и передача

- Dispatch **3/3**, одна гармоника ×30 мин в каждом, сумма таймаутов 90 мин. Все сборки завершены и прочитаны. `check-tooling` каждого прогона — ok против `31c890b11a7677f04d979f31f1b3c921ee48fd13`: pool `k1-highmem4`, SHA каждого прогона соответствует таблице, файлы lane и пять хешей сводки совпадают с базой.
- Строгий лимит фазы соблюдён перед каждым dispatch по отдельному `k1g.sh budget`: Q4 **164+0+60=224**, Q5 **164+60+60=284**, Q6 **224+0+60=284**, всё ≤330. Итоговый budget: **9 сборок проекта; used 237, reserved 0 минут пула**, не более ~$6,19. На фазу 8 приходится 73 минуты по округлённому ledger (237−164). Потолок владельца не менялся.
- Досрочное завершение: 3/3 dispatch исчерпаны. Четвёртая сборка, изменения инварианта/контракта и новое доказательство не входят в фазу 8. Счётчики STOP заморожены: 1 из 3 (2 из 3 при учёте job 41/42), около 138 из 180 минут. Resource не даёт PASS/measurement; R9 не требовался и не запускался. Вердикт K-1 не меняется.
- **Восстановление D20/D22:** оба proof-файла `library/core/src/slice/sort/shared/smallsort.rs` и `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs` возвращены точно к `84a2d5f4`; `git diff --exit-code 84a2d5f4 -- library/` — чисто. Формулировка 1, loop-атрибута нет, прежние помощники и гармоники сохранены. Коммит восстановления: `bfdc8a4e27ab96386fc5cfed287f28cb4c512d23`. Runtime и файлы lane не менялись; K1-network не тронут.
- `RUN-REQUEST.json` сохранён как последний отправленный Q6; evidence относится к SHA Q6 в таблице, а не к восстановленному HEAD. После восстановления временной `bm_u64_len8` нет — этот запрос не является заданием на новый прогон. Контракты `insert_tail` и `bidirectional_merge` новых доказательств не получили, ограничения F1 сохраняются.
- Следующий шаг координатора: передать владельцу находку 10 — десятки GiB даже с тривиальным инвариантом, отсутствие пройденной инструментации полного инварианта на N=8/16/32 и незакрытый Q2. Дальнейшая работа — только по новому заданию. Измеренные resource TIMEOUT/SIGKILL не превращать в proof acceptance или в новый STOP.

**ФАЗА 8 ЗАВЕРШЕНА** — 2026-10-26T02:25:06Z. Отчёт и восстановление опубликованы в собственной ветке до T0+270. Активных сборок нет. Следующее действие — только по новому заданию координатора.

## Фаза 7

- Агент: K1-merge, Codex. Вход: `c70f7250`, заключение фазы 6; вердикт K-1 не меняется.
- T0: 2026-10-25T22:15:30Z (UTC системных часов; `date -u`).
- T0+300 (новые dispatch не запускать): 2026-10-26T03:15:30Z.
- T0+330 (конец отчёта): 2026-10-26T03:45:30Z.
- Лимиты: ≤3 dispatch, одна гармоника ×60 мин на запрос, только `resource`, `gcb-e2-highmem-4`; ≤2 незавершённых сборок. Бюджет проекта — ≤370 минут пула / $10, включая smoke.
- База check-tooling: `31c890b11a7677f04d979f31f1b3c921ee48fd13`. Файлы lane не меняются. Ожидание — `k1g.sh watch`, затем конец turn, без опроса и без Codex goal.
- Счётчики STOP заморожены: 1 из 3 (2 из 3 при учёте job 41/42), около 138 из 180 минут без продвижения. Resource-прогоны не дают PASS/measurement; R9 не требуется.

### Журнал решений фазы 7

- **P7-D1 (R7).** Начать с A (job 36, `5edf162c`) и B (job 41, `5c0b06c1`); разрешённая пара параллельных сборок отвечает на независимые Q1/Q2 и Q3. Альтернатива — последовательные A/B; параллельность сокращает ожидание без расширения числа прогонов. C выбрать только по результатам. Перед запуском восстанавливать только отличающиеся proof-файлы `library/`; окончательное восстановление — proof-файлы входного `c70f7250` (D20/D22).

- **P7-D2 (R7, выбор C после A/B).** Вариант (в): повторить B без loop contract на цикле `bidirectional_merge`, с той же `bm_u64_len32_plain`, без изменения её предположений и проверок и без изменения runtime. Снять вместе `loop_invariant` и его `loop_modifies`: write set — часть того же loop contract, оставлять его отдельно не нужно. Причина: B и job 41 не показывают предупреждения о трансформации; контроль отделит наблюдаемую стоимость обычной proof от наличия атрибутов инварианта. Если C также даст TIMEOUT, одинаковый исход не докажет, что контракт в B игнорировался: вопрос останется не установленным по доступному логу. Альтернативы: job 35 с тривиальным инвариантом уточнил бы распределение памяти счётчика/инварианта, но превышение 16 GB для основного состояния A уже измерено; уменьшение длины A не выбрано, поскольку A не прошёл. Не запускать C — потерять разрешённый контроль для неясного Q3. Новых формулировок нет; C — удаление loop-атрибутов, resource без credit. Бюджет допускает ещё 90 минут резерва; до дедлайна полный envelope помещается.

### Журнал прогонов фазы 7

Все три прогона: одна гармоника, `resource`, `gcb-e2-highmem-4`, timeout 60 мин, expect SUCCESS. Cloud Build — FAILURE у всех; во всех сводках gate false, measurement_ok=None. Ни одной новой принятой proof нет. `check-tooling` каждого прогона — **ok** против `31c890b11a7677f04d979f31f1b3c921ee48fd13`: проверен private pool `k1-highmem4`; source SHA соответствует коммиту прогона в таблице; файлы lane и пять хешей сводки совпадают с базой.

| Прогон / request_id | Состояние | SHA сборки | Cloud Build id | Статус сводки / гармоники |
|---|---|---|---|---|
| A / merge-p7-resource-a-022 | job 36, `5edf162c`; `proof_for_contract`, `bm_u64_len32`, `k1_bm_inv3`, лёгкий счётчик | `3f68815f0707f1eb184ba2b05ee8613cb9788e56` | `929ef63e-58d2-4838-8a42-c5465d96797a` | TOOL_ERROR / NOT_RUN; `goto-instrument` SIGKILL |
| B / merge-p7-resource-b-023 | job 41, `5c0b06c1`; обычная proof `bm_u64_len32_plain`, loop contract сохранён | `c05d7eeb1240f082cd7a42f023926e29d013b699` | `1ac4ea31-4a17-49dd-8605-e403e72ac8df` | COMPLETE / TIMEOUT 60 мин |
| C / merge-p7-resource-c-024 | B без `loop_invariant` и связанного `loop_modifies`; та же гармоника и проверки | `059c0fdd5bceba9a045b1b779a39190009cdd02a` | `692f8e9b-d8ab-4c0d-a1e1-3e9b548ff389` | COMPLETE / TIMEOUT 60 мин |

### Ресурсные данные фазы 7

Интервалы `first_s`–`last_s` отсчитываются от старта проверки, выборки каждые 2 с. Это наблюдаемое присутствие команды, не точное CPU-время. Пики команд — VmHWM; KiB указаны точно, GiB округлены. Отсутствие команды в выборках не доказывает, что она не запускалась.

| Прогон | kani-compiler: пик / интервал | goto-instrument: пик / интервал | cbmc: пик / интервал | Verification Time | Подготовка / весь шаг проверки |
|---|---|---|---|---|---|
| A | 1 616 036 KiB (1,54 GiB), 0–66 с | 32 037 732 KiB (30,55 GiB, **>16 GB**), 70–404 с | не достигнут; гармоника NOT_RUN | отсутствует | проверка через 408 с после validate; wall 411,13 с |
| B | 1 607 744 KiB (1,53 GiB), 0–62 с | 1 264 672 KiB (1,21 GiB), 66–84 с | 246 836 KiB (0,24 GiB), 86–3683 с | отсутствует, TIMEOUT 60 мин | проверка через 361 с; wall 3685 с |
| C | 1 584 880 KiB (1,51 GiB), 2–62 с | в выборках не зарегистрирован; пик/время не измерены | 2 875 960 KiB (2,74 GiB), 64–3661 с | отсутствует, TIMEOUT 60 мин | проверка через 352 с; wall 3663 с |

У A `time -v` max RSS **32 179 636 KiB (30,69 GiB)** выше крупнейшего пика команды: рост между выборками. По правилу lane это истинный пик одиночного процесса. У B/C max RSS совпадает с наибольшим пиком команды: 1 607 744 / 2 875 960 KiB. Swap у всех выключен; cgroup-лимита и счётчика OOM-kill в resource-lane нет.

### Находка 9: ответы на Q1–Q3

- **Q1.** Основное состояние job 36 не проходит инструментацию и на машине 32 GB. `goto-instrument` наблюдался 70–404 с (около 334 с), достиг 30,55 GiB и завершился по SIGKILL. Это уже больше 16 GB раннера организаторов; общий одиночный пик по `time -v` — 30,69 GiB. Полный пик и время успешной инструментации не получены: наблюдается только рост до убийства процесса. SIGKILL при таком пике согласуется с исчерпанием памяти; отдельного kernel OOM-счётчика нет. Bounded `log-grep` A (2731–2733): инструментация `bidirectional_merge`, предупреждение «transformed loops will not be unwound after applying loop contracts», затем signal 9. В A применение loop contract отражено в логе.
- **Q2.** Не измерено: в A до CBMC не дошло, гармоника NOT_RUN. Данных о принятии контракта, Verification Time и covers нет. B/C — обычные proof и не заменяют `proof_for_contract` для `stub_verified` (R4).
- **Q3, время.** Job 41 без 10-минутного предела тоже не завершился: B — TIMEOUT на 60 мин при пике CBMC 0,24 GiB. Он наблюдался около 3597 с; инструментация прошла, наблюдаемый интервал 18 с. Полного времени до SUCCESS нет. Контроль C без loop contract также TIMEOUT на 60 мин; CBMC наблюдался около 3597 с при 2,74 GiB. Оба обычных доказательства превышают 10 мин в этом lane, без нового proof credit.
- **Q3, loop contract.** B и прежний job 41 по bounded `log-grep` дают одинаковые строки 2719–2720 (VERIFICATION FAILED, CBMC timed out), без предупреждения о трансформации. C даёт тот же итог и тоже без предупреждения. При удалении только loop-атрибутов изменилась измеренная картина: в B есть `goto-instrument` 66–84 с / 1,21 GiB и CBMC 0,24 GiB; в C `goto-instrument` не попал в выборки, CBMC 2,74 GiB. Это свидетельство влияния атрибутов на обработку программы, **но не прямое подтверждение применения инварианта в B/job 41**. Успешный вывод инструмента мог фильтроваться; факт применения по доступному логу остаётся не установленным. Одинаковые TIMEOUT не доказывают игнорирование атрибутов. Гипотеза находки 8 «дорог сам инвариант» не установлена: контроль без него тоже не завершился за час.

**Строка для владельца: «пик >16 GB»: блокер инструмента подтверждён числом.** Относится к основному `proof_for_contract` состоянию A. Это не вердикт K-1; решение о дальнейшей работе принимает владелец. macOS: не измерено, проверяется на этапе подачи.

### Завершение и передача

- Dispatch: **3/3**, сумма таймаутов гармоник 180 мин. Все сборки завершены, непрочитанных результатов нет. Досрочное закрытие — прогоны исчерпаны; новые формулировки, смена pin и четвёртый dispatch не разрешены этой фазой.
- Итоговый `k1g.sh budget`: **6 сборок проекта, 164 минуты пула использовано, 0 зарезервировано из 370**, не более ~$4,28. С учётом 12 минут smoke на фазу 7 приходится 152 минуты по округлённому ledger. Потолок владельца не менялся.
- Счётчики STOP сохранены: 1 из 3 (2 из 3 при учёте job 41/42), около 138 из 180 минут без продвижения. Результаты resource не засчитываются как measurement/PASS; R9 не нужен и не запускался. Вердикт K-1 не меняется.
- **Восстановление (D20/D22):** оба proof-файла `library/core/src/slice/sort/shared/smallsort.rs` и `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs` возвращены точно к `c70f7250`; `git diff --exit-code c70f7250 -- library/` — чисто. Формулировка 1, атрибута на цикле нет, прежние помощники и гармоники сохранены. Файлы lane не менялись. Коммит восстановления: `3c0cb4b9458899dbe64c8dd3a5a42a54f53fe6b9`.
- `RUN-REQUEST.json` сохранён как последний отправленный запрос C; evidence относится к SHA C в таблице, а не к восстановленному HEAD. Новые сборки не отправлять. Контракты `insert_tail` и `bidirectional_merge` на восстановленном HEAD не получили новых доказательств; ограничения F1 сохраняются, K1-network не тронут.
- Следующий шаг для координатора: передать владельцу измеренный нижний предел памяти A, TIMEOUT B/C и оставшийся вопрос применения loop contract. Без нового задания действий нет. Дальнейшая атрибуция памяти (job 35 с тривиальным инвариантом), точного способа обработки loop contract и полного времени успешного доказательства в этой фазе не выполнена.

**ФАЗА 7 ЗАВЕРШЕНА** — 2026-10-26T00:56:00Z. Отчёт и восстановление опубликованы в собственной ветке; завершение до T0+330. Дальнейшая работа — только по следующему заданию координатора.

## Фаза 6

- T0: 2026-10-25T09:16:07Z (`date -u`)
- T0+40 (новые прогоны не запускать): 2026-10-25T09:56:07Z
- T0+55 (конец отчёта): 2026-10-25T10:11:07Z
- Лимиты: ≤ 3 dispatch, сумма таймаутов ≤ 30 мин, одна гармоника на запрос, validate && commit && dispatch (TASK-merge.md «Фаза 6»). Lane-база check-tooling: `aca80458`. Вход: «Передача (для фазы 6)» на 2730c500.
- Счётчики STOP на входе: 1 формулировка из 3 проверена, около 108 из 180 минут без продвижения.

### Журнал прогонов фазы 6

| # | request_id | kind | job | head SHA | гармоники × таймаут | итог |
|---|---|---|---|---|---|---|
| 19 | merge-p6-attr-019 | diagnostic | 40 | 859391c9 | 1 × 8 мин | COMPLETE, gate false, check-tooling ok. Прогон 1, атрибуция находки 7: контракт job 32 плюс `forall` «половины отсортированы» в `requires`, без счётчика; тривиальный инвариант. **`goto-instrument` пройден**, OUT_OF_MEMORY в CBMC, как job 30, 32 (1 OOM-kill, 13 GiB, wall 6:14) |
| 20 | merge-p6-plain-020 | measurement | 41 | 5c0b06c1 | 1 × 10 мин | COMPLETE, gate false, check-tooling ok. Прогон 2: обычная `#[kani::proof]` `bm_u64_len32_plain`, инвариант `k1_bm_inv3` на цикле, лёгкие `requires`/`ensures` в гармонике. `goto-instrument` пройден, **CBMC — TIMEOUT 10 мин**, пик cgroup 1,84 GiB, OOM-kill нет (wall 10:52) |
| 21 | merge-p6-plainsorted-021 | measurement | 42 | fa5ca00e | 1 × 10 мин | COMPLETE, gate false, check-tooling ok. Прогон 3: как прогон 2, но без счётчика — инвариант `k1_bm_inv3_sorted`, гармоника `bm_u64_len32_plain_sorted` проверяет только сортированность. `goto-instrument` пройден, **CBMC — TIMEOUT 10 мин**, пик cgroup 1,79 GiB, OOM-kill нет (wall 10:51) |

Итого фазы 6: dispatch 3 из 3, сумма таймаутов 28 из 30 мин. Прогоны закончены в 09:45 UTC. Ветка восстановлена (D22).

### Находка 8: атрибуция находки 7 и цена инварианта в CBMC (job 40, 41, 42)

- **Инструментацию ломает счётчик перестановки в `ensures`** (лёгкая кодировка с `wrapping_add` и простыми загрузками при тривиальном инварианте не запускалась: job 38 шёл с полным инвариантом). Job 40 и job 35 (фаза 5) отличаются только `ensures` с `k1_perm_l`. Остальное у них общее: `requires` «половины отсортированы» через `forall`, `ensures` сортированности через `forall`, тривиальный инвариант, `loop_modifies` job 29. Без счётчика `goto-instrument` проходит (job 40, OOM потом в CBMC, как job 30, 32). Со счётчиком — OOM в `goto-instrument` (job 35). Оба `forall` инструментацию не ломают.
- **Перестановку на SAT-бэкенде иначе не выразить — рассуждение, прогоном не проверено.** Равенство мультимножеств — это равенство числа вхождений, кванторами первого порядка без функции-свидетеля оно не записывается. Свидетеля-биекцию пришлось бы передать в контракт как ghost-состояние; в std такого нет, а менять тело запрещает R2. `exists!` без свидетеля требует z3 и даёт лишь «каждый элемент выхода есть во входе», без кратностей. Поэтому для `proof_for_contract` с loop contract доступен только развёрнутый счётчик (32 позиции × 2 массива — минимум для длины 32), и его инструментация не проходит под 13 GiB.
- **В обычной proof инструментация проходит, но CBMC не укладывается в 10 минут.** Обычная `#[kani::proof]` с инвариантом `k1_bm_inv3` и лёгкой спецификацией в гармонике — TIMEOUT (job 41, пик 1,84 GiB). То же без счётчика, с одной сортированностью в инварианте и в `assert` — тоже TIMEOUT (job 42, пик 1,79 GiB). Обычная гармоника с формулировкой 3 на длине 32 в 10 минут не укладывается и без перестановки. Гипотеза, не измерено: дорог сам инвариант (учёт указателей, кванторная сортированность концов, соотношения половин). Контроля без loop contract не было, и что loop contract применён, лог не показывает. Память при этом не предел.
- **Не проверено:** где CBMC тратит время в job 41, 42 (лог без статистики формулы, `log-grep` по `size of program|variables|clauses` пуст); сколько заняла бы длина 32 без таймаута; раскрывает ли CBMC кванторы в 32 копии (риск координатора); масштаб по длинам — короче 32 формулировку 3 не мерили; z3 не пробовали.

## Фаза 5

- T0: 2026-10-25T08:15:03Z (`date -u`)
- T0+60 (новые прогоны не запускать): 2026-10-25T09:15:03Z
- T0+80 (конец отчёта): 2026-10-25T09:35:03Z
- Лимиты: ≤ 3 dispatch, сумма таймаутов ≤ 30 мин, одна гармоника на запрос, validate && commit && dispatch (TASK-merge.md «Фаза 5»). Lane-база check-tooling: `aca80458`. Вход: «Передача (для фазы 5)» на 312576a9.
- Счётчики STOP на входе: 1 формулировка из 3 проверена, около 90 из 180 минут без продвижения.

Лёгкие помощники (`K1Probe`, `k1_count_l`, `k1_perm_l`, `k1_merge_halves_sorted_q`, `k1_bm_inv3`) — коммит `2665ea3ff40ed1c49e96f304a2741351ca4bf422`. Локально не компилировались (R6); компиляция подтверждается прогоном 1.

### Журнал прогонов фазы 5

| # | request_id | kind | job | head SHA | гармоники × таймаут | итог |
|---|---|---|---|---|---|---|
| 16 | merge-p5-instr-016 | diagnostic | 35 | 094c3287 | 1 × 8 мин | RUNNER_ERROR, gate false, check-tooling ok. Прогон 1: контракт формулировки 3 (`forall` в `requires`/`ensures`, лёгкий счётчик в `ensures`), тривиальный инвариант, `loop_modifies` job 29. Помощники компилируются. **`goto-instrument` — OUT_OF_MEMORY** (SIGKILL после предупреждения о loop contracts, 1 OOM-kill, 13 GiB, wall 1:41) |
| 17 | merge-p5-inv3-017 | measurement | 36 | 5edf162c | 1 × 10 мин | RUNNER_ERROR, gate false, check-tooling ok. Прогон 2: инвариант `k1_bm_inv3`, тот же контракт. **`goto-instrument` — OUT_OF_MEMORY**, как в прогоне 1 (1 OOM-kill, 13 GiB, wall 2:38) |
| 18 | merge-p5-inv3-plain-018 | measurement | 38 | 1e906d61 | 1 × 10 мин | RUNNER_ERROR, gate false, check-tooling ok. Прогон 3, правка формулировки 3 (D19): как прогон 2, но в спецификации нет `ptr::add`/`read_unaligned`. **`goto-instrument` — OUT_OF_MEMORY** (1 OOM-kill, 13 GiB, wall 2:49) |

Итого фазы 5: dispatch 3 из 3, сумма таймаутов 28 из 30 мин. Прогоны закончены в 08:32 UTC. Ветка восстановлена (D20): `smallsort.rs` совпадает с 26049195 (формулировка 1, атрибута на цикле нет), лёгкие помощники остались в `merge.rs`. SHA восстановления — в D20.

### Находка 7: формулировка 3 не проходит `goto-instrument` под `proof_for_contract` (job 35, 36, 38)

- Все три прогона упали в `goto-instrument` по памяти, CBMC не запускался. По логу (`log-lines`) последняя строка перед падением — предупреждение «transformed loops will not be unwound after applying loop contracts». Ему предшествует `Instrumenting` функции `bidirectional_merge`. Значит, память кончается уже после применения loop contract, а не при разборе спецификации.
- **Сколько памяти не хватило, лог не говорит.** `goto-instrument` не печатает размеров. Есть только пик cgroup, равный пределу 13,00 GiB, и время до OOM-kill: 1:41 (job 35), 2:38 (job 36), 2:49 (job 38).
- **Сравнение с job 32** (инструментация прошла): в прогоне 1 к нему добавлены только два `forall` в `requires` (половины отсортированы) и лёгкий счётчик в `ensures` — 64 загрузки с одним сравнением, а не 64 × 19. Хватило и этого. Что из двух решает, не установлено: в фазе было 3 dispatch, атрибуция не дала бы ответа на главный вопрос (D19).
- **Правка D19 не помогла** (job 38): без `ptr::add`/`read_unaligned` в спецификации — тот же OOM. Гипотеза «тело `ptr::add` с UB-проверками раздувает инлайн» не подтверждается.
- **Контраст с job 24** (фаза 2): там обычная `#[kani::proof]` с тяжёлым инвариантом формулировки 2. `goto-instrument` прошёл, OOM был уже в CBMC. Под `proof_for_contract` тот же класс программ падает раньше. Значит, дорога связка «проверка контракта функции + loop contract в ней», а не loop contract сам по себе. Гипотеза, не проверена.
- **Риск координатора** (CBMC раскрывает квантор в 32 копии) не проверен: CBMC в фазе 5 не запускался.

## Фаза 4

- T0: 2026-10-24T21:30:48Z (`date -u`)
- T0+40 (новые прогоны не запускать): 2026-10-24T22:10:48Z
- T0+55 (конец отчёта): 2026-10-24T22:25:48Z
- Лимиты: ≤ 2 dispatch, сумма таймаутов ≤ 20 мин, одна гармоника на запрос, validate && commit && dispatch (TASK-merge.md «Фаза 4»). Lane-база check-tooling: `aca80458`. Вход: вердикт FAIL (STOP) на d7c91adc.

### Журнал прогонов фазы 4

| # | request_id | kind | job | head SHA | гармоники × таймаут | итог |
|---|---|---|---|---|---|---|
| 14 | merge-p4-trivial-014 | diagnostic | 30 | b94fac35 | 1 × 10 мин | COMPLETE, gate false, check-tooling ok. Прогон A: тривиальный контракт `bidirectional_merge` (только `requires` безопасности, `ensures(true)`) плюс loop contract как в job 29. **`goto-instrument` пройден**, `bm_u64_len32` — OUT_OF_MEMORY уже в CBMC (1 OOM-kill, 13 GiB, swap off, wall 5:43) |
| 15 | merge-p4-forall-015 | diagnostic | 32 | 188451df | 1 × 10 мин | COMPLETE, gate false, check-tooling ok. Прогон B: как A, но вместо `ensures(true)` сортированность одним `crate::forall!` по константному диапазону `1..32` с охраной `i >= len` (`k1_sorted_q`). **`goto-instrument` пройден**, OUT_OF_MEMORY в CBMC, как в A (1 OOM-kill, 13 GiB, wall 5:47) |

Итого фазы 4: dispatch 2 из 2, сумма таймаутов 20 из 20 мин. Прогоны закончены в 21:47 UTC. Ветка восстановлена коммитом `260491952485e61609bce90f5df337332a2df628`: `smallsort.rs` совпадает с d7c91adc (формулировка 1, атрибута на цикле нет), в `merge.rs` добавлен только неиспользуемый `k1_sorted_q`.

### Находка 6: блокер инструментации — тяжёлая спецификация функции, а не loop contract (job 30, 32)

- Job 29 и 30 отличаются только контрактом `bidirectional_merge`. Инвариант (тривиальный) и явный `loop_modifies` у них одинаковые.
  - С рабочим контрактом (job 29) `goto-instrument` падает по памяти. В `requires` там `k1_merge_halves_sorted`, в `ensures` — развёрнутые на 32 шага `k1_sorted_u`/`k1_count_u`, а `is_probe` — до 19 охраняемых сравнений на элемент.
  - С тривиальным контрактом (job 30: только `requires` безопасности, `ensures(true)`) `goto-instrument` проходит.
- Сортированность одним `forall!` в `ensures` (job 32) инструментацию тоже проходит.
- Значит, утверждение находки 3, D13 и D15 «любой loop contract на этом цикле даёт OOM» неверно. Верно только для тяжёлой развёрнутой спецификации в паре с loop contract. D12 («размер инварианта не важен») остаётся в силе, но проверял не ту переменную.
- В A и B CBMC кончается по памяти через несколько минут, так же, как в job 24 (обычная proof). Гипотеза, не проверена: тривиальный инвариант оставляет шесть указателей цикла полностью произвольными, и код после цикла разыменовывает их, так что анализ указателей CBMC охватывает все объекты программы. Настоящий инвариант привязывает указатели к `src`/`dst` и смещениям.
- Ограничение pin: SAT-бэкенд Kani `9461e07a` кодирует кванторы только с константными границами. При символьной границе Kani сообщает FAILED и требует `#[kani::solver(z3)]` (документация `reference/experimental/quantifiers.md` на pin). Поэтому `k1_sorted_q` квантифицирует по `1..32` с охраной по длине.

## Фаза 3

- T0: 2026-10-24T20:58:51Z (`date -u`)
- T0+60 (новые прогоны не запускать): 2026-10-24T21:58:51Z
- T0+80 (конец отчёта): 2026-10-24T22:18:51Z
- Лимиты: ≤ 3 dispatch, сумма таймаутов ≤ 30 мин, в запросе с возможным OOM — одна гармоника (TASK-merge.md «Фаза 3»). Lane-база check-tooling: `aca80458`.
- Счётчики STOP на начало: 2 формулировки из 3, около 63 из 180 минут без продвижения.

### Журнал прогонов фазы 3

| # | request_id | kind | job | head SHA | гармоники × таймаут | итог |
|---|---|---|---|---|---|---|
| 11 | merge-p3-toy-011 | diagnostic | 27 | d83f3144 | 1 × 8 мин | COMPLETE, gate true. `toy_loop_contract` SUCCESS 0,11 с, 0/138, cover 2/2. Пик cgroup 1,70 GiB, OOM-kill 0. Игрушечный `for` по `Range` с тривиальным `loop_invariant` не даёт OOM. Оговорка: при `unwind(34)` и `n ≤ 32` тот же SUCCESS дала бы и обычная развёртка, и вывод goto-instrument Kani печатает только при ошибке. Поэтому применение контракта этим прогоном не доказано |
| 12 | merge-p3-modifies-012 | diagnostic | 28 | 22e14c32 | 1 × 10 мин | REQUEST_INVALID: `purpose` длиннее 300 символов. Kani не запускался. Моя ошибка: валидатор отклонил запрос, но dispatch был в той же команде без `&&`. Dispatch засчитан, таймаут засчитан консервативно |
| 13 | merge-p3-modifies-013 | diagnostic | 29 | 26a3f824 | 1 × 10 мин | RUNNER_ERROR за 2:18. Явный `loop_modifies` (шесть указателей-локалов и `dst[..len]`) принят компилятором, но `goto-instrument` убит OOM так же, как в job 17–22: 13 GiB, 1 OOM-kill, swap off, сразу после WARNING о loop contracts. `bm_u64_len32` NOT_RUN. check-tooling ok против `aca80458` |

Итого фазы 3: dispatch 3 из 3, сумма таймаутов 28 из 30 мин (8 + 10 + 10; таймаут job 28 засчитан, хотя Kani не запускался). Прогоны закончены в 21:09 UTC. check-tooling job 27 и 29 — ok против `aca80458`.

### Находка 5: контроль инструмента и явный loop_modifies (job 27, 29)

- **Контроль.** Игрушечный `for i in 0..n` над `[u64; 32]` с тривиальным `loop_invariant`, обычная proof (`toy_loop_contract`, job 27): SUCCESS, 0,11 с, пик 1,70 GiB. Контроль не различающий: это обычная proof, а OOM goto-instrument на `bidirectional_merge` был только под `proof_for_contract` (в обычной proof job 24 goto-instrument прошёл). В логе job 27 нет WARNING о loop contracts, который есть в job 29. Тот же SUCCESS дала бы и обычная развёртка. Значит, job 27 не показывает ни того, что контракт применился, ни того, что инструмент исправен на сопоставимом цикле (review F2).
- **Явный `loop_modifies`** на цикле `bidirectional_merge` с тривиальным инвариантом под `proof_for_contract` (job 29): падает так же, как с выведенным modifies (job 22).
- **По правилу фазы 3** (TASK-merge.md) формулировка 2 исключена по одной ветви правила: явный `loop_modifies` падает так же (job 29). Ветвь «OOM на игрушечном цикле» не применяется: job 27 её не проверяет. Диагностический атрибут с цикла снят (D15).

## Фаза 2

- T0: 2026-10-24T19:47:03Z (`date -u`)
- T0+180 (новые прогоны не запускать): 2026-10-24T22:47:03Z
- T0+200 (конец отчёта): 2026-10-24T23:07:03Z
- Лимиты: ≤ 6 dispatch, сумма таймаутов ≤ 180 мин. Lane-база check-tooling: `aca80458`.
- Счётчики STOP на начало: 1 формулировка из 3, около 15 из 180 минут без продвижения.

### Журнал прогонов фазы 2

| # | request_id | kind | job | head SHA | гармоники × таймаут | итог |
|---|---|---|---|---|---|---|
| 5 | merge-p2-inv-005 | diagnostic | 17 | 12984437 | 3 × 13 мин | RUNNER_ERROR за 2:23: `goto-instrument` убит OOM (13 GiB, 1 OOM-kill) на первой гармонике `bm_u64` сразу после применения loop contract. Первая гипотеза (D10): вложенные циклы `is_probe` внутри `k1_count` размножились при развёртке в goto-instrument. Её опровергли job 19–22 (D13). Гармоники NOT_RUN |
| 6 | merge-p2-inv-006 | diagnostic | 19 | 330d590f | 3 × 13 мин | RUNNER_ERROR за 2:06: снова OOM `goto-instrument` на `bm_u64`; без циклов `is_probe` остались только одиночные циклы `k1_sorted`/`k1_count`. Гипотеза D10 о размножении вложенных циклов неполна (D11) |
| 7 | merge-p2-inv-007 | diagnostic | 20 | 873d607d | 2 × 13 мин | RUNNER_ERROR за 2:16: снова OOM `goto-instrument` на `bm_u64`, хотя циклов в спецификации нет: строки «does not have a contract» исчезли, WARNING о loop contracts есть. Размер инварианта не влияет на время падения (D12) |
| 8 | merge-p2-bisect-008 | diagnostic | 21 | d0e6a7eb | 3 × 10 мин | RUNNER_ERROR за 1:39: Kani первой запустил `bm_u64_len32`, а не по алфавиту, и снова OOM `goto-instrument`. Бисекция данных не дала: порядок гармоник в Kani не управляется ни запросом, ни именами |
| 9 | merge-p2-bisect-009 | diagnostic | 22 | a77b38f6 | 1 × 8 мин | RUNNER_ERROR за 3:04: тривиальный инвариант `idx <= len / 2` (`bm_bisect_a_trivial_u16`) тоже даёт OOM `goto-instrument`. Содержание инварианта ни при чём: любой loop contract на этом цикле под `proof_for_contract` не проходит инструментацию в 13 GiB |
| 10 | merge-p2-bisect-010 | diagnostic | 24 | b838761a | 3 × 10 мин | COMPLETE, gate false, check-tooling ok против `aca80458`. Тривиальный инвариант в обычной `#[kani::proof]` (`bm_bisect_plain_trivial_u16`): goto-instrument прошёл, затем OUT_OF_MEMORY уже в CBMC, примерно через 2 минуты, 1 OOM-kill. `sort4_b16` SUCCESS 46,7 с, 0/521, cover 1/1. `sort4_b85` SUCCESS 427,3 с, 0/521, cover 1/1 |

Итого фазы 2: dispatch 6 из 6, сумма таймаутов 172 из 180 мин. Фаза закрыта досрочно в 20:35 UTC: dispatch исчерпаны (§9).

### Находка 3: loop contract на цикле `bidirectional_merge` не помещается в 13 GiB (job 17–24)

- Любой `loop_invariant` на цикле `for _ in 0..len_div_2` в `bidirectional_merge` даёт OOM на Kani `9461e07a`. Так ведут себя полный инвариант формулировки 2 и тривиальный `idx <= len / 2` (job 22).
- Под `proof_for_contract` (режим CHECK контракта функции) падает `goto-instrument`, примерно через минуту после WARNING «transformed loops will not be unwound after applying loop contracts» (job 17, 19, 20, 21, 22).
- В обычной `#[kani::proof]` goto-instrument проходит, но CBMC кончается по памяти примерно через 2 минуты (job 24). Связь этого OOM с loop contract — гипотеза: контрольного прогона той же гармоники без инварианта не было (review F3).
- Время падения не зависит от объёма инварианта и от циклов в нём (D10–D12). Причина внутри Kani/CBMC не установлена, полного лога нет. Кандидаты (не проверены): вывод `loop_modifies` alias-анализом по встроенному телу, куда попадают контрактные обёртки std (`kani_register_contract` для `ptr::add`, `ptr::sub`, `offset_from` видны в логе); преобразование `for` по `Range`.
- Тело цикла и lane менять нельзя (R2, §5), а pin Kani — это pin CI организаторов. Все OOM получены под лимитом 13 GiB. Хватило бы 16 ГБ раннера организаторов, не проверено. По §2 OUT_OF_MEMORY под 13 GiB — не самостоятельный повод STOP, поэтому формулировка 2 не засчитана как провал (D13, исправлено в фазе 3).

### Находка 4: sort4_stable по типам-массивам (job 24, SHA b838761a, diagnostic)

- `[u8; 16]` — 46,7 с, `[u8; 85]` — 427,3 с. Вместе с u64 (27,5 с, job 9) это объясняет 586 с у `sort4_all` в job 8: почти всё время уходит на `[u8; 85]`. Каждый тип по отдельности укладывается в 600 с.

## Фаза 1

- T0: 2026-10-24T14:57:30Z (`date -u`)
- T0+120 (новые прогоны не запускать): 2026-10-24T16:57:30Z
- T0+140 (конец отчёта): 2026-10-24T17:17:30Z
- Лимиты: ≤ 6 dispatch, сумма таймаутов ≤ 120 мин.

### Журнал прогонов фазы 1

| # | request_id | kind | job | head SHA | гармоники × таймаут | итог |
|---|---|---|---|---|---|---|
| 1 | merge-p1-probe-001 | diagnostic | 6 | c9c38465 | 4 × 10 мин | CircleCI `infrastructure_fail` примерно через 11 мин, артефактов нет: RUNNER_ERROR |
| 2 | merge-p1-probe-002 | diagnostic | 8 | 29da0c3c | 4 × 10 мин | COMPLETE, gate true, check-tooling ok; полное время job 13:16, max RSS 3,8 ГиБ (4 019 032 KiB) |
| 3 | merge-p1-scale-003 | diagnostic | 9 | 00d8cfd4 | 4 × 6 мин | COMPLETE, gate false (`general_u64` TIMEOUT), check-tooling ok; max RSS 11,5 ГиБ |
| 4 | merge-p1-inv-004 | diagnostic | 11 | 222f20f6 | 2 × 8 мин | CircleCI `infrastructure_fail` примерно через 9 мин, артефактов нет: RUNNER_ERROR. Формулировка 2 не проверена |

Сумма таймаутов: 120 из 120 мин, бюджет фазы исчерпан. Dispatch: 4 из 6.

### Находка 2: масштабирование (job 9, SHA 00d8cfd4)

| гармоника | что | статус | время, с |
|---|---|---|---|
| sort4_u64 | sort4_stable, только u64 | SUCCESS | 27,5 |
| bm_u64_len12 | bidirectional_merge, u64, длина 12, формулировка 1 | SUCCESS | 100,0 |
| bm_u64_len16 | то же, длина 16 | SUCCESS | 323,5 |
| general_u64 | верхняя гармоника, длины 0..=32, все callee через stub_verified | TIMEOUT (6 мин) | — |

- **Формулировка 1** (прямое доказательство постусловия, длина разбирается на константы) растёт примерно ×3,2 на +4 длины. Длина 16 занимает 323 с, по экстраполяции предел 600 с — около 18. Длину 32 она не возьмёт. Для FAIL-записи: наибольшая проверенная длина в 10 минут при прямой проверке u64 — 16 (job 9). Длину 18 не замеряли.
- **sort4:** u64 — 27,5 с против 586 с за четыре типа. Время дают типы-массивы `[u8; 16]` и `[u8; 85]`. Measurement надо делать по типам, а стоимость byte-массивов — отдельный открытый вопрос.
- **Композиция:** `general_u64` не уложился в 6 мин при max RSS 11,5 ГиБ из 15. Это первый замер, причина не разобрана: 33 длины в одной гармонике и копии заглушек с проверками на каждом вызове.
- **infrastructure_fail** (job 6 у меня, job 7 у K1-network) совпадает с исчерпанием памяти VM: RSS в job 9 уже 11,5 ГиБ. Тяжёлые гармоники выносить в отдельные запросы.

### Находка 1: проба old() и контроль R11 (job 8, SHA 29da0c3c)

- **old():** `insert_tail` с постусловием перестановки `old(k1_count(..)) == k1_count(..)` компилируется и доказывается. `insert_tail_u64_upto8`: длины региона 2..=8, u64, SUCCESS, 39,4 с, cover 9/9. `old()` берётся от `usize`, ограничение `T: Clone` не возникает (D1, D2).
- **bidirectional_merge, перестановка без old():** компилируется и доказывается. `bm_u64_upto8`: длины 2..=8, u64, SUCCESS, но 110,8 с, cover 9/9. Время растёт быстро, длина 32 этой формулировкой под вопросом, замер в прогоне 3.
- **R11:** `r11_control_bm_requires` дал ожидаемый FAILED, проваленная проверка `CopyOnDrop::<T>::k1_merge_halves_sorted(v, &is_less)` @ smallsort.rs:778. **Предусловия callee в точках `stub_verified` при `--no-assert-contracts` проверяются**, композиция засчитываемая. K1-network независимо получил то же в job 5. Cover контроля 0/1: после провала `kani::assert` Kani обрывает путь, для гармоники с ожидаемым FAILED это ожидаемо.
- **sort4_stable** для четырёх типов в одной гармонике: SUCCESS, 586,3 с, на грани лимита 600 с. Measurement будет по типам отдельно.

## 1. Вердикт

**ФАЗА 6: ЗАКЛЮЧЕНИЕ K1-merge (не вердикт K-1) — блокер в инструменте под лимитом 13 GiB, и обычная proof формулировки 3 не укладывается в 10 минут.** На Kani `9461e07a` пути к контракту `bidirectional_merge` на длине 32 за 10 минут, который можно связать со `stub_verified`, не найдено.
- **Основание 1 — инструмент.** Под `proof_for_contract` с loop contract `goto-instrument` падает по памяти (13 GiB), как только в `ensures` есть счётчик перестановки (job 35, SHA 094c3287; без счётчика проходит — job 40, SHA 859391c9). Перестановку без счётчика на SAT-бэкенде, по моему рассуждению, не выразить (находка 8, не проверено прогоном). Исключено: тяжёлая развёрнутая спецификация (job 29), лёгкий счётчик по типу с тривиальным инвариантом (job 35), он же с настоящим инвариантом (job 36), `forall` как причина (job 40). Блокер — OOM под 13 GiB; по §2 это не самостоятельный повод STOP, на 16 GB не проверено.
- **Основание 2 — цена в CBMC.** В обход связки, в обычной `#[kani::proof]`, инвариант формулировки 3 на длине 32 u64 — TIMEOUT 10 минут (job 41, SHA 5c0b06c1). Без счётчика — тоже TIMEOUT (job 42, SHA fa5ca00e). Память в обоих меньше 2 GiB. Значит, обойти инструмент мало: обычная гармоника с формулировкой 3 на длине 32 не укладывается. Что внутри дорого (инвариант, его части, атрибуты контракта на функции), не измерено — гипотеза.
- **Не проверено:** счётчик с простыми загрузками и `wrapping_add` (job 38) при тривиальном инварианте — job 38 шёл с полным `k1_bm_inv3`, где есть второй счётчик; применён ли loop contract в обычной proof (Kani печатает вывод `goto-instrument` только при ошибке); влияют ли на обычную proof атрибуты контракта, остававшиеся на `bidirectional_merge` в job 41, 42; `exists!` с константными границами на SAT и z3 (`#[kani::solver(z3)]`); время формулировки 3 на длинах меньше 32 и без таймаута; где тратит время CBMC; другие версии Kani; другая форма инварианта (например, без кванторов, на длине 32 развёрнутая); 16 GB раннера организаторов (`goto-instrument` упирался в 13 GiB).
- **Что потребовалось бы от владельца:** (а) другая версия Kani, где `proof_for_contract` с loop contract инструментирует развёрнутый счётчик; (б) отчёт в Kani об OOM `goto-instrument` в этой связке (воспроизведение — job 35 против job 40); (в) решение, допустим ли иной способ связать доказательство со `stub_verified` (например, обычная proof постусловия вместо `proof_for_contract`). Но основание 2 говорит, что и тогда нужен более дешёвый инвариант. (г) прогон `goto-instrument` для job 35 с памятью от 16 GB (раннер организаторов); (д) для коротких длин остаётся формулировка 1: длина 16 за 323,5 с (job 9).
- **Счётчики STOP на конец фазы 6** (09:45 UTC): 1 формулировка из 3 по букве правил, 2 из 3, если засчитать job 41/42 (D23). Без продвижения — около 138 из 180 минут: 108 на входе, 30 в фазе 6.
- **Ветка:** коммит восстановления `4f17fcd5782df3e9877ed7e20637f6b9c25fa3ad`; `smallsort.rs` совпадает с 26049195 — формулировка 1, атрибута на цикле нет (D22). Для K1-network в силе абзац F1.
- R9 review обязателен по заданию фазы 6 — раздел 7. macOS: не измерено, проверяется на этапе подачи.

### Итог фазы 5

**ФАЗА 5: INCONCLUSIVE на 13 GiB. Главный вопрос K-1 не решён: берёт ли формулировка 3 `bidirectional_merge` на длине 32 — неизвестно.**
- **Что произошло:** три прогона формулировки 3 на `bm_u64_len32` — job 35 (тривиальный инвариант), job 36 (настоящий инвариант) и job 38 (одна правка: спецификация без `ptr::add`/`read_unaligned`). Все три упали в `goto-instrument` по памяти, CBMC не запускался (находка 7). По правилу фазы 5 исход «только по памяти» — INCONCLUSIVE, не провал формулировки и не STOP. R9 не нужен.
- **Сколько памяти не хватило:** по логу не установить. Пик cgroup равен пределу 13,00 GiB, `goto-instrument` размеров не печатает.
- **Счётчики STOP на конец фазы 5** (08:33 UTC): по §2 проверена 1 формулировка из 3 — формулировка 3 не провалена. Минут без продвижения — около 108 из 180: 90 на входе и 18 в фазе 5. Доказанных фрагментов `bidirectional_merge` нет.
- **Ветка:** формулировка 1, атрибута на цикле нет; лёгкие помощники в `merge.rs` (D20). Для K1-network в силе абзац F1: контракты `insert_tail` и `bidirectional_merge` в текущей редакции не доказаны ни на одной длине. Лёгкие помощники — коммит 2665ea3f, они компилируются. Итоговая редакция с простыми загрузками — 1e906d61.

### Передача (для фазы 6)

Блокер уже не размер спецификации в CBMC, а `goto-instrument` в связке «`proof_for_contract` + loop contract». Даже лёгкая спецификация (два `forall` и 64 загрузки) перегружает его, а обычная proof с тяжёлым инвариантом проходила (job 24). Предлагаемые шаги, по одной гармонике на запрос, все diagnostic:
1. **Атрибуция (2 коротких прогона, OOM наступает за 2–3 минуты):** контракт job 32 плюс отдельно (а) `forall` в `requires` или (б) `k1_perm_l` в `ensures`. Это ответит, что из двух переполняет `goto-instrument`.
2. **Цена инварианта формулировки 3 в CBMC отдельно от проверки контракта:** обычная `#[kani::proof]`. В ней `kani::assume` по `requires` через `forall`, вызов `bidirectional_merge` с `k1_bm_inv3` на цикле, затем `assert` по `ensures`. Обходит связку, на которой падает `goto-instrument`. Ответит, по силам ли CBMC сам инвариант на длине 32 и за сколько. `stub_verified` такой proof не даёт (R4), поэтому это измерение, а не доказательство контракта.
3. Если (2) укладывается в 10 минут, а `proof_for_contract` не проходит — это ограничение pin Kani `9461e07a`, а не формулировки. Тогда нужно решение владельца: допустим ли для `bidirectional_merge` иной способ связать доказательство с `stub_verified`.

**Оценка:** шаги 1–2 — одна фаза, 3 dispatch. До PASS — не меньше 4–6 фаз, и только если шаг 3 решаем.

### Итог фазы 4

**ФАЗА 4 ЗАВЕРШЕНА. Вердикт фазы 3 FAIL (STOP) отозван.**
- **Основание отзыва:** job 30 (SHA b94fac35). Тот же цикл, тот же тривиальный инвариант и тот же явный `loop_modifies`, что в job 29, но с тривиальным контрактом функции, — и `goto-instrument` проходит. Job 32 (SHA 188451df): проходит и сортированность через `forall!`. Исключение формулировки 2 в фазе 3 опиралось на job 29, а там падение вызывала тяжёлая спецификация функции, а не loop contract (находка 6).
- **Счётчики STOP на конец фазы 4** (21:47 UTC): по §2 проверена 1 формулировка из 3; формулировка 2 не провалена — до проверки по существу не дошло. Минут без продвижения — около 90 из 180: 73 к концу фазы 3 и 17 в фазе 4. Доказанных фрагментов `bidirectional_merge` нет.
- Это промежуточный итог, не вердикт K-1. Review по §9 не нужен. macOS: не измерено, проверяется на этапе подачи.

### Передача (для фазы 5)

**Кандидат третьей формулировки — лёгкая спецификация плюс настоящий инвариант цикла:**
1. **Сортированность** в `requires` (половины) и в `ensures` — одним `forall!` по константному диапазону `1..32` с охраной по длине, как `k1_sorted_q` (job 32 прошёл инструментацию). В инварианте так же: оба отсортированных конца выхода.
2. **Перестановка** кванторами не выражается: это равенство сумм. Варианты по возрастанию риска:
   - (а) оставить счётчик пробы, но сделать его лёгким. `is_probe` специализировать по типу через трейт, как `K1BmInv`: для `u64`/`i32`/`u8` одно сравнение, для `[u8; 16]` два слова, для `[u8; 85]` одиннадцать сравнений. Сейчас на каждый элемент до 19 охраняемых сравнений, которые goto-instrument не сворачивает. Тогда `k1_count_u` — это 32 охраняемых сравнения на вызов. Проверять отдельным прогоном: тривиальный инвариант плюс `ensures` со счётчиком, проходит ли goto-instrument;
   - (б) если и лёгкий счётчик не проходит — `exists!` с биекцией. Требует z3 и вряд ли укладывается в 10 минут, последний резерв.
3. **Инвариант:** `k1_bm_inv_core` (учёт указателей, концы выхода, межполовинные соотношения) с сортированностью через `forall!` и сохранение счётчика через лёгкий `k1_count_u`. Учёт указателей нужен и для CBMC: с тривиальным инвариантом CBMC кончается по памяти (job 24, 30, 32, гипотеза в находке 6).
4. **Порядок прогонов** (одна гармоника на запрос, `bm_u64_len32`, diagnostic):
   - (1) тривиальный инвариант + `forall` в `requires`/`ensures` + лёгкий счётчик в `ensures` — проходит ли инструментацию;
   - (2) полный инвариант формулировки 3 — проходит ли CBMC и за сколько.
   - Если (2) даёт SUCCESS за 600 с или меньше, это ответ на главный вопрос фазы 2, дальше `bm_u64` на 2..=32 и остальные типы. Если OOM или TIMEOUT при рабочей инструментации — это проверка формулировки 3 по §2.

**Состояние ветки** — `26049195`: формулировка 1 как на d7c91adc. Для K1-network в силе абзац review F1: на HEAD контракты `insert_tail` и `bidirectional_merge` в текущей редакции не доказаны ни на одной длине.

**Оценка:** до ответа, берёт ли формулировка 3 длину 32, — 1–2 фазы по 3–4 прогона. Основание: два шага инструментации из п. 4, а каждый прогон с OOM длится около 6 минут. До PASS при положительном ответе — ещё 4–6 фаз (оценка фазы 2).

### Вердикт фазы 3 (отозван в фазе 4)

**Цепочка general: FAIL (STOP)** — отозван, см. выше. Причина: контракт `bidirectional_merge` не доказан на длине 32 за 10 минут ни одной формулировкой. macOS: не измерено, проверяется на этапе подачи.

- **Формулировка 1** (прямое доказательство): наибольшая проверенная длина в 10 минут — 16, `bm_u64_len16` за 323,5 с (job 9, SHA 00d8cfd4). Время растёт примерно ×3,2 на +4 длины. Длину 18 не замеряли.
- **Формулировка 2** (инвариант цикла) исключена инструментом. Любой loop contract на цикле `bidirectional_merge`, включая тривиальный с явным `loop_modifies`, даёт OOM goto-instrument под `proof_for_contract` при лимите 13 GiB: job 17, 19–22, 29. В обычной proof OOM случился уже в CBMC (job 24), его связь с контрактом цикла — гипотеза. Исключение опирается на job 29: явный `loop_modifies` падает так же. Игрушечный контроль (job 27) не различающий и в основание не входит.
- **Третьей формулировки** нет: кандидата, который по оценке брал бы длину 32, у меня нет (передача фазы 2, п. 2).
- **Основание вердикта** — правило итога фазы 3 из TASK-merge.md, а не порог «три формулировки» из §2: по §2 проверена одна формулировка из трёх. Вывод о 16 ГБ раннера организаторов не проверен: все OOM получены под лимитом 13 GiB, и по §2 OUT_OF_MEMORY под 13 GiB сам по себе не повод STOP.
- **Для K1-network: на HEAD ни один из двух контрактов не доказан в текущей редакции клауз ни на одной длине** (review F1).
  - `bidirectional_merge`: текущие клаузы (`k1_sorted_u`/`k1_count_u`, `requires(v.len() >= 2 && v.len() <= 32)`, `is_probe` без циклов) появились после job 19. Ни одного SUCCESS для них нет: job 20–22 и 29 упали в goto-instrument, job 24 — обычная proof. SUCCESS есть только у прежней редакции (`k1_sorted`/`k1_count` с циклами, `is_probe` с циклами): u64, длины 2..=8 и 12, 16 (job 8 на 29da0c3c, job 9 на 00d8cfd4).
  - `insert_tail`: доказан только u64 с регионом 2..=8 и прежним `is_probe` (job 8 на 29da0c3c). `insert_tail_int`/`insert_tail_bytes` не запускались.
  - `bm_u8` (для `small_sort_network`) и `bm_{i32,b16,b85}` не запускались. Kani не сверяет инстанциацию заглушки с доказанной (D4), поэтому `stub_verified` на этих контрактах по R4 пока не засчитывается.

Счётчики STOP на конец фазы 3 (21:09 UTC): по §2 проверена 1 формулировка из 3. Минут без продвижения — около 73 из 180: 63 к концу фазы 2 и 10 в фазе 3, с 20:58 до 21:09.

Review R9 — раздел 7.

### Итог фазы 2 (исходная редакция, исправлена в фазе 3)

**ФАЗА 2 ЗАВЕРШЕНА.** Это не вердикт K-1: PASS и STOP не наступили. Ответ на главный вопрос фазы: ни одна проверенная формулировка контракта `bidirectional_merge` не берёт длину 32 за 10 минут. Формулировка 1 растёт примерно ×3,2 на +4 длины (16 — 323 с). Формулировка 2, инвариант цикла, не проходит инструментацию Kani `9461e07a` под лимитом 13 GiB даже с тривиальным инвариантом (находка 3); при 16 ГБ не проверялась. По §2 это OUT_OF_MEMORY, а не провал формулировки. *(Исправлено в фазе 3: в исходной редакции было «до STOP осталась одна формулировка».)* macOS: не измерено, проверяется на этапе подачи.

### Счётчики STOP (bidirectional_merge), конец фазы 2 (20:35 UTC)

- Формулировки, проверенные diagnostic-прогоном: **1 из 3** по §2. Формулировка 1 — прямое доказательство (job 8, 9): наибольшая проверенная длина в 10 минут — 16, 323 с. Формулировка 2 — инвариант цикла (job 17, 19–22, 24): OUT_OF_MEMORY под 13 GiB при любом инварианте. По §2 это не провал, поэтому она не засчитана (D13). *(Исправлено в фазе 3: в исходной редакции было «2 из 3».)*
- Минуты работы без продвижения: **около 63 из 180.** Это 15 минут фазы 1 и 48 минут фазы 2, с 19:47 до 20:35. Доказанных фрагментов `bidirectional_merge` или больших длин в фазе 2 нет. `sort4` по типам — продвижение по другому callee, оно счётчик не сбрасывает.

### Передача (для фазы 3)

**Доказано в фазе 2** (diagnostic, в зачёт по §2 п. 4 не идёт): `sort4_stable` для `[u8; 16]` за 46,7 с и `[u8; 85]` за 427,3 с (job 24, SHA b838761a, check-tooling ok).

**Состояние ветки** (коммит после b838761a, прогоном не проверялся):
- Атрибут `loop_invariant` с цикла снят: с ним любая гармоника, которая доходит до тела `bidirectional_merge`, падала по памяти, в том числе `bm_u8` у K1-network. Ветка снова в состоянии формулировки 1. Код инварианта (`k1_bm_inv*`, трейт `K1BmInv`) оставлен неподключённым. Гармоники бисекции удалены, они есть в b838761a.
- Контракт `bidirectional_merge` изменён (D11): `requires(v.len() >= 2 && v.len() <= 32)`, а ensures и `k1_merge_halves_sorted` используют развёрнутые `k1_sorted_u`/`k1_count_u` вместо циклов. Код скомпилирован в job 20–24, но контракт с этими клаузами ещё не доказан ни одним SUCCESS. Для K1-network: новый `requires(len <= 32)` выполняется на всех call sites (порог 32).
- `is_probe` без циклов (D10): действует во всех гармониках. `sort4_b16`/`sort4_b85` в job 24 прошли уже с ним.
- Добавлены и не запускались: `sort4_i32`, `sort8_{i32,u64,b16}` (`stub_verified` на `sort4_stable` и `bidirectional_merge`), `bm_u64_len32`, `general_u64_len32` (одна длина, макрос `general_band!` для семейства полос).

**Следующий шаг (фаза 3):**
1. Единственный недорогой вопрос по формулировке 2: явный `#[kani::loop_modifies(..)]` вместо вывода alias-анализом. Тривиальный инвариант, один прогон, одна гармоника. Если goto-instrument и CBMC проходят, вернуть полный инвариант. Риски: исходный `dst` затенён, а итератор `for` назвать нельзя. Если явный modifies не принимается или падает так же, loop contracts на этом цикле закрыты.
2. Третья формулировка без loop contract. Кандидатов, которые по оценке берут длину 32, у меня нет. Контракты на `merge_up`/`merge_down` не сокращают развёртку: шаг остаётся таким же точным, как тело. Перестановку можно выразить иначе, но по SAT-стоимости все известные мне варианты не дешевле счётчика пробы, а редукции для перестановки на типах general запрещены (R5). Если пункт 1 не даст результата, честный исход — STOP по §2: наибольшая длина в 10 минут при прямой проверке u64 — 16 (job 9). Перед STOP нужен review R9.
3. Только если формулировка 2 оживёт: `bm_u64_len32` → `bm_u64` → остальные `bm_*`, затем `sort8_*` и полосы `general_*`.

**Оценка до PASS или STOP:** до STOP — 1–2 часа, одна фаза: один прогон по `loop_modifies`, при отказе оформить STOP и пройти review. До PASS, если явный modifies сработает и инвариант окажется быстрым, — 6–10 часов, 4–6 фаз: осталось около 20 measurement-гармоник по ≤ 4 на прогон и неизвестная стоимость композиции. Основание: за фазу 2 шесть прогонов подряд кончились OOM при любом содержании инварианта.

### Передача фазы 1

**Доказано** (всё diagnostic, в зачёт по §2 п. 4 пока не идёт; тот же Kani pin, check-tooling ok):
- Контроль R11: FAILED на `k1_merge_halves_sorted` (job 8, SHA 29da0c3c). Предусловия в точках `stub_verified` проверяются.
- Контракт `insert_tail` с перестановкой через `old(count)`: u64, длины региона 2..=8, 39 с (job 8).
- Контракт `bidirectional_merge`, формулировка 1: u64, длины 2..=8 за 111 с (job 8); длина 12 за 100 с, длина 16 за 323 с (job 9, SHA 00d8cfd4).
- Контракт `sort4_stable`: четыре типа вместе за 586 с (job 8), u64 отдельно за 27,5 с (job 9).

**Начато, но не проверено:**
- Формулировка 2 для `bidirectional_merge` (D9). Код на ветке начиная с 222f20f6: атрибут `loop_invariant` в `smallsort.rs`, `k1_bm_inv` в `merge.rs`. Job 11 умер с `infrastructure_fail`. **Внимание:** инвариант стоит на цикле, поэтому с этого SHA все прогоны `bidirectional_merge`, включая `sort8_stable`, идут через loop contract. Чтобы повторить формулировку 1, атрибут нужно убрать.
- Контракт `sort8_stable` и гармоника `sort8_all`: написаны, не запускались.
- `insert_tail_int` и `insert_tail_bytes` (длины 2..=16), `bm_{u8,i32,u64,b16,b85}` (2..=32): написаны, не запускались.
- Верхние гармоники `general_{i32,u64,b16,b85}`: реальные trait entrypoints, длины 0..=32, `stub_verified` на всех четырёх callee, cover на 0, 1, 2, 7, 8, 15, 16, 32. `general_u64` дал TIMEOUT за 6 мин при RSS 11,5 ГиБ (job 9).

**Следующий шаг:**
1. Главный риск lane: четыре тяжёлых прогона обоих агентов (мои job 6 и 11, у K1-network job 7 и 12) кончились `infrastructure_fail` без артефактов. Совпадает с исчерпанием 15 ГиБ: RSS в job 9 — 11,5 ГиБ. Предложение координатору (файлы lane не мои): ограничить память шага verify, например `prlimit --as` или `systemd-run -p MemoryMax=13G`. Тогда OOM станет TOOL_ERROR или PARTIAL со сводкой, а не потерей job. До этого — **одна тяжёлая или непроверенная гармоника на запрос.**
2. Перезапустить формулировку 2 по одной: сначала `bm_u64_len16` (без инварианта было 323 с), затем `bm_u64` (2..=32).
3. Если формулировка 2 не проходит, следующий кандидат, формулировка 3: тот же инвариант без счётчика пробы плюс отдельное доказательство перестановки, или контракты на `merge_up`/`merge_down` с инвариантом над ними.
4. Композиция: разбить `general_*` на полосы длин (например, 0..=15, 16..=23, 24..=32) — критерий допускает семейство гармоник. Проверить гипотезу, что дорого обходится доказательство равенства сумм счётчиков с разной группировкой слагаемых (сумма по 32 элементам против сумм по половинам).
5. Стоимость типов-массивов: `sort4` для `[u8; 16]`/`[u8; 85]` — около 560 с из 586.
6. Measurement-прогоны по одной гармонике на тип для `sort4`, `insert_tail` и `sort8`.

**Оценка до PASS или STOP:** 8–14 часов работы агента, 5–7 фаз. Основание: каждый прогон длится 13–15 минут, тяжёлые гармоники приходится запускать по одной, в фазе не больше 6 прогонов. Осталось 19 measurement-гармоник плюс неизвестная стоимость композиции. Раньше может наступить STOP: если формулировки 2 и 3 не возьмут длину 32, наибольшая длина в 10 минут для прямой проверки u64 — 16 (job 9).

## 2. Таблица обязательств

Все прогоны — `diagnostic` на `circleci-linux-large`. Measurement-прогонов нет, в зачёт по §2 п. 4 ничего не идёт. Память — max RSS всего прогона вместе с компиляцией std, KiB / 2²⁰. check-tooling для фазы 1 — против базы `77479d23`, для фаз 2–3 — против `aca80458`.

| Обязательство | Гармоника | request_id | job | head SHA | раннер | статус | время | память | cover | check-tooling |
|---|---|---|---|---|---|---|---|---|---|---|
| R11, контроль предусловий в точке `stub_verified` | `r11_control_bm_requires` | merge-p1-probe-002 | 8 | 29da0c3c | circleci-linux-large | FAILED, как ожидалось (`k1_merge_halves_sorted`) | 0,18 с | 3,8 GiB | 0/1 (путь обрывается провалом) | ok |
| `insert_tail`, u64, регион 2..=8 | `insert_tail_u64_upto8` | merge-p1-probe-002 | 8 | 29da0c3c | circleci-linux-large | SUCCESS | 39,4 с | 3,8 GiB | 9/9 | ok |
| `bidirectional_merge` ф. 1, u64, 2..=8 | `bm_u64_upto8` | merge-p1-probe-002 | 8 | 29da0c3c | circleci-linux-large | SUCCESS | 110,8 с | 3,8 GiB | 9/9 | ok |
| `sort4_stable`, четыре типа | `sort4_all` | merge-p1-probe-002 | 8 | 29da0c3c | circleci-linux-large | SUCCESS | 586,3 с | 3,8 GiB | 5/5 | ok |
| `sort4_stable`, u64 | `sort4_u64` | merge-p1-scale-003 | 9 | 00d8cfd4 | circleci-linux-large | SUCCESS | 27,5 с | 11,5 GiB | 1/1 | ok |
| `bidirectional_merge` ф. 1, u64, длина 12 | `bm_u64_len12` | merge-p1-scale-003 | 9 | 00d8cfd4 | circleci-linux-large | SUCCESS | 100,0 с | 11,5 GiB | 1/1 | ok |
| `bidirectional_merge` ф. 1, u64, длина 16 | `bm_u64_len16` | merge-p1-scale-003 | 9 | 00d8cfd4 | circleci-linux-large | SUCCESS | 323,5 с | 11,5 GiB | 1/1 | ok |
| верхняя general, u64, 0..=32 | `general_u64` | merge-p1-scale-003 | 9 | 00d8cfd4 | circleci-linux-large | TIMEOUT (6 мин) | — | 11,5 GiB | — | ok |
| `bidirectional_merge` ф. 2, u64 (разные кодировки и бисекция) | `bm_u64`, `bm_u64_len32`, `bm_bisect_*` | merge-p2-inv-005…bisect-009 | 17, 19, 20, 21, 22 | 12984437…a77b38f6 | circleci-linux-large | NOT_RUN, OOM goto-instrument | — | 13 GiB (лимит) | — | ok |
| то же, обычная proof | `bm_bisect_plain_trivial_u16` | merge-p2-bisect-010 | 24 | b838761a | circleci-linux-large | OUT_OF_MEMORY (CBMC) | — | 11,7 GiB | — | ok |
| `sort4_stable`, `[u8; 16]` | `sort4_b16` | merge-p2-bisect-010 | 24 | b838761a | circleci-linux-large | SUCCESS | 46,7 с | 11,7 GiB | 1/1 | ok |
| `sort4_stable`, `[u8; 85]` | `sort4_b85` | merge-p2-bisect-010 | 24 | b838761a | circleci-linux-large | SUCCESS | 427,3 с | 11,7 GiB | 1/1 | ok |
| контроль инструмента: игрушечный loop contract | `toy_loop_contract` | merge-p3-toy-011 | 27 | d83f3144 | circleci-linux-large | SUCCESS | 0,11 с | 1,5 GiB | 2/2 | ok |
| ф. 2, явный `loop_modifies`, тривиальный инвариант | `bm_u64_len32` | merge-p3-modifies-013 | 29 | 26a3f824 | circleci-linux-large | NOT_RUN, OOM goto-instrument | — | 13 GiB (лимит) | — | ok |

Не запускались: `sort4_i32`, `sort8_*`, `insert_tail_int`/`insert_tail_bytes`, `bm_{u8,i32,b16,b85}` на 2..=32, `general_{i32,b16,b85}`, `general_u64_len32`.

## 3. Редукции

Нет. Ширина u8, принцип 0–1 и ограниченный домен значений не применялись. Сравнение с пробой — по полному значению (D1).

## 4. Журнал решений

- **D1. Перестановка через пробное значение.** Глобальный байтовый буфер `K1_PROBE` гармоника заполняет произвольным значением в начале. Контракт утверждает: число элементов, побайтно равных пробе, сохраняется. В proof_for_contract проба произвольна, значит доказано для всех значений, а это равенство мультимножеств по полному значению. Под `stub_verified` одна проба действует для всех заглушек и для итоговой проверки, поэтому композиция корректна. Побайтное равенство совпадает с равенством значений, потому что у типов K-1 нет padding. Это не редукция (R5): домен значений не ограничен. Альтернативы: подсчёт по всем элементам O(n²), он требует транзитивности перестановок на уровне SAT; `old()` от копии массива, он требует `T: Clone`. Обе отвергнуты.
- **D2. `old()` только от `usize`.** `old(count(...))` клонирует `usize`, ограничение `T: Clone` не возникает (§7).
- **D3. Сортированность через comparator.** Клаузы контракта Kani — `Fn`-замыкания (`apply_closure<U: Fn>`), а `is_less: &mut F` с `F: FnMut`. Хелпер `call_less` вызывает его через приведение `*const &mut F` → `*mut`. Это корректно для comparator гармоник: они без состояния, function items. Строгий слабый порядок фиксируют конкретные comparator: ключ `x >> 1` для целых, `a[0]` для массивов. Ключи совпадают у элементов с разными полными значениями, поэтому перестановка не следует из сортированности.
- **D4. Инстанциации.** Kani не сверяет инстанциацию заглушки с инстанциацией proof. Поэтому proof_for_contract пишется для каждой пары (T, F), которую заглушают верхние гармоники, а F — общий function item.
- **D5. Хелперы как inherent-методы `CopyOnDrop<T>`.** `kani_k1.rs` объявляет `mod merge;` приватным, и атрибуты в `smallsort.rs` не могут назвать `kani_k1::merge`. Inherent-методы с `pub(crate)` видны из `smallsort` и не требуют правки чужих файлов.
- **D6. Конкретные длины внутри одной гармоники.** Символьная длина `len ∈ 0..=32` разбирается `match` на константные N (`by_len!`), поэтому у всех циклов константные границы. Это одна гармоника на реальном entrypoint, а не семейство гармоник.
- **D7. `#[kani::unwind(34)]` после job 6.** Причина `infrastructure_fail` неизвестна: лог не выгружен. Гипотеза — неограниченная развёртка, если константа где-то теряется. Отсюда страховочная граница 34 (самый длинный цикл — 32 элемента) и сравнение с пробой словами по 8 байт: `compare_bytes`/memcmp крутил бы 85 итераций для `[u8; 85]`. Если 34 не хватит, Kani сообщит провал unwinding assertion, ложного PASS не будет.
- **D8. `use crate::kani;` в `smallsort.rs`** стоит перед `mod kani_k1;`. Он нужен для `kani::requires` и для кода, который генерируют макросы. K1-network добавил ту же строку в то же место.

- **D9. Формулировка 2 для bidirectional_merge — инвариант цикла** (`k1_bm_inv`, атрибут `cfg_attr(kani, kani::loop_invariant(..))` на цикле, R2). Содержание: учёт указателей (a, b, c, d — сколько потреблено с каждого конца половин, u — длина выхода с каждого конца); оба конца выхода отсортированы; последний выход снизу ≤ оставшихся ≤ последний выход сверху; четыре межполовинных соотношения между потреблённым и оставшимся, они нужны, когда голова исчерпана и merge читает устаревший элемент, два из них строгие; сохранение счётчика пробы. Смещения считаются по адресам с проверкой кратности размеру: указатели после havoc иначе вызвали бы проверку UB у `offset_from`. `loop_modifies` выводит Kani; если вывод неполон, Kani сообщает провал, а не ложный успех.

- **D10. `is_probe` без циклов (фаза 2, после job 17).** С `-Z loop-contracts` CBMC развёртывает циклы без контракта ещё в goto-instrument, до распространения констант (WARNING «transformed loops will not be unwound after applying loop contracts»), а DFCC встраивает вызовы из инварианта в функцию с контрактом цикла. Два цикла `is_probe` внутри цикла `k1_count` давали 34 × 68 копий тела на каждый из пяти вызовов `k1_count` в инварианте, и так в трёх местах (база, предположение, шаг). goto-instrument превысил 13 GiB за 2 минуты. Теперь `is_probe` — до 16 охраняемых сравнений словами по 8 байт и хвост 4/2/1 байта, без циклов. Семантика та же: побайтное равенство с пробой. Альтернатива — `kani::forall!` в инварианте — не выражает подсчёт, отвергнута. Это исправление кодировки, а не новая формулировка: счётчик формулировок не растёт.

- **D11. Спецификация `bidirectional_merge` без циклов (после job 19).** И с `is_probe` без циклов goto-instrument упал по памяти; в функции с контрактом цикла после встраивания оставались одиночные циклы `k1_sorted` и `k1_count`. По логу не видно, пришли они из инварианта или из клауз контракта. Поэтому инвариант и клаузы контракта `bidirectional_merge` переведены на `k1_count_u`/`k1_sorted_u`: развёртка макросом на 32 шага с охраной `i < len`, без циклов. Развёртка верна только при длине ≤ 32, отсюда `requires(v.len() <= 32)`. Его выполняют все реальные call sites: порог general и network равен 32, `sort8_stable` передаёт 8. Инвариант при `len > 32` ложен. Альтернатива — ограничить развёртку через `#[kani::unwind]` поменьше — не убирает циклы из встроенного кода и отвергнута.

- **D12. Бисекция OOM в одной сборке (после job 20).** Три падения (job 17, 19, 20) наступали примерно через минуту работы goto-instrument, и объём инварианта на это не влиял. Это похоже на структурную проблему loop contract на этом цикле, а не на размер кода. Инвариант выбирается трейтом `K1BmInv` со специализацией по типу элемента: `u16` — тривиальный `idx <= len / 2`, `i16` — всё, кроме счётчика пробы, остальные типы — полный. `u16` и `i16` встречаются только в гармониках `bm_bisect_*`, их результат в зачёт не идёт. Kani обходит гармоники по алфавиту и обрывает прогон на первом падении goto-instrument, поэтому порядок от тривиального к полному показывает границу. Альтернатива — три отдельных прогона — съела бы оставшиеся dispatch фазы.

- **D13. Статус формулировки 2 после фазы 2 (исправлено в фазе 3).** Шесть прогонов: полный инвариант в трёх кодировках (job 17, 19, 20), бисекция (job 21) и тривиальный инвариант (job 22 под `proof_for_contract`, job 24 в обычной proof). Все кончились OOM под лимитом 13 GiB, и содержание инварианта на исход не влияло. Укладывается ли прогон в 16 ГБ раннера организаторов, не проверено. По §2 OUT_OF_MEMORY под 13 GiB — не самостоятельный повод STOP, поэтому формулировка 2 не засчитана как провал. Первая редакция D13 («не может … на 16 ГБ», засчитана 2 из 3) делала непроверенный вывод и заменена. Исключить формулировку 2 может правило фазы 3 (TASK-merge.md): OOM на игрушечном цикле (свойство инструмента), либо явный `loop_modifies` не принимается или падает так же.
- **D14. Атрибут инварианта снят с цикла в конце фазы 2.** Ветку забирает K1-network, а с атрибутом любой прогон `bidirectional_merge` без заглушки падал. Альтернатива — оставить атрибут для фазы 3 — ломала бы чужие и свои прогоны формулировки 1.

- **D15. Вердикт FAIL (STOP) по правилу фазы 3 (после job 29).** Явный `loop_modifies` падает так же, значит, по TASK-merge.md формулировка 2 исключена. Кандидата для третьей формулировки нет. Альтернатива — «ФАЗА 3 ЗАВЕРШЕНА» без вердикта — по правилу фазы 3 допустима, только если формулировка 2 не исключена. Диагностический атрибут снят с цикла, ветка в состоянии формулировки 1.
- **D17. Отзыв вердикта (фаза 4).** Правило фазы 4 (TASK-merge.md): если `goto-instrument` пройден при тривиальном контракте функции, вердикт FAIL (STOP) отзывается. Job 30 прошёл. Прогон B потрачен на кванторы, а не на повтор A: вопрос задания — проходит ли инструментацию спецификация с кванторами, и ответ на него задаёт кандидата третьей формулировки. Альтернатива — B с настоящим `k1_bm_inv_core`, чтобы проверить гипотезу о CBMC, — меняла бы две переменные сразу.
- **D16. Ошибка процесса в фазе 3.** Запрос job 28 не прошёл валидатор (`purpose` длиннее 300 символов), но commit и dispatch стояли в той же команде на отдельных строках и выполнились. Dispatch потрачен впустую. Дальше validate, commit и dispatch связаны через `&&`.
- **D18. Прогон 1 не пропущен, прогоны 1 и 2 запущены параллельно (фаза 5).** Альтернативы: (а) пропустить прогон 1 и сохранить dispatch на вторую длину или тип; (б) прогоны по очереди. Выбрано: прогон 1 (job 35) и прогон 2 (job 36) на разных SHA одновременно. Причина: если прогон 2 упадёт в `goto-instrument`, без прогона 1 не различить, мешает счётчик или инвариант. Параллельный запуск не стоит времени, а третий dispatch остаётся на одну правку формулировки по п. 4 задания. Цена — при успехе прогона 2 нет запасного прогона на вторую длину. Таймаут прогона 1 — 8 минут: в нём ожидается OOM в CBMC около шестой минуты (job 30, 32), сумма 8 + 10 оставляет 12 минут на правку.
- **D19. Правка формулировки 3 третьим dispatch (после job 35, 36).** Прогон 1 отличается от job 32 (инструментация прошла) двумя `forall` в `requires` и лёгким счётчиком в `ensures`, то есть 64 пробами. Этого хватило для OOM в `goto-instrument`. Значит, память растёт не от числа сравнений в пробе, а от объёма кода спецификации. Гипотеза, не проверена: Kani кладёт `requires`/`ensures` в ту же функцию, что и тело с циклом. Перед применением loop contract DFCC её целиком инлайнит, а анализ указателей по этой функции растёт быстрее линейного. Каждое `ptr::add` и `read_unaligned` в спецификации инлайнится с библиотечным телом и UB-проверками. Квантор — одно выражение, поэтому job 32 прошёл. Правка в пределах формулировки 3, кодировка та же: в лёгком счётчике, в счётчике инварианта и в `k1_bm_inv_core` `ptr::add` заменён на `wrapping_add`, проба целых — простая загрузка `*p` вместо `read_unaligned`. Альтернативы: (а) `exists!` с z3 — последний резерв по заданию; (б) отдельный прогон на атрибуцию (`forall` в `requires` или счётчик) — dispatch последний, атрибуция не даёт ответа на главный вопрос. Выбрано: правка с настоящим инвариантом, measurement.
- **D20. Ветка на конец фазы 5.** Коммит восстановления — `81934063b5d31f0b015c41528297e89a02184825`. Формулировка 3 не доказана ни на одной длине, поэтому атрибут инварианта с цикла снят (D14): `smallsort.rs` возвращён к 26049195, это формулировка 1 с контрактом на `k1_sorted_u`/`k1_count_u`. В `merge.rs` остались лёгкие помощники: `K1Probe` (целые — простая загрузка), `k1_count_l`, `k1_perm_l`, `k1_merge_halves_sorted_q`, `k1_bm_inv3`, `k1_bm_inv_count_l`. Они компилируются (job 35, 36, 38), но ни в одном доказанном контракте не участвуют. `k1_bm_inv_core` теперь проверяет сортированность через `k1_sorted_q` и строит указатели через `wrapping_add`. Запись формулировки 2 в исходном виде — на 312576a9.
- **D21. План фазы 6.** Ориентир — передача фазы 5, отступлений нет. Прогоны 1 (атрибуция, job 40) и 2 (обычная proof с `k1_bm_inv3`, job 41) шли параллельно на разных SHA. Третий dispatch выбран после них. Альтернативы: (а) вторая атрибуция — счётчик без `forall`. Не нужна: job 40 и 35 уже различаются ровно счётчиком. (б) Обычная proof на длине 16, чтобы сравнить с формулировкой 1 (323,5 с, job 9). Отложена: она не отвечает, укладывается ли длина 32. (в) Обычная proof без счётчика (job 42) — выбрана: она различает, счётчик ли делает CBMC дорогим.
- **D22. Ветка на конец фазы 6.** Контракт не доказан, атрибут инварианта с цикла снят (D14): `smallsort.rs` снова совпадает с 26049195. В `merge.rs` остаются гармоники-измерения `bm_u64_len32_plain` и `bm_u64_len32_plain_sorted` и помощник `k1_bm_inv3_sorted`. Без атрибута на цикле эти гармоники — обычные proof без loop contract; это не доказательства контракта (R4), и ни одна заглушка на них не опирается. SHA восстановления — в разделе 1.
- **D23. Счёт формулировок после фазы 6.** Формулировка 3 по времени не уложилась в обычной proof (job 41) и в облегчённом варианте без счётчика (job 42). Но доказательство её контракта (`proof_for_contract`) до CBMC не дошло ни разу. Правило п. 4 фазы 5 говорит о TIMEOUT «при пройденной инструментации» прогона контракта. По букве оно не сработало, поэтому формулировка 3 **не засчитана** как проваленная: проверена 1 формулировка из 3. Альтернатива — засчитать её, тогда 2 из 3: время обычной proof — нижняя граница для proof контракта, в которой ещё и проверки write set. Решение по счёту оставлено владельцу, основание — находка 8.

### Счётчики STOP (bidirectional_merge), конец фазы 1 (16:15 UTC)

- Формулировки, проверенные diagnostic-прогоном: **1 из 3** — прямое доказательство (job 8, 9). Формулировка 2 не засчитана: job 11 не дал результата (RUNNER_ERROR, не провал формулировки).
- Минуты работы без продвижения: **около 15 из 180.** Последнее продвижение — длина 16 доказана в job 9, результат в 15:58 UTC.

## 5. Отвергнутые подходы

- **Формулировка 2 на Kani `9461e07a`** (инвариант цикла `bidirectional_merge`): OOM в goto-instrument под `proof_for_contract` и в CBMC в обычной proof, даже с тривиальным инвариантом (job 17–24, D13), и с явным `loop_modifies` (job 29, D15). Исключена по правилу фазы 3. **Исключение отозвано в фазе 4:** падение вызывала тяжёлая развёрнутая спецификация функции, а с тривиальной или кванторной спецификацией инструментация проходит (job 30, 32, находка 6). Отвергнута только тяжёлая развёрнутая спецификация в паре с loop contract.
- **Формулировка 3 на длине 32 в обычной proof** (job 41, 42): TIMEOUT 10 минут и со счётчиком, и без него.
- **Замена `ptr::add`/`read_unaligned` в спецификации на `wrapping_add` и простые загрузки** (D19, job 38): OOM в `goto-instrument` остался.
- **Бисекция в одной сборке по порядку гармоник** (job 21): Kani обходит гармоники не в порядке запроса и не по алфавиту, и первое падение goto-instrument обрывает весь прогон. Нужна одна гармоника на запрос.

- **Формулировка 1 для длины 32** (прямое доказательство постусловия `bidirectional_merge` со счётчиком пробы): время растёт примерно ×3,2 на +4 длины (job 9), длину 32 за 10 минут не возьмёт. Подходит для коротких длин и как запасная запись для FAIL.
- **`compare_bytes`/memcmp для равенства с пробой:** цикл по байтам, 85 итераций для `[u8; 85]`, конфликтует с границей unwind. Заменён сравнением словами по 8 байт (D7).
- **`offset_from` в инварианте цикла:** после havoc указатель может стоять на некратном смещении, и сработает проверка UB. Заменён арифметикой адресов с проверкой кратности (D9).

## 6. Открытые вопросы

- Что внутри Kani/CBMC даёт OOM у loop contract на цикле `bidirectional_merge`. Вывод `loop_modifies` по встроенным контрактным обёрткам std? Преобразование `for` по `Range`? Без полного лога это не установить. Явный `loop_modifies` не помог (job 29), так что вывод alias-анализом — не единственная причина или не причина вовсе.

- Причина `infrastructure_fail` (job 6, job 11; у K1-network job 7 и job 12 — четыре гармоники, среди них настоящий `insert_tail` на длинах 13 и 17). Лога нет, так что гипотеза о памяти не подтверждена. Без ограничения памяти в lane тяжёлые прогоны теряются целиком.
- Почему `sort4` на типах-массивах в 20 раз дороже, чем на u64.
- Масштабируется ли композиция `general_*` по длинам; где узкое место — в заглушках или в арифметике счётчиков.
- Почему развёрнутый счётчик в `ensures` переполняет `goto-instrument` только под `proof_for_contract` с loop contract (атрибуция — находка 8, механизм не установлен).
- Где CBMC тратит время в job 41, 42 и сколько заняла бы длина 32 без таймаута.
- Тянул бы инвариант цикла длину 32 за 10 минут, если бы инструментация проходила. Неизвестно: формулировка 2 исключена инструментом, до проверки времени не дошло.

## 7. Review

Фаза 5: итог INCONCLUSIVE по памяти, не FAIL (STOP). R9 по заданию фазы 5 не нужен.

**Фаза 6, R9** (`smallsort-reviewer`, кандидат `aa5ad813`, файлы: RESULT-merge.md, merge.rs, smallsort.rs; без выводов автора в запросе): **GO_WITH_NITS**. Проверены сводки и стадии job 35, 36, 38, 40, 41, 42 и check-tooling всех шести (ok), атрибуция job 35 против 40 по диффу, R2 (diff `smallsort.rs` к 26049195 пуст), R3, R4, R5, отсутствие дефектов в новых помощниках.

| # | Замечание | Исправление |
|---|---|---|
| 1 | Job 38 не исключает лёгкую кодировку счётчика при тривиальном инварианте | Перенесено в «Не проверено», убрано из «Исключено» |
| 2 | Причины TIMEOUT job 41, 42 не измерены; применение loop contract в обычной proof лог не подтверждает | Переписано как гипотеза, добавлено в «Не проверено» |
| 3 | Основание 1 — OOM под 13 GiB, вариант 16 GB не в списке владельцу | Добавлен п. (г), заголовок уточнён |
| 4 | «Перестановку не выразить» — рассуждение | Помечено как рассуждение |
| 5 | Doc `bm_u64_len32_plain`: на функции оставались атрибуты контракта | Doc исправлен, пункт в «Не проверено» |
| 6 | Нет записи о review фазы 6 | Эта запись |
| 7 | D23 и R7 | Решение принято (1 из 3 по букве), альтернатива записана; оставлено как есть |

Фаза 4: вердикт отозван, итог промежуточный, review по заданию фазы 4 не нужен.


В фазах 1 и 2 не проводился: это промежуточные итоги, а по §9 review нужен только для PASS или FAIL.

**R9 перед вердиктом FAIL (STOP), фаза 3.** Reviewer — субагент `smallsort-reviewer` (Claude Opus 5.5, отдельный контекст). Ему переданы явный список закоммиченных файлов (`smallsort.rs`, `kani_k1/merge.rs`, `RESULT-merge.md`, `RUN-REQUEST.json`), нормы и номера job, без выводов автора. Кандидат — `def807528752a1095d50badf6178a89dd4a5f352`. Reviewer читал evidence только через `k1.sh summary/log-grep/log-lines` и сам выполнил check-tooling: job 8 и 9 — ok против `77479d23`; 17, 19–22, 24, 27 и 29 — ok против `aca80458`.

**Решение: GO_WITH_NITS.** Вердикт подтверждён evidence и правилом фазы 3. Отдельно отмечено напряжение с §2: при упоре только в память там INCONCLUSIVE. RESULT это раскрывает, а действует правило фазы 3; координатору стоит это учесть.

| Находка | Класс | Суть | Устранение |
|---|---|---|---|
| F1 | should-fix | Вердикт подразумевал, что контракты `insert_tail`/`bidirectional_merge` доказаны до длины 16. В текущей редакции клауз SUCCESS нет ни на одной длине, `bm_u8` и `insert_tail_int/bytes` не запускались | раздел 1, абзац «Для K1-network» |
| F2 | should-fix | Контроль job 27 — обычная proof без признаков применения контракта, не различающий | находка 5 и раздел 1: исключение опирается только на job 29 |
| F3 | nit | OOM CBMC в job 24 приписан loop contract без контроля | помечен как гипотеза (находка 3, раздел 1) |
| F4 | nit | Расхождения таблицы со сводками: cover 5/5 и 1/1, память 3,8 и 11,7 GiB, check-tooling job 17–22 | таблица и журнал фазы 1 исправлены, время R11 добавлено |
| F5 | nit | Устаревшие строки про непроверенный `loop_modifies` в разделах 5, 6, 7 | исправлены |
| F6 | nit, инфо | Вердикт стоял до записи review. При merge в K1-network возможны конфликты в `RUN-REQUEST.json` и в строках `use crate::kani; mod kani_k1;` (D8) | review записан здесь. Конфликты тривиальные, решает K1-network |

Reviewer считает, что повторный review после этих текстовых правок не нужен.


## Волна 1

T0: 2026-10-26T10:46:18Z (UTC, `date -u`).

Новые dispatch до **2026-10-26T16:16:18Z**, отчёт до **2026-10-26T16:46:18Z**.
База `9de80e0bec13896bb35a5e04e771448d9fe3931b` уже влита до T0;
проверена ancestry и отсутствие diff файлов lane. T0 опубликован в `e17a79ec`.

### Решения волны 1

- **D0 (до первого dispatch): вариант (а), реальные тела.** О1 вызывает
  `sort4_stable`, `sort8_stable`, `insert_tail`, `bidirectional_merge` без
  `stub_verified`, включая вложенное слияние в `sort8_stable`. Comparator —
  `kani::any()` на каждом вызове, без вызова comparator из спецификаций.
  Существующие атрибуты контрактов не меняются; обычные proof не выбирают
  их как проверяемые/подставляемые контракты. Альтернатива — общий контракт
  безопасности — потребовала бы отдельного доказательства и изменения
  общего с network `insert_tail`; реальное тело избегает этой зависимости.
- **W1-D1 (R7): контроль Б — честный comparator на конкретном упорядоченном
  входе длины 4, затем `assert!(false)` под `should_panic`.** Это гарантирует,
  что намеренный дефект находится на пути без паники самого алгоритма.
  Альтернатива — произвольный comparator в мутанте — добавляет ожидаемую
  панику алгоритма, затрудняя локализацию маскировки. В контрольной гармонике
  Б нет заглушек. Если Kani даст SUCCESS, контроль не пройден, зачёта О1 нет.
- **W1-D2:** первый запрос содержит три гармоники: мутант Б, мутант А,
  положительную А с проверкой точной перестановки и cover panic boundary.
  Обе FAILED привязаны к уникальному тексту намеренного дефекта. Контроль А
  использует u64 без редукции значений; это контроль механизма, не результат
  О2 для non-Copy/Drop. До зелёного контроля K-6+ не запускается.

### Ledger волны 1

- `stub_verified`: нет. R11 не применяется до появления такой композиции.
- Ручная заглушка ровно одна: `w1_abort_ord_violation` заменяет только
  `panic_on_ord_violation` в двух контрольных гармониках А (перестановка).
  `kani::assume(false)` только в её теле, непосредственно после `cover(true,
  "wave1: panic_on_ord_violation is reachable")`. Обоснование: паника при
  нарушении порядка — не UB; путь после неё не исследуется (`-Cpanic=abort`).
  Достижимость отдельно проверяет `w1_control_a_panic_reachable`.
- Других новых `assume`/`any_where` нет. Все гармоники содержат cover
  нормального возврата; cover мутанта Б стоит перед намеренным дефектом.

### Редукции и ограничения

- Новые контроли: постоянная длина 4, полные u64; редукции домена нет.
- Unwind, CopyOnDrop на панике и non-Copy/Drop пока не измерены.
- K-6+ (а)/(б), длины 17/24/32 пока не измерены, proof credit отсутствует.

### Журнал прогонов волны 1

Первый запрос `w1-merge-control-001`: 3 × 10 = 30 минут таймаутов;
лимит после dispatch: 1/10, 30/200 минут, оценка ≤760/5000 кредитов.
Статус, SHA, Verification Time, память, cover, gate и check-tooling будут
записаны после завершения job. Review запрашивается на опубликованный SHA.

REVIEW REQUEST 2b308ad664c44d6e276eaf4a3bd7c00cc3626a06

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Контроль §4.1; evidence — первый
CircleCI job волны, id будет добавлен после dispatch. Независимый review R9
проводит координатор; собственного reviewer-субагента не запускаю.


### Job 46 — обязательный контроль, блокер Б

- Запрос `w1-merge-control-001`, head `2dec31e1a0a2c04da592031a67fad42cd503dd29`.
- COMPLETE, gate **false**, expectation met false, measurement ok false;
  Kani exit 1. Никакого зачёта О1/О2 по этому run нет.
- Память всего run: max RSS 1664148 KiB; cgroup peak 1.82 GiB,
  ENFORCED 13 GiB, OOM kills 0, swap off. Это общий пик, не пик гармоники.
- check-tooling **ok** против `9de80e0bec13896bb35a5e04e771448d9fe3931b`:
  lane diff отсутствует, пять bound SHA-256 совпадают.

| Гармоника | Ожидание | Статус | Verification Time, с | cover | Локализованный дефект |
|---|---|---|---:|---|---|
| `w1_control_b_must_fail` | FAILED | SUCCESS | 0.37774193 | 1/1 | merge.rs:1202, намеренный assert |
| `w1_control_a_must_fail` | FAILED | FAILED | 4.63229 | 2/2 | merge.rs:1224, намеренный assert |
| `w1_control_a_panic_reachable` | SUCCESS | SUCCESS | 4.711949 | 2/2 | 0 failed checks |

В обоих мутантах текст failed check — `This is a placeholder message; Kani
 doesn't support message formatted at runtime` (перенос только в этом отчёте).
Поэтому заданные `expect_check` не совпали и контроль А формально не принят,
несмотря на локализованный FAILED. У Б есть самостоятельный блокер, который
исправление текста не устранит: Kani считает Rust `assert!(false)` ожидаемой
паникой. Лог прочитан только через `k1.sh log-grep` (7 строк) и `log-lines`
(2705..2756, 52 строки). Финальная строка Б:
`VERIFICATION:- SUCCESSFUL (encountered one or more panics as expected)`.

**W1-D3 (R7): контроль Б не пройден; K-6+ (а)/(б) не запускать.**
Измеренные результаты подтверждают опасность маскировки, описанную в R5 §4.1.
Не меняю требование FAILED на SUCCESS и не объявляю зелёным контроль,
предназначенный обнаружить эту маскировку. Альтернативы: (а) использовать
`kani::assert` или UB-мутант вместо Rust `assert!` — это другой контроль,
не доказывающий отсутствие маскировки Rust assertions; (б) вариант А для О1 —
противоречит прямому правилу без ручных заглушек в О1; (в) продолжить K-6+ и
не засчитывать — противоречит «без зелёного контроля дальше не идти».
Оставляю блокер для независимого review координатора, без вопроса владельцу.

**W1-D4:** отдельный повтор обязательного контроля А допустим до закрытия Б:
он исправляет ошибку самого контроля и не является переходом к K-6+.
Пользовательский форматированный текст заменён на `assert!(v[0] != v[0])`
с обычным текстом выражения; `expect_check` = `v[0] != v[0]`. Положительная
А повторяется в том же наборе коммитов. Б не повторяю: его причина уже
измерена, повтор без изменения механизма не несёт нового результата.

REVIEW REQUEST 2dec31e1a0a2c04da592031a67fad42cd503dd29

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: CircleCI job 46,
`summary`, ограниченный `log-lines 46 2705 52`, check-tooling против базы волны.
Координатору: требуется review обязательного контроля §4.1.

Повтор А `w1-merge-control-a-002`: 2 × 10 = 20 минут таймаутов.
После второго dispatch: 2/10, 50/200 минут, верхняя бюджетная оценка
≤1320/5000 кредитов; фактические кредиты не измерены.
Таблица маршрутов general/stable-Freeze × 17/24/32 пока полностью
**не измерена**. О1 по маршрутам со слиянием не установлена даже на 17;
это блокировка по контролю, а не измеренный TIMEOUT/FAILED безопасности.

REVIEW REQUEST dcea786d7c04265831382585bcc8d6d6a05a46e2

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Повтор контроля А;
новый job будет указан после завершения. Review по R9 — координатор.

### Job 47 — повтор контроля А

- Запрос `w1-merge-control-a-002`, head `c1ff2ca2ed42b39c76f6eb3aff80ed0aaa325fc3`.
- COMPLETE, gate **true**, expectation met true, measurement ok true;
  Kani exit 1 ожидаем из-за контрольного мутанта FAILED.
- Память всего run: max RSS 1622424 KiB; cgroup peak 1.82 GiB,
  ENFORCED 13 GiB, OOM kills 0, swap off. Пик не относится к одной гармонике.
- check-tooling **ok** против `9de80e0bec13896bb35a5e04e771448d9fe3931b`:
  lane diff отсутствует, все пять bound SHA-256 совпадают.

| Гармоника | Ожидание | Статус | Verification Time, с | cover | Failed check |
|---|---|---|---:|---|---|
| `w1_control_a_must_fail` | FAILED | FAILED | 5.3462563 | 2/2 | `assertion failed: v[0] != v[0]`, merge.rs:1224 |
| `w1_control_a_panic_reachable` | SUCCESS | SUCCESS | 4.944808 | 2/2 | нет, 0/321 |

Требование `expect_check` теперь выполнено. Контроль А имеет измерительное
подтверждение; независимый review R9 ещё не получен, до него зачёта нет.
Это не доказательство О2 для non-Copy/Drop и не переносится на длины 17..32.

REVIEW REQUEST c1ff2ca2ed42b39c76f6eb3aff80ed0aaa325fc3

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 47 `summary`,
check-tooling против базы волны. Для исходного контроля Б — job 46 на
`2dec31e1a0a2c04da592031a67fad42cd503dd29` (предыдущий REVIEW REQUEST).

### Текущее покрытие и следующий шаг (2026-10-26 10:57 UTC)

| Маршрут | Длина | Verification Time | gate | cover | Состояние |
|---|---:|---|---|---|---|
| `bidirectional_merge`, О1 | 32 | — | — | — | не запускался: контроль Б |
| general, О1 | 17 | — | — | — | не запускался: контроль Б |
| general, О1 | 24 | — | — | — | не запускался: контроль Б |
| general, О1 | 32 | — | — | — | не запускался: контроль Б |
| stable-Freeze, О1 | 17 | — | — | — | не запускался: контроль Б |
| stable-Freeze, О1 | 24 | — | — | — | не запускался: контроль Б |
| stable-Freeze, О1 | 32 | — | — | — | не запускался: контроль Б |

Для координатора: **О1 по маршрутам со слиянием не закрыта даже на 17** —
по блокеру обязательного контроля Б, а не по провалу безопасности алгоритма
или ресурсному пределу. Не установлено, сколько времени заняли бы K-6+.
Безопасность, перестановка non-Copy и drop, восстановление при unwind,
контракт безопасности слияния и K-13 не измерены в этой волне.

**W1-D5 (R7):** новые dispatch после job 47 не делаю до разрешения блокера Б.
Не меняю runtime std, lane, смысл expected FAILED или правила зачёта.
Review запрошен через RESULT, как предписано; ожидается независимый вердикт
координатора. Это не завершение волны: обязательные шаги K-6+ не выполнены,
окно и лимиты не исчерпаны; строку `ВОЛНА 1 ЗАВЕРШЕНА` пока не ставлю.
Незавершённых job нет. Расход лимитов: **2/10 dispatch, 50/200 минут
таймаутов**, оценка ≤1320/5000 кредитов; фактические кредиты не измерены.


### CD-1: поправка контроля Б (2026-10-26 11:02 UTC)

База координатора `440b06c9` влита обычным merge; раздел «Решения
координатора по ходу волны» R5-WAVE1.md прочитан. По сообщению координатора:
review R9 `2b308ad6` — **NO_GO** для прежнего контроля Б; вывод W1-D3 верен;
контроль А с `v[0] != v[0]` **принимается**. CD-1 заменяет требование
assert!-мутанта для Б на два мутанта класса безопасности. Исторический
`w1_control_b_must_fail` оставлен как демонстрация маскировки, не контроль.

**W1-D6 (R7, CD-1):** два новых контроля исполняют реальное слияние длины 4
и после нормального возврата читают сырой указатель на один элемент за
аллокацией источника. Прочитанное значение записывается в допустимую память
назначения. Мутанты различаются comparator: честный на `[0,1,2,3]` и
`kani::any()` на каждом сравнении при произвольном входе. Во втором случае
паника алгоритма достижима (та же инстанциация, что положительный контроль
А, cover в job 47). Cover каждого нового мутанта — после нормального
возврата, до намеренного UB. Ожидаются FAILED с `expect_check` =
`dereference failure: pointer outside object bounds`.

**Смысл последующего О1:** нет упавших проверок безопасности Kani на любом
пути; любые паники класса assertion допустимы. Это не утверждает отсутствие
переполнений, ошибочных индексов или других паник. Под `should_panic` нет
`stub_verified`, `proof_for_contract` или проверок контрактов. D0 реальные
тела сохраняется. Исходные атрибуты функций не проверяются обычной proof
с флагом CI `--no-assert-contracts` и без подстановки контрактов.

**W1-D7 (R7):** дополнительное дублирование О1 вариантом А пока не выбираю:
приоритет — измерить заданные длины и маршруты в оставшемся бюджете.
Альтернатива усилила бы вывод до отсутствия других паник, но удвоила бы
семейства. Обязательные проверки свойств остаются только в варианте А.
CD-1 разрешает исключение assume(false) и для контролей А; ledger остаётся
без изменений. Новых assume/stub в контролях Б нет.

Запрос `w1-merge-control-b-cd1-003`: 2 × 10 минут. После dispatch лимиты:
**3/10 dispatch, 70/200 минут таймаутов**, верхняя оценка ≤1880/5000 кредитов.
W1-D5 отменён в части ожидания разъяснения: CD-1 получено; K-6+ разрешён
после зелёного нового контроля Б. Review запрашивается независимо.

REVIEW REQUEST 926967773a4dfbfe0008f39cf9cccf18a93f1d15

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Новый контроль Б по CD-1;
evidence — следующий CircleCI job. Предыдущий контроль А: job 47.


### Job 48 — новый контроль Б по CD-1

- Запрос `w1-merge-control-b-cd1-003`, head `22f7c450df04be0a10940e783d0bcadaa730e647`.
- COMPLETE, gate **true**, expectation met true, measurement ok true,
  Kani exit 1 ожидаем из-за двух контрольных FAILED.
- Память всего run: max RSS 1604044 KiB, cgroup peak 1.82 GiB,
  ENFORCED 13 GiB, OOM kills 0, swap off.
- check-tooling **ok** против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.

| Гармоника | Статус (ожидался FAILED) | Verification Time, с | cover | Локализация |
|---|---|---:|---|---|
| `w1_control_b_oob_honest` | FAILED | 0.37891668 | 1/1 | merge.rs:1268 |
| `w1_control_b_oob_arbitrary` | FAILED | 0.58665735 | 1/1 | merge.rs:1287 |

Оба failed check содержат точный `dereference failure: pointer outside object
bounds`. В произвольном случае дополнительно упала assertion-класса паника
`smallsort.rs:884`, но наличие паники не замаскировало pointer safety failure.
Контрольные измерения теперь удовлетворяют CD-1; review R9 запрошен, до
вердикта независимого reviewer зачёта результатов нет. По правилам R9
продолжаю следующие шаги, не ожидая review.

REVIEW REQUEST 22f7c450df04be0a10940e783d0bcadaa730e647

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 48 `summary`,
check-tooling против базы волны. Контроли Б по CD-1; контроль А — job 47.

### K-6+ (а), реальное слияние 32

Запрос `w1-merge-k6a-32-004`: фиксированная длина 32, полный u64,
произвольный `kani::any()` на каждом сравнении, `should_panic`, без
`stub_verified`, ручных заглушек, assumes или проверок свойств/контрактов.
Вход произвольный, даже отсортированность половин не предполагается:
SAFETY функции требует валидные непересекающиеся области и len >= 2.
Cover — нормальный возврат. Вывод по CD-1 ограничен проверками безопасности.
Атрибут unwind 34; в слиянии длины 32 цикл len/2 имеет 16 итераций.
Верхние гармоники имеют также другие циклы и map до 32 элементов.

После четвёртого dispatch: **4/10, 80/200 минут таймаутов**;
верхняя оценка ≤2240/5000 кредитов. K-6+ (б) ещё не измерен.

REVIEW REQUEST 227d17179749806b6310ee547f22c3afa91dab2b

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. K-6+ (а), О1 по CD-1,
реальное слияние u64 длины 32; evidence — следующий CircleCI job.


### Job 49 — K-6+ (а), реальное слияние u64 × 32

- Запрос `w1-merge-k6a-32-004`, head `1d230f7577de2cbbd1f0bcb13361de5b7a6459c3`.
- COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
- `w1_merge_u64_len32_safety`: **SUCCESS**, Verification Time **4.5430408 с**,
  cover **1/1**. Assertion-класса паника `smallsort.rs:884` достижима (1/102
  failed checks), допустима согласно CD-1. Провалов безопасности Kani нет.
- Память всего run: max RSS 1608072 KiB, cgroup peak 1.77 GiB,
  ENFORCED 13 GiB, OOM kills 0, swap off. Одна гармоника: пик run — только
  верхняя оценка её памяти, включает компиляцию.
- check-tooling **ok** против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
- Откат к контракту безопасности не требуется: реальное тело прошло 32.
  Длины 17/24 отдельного слияния не измерялись, вывод о них не делаю.
- R9 ещё ожидается; независимый proof credit до него не заявлен.

REVIEW REQUEST 1d230f7577de2cbbd1f0bcb13361de5b7a6459c3

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 49 `summary`,
check-tooling против базы волны. Контроли CD-1 — job 48; А — job 47.

### W1-D8 (R7): u64 на unstable entrypoint выбирает network

Проверен исходный dispatch `smallsort.rs`: `u64: Copy + Freeze`,
`has_efficient_in_place_swap::<u64>()` true, поэтому
`<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort` идёт в network.
Это несовместимо с буквальным заданием «general через unstable trait, u64».
Runtime и специализации не меняю, чужой network не подменяю.

Выбор: (1) `small_sort_general` напрямую на **u64**, чтобы измерить именно
заданные тела и тип; (2) дополнительно реальные unstable trait entrypoints
для `#[repr(transparent)] struct W1GeneralU64(u64)` **без Copy**, размер 8,
Freeze, без Drop, ключи — все u64 без редукции. Он выбирает general и
сохраняет размерную ветку sort8. (3) stable-Freeze проверяется через
`<u64 as StableSmallSortTypeImpl>::small_sort` с scratch 48.
Альтернативы: только прямой general — не покрывает trait dispatch; только
оболочка — не является буквально типом u64; массив >8 байт — меняет размер.
Дополнительные три гармоники оболочки помещаются в бюджет: все 9 верхних
гармоник вместе с уже потраченными 80 минутами = 170/200 минут.

Верхние гармоники подготовлены для 17/24/32; comparator возвращает
`kani::any()` на каждом вызове, callee реальные по D0, проверок свойств,
assumes, заглушек и контрактных проверок нет. Cover нормального возврата
у каждой постоянной длины. Вывод О1 ограничен CD-1; перестановка и Drop
в этих гармониках не проверяются. Оболочка non-Copy не даёт вывода О2.

Первый запрос верхних `w1-merge-k6b-general-005`: general u64 17/24/32,
stable-Freeze u64 17; 4 × 10 минут. После dispatch:
**5/10 dispatch, 120/200 минут таймаутов**, оценка ≤3200/5000 кредитов.

REVIEW REQUEST 568c0682ed68e3cee695acda00583f46fbd8e803

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Верхние семейства K-6+ (б);
первый запрос содержит general u64 17/24/32 и stable-Freeze u64 17.
Прозрачная non-Copy оболочка для trait general раскрыта в W1-D8.

### R9: контроль §4.1 засчитан координатором

Сообщение координатора: независимый review `92696777` (новый контроль Б
по CD-1) — **GO_WITH_NITS**. Контроль §4.1: **А job 47 + Б job 48
засчитан**. Review K-6+ (а) `227d1717` ещё идёт, его зачёт пока не заявляю.

Ниты reviewer:

- `expect_check` сверяется только по тексту, без места. Для job 48 выше
  сохранены места намеренного safety failure: `merge.rs:1268` (honest) и
  `merge.rs:1287` (arbitrary); отдельно раскрыта паника `smallsort.rs:884`
  в arbitrary. Для будущих FAILED-контролей также сохранять точный текст
  и локализацию, чтобы не спутать мутант с посторонним дефектом.
- Covers у FAILED-строк гейтом не проверяются. Значения 1/1 из summary
  приведены как наблюдение; основание достижимости мутанта — локализованный
  провал безопасности на намеренном чтении, а не только gate/cover.

На момент сообщения активен job **51**, head `8d6d5387`, запрос
`w1-merge-k6b-general-005`: general u64 direct 17/24/32 и stable-Freeze
u64 trait 17. `k1.sh watch 51` уже зарегистрирован; повторно не регистрирую,
состояние job не опрашиваю и новых прогонов во время ожидания не запускаю.


### Job 51 — K-6+ (б), general direct и stable-Freeze 17

- Запрос `w1-merge-k6b-general-005`, head `8d6d53878753af2c3f6c226b30da9a1035fd993d`.
- COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
- Память всего run: max RSS 1708212 KiB, cgroup peak 1.83 GiB,
  ENFORCED 13 GiB, OOM kills 0, swap off. Это пик четырёх гармоник плюс
  компиляция, не индивидуальная память гармоники.
- check-tooling **ok** против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.

| Маршрут | Тип | Длина | Статус | Verification Time, с | gate | cover |
|---|---|---:|---|---:|---|---|
| general, прямой `small_sort_general` | u64 | 17 | SUCCESS | 9.844458 | true | 1/1 |
| general, прямой `small_sort_general` | u64 | 24 | SUCCESS | 16.768135 | true | 1/1 |
| general, прямой `small_sort_general` | u64 | 32 | SUCCESS | 27.183834 | true | 1/1 |
| stable-Freeze, trait entrypoint | u64 | 17 | SUCCESS | 9.501499 | true | 1/1 |

У каждой гармоники одна достижимая assertion-класса паника `smallsort.rs:884`,
допустимая по CD-1. Отсутствие провалов безопасности, а не отсутствие любых
паник. Это не результат перестановки/Drop или отсортированности. Отдельные
длины не доказывают все промежуточные длины. R9 по верхним ещё ожидается.

REVIEW REQUEST 8d6d53878753af2c3f6c226b30da9a1035fd993d

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 51 `summary`,
check-tooling против базы волны. Область типов/dispatch раскрыта в W1-D8.
Контроль §4.1 засчитан (сообщение координатора выше).

Следующий запрос `w1-merge-k6b-stable-trait-006`: stable-Freeze u64 24/32,
general через unstable trait для прозрачного non-Copy u64 17/24;
4 × 10 минут. Исходники гармоник не изменяются после job 51.
После dispatch: **6/10, 160/200 минут таймаутов**, оценка ≤4160/5000 кредитов.
General через trait на 32 остаётся отдельным следующим запросом.

REVIEW REQUEST bc94cf45013f787d07607708c5c7a2a1fbb63212

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. K-6+ (б): stable-Freeze
u64 24/32, general trait non-Copy transparent u64 17/24; evidence —
следующий CircleCI job. Код гармоник тот же, что в job 51.


### R9 K-6+ (а) и CD-2 (сообщение координатора)

Review `227d1717` — **GO_WITH_NITS**, условно: job 49 и верхние на прежнем
comparator засчитываются только после перепрогона с читающим comparator.
База `61ddbfc4` влита обычным merge, CD-2 в R5-WAVE1.md прочитан.
Предыдущее SUCCESS без чтения аргументов не даёт достаточного покрытия:
создание `&*p` само по себе не читает память, а reference-validity checks
во флагах CI не включены. Не заявляю окончательного зачёта О1 по job 49/51/52.

Исправления:

- `w1_arbitrary_less` сначала делает `ptr::read_volatile(a)` и
  `ptr::read_volatile(b)`, затем возвращает `kani::any()`.
- Comparator прозрачной оболочки читает оба полных u64 payload через
  `ptr::read_volatile(&a.0)` и `ptr::read_volatile(&b.0)` перед `kani::any()`.
  Volatile выбран и для u64, чтобы чтение не исчезло как неиспользуемое.
- Требование `N >= 2` в helper слияния закреплено const assert, вместе с
  верхней границей 32; это compile-time проверка, не runtime assertion.
- Уточнение unwind: на длине 32 цикл слияния имеет **16** итераций, не 32.
- Чётный путь слияния проверяется отдельно при 32; нечётный хвост
  `smallsort.rs:850-856` будет проверен верхними маршрутами при **17**.
  Таблица итогов обязана сохранять это различие.

**W1-D9 (R7): экономия резервируемых таймаутов без редукции домена.**
На job 52 уже израсходованы 160/200 минут таймаутов. Для полного повтора
слияния32 и девяти верхних инстанциаций делаю три гармоники:

- длина17: `kani::any::<u8>()` выбирает direct general (0), general trait
  прозрачного non-Copy u64 (1), stable-Freeze u64 (все остальные значения);
- длина24: тот же независимый выбор из трёх маршрутов;
- длина32: `kani::any::<bool>()` выбирает отдельное слияние32 или такой же
  выбор одного из трёх верхних маршрутов.

Маршруты выбираются до сортировки, не исполняются последовательно: паника
раннего маршрута не может исключить другие. Каждый helper создаёт свой
полностью произвольный вход. Assumes, зависимых от входа редукций и заглушек
нет. Ожидаются три различных cover нормального возврата при 17 и 24 и четыре
при 32. Verification Time будет общим на длину для набора маршрутов,
не индивидуальным временем каждой строки. Для каждой строки это общий
верхний предел ≤600 с, а не отдельное измерение времени маршрута.

Альтернатива — отдельный повтор десяти гармоник — нарушила бы лимит 200 мин.
Первоначальная оценка четырёх объединённых гармоник дала бы 200 минут и
верхнюю оценку 5120 кредитов (выше 5000); добавление merge32 независимой
веткой в гармонику32 даёт **190 минут и ≤4920 кредитов** для семи dispatch.
Повтор остаётся measurement, по 10 минут на гармонику. Следующий запрос
будет отправлен только после окончания активного job 52 и чтения summary.

Job 52, уже запущенный на прежнем comparator, дочитывается как историческое
измерение без окончательного зачёта. Watch активен; новых job пока нет.

REVIEW REQUEST c7bcf073ea5797f56cacd08a3ae96f97d8cd83b4

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Исправление CD-2 и три
объединённые гармоники, код к следующему прогону после job 52.
RUN-REQUEST пока соответствует запущенному job 52; запрос повтора
будет изменён, провалидирован и опубликован после его завершения.


### Job 52 — исторический прогон до CD-2, не окончательный зачёт

- Запрос `w1-merge-k6b-stable-trait-006`, head `568add0a6d24c19dc770befb0eec7ea123fad109`.
- COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
- Память всего run: max RSS 1956872 KiB, cgroup peak 2.18 GiB,
  ENFORCED 13 GiB, OOM kills 0, swap off.
- check-tooling **ok** против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.

| Маршрут | Тип | Длина | Статус | Verification Time, с | cover |
|---|---|---:|---|---:|---|
| stable-Freeze, trait | u64 | 24 | SUCCESS | 16.04005 | 1/1 |
| stable-Freeze, trait | u64 | 32 | SUCCESS | 26.780031 | 1/1 |
| general, unstable trait | transparent non-Copy u64 | 17 | SUCCESS | 12.006729 | 1/1 |
| general, unstable trait | transparent non-Copy u64 | 24 | SUCCESS | 19.583809 | 1/1 |

Во всех строках — одна assertion-класса паника `smallsort.rs:884`.
Comparator этого SHA не читает аргументы; по CD-2 эти результаты требуют
повтора и не являются достаточным самостоятельным основанием для зачёта О1.
Никаких выводов о времени читающего comparator из этих чисел не делаю.
Пик общий на run, не память каждой строки.

### Повтор по CD-2 всех K-6+ в заданных длинах

Запрос `w1-merge-cd2-all-routes-007` использует код `c7bcf073`:
три гармоники с независимым выбором маршрута, согласно W1-D9.
Слияние32 включено независимой веткой гармоники32; все три верхних
маршрута проверяются при 17/24/32, в том числе ранее не измеренный
unstable general trait на 32. Comparator обоих типов читает оба аргумента.
Ожидаемые cover: 3/3, 3/3, 4/4 соответственно. У каждого helper свой
произвольный массив; нет assumes, stubs или проверок свойств/контрактов.

3 × 10 = 30 минут. После dispatch:
**7/10 dispatch, 190/200 минут таймаутов, верхняя оценка ≤4920/5000 кредитов**.
Это последний запланированный запрос K-6+: дополнительных отдельных
повторов нет, если новые ошибки или review не потребуют исправлений.
Измерительные результаты и окончательный зачёт ожидаются после этого job
и независимого R9. Таблица О1 будет заменена на результаты читающего comparator.

REVIEW REQUEST 30174dc68c2353a0615b263873fb1e9c3e16b15b

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Перепрогон K-6+ (а)/(б)
после CD-2; три гармоники покрывают десять инстанциаций без assumes.
Evidence — следующий CircleCI job; прежние job 49/51/52 раскрыты выше.

### R9 верхних семейств: уточнение покрытия и следующий приоритет

Сообщение координатора: review `568c0682` — **GO_WITH_NITS**, с исправлением
заявлений. На длинах 17/24/32 `small_sort_general_with_scratch` исполняет
только presort **sort8**, поскольку len >= 16 и размер типа 8. Ветки sort4
(len 8..15) и копирования одного элемента (len 2..7) этими опытами не покрыты.
Quicksort вызывает small_sort при любых длинах <=32. Поэтому текущий охват
О1 general/stable — **только длины 17/24/32 и ветка sort8**, после повторов
CD-2; формулировка «весь маршрут до 32» пока недопустима.

Дополнительные ниты/ограничения:

- Trait-гармоники пока вызывают `UnstableSmallSortFreezeTypeImpl`; в следующей
  редакции предпочтителен `UnstableSmallSortTypeImpl`, реальный вход quicksort.
  При этом прозрачный non-Copy u64 нужен для выбора general, как в W1-D8.
- **Uninit-чтения не проверены:** во флагах lane нет `-Z uninit-checks`.
  О1 означает отсутствие включённых проверок безопасности Kani, а не всех
  мыслимых UB-категорий. Отдельного результата K-3 в этой волне нет.
- Scratch 48 соответствует минимальному реальному вызову; это допустимо,
  произвольный размер scratch за пределами этой модели не заявлен.

Следующий приоритет координатора после CD-2: расширить семейство постоянных
длин, минимум 2/3/7/8/9/15/16 плюс измеренные 17/24/32; предпочтительно все
2..=32, в пределах 200 минут таймаутов. Это важнее дополнительных trait-
длин. Job **53** уже запущен, head `38faf5ff`, запрос
`w1-merge-cd2-all-routes-007`; его не отменяю, watch активен.
С учётом него зарезервировано 190/200 минут, остаётся **10 минут**.
После summary job 53 приму R7-решение о размере одной дополнительной
гармоники-семейства, опираясь на измеренное время читающего comparator.
Не заявляю заранее, что расширение уложится. Прежняя оценка ≤4920 кредитов
относилась к семи dispatch; для дополнительного запроса бюджет надо
пересчитать с учётом уже завершённых коротких job, не скрывая фактический
расход за прежней суммой резервных верхних оценок.


### Job 53 — CD-2: чтение обоих аргументов comparator

- Запрос `w1-merge-cd2-all-routes-007`, head `38faf5ff0b1d4bd342097f646e26c02ba9fd4266`.
- COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
- Память всего run: max RSS 5539884 KiB, cgroup peak 5.55 GiB,
  ENFORCED 13 GiB, OOM kills 0, swap off. Пик общий на run, не на строку.
- check-tooling **ok** против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.

| Набор маршрутов в гармонике | Длина | Статус | Verification Time, с | gate | cover | Ветка |
|---|---:|---|---:|---|---|---|
| general u64 direct + general Freeze trait non-Copy u64 + stable-Freeze u64 | 17 | SUCCESS | 49.96133 | true | 3/3 | sort8, нечётный хвост финального слияния |
| те же три маршрута | 24 | SUCCESS | 85.08464 | true | 3/3 | sort8, чётное финальное слияние |
| те же три маршрута + отдельное слияние u64 | 32 | SUCCESS | 165.27512 | true | 4/4 | sort8 у верхних; отдельное слияние только чётное |

Время каждой строки — **общее** на независимо выбранные маршруты,
не отдельный замер каждого. Все маршруты входа и оба аргумента comparator
покрыты без assumes; у каждой строки есть assertion-класса паника
`smallsort.rs:884` и нет провалов включённых проверок безопасности.
Область вывода: CD-1/CD-2, presort sort8, фиксированные длины 17/24/32.
Не следуют полная перестановка, Drop, отсутствие иных паник и uninit safety.
Результаты job 49/51/52 теперь имеют повтор с читающим comparator на этих
инстанциациях; окончательный независимый зачёт по CD-2 ожидает R9.

REVIEW REQUEST 38faf5ff0b1d4bd342097f646e26c02ba9fd4266

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 53 `summary`,
check-tooling против базы волны. Повтор CD-2; три гармоники с cover 3/3,3/3,4/4.

### W1-D10 (R7): последнее расширение — обязательные границы

В оставшиеся 10 минут таймаутов выбираю одну гармонику с постоянными
длинами **0,1,2,3,7,8,9,15,16** для direct general u64 и stable-Freeze u64.
Это минимум координатора плюс пустой/одноэлементный возврат. На длине16
дополнительно выбирается general trait для прозрачного non-Copy u64 через
**UnstableSmallSortTypeImpl**, то есть реальный quicksort entrypoint.
Helper trait переведён на него в текущей редакции. Для job 53 таблица
сохраняет фактически проверенный прежний FreezeTypeImpl, без переноса
кредита на новый вход на длинах 17/24/32.

Причина не выбирать всё 2..=32: измеренный совместный N32 занял 165 с и
пик всего run 5.55 GiB. Семейство из 31 длины с многими копиями real-body
может не уложиться в 600 с/13 GiB; после расхода последних 10 минут нет
бюджета отката. Это оценка риска, не измеренное утверждение о невозможности
полного семейства. Приоритет — закрыть все размерные ветки и их границы.
Альтернатива full 2..32 оставлена неизмеренной и явно раскрывается.

Выбор длины — полный u8, остальные значения возвращаются без сортировки;
это не assume и не доказательство пропущенных длин. Каждая выбранная длина
имеет отдельный normal-return cover, оба маршрута имеют cover в helpers.
На N16 дополнительный cover у реального unstable trait. Ожидается 29 cover
(18 general/stable + 1 trait + 9 длин + конец селектора); точное число будет
взято из summary. Comparator volatile-read на каждом вызове, stubs/assumes
и проверки свойств/контрактов отсутствуют. Scratch 48, как ранее.

Запрос `w1-merge-cd2-boundaries-008`, 1 × 10 минут. После dispatch:
**8/10 dispatch, 200/200 минут таймаутов**. Других K-6+ dispatch не будет.
Перестановка non-Copy/Drop и K-13 этим запросом не проверяются.

Бюджет кредитов пересчитан с освобождением неиспользованных резервов:
wall_whole_run из summary завершённых job 46/47/48/49/51/52/53 в секундах —
49.81, 51.16, 41.18, 40.34, 103.41, 118.24, 347.57; всего 751.71 с
(12.5285 мин). Плюс 8 × ~8 мин подготовки и 10 мин следующего таймаута:
20 × (12.5285 + 64 + 10) ≈ **1731 кредит** сценарной оценки, ниже 5000.
Это **не фактический счёт CircleCI** и не подтверждённый ledger расходов;
верхняя резервная оценка 5280 без освобождения прошлых таймаутов завышает
оставшуюся потребность. Фактические кредиты не измерялись.

REVIEW REQUEST a6c9bf377fa1b2d9e8d66b364eca3c5dff072aff

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Дополнение CD-2: границы
0/1/2/3/7/8/9/15/16, general direct и stable-Freeze, плюс реальный
UnstableSmallSortTypeImpl на 16. Evidence — следующий CircleCI job.


### CD-3 и независимый review CD-2

По сообщению координатора R9 по `c7bcf073` + запросу `30174dc6`:
**GO_WITH_NITS**. Требуется измерить дефект CD-2 отдельным мутантом:
второй аргумент читающего comparator — сырой указатель за аллокацией,
`should_panic`, ожидается FAILED `dereference failure: pointer outside
object bounds`. Такой контроль подготовлен как
`w1_cd2_comparator_oob_must_fail`: первый аргумент `&v[0]` валиден, второй
`&*v.as_ptr().wrapping_add(4)` намеренно неверен; срабатывание и место будут
записаны после measurement, не предугадываются.

Уточнённая формулировка О1: **нет разыменования за объектом, мёртвого или
невыровненного указателя в рамках включённых проверок Kani**. Это не
«ссылки comparator валидны». Uninit-чтения, полная reference validity,
перестановка/Drop и unwind не доказаны. Старые результаты цитируются только
с соответствующими SHA: job49 `1d230f7577de2cbbd1f0bcb13361de5b7a6459c3`,
job51 `8d6d53878753af2c3f6c226b30da9a1035fd993d`,
job52 `568add0a6d24c19dc770befb0eec7ea123fad109`.

База `73ad9fc2` влита, CD-3 прочитан. Старый лимит суммы таймаутов снят.
Новые ограничения: **до 16 dispatch, до 250 фактических минут job**, потолок
волны 9000 кредитов сохраняется. Фактический учёт по API ведёт координатор;
по его сообщению jobs46–49,51,52 израсходовали около **14 минут** (без
последующих53/56). В RESULT веду оценку по summary wall, не выдаю её за
фактический биллинг. Старые записи 200/200 и «последний запрос» отменены CD-3.

**W1-D11 (R7):** после чтения job56 расширяю до всех **2..=32** с отдельной
постоянной гармоникой на длину, читающим comparator и тремя независимо
выбираемыми маршрутами (direct general u64, реальный
`UnstableSmallSortTypeImpl` на non-Copy transparent u64, stable-Freeze u64).
Так general/stable и trait получают одно семейство без увеличения числа
harmonics относительно полного покрытия двух главных маршрутов.
Ожидаемые cover — три нормальных возврата в каждой гармонике.

На данный момент использовано 8 dispatch, включая активный56. Осталось8:
31 длина + 1 дешёвый контроль CD-2 = **32 гармоники**, ровно8 запросов по4
(40 минут таймаутов на запрос, соблюдается). На длине32 три маршрута с
читающим comparator уже укладывались в165 с вместе с отдельным слиянием
(job53); отдельные длины дадут меньший риск, чем единая большая формула.
Это план, не утверждение о ещё не измеренном времени.

Приоритеты CD-3 соблюдаются так: job56 закрывает минимальные ветки;
следующий запрос содержит начало полного семейства и дешёвый контроль;
все последующие расширяют семейство по длинам. Trait проверяется в тех же
гармониках, без дополнительных dispatch. Если будет TIMEOUT/OOM/NO_GO,
пересмотрю пакетирование оставшихся длин и честно раскрою пропуски вместо
выхода за16 dispatch/250 минут/окно. Окончательное решение о dispatch —
после окончания активного56. Сейчас новых job нет, watch56 уже действует.

REVIEW REQUEST c5720c76aa23a30eef17057fe4500db93ddfac98

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Подготовленный контроль
CD-2 и полное семейство2..32 по CD-3; RUN-REQUEST пока относится к
активному56 и будет обновлён после его summary.


### Job56 — границы всех presort-веток

- Запрос `w1-merge-cd2-boundaries-008`, head `d0b1192d5af1468dfa80a99219e9f33374aebedb`.
- COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit0.
- `w1_cd2_presort_boundaries_safety`: **SUCCESS**, Verification Time
  **139.0581 с**, cover **29/29**. Assertion-класса паника `smallsort.rs:884`
  достижима, провалов включённых safety checks нет.
- Память run: max RSS3881248 KiB, cgroup peak4.78 GiB; ENFORCED13GiB,
  OOM kills0, swap off. Одна гармоника, пик включает компиляцию.
- check-tooling **ok** против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.

| Маршрут/тип | Постоянные длины | Общее Verification Time | gate | cover | Ветки |
|---|---|---:|---|---|---|
| direct general u64 и stable-Freeze u64 | 0,1,2,3,7,8,9,15,16 | 139.0581с | true | в общем29/29 | ранний возврат; копия1; sort4; sort8; чётный/нечётный merge |
| реальный unstable trait, transparent non-Copy u64 | 16 | тот же общий139.0581с | true | в общем29/29 | sort8 |

Время общее для всей гармоники; по отдельным маршрутам/длинам не измерено.
Вместе с job53, head `38faf5ff0b1d4bd342097f646e26c02ba9fd4266`, измерены
все размерные ветки general/stable, но пока не все длины2..32.
Контроль входных чтений CD-2 и независимый R9 для этой таблицы ещё ожидаются.
Полная reference validity/uninit/unwind/перестановка/Drop не заявлены.

REVIEW REQUEST d0b1192d5af1468dfa80a99219e9f33374aebedb

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job56 `summary`,
check-tooling против базы волны. Cover29/29; предыдущий кандидат `a6c9bf37`.

### Полное семейство CD-3, пакет1

Запрос `w1-merge-cd3-len2to4-control-009`: N2/3/4 (по три независимых
маршрута, реальный unstable trait), плюс измеренный отрицательный контроль
читающего comparator. Для FAILED ожидается точный текст safety failure;
место будет сохранено из summary. Код подготовлен на `c5720c76`.
Пакеты дальнейшего полного семейства: 5..8,9..12,13..16,17..20,21..24,
25..28,29..32. Это8 дополнительных dispatch до16/16 включительно.
В каждом запросе4 ×10мин, не больше40. Один активный job сохраняется.

После следующего dispatch: **9/16**, лимит фактических минут **250**;
последний подтверждённый координатором учёт — около14мин за46..49,51,52.
Оценка по summary всех восьми завершённых job46..49,51..53,56:
751.71+181.46=**933.17с (15.5528мин)** verify-команд с компиляцией,
без подготовки CircleCI; это не фактический job wall/billing. API-учёт
проверяет координатор по CD-3. Job53/56 ещё не вошли в присланные14мин.

REVIEW REQUEST eab5af1d1eab030a8c45506dc72974ecc79e8400

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. CD-3 N2/3/4 и
отрицательный контроль CD-2; evidence — следующий CircleCI job.

### R9 границ presort: GO_WITH_NITS

По сообщению координатора независимый review `a6c9bf37` —
**GO_WITH_NITS**, нарушений нет. Полное семейство `c5720c76` ещё на review;
будущие результаты не засчитываю заранее.

Учтены ниты:

- Job53 относится **только** к SHA
  `38faf5ff0b1d4bd342097f646e26c02ba9fd4266`: general trait в нём —
  `UnstableSmallSortFreezeTypeImpl`. Это не измерение нового
  `UnstableSmallSortTypeImpl` при17/24/32. Новый реальный вход измерен
  в job56, SHA `d0b1192d5af1468dfa80a99219e9f33374aebedb`, только при16.
  Полное семейство с новым входом будет иметь собственные job/SHA.
- У u64 и его прозрачной оболочки размер8. Ветка presort sort4 **при len>=16**
  для типов **размером>16 байт** не инстанцируется. Это область K-16,
  матрица типов волны3. Покрытие нижней ветки sort4 при8..15 не заменяет
  проверку типа>16 при больших длинах. Для такой матрицы доказательства нет.
- Ожидание cover job56 было29; `summary` фактически сообщает **29/29**.
  Ожидания совпали. У job53 ожидаемые3/3,3/3,4/4 также совпали со summary.
- Бюджетное обоснование **W1-D10 устарело после CD-3**. Выбор граничного
  набора оставлен как историческое решение до нового бюджета, а не причина
  ограничивать дальнейшие прогоны. Действуют16 dispatch/250 фактических
  минут и полное семейство2..32 по W1-D11.

Активен job59, head `3820d796`, запрос `w1-merge-cd3-len2to4-control-009`.
Watch59 зарегистрирован; новых прогонов и опроса состояния нет.


### R9 полного семейства и обновление CD-3

По сообщению координатора review `c5720c76` (контроль CD-2 + семейство
2..=32) — **GO_WITH_NITS**. Условие каждого нового dispatch: включать
`w1_cd2_comparator_oob_must_fail`, expect **FAILED**, expect_check
`dereference failure: pointer outside object bounds`; все
`w1_cd3_all_lenN_safety` — expect **SUCCESS**. Место expected check —
`core/src/ptr/mod.rs` внутри `read_volatile`, сохраняется из summary.

Поправка CD-3 с origin/base влита: лимит dispatch теперь **22**, фактических
минут по-прежнему **250**. В одном запросе4 гармоники/40мин сохраняется.
Пакетирование исправлено: три длины + обязательный контроль в каждом job.
Для31 длины требуется11 запросов полного семейства, всего19/22 dispatch
(8 ранее +11 семейства), с запасом3 для исправлений/повторов.

**W1-D12 (R7):** N17/24/32 оставляю в новом семействе: job53 на
`38faf5ff0b1d4bd342097f646e26c02ba9fd4266` использовал FreezeTypeImpl,
а теперь измеряется реальный UnstableSmallSortTypeImpl. Для general direct
и stable-Freeze это повтор; для нового trait entrypoint — новое измерение.
Дополнительные мутанты первого аргумента и comparator оболочки пока не
включаю: это необязательное усиление, текущий обязательный контроль уже
измерен в job59. Ограничение контроля (второй аргумент, u64 comparator)
явно раскрыто; отсутствие новых самостоятельных контролей не скрывается.


### Job 59 — полное семейство CD-3

Запрос `w1-merge-cd3-len2to4-control-009`, head `3820d796f0424461ca6bc36e313a5eaa6190e294`.
COMPLETE, expectation_met=True, measurement_ok=True, Kani exit=1. Gate=true подтверждён командой summary; check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Память run: max RSS 2154244 KiB, cgroup peak 2.35 GiB, ENFORCED 13 GiB, OOM kills 0, swap off. Wall verify-команды с компиляцией 0:58.70; пик общий на run.

| Гармоника | expect | status | Verification Time, с | cover |
|---|---|---|---:|---|
| `w1_cd3_all_len2_safety` | SUCCESS | SUCCESS | 2.7584276 | 3/3 |
| `w1_cd3_all_len3_safety` | SUCCESS | SUCCESS | 3.7802327 | 3/3 |
| `w1_cd3_all_len4_safety` | SUCCESS | SUCCESS | 5.215171 | 3/3 |
| `w1_cd2_comparator_oob_must_fail` | FAILED | FAILED | 0.03472342 | 1/1 |

Локализованные failed checks (assertion-паники SUCCESS-строк допустимы по CD-1):
- `w1_cd3_all_len2_safety`: `This is a placeholder message; Kani doesn't support message formatted at runtime` @ `/home/circleci/project/library/core/src/slice/sort/shared/smallsort.rs:884`.
- `w1_cd3_all_len3_safety`: `This is a placeholder message; Kani doesn't support message formatted at runtime` @ `/home/circleci/project/library/core/src/slice/sort/shared/smallsort.rs:884`.
- `w1_cd3_all_len4_safety`: `This is a placeholder message; Kani doesn't support message formatted at runtime` @ `/home/circleci/project/library/core/src/slice/sort/shared/smallsort.rs:884`.
- `w1_cd2_comparator_oob_must_fail`: `dereference failure: pointer invalid` @ `/home/circleci/project/library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs:1460`.
- `w1_cd2_comparator_oob_must_fail`: `dereference failure: pointer outside object bounds` @ `/home/circleci/project/library/core/src/ptr/mod.rs:2179`.

У каждой SUCCESS-строки ожидаются три normal-return cover; число в таблице взято из summary. Контроль проверяет второй аргумент u64 comparator; expected text и место приведены выше. Covers FAILED-строки не являются условием gate: достижимость подтверждает локализованный провал.
Время одной длины общее для independently chosen direct general u64, actual UnstableSmallSortTypeImpl transparent non-Copy u64, stable-Freeze u64. Не отдельные времена маршрутов. Ссылочная валидность/uninit/Drop/перестановка/unwind не заявлены.

REVIEW REQUEST 3820d796f0424461ca6bc36e313a5eaa6190e294

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`, `research/challenge-8/kani-k1/RUN-REQUEST.json`, `research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: summary этого job и check-tooling против базы волны. Код семейства R9 GO_WITH_NITS на c5720c76; зачёт новых измерений — через координатора.

Сумма wall verify-команд по summary 9 завершённых собственных jobs: 991.87 с (16.5312 мин), без подготовки CircleCI. Это оценка для RESULT, не API job wall; фактический учёт 250 минут ведёт координатор.

Следующий запрос `w1-merge-cd3-len5to7-010`: длины [5, 6, 7] + обязательный CD-2 FAILED-контроль. После dispatch **10/22**, лимит **250 фактических минут**; один активный job, окно dispatch до16:16:18Z. Lane и код семейства не изменяются.

REVIEW REQUEST c0342b31056b926aec62da9d624beae734ac7528

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. CD-3 N5/6/7 + обязательный
CD-2 FAILED-контроль; evidence — следующий CircleCI job.


### Продолжение W1-merge (Claude), T0 2026-10-26T12:51:49Z

CD-4: исполнитель W1-merge сменён (Codex → Claude, субагент координатора),
ветка и worktree прежние, старт с чистого `c15284bc`. База `36e5b6f6`
влита обычным merge; lane diff против `9de80e0b` пуст. Окно прежнее:
dispatch до **16:16:18Z**, отчёт до **16:46:18Z**. Лимиты CD-3: 22 dispatch,
250 фактических минут; использовано 11 dispatch (включая job 66), ≈29 мин
по данным координатора.

### Job 66 — полное семейство CD-3, N5/6/7 + контроль CD-2

Запрос `w1-merge-cd3-len5to7-010`, head `c15284bc9c0569a43257a5575e380a3575889dbe`.
COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 1
(ожидаем из-за контроля FAILED). check-tooling **ok** против
`9de80e0bec13896bb35a5e04e771448d9fe3931b`. Память run: max RSS 2153672 KiB,
cgroup peak 2.34 GiB, ENFORCED 13 GiB, OOM kills 0, swap off; wall verify
с компиляцией 1:10.87.

| Гармоника | expect | status | Verification Time, с | failed/total | cover |
|---|---|---|---:|---|---|
| `w1_cd3_all_len5_safety` | SUCCESS | SUCCESS | 6.248865 | 1/645 | 3/3 |
| `w1_cd3_all_len6_safety` | SUCCESS | SUCCESS | 8.316657 | 1/645 | 3/3 |
| `w1_cd3_all_len7_safety` | SUCCESS | SUCCESS | 9.941335 | 1/645 | 3/3 |
| `w1_cd2_comparator_oob_must_fail` | FAILED | FAILED | 0.033569846 | 2/19 | 1/1 |

- SUCCESS-строки: единственный failed check — assertion-класса паника
  `smallsort.rs:884` (placeholder message), допустима по CD-1. 14 unreachable
  checks в каждой (summary notes).
- Контроль: `dereference failure: pointer invalid` @ `kani_k1/merge.rs:1460` и
  `dereference failure: pointer outside object bounds` @ `core/src/ptr/mod.rs:2179`
  — те же места, что в job 59.
- Время строки общее для трёх независимо выбираемых маршрутов (direct
  general u64, реальный `UnstableSmallSortTypeImpl` на transparent non-Copy
  u64, stable-Freeze u64).

**W1-D13 (R7, CD-4):** по заданию продолжения контроль CD-2 больше не
включается в каждый запрос, пока код `merge.rs` не меняется (он неизменен с
`c5720c76`; контроль измерен в job 59 и 66). Это заменяет условие из R9
`c5720c76` «контроль в каждом dispatch». N17/24/32 не перепрогоняются: для
direct general и stable-Freeze они измерены с читающим comparator в job 53;
реальный `UnstableSmallSortTypeImpl` на 17/24/32 остаётся неизмеренным
(в job 53 — `UnstableSmallSortFreezeTypeImpl`), это раскрывается в итоге.
Оставшиеся 22 длины: пакеты [8,9,10,11], [12,13,14,15], [16,18,19,20],
[21,22,23,25], [26,27,28,29], [30,31] — 6 dispatch, до 17/22.

Запрос `w1-merge-cd3-len8to11-011`: N8/9/10/11, expect SUCCESS. Dispatch 12/22.

### Job 68 — CD-3 N8/9/10/11

Запрос `w1-merge-cd3-len8to11-011`, head `38accaf131d6ea3e8d36fb2f4d21d1924e7f8f68`.
COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
check-tooling **ok** против `9de80e0b…`. Память run: max RSS 2154412 KiB,
cgroup peak 2.36 GiB, ENFORCED 13 GiB, OOM 0, swap off; wall verify 1:54.84.

| Гармоника | status | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `w1_cd3_all_len8_safety` | SUCCESS | 14.61601 | 1/645 | 3/3 |
| `w1_cd3_all_len9_safety` | SUCCESS | 15.602869 | 1/645 | 3/3 |
| `w1_cd3_all_len10_safety` | SUCCESS | 18.411224 | 1/645 | 3/3 |
| `w1_cd3_all_len11_safety` | SUCCESS | 20.330036 | 1/645 | 3/3 |

Единственный failed check каждой строки — assertion-класса `smallsort.rs:884`
(CD-1). 10 unreachable checks в каждой строке.

Запрос `w1-merge-cd3-len12to15-012`: N12/13/14/15, expect SUCCESS. Dispatch 13/22.

### Job 69 — CD-3 N12/13/14/15

Запрос `w1-merge-cd3-len12to15-012`, head `2787a8b291cee96fd54aa68a967d853040b07021`.
COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
check-tooling **ok** против `9de80e0b…`. Память run: max RSS 2154332 KiB,
cgroup peak 2.36 GiB, ENFORCED 13 GiB, OOM 0, swap off; wall verify 2:24.89.

| Гармоника | status | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `w1_cd3_all_len12_safety` | SUCCESS | 22.71148 | 1/645 | 3/3 |
| `w1_cd3_all_len13_safety` | SUCCESS | 23.134647 | 1/645 | 3/3 |
| `w1_cd3_all_len14_safety` | SUCCESS | 27.154371 | 1/645 | 3/3 |
| `w1_cd3_all_len15_safety` | SUCCESS | 28.768175 | 1/645 | 3/3 |

Единственный failed check каждой строки — assertion-класса `smallsort.rs:884`
(CD-1). 10 unreachable checks в каждой строке.

Запрос `w1-merge-cd3-len16to20-013`: N16/18/19/20, expect SUCCESS. Dispatch 14/22.

### Job 70 — CD-3 N16/18/19/20

Запрос `w1-merge-cd3-len16to20-013`, head `c916a578a8841ce5d20b216381d430bbf195eaff`.
COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
check-tooling **ok** против `9de80e0b…`. Память run: max RSS 2347504 KiB,
cgroup peak 3.29 GiB, ENFORCED 13 GiB, OOM 0, swap off; wall verify 4:40.81.

| Гармоника | status | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `w1_cd3_all_len16_safety` | SUCCESS | 50.011974 | 1/645 | 3/3 |
| `w1_cd3_all_len18_safety` | SUCCESS | 54.93522 | 1/645 | 3/3 |
| `w1_cd3_all_len19_safety` | SUCCESS | 60.83016 | 1/645 | 3/3 |
| `w1_cd3_all_len20_safety` | SUCCESS | 62.214634 | 1/645 | 3/3 |

Единственный failed check каждой строки — assertion-класса `smallsort.rs:884`
(CD-1). 8 unreachable checks в каждой строке.

**W1-D14 (R7):** trait-маршрут на 17/24/32 не перепрогоняю (указание
координатора). Основание, что пробел узкий: в `smallsort.rs:90-103`
`impl<T: FreezeMarker> UnstableSmallSortTypeImpl` для Freeze-типа лишь
пересылает в `<T as UnstableSmallSortFreezeTypeImpl>::small_sort`
(`#[inline(always)]`); `W1GeneralU64` — Freeze. Job 53 измерил именно
callee пересылки. Это чтение исходника, не измерение; раскрывается в итоге.

Запрос `w1-merge-cd3-len21to25-014`: N21/22/23/25, expect SUCCESS. Dispatch 15/22.

### Job 71 — CD-3 N21/22/23/25

Запрос `w1-merge-cd3-len21to25-014`, head `bae2b2063f53fbea9a407c14813cba33d37e96d0`.
COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
check-tooling **ok** против `9de80e0b…`. Память run: max RSS 3079148 KiB,
cgroup peak 4.01 GiB, ENFORCED 13 GiB, OOM 0, swap off; wall verify 5:27.81.

| Гармоника | status | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `w1_cd3_all_len21_safety` | SUCCESS | 61.972004 | 1/645 | 3/3 |
| `w1_cd3_all_len22_safety` | SUCCESS | 65.25795 | 1/645 | 3/3 |
| `w1_cd3_all_len23_safety` | SUCCESS | 71.73119 | 1/645 | 3/3 |
| `w1_cd3_all_len25_safety` | SUCCESS | 81.748344 | 1/645 | 3/3 |

Единственный failed check каждой строки — assertion-класса `smallsort.rs:884`
(CD-1). 8 unreachable checks в каждой строке.

Запрос `w1-merge-cd3-len26to29-015`: N26/27/28/29, expect SUCCESS. Dispatch 16/22.

### Job 72 — CD-3 N26/27/28/29

Запрос `w1-merge-cd3-len26to29-015`, head `4f1cfaa0e01c242d41e0bd91ec0b70d1b4c566a9`.
COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
check-tooling **ok** против `9de80e0b…`. Память run: max RSS 3827424 KiB,
cgroup peak 4.99 GiB, ENFORCED 13 GiB, OOM 0, swap off; wall verify 7:42.57.

| Гармоника | status | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `w1_cd3_all_len26_safety` | SUCCESS | 96.47715 | 1/645 | 3/3 |
| `w1_cd3_all_len27_safety` | SUCCESS | 101.03213 | 1/645 | 3/3 |
| `w1_cd3_all_len28_safety` | SUCCESS | 102.43274 | 1/645 | 3/3 |
| `w1_cd3_all_len29_safety` | SUCCESS | 111.75234 | 1/645 | 3/3 |

Единственный failed check каждой строки — assertion-класса `smallsort.rs:884`
(CD-1). 8 unreachable checks в каждой строке.

Запрос `w1-merge-cd3-len30to31-016`: N30/31, expect SUCCESS. Dispatch 17/22 (последний пакет семейства).

### Job 73 — CD-3 N30/31

Запрос `w1-merge-cd3-len30to31-016`, head `3a347ad00131a7eb2530725e648b298b317120a4`.
COMPLETE, gate **true**, expectation met true, measurement ok true, Kani exit 0.
check-tooling **ok** против `9de80e0b…`. Память run: max RSS 4287908 KiB,
cgroup peak 4.96 GiB, ENFORCED 13 GiB, OOM 0, swap off; wall verify 5:13.01.

| Гармоника | status | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `w1_cd3_all_len30_safety` | SUCCESS | 127.47352 | 1/645 | 3/3 |
| `w1_cd3_all_len31_safety` | SUCCESS | 138.8601 | 1/645 | 3/3 |

Единственный failed check каждой строки — assertion-класса `smallsort.rs:884`
(CD-1). 8 unreachable checks в каждой строке. Семейство CD-3 закрыто:
TIMEOUT, OOM, tool failure или FAILED безопасности не было ни в одном job.

### Итог волны 1 W1-merge

Обозначения маршрутов: **D** — `small_sort_general` напрямую, u64;
**T** — general через trait, `#[repr(transparent)] W1GeneralU64(u64)` без Copy
(Freeze, размер 8); **S** — `<u64 as StableSmallSortTypeImpl>::small_sort`,
scratch 48. В одной гармонике маршрут выбирается `kani::any()`, время —
**общее** на все маршруты строки, отдельно по маршрутам не измерено.
Comparator во всех строках читает оба аргумента (CD-2) и возвращает
`kani::any()`. Все строки: SUCCESS, единственный failed check —
assertion-класса паника `smallsort.rs:884` (допустима по CD-1),
check-tooling ok, ENFORCED 13 GiB, OOM 0.

| Длина | Маршруты | Verification Time, с | gate | cover | job | head |
|---:|---|---:|---|---|---|---|
| 0 | D, S | 139.0581 (вся гармоника границ) | true | 29/29 (вся гармоника) | 56 | `d0b1192d` |
| 1 | D, S | то же | true | то же | 56 | `d0b1192d` |
| 2 | D, T, S | 2.7584276 | true | 3/3 | 59 | `3820d796` |
| 3 | D, T, S | 3.7802327 | true | 3/3 | 59 | `3820d796` |
| 4 | D, T, S | 5.215171 | true | 3/3 | 59 | `3820d796` |
| 5 | D, T, S | 6.248865 | true | 3/3 | 66 | `c15284bc` |
| 6 | D, T, S | 8.316657 | true | 3/3 | 66 | `c15284bc` |
| 7 | D, T, S | 9.941335 | true | 3/3 | 66 | `c15284bc` |
| 8 | D, T, S | 14.61601 | true | 3/3 | 68 | `38accaf1` |
| 9 | D, T, S | 15.602869 | true | 3/3 | 68 | `38accaf1` |
| 10 | D, T, S | 18.411224 | true | 3/3 | 68 | `38accaf1` |
| 11 | D, T, S | 20.330036 | true | 3/3 | 68 | `38accaf1` |
| 12 | D, T, S | 22.71148 | true | 3/3 | 69 | `2787a8b2` |
| 13 | D, T, S | 23.134647 | true | 3/3 | 69 | `2787a8b2` |
| 14 | D, T, S | 27.154371 | true | 3/3 | 69 | `2787a8b2` |
| 15 | D, T, S | 28.768175 | true | 3/3 | 69 | `2787a8b2` |
| 16 | D, T, S | 50.011974 | true | 3/3 | 70 | `c916a578` |
| 17 | D, T\*, S | 49.96133 | true | 3/3 | 53 | `38faf5ff` |
| 18 | D, T, S | 54.93522 | true | 3/3 | 70 | `c916a578` |
| 19 | D, T, S | 60.83016 | true | 3/3 | 70 | `c916a578` |
| 20 | D, T, S | 62.214634 | true | 3/3 | 70 | `c916a578` |
| 21 | D, T, S | 61.972004 | true | 3/3 | 71 | `bae2b206` |
| 22 | D, T, S | 65.25795 | true | 3/3 | 71 | `bae2b206` |
| 23 | D, T, S | 71.73119 | true | 3/3 | 71 | `bae2b206` |
| 24 | D, T\*, S | 85.08464 | true | 3/3 | 53 | `38faf5ff` |
| 25 | D, T, S | 81.748344 | true | 3/3 | 71 | `bae2b206` |
| 26 | D, T, S | 96.47715 | true | 3/3 | 72 | `4f1cfaa0` |
| 27 | D, T, S | 101.03213 | true | 3/3 | 72 | `4f1cfaa0` |
| 28 | D, T, S | 102.43274 | true | 3/3 | 72 | `4f1cfaa0` |
| 29 | D, T, S | 111.75234 | true | 3/3 | 72 | `4f1cfaa0` |
| 30 | D, T, S | 127.47352 | true | 3/3 | 73 | `3a347ad0` |
| 31 | D, T, S | 138.8601 | true | 3/3 | 73 | `3a347ad0` |
| 32 | D, T\*, S, + слияние u64×32 | 165.27512 | true | 4/4 | 53 | `38faf5ff` |
| слияние u64×32 отдельно | `bidirectional_merge` | в строке 32 (job 53) | true | 4/4 | 53 | `38faf5ff` |

T — `UnstableSmallSortTypeImpl` (реальный вход quicksort). **T\*** — в job 53
`UnstableSmallSortFreezeTypeImpl`; для Freeze-типа `UnstableSmallSortTypeImpl`
только пересылает в него (`smallsort.rs:90-103`, W1-D14). Длины 0/1/2/3/7/8/9/15
D и S дополнительно измерены в job 56 (139.0581 с на всю гармонику), длина 16
T и D/S — тоже в job 56. Job 49 (`1d230f75`, слияние u64×32, 4.5430408 с) и
51/52 — до CD-2, comparator без чтения, самостоятельного зачёта не дают.
Наибольшее время строки — 165.28 с (N32), пик cgroup по всем run ≤ 5.55 GiB.

**Область и ограничения.**

- Типы: только u64; для T — прозрачный non-Copy u64 (Freeze, без Drop).
  Ветка presort sort4 при len ≥ 16 для типов > 16 байт не инстанцируется
  (K-16, волна 3).
- Comparator: `kani::any()`, читает оба аргумента (`read_volatile`, CD-2);
  контроль CD-2 (второй аргумент за объектом) измерен FAILED в job 59 и 66.
- Смысл О1 по CD-1: ни на одном пути нет упавшей проверки безопасности Kani
  (разыменование за объектом, мёртвый/невыровненный указатель в рамках
  включённых проверок). Паники класса assertion допустимы; отсутствие
  других паник, перестановка, Drop, сортированность не проверялись.
- Uninit-чтения не проверены (нет `-Z uninit-checks`); полная reference
  validity не заявлена.
- Unwind не моделируется (`-Cpanic=abort`): восстановление при панике
  comparator (CopyOnDrop/guards) не проверено.
- Слияние отдельно — только длина 32 (чётный путь); нечётный хвост
  финального слияния покрыт верхними маршрутами на нечётных длинах 17..31.
- Не измерено: T на длинах 0 и 1 (тело general при len < 2 сразу
  возвращается, `smallsort.rs:226`; T его не вызывал); новый вход T на
  17/24/32 (измерен пересылаемый callee, T\*). Неудачных или
  незасчитанных длин нет. Длины — постоянные, по отдельной гармонике;
  символьной длины нет.
- Network-маршрут — у W1-network; K-13 не брался (передан W1-network, CD-4).

О1 по маршрутам со слиянием закрыта до 32.

**Расход.** Dispatch **17/22** (W1-merge Claude: job 68–73, 6 dispatch; job 66
— dispatch Codex). Фактические минуты до job 66 включительно — ≈29 мин по
данным координатора. Wall verify-команд job 68–73 по summary:
114.84 + 144.89 + 280.81 + 327.81 + 462.57 + 313.01 = 1643.93 с (27.4 мин);
с подготовкой CircleCI оценка ≈36 мин, итого ≈65 из 250 мин. Это оценка по
summary, не API; сверка — у координатора. Незавершённых job нет.

REVIEW REQUEST e07da161d347a410b2d3af9d47f9d580278ccc2b

Файлы: `research/challenge-8/kani-k1/RESULT-merge.md`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`. `merge.rs` не менялся с
`c5720c76` (R9 GO_WITH_NITS). Evidence: summary job 66, 68–73 и check-tooling
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.

ВОЛНА 1 ЗАВЕРШЕНА

## Волна 2

T0: 2026-10-26T15:18:47Z (`date -u`).

Новые dispatch до **2026-10-26T18:48:47Z**, отчёт до **2026-10-26T19:18:47Z**.
П1: ≤14 dispatch, ≤150 фактических минут job, один незавершённый job.
T0 опубликован в `2f0a6e7b`. Lane diff против `9de80e0b…` пуст.

### Решения R7

- **W2-D1.** П1 выполняется по выданному владельцем заданию; исторический
  статус «НЕ ВЫДАНО» в документах не блокирует. П2 не выполняется.
- **W2-D2.** C-5: по одной гармонике под `should_panic`, реальное слияние
  `[0,1,2,3]` и честный comparator, cover нормального возврата до проверки.
  Выбран `intrinsics::assume`, разрешённый заданием вместо `assert_unchecked`.
  Все четыре ожидания FAILED получены из исходников Kani на pin
  `9461e07af7ec929f050aa4192f29363c9be07779`; фактические исходы фиксируются
  независимо от gate. Несовпадение — измерение, не причина менять ожидание.
- **W2-D3.** Контроль А — новые `w2_control_a_assertion` (FAILED,
  `assertion failed: value != value`) и `w2_control_a_reachable` (SUCCESS)
  в своём `merge.rs`, с читающим comparator. До их measurement нет зачёта O1-A.
- **W2-D4.** O1-A повторяет CD-3 N2..32 через те же helpers: D general u64,
  T реальный `UnstableSmallSortTypeImpl` на transparent non-Copy u64,
  S stable-Freeze u64. Маршрут выбирается независимо до создания входа.
  Слияние u64×32 — отдельная гармоника. Время объединённой длины общее для
  D/T/S; при >180 с длина делится по маршрутам. Альтернатива сразу разделить
  все маршруты требует лишних dispatch; оставлены четыре резервных dispatch
  сверх плана 1 C-5 + 1 контроль А + 8 пакетов O1-A.

### Ledger и область

- `stub_verified`: нет; callee реальные, контракты/runtime/lane не меняются.
- Единственная ручная заглушка — прежняя `w1_abort_ord_violation` для
  `panic_on_ord_violation`: `cover(true)` затем `kani::assume(false)`;
  применяется только в новых контролях А и O1-A. Обоснование `-Cpanic=abort`.
  Достижимость отдельно проверяет `w2_control_a_reachable` и covers сводок.
- C-5 `intrinsics::assume(first != 0)` — намеренно нарушенное условие
  измеряемой проверки, не ограничение входов доказательства. Cover перед ним.
- Новых `any_where` и других `kani::assume` нет. Массивы ровно N, scratch 48;
  все u64 без редукции значений. N0/1 — прежние ранние возвраты, вне повтора П1.
- Не проверяются uninit-чтения (нет `-Z uninit-checks`), алиасинг, полная
  reference validity, перестановка/сортированность/Drop и восстановление
  CopyOnDrop при unwind. Отдельное слияние N32 покрывает чётный путь;
  нечётный хвост измеряется верхними маршрутами на нечётных N17..31.

### C-5: ожидания до dispatch

Источник: официальный `model-checking/kani`, pin выше. `intrinsic.rs:299–304`
порождает класс `assume`; `rvalue.rs:187–231` — `arithmetic_overflow`;
`intrinsic.rs:1125–1148` передаёт copy в CBMC memcpy (текст подтверждён
`tests/expected/intrinsics/copy-nonoverlapping/copy-overlapping/expected`);
`rustc_intrinsics.rs:102–136` подставляет offset model,
`library/kani_core/src/models.rs:163–166` — `safety_check` границ.
`call_cbmc.rs:716–759` маскирует только класс `assertion`.
`operand.rs:60–64` отключает std RuntimeChecks.

| Гармоника (префикс `w2_c5_`) | expect | expect_check | actual / место |
|---|---|---|---|
| `intrinsic_assume` | FAILED | `Rust intrinsic assumption failed` | FAILED, `merge.rs:1522` |
| `unchecked_add` | FAILED | ``attempt to compute `unchecked_add` which would overflow`` | FAILED, `core/src/num/uint_macros.rs:1039` |
| `copy_nonoverlapping` | FAILED | `memcpy src/dst overlap` | FAILED, `core/src/ptr/mod.rs:582` |
| `ptr_add` | FAILED | `Offset result and original pointer must point to the same allocation` | FAILED, `core/src/lib.rs:357` (offset model) |

### Журнал прогонов

Подготовлен `w2-merge-c5-001`: 4×10 мин, measurement,
`circleci-linux-large`; request validate и `git diff --check` — ok.
После dispatch: **1/14**. Фактические минуты job ещё не измерены;
API-учёт сверяет координатор. O1-A пока не измерена, proof credit нет.

REVIEW REQUEST e4e24db87cf554ba4c0011ee8acae4d33dbe8d2e

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Review R9 через координатора.

### Job 76 — C-5

Head `73d430ecfbf84bb86b3244b2634bdb4b41e3c235`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 1 (четыре ожидаемых FAILED).
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1655396 KiB, cgroup peak 1.89 GiB, ENFORCED 13 GiB,
OOM 0, swap off, wall verify с компиляцией 41.12 с.

| Гармоника (префикс `w2_c5_`) | expect / actual | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `intrinsic_assume` | FAILED / FAILED | 0.36273086 | 1/139 | 1/1 |
| `unchecked_add` | FAILED / FAILED | 0.36430338 | 1/153 | 1/1 |
| `copy_nonoverlapping` | FAILED / FAILED | 0.3752446 | 1/126 | 1/1 |
| `ptr_add` | FAILED / FAILED | 0.37160674 | 1/137 | 1/1 |

Текст и место единственного failed check каждой строки — в таблице C-5
выше. В каждой строке 4 unreachable checks. Все четыре нарушения измерены
как FAILED под `should_panic`, маскировки этих проверок не наблюдалось.
Это измерение C-5; независимый R9 пока ожидается.

Следующий запрос `w2-merge-control-a-002`: две гармоники по 10 мин.
После dispatch **2/14**; завершённый job один, wall verify 0.6853 мин
(без подготовки CircleCI, не API job wall). O1-A пока не измерена.

REVIEW REQUEST 8af80c538e36d9a3395daf5732804b21b4249bba

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(без изменений с `e4e24db8`), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence C-5: job 76 summary
и check-tooling ok. Следующее измерение — контроль А.

### Job 78 — контроль (А)

Head `87a0ff6c6514839681df889aebfa12b6c3742c1f`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 1 (ожидаемый FAILED).
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1607440 KiB, cgroup peak 1.84 GiB, ENFORCED 13 GiB,
OOM 0, swap off, wall verify с компиляцией 41.03 с.

| Гармоника | expect / actual | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `w2_control_a_assertion` | FAILED / FAILED | 0.62573564 | 1/114 | 2/2 |
| `w2_control_a_reachable` | SUCCESS / SUCCESS | 0.5946428 | 0/113 | 2/2 |

Единственный failed check: `assertion failed: value != value`
@ `kani_k1/merge.rs:1573`. В обеих гармониках 4 unreachable checks.
Cover заглушки и нормального возврата выполнены. Контроль А измерен до
первого O1-A; независимый review R9 ещё ожидается, окончательного зачёта нет.

Следующий запрос `w2-merge-o1a-len2to5-003`: N2/3/4/5, 4×10 мин.
Ожидается SUCCESS и 4 cover на строку (D/T/S + заглушка).
После dispatch **3/14**. Два завершённых job: суммарный wall verify
82.15 с (1.3692 мин), без подготовки CircleCI; API job wall у координатора.

REVIEW REQUEST e4a09490c1c6ae8b5b3d0b1088a1ba1e0323458d

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `e4e24db8`), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: контроли job 76/78,
обе сводки и check-tooling ok; далее O1-A N2..5.

### Job 79 — O1-A N2..5

Head `b622e9378b7fd340f4a6ab50e7bc3ca4d8fb9428`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 2168356 KiB, cgroup peak 2.37 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 63.34 с.

| Гармоника (префикс `w2_a_all_`) | Маршруты | expect / actual | Verification Time, с | gate | cover |
|---|---|---|---:|---|---|
| `len2_safety` | D/T/S | SUCCESS / SUCCESS | 2.5793238 | true | 4/4 |
| `len3_safety` | D/T/S | SUCCESS / SUCCESS | 3.548163 | true | 4/4 |
| `len4_safety` | D/T/S | SUCCESS / SUCCESS | 4.867044 | true | 4/4 |
| `len5_safety` | D/T/S | SUCCESS / SUCCESS | 6.181312 | true | 4/4 |

Каждая строка: 0/645 failed checks, 15 unreachable checks; время общее для
независимого выбора D/T/S, covers — D/T/S и вызов заглушки. Измерены N2..5,
все ≤180 с; независимый R9 ещё ожидается.

REVIEW REQUEST b622e9378b7fd340f4a6ab50e7bc3ca4d8fb9428

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(без изменений с `e4e24db8`), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 79 summary,
check-tooling ok; контроли job 76/78.

Следующий запрос `w2-merge-o1a-len6to9-004`: N6/7/8/9, 4×10 мин.
После dispatch **4/14**. Три завершённых job, wall verify суммарно
145.49 с (2.4248 мин); подготовка CircleCI не включена, API-учёт у координатора.

### R9 — GO_WITH_NITS (сообщение координатора)

Review `e4e24db87cf554ba4c0011ee8acae4d33dbe8d2e` — **GO_WITH_NITS**.
Классы C-5 подтверждены на pin: `assume`, `arithmetic_overflow`,
`precondition_instance` (memcpy), `safety_check`; все не `assertion`.
Измеренные FAILED job 76 совпали с ожиданиями и точными текстами.

Ниты учтены:
- В summary явно сверены полные counts: job 78 **2/2** в каждой гармонике
  (нормальный возврат + `wave1: panic_on_ord_violation is reachable`),
  job 79 и 81 **4/4** в каждой строке (D/T/S + тот же cover заглушки).
  Это отдельная проверка counts, не вывод только из gate.
- C-5 status/text записываются независимо от gate. Отсутствие Rust-location
  у модели memcpy допускается как результат измерения; в job 76 место
  фактически есть (`core/src/ptr/mod.rs:582`) и gate true.

### Job 81 — O1-A N6..9

Head `b27d4ea791ef4c08b7190ed53b6f04dbb8587a3a`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 2162488 KiB, cgroup peak 2.37 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 102.90 с.

| Гармоника (префикс `w2_a_all_`) | Маршруты | expect / actual | Verification Time, с | gate | cover |
|---|---|---|---:|---|---|
| `len6_safety` | D/T/S | SUCCESS / SUCCESS | 8.689595 | true | 4/4 |
| `len7_safety` | D/T/S | SUCCESS / SUCCESS | 10.21102 | true | 4/4 |
| `len8_safety` | D/T/S | SUCCESS / SUCCESS | 16.11851 | true | 4/4 |
| `len9_safety` | D/T/S | SUCCESS / SUCCESS | 17.801754 | true | 4/4 |

Каждая строка: 0/645 failed checks. Unreachable: N6/7 — 15, N8/9 — 11.
Cover заглушки выполнен: полный счёт 4/4 сверён по summary каждой строки.
Время общее для независимо выбранных D/T/S. Измерены все N2..9, ≤180 с.

REVIEW REQUEST b27d4ea791ef4c08b7190ed53b6f04dbb8587a3a

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `e4e24db8`, R9 GO_WITH_NITS), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 81 summary,
check-tooling ok, полный count cover сверён.

Следующий запрос `w2-merge-o1a-len10to13-005`: N10/11/12/13, 4×10 мин.
После dispatch **5/14**. Четыре завершённых job: wall verify суммарно
248.39 с (4.1398 мин), без подготовки CircleCI; API-учёт у координатора.

### Job 83 — O1-A N10..13

Head `d57f69c8f40ad53cbafc2dd4466e801d79fe691c`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 2154548 KiB, cgroup peak 2.36 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 128.94 с.

| Гармоника (префикс `w2_a_all_`) | Маршруты | expect / actual | Verification Time, с | gate | cover |
|---|---|---|---:|---|---|
| `len10_safety` | D/T/S | SUCCESS / SUCCESS | 17.432873 | true | 4/4 |
| `len11_safety` | D/T/S | SUCCESS / SUCCESS | 20.485754 | true | 4/4 |
| `len12_safety` | D/T/S | SUCCESS / SUCCESS | 21.9637 | true | 4/4 |
| `len13_safety` | D/T/S | SUCCESS / SUCCESS | 24.926888 | true | 4/4 |

Каждая строка: 0/645 failed checks, 11 unreachable checks. Полный счёт 4/4
(D/T/S + `panic_on_ord_violation is reachable`) сверён по summary отдельно
от gate. Время общее для D/T/S. Все N2..13 измерены, каждая ≤180 с.

REVIEW REQUEST d57f69c8f40ad53cbafc2dd4466e801d79fe691c

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `e4e24db8`, R9 GO_WITH_NITS), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 83 summary
и check-tooling ok.

Следующий запрос `w2-merge-o1a-len14to17-006`: N14/15/16/17, 4×10 мин.
После dispatch **6/14**. Пять завершённых job: wall verify суммарно
377.33 с (6.2888 мин), без подготовки CircleCI; API-учёт у координатора.

### Job 84 — O1-A N14..17

Head `09fa4c8d8a2c1454edb2ad418901058c41cfb52e`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 2157792 KiB, cgroup peak 2.58 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 196.79 с.

| Гармоника (префикс `w2_a_all_`) | Маршруты | expect / actual | Verification Time, с | gate | cover |
|---|---|---|---:|---|---|
| `len14_safety` | D/T/S | SUCCESS / SUCCESS | 29.337519 | true | 4/4 |
| `len15_safety` | D/T/S | SUCCESS / SUCCESS | 31.130058 | true | 4/4 |
| `len16_safety` | D/T/S | SUCCESS / SUCCESS | 43.146065 | true | 4/4 |
| `len17_safety` | D/T/S | SUCCESS / SUCCESS | 46.642475 | true | 4/4 |

Каждая строка: 0/645 failed checks. Unreachable N14/15 — 11, N16/17 — 9.
Полный счёт 4/4 (D/T/S + `panic_on_ord_violation is reachable`) сверён
по summary отдельно от gate. Время общее для D/T/S. Измерены все N2..17,
каждая ≤180 с; N16 — переход presort sort8, N17 — нечётный хвост слияния.

REVIEW REQUEST 09fa4c8d8a2c1454edb2ad418901058c41cfb52e

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `e4e24db8`, R9 GO_WITH_NITS), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 84 summary
и check-tooling ok.

Следующий запрос `w2-merge-o1a-len18to21-007`: N18/19/20/21, 4×10 мин.
После dispatch **7/14**. Шесть завершённых job: wall verify суммарно
574.12 с (9.5687 мин), без подготовки CircleCI; API-учёт у координатора.

### Job 86 — O1-A N18..21

Head `133f3547f52617d206d64ec6d937c1bb4d0b1edc`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 2494916 KiB, cgroup peak 3.46 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 282.70 с.

| Гармоника (префикс `w2_a_all_`) | Маршруты | expect / actual | Verification Time, с | gate | cover |
|---|---|---|---:|---|---|
| `len18_safety` | D/T/S | SUCCESS / SUCCESS | 48.65015 | true | 4/4 |
| `len19_safety` | D/T/S | SUCCESS / SUCCESS | 59.94247 | true | 4/4 |
| `len20_safety` | D/T/S | SUCCESS / SUCCESS | 59.3483 | true | 4/4 |
| `len21_safety` | D/T/S | SUCCESS / SUCCESS | 65.65012 | true | 4/4 |

Каждая строка: 0/645 failed checks, 9 unreachable checks. Полный счёт 4/4
(D/T/S + `panic_on_ord_violation is reachable`) сверён по summary отдельно
от gate. Время общее для D/T/S. Все N2..21 измерены, каждая ≤180 с.

REVIEW REQUEST 133f3547f52617d206d64ec6d937c1bb4d0b1edc

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `e4e24db8`, R9 GO_WITH_NITS), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 86 summary
и check-tooling ok.

Следующий запрос `w2-merge-o1a-len22to25-008`: N22/23/24/25, 4×10 мин.
После dispatch **8/14**. Семь завершённых job: wall verify суммарно
856.82 с (14.2803 мин), без подготовки CircleCI; API-учёт у координатора.

### Job 87 — O1-A N22..25

Head `7f4fccfd06c62e0e37cc17b1ae24d26963c63611`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 3084428 KiB, cgroup peak 4.28 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 364.94 с.

| Гармоника (префикс `w2_a_all_`) | Маршруты | expect / actual | Verification Time, с | gate | cover |
|---|---|---|---:|---|---|
| `len22_safety` | D/T/S | SUCCESS / SUCCESS | 73.35616 | true | 4/4 |
| `len23_safety` | D/T/S | SUCCESS / SUCCESS | 76.80564 | true | 4/4 |
| `len24_safety` | D/T/S | SUCCESS / SUCCESS | 79.66041 | true | 4/4 |
| `len25_safety` | D/T/S | SUCCESS / SUCCESS | 85.714836 | true | 4/4 |

Каждая строка: 0/645 failed checks, 9 unreachable checks. Полный счёт 4/4
(D/T/S + `panic_on_ord_violation is reachable`) сверён по summary отдельно
от gate. Время общее для D/T/S. Все N2..25 измерены, каждая ≤180 с.

REVIEW REQUEST 7f4fccfd06c62e0e37cc17b1ae24d26963c63611

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `e4e24db8`, R9 GO_WITH_NITS), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 87 summary
и check-tooling ok.

Следующий запрос `w2-merge-o1a-len26to29-009`: N26/27/28/29, 4×10 мин.
После dispatch **9/14**. Восемь завершённых job: wall verify суммарно
1221.76 с (20.3627 мин), без подготовки CircleCI; API-учёт у координатора.

### Job 90 — O1-A N26..29

Head `752f55eeba02ffc8add43038f38ab3ad78c642e0`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: Xeon 8175M 2.50GHz, max RSS 3820760 KiB, cgroup peak 4.75 GiB,
ENFORCED 13 GiB, OOM 0, swap off; wall verify с компиляцией 533.23 с.

| Гармоника (префикс `w2_a_all_`) | Маршруты | expect / actual | Verification Time, с | gate | cover |
|---|---|---|---:|---|---|
| `len26_safety` | D/T/S | SUCCESS / SUCCESS | 103.82107 | true | 4/4 |
| `len27_safety` | D/T/S | SUCCESS / SUCCESS | 111.82898 | true | 4/4 |
| `len28_safety` | D/T/S | SUCCESS / SUCCESS | 128.04454 | true | 4/4 |
| `len29_safety` | D/T/S | SUCCESS / SUCCESS | 133.3675 | true | 4/4 |

Каждая строка: 0/645 failed checks, 9 unreachable checks. Полный счёт 4/4
(D/T/S + `panic_on_ord_violation is reachable`) сверён по summary отдельно
от gate. Время общее для D/T/S. Все N2..29 измерены, каждая ≤180 с.

REVIEW REQUEST 752f55eeba02ffc8add43038f38ab3ad78c642e0

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `e4e24db8`, R9 GO_WITH_NITS), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 90 summary
и check-tooling ok.

Следующий запрос `w2-merge-o1a-len30to32-merge-010`: N30/31/32 D/T/S
и отдельное слияние u64×32, 4×10 мин. N32 измеряется отдельно от слияния;
при превышении цели 180 с — разделение по маршрутам согласно W2-D4.
После dispatch **10/14**. Девять завершённых job: wall verify суммарно
1754.99 с (29.2498 мин), без подготовки CircleCI; API-учёт у координатора.

### Job 92 — O1-A N30..32 и отдельное слияние

Head `05905ca464f7a4ab658fe693fa392c5b6adc91a5`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 4513024 KiB, cgroup peak 5.65 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 443.51 с.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2_a_all_len30_safety` | SUCCESS / SUCCESS | 121.42389 | 0/645 | 9 | 4/4 |
| `w2_a_all_len31_safety` | SUCCESS / SUCCESS | 126.13239 | 0/645 | 9 | 4/4 |
| `w2_a_all_len32_safety` | SUCCESS / SUCCESS | 142.42654 | 0/645 | 9 | 4/4 |
| `w2_a_merge_u64_len32_safety` | SUCCESS / SUCCESS | 9.213874 | 0/113 | 4 | 2/2 |

Полные counts cover сверены по summary отдельно от gate: D/T/S +
`panic_on_ord_violation is reachable` — 4/4; отдельное слияние + заглушка —
2/2. Все ≤180 с, разделение по маршрутам не требуется.

### Итог П1: O1-A

**О1 по (А) закрыта до 32** для маршрутов W2-merge: N2..32 D/T/S,
отдельное слияние u64×32. N0/1 D/S остаются прежними ранними возвратами
волны 1 (job 56); T N0/1 отдельно не измерен и в повтор П1 не входил.

D — прямой `small_sort_general` на u64; T — реальный
`UnstableSmallSortTypeImpl` на transparent non-Copy `W1GeneralU64(u64)`
(Freeze, без Drop); S — `StableSmallSortTypeImpl` на u64, scratch 48.
Время D/T/S в каждой строке **общее** для независимого выбора маршрута,
отдельные времена маршрутов не измерены. Имя гармоники —
`w2_a_all_lenN_safety`; отдельное слияние указано последней строкой.

Во всех строках: SUCCESS, 0 failed checks, gate true, check-tooling ok;
полный cover заглушки проверен по counts summary, а не только по gate.
Comparator читает оба аргумента `read_volatile`, затем возвращает
`kani::any()`. Единственная обрезанная ветка — `panic_on_ord_violation`
через `w1_abort_ord_violation` с cover и `kani::assume(false)`.

| Длина | Маршруты | Verification Time, с | gate | cover | job | head |
|---:|---|---:|---|---|---:|---|
| 2 | D/T/S | 2.5793238 | true | 4/4 | 79 | `b622e937` |
| 3 | D/T/S | 3.548163 | true | 4/4 | 79 | `b622e937` |
| 4 | D/T/S | 4.867044 | true | 4/4 | 79 | `b622e937` |
| 5 | D/T/S | 6.181312 | true | 4/4 | 79 | `b622e937` |
| 6 | D/T/S | 8.689595 | true | 4/4 | 81 | `b27d4ea7` |
| 7 | D/T/S | 10.21102 | true | 4/4 | 81 | `b27d4ea7` |
| 8 | D/T/S | 16.11851 | true | 4/4 | 81 | `b27d4ea7` |
| 9 | D/T/S | 17.801754 | true | 4/4 | 81 | `b27d4ea7` |
| 10 | D/T/S | 17.432873 | true | 4/4 | 83 | `d57f69c8` |
| 11 | D/T/S | 20.485754 | true | 4/4 | 83 | `d57f69c8` |
| 12 | D/T/S | 21.9637 | true | 4/4 | 83 | `d57f69c8` |
| 13 | D/T/S | 24.926888 | true | 4/4 | 83 | `d57f69c8` |
| 14 | D/T/S | 29.337519 | true | 4/4 | 84 | `09fa4c8d` |
| 15 | D/T/S | 31.130058 | true | 4/4 | 84 | `09fa4c8d` |
| 16 | D/T/S | 43.146065 | true | 4/4 | 84 | `09fa4c8d` |
| 17 | D/T/S | 46.642475 | true | 4/4 | 84 | `09fa4c8d` |
| 18 | D/T/S | 48.65015 | true | 4/4 | 86 | `133f3547` |
| 19 | D/T/S | 59.94247 | true | 4/4 | 86 | `133f3547` |
| 20 | D/T/S | 59.3483 | true | 4/4 | 86 | `133f3547` |
| 21 | D/T/S | 65.65012 | true | 4/4 | 86 | `133f3547` |
| 22 | D/T/S | 73.35616 | true | 4/4 | 87 | `7f4fccfd` |
| 23 | D/T/S | 76.80564 | true | 4/4 | 87 | `7f4fccfd` |
| 24 | D/T/S | 79.66041 | true | 4/4 | 87 | `7f4fccfd` |
| 25 | D/T/S | 85.714836 | true | 4/4 | 87 | `7f4fccfd` |
| 26 | D/T/S | 103.82107 | true | 4/4 | 90 | `752f55ee` |
| 27 | D/T/S | 111.82898 | true | 4/4 | 90 | `752f55ee` |
| 28 | D/T/S | 128.04454 | true | 4/4 | 90 | `752f55ee` |
| 29 | D/T/S | 133.3675 | true | 4/4 | 90 | `752f55ee` |
| 30 | D/T/S | 121.42389 | true | 4/4 | 92 | `05905ca4` |
| 31 | D/T/S | 126.13239 | true | 4/4 | 92 | `05905ca4` |
| 32 | D/T/S | 142.42654 | true | 4/4 | 92 | `05905ca4` |
| 32 | отдельное слияние u64 | 9.213874 | true | 2/2 | 92 | `05905ca4` |

C-5: четыре ожидаемых FAILED измерены в job 76, точные тексты и места
сохранены в таблице C-5. Маскировки `assume`, `arithmetic_overflow`,
`precondition_instance` memcpy и `safety_check` под `should_panic`
не наблюдалось. Контроль А job 78: assertion FAILED `merge.rs:1573`,
reachability SUCCESS; полный счёт 2/2 у обеих гармоник.

R9 кода `e4e24db8` — GO_WITH_NITS (координатор); оба нита учтены в журнале.
Код `merge.rs` после этого SHA не менялся. Итоговая сводка передаётся
координатору отдельной строкой REVIEW REQUEST.

Не измерено в П1: macOS (M-1 у координатора), другие типы и network
(отдельный агент), uninit-чтения, алиасинг, полная reference validity,
перестановка/сортированность/Drop, unwind/CopyOnDrop. Реальные callee,
без `stub_verified`; массивы ровно N, без редукций значений u64.
Отдельное слияние N32 — чётный путь; нечётный хвост покрыт верхними
маршрутами N17/19/21/23/25/27/29/31. П2 не начинался.

**Расход и завершение.**
Dispatch **10/14**, завершённых jobs 10, незавершённых нет.
Сумма wall verify с компиляцией по summary **2198.50 с (36.6417 мин)**,
подготовка CircleCI не включена; фактический API-учёт сверяет координатор.
На 2026-10-26T16:32:43Z от T0 прошло 73.94 мин;
при одном последовательном job это верхняя граница суммы фактических минут
job (<150), включающая также паузы между job и работу с отчётами;
это не точный биллинг. Максимальный RSS run 4513024 KiB,
cgroup peak 5.65 GiB, ENFORCED 13 GiB во всех jobs, OOM 0.
Окно dispatch до 18:48:47Z и отчёта до 19:18:47Z соблюдено.

ВОЛНА 2 П1 ЗАВЕРШЁН

REVIEW REQUEST 3178f164d0e9ccecb0817e2e84d3b11bc67fe487

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(без изменений с `e4e24db8`, R9 GO_WITH_NITS),
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: summary jobs
76/78/79/81/83/84/86/87/90/92 и check-tooling ok каждого против
`9de80e0bec13896bb35a5e04e771448d9fe3931b`; итоговая матрица П1 выше.

### Приоритет 2

T0 П2: 2026-10-26T18:58:21Z (`date -u`).
Окно 6 ч: до **2026-10-27T00:58:21Z**; ≤40 dispatch.

П1 принят координатором: О1-А до 32, C-5 и контроль А засчитаны.
CD-6 прочитан через `git show origin/experiment/kani-k1-base-20261024:…/R6-WAVE2.md`
(решение `eb331360`). База не вливается, check-tooling остаётся
`9de80e0bec13896bb35a5e04e771448d9fe3931b`. Лимит минут снят;
≤180 с — ориентир, основной слой ≤600 с. Более долгие/ресурсные точки
записываются кандидатами расширенного слоя; W2 их в Cloud Build не запускает.

#### П2 — решения R7 и ledger

- **P2-D1.** K-10: u64/u8, N0..16. General — прямой
  `small_sort_general`, stable-Freeze — реальный stable trait, scratch 48.
  В одной GS-гармонике фиксированы тип/N, D/S выбираются независимым bool;
  после свойств два cover маршрутов. u64/u8 через unstable trait выбрали бы
  network, поэтому этот entrypoint не подменяет general (W1-D8).
- **P2-D2.** Сортированность и перестановка по пробе проверяются вместе,
  отдельно от гармоник безопасности П1. Перед сортировкой полный вход
  копируется, `set_probe::<T>()` выбирает одну неизменную произвольную
  байтовую пробу; после сравниваются `k1_count_u` исходного и выходного
  массивов. Это тот же счётчик и та же проба, что в контракте слияния.
  Все значения u64/u8 символические, редукции значений нет.
- **P2-D3.** Comparator — прежний K-1 `lt_u64`/`lt_u8`: строгий слабый
  порядок по ключу `x >> 1`; bit0 остаётся payload. Это сохраняет пары
  разных полных значений с равными ключами, перестановка проверяется по
  полным значениям. Кредит не переносится на произвольный comparator.
- **P2-D4.** Единственный `stub_verified` у GS — `bidirectional_merge`,
  существующая формулировка 1, без правки контракта и runtime.
  `insert_tail`, `sort4_stable`, `sort8_stable` остаются реальными.
  Для каждого типа и каждой реально вызываемой длины слияния 2..16 нужен
  измеренный `proof_for_contract` в том же наборе коммитов. Старые jobs K-1
  сами по себе не засчитываются. Сначала proof N2..4 и R11 на обоих типах,
  затем малые GS/fallback и наращивание. Контроль R11 ожидает FAILED
  `k1_merge_halves_sorted` на массиве `[6,0,2,4]`, память корректна.
- **P2-D5.** Fallback вызывается напрямую, оба типа выбираются независимым
  bool, у каждого normal-return cover после свойств; заглушек нет.
  Если объединённая гармоника не укладывается, типы/маршруты разделяются.
  Measurement 10 мин; если точка остаётся вне лимита, записывается кандидат
  расширенного слоя с job/status/time/memory, работа с другими продолжается.
- **Ledger П2.** Ручных заглушек и `kani::assume(false)` нет. `any_where`
  только в proof N2..4 (len 2..4), каждая длина имеет свой cover, плюс
  cover `bm_len` после вызова с предположенными requires. В contract proofs
  предусловия предполагает инструмент, в GS их проверяет stub (R11).
  В GS/fallback новых assumes нет. Unwind 34, массивы ровно N.
  Контракты, helpers K-1, П1 и lane не меняются.

#### П2 — журнал прогонов

Подготовлен `w2-merge-p2-contract-small-r11-001`: proof u64/u8 N2..4
и R11 u64/u8, 4×10 мин. Expect SUCCESS/SUCCESS/FAILED/FAILED.
Request validate и `git diff --check` — ok; lane diff с `9de80e0b` пуст.
После dispatch П2 **1/40**. Нового proof credit П2 пока нет.

REVIEW REQUEST cd284852e41de2881bf825b1a960c19ac84803e2

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`,
`research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. K-10 П2; первый measurement
проверяет contract prerequisites N2..4 и R11 на обоих типах. Review у координатора.

#### П2 job 110 — proof N2..4 и R11

Head `ceed78d0e80a3dd5dd2bbe36b1799b563be7a574`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 1 (ожидаемые R11 FAILED).
check-tooling ok против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1764512 KiB, cgroup peak 1.88 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 152.13 с.

| Гармоника | expect / actual | Verification Time, с | failed/total | cover |
|---|---|---:|---|---|
| `w2p2_bm_u64_len2to4` | SUCCESS / SUCCESS | 54.87392 | 0/448 | 6/6 |
| `w2p2_bm_u8_len2to4` | SUCCESS / SUCCESS | 49.882053 | 0/441 | 6/6 |
| `w2p2_r11_u64` | FAILED / FAILED | 0.2530806 | 1/465 | 1/1 |
| `w2p2_r11_u8` | FAILED / FAILED | 0.24487017 | 1/458 | 1/1 |

Оба R11: `CopyOnDrop::<T>::k1_merge_halves_sorted(v, &is_less)`
@ `smallsort.rs:780`. Unreachable по строкам: 102/104/121/121.
Proof cover: все три длины и три возврата `bm_len` — 6/6;
R11 cover перед вызовом — 1/1. Полные counts сверены по summary.
Проверка requires в stub для обоих comparator измерена; proof credit
композиции пока не заявлен, R9 П2 ожидается.

Перед job 110 первый вызов dispatch остановился на `git fetch` HTTP 429,
до обращения к CircleCI; job не создан. Повтор после паузы создал job 110.
Учёт П2: CircleCI dispatch **1**, отказ preflight **1**; для потолка 40
считаю консервативно обе попытки. Следующий запрос — попытка **3/40**,
успешный dispatch **2**.

REVIEW REQUEST ceed78d0e80a3dd5dd2bbe36b1799b563be7a574

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `cd284852`), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 110 summary
и check-tooling ok. Далее `w2-merge-p2-gs-len0to1-002`: четыре GS-гармоники
u64/u8 N0/1, expected SUCCESS, по два cover D/S.

#### П2 job 112 — RUNNER_ERROR, сводки нет

Head `756252a3` (запрос `w2-merge-p2-gs-len0to1-002`), CircleCI failed.
`k1.sh summary 112`: `job 112 has no summary artifact: treat as RUNNER_ERROR`.
Verification Time, Kani status, память, cover и gate отсутствуют;
результатам GS N0/1 зачёт не даётся. Причина внутри runner не установлена.
Независимое сравнение lane-файлов с `9de80e0b` прошло, полный check-tooling
не завершён: нет summary.json и связанных хешей.

**P2-D6 (R7).** Повторяю те же четыре GS-гармоники без изменения кода,
новый request `w2-merge-p2-gs-len0to1-retry-003`. Не трактую отсутствие
сводки как FAILED проверки Kani либо ресурсный предел гармоники.
П2 после повтора: CircleCI dispatch **3/40**, preflight отказов 1;
консервативно все попытки **4/40**. Code review `cd284852` ожидается.

#### П2 job 114 — RUNNER_ERROR / checkout HTTP 429

Head `beb5b5a887fb922299b57dca27c6efcffaeadbac`, CircleCI failed;
`summary 114`: нет summary artifact. Сравнение lane с `9de80e0b` ok,
полный check-tooling не завершён (нет summary.json). Kani status/time,
память, covers и gate отсутствуют; GS N0/1 по-прежнему не измерены.

Служебные метаданные CircleCI: job 112 длился 2.064 с, job 114 — 3.710 с.
В metadata job 114 провален `Checkout code`, 2215 мс; ограниченная выборка
ошибок только этого шага: `RPC failed; HTTP 429 curl 22`,
`fatal: expected flush after ref listing`, git clone exit 128.
Это отказ до checkout исходников, не FAILED Kani и не кандидат ресурсного слоя.

**P2-D7 (R7).** После двух быстрых RUNNER_ERROR повтор откладывается
на несколько минут для снятия GitHub rate limit. Диагностика — только
read-only metadata CircleCI и ограниченная выборка ошибок checkout;
логи verifier отсутствуют и не заменяются догадками. Lane/код не меняются.
Следующий запрос `w2-merge-p2-gs-len0to1-retry-004`, те же четыре гармоники.
После него CircleCI dispatch **4**, плюс один preflight отказ;
консервативно попыток **5/40**. Окно до 2026-10-27T00:58:21Z сохраняется.

#### П2 job 115 — GS u64/u8 N0/1

Head `300a94f6d5479a4a0eb2b2f483e636d42f094116`, COMPLETE; gate true,
expectation met true, measurement ok true, Kani exit 0; check-tooling ok
против `9de80e0bec13896bb35a5e04e771448d9fe3931b`.
Run: max RSS 1862888 KiB, cgroup peak 1.98 GiB, ENFORCED 13 GiB,
OOM 0, swap off; wall verify с компиляцией 42.56 с.

| Гармоника | expect / actual | Verification Time, с | failed/total | unreachable | cover |
|---|---|---:|---|---:|---|
| `w2p2_gs_u64_len0` | SUCCESS / SUCCESS | 0.24728438 | 0/642 | 136 | 2/2 |
| `w2p2_gs_u8_len0` | SUCCESS / SUCCESS | 0.24541076 | 0/635 | 136 | 2/2 |
| `w2p2_gs_u64_len1` | SUCCESS / SUCCESS | 0.49166006 | 0/642 | 128 | 2/2 |
| `w2p2_gs_u8_len1` | SUCCESS / SUCCESS | 0.43554628 | 0/635 | 130 | 2/2 |

Полные counts 2/2 D/S сверены по summary отдельно от gate. На N0/1
слияние не вызывается; proof N2..4/R11 job 110 остаются prerequisites для
следующих длин. Сортированность и перестановка измерены; R9 П2 ожидается.

REVIEW REQUEST 300a94f6d5479a4a0eb2b2f483e636d42f094116

Файлы: `library/core/src/slice/sort/shared/smallsort/kani_k1/merge.rs`
(код `cd284852`), `research/challenge-8/kani-k1/RUN-REQUEST.json`,
`research/challenge-8/kani-k1/RESULT-merge.md`. Evidence: job 110/115 summaries
и check-tooling ok. Следующий `w2-merge-p2-f01-gs2-005`: fallback N0/1
(оба типа) и GS N2 u64/u8. После dispatch П2: CircleCI **5**, с preflight
отказом консервативно **6/40** попыток.

#### П2 job 117 — RUNNER_ERROR без summary

Head `e19c46ce` (запрос `w2-merge-p2-f01-gs2-005`), CircleCI failed.
`k1.sh summary 117`: `job 117 has no summary artifact: treat as RUNNER_ERROR`.
Lane-файлы job совпадают с `9de80e0b`; полный check-tooling не завершён:
нет summary.json. Статусы Kani, Verification Time, память, covers и gate
отсутствуют. **Нелокализованный отказ раннера**, причина не установлена;
ни одной из четырёх гармоник результат не приписывается.
По сообщению координатора job завершился в 19:15:49Z, примерно за 2 с;
watch-117.log пустой, waiter не работал. Уведомление не ожидается.

#### Передача на ночь

- Новые dispatch остановлены по указанию координатора. Незавершённых jobs
  нет. П1 принят: О1-А до 32, C-5 и контроль А засчитаны. П2 не завершён.
- П2 закончено измерениями: job 110 — `proof_for_contract` слияния
  формулировки 1 u64/u8 N2..4 SUCCESS, cover 6/6; R11 обоих типов FAILED
  на `k1_merge_halves_sorted` @ `smallsort.rs:780`, cover 1/1.
  Job 115 — GS u64/u8 N0/1 SUCCESS (сортированность + перестановка по пробе),
  cover D/S 2/2. Gate true и check-tooling ok у обоих jobs.
- Следующий шаг K-10 — **GS с длины 2**. Job 117 содержал
  `w2p2_fallback_len0`, `w2p2_fallback_len1`, `w2p2_gs_u64_len2`,
  `w2p2_gs_u8_len2`, все expected SUCCESS. Этот пакет не дал измерений.
  `RUN-REQUEST.json` оставлен точным запросом job 117, а не новым dispatch.
  При возобновлении повторить пакет с новым request_id (например,
  `w2-merge-p2-f01-gs2-retry-006`), commit/push и только затем dispatch.
- Код подготовлен, но не измерен: GS u64/u8 N2..16; fallback u64/u8 N0..16;
  proof слияния каждого типа на N5..16. После повтора — GS N3/4 и fallback
  N2..4, затем наращивание. Для GS N2..4 prerequisites есть в job 110;
  перед зачётом N5+ нужны соответствующие proof длины слияния и всех
  вложенных вызовов (включая N8 у sort8_stable). Stub только merge,
  fallback без stubs, comparator `lt_u64`/`lt_u8` по `x >> 1`.
- Открытые R9: код П2 `cd284852e41de2881bf825b1a960c19ac84803e2`,
  evidence job 110 — `ceed78d0e80a3dd5dd2bbe36b1799b563be7a574`,
  evidence GS N0/1 — `300a94f6d5479a4a0eb2b2f483e636d42f094116`.
  Вердиктов П2 в эту сессию не поступало; независимый зачёт не заявлен.
- П2: 5 CircleCI dispatch (110/112/114/115/117) и 1 отказ preflight HTTP 429;
  консервативно 6/40 попыток. T0 18:58:21Z, исходное окно до 00:58:21Z;
  дальнейшее расписание — по новой ночной очереди владельца. CD-6: минуты
  не ограничены, 180 с ориентир, measurement по 10 мин. Новую базу не вливать,
  check-tooling `9de80e0bec13896bb35a5e04e771448d9fe3931b`, lane не менять.
