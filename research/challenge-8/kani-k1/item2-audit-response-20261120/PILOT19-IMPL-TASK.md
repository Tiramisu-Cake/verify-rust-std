# Кампания 19. Matched-width N13–N19 на OB11

Подготовить один serial пакет из 11 exact roots. Повторить три actual Check для N18/N19, затем P‑3, пять no-merge consumers и два endpoint controls для N13–N17. Во всех строках **11 object bits, local cap 6 GiB**. Для этой стадии закрываем mixed-OB рёбра matched повторами. За основу привязки ролей взять inventory g0 `2547412124` с 30 терминальными корнями и 23 331 свойством. N20 вынесен в кампанию 20. [Native inventory](NATIVE-INVENTORY-N13-N20.md) · [План точечных повторов](INVENTORY-TASK.md)

## Pins и scope

- **Std** — существующий `3fff6aa0dbab95e9889ab864e6b88596c4e452fe` / tree `a41b4c4822ab9df70db698ce576b3112a670ba80` из 17A/17B. При необходимости взять отдельный detached worktree на этом pin. Все нужные selectors и guards уже есть. Пакет использует существующий std commit целиком. Сохранить exact `u8/KeyLess<u8>`, V34, независимые произвольные bytes и q, normal OFF, исходные harnesses, footprints, bodies и covers. [Замороженный std 17](PILOT17-IMPL-HANDOFF.md)
- **Control** — база 17B `628a03ef3d24ad433e977a7e3cfec003c9993292` / tree `26558404aa1e4a58c86ad7d3084230c60123b09b` в `/root/kani-ch8-q-pilot-control-v17b`. Новый кандидат `experiment/ch8-q-pilot-control-v19` с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7`. Дельта ограничена roster/OB, frozen request, соответствующими hashes и test fixtures. Сохранить существующие cfg definitions, workflow, event ref, runner, evidence limits и cleanup. Request `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`.
- **Tool** — `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, CaDiCaL, `--exact --jobs=1 --no-assert-contracts`, unwind36, regular output и export, отдельные target dirs, пустые extra CBMC args. OFF сохраняет обычные memory/bounds/overflow/unwind checks.

## Exact roster

Общий префикс — `slice::sort::shared::smallsort::verify::`. Ordinary stubs пусты. Check выполняют реальные тела с пустыми verified stubs. В B18/B19 исполняются actual `merge_up/down`. У всех positives ожидается native SUCCESS.

| № | Root ID | Exact selector suffix | Cfg / роль и домен | Verified stubs в Proof | Child, с | Covers |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1 | MB-MERGE-N18-OB11 | `sorting_q_merge::mb_merge_n18` | `merge_b`, Check merge, `v[1..19]` → scratch32+0 | ∅ | 600 | 6 |
| 2 | MB-MERGE-N19-OB11 | `sorting_q_merge::mb_merge_n19` | `merge_b`, Check merge, `v[1..20]` → scratch32+0 | ∅ | 600 | 6 |
| 3 | MA-INSERT-RIGHT-OB11 | `sorting_q_merge::ma_insert_right_b10_rel9` | `merge_a`, Check insert, base10/rel9 | ∅ | 600 | 7 |
| 4 | NM-INSERT-P3-OB11 | `sorting_q_pilot::p3_insert_u8_b01_rel1_16_q_any` | `no_merge_sort13`, Check q-only insert, base1/rel1–16 | ∅ | 600 | 24 |
| 5 | NM-NETWORK-N17-OB11 | `sorting_q_merge::nm_network_n17` | `no_merge_sort13`, Proof, `v[1..18]`, rel13–16 | sort13, insert_tail | 450 | 6 |
| 6 | NM-N17-QPOST-CORRUPT-OB11 | `sorting_q_merge::nm_network_n17_corrupt` | `no_merge_sort13`, контроль N17 | sort13, insert_tail | 300 | 2 |
| 7 | NM-NETWORK-N13-OB11 | `sorting_q_merge::nm_network_n13` | `no_merge_sort13`, Proof, `v[1..14]`, без вставок | sort13 | 450 | 6 |
| 8 | NM-N13-QPOST-CORRUPT-OB11 | `sorting_q_merge::nm_network_n13_corrupt` | `no_merge_sort13`, контроль N13 | sort13 | 300 | 2 |
| 9 | NM-NETWORK-N14-OB11 | `sorting_q_merge::nm_network_n14` | `no_merge_sort13`, Proof, `v[1..15]`, rel13 | sort13, insert_tail | 450 | 6 |
| 10 | NM-NETWORK-N15-OB11 | `sorting_q_merge::nm_network_n15` | `no_merge_sort13`, Proof, `v[1..16]`, rel13–14 | sort13, insert_tail | 450 | 6 |
| 11 | NM-NETWORK-N16-OB11 | `sorting_q_merge::nm_network_n16` | `no_merge_sort13`, Proof, `v[1..17]`, rel13–15 | sort13, insert_tail | 450 | 6 |

