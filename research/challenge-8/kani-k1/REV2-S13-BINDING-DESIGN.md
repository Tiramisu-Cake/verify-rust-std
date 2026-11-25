# REV2 · привязка 13-битной проверки к sort13_optimal

**Допуск exact S13/base1 — да при выполнении условий.** Полный байтовый leaf FIX3, привязка к 45 фактическим вызовам и битовый корень на том же теле дают путь к числовому порядку, сохранению кратностей и frame для произвольного инициализированного V34 при вызове `sort13_optimal(&mut v[1..14], &mut KeyLess::<u8>::with_q(q))`. Статическая часть готова. Для допуска нужны успешный нативный прогон с парным контролем и принятие внешнего порогового аргумента при независимом ревью.

**`stub_verified(sort13_optimal)` на `9834c96ce9` — этой связки недостаточно.** Нужен успешный `proof_for_contract(sort13_optimal)` на произвольных байтах с предусловиями, write set и числовым/q-постом, покрывающими точную геометрию каждого вызова потребителя. Битовый Proof и внешний перенос пока не включены в нативную проверку этого контракта.

`READY_FOR_INDEPENDENT_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`. Компиляция, discovery, нативные вердикты, covers и ресурсы двух новых корней остаются `UNKNOWN`.

## Что связывает Check листа с actual sort13

- База Std FIX3 `32129c149a15fb1b60a7314e738f3cb466d076e5`, дерево `1b0cc32c571b370178e64f2b8c79773d2ce27051`. Blob `smallsort.rs` `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` побайтно тот же у кандидата. В `sort13_optimal` guard `v.len() < 13` исключён длиной среза 13. `v_base` получают один раз из `v.as_mut_ptr()`. Затем исполняются 45 вызовов вида `swap_if_less(v_base, a, b, is_less)` в одном блоке, с одним и тем же `&mut KeyLess<u8>`. Между вызовами отсутствуют записи и развилки, влияющие на расписание. [Точное тело](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort.rs:597)
- Порядок пар ниже соответствует строкам 612–656. Для **каждой** пары `0 ≤ a < b < 13` проверено по литералам. Её targets — `v[1+a]` и `v[1+b]` исходного V34. Оба адреса получены из эксклюзивного среза `&mut v[1..14]`, входят в его доступный диапазон, смещения малы и выровнены для `u8`. Различные индексы дают непересекающиеся байты ненулевого размера. Это устанавливает нужные разрешения из reborrow среза, независимо от того, что leaf harness получает указатель посредством `backing.as_mut_ptr().add(1)`. Инициализация всех targets дана на входе, а после каждого шага сохраняется за счёт записи двух валидных байтов и frame других ячеек. `q` лежит в отдельном объекте компаратора. [Safety, modifies и тело листа](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort.rs:429)
- Exact selector FIX3 `slice::sort::shared::smallsort::verify::rev2_provider_cost::s13_swap_leaf` проверяет контракт реального `swap_if_less` без stubs. Его fixture охватывает любые инициализированные 34 байта, base1, все 78 ordered пар и независимый `q: u8`. Контракт сохраняет safety preconditions, добавляет точный тип `u8/KeyLess<u8>`, область пары и читаемость/записываемость двух targets. `modifies` разрешает запись только в эти targets. Пост проверяет полные `min/max` с неизменным q, harness повторно проверяет min/max и q и проверяет каждый из остальных 32 байтов. В actual листе `is_less(&*v_b, &*v_a)` выбирает два источника, `ptr::read` сохраняет второй байт во временное значение до обеих записей. При равенстве компаратор возвращает false, оба выходных значения совпадают с прежними. [Check и assertions](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:144) · [Компаратор](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)
- По зафиксированному разбору run `45661535099`, Ubuntu X64, лист получил `VERIFIED`, covers 6/6, 59,7 с cold wall / 32,7 с VT, 1,95 GiB группы / 0,34 GiB CBMC. Пины `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC 6.11.0, stock CaDiCaL, OB12, unwind 36, jobs=1, safety/overflow/unwind ON, uninit/validity OFF, `--no-assert-contracts`, три cfg FIX3. Это источник локального перехода с нужным профилем и доменом. У диагностического run `proof_credit=NONE`, независимый зачёт B1/B2 этим документом не присваивается. Сверка использовала сохранённые GO, Handoff и разбор FIX3. [GO FIX3](REV2-NETWORK-PROVIDERS-FIX3-GO.md) · [Handoff FIX3](REV2-NETWORK-PROVIDERS-HANDOFF.md) · [Результаты FIX3](REV2-NETWORK-PROVIDERS-RESULTS-ANALYSIS.md)

```text
01–06  (0,12) (1,10) (2,9) (3,7) (5,11) (6,8)
07–11  (1,6) (2,3) (4,11) (7,9) (8,10)
12–17  (0,4) (1,2) (3,6) (7,8) (9,10) (11,12)
18–21  (4,6) (5,9) (8,11) (10,12)
22–26  (0,5) (3,8) (4,7) (6,11) (9,10)
27–31  (0,1) (2,5) (6,9) (7,8) (10,11)
32–35  (1,3) (2,4) (5,6) (9,10)
36–39  (1,2) (3,4) (5,7) (6,8)
40–43  (2,3) (4,5) (6,7) (8,9)
44–45  (3,4) (5,6)
```

## Битовый корень и контроль

Оба корня вызывают actual `sort13_optimal` с actual `swap_if_less`. В младших 13 битах символического `u16` все комбинации свободны, бит 0 соответствует `v[1]`. Префикс `v[1..14]` заполняется этими битами как каноническими байтами `0/1`. Остальные 21 байт V34 и q остаются произвольными. При `k = input_mask.count_ones()` эталон `LOW_BITS ^ (LOW_BITS >> k)` содержит ровно k единиц при старших адресах. Вместе с отдельной проверкой каноничности равенство наблюдаемой маски эталону проверяет порядок и popcount.

| Роль | Exact selector | Ожидаемый итог |
| --- | --- | --- |
| S13/base1 | `slice::sort::shared::smallsort::verify::rev2_s13_binding::s13_base1_bits` | `VERIFIED` |
| Контроль S13/base1 | `slice::sort::shared::smallsort::verify::rev2_s13_binding::s13_base1_corrupt_mask` | Нативный `FAILURE` только у `REV2_S13_BASE1_SORTED_POPCOUNT` |

У обоих тот же `#[kani::proof]`, unwind 36 и общий helper с константным параметром. Контроль после вызова и проверки каноничности инвертирует младший бит **наблюдаемой** маски. Это меняет popcount на ±1 при любом выходе, равном эталону до порчи, в том числе для полностью нулевого и полностью единичного входа. V34 и компаратор остаются теми же. У обоих ожидаются успешные `REV2_S13_BASE1_Q_FRAME`, `REV2_S13_BASE1_V34_FRAME`, `REV2_S13_BASE1_CANONICAL_OUTPUT` и штатные safety/overflow/unwind. Ограничения через `assume` отсутствуют.

