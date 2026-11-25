# pr752 · независимое diff-ревью fallback N7

**GO по diff кандидата `a973479b9b`.** Изменение готово к отдельному решению координатора о подтверждающем прогоне. Замечания относятся к точности формулировок PR, готовые замены приведены ниже. Успех обоих N7, достижимость cover и время штатных партиций кандидата ожидают измерения.

| Проверенный объект | Значение |
| --- | --- |
| Worktree / ref | `/root/verify-rust-std-rev2-pr752-n7-w11` / `refs/heads/work/rev2-pr752-n7-w11` |
| Commit / tree | `a973479b9b55eb2a69527c95f82134d202a817c1` / `d5911d205aefc9464b968da029c3dabb983064ee` |
| Единственный parent / tree | `dab03cf510df5c35141cde49f1368b1242f5035e` / `7fd542ad59723ff2beeacb9632fb0568e81b0655` |

Сверил Git-объекты и фактический diff по заданию из `9b325943b0`. Результаты собственной проверки исходников и пересчёта матрицы сопоставил с handoff из `e25ef550ec`. [Задание](REV2-PR752-N7-TASK.md) · [Handoff](REV2-PR752-N7-HANDOFF.md)

## Исходники

- Единственная дельта дерева — `+12/−0` в `library/core/src/slice/sort/shared/smallsort/verify/merge.rs`. Удаление двух добавленных блоков возвращает blob родителя побайтно. Семь прежних макровызовов N0–N6 на месте. Runtime, trait-контракты, `Cargo.toml`, workflow, скрипты и tool pin совпадают с родителем. Worktree кандидата чистый. [Diff в исходнике](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:561)
- У каждого N7 ровно два атрибута, `#[kani::proof]` и `#[kani::unwind(34)]`, и один вызов прежнего helper. Дополнительных `cfg`, `stub`, `stub_verified`, `assume`, диагностических вызовов и контролей в добавленных блоках нет. Оба корня доступны через существующий `cfg(kani)` → `verify` → `merge` при выключенном `kani_smallsort_controls`. Сохранились все 18 opt-in корней, из них 17 отрицательных и один проходящий frame-контроль. Сверка по файлам дала `fixed_inputs.rs` 1, `forwarding_contracts.rs` 2, `helper_contracts.rs` 4, `merge/profiles.rs` 5, `tag_permutation.rs` 1 и `trait_contracts.rs` 5. [Регистрация verify](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort.rs:1024) · [Модули](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify.rs:79) · [Проходящий контроль](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:318)
- `fallback_route_properties` выбирает произвольный инициализированный `[T; 7]`, копирует исходное состояние и передаёт весь массив в реальные `small_sort_fallback` → `insertion_sort_shift_left` с offset 1 → `insert_tail`. Тот же `lt_u8` или `lt_u64` с ключом `value >> 1` проверяет порядок соседних элементов после возврата. Прежний `set_value_probe::<T>()` выбирает probe независимо от массива. Oracle сравнивает число полных побайтовых совпадений до и после, что охватывает все значения `u8` и `u64`, включая младший бит. После обеих проверок остаётся cover `fallback route properties checked`. Область утверждения — порядок ключей и сохранение кратностей полных значений для этих входов при нормальном возврате. [Helper](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:399) · [Probe](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:24) · [Oracle](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort/verify/merge.rs:342) · [Fallback](/root/verify-rust-std-rev2-pr752-n7-w11/library/core/src/slice/sort/shared/smallsort.rs:255)

| Точный селектор (`--harness … --exact`) | Вид / unwind | Единственный вызов |
| --- | --- | --- |
| `slice::sort::shared::smallsort::verify::merge::fallback_sorted_permutation_u8_n7` | `Proof` / 34 | `fallback_route_properties::<u8, _, 7>(lt_u8)` |
| `slice::sort::shared::smallsort::verify::merge::fallback_sorted_permutation_u64_n7` | `Proof` / 34 | `fallback_route_properties::<u64, _, 7>(lt_u64)` |

## Повтор локальных проверок

Обе команды из worktree кандидата завершились с кодом 0 и пустым выводом. Edition взят из `library/core/Cargo.toml`, `skip_children=true` ограничивает rustfmt изменённым файлом.

```sh
git diff --check dab03cf510 a973479b9b
/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max,skip_children=true --check library/core/src/slice/sort/shared/smallsort/verify/merge.rs
```

Cargo, rustc, Kani, CBMC, CI и push в этом ревью не запускались.

## Прогноз партиций

В `kani.yml` восемь verifier jobs, по четыре партиции на Ubuntu и macOS. `run-kani.sh` берёт полный std inventory, последовательно объединяет `standard-harnesses` и `contract-harnesses`, режет по `ceil(total/4)` и передаёт точные имена. Штатные параметры совпадают с базой. Это Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, OB12, `--no-assert-contracts`, `--output-format=terse`, Ubuntu `--jobs=2`, macOS `-j`. [Workflow](/root/verify-rust-std-rev2-pr752-n7-w11/.github/workflows/kani.yml:26) · [Invocations](/root/verify-rust-std-rev2-pr752-n7-w11/scripts/run-kani.sh:191) · [Границы](/root/verify-rust-std-rev2-pr752-n7-w11/scripts/run-kani.sh:289) · [Пин](/root/verify-rust-std-rev2-pr752-n7-w11/tool_config/kani-version.toml:5)

