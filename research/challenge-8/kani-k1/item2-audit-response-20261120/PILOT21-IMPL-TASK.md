# Кампания 21. Остальные wide network roots с actual вставками

Подготовить два serial пакета при **6 GiB, OB11** для N21–N23, N26, N28–N32. Отдельный пакет right sort13 Check при **8 GiB, OB11** готовится локально и ждёт явного решения владельца по этим геометриям. В 20 actual inserts дали SUCCESS у N20/N24/N25/N27 при 2,5–3,0 GiB. У N27 правый Check sort13 остановился при 6 GiB после CNF 25,5 млн clauses. N27 consumer и merge из 20 переиспользуются, его right Check и точный контроль добавляются ниже. [Итоги 20](run-44913550779/SUMMARY.md) · [Матрица wide](MERGE-WIDE-PLAN.md)

## Scope и формы корней

Std-база `bfa60b19ccdca4d0a872df1a3ef1d6f640dac3e0` / tree `3cc0e5aa1a8d5100c2812bef424291af5f630`, worktree `/root/verify-rust-std-ch8-q-pilot-v1`. Один локальный commit с добавлениями только в `verify/sorting_q_merge.rs`. Сохранить runtime, модели, active clauses, старые roots и их expected labels. Переиспользовать compact harness и helpers Check из 20. [База и формы 20](PILOT20-IMPL-HANDOFF.md)