Ожидаемые достижимые covers у обоих — `REV2_S13_BASE1_MIXED_INPUT`, `REV2_S13_BASE1_INPUT_INVERSION`, `REV2_S13_BASE1_REACHED_POST` и `CAL1 q actual comparator executed`. Например, маска `1` даёт смешанный вход с инверсией. Проверять нативные ID и locations для всех экземпляров cover компаратора, которые выдаст verifier. Cover достижения поста стоит после реального вызова и frame/каноничности перед целевым assert. Ожидаемый отказ контроля привязывается к этому assert по ID, location и метке в регулярном результате и stock export. Ошибка setup/runner или отказ safety/unwind делает контроль непригодным. [Корни и метки](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_binding.rs:9)

В профиле `--no-assert-contracts` обычные контракты идут в `Original` на пине Kani. Здесь ни S13, ни swap не являются целью Check или Replace. Replace листа применим на уровне исходной геометрии и даёт точную пару min/max, но добавляет 45 исполнений requires/old/havoc/ensures и обходов реального компаратора. Cover компаратора в таком корне потребовал бы отдельного actual Check листа как свидетельства достижимости. Выбран прямой вызов: доступны и фактические записи, и cover компаратора, а входная формула потенциально упрощается до однобитных переходов. Извлечённое расписание используется ниже для вспомогательной статической сверки. Исполняемый корень связан с actual телом самим вызовом. Выбор режима сверен через `git -C /root/kani-upstream-ch8-s1 show 9834c96ce9:kani-compiler/src/kani_middle/transform/contracts.rs`, функция `contract_mode`. [Профиль FIX3](REV2-NETWORK-PROVIDERS-HANDOFF.md)