Независимо пересчитал `base_ordered` из Ubuntu CAL1 `45281488869/1` и macOS CAL2 `45338903191/1`. Размеры и SHA-256 двух JSON совпали с их индексами, в индексах указаны проверенные SHA/tree родителя и pin. На обеих ОС существующие стандартные селекторы `verify/merge.rs` образуют один лексикографически упорядоченный блок. Вставка двух имён в этот блок сохраняет порядок всех старых записей. Ожидаемые позиции с единицы — 733 для `u64_n7`, 734 для `u8_n7`, обе в p2. В штатном наборе SmallSort прогнозируется **247 на ОС**, из них **186** в `standard-harnesses` и **61** в `contract-harnesses`. Порядок и числа относятся к прогнозу до discovery кандидата. [Ubuntu discovery](/root/ch8-artifacts/run-45281488869/ch8-cal1-Linux-X64-45281488869-1/discovery.json) · [macOS discovery](/root/ch8-artifacts/run-45338903191/ch8-cal2-macOS-ARM64-45338903191-1/discovery.json)

| ОС | Полный std p1–p4, база → прогноз | SmallSort p1–p4, база → прогноз | Перемещения существующих селекторов |
| --- | --- | --- | --- |
| Ubuntu | `552/552/552/550` → `552/552/552/552` | `0/184/0/61` → `0/186/0/61` | p2→p3 `mem::maybe_uninit::verify::check_zeroed_value_i128`, `mem::maybe_uninit::verify::check_zeroed_value_u32`. p3→p4 `ptr::const_ptr::verify::check_const_offset_from_u64`, `ptr::const_ptr::verify::check_const_offset_from_u64_arr`. |
| macOS | `551/551/551/551` → `552/552/552/550` | `0/184/0/61` → `0/186/0/61` | p2→p1 `num::nonzero::verify::nonzero_check_clamp_for_16`. p4→p3 `ptr::const_ptr::verify::check_const_offset_from_u64_arr`. |

Исторический baseline штатной матрицы привязан к `dab03cf510`, run `45173593629/1`. Критическая партиция macOS p2 заняла 85:28 job wall, из них 85:06 verify step. Исследовательский Ubuntu run `45358377716/1` замерял singleton на overlay `fb82da3c78`. Его 105,53 с суммарного VT, 158,21 с суммарного cold wall двух запусков и около 1,96 GiB пика группы на корень служат ориентиром для замера. Фактические VT и RSS кандидата, длительности партиций на обеих ОС и соблюдение лимитов владельца определяются по подтверждающему прогону. [Штатный baseline](CAL2-MAC-RESULTS-ANALYSIS.md#сценарий-четырёх-партиций) · [Singleton](REV2-FALLBACK-RESULTS-ANALYSIS.md#приёмка-двух-n7) · [Лимиты](OWNER-DECISION-LIMITS-20261125.md)

## Английский текст для PR

В handoff правильно указаны N0–N7, девять fallback harnesses и отдельный N7 на тип. Область oracle ограничена порядком ключей и полными кратностями при нормальном возврате. Текст не расширяет заявления про general, stable, network и trait-методы. Исторические 245 успешных harnesses и 1,028 covers привязаны к `1d2706e31f`, run `45140203972/1`. Четыре trait-контроля привязаны к `152f11556ab`, run `45068646559/1`. Сверка Git подтвердила совпадение его дерева с `4728d6f456`. Числа Source подтверждены diff к `b5adb2c5c9` по `library/` (19 файлов, `+4523/−0`). [Черновик PR](/root/smallsort-pr-drafts/PR-752-BODY-UPDATE-20261123.md) · [Исторический fork run](/root/smallsort-pr-drafts/PR-752-PUSH-20261123.md:22) · [Результаты trait-контролей](pr752-trait-contracts-20261122/BINDING-ACCEPTANCE.md#role-verdicts)

1. В Opening, заголовке `What is checked` и разделе CI заменить `247 ordinary SmallSort harnesses` на формулировку про штатный inventory. Слово `ordinary` здесь допускает прочтение как категория `standard-harnesses`, в которой ожидается 186 записей. Для Opening или CI подходит следующий текст.

   > The default CI inventory is expected to include 247 SmallSort harnesses per OS (186 standard and 61 contract harnesses). The two new standard N7 harnesses are expected in partition 2 on both OSes. The candidate’s CI results are pending.

   Для `What is checked` подходит `(247 SmallSort harnesses expected per OS with --no-assert-contracts)`, с `<code>` вокруг флага в HTML.

2. В Highlights явно описать свойства harnesses, пока подтверждение нового дерева впереди. Остальные предложения в Highlights и строки general, stable, network и trait-методов оставить в исходном объёме.

   > The direct insertion fallback harnesses cover lengths 0 through 7 for `u8` and `u64`, with a separate N7 harness for each type. They check key order and preservation of full-value multiplicities on normal return.

3. Для матрицы заменить `The eight verifier jobs run four partitions each on Ubuntu and macOS` на формулировку с одной партицией на job.

   > The workflow runs four verifier jobs on Ubuntu and four on macOS, one job per partition on each OS.

4. В Limitations про `panic_on_ord_violation` описать наличие stub, поскольку `use the original function` может читаться как достижение вызова. Сверка прямых атрибутов и макровызовов при выключенных контролях дала 71 корень с этим stub. Оба добавленных корня входят в группу без него.

   > Seventy-one harnesses replace `panic_on_ord_violation` with a stub that calls `assume(false)`. The other 176 harnesses in the expected CI inventory leave that function unstubbed. Comparator panics and panic unwinding are outside the stated coverage.

При подтверждении на точном tree сверяются реальные селекторы, успех восьми verifier jobs и 247 SmallSort successes на ОС. Успех harness, отдельные свидетельства для двух assertions и достижимость cover фиксируются по тому, что видно в штатном terse выводе. [Условия подтверждения](REV2-PR752-N7-TASK.md#локальная-проверка-handoff-и-подтверждение)
