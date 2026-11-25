# REV2 S13/base1 · пакет диагностического прогона

**READY_FOR_REVIEW** · `go=NOT_GRANTED` · `proof_credit=NONE`.

Ревью g0 `68f46bbe72` принимает привязку и внешний пороговый перенос для exact S13/base1 и разрешает один будущий диагностический Ubuntu-пакет. Здесь зафиксированы его локальные входы для ревью tree. Компиляция, нативный discovery, вердикты и ресурсы остаются `UNKNOWN`. [Ревью дизайна](REV2-S13-BINDING-REVIEW.md) · [Дизайн](REV2-S13-BINDING-DESIGN.md)

## Идентичности пакета

| Объект | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Control FIX3 | `0dcc435f7d3f7e73a7ae362445e385e1747cedc9` | `8ec7f5a766154288b8b441be85f34103dc80a12e` | `cdd188a0a8c987c04cb5722a89b3533e3c72015d` |
| Control S13 binding | `4beae2f1b03f6e88abd8dc673eb5a37b835f2dd3` | `c58dac28828becef22d4a3959be30f1b2204310a` | `0dcc435f7d3f7e73a7ae362445e385e1747cedc9` |
| Локальный review-trigger | `0063edc7e748ef32c9644768ac5819c747fd6430` | `c58dac28828becef22d4a3959be30f1b2204310a` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Std overlay S13 binding | `32c2857f4b7137601de54ea42a02610c8fd29ed9` | `0e682cfceaed5d33d3d3374b5dc97da5012bba93` | `32129c149a15fb1b60a7314e738f3cb466d076e5` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |

- Control worktree `/root/kani-rev2-s13-binding-control-w14`, ветка `work/rev2-s13-binding-control-w14`. Локальный trigger доступен по `local/rev2-s13-binding-trigger-review`. Оба коммита с `[skip ci]`, автор `Tiramisu-Cake <igkharin@gmail.com>`. [Workflow](/root/kani-rev2-s13-binding-control-w14/.github/workflows/ch8-q-pilot.yml) · [Runner](/root/kani-rev2-s13-binding-control-w14/ch8-cal1/run.py)
- SHA-256 request `009a81ea082fe51a7e3f978b133a32108c3d11f9b9e7979f38c07efd92c2a936`, SHA-256 bundle `8f72138f0f1129ec197b55bac2b946cee28401f2848f246bf57aaa046d67e5da`. Canonical roster SHA-256 `8d9d0d98d55db676b37dabf751020f6ec7709abccc2e59034a6a23f85b597f1c`. [Request](/root/kani-rev2-s13-binding-control-w14/ch8-cal1/CI-REQUEST.json) · [Bundle](/root/kani-rev2-s13-binding-control-w14/ch8-cal1/std-overlay.bundle)
- Bundle требует один prereq `dab03cf510df5c35141cde49f1368b1242f5035e` и объявляет только Std overlay `HEAD`. Цепь поверх базы — CAL1 `080a010415` → CAL2 `043a1f19f9` → FIX3 `32129c149a` → S13 `32c2857f4b`. Guard сверяет commit/tree/sole parent всей цепи. Удаление новой cfg-регистрации и lint-записи восстанавливает точные blobs FIX3. Diff к FIX3 содержит только эти два изменения и модуль Proof. [Layout guard](/root/kani-rev2-s13-binding-control-w14/ch8-cal1/request.py)

