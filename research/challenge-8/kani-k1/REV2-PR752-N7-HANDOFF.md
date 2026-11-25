# pr752 · перенос двух fallback N7

## Локальный кандидат для w13

| Поле | Значение |
| --- | --- |
| Задание | [REV2-PR752-N7-TASK.md](REV2-PR752-N7-TASK.md) в `9b325943b07b6d08d8865f3b0caabc0de0f214d9` |
| Worktree | `/root/verify-rust-std-rev2-pr752-n7-w11` |
| Локальный ref | `refs/heads/work/rev2-pr752-n7-w11` |
| Commit | `a973479b9b55eb2a69527c95f82134d202a817c1` |
| Tree | `d5911d205aefc9464b968da029c3dabb983064ee` |
| Единственный parent | `dab03cf510df5c35141cde49f1368b1242f5035e` |
| Tree parent | `7fd542ad59723ff2beeacb9632fb0568e81b0655` |
| Коммит | `Add pr752 fallback proofs for length seven [skip ci]` · `Tiramisu-Cake <igkharin@gmail.com>` |

Точный diff содержит 12 добавленных строк в `verify/merge.rs`. Локальный кандидат прошёл статическую проверку. Ветка `pr752-push-candidate-20261123` в исходном worktree осталась на `dab03cf510`; публикационная ветка у владельца. Состояние g0 перед handoff — `dbb966e3b8c7d6fe1719ba4a626b56270a36c290`, где к заданию добавилось решение владельца о лимитах. [Два корня](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:571) · [Решение владельца](OWNER-DECISION-LIMITS-20261125.md)

| Точный селектор `--harness … --exact` | Вид | Unwind | Вызов |
| --- | --- | ---: | --- |
| `slice::sort::shared::smallsort::verify::merge::fallback_sorted_permutation_u8_n7` | `Proof` | 34 | `fallback_route_properties::<u8, _, 7>(lt_u8)` |
| `slice::sort::shared::smallsort::verify::merge::fallback_sorted_permutation_u64_n7` | `Proof` | 34 | `fallback_route_properties::<u64, _, 7>(lt_u64)` |

Для каждого типа `kani::any()` даёт произвольный инициализированный `[T; 7]`, активный срез занимает весь backing. Реальный `small_sort_fallback` вызывает `insertion_sort_shift_left` с offset 1 и далее `insert_tail`. Сортировка и oracle используют один компаратор с ключом `value >> 1`. Существующий `set_value_probe::<T>()` задаёт независимый произвольный probe до выбора входа. Oracle сравнивает до и после число вхождений полного значения, включая младший бит, поэтому равенство для произвольного probe охватывает все кратности. Проверки `output is sorted`, `input value counts are preserved` и post-call cover `fallback route properties checked` относятся к нормальному возврату на этих двух доменах. Стабильность равных ключей, другие типы и раскладки, trait-постусловия и поведение при панике за пределами этого утверждения. [Helper](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:399) · [Oracle](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:342) · [Реальный fallback](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort.rs:255)

### Локальные проверки

Команды из worktree кандидата. Обе завершились с кодом 0 и пустым выводом. `--edition 2024` соответствует `library/core/Cargo.toml`, `skip_children=true` ограничивает проверку одним файлом.

```sh
git diff --check HEAD^ HEAD
/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max,skip_children=true --check library/core/src/slice/sort/shared/smallsort/verify/merge.rs
```

Статическая сверка сопоставила с базой два отдельных блока с точными именами, `#[kani::proof]`, `#[kani::unwind(34)]` и одним вызовом helper в каждом. У новых корней отсутствуют `stub`, `stub_verified`, `assume`, дополнительные `cfg`, probes и контроли. `mod merge` включён в `cfg(kani)` через `verify` и доступен в обычном discovery с выключенным `kani_smallsort_controls`. Исполнение discovery кандидата ожидает разрешённого CI. Ниже вывод локальной проверки.

```text
Proof / unwind 34 / no stubs: slice::sort::shared::smallsort::verify::merge::fallback_sorted_permutation_u8_n7
Proof / unwind 34 / no stubs: slice::sort::shared::smallsort::verify::merge::fallback_sorted_permutation_u64_n7
Seven N0–N6 macro roots preserved
18 opt-in roots preserved: fixed_inputs.rs: 1, forwarding_contracts.rs: 2, helper_contracts.rs: 4, merge/profiles.rs: 5, tag_permutation.rs: 1, trait_contracts.rs: 5
Only 12 lines added in merge.rs; removing the two roots restores the base blob byte for byte
Runtime, trait contracts, workflow, script and pin have zero diff
```

