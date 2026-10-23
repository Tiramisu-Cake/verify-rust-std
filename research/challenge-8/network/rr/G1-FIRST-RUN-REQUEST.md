# First real G1 — execution request / BLOCKED

2026-10-12. Baseline `7e9851318f6eca5c356a439af7728e899cc6b5f1`;
policy origin/main `6e1a8e59c56669abe5e6ec2013478e45ed2cc267` прочитана.
**Cloud budget/charge 0/0; Build/token/ledger NONE; frontend/proof NOT_RUN.**
V4 отменён последним поручением: historical package NOT ADOPTED / NOT MIGRATED.
Следующий шаг — решение по запросу ниже, затем один разрешённый diagnostic run.
Новых runner/parser/CI проектов не требуется.

## Exact inputs и первый опыт

Read-only RR `/root/refinedrust-feasibility-sources/refinedrust-332d945fafa14bf55c0c8390cb35ec4b0c012cff`:
HEAD `332d945fafa14bf55c0c8390cb35ec4b0c012cff`, tree
`b33bcccbbbd6168ac73e0c7238a1edddbe34057c`; HEAD/tree и clean checkout
повторно проверены. Source recovery закрыт; полный byte receipt сохранён в
[G1-SOURCE-RECOVERY](G1-SOURCE-RECOVERY.md). В Cloud этот source ещё не доставлен.
Std `c7ca8c467aecf10a4b53039372ee97714f854ee3`, SmallSort blob
`e555fce440872898e47fd5114f32eb15401d07df`, SHA256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
Compiler nightly-2026-08-28 / `e457a7b0d326d67b4322ef0d11bd715cfaeda48f`;
host `x86_64-unknown-linux-gnu`. Stock workflow подтверждён
[G1-PINNED-FRONTEND-AUDIT](G1-PINNED-FRONTEND-AUDIT.md).

Существующий минимальный candidate: image/version/hash preflight → disposable
exact core + ghost-only byte receipts → отдельный stock control → один target:

```bash
RR_CONFIG=/workspace/evidence/g1/RefinedRust.toml cargo refinedrust -- \
  --manifest-path /workspace/g1-source/library/Cargo.toml -p core \
  --locked --offline --target x86_64-unknown-linux-gnu
```

**Только Cloud после авторизации.** Native Cargo wrapper вызывает cargo check;
runner вызывает эквивалентный sibling `cargo-refinedrust -- ...`. Runtime std и
generic signatures неизменны. Explicit pinned ptr/closures/sized `.rrlib`,
run_check=false, no_verify=false, admit_proofs=false, panic=unwind, overflow/
MIR/NLL/linking on; hook unset. Rocq/Dune execution не нужен для generation-only.
Сохраняются полные diagnostics, команды/версии/config/hash receipts, partial
MIR/Radium/spec/proof skeletons и verified external evidence archive.
Никакой собственный Radium parser не является gate.

Первый причинный отказ review по stage/symbol/span: compiler compatibility;
frontend admission / missing library spec; selected unsupported language feature;
либо generated resource/linking obligations **UNPROVED**. Unrelated core failure
не доказывает отказ insert_tail. Generated output и collector SUCCESS не safety PASS.

## Три оставшихся gate и точный запрос владельцу

1. **Окружение.** Предоставить совместимый immutable image digest и receipt
   либо отдельно разрешить cold setup (timeout1740 / ceiling1800 ledger s).
   Image содержит pinned Rust cargo/rustc/rustc-dev/llvm-tools/rust-std, linker,
   git/python3/time/CA, sibling RR binaries с embedded Cargo/rustc paths,
   проверенный exact RR checkout/stdlib exports и offline union frontend+core
   Cargo dependencies. Freeze binary hashes, vendor/config и OS closure.
   [freeze.json](g1-minimal/freeze.json) сейчас NOT_FROZEN: digest/binary/config
   hashes null; registry inventory ранее denied, наличие image UNKNOWN.
   Cold candidate остаётся NOT_DISPATCHABLE: context URI/generation/SHA256,
   exact OS packages/vendor closure, builder digest и registry destination
   не назначены. Local exact source и export audit уже подтверждены; прежние
   source-unavailable поля cold/source-transfer manifest исторические.
   Не требуется новый GitLab recovery или regeneration stdlib proofs.
