# G1 minimal: штатный frontend, actual insert_tail

2026-10-12. **PREPARATION ONLY / NOT_RUN; Cloud budget/charge 0/0; Build/token NONE.**
Собственный worktree `/root/verify-rust-std-refinedrust-feasibility-20261011`,
ветка `research/refinedrust-feasibility-20261011`, исходный HEAD
`c48bf37c34bd0c68c5d934ec3a898e29b48af0ff`. Этот план заменяет обязательные
parser/correspondence gates первого G1 в прежних execution/readiness документах.
Старый пакет и результаты synthetic tests сохраняются как история.

## Минимальный эксперимент

Гипотеза: unpatched RR может обработать actual generic `insert_tail` и показать
первый реальный admission/resource blocker без собственного Radium parser.
Потребитель — actual `insertion_sort_shift_left`; G1 проверяет только frontend,
не безопасность helper и не применимость к slice caller.

Использовать disposable Cloud checkout **точного core**, без переписывания
SmallSort, signatures, runtime wrappers или подмены их sysroot-версиями.
`cargo refinedrust` работает на уровне crate: `-p core` не означает выбор одного
тела. Поэтому отказ на постороннем core item сохраняется как INCONCLUSIVE для
insert_tail, а не объявляется невозможностью его проверки. Изолированный
переписанный helper с sysroot ManuallyDrop не служит exact-source positive.

Ghost delta: регистрация `rr` в crate и `#[rr::verify]` на insert_tail и actual
CopyOnDrop::drop; только требуемые штатным frontend ADT/function annotations на
ManuallyDrop/MaybeDangling/new/Deref/as_ref и реально достигнутых callees.
Не переносить автоматически весь annotations.json, unit refinements или
`may_unwind_if(True)` как ресурсный контракт. Недостающие annotations/specs
фиксировать по диагностике; assumed `only_spec`, новые shims, stronger FnMut,
Copy/Freeze/purity и новые trusted semantics не разрешены. Перед запуском freeze
точного annotation diff и equality после удаления только добавленного ghost.

Будущая последовательность — version/hash preflight, отдельный маленький
`#[rr::verify] fn ...() {}` control, затем **один** target invocation штатного
workflow (форма команды, сейчас не исполнять):

```text
RR_CONFIG=/workspace/RefinedRust.toml cargo refinedrust -- \
  --manifest-path /workspace/source/library/Cargo.toml -p core \
  --locked --offline --target x86_64-unknown-linux-gnu
```

Toolchain явно выбрать nightly-2026-08-28; записать bootstrap capability,
Cargo config/lock/dependency closure и `-Cpanic=unwind -Coverflow-checks=on`.
Config: `run_check=false`, debug/MIR/borrowck dumps и linking requirements on,
`skip_unsupported_features=false`, `register_all_adts=false`, conservative panic;
никаких proof admits/trust_debug/скрытого post-generation hook. Не навязывать
`find_stdlib=false/lib_load_paths=[]` как prerequisite: использовать официальный
механизм pinned stdlib exports, перечислить реально загруженные `.rrlib` и
shim/spec boundaries; их наличие не доказывает actual callee. Если нужного
binding нет — сохранить LIBRARY-SPEC gap. Compiler-only `cargo check` нужен
лишь для отделения неоднозначного compiler/frontend отказа, в рамках той же
будущей разрешённой lane/ceiling; не обязательная отдельная сборка всего std.

## Identities, evidence и вывод

