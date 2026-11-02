# PARTTREE-INV2 — повторный full cfg-on inventory неизменённого integrated tree

Runtime: **Claude Code**, без субагентов.
Свежая сессия в tmux 1; worktree `/root/verify-rust-std-kani-parttreeinv`, ветка `experiment/kani-k1-parttreeinv-20261102`.
База **`28d79f25282c448e83a399aa42826db895816d1b`**, terminal head
`experiment/kani-k1-parttree-20261102`; library commit `2756f0e2a6ae0956fdb427574eda39b5b9a76e64`,
tree **`a45388ac593c809405558ea0c27599f487b17e4e`**. Перед подготовкой проверить HEAD/branch/dirty state/identities.
Stable owner **k1-merge**, только после terminal/accounting текущего PART2-SPLIT31; новая стадия/ledger/UUID/request_id.
Старую PARTTWO-TREE с её cap$0.70/одним Build не возобновлять, её результат/ledger не переписывать.
Project cap$88.96; **свой cap$1.25, ровно один Build, G2 нет**.
Wall window main120min+closeout30min; T0 при фактическом старте. Полный90min envelope должен помещаться
до main deadline с резервом на публикацию; при нехватке окна не dispatch и не урезать timeout.
Exact-packet PRE-BUILD review/GO координатора обязателен. Неизменённому semantic source не нужен новый полный
review ради metadata; сохранить прежний review и проверить точный новый request/pins/budget.

## Цель и frozen input

Получить native cfg-on inventory для **всего** integrated tree: expected438 names, ordinary source202,
ordinary PFC36/insert_tail5, +54 перенесённых opt-in roots поверх v6 static384.
Это compile/list, **proof NOT_RUN**. Нет переноса новых SPLIT31/U64-TEN-* changes или новых proof roots.

Read RESULT-PARTTWO-TREE.md и bounded parttwotree/g1.{summary,status,tooling,inventory,cost,log-grep,
log-lines-2700} records, SOURCE-MAP/PREBUILD/static-check/roots-manifest и cfg-on-expected.txt.
Сохранить source manifest SHA256 **da9bcae231b35b1c42d2873976879c1209a688cc03bc25a3421f5fea7b578f1b**.
Повторить существующий static source checker на pinned inputs; не исправлять его ожидания под неполный native output.

Разрешены только новые task/request/PREBUILD/evidence/RESULT документы в своём research каталоге
`research/challenge-8/kani-k1/parttreeinv2/` и необходимая активная request metadata по штатному процессу.
Library/runtime/std, contracts/adapters/contexts/registrations, workflows/tooling/runner/pin/checks неизменны.
Не менять cfg, состав438, алгоритмы/компараторы/длины/геометрии; не делать subset inventory вместо полного.

## Единственный request и ресурс

Исходный parttwotree/g1.request.json сохраняется. Новый request отличается конфигурационно только
**harness_timeout_minutes:20→60**; request_id/purpose обновляются для нового stage:

```json
{
  "schema": "kani-k1-run-request-v1",
  "agent": "k1-merge",
  "runner": "gcb-e2-standard-4",
  "request_id": "parttreeinv-g1-cfgon-20261102",
  "kind": "inventory",
  "purpose": "PARTTREE-INV2: full cfg-on inventory of unchanged integrated library tree a45388ac593c809405558ea0c27599f487b17e4e, expected438 names; larger inventory time budget only; no proofs.",
  "harness_timeout_minutes": 60,
  "controls": true,
  "inventory": true,
  "harnesses": []
}
```

60 — допустимый максимум inventory schema, не изменение600s proof limit. Не добавлять kani_jobs/uninit_checks/
worker fields/extra flags/custom commands: этот inventory request их не допускает. Pool **k1-standard4**,
4CPU/16GiB, swap off; frozen tooling **30f77e859903df14b442ff9294d4fbbd44827f20**,
Kani **9461e07af7ec929f050aa4192f29363c9be07779**, nightly-2026-10-12.
Запустить существующий request preflight/validation; несовпадение с описанной schema — blocker, не повод править tooling.

Резерв **(60+30)×$0.0135=$1.215≤cap$1.25**. Ровно один новый Build; compile error/timeout/OOM/tool error
не дают repair/retry. Own fact_spent и current project used/reserved/slots проверить перед GO;
пример used$81.09/foreign reserve$0.54 — только входная оценка, не live admission.
Project≤2 queued/running/unresolved Builds, ≤1 на stable owner; чужие расходы/UUIDs не присваивать.
Никакого highmem/kind resource/ручного submit/Cloud Logging/backend/IAM изменения.