## Перенос на произвольные байты

1. Фиксируем произвольный инициализированный V34, точный срез и произвольный порог `q`. Пусть `B_q(x) = [x ≥ q]`. Для полных `u8` выполняются `B_q(min(x,y)) = B_q(x) & B_q(y)` и `B_q(max(x,y)) = B_q(x) | B_q(y)`. Первая формула требует, чтобы оба байта достигали порога, вторая — чтобы его достигал хотя бы один. При `x=y` оба бита одинаковы и остаются прежними.
2. Перед первым шагом все 13 байтов читаемы, записываемы и инициализированы. Для шага k применимость Check следует из геометрии соответствующей пары и инварианта. Два вывода min/max снова валидны и инициализированы, остальные байты, q и распределение доступной памяти прежние. Значит, условия входа выполнены и на следующем шаге. Упорядоченная пара пороговых битов совпадает с результатом того же actual шага на канонических 0/1. По индукции на 45 шагах проекция байтового выхода равна выводу битового корня на проекции входа. Frame всех 21 внешних байтов и q следует из локальных frames на каждом шаге.
3. `KeyLess<u8>::call_mut` вычисляет `a < b` по полным байтам, не читая q и не изменяя состояние. Guard и расписание также не читают q. Поэтому, меняя наблюдательный порог, мы рассматриваем одно и то же байтовое исполнение с одним результатом для фиксированного входа. Битовый пост должен выполняться для всех 8192 входов. Тогда каждая пороговая проекция результата упорядочена и сохраняет popcount.
4. Если в выходе на позициях `i<j` стоят `x>y`, при `q=x` получились бы биты `1,0`, что исключено. Пусть `C(q)` — число байтов `≥q` в 13 позициях. Для `t=0..254` кратность равна `C(t)-C(t+1)`, кратность 255 равна `C(255)`. `C(0)=13` до и после. Сохранение всех `C(q)` сохраняет все кратности и для любого q даёт старое число байтов `<q` как `13-C(q)`.

FIX3 сообщает машинную проверку байтового перехода и его локального frame на профиле листа. Будущий нативный прогон кандидата проверит реальные 0/1 исполнения, их frame, safety/unwind и составной битовый пост. Побайтная фиксация исходника и сверка вызовов дают статическую привязку. Индукция, применимость листа на каждом шаге (включая initialized targets при uninit OFF), независимость исполнения от q и вывод о числовом порядке/кратностях остаются внешним аргументом. Область вывода — exact N13/base1, initialized V34 и `u8/KeyLess<u8>`.

## Что нужно для native Replace

Цель — `proof_for_contract(sort13_optimal)`, уже зарегистрированная для exact S13/base1 как `slice::sort::shared::smallsort::verify::cal1::nm_sort13_left_len13`. Его fixture задаёт произвольные полные байты и q и проверяет frame V34. CAL1-контракт под `kani_smallsort_cal1` требует точную специализацию `u8/KeyLess<u8>`, длину среза 13–17, читаемость всего среза и записываемость первых 13. `modifies(v.as_mut_ptr().cast::<[T; 13]>())` ограничивает havoc и запись первыми 13 байтами в этой специализации. Хвост среза, байты вне среза и q лежат вне write set. Пост явно сохраняет q, требует числовой порядок и сохранение числа байтов `<q` для q этого вызова. За пределами префикса нужны такой write set и проверка байтового frame в точной геометрии harness/consumer. При необходимости полного мультимножества как **нативной** гарантии stub нужно усилить пост: havoc может дать разные массивы для разных q, и один q-пост не связывает их между запусками. [Аннотация](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort.rs:588) · [Модель CAL1](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs:41) · [Check](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1.rs:20)

В дереве FIX3 единственный `stub_verified(sort13_optimal)` — `cal1::compact_network_n25_actual_insert`. Из V34 передаётся `v[1..26]`, длина 25, поэтому левая половина `v[1..13]` имеет длину 12 и идёт в sort9. Правая `v[13..26]` имеет длину 13 и вызывает sort13 с **base13**. Потребителю нужна отдельная квалификация Check на этом правом вызове и на полном домене его байтов и q. Другие зарегистрированные Check S13 используют `v[1..18]` (длина 17) и `v[17..33]` (длина 16). Общий requires также допускает длины 14 и 15 и не фиксирует V34/base1. Каждое использование Replace нуждается в покрытии всей своей достижимой области. `VERIFIED` старого N25 измерял потребителя с Replace. Старый exact N13 Check на CAL2/OB11 завершился за 880,2 с VT и 8,94 GiB группы, а CAL2/OB12 достиг капа 10 GiB. FIX3 `s13_plain_byte` с Replace листа — отдельный Proof, отсечённый на 180 с. [Actual split](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort.rs:385) · [N25 consumer](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1.rs:122) · [CAL1](CAL1-RESULTS-ANALYSIS.md) · [CAL2](CAL2-RESULTS-ANALYSIS.md)