2. **V3 adoption и узкая lane.** Согласовать review/adoption существующих
   [owner proposal](g1-minimal/coordinator-owner.proposal.patch) и
   [dispatcher proposal](g1-minimal/dispatcher.proposal.patch) в собственный client.
   Base `454d8a17e9c7989cbfebf24c4cdd31fea629abb0`; transport/packager сохранены.
   Owner allowlist расширяется до четырёх имён при **schema3/max3**;
   v2→v3 transition не повторяется, live state не редактируется.
   Все три действующих client owners принимают адресный owner patch сами на
   безопасной границе без конфликтующей dispatcher-команды; нужны fresh ACK
   с committed infra SHA + coordination/control SHA256, плюс ACK собственного
   RR client. До всех ACK — ни RR request/reservation/submit, ни peer writes.
   Старый code SHA256 `49464b5a1078c99f8f44ef0bba06bb285c039ca0a0ab10d104bc7b54f32cb4bc`
   подтверждён чтением select-night/merge-origin/verifast-upstream-l.
   Proposed coordinator SHA256
   `9b03adb5bfc3bbcb12160ff1ec054d67b9ad6d1e062bacc7224be5ad7b539140`;
   patch SHA256 `5cdb08e5cd6e327ce74a7e0de40ea178836b3247c63a52731c4860c0fd8fe7e0`.
   Production clients/state не менялись. Review/ACK пока отсутствуют.
3. **Исполнение.** Назначить phase (предложение `RR-G1-FIRST-FRONTEND`), lane
   `refinedrust-g1-minimal`, явное UTC start/main/absolute окно, published
   frozen proof/infra SHAs, собственный absolute ledger
   `/root/verify-rust-std-refinedrust-feasibility-20261011/research/challenge-8/refinedrust-feasibility/g1-minimal/BUDGET.json`
   и state `/root/refinedrust-feasibility-sources/cloud-g1-state` (не созданы).
   Разрешить один warm attempt: **timeout1200 / ceiling1260 ledger s**,
   E2_STANDARD_2/jobs1/disk100GB. Cold1800 — отдельный account/recipe/approval,
   не часть warm бюджета. Нужны существующие submit/status/log/evidence permissions,
   image read; cold дополнительно context transfer и approved registry write.
   IAM/quotas/triggers/credentials здесь не менялись. Окно/бюджет UNASSIGNED.

После закрытия gates точная форма submit из own reviewed client:

```bash
python3 research/challenge-8/cloud-build/control.py \
  --phase-id "$rr_phase" --ledger "$rr_ledger" --state-dir "$rr_state" \
  --owner refinedrust-feasibility submit \
  --infra-sha "$rr_infra_sha" --proof-sha "$rr_proof_sha" \
  --lane refinedrust-g1-minimal --source-mode pinned-objects --timeout 1200
```

Переменные берутся из отдельно approved frozen account, сейчас команда не исполняется.
Dispatcher под общим flock учитывает API untracked + unresolved; максимум три,
один на owner/ledger. При занятых slots штатное ожидание/reconcile в разрешённом
окне, без отмены peers/alias/заимствования budget. Unknown API reply удерживает slot;
повторный submit запрещён. Snapshot live schema3/max3 содержит merge Build
`7f45c598-f9f2-424a-ae19-84701c9aaf4f`, token
`dispatch-28ded6436a7040dca326871fc42abb50`; это сохранённая reservation,
не API capacity verdict. Свободные slots проверяются dispatcher при submit;
project-specific provider quota остаётся UNKNOWN, её нельзя вывести из active.json.

## Checks и остановка

Isolated synthetic owner proposal: PASS — RR занимает третий slot, четвёртый
отклонён; duplicate owner/ledger и unknown token отклонены; API untracked и
unresolved учитываются, peer JSON сохраняется; старый client fail closed.
Ни API, ни live lock/state не использованы. TemporaryDirectory с префиксом
refinedrust-feasibility-v3-owner- автоматически удалён, Python -B без pyc.

PASS_DIAGNOSTIC требует complete evidence и manual actual target admission;
proof status всегда NOT_RUN/UNPROVED. Compiler/setup/unrelated failure, timeout,
OOM/missing output — INCONCLUSIVE с первым причинным blocker. Pin/runtime mismatch,
selected unsupported feature, новый trust requirement, deadline/ceiling или
unknown submission → STOP/evidence checkpoint, без неразрешённого retry.
Сейчас **STOP до решения по трём gates**, Cloud и VPS toolchain NOT_RUN.

Cleanup: df -h/-i до: free1.9G/97%, inode24%; после подготовки: free1.8G/97%,
inode25% (общий VPS меняется параллельно). Собственных устойчивых удалённых путей
нет, reclaimed persistent space **0 bytes**. Изолированный test temp автоматически
убран. /tmp/g1-cfg-v2, g1-cb-old.patch, g1-cfg-patch, g1-cb61-h2b-static-20261008,
g1-cb61-h2c-static-20261008, g1-remediation-review-217c939 оставлены: принадлежность,
активное использование/evidence need не установлены; имя не основание удаления.
Sources/Git objects/evidence/peers/coordinator сохранены.