- Все корни `merge_wide`, `u8/KeyLess<u8>`, OB11, normal OFF. У positives initialized V34, произвольные байты и независимый произвольный q. У Check actual тело и пустые stubs. Presort пишет только первые 9/13 байтов exact аргумента, сохраняет хвост, V34 outside frame и q, проверяет numeric order и count ниже того же q. Семь covers. У whole merge literal `v[1..1+N]`, input split после `floor(N/2)`, disjoint `MaybeUninit<[u8;32]>` с dst+0. Actual up/down и guard, source-only old, active assigns, full writes, q/post и source frame. Шесть covers, у существующего N32 восемь, включая маску 0 и `u32::MAX`.
- У каждого consumer real `small_sort_network`, actual insertion loop и copy-back. Полный набор verified stubs у N21–N23 — `sort9_optimal, bidirectional_merge`, у N26, N28–N32 — `sort13_optimal, bidirectional_merge`. Actual `insert_tail` проверяется обычными memory/bounds/overflow/unwind. Native merge geometry/numeric Pre проверяются на состоянии после вставок. Сохранить исходный q/order-stat на всём активном срезе, q-frame, каждый внешний байт V34 и шесть covers. N32 использует wide oracle с u64 intermediate и u32 output, buffer полностью занят 32 байтами.
- Каждому указанному контролю дать тот же exact span и stub set, что у его positive. Литеральный активный вход из нулей, q=1, произвольные внешние байты. После actual network покрыть полезный возврат `v[1] == 0`, записать `v[1]=255`, покрыть порчу и проверить q/frame. Ожидать единственную `COMPACT_N{N}_ACT_INSERT_CORRUPT_QPOST` с covers `COMPACT_N{N}_ACT_INSERT_CORRUPT_USEFUL_RETURN` и `COMPACT_N{N}_ACT_INSERT_CORRUPT_PATH`. У N24 stubs sort9/merge, у N27 sort13/merge, positives уже в 20. Ordinary stubs пусты у всех корней. [Шаблон контролей](PILOT20-IMPL-HANDOFF.md#exact-геометрии-и-роли) · [Grouped-property правило](GROUPED-PROPERTY-DECISION.md#правило-допуска)

## Exact маршруты и зависимости

В таблице пары — `(backing base, аргумент len)`. Активный срез consumer `v[1..1+N]`. Для каждого N нужен Check whole merge этой же длины. При odd N slot `floor(N/2)` записывается actual odd copy. Выражения tail относительны к своей базе.

| N | Presort L / R | Actual tails L / R | Особенность |
| ---: | --- | --- | --- |
| 21 | sort9 (1,10) / (11,11) | 9 / 9–10 | odd slot10, left Check из 16 |
| 22 | sort9 (1,11) / (12,11) | 9–10 / 9–10 | even |
| 23 | sort9 (1,11) / (12,12) | 9–10 / 9–11 | odd slot11 |
| 26 | sort13 (1,13) / (14,13) | ∅ / ∅ | оба actual loop пусты |
| 28 | sort13 (1,14) / (15,14) | 13 / 13 | even |
| 29 | sort13 (1,14) / (15,15) | 13 / 13–14 | odd slot14 |
| 30 | sort13 (1,15) / (16,15) | 13–14 / 13–14 | even |
| 31 | sort13 (1,15) / (16,16) | 13–14 / 13–15 | odd slot15 |
| 32 | sort13 (1,16) / (17,16) | 13–15 / 13–15 | even, scratch целиком |

Левый Check sort9 N21 — `MW-S9-L10` из 16. Для верхней группы проверить четыре left Check 17A и семь right из блока 21C. Пока конкретный Check открыт, native SUCCESS соответствующего consumer остаётся условным. Старый N32 whole merge Check прошёл на OB11 за 482 с при **6,04 GiB**. Его exact повтор при 6 GiB — измерение fit. Cutoff оставляет ресурсный вопрос N32 открытым и сохраняет прежний функциональный результат в его профиле. [Check 16](run-44890498157/SUMMARY.md) · [Check 17A](run-44896810040/SUMMARY.md)

## 21A. N21–N23 и контрольные привязки N24/N27, 6 GiB

Exact selector prefix `slice::sort::shared::smallsort::verify::sorting_q_merge::`. В колонке основания для controls совпадают geometry, cfg, width и stubs с указанным positive.

| Root ID | Selector suffix | Роль | Child, с |
| --- | --- | --- | ---: |
| MW-S9-L-B01-L11-OB11 | `mw_sort9_left_b01_len11` | Check sort9, `v[1..12]`, writes `v[1..10]` | 600 |
| MW-S9-R-B11-L11-OB11 | `mw_sort9_right_b11_len11` | Check sort9, `v[11..22]`, writes `v[11..20]` | 600 |
| MW-S9-R-B12-L11-OB11 | `mw_sort9_right_b12_len11` | Check sort9, `v[12..23]`, writes `v[12..21]` | 600 |
| MW-S9-R-B12-L12-OB11 | `mw_sort9_right_b12_len12` | Check sort9, `v[12..24]`, writes `v[12..21]` | 600 |
| MW-MERGE-N21-OB11 | `mw_merge_n21` | Check merge N21 | 600 |
| MW-MERGE-N22-OB11 | `mw_merge_n22` | Check merge N22 | 600 |
| MW-MERGE-N23-OB11 | `mw_merge_n23` | Check merge N23 | 600 |
| COMPACT-N21-ACT-INSERT-OB11 | `compact_network_n21_actual_insert` | Proof N21 | 450 |
| COMPACT-N21-ACT-INSERT-CORRUPT-OB11 | `compact_network_n21_actual_insert_corrupt` | Control N21 | 300 |
| COMPACT-N22-ACT-INSERT-OB11 | `compact_network_n22_actual_insert` | Proof N22 | 450 |
| COMPACT-N22-ACT-INSERT-CORRUPT-OB11 | `compact_network_n22_actual_insert_corrupt` | Control N22 | 300 |
| COMPACT-N23-ACT-INSERT-OB11 | `compact_network_n23_actual_insert` | Proof N23 | 450 |
| COMPACT-N23-ACT-INSERT-CORRUPT-OB11 | `compact_network_n23_actual_insert_corrupt` | Control N23 | 300 |
| COMPACT-N24-ACT-INSERT-CORRUPT-OB11 | `compact_network_n24_actual_insert_corrupt` | Control к N24 из 20 | 300 |
| COMPACT-N27-ACT-INSERT-CORRUPT-OB11 | `compact_network_n27_actual_insert_corrupt` | Control к N27 из 20 | 300 |

15 roots, **7 050 с child**, остаток до job cutoff после setup/finalization **1 410 с**. N27 control — проверка чувствительности. Его whole-chain qualification ждёт правый Check R14. N24 control нужен для собственной контрольной привязки, оставленной в handoff 20. [Qualification N20/N24/N25](PILOT21-QUALIFICATION-TASK.md)

## 21B. N26, N28–N32, 6 GiB

Порядок selector groups — N26, N28, N29, N30, N31, N32. Для каждого N три exact строки подряд.

| Root ID | Selector suffix | Роль | Child, с |
| --- | --- | --- | ---: |
| `MW-MERGE-N{N}-OB11` | `mw_merge_n{N}` | Check merge, у N32 существующий exact selector и ресурсный повтор | 600 |
| `COMPACT-N{N}-ACT-INSERT-OB11` | `compact_network_n{N}_actual_insert` | Proof, sort13/merge | 450 |
| `COMPACT-N{N}-ACT-INSERT-CORRUPT-OB11` | `compact_network_n{N}_actual_insert_corrupt` | Control с теми же stubs | 300 |

18 roots, **8 100 с child**, остаток **360 с**. Для этого пакета aggregate artifact cap **512 MiB**. 18 × 25 MiB дают до 450 MiB members плюс индекс. Per-root caps остаются прежними. Для N26 зафиксировать два входа в `insertion_sort_shift_left` с offset13 и ноль вызовов `insert_tail`. Результаты consumers/control до закрытия sort13 остаются диагностикой без допуска.

## 21C. Right sort13, 8 GiB только после решения владельца

Семь exact Check в `merge_wide`, OB11, actual 45 swaps, один thin footprint первых 13, прежние native roles, frame и семь covers. Пакет serial, jobs=1. Полоса 8 GiB применяется только после явной записи решения для этих root IDs и отдельного GO. Текущее решение по пяти корням 17A относится к прежним exact roots. Для уже измеренного `MW-S13-R13` (base13/len13, N25, 7,32 GiB) в решении владельца нужна отдельная применимость к этому root. Повтор R13 изначально не входит в roster 21C. [Действующий узкий допуск](OWNER-DECISION-SORT13-8GIB.md) · [R14 при 6 GiB](run-44913550779/SUMMARY.md)

| Root ID | Exact selector suffix | Вход / writes | Consumer |
| --- | --- | --- | --- |
| MW-S13-R-B14-L13-OB11 | `mw_sort13_right_b14_len13` | `v[14..27]` / `v[14..27]` | N26 |
| MW-S13-R-B14-L14-OB11 | `mw_sort13_right_b14_len14` | `v[14..28]` / `v[14..27]` | N27, точный повтор cutoff |
| MW-S13-R-B15-L14-OB11 | `mw_sort13_right_b15_len14` | `v[15..29]` / `v[15..28]` | N28 |
| MW-S13-R-B15-L15-OB11 | `mw_sort13_right_b15_len15` | `v[15..30]` / `v[15..28]` | N29 |
| MW-S13-R-B16-L15-OB11 | `mw_sort13_right_b16_len15` | `v[16..31]` / `v[16..29]` | N30 |
| MW-S13-R-B16-L16-OB11 | `mw_sort13_right_b16_len16` | `v[16..32]` / `v[16..29]` | N31 |
| MW-S13-R-B17-L16-OB11 | `mw_sort13_right_b17_len16` | `v[17..33]` / `v[17..30]` | N32 |

По **1 100 с child**, всего **7 700 с**, остаток **760 с** после setup/finalization. Измеренный Check R13 занял 875 с child, это ориентир для начального окна. При timeout или cap сохранить фазу и оставшийся exact provider; изменение бюджета требует следующего измерительного решения.

**Left 17A.** Сверить `NM-S13-L13` для N26/N27, L14 для N28/N29, L15 для N30/N31 и L16 для N32: base1, длины 13–16, входы `v[1..14]`…`v[1..17]`, writes `v[1..14]`. Обе стороны OB11. Сверить reachable тела, активные `presort_geometry`, thin modifies, тот же `old`/numeric/q post и exact guards. В обоих профилях `kani_smallsort_q_compact_presort13` выключен. Разрешение len17 в `no_merge_sort13` сохраняет предикат на 13–16. Q-only insert clause действует на другом callee, а wide inserts идут в Original. Сверить native Check и caller geometry Pre. При принятой сверке использовать существующие exact левые Check и их ресурсную запись. При открытом переносе выписать конкретную геометрию для отдельного matched Check и решения о её полосе. [Левые Check](run-44896810040/SUMMARY.md) · [Scope решения владельца](OWNER-DECISION-SORT13-8GIB.md)

## Control, budget и handoff

- Основа v20 `0b4ba53bc4dac8be2fae81916db9ad0a332713a0` / tree `aba7ec3689b53644c105a138283f2efd7db4fcb6`, worktree `/root/kani-ch8-q-pilot-control-v20`. Три frozen control кандидата `experiment/ch8-q-pilot-control-v21a`, `…-v21b`, `…-v21c`, каждый с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Один std pin. Сохранить workflow/event ref, `merge_wide`, cleanup и bounded runner. Request `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`.
- Tool `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`. CaDiCaL, `--exact --jobs=1 --no-assert-contracts`, OB11, unwind36, OFF, regular + export, без extra CBMC args, отдельные target dirs. Local 6/6/8 GiB на job, outer 12 GiB, reserve 2 GiB. Job 10 800 с, setup/build до 1 800 с, финализация 540 с, child allowance 8 460 с. Latest start за timeout + 30 с до supervisor cutoff. Capture 16/1/8 MiB, aggregate 384/512/384 MiB. Фиксировать capacity/CNF/solve, effective cap, sampled child PGID, outer/component RSS, VT/child, terminal inventory либо первопричину cutoff.
- Сверить source/cfg, точные срезы, stubs и labels обоих маршрутов, всю матрицу зависимостей. Выполнить rustfmt check-only, `git diff --check`, `validate` с synthetic metadata, `check-source` и `python3 -m unittest -v test_run.py` для всех пакетов. Проверить order/width/cap, bounds evidence и бюджеты, latest-start окна 630/480/330/1 130 с и error paths. Handoff `PILOT21-IMPL-HANDOFF.md` с pins/trees/hashes, frozen roster, зависимостями и проверками. Коммиты `[skip ci]`, `Tiramisu-Cake <igkharin@gmail.com>`. Диспатч после review и отдельного GO, для 21C также после решения владельца.
