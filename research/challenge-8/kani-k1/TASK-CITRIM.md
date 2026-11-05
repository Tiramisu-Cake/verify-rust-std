# CITRIM — убрать корни дольше 200 с без потери покрытия

**Выдано координатором 2026-11-05, решение владельца.** Dispatch только после exact-packet PRE-BUILD review/GO
координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-citrim**, ветка **experiment/kani-k1-citrim-20261105** от **4fa6151b6a**
  (VEIGHTINTEG: library = кандидат v8b, 219 ordinary; тот же набор 204 корней, что в v8a, плюс 15 новых).
- Slug **citrim**, stable owner **k1-merge**. Request_id/stage/ledger `citrim-*`.
- Project cap **$118.96**, свой cap **$3.00**. **До двух сборок** G1/G2, G2 — после разбора G1 и GO координатора.
  Retry нет. Один compile-error repair на сборку, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 300 + closeout 30 мин.

## Цель

Критерий ревью организаторов: контракты и харнессы не должны давать «excessive verification run time». В полном CI
v7 на Actions (тот же pin `cd355b0b`) эти корни шли дольше 200 с хотя бы на одной ОС (verification time, с):

| Корень (`verify::`) | ubuntu | macOS |
|---|---:|---:|
| `merge::general_direct_u64_n9` | 374.0 | 211.6 |
| `merge::stable_direct_u64_n9` | 237.5 | 172.5 |
| `network::dispatch_safety_stable_unstable_bytes16_n15_16_17` | 154.3 | 218.1 |
| `network::dispatch_safety_stable_unstable_bytes16_n32` | 160.1 | 306.1 |
| `network::dispatch_safety_stable_unstable_bytes17_n15_16_17` | 147.7 | 265.5 |
| `network::insert_tail_contract_u64_start1_tail2_to8` | 185.1 | 281.5 |
| `network::insert_tail_contract_u64_start1_tail9_to12` | 174.6 | 227.8 |
| `network::insert_tail_contract_u64_start1_tail13_to14` | 161.7 | 207.4 |
| `network::network_safety_unstable_u64_n30_to32` | 209.5 | 235.5 |

Нужно, чтобы каждый заменяющий корень укладывался с запасом: **цель ≤ 120 с на GCB standard4** (Actions бывают
медленнее GCB до ~2×; точного соотношения у нас нет — в RESULT дать оценку по имеющимся парам GCB/Actions).

## Как

1. **Разбиение с тем же объединением доменов.** Делить корень на части по длинам (`n15_16_17` → отдельные N),
   диапазонам хвоста, маршрутам или ветвям, так что объединение доменов частей **в точности** равно домену исходного
   корня: те же T, компаратор, входы, covers, assertions. Разбиение не должно терять ни одного случая — для каждого
   корня в RESULT таблица «исходный домен = ∪ частей» с обоснованием и статической проверкой (скрипт по аналогии с
   `trimpart/check_trimpart.py`).
2. **Удешевление без изменения смысла** (если разбиения мало): solver-атрибут (`cadical`/`kissat`), сужение
   `unwind` до точного необходимого, если это не меняет домен. Каждое такое изменение обосновать.
3. **Нельзя:** убирать проверки, сужать домен, удалять корни без замены. Если корень не удаётся уложить — оставить
   как есть и записать факт; решение о потере покрытия принимает владелец.
4. Тела прочих ordinary-корней не менять. Контроли не трогать.

## Сборки

- **G1:** все новые части, kind diagnostic, `controls: false`, jobs 1, gcb-e2-standard-4, лимит на корень 5 мин.
  ≤ 25 строк; если частей больше — приоритет по самым медленным корням, остальное в G2.
- **G2:** доработка частей, превысивших 120 с, и/или оставшиеся корни. Плюс `inventory: true` для итогового
  ordinary-набора.

## Коммиты

- Library-коммит (замена корней в `verify/*.rs`) и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не
  опрашивать статус в цикле.

## RESULT

**RESULT-CITRIM.md**, ≤ 45 строк: identities; таблица «исходный корень → части, время каждой части, сумма до/после»;
обоснование равенства доменов; итоговый ordinary-набор (count и delta) и суммарное время до/после; что не удалось.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory. Raw logs, archives, Cloud Logging и
  credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Runtime `smallsort.rs`, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **CITRIM ЗАВЕРШЁН**, одна стадия, затем стоп.
