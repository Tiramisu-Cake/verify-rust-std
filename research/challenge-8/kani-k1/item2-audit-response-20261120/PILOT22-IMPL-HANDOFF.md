# Pilot 22. Локальный handoff компактного Check merge N32

Пакет содержит два последовательных exact root для проверки эквивалентности observer и Check полного merge при local cap 6 GiB. Frozen request имеет `status=READY`, `go=NOT_GRANTED`, `proof_credit=NONE`. Пакет остаётся `RESEARCH_ONLY`. Для dispatch нужны review и отдельный GO. [Задание](PILOT22-IMPL-TASK.md) · [Frozen request](/root/kani-ch8-q-pilot-control-v22/ch8-q-pilot-control/CI-REQUEST.json)

## Пины и деревья

| Объект | Commit | Tree |
| --- | --- | --- |
| g0 задания | `922a4742596f731b355d72df318ad83bea1f7ad1` | `eb27065def420271d5c85a3f1b8a9d1da5b69c9a` |
| g0 перед handoff | `d4bf8b583cfe4863fd1bf774f900c4fd32960dc4` | `8d925785536be584e4afa391a91916a43af08c3e` |
| База и единственный parent Std | `e2bd3c6adc870729794a6b2fe44eece988402d8f` | `7e62553ab80d6178ce8f01c8212e084b2186e308` |
| Std 22 | `54123e752d38702383b5a3b59b3cfd4bf016eca1` | `56cbabfdb81dec22c09be8c2af70d0a9416b98b5` |
| База содержимого Control 21B | `d62b75ddd9cbc4e4fa5366f1ae225833d71f52f3` | `324123d4ea2c0c961b3bab36987de147913ade90` |
| Единственный parent Control 22 | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` | `53b372008b70704b15a404275f81fa078ed50034` |
| Control 22 | `6518a69cbe3cd70c03cea07ae64305aeba5104fb` | `54c750649f32e839c8222c46e05c30039746f9b5` |
| Tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |

- Std подготовлен в `/root/verify-rust-std-ch8-q-pilot-v1` на `experiment/ch8-q-pilot-v1`. Diff к parent ограничен `verify/sorting_q_merge_model.rs` и `verify/sorting_q_merge.rs`. `smallsort.rs`, fixture `mw_merge_n32` и все прежние harness в `sorting_q_merge.rs` побайтно совпадают с базой.
- Control подготовлен в `/root/kani-ch8-q-pilot-control-v22` на `experiment/ch8-q-pilot-control-v22`. Diff к 21B содержит `CI-REQUEST.json`, `run.py`, `test_run.py`. Diff к `ba32286ee4` также содержит унаследованный workflow, побайтно равный workflow 21B. Event ref `refs/heads/uninit-ci/ch8-q-pilot-v1`. Название шага «Run seven q-pilot roots» унаследовано из workflow. Фактический порядок и число корней задаёт frozen roster.

| Файл | SHA-256 |
| --- | --- |
| `sorting_q_merge_model.rs` | `1dd547e928c9915894739f4c2359d838dea969607bda2ae7850e92a436a44a4e` |
| `sorting_q_merge.rs` | `3ee90d73c6a87fe9ade213093a363d51b4e393e3984ae4c489c4af8843a79695` |
| `smallsort.rs` | `bd4eb6faffe3992d26c282553b01b4008c88cfe75e820f622c40e4d50bde408a` |
| `CI-REQUEST.json` | `0099baa398885b9b229274610406353fa90b472f19901d010dfbe0bc2d6d3827` |
| `run.py` | `e7ddb0bbd54a17b8cfa42c5816400db786761d69ee3b0712db59d318ee45fd2a` |
| `test_run.py` | `7a4f7cfd7435f64942c8af1c065f79f0c767e506e1b110405cc3796b0caddd4a` |
| `.github/workflows/ch8-q-pilot.yml` | `fce4f840b1300c90ac808883bf4d03678348c34f770c39ef6c3f51284ecc058f` |

## Observer и контракт

Под `kani_smallsort_q_compact_merge32` и при `len == 32` общий source-only `merge_capture` сохраняет `q`, длину и `Below(u8)`. Счётчик суммирует 32 предиката `byte < q`. Post после общих проверок q, допустимой длины и readable dst сверяет `(byte < q) == (i < below)` для всех 32 позиций через `&=`. Индекс проходит 0–31, счётчик лежит в 0–32. При выключенном cfg и на длинах 20–31 используется прежняя маска с индексом 0 в младшем бите. Для `below=0` целевая маска равна `u32::MAX`, для `below=32` равна нулю. [Observer](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge_model.rs:593)

Обе ветви используют общие domain/geometry и guard перед чтением dst. Активный wide-контракт имеет один Kani `ensures` с `old(merge_capture(v, is_less))`, где `is_less` передаётся через `&mut F`. Возвращаемое значение `Option<MergeSnapshot>` реализует `Clone`. `MergeSnapshot` и его `MergeTarget` выводят `Clone, Copy`.

`mw_merge_n32_observer_equiv` вызывает те же четыре функции capture/post, которыми пользуются ветви observer. Они получают одни и те же произвольные initialized `[u8; 32]` для входа и выхода и независимый произвольный `q`. В harness отсутствуют assumes и вызовы merge. Сравниваются булевы результаты. Три covers проверяют достижимость `below=0`, `below=32` и смешанного входа с неверным output.

`mw_merge_n32` сохраняет `u8/KeyLess<u8>`, backing V34 и `v[1..33]`, numeric Pre на двух половинах по 16, отдельный `MaybeUninit<[u8; 32]>` scratch с offset 0, `modifies` всей области scratch, actual 16 up/down пар, ord-guard, q-frame и V34 source-frame. [Fixture и harness](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort/verify/sorting_q_merge.rs:1801)

## Frozen roster и exact argv

Полный selector образуется из `slice::sort::shared::smallsort::verify::sorting_q_merge::` и suffix из таблицы. Обе строки используют CaDiCaL по умолчанию pinned tool, OB11, OFF, unwind36, пустые ordinary и verified stubs. Ожидаемый terminal outcome обоих корней `SUCCESS`.

| Порядок | Root ID | Selector suffix | Роль | Child, с | Latest start до cutoff, с | Covers |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | `MW-MERGE-N32-OBSERVER-EQUIV` | `mw_merge_n32_observer_equiv` | Plain Proof | 180 | 210 | 3 |
| 2 | `MW-MERGE-N32-COMPACT-OB11` | `mw_merge_n32` | Check `bidirectional_merge` | 600 | 630 | 8 |

В equivalence ожидаются `MW_MERGE_N32_OBSERVER_BELOW0`, `MW_MERGE_N32_OBSERVER_BELOW32` и `MW_MERGE_N32_OBSERVER_MIXED_BAD_OUTPUT`. В Check ожидаются `MW_MERGE_Q_ZERO`, `MW_MERGE_Q_MAX`, `MW_MERGE_SPLIT_Q`, `MW_MERGE_CROSS_HALF_TIE`, `MW_MERGE_Q_ABSENT`, `MW_MERGE_N32_BELOW32`, `MW_MERGE_N32_BELOW0` и `MW_MERGE_N32_USEFUL_RETURN`.

Обе строки получают профиль `compact_merge32` в `RUSTFLAGS`.

```text
--cfg=kani_smallsort_sorting --cfg=kani_smallsort_q_pilot --cfg=kani_smallsort_q_merge --cfg=kani_smallsort_q_merge_b --cfg=kani_smallsort_q_merge_sort9 --cfg=kani_smallsort_q_merge_wide --cfg=kani_smallsort_q_compact_merge32
```

Runner подставляет в argv `{selector}` и `{timeout_seconds}` из таблицы, `{tool_script}` из pinned Tool (`scripts/kani`), `{std_library}` из pinned Std (`library`), а `{export}` и `{kani_target}` из отдельного рабочего каталога каждого root. `CARGO_TARGET_DIR` также отдельный для каждого root. Дополнительные CBMC args пусты.

```text
{tool_script} verify-std -Z unstable-options -Z function-contracts -Z mem-predicates
-Z float-lib -Z c-ffi -Z stubbing --no-assert-contracts --jobs=1 --harness {selector}
--exact --default-unwind 36 --harness-timeout {timeout_seconds}s --output-format=regular
-Z export-json --export-json {export} --target-dir {kani_target} {std_library}
--cbmc-args --object-bits 11
```

Child-бюджет составляет 780 с, job 10 800 с, setup/build 1 800 с и финализация 540 с. Headroom на запуск root составляет 30 с. Local 6 291 456 KiB, outer 12 582 912 KiB, reserve 2 097 152 KiB. Сохраняются bounded captures 21B, 16/1/8 MiB stdout/stderr/export на root и 512 MiB aggregate, включая index. Для двух корней лимит capture members составляет 50 MiB.

## Локальная валидация

- Scoped diff и `git diff --check` прошли для Std относительно parent и для Control относительно parent и базы содержимого. Сверены byte identity прежних fixture/consumer/control harness и `smallsort.rs`, общий preamble модели и post guard, одно активное `ensures`, `Clone`, roster, полный argv и унаследованные лимиты.
- `python3 run.py validate` прошёл с синтетическими GitHub metadata. `python3 run.py check-source --std … --tool …` прошёл на чистых exact checkout Std и Tool, включая все восемь SHA-256 Std. `python3 -m unittest -v test_run.py` прошёл 14/14, включая frozen roster, effective cap, bounded captures и error paths.
- `rustfmt 1.12.0-nightly (65ce8611fe 2026-11-18)` с `--check --edition 2024 --config skip_children=true,use_small_heuristics=Max --unstable-features` прошёл на изменённых блоках. Полные `sorting_q_merge.rs` и `sorting_q_merge_model.rs` выдают соответственно 30 и 4 замечания базы. После нормализации путей и координат вывод для каждого файла совпадает с базой.

## Критерий допуска после отдельного GO

Для связи компактного Check с прежним Replace N32 нужны `SUCCESS` обоих root, три covers эквивалентности, 8/8 covers Check, native ensures/DFCC/safety, успешный unwind, q/source-frame и сверка active clauses, pins, actual copy-back и q-post/control N32 из 21B. При оценке 6 GiB сопоставить с 21B и 16 effective cap, sampled child PGID peak, фазу, первую CNF и child/VT. При повторном cutoff или timeout дальнейший вариант из задания требует решения владельца на исходный `mw_merge_n32` в полосе 6,5 GiB. [21B](run-44919643424/SUMMARY.md) · [16](run-44890498157/SUMMARY.md) · [Правило допуска](GROUPED-PROPERTY-DECISION.md#правило-допуска)

Формальная компиляция, proof outcomes и fit Pilot 22 ожидают запуска после GO. Push, CI и операции с trigger ref в этой стадии отсутствуют.
