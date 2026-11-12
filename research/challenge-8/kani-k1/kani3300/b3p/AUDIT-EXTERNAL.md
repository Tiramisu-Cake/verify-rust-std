# KANI B3P: внешний аудит кода и текста PR

Дата: 2026-11-12.

**Вердикт:** как узкий багфикс PR состоятелен, но до отправки нужно исправить один дефект в самом коде (вероятный ICE) и честнее очертить границы фикса.

## Что проверялось

- Текст PR: `PR-UPSTREAM.md` на research-коммите `d26f926b61fd59b589e1fd58792bd0d227a0217b`.
- Код: Kani-коммит `83a413f9be2d57389c991d9f5d1250b4e4386203` (ветка `fix/zst-union-codegen-v2`, один коммит от `bf9c58e662`).
- Исходник CBMC 6.11.0, `src/util/simplify_utils.cpp` (тег `cbmc-6.11.0`).

## Ограничения аудита

- Аудит статический: Kani не собирался и не запускался. Находки A и B получены чтением кода и требуют прогона.
- Страница CI-прогона `43184599218` не открылась (rate limit), поэтому заявления текста PR о результатах CI не проверены.
- Содержимое issues #5085 и #4854 не проверялось.

## 1. Что решает код и соответствует ли текст

Код решает ровно одно: в `codegen_union`, в padded-обёртке `{payload, padding}`, payload нулевой ширины заменяется на пустой `Unit`. Логический тип arm'а в `unionfield` остаётся прежним, ширины не меняются.

Причина в тексте PR названа верно. В CBMC 6.11.0 `bits2expr` на строке 345 файла `simplify_utils.cpp` требует ширину элемента массива больше нуля (`CHECK_RETURN(el_size_opt.has_value() && *el_size_opt > 0)`), а пустую структуру собирает без проблем.

Текст в целом честный: семь harness'ов совпадают с кодом, деление «4 падают на base, 3 контрольных» согласуется с причиной (падают только arm'ы-массивы). Расхождения:

- **«Widths still come from the rustc layout»** верно для ширин, но само решение «ZST или нет» принимается по goto-типу (`sizeof_in_bits`), а не по layout.
- **Нет `Resolves #…`**, хотя шаблон PR в Kani (`.github/PULL_REQUEST_TEMPLATE.md`) этого требует. Issue на этот баг, судя по тексту, не заведён.
- **«macOS 14 runner is not available on the fork»** вызывает сомнение: `macos-14` — стандартный hosted-раннер. Нужно проверить, что job не был отменён или не завис, и описать как есть.

## 2. Пробелы

### A. Вероятный ICE из-за `sizeof_in_bits` (блокер)

Теперь для каждого padded arm'а вызывается `ty.sizeof_in_bits(&ctx.symbol_table)`. Цепочка по коду:

1. `ensure_struct` сначала вставляет в таблицу символов `IncompleteStruct`, потом вызывает замыкание с полями.
2. Pointee указателя кодогенерируется жадно (`codegen_ty(pointee_type).to_pointer()`), то есть union под указателем строится, пока внешняя структура ещё неполная.
3. `Type::sizeof_in_bits` на `StructTag` делает lookup и на `IncompleteStruct` уходит в `unreachable!("IncompleteStruct doesn't have a sizeof")`.

Поэтому ожидается паника компилятора на валидном Rust, который на base компилировался:

```rust
struct Node {
    next: *const U,
}

union U {
    big: [u8; 16],
    small: Node,
}

#[kani::proof]
fn recursive_arm() {
    let _n = Node { next: std::ptr::null() };
}
```

Вариант с ZST-arm'ом, ближе к теме PR:

```rust
#[repr(C)]
struct Node2 {
    next: *const Link,
}

#[repr(C)]
union Link {
    bytes: [u8; 8],
    marker: [Node2; 0],
}

#[kani::proof]
fn recursive_zst_arm() {
    let _n = Node2 { next: std::ptr::null() };
}
```

Важно, чтобы кодогенерация началась со структуры, а не с union, поэтому harness упоминает только `Node`.

Лечится просто: размер из layout уже посчитан в `fields_info` (`ty_size`), его нужно донести до места решения. Набросок (не компилировался):

```rust
let fields_info: Vec<(String, Type, u64, bool)> = def.variants().raw[0]
    .fields
    .iter()
    .map(|f| {
        let ty = rustc_internal::stable(f.ty(ctx.tcx, subst).skip_normalization());
        let ty_size = ty.layout().unwrap().shape().size.bits();
        let padding_size = union_size - ty_size;
        (f.name.to_string(), ctx.codegen_ty_stable(ty), padding_size as u64, ty_size == 0)
    })
    .collect();
// ...
let payload = if *is_zst { ctx.codegen_ty_unit() } else { ty.clone() };
```

Эквивалентная проверка без нового поля: `*padding == union_size`. После этого фраза текста PR про layout станет точной.

### B. Фикс закрывает только полностью нулевой arm

`bits2expr` рекурсивно обходит компоненты любой структуры, а Kani оставляет ZST-поля в структурах (`codegen_struct_fields`). Поэтому arm ненулевой ширины с ZST-массивом внутри, скорее всего, падает и после фикса:

```rust
#[repr(C)]
#[derive(Clone, Copy)]
struct Tail {
    b: u8,
    z: [(); 2],
}

#[repr(C)]
union U2 {
    bytes: [u8; 8],
    tail: Tail,
}
```

То же вероятно для arm'а без padding (например, `(u64, [(); 2])` первым полем) и вообще вне union (класс #5085). Нужно прогнать и записать результат в ограничения PR. Иначе ревьюер найдёт это сам.

### C. Тесты

- **Порядок полей.** Нет случая, где ZST-arm объявлен первым. Ветка `ID_union` в `bits2expr` перебирает компоненты по порядку и берёт первый подходящий, так что это отдельный путь.
- **Вложенные формы.** Нет `[[(); 2]; 3]`, `[[u8; 0]; 2]`, `[Z; 2]` с выравниванием и ZST-структуры, оборачивающей массив.
- **Невакуумность.** `expected` проверяет только успех. Стоит добавить `kani::cover!` или одну ожидаемо падающую проверку.

### D. Текст PR

- **Прецедент.** После фикса ZST-arm получает ту же форму `{Unit, padding}`, что у `uninit: ()` в любом `MaybeUninit<T>` (`()` кодогенерируется через `codegen_ty_unit`). Это сильный аргумент в пользу безопасности, его стоит добавить одной фразой.
- **Workaround.** Стоит сказать прямо, что это обход на стороне Kani, а корень в `bits2expr`. Завести issue в diffblue/cbmc и сослаться на него: это снимет вопрос «почему не чинить в общем виде».
- **Другие проверки.** Упомянут только Kani CI. Нужно убедиться, что прошли `format-check` и `verify-std-check`.

## 3. Годится ли на самостоятельный PR

Да: изменение маленькое, семантику не меняет (нулевой payload не несёт битов) и идёт с регрессионным тестом. Но в нынешнем виде отправлять не стоит. Минимум до отправки:

1. Заменить `sizeof_in_bits` на размер из layout и добавить рекурсивный тест из пункта A.
2. Прогнать случай B и описать результат в ограничениях.
3. Завести issue в Kani и поставить `Resolves #N`.
4. Сделать rebase на свежий `main` и проверить, нет ли уже открытого PR на `codegen_union`.

Тесты из пункта C желательны, но не блокируют.