Для рабочего native ребра ещё нужен укладывающийся в профиль Check указанной функции на всей области выбранного потребителя или механизм, который заставит Kani проверять композицию листа, привязки и переноса внутри этого Check. На данном пине отдельный Proof на 0/1 не является целью `proof_for_contract(sort13_optimal)`, а внешний вывод не является проверенным телом её контракта. Объём кандидата остаётся в пределах exact S13/base1.

## Локальный кандидат и проверки

Worktree `/root/verify-rust-std-rev2-s13-binding-w14`, ветка `work/rev2-s13-binding-w14`.

| Объект | SHA |
| --- | --- |
| Parent FIX3 | `32129c149a15fb1b60a7314e738f3cb466d076e5` |
| Commit | `32c2857f4b7137601de54ea42a02610c8fd29ed9` |
| Tree | `0e682cfceaed5d33d3d3374b5dc97da5012bba93` |

Изменены только `library/core/Cargo.toml` (декларация cfg для lint), `library/core/src/slice/sort/shared/smallsort/verify.rs` (регистрация модуля) и новый `library/core/src/slice/sort/shared/smallsort/verify/rev2_s13_binding.rs` (два harness и общий helper). Новый opt-in `kani_smallsort_rev2_s13_binding` нужен дополнительно к трём cfg FIX3. При его отсутствии roster FIX3 остаётся прежним по статической сверке. Без `cfg(kani)` закрыт весь `verify`.

Отдельно сверена видимость новых имён:

- `mod rev2_s13_binding` объявлен в `verify.rs` и разрешается в одноимённый файл под `verify/`. Обе proof-функции приватны, как в соседних модулях. `LOW_BITS`, `check_s13_base1` и его параметр имеют локальную видимость. Полные пути следуют из `smallsort::verify::rev2_s13_binding` и имён функций. [Регистрация](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify.rs:97)
- `super::super::sort13_optimal` разрешается в приватную функцию предка `smallsort`, доступную его потомкам. `super::cal1_model::KeyLess` идёт в sibling, видимый внутри `verify`. Новый cfg требует `kani_smallsort_cal1`, под которым объявлен этот sibling. Сам `KeyLess` видим внутри `smallsort`, а `with_q` и `q` с `pub(super)` доступны потомкам `verify`. Эти пути совпадают с импортами FIX3. [Импорты FIX3](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:4) · [Видимость KeyLess](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:5)
- `crate::kani` создан вызовом `kani_core::kani_lib!(core)`. В локальном Git пина сверены re-export и `proof/unwind`, intrinsics `any/assert/cover`, `Arbitrary` для `u8`, `u16` и массивов. `u16::from(u8)` — стандартная widening-конверсия через prelude. `u16::count_ones` использует `ctpop`, для которого на пине есть codegen. Индексы проходов от 0 до 12, popcount от 0 до 13, все сдвиги укладываются в 16 бит. [Core integration](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/lib.rs:367) · [Метод count_ones](/root/verify-rust-std-rev2-s13-binding-w14/library/core/src/num/uint_macros.rs:161)

Из worktree кандидата следующие проверки прошли. `skip_children` ограничивает rustfmt двумя затронутыми файлами. `reorder_modules=false` оставляет унаследованный порядок объявлений FIX3.

```bash
cd /root/verify-rust-std-rev2-s13-binding-w14
verify=library/core/src/slice/sort/shared/smallsort/verify
/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --check --edition 2024 \
  --config use_small_heuristics=Max --config skip_children=true,reorder_modules=false \
  "${verify}.rs" "$verify/rev2_s13_binding.rs"
git diff HEAD^ HEAD --check
git diff --exit-code HEAD^ HEAD -- library/core/src/slice/sort/shared/smallsort.rs
```