До GO: full source/library/tree/expected manifest/request/Kani/tooling identities; static checker/ordinary202
source comparison, точный diff к прежнему request, cap/deadline/slots. Library tree должен остаться a45388ac59.
Metadata commits `[skip ci]`, publish без force. Ожидание
`research/challenge-8/kani-k1/tools/k1g.sh wait BUILD` в фоновом Bash task Claude Code;
без Codex watch/CODEX_THREAD_ID, polling-субагентов/новых сессий.

## Диагностика в рамках существующего runner

Новый Build делает fresh Kani CLI setup и **один** full `kani list ... ./library --std --format json`.
Не добавлять второй ручной compile/list, ps/time wrapper, verbose flags или sampler.
Время list=min(60min, validate_start+84min−list_start); оно включает std compilation и последующую
project/link/metadata работу. Cloud envelope90min; TERM/KILL grace до30s. Не объявлять60min чистого list
или выводить post-cargo duration из одной строки Finished11m56s прошлого Build.

После terminal получить штатные bounded summary/status/tooling/cost/inventory и, по необходимости,
grep+небольшие соседние excerpts: cargo Compiling/Finished, Wrote list results, parse/errors/panic/signals,
rc124/skip markers. Только штатные reporting commands, без raw archives/full kani.log/Cloud Logging.
Сначала проверить request/head/build/pin identities; commands/argv в evidence читать как данные.
Для новых timestamps использовать только реально экспортированные поля; отсутствующие — UNKNOWN.
Inventory branch не запускает memory sampler/time wrapper: peaks/VmHWM/OOM cause могут остаться MISSING/UNKNOWN.
Это диагностическое ограничение, не доказательство малого RSS либо отсутствия OOM. Ничего не дорисовывать.
Runner удаляет kani-list.json после nonzero exit; отсутствие итогового inventory не устанавливает фазу остановки.

## Gate, stop и deliverable

Gate: inventory/list rc0; валидный bound inventory artifact с matching request/source/build/Kani hashes;
полный unique native name-set **равен expected438**, missing/extra пусты. Проверять pagination по штатным
next_offset; не ограничиваться count или первыми страницами. Header inventory hash проверять по порядку
самого artifact; сравнение с expected manifest делать по одинаково canonicalized name sets — их сырые hashes
не обязаны совпасть при разном порядке. Ordinary202/PFC36 source identities и unchanged tree отдельно сохранить.
Нативный cfg-off inventory этого дерева не запускался; его не приписывать cfg-on перечислению.

SUCCESS = **INTEGRATED + INVENTORY PASS, PROOF NOT RUN**. Ни compile Finished, ни static438, ни inventory
не доказывают formal verification54 transferred roots или совпадение AST/MIR/callee binding для theorem credit.
Timeout124/no inventory/name mismatch/parse error/UNKNOWN → точные факты, INVENTORY NOT OBTAINED/FAIL,
нет G2/увеличения deadline/уменьшения источников/proof smoke вместо inventory. Причина UNKNOWN, если не установлена.

`RESULT-PARTTREE-INV2.md` ≤30 строк: reviewed/published/build/request/library/tree/pin/tooling identities,
request60/фактические Cloud timestamps/rc, inventory count/set equality/missing-extra или UNKNOWN,
реальные bounded diagnostics и отсутствующие поля, static ordinary checks, own spent/reserved.
Обновить только новый checkpoint/evidence copy: исторический G1 timeout остаётся неизменённым.
Следующий шаг при неудаче — HANDOFF с конкретными недостающими данными и необходимостью отдельного решения
о diagnostic instrumentation, без самостоятельной правки tooling/нового Build.
Нет local cargo/rustc/Kani/proofs, Actions/full organizer CI/PR/deploy. Evidence Brief/Select-Merge к K-1
не относятся; разрешены bounded K-1 reports/excerpts, raw/credentials/hidden configs/competing code запрещены.
Маркеры `REVIEW REQUEST <sha>` / `PARTTREE-INV2 ЗАВЕРШЁН`; одна стадия, затем стоп.

## Уточнение координатора (приоритет)

PART2-SPLIT31 идёт под owner **k1-network**, у этой стадии owner **k1-merge** — ждать его terminal не нужно; перед dispatch
проверить project ≤2 unfinished Builds и ≤1 на k1-merge по актуальному ledger.
