# Exact RefinedRust frontend audit — G1 diagnostic

2026-10-12; project baseline `2fb4ec507b35e04a0953bb2176a9c6434bf506c5`.
Policy/Cloud rules прочитаны на origin/main
`6e1a8e59c56669abe5e6ec2013478e45ed2cc267`. **Cloud budget/charge 0/0**.
Ни compiler, source extraction, frontend, Rocq/Dune, ни Cloud Build не запускались.

Read-only source root:
`/root/refinedrust-feasibility-sources/refinedrust-332d945fafa14bf55c0c8390cb35ec4b0c012cff`.
HEAD `332d945fafa14bf55c0c8390cb35ec4b0c012cff`, tree
`b33bcccbbbd6168ac73e0c7238a1edddbe34057c`; source identity —
[G1-SOURCE-RECOVERY](G1-SOURCE-RECOVERY.md). Все file:line ниже относятся к этому
exact source, не к движущейся upstream ветке. Trusted RR bytes не изменены.

## Подтверждённый штатный workflow

| Вопрос | Source / результат |
| --- | --- |
| Cargo routing | `rr_frontend/refinedrust_frontend/src/bin/cargo-refinedrust.rs:130–139` отделяет RR options до `--`, Cargo options после него. Direct `cargo-refinedrust -- ...` также корректен. Строки54–59 запускают **cargo check**, ставят sibling refinedrust-rustc и CARGO_TARGET_DIR |
| Embedded tool paths | `rr_frontend/refinedrust_frontend/build.rs:36–45` встраивает `which(CARGO/RUSTC)`; wrapper54 вызывает **env!(RR_CARGO)**. Совпадение standalone cargo hash недостаточно без проверки этого пути |
| Выбор функций | `translation/src/environment/collect_prusti_spec_visitor.rs:68–160` собирает procedures, но `translation/src/lib.rs:2253–2305` регистрирует только функции с rr-атрибутами/подходящими impl attrs. `rr::verify` — такой marker; `spec_parsers/verbose_function_spec_parser.rs:1068` не добавляет им контракт |
| ADT coverage | `translation/src/lib.rs:1804–1834`: register_all_adts=false выключает eager ADTs, **не общий drop-glue scan**. `types/translator.rs:911,1233` лениво регистрирует используемые structs; отсутствие refined_by не требует unit refinement |
| Frontend on/off | `refinedrust-rustc.rs:54–58,78–112`: no_verify=true отключает translation/dumps; dependency crates получают его при verify_deps=false. Core выбран -p core, значит primary package; recorded compiler env должен это подтвердить |
| Proof execution | `refinedrust-rustc.rs:136–163`: post_generation_hook отдельно запускает command; run_check=true вызывает dune build. Candidate оставляет hook unset и run_check=false. `translation/src/lib.rs:967`: admit_proofs управляет генерируемыми proof templates; false **не доказывает** их obligations |
| Unwind | `rrconfig/src/lib.rs:130–132,246`: conservative panic mode штатный. MIR Drop/unwind и generated normal/exceptional specs существуют в source; их **наличие/соответствие target** устанавливается только по реальному output. Candidate сохраняет -Cpanic=unwind и overflow checks |
| Linking | README170–178 и `rrconfig/src/lib.rs:85,119`: generate_linking_requirements=true явно нужен для участвующих crates. Это generated obligations, не автоматически закрытый linking theorem |
| MIR/NLL | `refinedrust-rustc.rs:88–111`: debug dump → log_dir/mir; borrowck → log_dir/nll-facts; -Zalways-encode-mir/-Zpolonius и overflow override при no_verify=false. `translation/src/lib.rs:1090–1189`: Radium/Rocq code/specs → output_dir/crate/generated, skeletons → proofs, interface.rrlib → output_dir/crate |
| Messages | `refinedrust-rustc.rs:45`: env_logger. `translation/src/lib.rs:3418–3453` пишет info о loadpath/found interfaces/includes, frontend errors сохраняются в command stdout/stderr. Exit0 без target evidence не admission theorem |

Итак, Cargo invocation crate-level, но `rr::verify` **действительно выбирает
функцию для регистрации**. Прежняя фраза «нет выбора DefId» не означает перевод
всех unannotated functions. Общие trait/ADT/drop-glue stages всё ещё могут
остановить crate до target; это INCONCLUSIVE для insert_tail.

## Stdlib interfaces и минимальные исправления

`translation/src/shims/mod.rs:15–42` рекурсивно находит `.rrlib` в lib_load_paths;
**discovery не импорт**. `translation/src/lib.rs:3380–3395,3418–3460` загружает
только rr::include/export_include и их export_libs. Crate attr parser
`spec_parsers/crate_attr_parser.rs:94–102` распознаёт include/export_include.
Официальный `stdlib/stdlib/src/lib.rs:3–5,12–30` показывает register_tool,
custom_inner_attributes и export_include setup.

Candidate исправлен только по этим фактам:

- Core ghost setup дополнен `#![feature(custom_inner_attributes)]` и
  `#![rr::include("ptr")]`, `#![rr::include("closures")]`,
  `#![rr::include("sized")]`; byte injector разрешает только эти дополнительные
  literals. Unit refinements/True unwind/only_spec не добавлены.
- `freeze.json.lib_load_paths=["/opt/refinedrust/stdlib"]`: recursive discovery
  pinned outputs, без opam/Nix runtime dependency. `find_stdlib=false` здесь
  означает **явный непустой loadpath**, а не запрет stdlib models.
- `RUST_LOG=info` сохраняет native library/translation diagnostics.
- Cloud-only RR --version stage записывает compiler/Cargo build metadata и
  проверяет embedded paths против frozen binaries до source/target stages.

