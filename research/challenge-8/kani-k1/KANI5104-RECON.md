# Kani #5104: статическая разведка

Дата: 2026-11-15. Объём: issue и все комментарии через GitHub plugin; чтение локального Kani/CBMC source. Никакие сборки, `cargo`, `rustc`, Kani, CBMC, Miri или CI не запускались. Этот файл фиксирует гипотезы, а не устанавливает root cause.

## Краткий вывод

- #5104 — открытый issue с метками `[C] Bug` и `T-High Priority`: [официальный issue](https://github.com/model-checking/kani/issues/5104). Автор сообщает ложные assertion failures для чтения через указатель, выбранный условием, когда pointee — `[u8; 1]`; аналогичный `u8`-контроль проходит. В standalone примере `select_unpredictable` и обычный `if` оба падают; перестановка символических индексов проходит. Автор прямо говорит, что компонент не установлен и false `SUCCESS` не показан.
- Комментарий с реальным `core::slice::sort::shared::smallsort::swap_if_less` сообщает сбои для `[u8; 1]` и `[u8; 17]`, успех для `u8` и для замены на `ptr::swap`. По вердиктам первое несовпадение появляется после `ptr::read(v_b_swap)`, но trace не изучался. Это source-reported результат, не независимая проверка: [comment 1](https://github.com/model-checking/kani/issues/5104#issuecomment-6606222923).
- Второй комментарий сообщает похожие сбои при байтовом чтении через указатели из `each_mut`/`map`/`from_fn`. Его compact trace отображает выбранный адрес как `rows!0@1[1] + 5`, а значение — как байт `rows[0]`; в текстовом описании trace показан шаг записи `rows[0][5]`, но не шаг `rows[1][5]`. Это **не доказывает**, что соответствующая запись отсутствовала в Kani GOTO: агрегатная инициализация, свёртка констант, trace omission или slicing могут скрыть отдельный шаг/литеральный store. Нужна проверка значения и адреса записи на каждом промежуточном представлении, а не подсчёт двух literal stores. Тот же C-шаблон проходит на CBMC 6.11.0; автор не воспроизвёл проблему без Kani. Это делает Kani lowering приоритетной границей для сравнения, но C-прохождение не исключает CBMC, поскольку C и Rust могут дать разные GOTO: [comment 2](https://github.com/model-checking/kani/issues/5104#issuecomment-6834737844).
- Статический просмотр не доказывает, что сбой относится к SEL1, Kani codegen либо CBMC. Уверенность в атрибуции компонента: **низкая**. Высокая уверенность только в границах SEL1 ниже и в том, что требуется сравнение промежуточных представлений.

## Что именно отделяет SEL1

Сверен точный diff Kani `69b13711e60a87458200833445d47488ab466344` → `39a6521bf1b042358801cf613fd340623f35f851` (SEL1; 70 файлов, включая тесты); отдельно просмотренный C2-S6 ref — `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`. Ниже утверждения относятся к этим refs, не к изменяемому checkout HEAD.

- SEL1-специфичная функция `select_unpredictable_fallback` в [`kani_middle/mod.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/kani_middle/mod.rs:161) сужает выбор fallback до core intrinsic с ожидаемой сигнатурой.
- Её локальный потребитель в обычном uninit call-transfer path проверяет sized/layout mask и протокол переноса shadow-памяти в [`uninit_visitor.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:64). Неподдержанный shadow transfer завершается explicit unsupported check.
- Ещё один потребитель — points-to analysis: он моделирует fallback-назначения как объединение referents обоих аргументов без условного ребра и без адреса caller argument slots ([`points_to_analysis.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/kani_middle/points_to/points_to_analysis.rs:371)). Это анализ alias/reachability для инструментирования.
- Diff показывает, что SEL1 вынес ранее существовавшую проверку `!must_be_overridden() && has_body()` в общий `has_intrinsic_fallback`: до diff она уже применялась в Kani codegen и reachability, после diff эти участки вызывают общий helper. Новая SEL1-специфичная поддержка `select_unpredictable` относится к uninit pairing и points-to; нового обычного value-lowering она не добавляет. Поэтому перенос shadow сам по себе не исправляет значение выбранного `[u8; 1]`. В issue сбой воспроизводится без `-Z uninit-checks` и при обычном `if`: это основание вести #5104 отдельно, но не доказательство отсутствия косвенного влияния SEL1.

Для обычного пути чтения полезно просмотреть конкретные участки pinned Kani source:

- `codegen_projection` обрабатывает `Deref`, `Index`, `ConstantIndex` и создаёт GOTO выражения доступа/адреса: [`place.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/codegen_cprover_gotoc/codegen/place.rs:422), сборка MIR place — [`place.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/codegen_cprover_gotoc/codegen/place.rs:760).
- `codegen_rvalue_stable` задаёт lowering `Ref`/`AddressOf` и pointer casts: [`rvalue.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/codegen_cprover_gotoc/codegen/rvalue.rs:770). Обычные присваивания превращаются в GOTO `assign` из codegen места и rvalue: [`statement.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:319).
- Для `select_unpredictable` проверить именно resolved intrinsic call: общий fallback gate — [`statement.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:922); intrinsic-specific путь начинается в [`intrinsic.rs`](/root/kani-fix-3300-sel1/kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs:46). Контекст из MIR решит, попадает ли конкретный вызов туда либо компилируется как Rust fallback body.
- Сверка артефактов по driver: компилятор создаёт SymTabGoto artifact, который linker переводит в Goto в [`project.rs`](/root/kani-fix-3300-sel1/kani-driver/src/project.rs:156); последующие `goto-instrument` transformations идут через [`call_goto_instrument.rs`](/root/kani-fix-3300-sel1/kani-driver/src/call_goto_instrument.rs:34).

## Участки исполнения, которые стоит сопоставить

В CBMC checkout `/root/cbmc-fix-zst-bits2expr` текущий HEAD `9f2d01ec2bf115879c86e22203d403ba156d22e5`; тег `cbmc-6.11.0` — `820ff0f555b43fb78e0cd9332e498461bd14244b`. В просмотренном `value_set_dereference.cpp` diff между HEAD и тегом меняет только типы/литералы единиц (`mp_integer` → `bytest`); контрольная логика индексации и `byte_extract` ниже та же. Ссылка на [официальный файл в теге 6.11.0](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/pointer-analysis/value_set_dereference.cpp). Это сверка одного файла, не эквивалентность всего backend.

1. Kani MIR → GOTO: сравнить условный выбор/`select_unpredictable`, массивные локалы и доступы/присваивания через перечисленные `place.rs`, `rvalue.rs`, `statement.rs` функции. Следить за адресом и записанным байтовым значением каждой строки; корректная агрегатная инициализация может не выглядеть как два store.
2. CBMC pointer dereference: [`value_set_dereference.cpp`](/root/cbmc-fix-zst-bits2expr/src/pointer-analysis/value_set_dereference.cpp:611) пытается представить constant-offset array access как index; далее строит subexpression по offset и при необходимости извлекает байты. [`memory_model_bytes`](/root/cbmc-fix-zst-bits2expr/src/pointer-analysis/value_set_dereference.cpp:754) выбирает byte-array index или `byte_extract`. По диффу эти ветви семантически совпадают с тегом 6.11.0. Нужно установить, какой путь реально получает GOTO для reproducer; статическое наличие ветвей не указывает на дефект.
3. CBMC symbolic execution применяет GOTO stores/byte updates и формирует witness. C-пример отличается frontend/lowering и не изолирует этот этап.

## Reproducer и диагностическая минимизация

В issue указаны Kani 0.68.0 / CBMC 6.11.0 на двух pins: `9461e07af7ec929f050aa4192f29363c9be07779`
(nightly-2026-10-12) и `744b3e84d6eb68fd5456826997568666791bd355` (nightly-2026-10-23).
Одинаковый исходный отказ — 1/33, оба covers достигнуты; plain-if контроль — 1/28, scalar-u8 — 0/16.
Reported command, по одному root на invocation:

```text
cargo kani -Z unstable-options --output-format=terse --solver cadical --harness-timeout 3m --jobs=1 --harness check::arrayfactor_f7_witness_bytes1 --exact
```

Это данные issue, не команда к исполнению в этой стадии. В standalone crate из issue функция находится внутри
`#[cfg(kani)] mod check`. Ниже её тело с теми же двумя covers и ветвящимися assertions; `use` перенесён внутрь функции:

```rust
#[kani::proof]
#[kani::unwind(180)]
fn arrayfactor_f7_witness_bytes1() {
    use std::{hint, ptr};

    let x: [u8; 1] = [1];
    let y: [u8; 1] = [2];
    let mut v = [x, y];
    let c: bool = kani::any();
    let base = v.as_mut_ptr();
    // SAFETY: position 1 is in bounds of the two-element array.
    let s = hint::select_unpredictable(c, base, unsafe { base.add(1) });
    // SAFETY: `s` points to an initialized element of the live array.
    let got = unsafe { ptr::read(s) };
    let first_ok = got[0] == x[0];
    let second_ok = got[0] == y[0];
    kani::cover(c && x[0] != y[0], "arrayfactor F7: first selected, values differ");
    kani::cover(!c && x[0] != y[0], "arrayfactor F7: second selected, values differ");
    if c {
        kani::assert(first_ok, "arrayfactor F7: first selected value");
    } else {
        kani::assert(second_ok, "arrayfactor F7: second selected value");
    }
}
```

Issue сообщает, что на двух указанных Kani commits падает только `c == true` assertion; harness **не запускался нами**. Следующий вариант лишь **UNTESTED minimization candidate**: он меняет F7 на одну ожидаемую conditional assertion и убирает covers, чтобы проверить минимизацию после фиксации известного repro.

```rust
let x: [u8; 1] = [1];
let y: [u8; 1] = [2];
let mut v = [x, y];
let c: bool = kani::any();
let base = v.as_mut_ptr();
let p = core::hint::select_unpredictable(c, base, unsafe { base.add(1) });
let got = unsafe { core::ptr::read(p) };
assert_eq!(got[0], if c { x[0] } else { y[0] });
```

Сохранить точное условие, pointee type и проверку; отдельно сравнить исходный `if` pointer control. Следующий диагностический пакет должен менять по одному фактору: `[u8; 1]` ↔ `u8`; constant values ↔ `kani::any`; `base/add` ↔ literal element pointers; typed read ↔ byte-cast read; `select_unpredictable` ↔ `if`; непосредственная запись элементов ↔ `each_mut/map/from_fn`. Не добавлять все факторы в один крупный reproducer.

## Дискриминирующий план на будущее

1. На одном зафиксированном Kani/Rust/CBMC pin сохранить exact F7, его MIR и следующие артефакты: raw Kani `.symtab.out`/SymTabGoto, linked GOTO (в проекте `Goto` artifact), post-`goto-instrument` GOTO и symex trace. Отслеживать байтовые значения и адреса инициализирующих записей и чтения через все этапы. Не требовать двух явных store-инструкций: агрегатная инициализация, constant folding и trace/slicing могут менять или скрывать их форму.
2. В MIR и raw SymTabGoto выяснить фактическое lowering `select_unpredictable` — вызов Rust fallback или intrinsic lowering — и связать каждый MIR store/read с адресом/value в GOTO. Повторить для `if`, `u8` и символических индексов.
3. В linked и post-instrument GOTO убедиться, что адрес/condition выбора и данные в обоих элементах сохраняют требуемую связь. Затем по trace установить конкретный dereference address, memory object, offset/type и прочитанное значение. Только установленное расхождение между соседними этапами локализует виновника.
4. Если GOTO сохраняет ожидаемую семантику, подать его и C-контроль в один CBMC build/options и сопоставить dereference/array update/symex. Исходный C-pass полезен, но не исключает backend-проблему, пока GOTO не эквивалентен.
5. После этого повторить exact F7 на base и SEL1 pins при неизменном CBMC; затем, если нужно, менять только CBMC. Сравнивать значения/адреса на pinned артефактах, не только итоговый verdict.

Комментарий 2 также сообщает, что для `each_mut_pointers` не помогли `--no-slice-formula`, `--cbmc-args --no-array-field-sensitivity` и `--cbmc-args --object-bits 32`. Это только результаты автора, не независимые проверки и не доказательство исключения соответствующих механизмов.

## Предварительная оценка работ

- Подготовить exact reproducer и MIR/GOTO-снимки для четырёх контрольных форм: ориентир **0.5–1 человеко-дня**.
- Сопоставить Kani lowering и локализовать первый некорректный MIR→GOTO переход либо подтвердить семантически ожидаемый GOTO: **1–2 человеко-дня**.
- Если GOTO ожидаемый, минимизировать эквивалентный GOTO и исследовать CBMC dereference/array update path с владельцами компонента: **2–4 человеко-дня**.
- Исправление и regression coverage оценивать после локализации; заранее назначать компонент или размер патча оснований нет.

Это предварительная оценка трудозатрат на разведку/локализацию, а не календарное обещание и не срок исправления. Все runtime-проверки из перечисленных этапов на момент этой заметки **NOT RUN**.