Следующая сверка (Python 3.11+) проверяет разрешённые пути diff, байты FIX3, статическое cfg-off, guard, базовый указатель, компаратор и ровно 45 вызовов. Извлечённый порядок сравнивается с таблицей FIX3 и перебирается как булева схема. Перебор проверяет модель по исходнику и формулу маски, без компиляции harness.

```bash
python3 - <<'PY'
from pathlib import Path
import re
import subprocess
import tomllib

fix3 = "32129c149a15fb1b60a7314e738f3cb466d076e5"
impl = "library/core/src/slice/sort/shared/smallsort.rs"
registry = impl.removesuffix(".rs") + "/verify.rs"
model = registry.removesuffix(".rs") + "/rev2_provider_cost.rs"
manifest = "library/core/Cargo.toml"

def git(*args):
    return subprocess.check_output(("git", *args))

def pinned(path):
    return git("show", f"{fix3}:{path}")

source = Path(impl).read_bytes()
assert git("rev-parse", f"{fix3}^{{tree}}").strip() == b"1b0cc32c571b370178e64f2b8c79773d2ce27051"
assert git("hash-object", impl).strip() == b"0b77c3dbb3b767ba35281a2a686aa477ff1344c5"
assert source == pinned(impl)
assert Path(model).read_bytes() == pinned(model)
assert git("diff", "--name-only", fix3, "--", "library").decode().splitlines() == [
    manifest, registry, registry.removesuffix(".rs") + "/rev2_s13_binding.rs",
]

gate = b"""#[cfg(all(
    kani_smallsort_cal1,
    kani_smallsort_cal2_merge_mask,
    kani_smallsort_rev2_provider_cost,
    kani_smallsort_rev2_s13_binding
))]
mod rev2_s13_binding;
"""
lint = b"    'cfg(kani_smallsort_rev2_s13_binding)',\n"
for path, addition in ((registry, gate), (manifest, lint)):
    data = Path(path).read_bytes()
    assert data.count(addition) == 1 and data.replace(addition, b"") == pinned(path)
assert b'#[cfg(kani)]\n#[unstable(feature = "kani", issue = "none")]\nmod verify;' in source
assert "cfg(kani_smallsort_rev2_s13_binding)" in tomllib.loads(
    Path(manifest).read_text()
)["lints"]["rust"]["unexpected_cfgs"]["check-cfg"]
print("FIX3 runtime bytes and cfg-off registry match")

header = "fn sort13_optimal<T, F>(v: &mut [T], is_less: &mut F)"
sort13 = source.decode().split(header, 1)[1].split("\n}\n", 1)[0] + "\n}"
sort13 = " ".join(re.sub(r"(?m)^\s*//[^\n]*", "", sort13).split())
call = r"swap_if_less\(v_base, (\d+), (\d+), is_less\);"
assert re.fullmatch(
    r"where F: FnMut\(&T, &T\) -> bool, \{ "
    r"if v\.len\(\) < 13 \{ intrinsics::abort_immediate\(\); \} "
    r"let v_base = v\.as_mut_ptr\(\); unsafe \{ "
    rf"(?:{call} ){{45}}\}} \}}",
    sort13,
)
pairs = [(int(a), int(b)) for a, b in re.findall(call, sort13)]
table = pinned(model).decode().split("const SWAP_PAIRS:", 1)[1].split("];", 1)[0]
assert pairs == [(int(a), int(b)) for a, b in re.findall(r"\((\d+), (\d+)\)", table)]
assert len(pairs) == 45 and all(0 <= a < b < 13 for a, b in pairs)
print("45 calls in order, all 45 pairs in Check domain at V34 slots (1+a, 1+b)")

low_bits = (1 << 13) - 1
for mask in range(low_bits + 1):
    bits = [(mask >> i) & 1 for i in range(13)]
    for a, b in pairs:
        bits[a], bits[b] = bits[a] & bits[b], bits[a] | bits[b]
    assert bits == sorted(bits) and sum(bits) == mask.bit_count()
    observed = sum(bit << i for i, bit in enumerate(bits))
    expected = low_bits ^ (low_bits >> mask.bit_count())
    assert observed == expected and ((observed ^ 1).bit_count() != mask.bit_count())
print("8192 binary inputs: order, popcount, expected mask and corrupt-mask difference OK")
PY
```

