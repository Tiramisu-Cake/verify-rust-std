# Worker14 — S1/R8: исторический CI baseline и coverage inventory

2026-11-16. Задание: прямое поручение владельца этой сессии; роль14 из
[roadmap](../../../ROADMAP-CH8-ITEMS1-2-FOUR-WORKERS.md), §6 и R8;
[план](../../../PLAN-CH8-ITEM2-SORTING-v2.md), §9. Корректность, не security.
Research-only, **0 dispatch, 0 local builds, 0 push**. Runtime/CI/model files не изменены.
Текущий пакет готов для передачи; **R8 ещё UNKNOWN**, новых S-измерений нет.

## Identities и границы evidence

- [PR model-checking/verify-rust-std#752](https://github.com/model-checking/verify-rust-std/pull/752),
  API-confirmed head **`872d5a43380752786415bc00d2a12ce0e930cb37`**.
- [Fork run42363378063](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/42363378063),
  `workflow_dispatch`, attempt1, head совпадает, 16/16 jobs `success`.
  Это существующий fork run, не upstream PR check и не запуск worker14.
- Старый Kani **`cd355b0bccd32300713bc2ce4f765dafa1510607`** из pinned `tool_config/kani-version.toml`.
  Будущий S pin **`0aac16ef62da9e9d5645782d458593e5d78143ba`** — другая identity.
- Источник per-root VT: [опубликованный TSV](https://github.com/Tiramisu-Cake/verify-rust-std/blob/e63e7fadfdc8a9e4871f872fdf022092cbb7387e/research/challenge-8/kani-k1/v10cci/v10-autoharness-smallsort.tsv)
  и [его описание](https://github.com/Tiramisu-Cake/verify-rust-std/blob/e63e7fadfdc8a9e4871f872fdf022092cbb7387e/research/challenge-8/kani-k1/v10cci/README.md).
  Это **source-reported** extraction старых autoharness logs, не новая независимая перепроверка verdicts/covers.
  Получен через `gh api contents`, байты совпали с pinned Git blob; `published-timings-source.json` хранит blob SHA.
- Job/step metadata получены через `gh api .../actions/runs/.../jobs?per_page=100`,
  total16, без пагинации. Снимок — `api-summary.json`.
- Membership/runner image уточнены только явными диапазонами `gh api .../actions/jobs/ID/logs`
  с `Range`, **HTTP206**, проверкой Content-Range/размера. Запрос≤65536байт;
  сохранялись выбранные строки и range SHA256, **не raw logs**. Индекс — `samples/*.json`.
  Никаких artifacts, архивов, Cloud/GCS или полного log download.
- Check-run API `output.summary/text` для Kani List и partition checks равны null;
  попытка не дала нужного inventory. Job summary из GitHub UI не подменён ими.

## Baseline по каждому root и памяти

Полные235 строк — [baseline-roots.tsv](baseline-roots.tsv); исходные covers/status/time —
[published-timings.tsv](published-timings.tsv). VT — поле Kani `Verification Time`, **не elapsed root/runner**.

| Метрика | Ubuntu | macOS |
|---|---:|---:|
| SmallSort ordinary roots, source-reported SUCCESSFUL | 235 | 235 |
| Sum VT, unrounded seconds | 7801.879658047 | 10534.459671914 |
| Manual VT total внутри autoharness job, округлённый source report | 11833 | 14978 |
| SmallSort share, source report | 65.9% | 70.3% |
| Max VT | 246.12196 | 340.47784 |
| Max root | `merge::stable_direct_u64_n9` | `merge::general_direct_u64_n9` |
| Per-root aggregate driver+backend RSS | **UNKNOWN** | **UNKNOWN** |
| Per-root full wall / phase wall | **UNKNOWN** | **UNKNOWN** |
| Concurrent aggregate RSS / whole-job peak | **UNKNOWN** | **UNKNOWN** |
| Autoharness verification step elapsed | 5907s | 7353s |
| Autoharness job elapsed, including setup | 6047s | 7373s |

В этом TSV нет поля памяти. Pinned `run-kani.sh` не измеряет per-root/process-tree RSS;
REST job metadata также не даёт память. Воспроизводимый baseline памяти ретроспективно
не установлен. Успешный run, RAM раннера, VT, другие Cloud-запуски и сумма отдельных
несинхронных process peaks **не являются** измерением root aggregate RSS.
Пустые RSS/wall ячейки TSV означают UNKNOWN, не0. Для R8 их надо измерить в matched arms.
978/978 covers и zero failed checks/OS — опубликованные claims, не independent proof credit.
B1/B2 credit этим пакетом не устанавливается; `download_verified` не менялся.

## Шарды

[baseline-shards.json](baseline-shards.json): actual job/step elapsed и отдельная
**проекция** autoharness VT на тот же набор имён. Последняя не измеряет VT partition job.

| OS | Partition | Все roots | SmallSort | Job elapsed | Verification step elapsed | SmallSort VT projection |
|---|---:|---:|---:|---:|---:|---:|
| Ubuntu | 1 | 494 | 0 | 2429s | 2302s | 0 |
| Ubuntu | 2 | 494 | 183 | 4357s | 4230s | 5431.255439s |
| Ubuntu | 3 | 494 | 0 | 1941s | 1895s | 0 |
| Ubuntu | **4** | 494 | 52 | **4565s** | **4525s** | 2370.624220s |
| macOS | 1 | 494 | 0 | 2126s | 2113s | 0 |
| macOS | 2 | 494 | 183 | 3822s | 3805s | 7561.482943s |
| macOS | 3 | 494 | 0 | 1680s | 1668s | 0 |
| macOS | **4** | 492 | 52 | **4196s** | **4178s** | 2972.976729s |

Худший elapsed shard — **№4 на обеих ОС**: Ubuntu76м05с, macOS69м56с с setup.
Наибольшая SmallSort VT projection — №2. Из этих фактов не выводится, что SmallSort
причинил задержку№4: там присутствуют другие roots и setup/compilation.
Полный workflow elapsed `created_at→updated_at` — 9250s; включает List/Metrics/Analyzer/Build JSON,
это не SmallSort-only cost. Сумма8 partition job elapsed — 25116 runner-seconds.

Проверка membership: обе ОС дают disjoint множества **183 standard +52 contract =235**,
равные TSV; списки — `shard-{ubuntu,macos}-{2,4}-roots.txt`. Это не произвольное
лексикографическое деление235 имён. Pinned script объединяет
`standard-harnesses` **затем** `contract-harnesses` всего std inventory, в порядке JSON;
`chunk=ceil(total/4)=494`, slices `[0,494)`, `[494,988)`, `[988,1482)`, `[1482,total)`.
Выборки подтверждают total1976 Ubuntu /1974 macOS, starts494/1482 для shards2/4.
Нулевые SmallSort counts shards1/3 следуют из disjoint slicing и уже полного235 union;
их полные логи/manifest не читались. Причина разницы2 в общем inventory не исследовалась.

## Jobs и runner limits

Источники: pinned [workflow](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/.github/workflows/kani.yml),
[script](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/scripts/run-kani.sh),
[официальные public runner specs](https://github.com/github/docs/blob/main/data/reusables/actions/supported-github-runners.md).
Снимок identities/двух строк specs — `runner-specs.json`; specs текущие, не historical measured capacity.

| Mode | Ubuntu | macOS |
|---|---|---|
| Sampled runner image | ubuntu-24.04,20261101.360.1 | macos-26-arm64,20261102.0473.1 |
| Documented public resources | 4 CPU,16 GB RAM,x64 | 3 CPU(M1),7 GB RAM,arm64 |
| Partition `KANI_JOBS` | `2` → `--jobs=2` | empty → `-j`, thread-pool default |
| Measured effective partition concurrency | не измерена | не измерена; не объявлять jobs2/3 по CPU count |
| Autoharness | **`--jobs=3 --harness-timeout 10m --default-unwind 1000 --output-format=terse`**, обе ОС | тот же explicit argv |

Важное различие: published235 timings относятся к **jobs3 autoharness**, а не jobs2 partition.
`KANI_JOBS` script применяет в subset path; не управляет explicit autoharness `--jobs=3`.
Partition path не задаёт `--harness-timeout`; 600s из autoharness не переносить на него.
В workflow нет собственного `timeout-minutes`/root RSS limiter. Указанные GitHub GB
сохраняются как GB; проектная jobs2/16GiB квалификация должна записать фактический
MemTotal/cgroup limit в bytes, а не молча приравнять единицы. macOS7GB не удовлетворяет
предпосылке «две задачи по6GiB на16GiB»; её actual parallelism/RSS нужно квалифицировать отдельно.
Остальные общие organizer flags: `--no-assert-contracts`, function-contracts/mem-predicates/
float-lib/c-ffi/loop-contracts/quantifiers/stubbing, CBMC `--object-bits 12`; extra-UB OFF.

## Coverage и R8 handoff

[Coverage table](COVERAGE.md), [replace-map235](replace-map.tsv),
[формат будущего cost report](COST-REPORT-FORMAT.md), [JSON template](cost-report.template.json).
Никакие roots пока не сняты; ни один future theorem не имеет proof credit.
Рабочие gates: matched total VT не хуже baseline на одном новом pin,≤600s/root,
цель single-root aggregate≤6GiB, затем **measured jobs2 fit16GiB**, critical shard/full elapsed
и обе платформы. Параметры настоящего dispatch, budget и GO остаются у координатора.
Новый пункт2 budget≤14 не автоматически добавляется к старым18; эта сессия потратила0.

Known gaps: historical RSS/root wall/phase split отсутствуют; actual partition SmallSort VT отсутствует;
S3/S4 theorem/root identities ещё не выданы; matched S5 baseline/new ещё не запущены.
Это ограничения R8 evidence, не повод получать raw logs или запускать CI в этой сессии.