Source `c7ca8c467aecf10a4b53039372ee97714f854ee3`; SmallSort blob
`e555fce440872898e47fd5114f32eb15401d07df`, SHA256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`
(повторно проверен чтением Git object). Tool
`332d945fafa14bf55c0c8390cb35ec4b0c012cff`; compiler
`e457a7b0d326d67b4322ef0d11bd715cfaeda48f`, host x86_64-unknown-linux-gnu.
Полная source/tree/callee/tool/lock/component identity — [g1/inputs.json](g1/inputs.json).
Его старые dispatch/max_active поля **не являются текущим разрешением**.

Официальные источники: [pinned README](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/README.md),
[cargo wrapper](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/refinedrust_frontend/src/bin/cargo-refinedrust.rs),
[config](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/rrconfig/src/lib.rs).
Сегодня web blob недоступен, два raw fetch завершились timeout 20 s, Git remote
не ответил и был остановлен. Workflow выводы опираются на прежний pinned audit
в G0/G1 docs; свежей независимой проверки этих upstream bytes нет. Перед
реализацией сверить доступный pinned checkout с tree/blob/SHA256 receipts,
включая точную поддержку config, stdlib setup и command routing. Pin не менять.

Сохранять полные stdout/stderr, argv/cwd/config/env, exit/signal/timeout/timing,
rustc -Vv/Cargo и binary hashes, original/annotated/stripped source receipts;
весь generated output (`generated_code_*`, `generated_specs_*`, proof skeletons,
`interface.rrlib`, linking requirements), MIR/borrowck и frontend logs, включая
частичные artifacts при отказе. Вручную проверить source span/DefId target,
callee bindings, normal Drop и оба comparator unwind edges, suppression payload
Drop. Отсутствие artifact/edge — UNKNOWN, наличие имени — не correspondence.
Archive/config/input/file hashes и upload receipt проверить независимо по Build
API/dispatcher; raw logs/generated source вне Git. Собственный parser и reviewed
map не блокируют сбор данных; автоматизацию решать после реального output.

| Наблюдение | Значение / следующий decision |
| --- | --- |
| Cargo/rustc отвергает точный core | Compiler compatibility/setup; сохранить полный error, без замены source/compiler |
| Нет выбранного body/spec/binding | Frontend admission или LIBRARY-SPEC gap; отличить unrelated crate failure |
| Явный отказ выбранной операции/type | Unsupported language feature на данном pin; checkpoint без semantic patch |
| Есть code/spec/skeleton/linking obligations | GENERATED / UNPROVED; перечислить obligations, не safety PASS |
| OOM/timeout/неполные artifacts | INCONCLUSIVE; не intended negative и не разрешение retry |

Ресурсные долги: CURRENT T/F после callback, scalar↔one-cell array,
ownership read/copy/merge, guard/glue/tmp closure и actual callee applicability.
Конечный domain остаётся generic T/F, legal mutation/panic и caller-reachable
length/ZST paths. Normal post возвращает initialized uniquely owned range,
CURRENT F/frame, закрытые tmp/loans; unwind до guard возвращает intact range,
после shift actual guard восстанавливает CURRENT held owner в текущий gap.
Sortedness/rollback не обещаются на panic; abort отдельно. Эти posts в G1
**не доказаны**. `run_check=false` оставляет Rocq verification NOT_RUN;
успешная генерация и Cloud SUCCESS не доказывают безопасность.

## Cloud minimum и разрешения

Прочитана текущая policy/runbooks/COMPLETION-PLAN из origin/main
`6e1a8e59c56669abe5e6ec2013478e45ed2cc267` (PR #8; прежняя policy
`5bf53668a4afa51c302e599be91a2dbc4b24042d` сохранена). Общие docs принять
адресно до следующей executable сессии; чужую research history не merge.
Migration receipt `5ce5bf402d2537ca3a49e403cf942e63abf785dc` прочитан.
Live read-only active.json: **schema_version=3/max_active=3/reservations=[]**.
ACK/readback migration уже выполнены для select-sort4/merge/verifast;
three-Build overlap NOT_OBSERVED. Старый v2 текст этой ветки устарел.
**V3_OWNERS исключает refinedrust-feasibility**: нужен отдельный owner/adoption
decision и reviewed client/lane/recipe registration; alias peer или прямой
submit недопустимы. Лимит не увеличивать; occupancy включает API untracked и
unresolved Builds, один на owner/ledger. Пустой state не является API capacity audit.

Минимальная closure — Linux x86_64, pinned cargo/rustc/rustc-dev/llvm-tools,
два sibling RR binaries, linker и locked frontend/target Cargo dependencies,
exact source Gitlinks, config и нужные pinned stdlib exports. Полный Rocq/Dune
proof environment не нужен, если exports уже подготовлены и проверены;
иначе отдельно оценить их setup, не подменять произвольными artifacts.
Повторно использовать verified digest-pinned image; новый bespoke Docker/image
receipt framework не prerequisite. Digest/infra/recipe сейчас UNCONFIRMED.
Начальный resource proposal: штатная E2_STANDARD_2, jobs=1, 100 GB disk;
это минимальный кандидат, не измеренная гарантия RAM/времени. OOM — полезная
диагностика, без автоматического перехода на 32 CPU.

Для будущего одного warm diagnostic предложить timeout **1200 s**, reservation
**1260 s** (queue envelope 60, packaging reserve минимум 70 внутри timeout).
Cold setup при отсутствии подходящего image — отдельно до **1800 ledger s**,
не доступный сейчас бюджет и не прогноз завершения. Нужны explicit phase/window,
свой ledger/state, опубликованные proof/infra SHAs, reviewed execution image/
recipe и разрешения submit/read/log/evidence upload; registry write только при
отдельно разрешённом cold setup. Использовать существующий dispatcher/IAM,
не менять production IAM/triggers/coordinator вручную. Charge ceil(create→finish),
unknown submit удерживает slot, никаких duplicate/retry/заимствований бюджета.

**STOP после documentation commit.** Parser development, Cloud, extraction,
compilation, verification, инфраструктурная интеграция и G2 сейчас не разрешены.