Побайтовая сверка подтверждает исходные компараторы, helper, oracle и код всех opt-in корней. `git status --porcelain=v1` в кандидате пуст. Локальная работа завершилась статическими проверками и rustfmt. Cargo, rustc, Kani, CBMC, push, dispatch и публикация отсутствуют в этом этапе.

## Прогноз штатной матрицы

`kani.yml` оставляет восемь verifier jobs (`Ubuntu/macOS × p1–p4`), остальные jobs и бюджет прежние. `scripts/run-kani.sh` получает полный std inventory, берёт `standard-harnesses` перед `contract-harnesses`, режет последовательность по `ceil(total/4)` и выбирает точные имена. SmallSort учитывается как подмножество этого inventory. Пин `9834c96ce90ff57d8495416530b080dc3d52ce25`, OB12, `--no-assert-contracts`, `--output-format=terse`, Ubuntu `--jobs=2`, macOS bare `-j`. [Workflow](/root/verify-rust-std-rev2-pr752-n7-w11/.github/workflows/kani.yml:26) · [Сбор списка и флаги](/root/verify-rust-std-rev2-pr752-n7-w11/scripts/run-kani.sh:191) · [Разбиение](/root/verify-rust-std-rev2-pr752-n7-w11/scripts/run-kani.sh:289) · [Пин](/root/verify-rust-std-rev2-pr752-n7-w11/tool_config/kani-version.toml:5)

Пересчёт использует `base_ordered` с точной базы `dab03cf510` для каждой ОС. Два стандартных селектора вставлены по наблюдаемому лексикографическому порядку существующей группы `verify/merge.rs`. В прогнозе `u64_n7` и `u8_n7` занимают позиции 733 и 734 (с единицы) на обеих ОС. Удаление этих двух записей восстанавливает прежний порядок. Фактический порядок и все перемещения подлежат сверке после разрешённого прогона. [Ubuntu CAL1 45281488869](/root/ch8-artifacts/run-45281488869/ch8-cal1-Linux-X64-45281488869-1/discovery.json) · [macOS CAL2 45338903191](/root/ch8-artifacts/run-45338903191/ch8-cal2-macOS-ARM64-45338903191-1/discovery.json)

| ОС | Полный std p1–p4, база → прогноз | SmallSort p1–p4, база → прогноз | Сдвиг старых селекторов |
| --- | --- | --- | --- |
| Ubuntu | `552/552/552/550` → `552/552/552/552` | `0/184/0/61` → `0/186/0/61` | p2→p3: `mem::maybe_uninit::verify::check_zeroed_value_i128`, `mem::maybe_uninit::verify::check_zeroed_value_u32`. p3→p4: `ptr::const_ptr::verify::check_const_offset_from_u64`, `ptr::const_ptr::verify::check_const_offset_from_u64_arr` |
| macOS | `551/551/551/551` → `552/552/552/550` | `0/184/0/61` → `0/186/0/61` | p2→p1: `num::nonzero::verify::nonzero_check_clamp_for_16`. p4→p3: `ptr::const_ptr::verify::check_const_offset_from_u64_arr` |

### Время и память