Для отдельного допуска к запуску ожидается Actions variable `CH8_REV2_S13_BINDING_TRIGGER_TREE=c58dac28828becef22d4a3959be30f1b2204310a`. Workflow передаёт её как `REV2_S13_BINDING_TRIGGER_TREE`. Сохранены gate FIX1 на `Tiramisu-Cake/kani`, push в `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt `1`, SHA payload `after`, единственный parent из таблицы и clean detached checkout. Отсутствующий, неправильный или несовпадающий pin блокирует gate. Переменная прежнего провайдера сама допуск не открывает. Finish заново сверяет trigger, upload зависит от допущенного gate и успешного finish. Локальный trigger фиксирует дерево для ревью. Actions variable не менялась. [Guard](/root/kani-rev2-s13-binding-control-w14/ch8-cal1/request.py) · [Образец FIX1](REV2-NETWORK-PROVIDERS-FIX1-TASK.md)

## Два слота и критерий

| Слот | Exact selector | Ожидаемый исход |
| --- | --- | --- |
| `S13-BASE1-BITS` | `slice::sort::shared::smallsort::verify::rev2_s13_binding::s13_base1_bits` | `VERIFIED` |
| `S13-BASE1-CORRUPT-MASK` | `slice::sort::shared::smallsort::verify::rev2_s13_binding::s13_base1_corrupt_mask` | `FAILED`, единственный нативный `FAILURE` у `REV2_S13_BASE1_SORTED_POPCOUNT` |

Оба обычные Proof без stubs, `u8/KeyLess<u8>`, V34, `v[1..14]`, 13 независимых канонических битов, свободные q и frame-байты. Контроль инвертирует бит наблюдаемой маски после вызова. В regular и stock требуются согласованные нативные терминалы и профили. Для отказа контроля сверяются ID, класс, метка и координата `core/src/slice/sort/shared/smallsort/verify/rev2_s13_binding.rs:53` в обоих каналах, плюс exit code 1. Отказы runner, safety/unwind и любые другие нативные `FAILURE` исключают совпадение с ожиданием. [Целевой assert](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_binding.rs:53) · [Сверка native результатов](/root/kani-rev2-s13-binding-control-w14/ch8-cal1/results.py)

Обязательны `SUCCESS` для `REV2_S13_BASE1_Q_FRAME`, `REV2_S13_BASE1_V34_FRAME`, `REV2_S13_BASE1_CANONICAL_OUTPUT`, а у положительного также для `REV2_S13_BASE1_SORTED_POPCOUNT`. Covers на обоих — `REV2_S13_BASE1_MIXED_INPUT`, `REV2_S13_BASE1_INPUT_INVERSION`, `REV2_S13_BASE1_REACHED_POST` и нативные экземпляры `CAL1 q actual comparator executed`. Receipt сохраняет исход `FAILED` у контроля и отдельно `expected_result`. Итог `PAIR_WITHIN_PROFILE` требует совпадения обоих исходов, достигнутых covers, полного свидетельства, reap, валидного sampler, финальной аттестации и соблюдения лимитов обоими слотами. Остальные пары сохраняют диагностические причины и `proof_credit=NONE`. [Отчёт](/root/kani-rev2-s13-binding-control-w14/ch8-cal1/report.py)

## Профиль и бюджет

Одна job `ubuntu-24.04`, 75 мин. После проверки исходников выполняются stock build, аттестация, cfg-on compile preflight и один cfg-on `kani list`. Проверяется наличие четырёх регистраций FIX3 с прежними категориями и двух новых Proof с их точными путями; измеряются ровно два новых селектора. Cfg-off проверен статически по bundle и исходникам. В build stock Kani флаги Std не передаются. У preflight, discovery и измерений одинаковый `RUSTFLAGS` с `kani_smallsort_cal1`, `kani_smallsort_cal2_merge_mask`, `kani_smallsort_rev2_provider_cost`, `kani_smallsort_rev2_s13_binding`.

Каждый singleton имеет отдельные cwd, Cargo/Kani target, tmp и export. Kani на пине из таблицы, CBMC 6.11.0, stock CaDiCaL, `--exact --jobs=1 --no-assert-contracts`, `--cbmc-args --object-bits 12`, unwind 36. Default safety, overflow и unwind включены, uninit/validity OFF. Для обоих холодное окно 180 с, TERM/KILL/reap 10 с, receipt 5 с, 4 194 304 KiB группы при резерве ОС 2 097 152 KiB. Setup использует прежний отдельный cap 10 GiB. Цель по VT ≤120 с на каждом корне.

| Фаза по общему monotonic clock | Бюджет | Конец от старта |
| --- | --- | --- |
| Setup целиком, включая preflight и discovery | 45:00 | 45:00 |
| Два слота по 195 с + по 10 с launch headroom | 6:50 | 51:50 |
| Финальная аттестация | 2:00 | 53:50 |
| Finish и upload | 12:00 | 65:50 |
| Резерв | 9:00 | 74:50 |
| Внешний предел job | 75:00 | 75:00 |

Supervisor FIX3 сохранён. Надёжный reap после отсечки позволяет перейти к следующему слоту. Ошибка supervision или неподтверждённый reap останавливают дальнейшие слоты. Отчёт сохраняет отсечку, фазу, VT при наблюдении, group/CBMC RSS, первую CNF при наблюдении, covers и bounded receipts. Критерий `PAIR_WITHIN_PROFILE` нужен для сравнения с историческим timeout байтового пути. Для pr752 отдельно остаются обе ОС и штатная партиция. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md) · [База FIX3](REV2-NETWORK-PROVIDERS-HANDOFF.md)

## Локальные проверки

- Python suite на точном shallow detached review-trigger, через shell-блок `pins` из workflow, с синтетическим push и свежей шкалой monotonic от 60 с. Gate выдал точные Std/Kani pins. **95/95 за 20,981 с**, Python 3.12.3. Проверены exact roster, отказ по старой переменной и изменённому дереву, profile/deadlines, продолжение после reap, сопоставление ожидаемого контроля и отклонение постороннего или неполного отказа.
- PyYAML разобрал workflow с запретом дубликатов ключей. Сверены одна Ubuntu job, push ref, permissions и имя Actions variable. `bash -n` прошёл у всех 6 shell-блоков.
- Bundle проверен `git bundle verify`, `git bundle list-heads` и `git bundle unbundle` на чистой shallow-базе Std с depth 2. Сверены prereq, HEAD, четыре дерева и родителя, неизменные refs и точный layout.
- `git diff --check` прошёл для дельты control от FIX3, локального trigger от sole parent, Std от FIX3 и Handoff в g0. `rustfmt --check` прошёл на затронутой проверочной части Std и закреплённом runtime файле:

```bash
cd /root/verify-rust-std-rev2-s13-binding-w14
root=library/core/src/slice/sort/shared/smallsort
/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --check --edition 2024 \
  --config use_small_heuristics=Max --config skip_children=true,reorder_modules=false \
  "${root}.rs" "$root/verify.rs" "$root/verify/rev2_s13_binding.rs"
```

Пакет, trigger и Handoff существуют локально. Cargo, rustc, Kani и CBMC локально не запускались. CI и публикации не было.