Назначенные FAILURES — ровно `NM_N17_CORRUPT_QPOST` и `NM_N13_CORRUPT_QPOST` в соответствующих контролях. Сверить native ID/class/location, полезный возврат и путь порчи. P‑3 и N17+control идут первыми в no-merge части, чтобы измерить ёмкость самого длинного пути. Runner исполняет заранее замороженный roster при штатном cleanup и доступном бюджете.

## Cap и критерии результата

- **6 GiB (6 291 456 KiB) у всех новых корней.** На OB12 B18/B19 занимали 4,49/4,70 GiB, MA right insert — 2,08 GiB, consumers N13–N17 — 2,46–4,03 GiB, контроли — 2,59/3,53 GiB. P‑3 был ближе всего к пределу с 5,62 GiB и 451 с child. Смена encoding требует замера. Для всех этих корней прежние результаты поддерживают старт с 6 GiB. Ранний риск P‑3 на OB11 — ёмкость модели из-за символического tail, которую подъём RSS cap не устраняет. При capacity error сохранить причину и рассмотреть отдельно q-only base1/rel13–16 с cover каждого tail, затем exact literal tails при необходимости. Текущий пакет сохраняет существующий P‑3 и std pin. [B18/B19](run-44876372471/SUMMARY.md) · [MA right](run-44872078840/SUMMARY.md) · [17B](run-44896876797/SUMMARY.md)
- **N18/N19.** Связать новые actual Check с существующими `MD-NETWORK-N18-OB11`, `MD-NETWORK-N19-OB11`, N19 q-post control и ACT sort9 из 15. Сверить active clauses на новом Check pin и потребителе. У `merge_b` роли B18/B19 совпадают с вызовом в `merge_c_sort9`. У `merge_a` MA right numeric/q post и inclusive assigns применяются к base10/rel9 также в `merge_c_sort9`. Проверить source diff относительно 11/12b/15 с учётом guards. У B18 scratch[0..18], split 9+9. У B19 scratch[0..19], split 9+10, odd slot 9. Сохранить source/q-frame, numeric/readable/writable/disjoint Pre, actual writes, guard и post. Historic N18 numeric-Pre negative остаётся свидетельством своего OB12 маршрута.
- **N13–N17.** Связать каждый новый consumer и нужный control с соответствующим `NM-S13-L13`…`L17` из 17A на том же pin и OB11. Подтвердить один Replace sort13, сохранность хвоста и все соответствующие preconditions вставок от q-only P‑3. Сопоставить native roles/locations с inventory, отметить отдельно повторные динамические вызовы, если общий ID требует подтверждения их покрытия. Успех нового consumer закрывает width при согласованных dependencies. Ресурс всей цепочки N13–N17 по-прежнему зависит от Check sort13 с историческим пиком 7,35 GiB. [Inventory по рёбрам](NATIVE-INVENTORY-N13-N20.md#mixed-ob-review-и-следующий-минимум) · [Замеры 17A](run-44896810040/SUMMARY.md)
- **Бюджет.** 5 250 с child (4 × 600 + 5 × 450 + 2 × 300), setup/build до 1 800 с, финализация 540 с, job 180 мин. Запас 3 210 с. Latest start за timeout + 30 с до supervisor cutoff. Outer 12 GiB, резерв 2 GiB, штатный effective cap. Capture 16/1/8 MiB на stdout/stderr/export, aggregate 384 MiB. Записывать native inventory, effective cap, sampled child PGID в KiB, outer/component peaks, VT/child, CNF, исходную причину cutoff или `NOT_RUN`. Сохранять capacity/RSS/timeout отдельно от вердикта по свойствам.

## N20. Решение по результату кампании 18

Основной маршрут — `compact_network_n20_actual_insert`. На OB12 он дал SUCCESS при 2,49 GiB и 33,6 с VT. У него actual вставки и ровно два verified stubs, `sort9_optimal` и `bidirectional_merge`. В кампании 20 повторить consumer и новый q-post control на OB11, используя два exact sort9 Check и whole-merge N20 Check из 16. Run 19 `44911175814` сохраняет свой замороженный roster. [Сводка 18](run-44907708573/SUMMARY.md) · [N20 matched](PILOT20-IMPL-TASK.md#n20-matched)

## Локальная проверка и handoff

Сверить exact selectors и cfg на frozen std, старые clauses/inputs, OB11 и таймаут каждой строки. Выполнить `git diff --check`, `validate` с синтетическими metadata, `check-source` и `python3 -m unittest -v test_run.py`. Проверить frozen roster, effective 6 GiB, latest-start windows 630/480/330 с, hash drift и error paths. Подготовить `PILOT19-IMPL-HANDOFF.md` с pins/trees/hashes и результатами проверок. Для офлайн-сверки результатов использовать согласованную structured native projection из задания inventory. Локальные коммиты `[skip ci]`, `Tiramisu-Cake <igkharin@gmail.com>`. Диспатч после review и отдельного GO. [Формат inventory](INVENTORY-TASK.md#формат-и-проверка-полноты)