Ubuntu singleton на исследовательском overlay `fb82da3c788c0e705cd598abee723200c0f28c42`, run `45358377716`, показал `u8` 22,42 с VT / 48,65 с cold wall и `u64` 83,11 с / 109,56 с. Оба пика группы около 1,96 GiB. Это 105,53 с serial VT (~1:46), 158,21 с суммарного cold wall двух отдельных запусков (~2:38) и около 83 с VT двух новых задач при идеальном перекрытии. Эти значения оценивают дополнительную работу в p2. Общая компиляция, соседние проверки и сдвиг границ влияют на время партиции. VT, cold wall и пик N7 на macOS пока неизвестны. У кандидата собственный штатный замер впереди. [REV2 singleton, область и замеры](REV2-FALLBACK-RESULTS-ANALYSIS.md#приёмка-двух-n7)

Сопоставимый baseline — `model-checking/verify-rust-std` Kani run `45173593629`, attempt 1, на точном `dab03cf510df5c35141cde49f1368b1242f5035e`. Все восемь verifier jobs и их `Run Kani Verification` завершились успешно. Время ниже рассчитано по `completed_at − started_at` отдельно для шага и для job. Очередь в wall не включена. Её длительность из этих полей неизвестна, при сравнении её учитывать отдельно, если доступны timestamps. `Verify step` включает время скрипта вместе с подготовкой, компиляцией, discovery и проверками. [Run](https://github.com/model-checking/verify-rust-std/actions/runs/45173593629) · [GitHub Actions job metadata](https://api.github.com/repos/model-checking/verify-rust-std/actions/runs/45173593629/jobs)

| ОС | Партиция | Baseline verify step | Baseline job wall | Кандидат verify / wall и дельты |
| --- | --- | ---: | ---: | --- |
| Ubuntu | p1 | 29:00 | 29:44 | Ожидают замера |
| Ubuntu | p2 | 78:28 | 80:16 | Ожидают замера |
| Ubuntu | p3 | 23:47 | 25:47 | Ожидают замера |
| Ubuntu | p4 | 76:17 | 77:16 | Ожидают замера |
| macOS | p1 | 35:53 | 36:10 | Ожидают замера |
| macOS | p2 | **85:06** | **85:28** | Ожидают замера |
| macOS | p3 | 62:08 | 62:33 | Ожидают замера |
| macOS | p4 | 75:54 | 76:13 | Ожидают замера |

Решение владельца задаёт до **120 с VT на корень на каждой ОС**, до **180 с cold wall** для отбора по singleton, до **4 GiB** на новую проверку и до **+5 мин wall** к сопоставимой критической партиции (macOS p2 **85:28 → 90:28**). Для Ubuntu при `jobs=2` ориентир до 10 GiB на группу с резервом ОС от 2 GiB. Для macOS ориентиры группы до 5 GiB и резерва от 1,25 GiB сформулированы при `jobs=1`. Штатный замер сохраняет bare `-j`, фактические параллельность и память учитывать по доступным данным. [Решение владельца](OWNER-DECISION-LIMITS-20261125.md) · [Сопоставимость штатного профиля](CAL2-MAC-RESULTS-ANALYSIS.md#сценарий-четырёх-партиций)

## Английские замены для описания PR

Фрагменты для рабочего текста PR. Исторические результаты CI и контролей относятся к своим деревьям и run ID. Формулировки general, stable, network и trait-методов сохраняются. [PR-752-BODY-UPDATE-20261123.md](/root/smallsort-pr-drafts/PR-752-BODY-UPDATE-20261123.md)

**Opening paragraph.** Replace the sentence beginning `245 harnesses pass` with the following.

> The updated candidate is expected to contain 247 ordinary SmallSort harnesses per OS. The baseline results and prior negative-control runs are documented below.

**Highlights.** Replace the coverage sentences in “Sorting correctness with a full-value oracle” after `the ordinary <` with the following.

> The general and stable routes are covered at `u8` and `u64` N0–N9. The direct insertion fallback is checked for lengths 0 through 7 on `u8` and `u64`, for key order and full-value multiplicities on normal return. N7 has a separate proof harness for each type. Network coverage includes sortedness at `u8` N0–N7 and N9–N13 and `u64` N0–N7 and N9, multiset preservation below the network width, and permutation of distinct tags at N9 and N13 for an arbitrary comparator.

**Challenge criteria and What is checked.** Replace the `Lengths` entry, the summary line, and the `Fallback insertion` row with the following.

```markdown
| Lengths | bounded as listed; correctness to N9 (general, stable), N13 (network sortedness), and N7 (direct fallback on `u8` and `u64`, with a separate N7 proof per type) |
<summary><b>What is checked</b> (247 ordinary SmallSort harnesses expected per OS, with <code>--no-assert-contracts</code>)</summary>
| Fallback insertion | 9 | `small_sort_fallback` | `u8`, `u64`; N0–N7, one N7 proof per type | key order and full-value multiplicities on normal return |
```

**Other head-relative wording.** In “Calibrated negative controls”, use `The prior runs and their results are listed under Negative controls.` for the final sentence. Under “Negative controls”, replace the `on this head` sentence with `The four trait-method controls failed their designated assertions in run 45068646559 (attempt 1) on 152f11556ab19c6dcfa21b5a0f1096603530ce67, which has the tree in 4728d6f456, with Kani 9834c96c.` In “Limitations”, replace `the other 174 use the original function` with `the other 176 are expected to use the original function in the updated inventory`. In “Source”, append the two N7 harnesses in candidate commit `a973479b9b55eb2a69527c95f82134d202a817c1` after the comment-only commit and update the library diff to 19 files, +4523/−0 against `b5adb2c5c9`. [Trait control run](pr752-trait-contracts-20261122/BINDING-ACCEPTANCE.md#run-and-property-reconciliation)

### Replacement CI section

The candidate uses the repository’s Kani workflow and pin `9834c96ce9`. The eight verifier jobs run four partitions each on Ubuntu and macOS, with object bits set to 12. Ubuntu uses `--jobs=2` and macOS uses `-j`. The runner lists the full std inventory, places standard harnesses before contract harnesses, and partitions the result into consecutive chunks of size `ceil(total/4)`.

The two new ordinary N7 harnesses are both expected in partition 2 on each OS. The expected SmallSort total is 247 per OS, pending CI.

| OS | Full std inventory per partition, baseline → expected | SmallSort per partition, baseline → expected | Existing selectors that move |
| --- | --- | --- | --- |
| Ubuntu | 552/552/552/550 → 552/552/552/552 | 0/184/0/61 → 0/186/0/61 | Two from p2 to p3 and two from p3 to p4 |
| macOS | 551/551/551/551 → 552/552/552/550 | 0/184/0/61 → 0/186/0/61 | One from p2 to p1 and one from p4 to p3 |

The upstream Kani workflow passed all eight verifier jobs on `dab03cf510df5c35141cde49f1368b1242f5035e`. Its longest job was macOS partition 2 at 85 min 28 s, including 85 min 06 s in the verification step. [Upstream run 45173593629, attempt 1](https://github.com/model-checking/verify-rust-std/actions/runs/45173593629)

The earlier fork dispatch on `1d2706e31f0cd909bd784fa43adf9a1d55be8469` passed all 16 jobs, including the eight verifier jobs, autoharness, metrics and Build JSON from logs. That run recorded 245 successful SmallSort harnesses and 1,028 satisfied covers per OS. The total SmallSort verification time was 6,151 s on Ubuntu and 11,395 s on macOS, about 65% and 67% of the manual-harness totals. The longest SmallSort proof took 183 s on Ubuntu and 306 s on macOS. The longest partition job in that fork run took 84 minutes. The workflow does not enforce cover satisfaction. [Fork run 45140203972, attempt 1](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/45140203972)

On the earlier head `872d5a43380752786415bc00d2a12ce0e930cb37`, the fork dispatches for Rust Tests (`42363383857`), Flux (`42363389143`), RAPx (`42363394305`), KMIR (`42363399372`), VeriFast (`42363404755`), VeriFast (negative) (`42363410264`), GOTO Transcoder (`42363415347`), Book (`42363420522`) and Testable SIMD (`42363425836`) each succeeded in attempt 1. [GitHub Actions run metadata for that head](https://api.github.com/repos/Tiramisu-Cake/verify-rust-std/actions/runs?head_sha=872d5a43380752786415bc00d2a12ce0e930cb37&event=workflow_dispatch)

On a pull request, autoharness runs with the `run-autoharness` label. It also runs in the merge queue and on dispatch. We would appreciate the label on this PR.

## Подтверждение после handoff

1. w13 выполняет независимое diff-ревью. После отдельного GO координатор проводит ровно один fork run штатного `kani.yml` на точном дереве кандидата. При необходимости отдельного trigger его дерево должно совпасть с `d5911d205aefc9464b968da029c3dabb983064ee`. Во всех commit messages, включая trigger, использовать `pr752`, `kani5196`, `issue56` без `#` перед цифрой.
2. Зафиксировать run ID и attempt, аттестованные head SHA, tree и Kani pin, профиль, общий успех workflow и успех всех восьми verifier jobs. Сверить полный ordered discovery и реальные границы для обеих ОС с прогнозом. В каждой ОС должны быть ровно два новых ordinary selector, весь прежний набор и 247 `SUCCESSFUL` SmallSort harnesses. Opt-in регистрации остаются вне этого штатного списка.
3. Для обоих N7 записать доступные свидетельства порядка, кратностей и cover. Если terse вывод даёт только агрегат успеха, отметить предел наблюдения по каждой отсутствующей записи. Успех harness и отдельно наблюдаемый `SATISFIED` фиксируются раздельно.
4. Заполнить verify step, job wall и обе дельты по p1–p4 на каждой ОС, очередь отдельно. Записать VT и доступные пиковые измерения двух корней. При превышении рабочего лимита передать координатору точную ОС, партицию, корень при наличии, длительности и доступное ресурсное свидетельство. Владелец вычитывает текст и публикует после приёмки подтверждающего прогона. [Процедура GO](pr752-trait-contracts-20261122/PLAN.md#go-на-один-dispatch-fork-ci)