```text
FIX3 runtime bytes and cfg-off registry match
45 calls in order, all 45 pairs in Check domain at V34 slots (1+a, 1+b)
8192 binary inputs: order, popcount, expected mask and corrupt-mask difference OK
```

Cargo, rustc, Kani и CBMC локально не запускались. Компиляция Rust, cfg-off/on discovery, штатные backend checks, фактические покрытия и единственный нативный отказ контроля требуют будущего прогона.

## Цена и критерий будущего пакета

Префикс содержит 13 независимых битов вместо 104, а один масочный пост заменяет отдельные проверки числового порядка и q-count. Ожидаем сокращения SAT-работы относительно `S13-PLAIN-BYTE`. Для ориентира переход от завершённого CAL2/OB11 Check к цели 120 с потребовал бы выигрыша примерно в 7,3 раза по VT. Эти отношения описывают входную ширину и целевой выигрыш, а не прогноз времени. У FIX3 этот Proof с byte Replace дошёл до 180 с без вердикта и имел 2,46 GiB группы до отсечки. Лист даёт отдельную измеренную точку 59,7 с wall / 32,7 с VT. Его цену нельзя умножать на 45 для оценки actual корня. У нового корня остаются raw-pointer выбор, копирования, covers компаратора и backend-задача доказать эквивалентность сети популяционному счётчику. Сужение данных может удешевить SAT, но затраты на память и symex actual 45 swap могут остаться значительными. Отсечка по времени или 4 GiB правдоподобна, целевые VT ≤120 с и cold wall ≤180 с пока гипотеза. [Сравнимые исторические профили](REV2-NETWORK-PROVIDERS-RESULTS-ANALYSIS.md)

Один будущий Ubuntu-пакет — compile preflight и один cfg-on discovery, затем два последовательных холодных singleton со своими target/export/tmp. Оба используют stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC 6.11.0, stock CaDiCaL, OB12, jobs=1, `--harness <selector> --exact --no-assert-contracts`, unwind 36, штатные safety/overflow/unwind ON, uninit/validity OFF. Сохраняются `verify_z` FIX3 и `--cbmc-args --object-bits 12`. В `RUSTFLAGS` передаются `--cfg=kani_smallsort_cal1 --cfg=kani_smallsort_cal2_merge_mask --cfg=kani_smallsort_rev2_provider_cost --cfg=kani_smallsort_rev2_s13_binding` у preflight/discovery и обоих корней. В discovery подтвердить ровно два новых exact Proof под новым модулем и наследуемый roster при выключенном дополнительном cfg. На каждый singleton 180 с cold wall, до 4 GiB группы и ≥2 GiB резерва. Измерить отдельно setup, child wall, VT, group и CBMC peak, причину/фазу возможной отсечки и native checks/covers. Два слота дают ≤6 мин cold wall, ≤6:50 с запасом по 15 с на reap/receipt и 10 с на старт. При прежних 45 мин на setup, 2 мин на аттестацию, 12 мин на финализацию и 9 мин резерва ориентир пакета — одна job до 75 мин. Измеренный FIX3 setup был 1 183 с, это ориентир для планирования, а не гарантированная цена. [Бюджет и профиль FIX3](REV2-NETWORK-PROVIDERS-HANDOFF.md)

Если положительный корень завершается с полным `VERIFIED` в профиле и контроль даёт единственный нужный нативный `FAILURE` с достигнутыми covers, пакет отличает работающий прямой битовый путь от зафиксированного timeout полного байтового пути. Это сравнение маршрутов целиком. Оно не изолирует эффект меньшего домена от эффекта отказа от Replace, и не измеряет извлечённую модель. Если встретится timeout/RSS с действительным setup и сопоставимыми идентичностями, пакет определит, прошёл ли этот вариант порог отбора, а незавершённый VT останется неизвестен. Отказ preflight, неверный selector, недостижимый cover или иной отказ контроля оставляет сравнение открытым.

Для pr752 после принятия внешней привязки нужны matched Ubuntu и macOS с VT ≤120 с и ≤4 GiB на проверку на каждой ОС, затем штатная партиция. На Ubuntu jobs=2 группа ≤10 GiB и резерв ≥2 GiB. На macOS jobs=1 группа ≤5 GiB и резерв ≥1,25 GiB. Прирост самой долгой штатной партиции ≤5 мин. [Решение владельца](OWNER-DECISION-LIMITS-20261125.md)