`ptr` содержит actual core ptr::{read,sub,copy_nonoverlapping} export paths;
`closures` — FnMut; `sized` — Sized/Drop. Exact interface blob/SHA256 receipts:
[stdlib-exports.json](g1-minimal/stdlib-exports.json). Остальная source closure
verified по full RR tree. Это existing stock modeling boundaries; их imports
не доказывают exact generic owner/copy/callback obligations или source refinement.

Actual std остаётся `c7ca8c467aecf10a4b53039372ee97714f854ee3`, SmallSort blob
`e555fce440872898e47fd5114f32eb15401d07df`. **MaybeDangling annotations сохранены**:
actual ManuallyDrop::new вызывает MaybeDangling::new, Deref вызывает as_ref
(manually_drop.rs181–185,271–278 этого source). Просмотр старого другого std blob
не разрешает удалять эти transitive callees. Deref/const/?Sized/MaybeDangling
binding/admission остаются диагностическими вопросами, не поводом для нового
summary или trusted patch.

## Первый G1 и Cloud inputs

Штатная target команда (Cloud-only, сейчас **не выполнять**):

```text
RR_CONFIG=/workspace/evidence/g1/RefinedRust.toml cargo refinedrust -- \
  --manifest-path /workspace/g1-source/library/Cargo.toml -p core \
  --locked --offline --target x86_64-unknown-linux-gnu
```

Sequence/entrypoint/source restore/evidence — [G1-RUN-READINESS](G1-RUN-READINESS.md),
с поправками этого audit. Control изолирован от core output. Сохраняются все raw
messages, versions, config/argv/env/exit/timing, source/ghost/tool hashes,
MIR/NLL/generated artifacts; first-error hint имеет UNREVIEWED attribution.
Собственный Radium parser не gate. Generation/diagnostic_complete не safety PASS;
resource N/U, CURRENT recovery, guard/glue/copy/shape и actual callee applicability
остаются UNPROVED. Unsupported selected feature, new semantic/trust requirement,
pin mismatch, deadline/OOM/incomplete evidence → checkpoint STOP, без retry.

Минимальная frontend closure: Linux x86_64, nightly-2026-08-28
(`rustc-dev`, `llvm-tools-preview`, cargo/rustc/rust-std), linker и locked Cargo
dependencies. Exact frontend Cargo.lock и compiler archives уже pinned; установка
Rocq/Dune нужна для proof checking, **не для generation-only с committed rrlib**.
Pinned source README допускает отдельно frontend и stdlib install; exports уже
в source tree, поэтому regeneration stdlib proofs не prerequisite diagnostic.
Совместимого **подтверждённого image digest всё ещё нет**: registry inventory
ранее denied. Exact tool/source/tree/embedded binaries/union vendor+Cargo config/
OS dependency closure и image digest должны быть frozen в отдельном setup.
Никакие apt/vendor/executable hashes не выдуманы.

Warm proposal **1200 s timeout /1260 ledger s**, cold отдельно **1740/1800**;
E2_STANDARD_2/jobs1/disk100GB остаётся unmeasured resource candidate. Production
IAM/quota/triggers/budget не менялись. Требуются отдельные allowed recipe/phase,
свой ledger/state/window, опубликованные proof/infra SHA и execution authorization.

## V4 и текущий checkpoint

Отдельный v4 infrastructure package публикуется в
`infra/coordinator-v4-refinedrust-20261012`, exact package SHA
`c506d59822532ecf1fad2681cac5b150eeec138f`; portable code
`3bf951e5fae4a34df48854f1e215dd881eb8658f`.
[READY_FOR_ADOPTION checkpoint](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c506d59822532ecf1fad2681cac5b150eeec138f/research/challenge-8/cloud-build/coordinator-v4-refinedrust-20261012/CHECKPOINT.md)
содержит addressed patch/процедуру и четыре MISSING ACK. Это явный schema4/max4 transition,
не подмена working v3 constant. Live **v3/max3** сохраняется, пока четыре real
clients не примут совместимые bytes и не дадут ACK; RR dispatcher ещё нужно
provision/review/adopt. После перехода RR сможет занимать четвёртый независимый
slot при тех же phase/IAM/budget gates; миграция сама G1 не разрешает.

Provider quota read-only query `gcloud beta quotas info list --service=cloudbuild.googleapis.com`
вернул SERVICE_DISABLED для Cloud Quotas API; API не включали. Project-specific
four-Build/CPU capacity **UNKNOWN**. Public defaults global Build10–30 и regional
E2 CPU5–100 не подтверждают конкретный проект/совместный machine mix:
[Google Cloud Build quotas](https://docs.cloud.google.com/build/quotas).

Validation: static Python3.10/JSON/ghost-anchor/allowlist checks и четыре pure
saved-data service tests PASS. Real frontend/version/image/compiler/verification
**NOT_RUN**. Старые планы/source-transfer записки сохраняются как история;
этот exact-source audit заменяет их UNKNOWN workflow/source-access утверждения.

VPS cleanup: до free2.3G/inodes20%, после free2.2G/inodes21%; root96% used.
Удалены только три собственных infra-test pyc под
`/root/verify-rust-std-coordinator-v4-refinedrust/research/challenge-8/cloud-build/__pycache__/`
и пустой каталог (coordination, coordination-v4-transition, coordination-v3-transition;
суффикс cpython-312.pyc). Freed **56 KiB allocated blocks**, active FD/mmap не найдены.
Mission-prefixed TemporaryDirectory fixtures автоматически убраны; /tmp peers,
shared caches, source, Git objects и raw evidence не удалялись. Paths/size receipt:
`/root/refinedrust-feasibility-sources/v4-audit-20261012/CLEANUP.json`.
