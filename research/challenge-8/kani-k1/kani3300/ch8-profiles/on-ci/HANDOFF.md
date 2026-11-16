# Profiles ON — worker15, одна стадия

Input g0 `ff62cd43d6c565ec93d8bc9f3c671c1e99d9d971`; задача TASK-CH8-PROF-ON-W15.md.
Локальный control: `d569db0c1f98e26573d0d15d022e9ac0c6d877fb`, tree `660633a37fb527dae4bdc2d9c845bd65ca578cdb`, branch `work/ch8-prof-on-w15`, worktree `/root/kani-ch8-prof-on-w15`. Единственный parent — SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7`. Commit имеет `[skip ci]`; исходный OFF control и historical evidence не менялись.

Source P′ `9fa2f7f97760584f38738909625c064006d8a936`; tool `Tiramisu-Cake/kani` SEL1, nightly-2026-10-23. Manifest62,9 negatives, all oracle/bounds/cfg/resource caps и batch53+9 сохранены. Flags как OFF плюс uninit ON, valid-value OFF. Tool source/build отделены от control; Git identities проверяются до/после групп. Static path `--repo ..` проходит; прежний `../..` отвергается.

RISKS.md/JSON: general scratch/PolymorphicIter достижим в `freeze_noncopy_n2` и case2 `rejects_always_true`; N32 network route не достигает ни одна строка. Статически недоступных flags/cfg не найдено. Known risk не меняет oracle: новый unsupported failure/недоступный flag/cfg/timeout остаётся blocker/UNKNOWN/STOP с точной причиной, не исчезнувшей строкой.

Reuse accept-v4 фиксируется CLASSIFIER-REUSE.json;15 source-chain files stock/SEL1 идентичны (TOOL-CLASSIFIER-COMPAT.json). Это reuse функций/gates, не перенос OFF admissions. **Historical replay scripts OFF-bound; не запускать их на ON artifacts.** После будущего CI каждую ON строку классифицировать заново с exact tool/config/row bindings, regular stdout, полным property inventory, reviewed roles/unsupported assert-false link, target/wrapper/clause/cover/frame binding и accepted matching leaf. Новые uninit properties и неизвестные роли не наследуют exemptions. Сам runner — консервативный recorder, не acceptance engine.

VALIDATION.json:46 runner synthetic tests +76 unchanged classifier tests PASS; exact control guard на synthetic GitHub attempt1 env PASS; audit_static.py и patch reconstruction PASS. ci-only.patch восстанавливает exact control tree из SEL1. normalized-control-delta.patch — удобный review view после mechanical rename/pins, не самостоятельный reconstructing patch. Обычная полная patch — ci-only.patch.

Проверка пакета (только Git/Python, без compiler/verifier):

```sh
cd /root/kani-ch8-prof-on-w15/ch8-prof-on-control
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q test_runner.py test_profiles.py test_batch.py test_workflow_repo.py test_on.py
```

Independent review **GO** после исправления exact-feature guard; исходный NO_GO сохранён в REVIEW-v1.json. Review identities/result — REVIEW.json и review-packet. CI-REQUEST.json содержит все pins/caps/hashes. MANIFEST.sha256 покрывает файлы handoff, кроме себя. Containing g0 commit сообщается в последней READY строке ответа, не circular hash внутри пакета.

Координатору для отдельного следующего этапа: проверить exact hashes/review, полномочия/бюджет и публикацию exact candidate; предложен один dispatch. В этой стадии push/CI/publications/ledger/local cargo-rustc-Kani-CBMC: **0**. Qualification **NOT_RUN**, independent proof credit **NONE**. Подготовка завершает ровно одну выданную стадию, не ON qualification.
