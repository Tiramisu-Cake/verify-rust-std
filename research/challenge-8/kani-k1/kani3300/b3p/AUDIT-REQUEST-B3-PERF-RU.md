# B3 (Kani: padded unions с ZST-полем) — perf после переноса на новый upstream. Отчёт для аудитора

2026-11-15. Подготовил координатор. CI — только форк Tiramisu-Cake/kani (GitHub Actions); локальных сборок нет.
PR в upstream не подан. Текст PR: t0 `kani3300/b3p/PR-UPSTREAM.md` (da703d8310).

## 1. Коротко

- Версии v1–v3 B3 (база upstream до `bf9c58e662` включительно): perf-задача Kani CI **зелёная** в каждом полном CI.
- Upstream main сдвинулся (13 коммитов 12–13 ноября). B3 перенесён без изменений кода на `0aac16ef62` → v4 `3d9a180938`.
- На v4 perf **ни разу не прошёл штатно**: 3 из 3 потерь раннера (лог не сохраняется), а в прогоне со сторожем памяти
  `s2n-quic-core` уронил свободную память до 833 МБ, сторож убил CBMC, тест FAILED.
- Чистый upstream `0aac16ef62` в тех же условиях: perf прошёл 2 из 2.
- Ранее сделанный вывод «perf у предела памяти, B3 не влияет» (по совпадению формул s2n-quic-core) **отозван** как
  недостаточный: прямое сравнение показывает различие B3 v4 и main, причина не установлена.

## 2. Версии B3

| Версия | Коммит (fork) | База upstream | Изменение кода `typ.rs` | Почему новая версия |
|---|---|---|---|---|
| v1 | `6db3c4dabd` (3 коммита) | `bf9c58e662`¹ | ZST-payload в padded union-arm → пустая struct; условие `ty.sizeof_in_bits(..) == 0` | первая версия |
| v2 | `83a413f9be` | `bf9c58e662` | то же, сжато в 1 коммит | упаковка для PR |
| v3 | `6e9e782024` | `bf9c58e662` | условие заменено на `*padding == union_size` (rustc layout), без обхода GOTO-типов; +тесты recursive/edge | внешний аудит t0 e6fb9eb7ec: A — `sizeof_in_bits` → ICE на рекурсивных типах; B — ZST внутри ненулевого arm; C — тесты |
| v4 | `3d9a180938` | `0aac16ef62` | **идентичен v3**, отличается только комментарий (ссылка на diffblue/cbmc#9487) | upstream ушёл вперёд; перенос, чтобы PR был на актуальном main |

¹ v1: родитель цепочки — `bf9c58e66`.
Проверка v3↔v4: `diff` двух патчей (без index/номеров строк) — отличаются только 3 строки комментария.
Баг воспроизводится и на новом main: тесты B3 без фикса на `0aac16ef62` дают CBMC `Invariant check failed` (run 43626647584).

Итоговое изменение кода v4 (`codegen_union`, typ.rs):

```rust
ctx.ensure_struct(struct_name, pretty_struct_name, |ctx, _| {
    let payload = if *padding == union_size as u64 { ctx.codegen_ty_unit() } else { ty.clone() };
    vec![DatatypeComponent::field(name, payload), pad.clone()]
})
```

## 3. Что сдвинулось в upstream (`bf9c58e662..0aac16ef62`, 13 коммитов, 131 файл)

#5058 aliasing UB в async executor; #5152 tail calls → unsupported; #5138 macOS-14→15 в CI; #5153 `default` в contract
attributes; #5063 `determine_targets`; #5012 serde-saphyr в compiletest; #5066 ICE discriminant niche > u64::MAX;
#5092 парсинг `--show-properties`; #5134 loop contracts в match arms; **#5057 value-validity для initialization stores
и field projections**; **#5093 contract clause depth без saturating**; **#5115 atomic store reads и initialization
tracking**; #5154 e2e тесты RFC 0015.
В codegen (`kani-compiler/src/codegen_cprover_gotoc`) из них изменены только `intrinsic.rs` и `rvalue.rs` (+9/−14).
Какой из них взаимодействует с B3 — не исследовано.

## 4. Perf по прогонам (ubuntu-24.04, 16 ГБ; perf-задача из upstream `kani.yml`)

| Run | Код | Perf |
|---|---|---|
| 43117729467 | v1 `6db3c4dabd` | success (45 мин) |
| 43184599218 | v2 `83a413f9be` | success (40 мин) |
| 43239475977 | v3 `6e9e782024` | success (44 мин) |
| 43605511755 попытка 1 | v4 `3d9a180938` | раннер потерян (73 мин) |
| 43605511755 попытка 2 | v4 | раннер потерян (73 мин) |
| 43620855491 | v4 + сторож памяти (<1500 МБ → kill CBMC) | `s2n-quic-core` FAILED (CBMC убит при 833 МБ свободно, t≈1640 с); остальные 14 ok |
| 43628958916 | main `0aac16ef62` | success (42 мин) |
| 43683645492 | v4, perf-задача upstream + лог памяти раз в минуту | раннер потерян (73 мин); лог не сохранён |
| 43683645556 | main `0aac16ef62`, то же | success (43 мин), 15/15; минимум свободной памяти 1805 МБ (s2n-quic-core, CBMC ≈6.9 ГБ); display_trait — CBMC до 10.6 ГБ, свободно 4.4 ГБ |

Примечания. В v1–v3 perf был по одному разу на версию (перезапуски касались других задач). Задачи «потерян раннер» —
аннотация GitHub «The hosted runner lost communication with the server… starves it for CPU/Memory».

## 5. Уже сделанная диагностика s2n-quic-core

Runs 43634544624 (main) / 43634541874 (B3 v4), сборка как в perf, `--output-format old`, свой сторож памяти:
у всех 40 harness одинаковые size of program expression и вердикты; у 10, решённых in-process, одинаковые числа
переменных и клауз (остальные — внешний SAT-решатель, чисел нет); `sync::spsc::tests::alloc_test` опускал свободную
память ниже 1 ГБ **в обоих**. Это не сравнивает пиковую память CBMC по harness и не покрывает GOTO-модель целиком.

## 6. Что не установлено / вопросы аудитору

1. Даёт ли B3 v4 на `0aac16ef62` бо́льшую пиковую память (или время) в `s2n-quic-core` или ином perf-тесте, и в каком harness.
   Сравнения пиковой памяти по harness main↔v4 нет.
2. Почему v3 на старой базе проходил perf, а тот же код на новой — нет: взаимодействие с #5115/#5057 (initialization
   tracking / value-validity) или иным коммитом, либо случайность. На старой базе каждая версия мерилась один раз.
3. Затрагивает ли условие `*padding == union_size` arm-ы, которые раньше не менялись (например `uninit: ()` в
   `MaybeUninit<T>`), и меняет ли это GOTO-типы/символы в perf-крейтах. Гипотеза, не проверено.
4. Достаточно ли для подачи draft текущего текста PR про perf (сейчас в нём утверждение о «тех же формулах» —
   его нужно переписать).

Предлагаемая следующая диагностика (не запускалась, ждёт решения): парный прогон v4/main со сторожем памяти и
пиковой RSS CBMC по каждому perf-тесту и harness; затем, при различии, — v3 на старой базе тем же способом и бисекция
13 upstream-коммитов под B3.
