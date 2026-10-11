# Повтор static preflight и F1 service checks

Compiler/extraction/refiner/verifier/proof runners не используются. `source-comparison.py` выполняет только Git object reads/hash checks. `test-integration-admission.py` импортирует два проверенных inert classifier/parser modules и вызывает `_body_glue_ast_evidence` на saved/synthetic AST; `_prepare`/hosted `run` не вызываются. Temporary synthetic fixtures автоматически удаляются. Original raw files/active merge runner/coordinator остаются неизменными.

Static команды, фактически выполненные:

```bash
git -C /root/verifast-maintainer-slice-i merge-base \
  b6cb276afd13107c2a90ca50acbb12ff0a992dd8 \
  a158398e336edce9817f62a55733a3470a986d7b
git -C /root/verifast-maintainer-slice-i diff \
  b6cb276afd13107c2a90ca50acbb12ff0a992dd8 \
  a158398e336edce9817f62a55733a3470a986d7b -- \
  src/verifast.ml src/verifast1.ml bin/rust/std/lib.rsspec \
  src/rust_frontend/vf_mir_translator/vf_mir_translator.ml \
  src/rust_frontend/vf_mir_exporter/src/lib.rs \
  src/rust_frontend/vf_mir/vf_mir.capnp src/refinement_checker
python3 research/challenge-8/verifast-review/i-glue-compat-20261012/source-comparison.py
```

Последняя команда выводит inventory/hash JSON; сохранён [INPUTS-AND-SOURCE-COMPARISON.json](INPUTS-AND-SOURCE-COMPARISON.json). Tool I repo path — read-only common object store; изменять/переключать его worktree не требуется. Совпадение source hashes с profile/manifest checked independently from patch filenames. 13 patches проверены как inputs, не применены к I.

F1 в собственной integration-runner copy: base project6283377b, old body gate там имеет дополнительные receiver/canonical metadata checks. Portable patch byte-identical опубликованному F1 patch с base420188dd; exact context match проверен. Единственная source mutation — этот hunk. Stock parser сохранён с snapshot628 bytes. Ни runtime contracts, ни source extraction, ни tool semantics не менялись.

Saved service inputs из `/tmp/merge-b1-v8-evidence-a9613c24`: positive `proof-ast.ml`, raw classification и extraction row; три hashes сверены с saved file inventory. Это use of saved AST для classifier check, **не** full raw-evidence review или proof-status upgrade v8. Дополнительный row argument передаёт именно прежнюю pinned extraction metadata; все canonical/lifetime проверки snapshot628 сохраняются. Synthetic duplicates изменяют оба равных contracts, штатный parser заново читает их из файла.

Фактически выполненная команда (из собственного project checkout):

```bash
c8_compat_package=research/challenge-8/verifast-review/i-glue-compat-20261012
c8_compat_output=$(mktemp -d /tmp/c8-compat-service.XXXXXX)
PYTHONDONTWRITEBYTECODE=1 python3 "$c8_compat_package/test-integration-admission.py" \
  --runner "$c8_compat_package/integration-runner/research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py" \
  --parser "$c8_compat_package/integration-runner/research/challenge-8/merge/overnight/stack-proof-ast-admission.py" \
  --case /tmp/merge-b1-v8-evidence-a9613c24/allprooflogs/checked-minimal-bridge/onecell-selected-drop/cases/positive \
  --extraction /tmp/merge-b1-v8-evidence-a9613c24/allprooflogs/checked-minimal-bridge/onecell-selected-drop/extraction.json \
  --mode fixed > "$c8_compat_output/f1-service.json"
```

В сессии output направлен в собственный package `F1-SERVICE-TESTS.json`. Результат: saved positive admitted; 14 duplicate/missing/extra/unknown/malformed/default/binder/wrapped mutants refused, 8 previous literal False/location cases pass. Это service-only; F1 applied только в собственной copy integration runner. Старая F1 reproduction уже сохранена в предыдущем immutable пакете; её результаты не переписаны.

**Будущая executable combined proof команда: NOT_DEFINED.** Tool head/profile/patch order заблокированы trust decision. Пины I/bounded v6/v8 не подставляются вместо отсутствующего нового candidate. Future gates указаны в FUTURE-GATES.md; новые session/ledger/provider authorization потребуются отдельно, никакого dispatch здесь нет.
