# K-5: контракты специализированных trait-методов small_sort

Запуски: 2026-10-28 UTC (28–29 октября Europe/Moscow). Ветка: `experiment/kani-k1-k5contracts-20261028`.


**Установлено опытом:** охвачены две из шести настоящих реализаций:
unstable default (A) и unstable Freeze (C), без успешного proof их контрактов.
Контракт на `default fn` отвергнут при compile, в том числе на 38-строчном
примере; qualified-цель метода с собственным generic `F` не разрешилась в C.
По исходникам резолвера ограничение `F` общее для всех шести реализаций
трёх методов. У default раньше срабатывает отказ парсера; после исправления
парсера останется тот же барьер разрешения `F` (вывод по исходникам,
не новый опыт с исправленным парсером).
Два простых положительных контроля получили Kani `SUCCESS`, ложный
trait-постконтракт упал именно на постусловии. При этом весь запуск D имеет
`gate: False`: реальная Cell-обёртка упёрлась в unwind для `memcmp`.
Контракт сортированности с пробой на трёх настоящих методах не доказан;
заключения «3/3» или «Kani вообще не поддерживает trait-контракты» нет.

Публичный [файл отчёта в ветке](https://github.com/Tiramisu-Cake/verify-rust-std/blob/experiment/kani-k1-k5contracts-20261028/research/challenge-8/kani-k1/RESULT-K5.md).
Правки R1 уточняют анализ исходников и готовят отдельные примеры; новых
сборок или повторного запуска примеров не было.

## Границы опыта

Проверяем сначала форму `ensures(|_| true)` + `modifies(v)`, без `old()`,
сортированности, пробы и вызовов компаратора в спецификации. Для такой формы
не нужны предусловия о порядке, длине или представлении элементов. Домены
гармоник и ограничения вызываемого алгоритма указаны отдельно ниже.

Полный pin Kani: `9461e07af7ec929f050aa4192f29363c9be07779`.
Исходная база лейна: `0f5ad96dd907ba06a30deb19e35fb746ea0bc72a`.
Rust в конфигурациях std и Kani: `nightly-2026-10-12`.
В [kani-dependencies на pin](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-dependencies)
указан CBMC `6.11.0`; это версия конфигурации, не самостоятельное измерение
версии исполняемого файла в сборке. Машина: `gcb-e2-standard-4`, kind `measurement`,
10 минут на гармонику. Pin и инфраструктура не менялись.

`k1g.sh dispatch experiment/kani-k1-k5contracts-20261028` отклонён локальной
проверкой имени: `branch must be experiment/kani-k1-<name>-<date>` (регулярное
выражение допускает только `[a-z]+` в имени). Сборка не создавалась.
Поэтому служебная ветка `experiment/kani-k1-kfivecontracts-20261028` публикуется
на тот же SHA, что и ветка задания. Все новые коммиты имеют `[skip ci]`.

## Источники Kani и границы объяснения

На pin есть ветка разрешения `<Type as Trait>::method` (она не обеспечивает
поддержку собственных generic-параметров метода):
[resolve_fn_path](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/resolve.rs#L60-L100),
[resolve_in_trait_impl](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/resolve.rs#L453-L499).
`proof_for_contract` записывает путь в атрибут, не переписывая его:
[contracts/mod.rs](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/library/kani_macros/src/sysroot/contracts/mod.rs#L569-L584).

Основная ошибка A — парсинг `default fn`, а не доказанный сброс токена
при повторной генерации. В
[contract_main](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/library/kani_macros/src/sysroot/contracts/mod.rs#L672-L695)
аннотированный item разбирается как `syn::ItemFn`. В
[Cargo.lock на pin](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/Cargo.lock#L1258-L1268)
для `kani_macros` разрешён `syn 2.0.119`
([package](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/Cargo.lock#L2260-L2268));
`2.0.18` в
[Cargo.toml](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/library/kani_macros/Cargo.toml#L13-L18)
— только semver-требование, не использованная версия.
В `2.0.119`
[ItemFn parser](https://github.com/dtolnay/syn/blob/2.0.119/src/item.rs#L1560-L1565)
не содержит `defaultness`: он переходит от атрибутов и visibility к сигнатуре.
В отличие от него,
[parse_impl_item_fn](https://github.com/dtolnay/syn/blob/2.0.119/src/item.rs#L2849-L2858)
отдельно читает токен `default`. Это согласуется с первым диагностическим
сообщением `expected fn` на `default`. Последующие `E0046`/`E0520` — каскад
диагностик Rust после отклонения метода, а не независимые первичные причины.
Источник макроса объясняет наблюдение; различающие сборки приведены ниже.

Тот же `contract_main` явно отвергает декларации trait-методов без тела
с предложением поставить атрибут на impl. Наличие ветки в исходниках само
по себе не считается результатом GCB-опыта на декларации.

## Поиск аналогов в трекере

Поиск в открытых и закрытых issues/PR `model-checking/kani`: `E0520`,
`specialization contract`, `default fn contract`, `trait method contract`,
`proof_for_contract trait impl`, а также `"expected fn" "default" contract`
и `"default fn" contract`. Прямой аналог проблемы специализации/default
не найден. Это результат поиска, не утверждение об отсутствии такого issue.

- [#4588](https://github.com/model-checking/kani/issues/4588), открыт: stubbing
  унаследованного default-метода не проходит проверку сигнатуры. Другой механизм.
- [#4084](https://github.com/model-checking/kani/issues/4084), открыт: историческая
  ошибка разрешения квалифицированного пути на Kani 0.61. На исследуемом pin
  соответствующая ветка резолвера уже есть; это не доказательство текущего отказа.
- [#4908](https://github.com/model-checking/kani/issues/4908), открыт: stubs и
  function contracts на trait-методах с собственными generic-параметрами.
  У настоящего `small_sort` такой параметр — `F`; C воспроизвёл соответствующий диагностический текст.
  Этот issue не объясняет первичный parser failure на `default fn` в A/B.

Новый Kani из открытого PR #737 (`cd355b0b`) — только условный follow-up вне K-5;
он здесь не собирался и не проверялся.

## Журнал сборок и вывод

### A — настоящий unstable default impl

Build: `d4056945-5e98-4201-8aaa-f5656a4caba9`.
Полный source SHA: `b8ab776552fb515839b028ea488ab69c94e7d51f`.
Атрибуты только на `impl<T> UnstableSmallSortTypeImpl for T::small_sort`.
Пути гармоник: `<u64 as UnstableSmallSortTypeImpl>::small_sort` и
`<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort`.
`u64` выбирает Freeze/Copy, **не** аннотированное default-тело; `Cell<u8>`
нужен для default. Компиляция не дошла до проверки путей и covers;
достижимость ни одной гармоники этим запуском не установлена.

Summary: `COMPILE_ERROR`, обе гармоники `NOT_RUN`, Kani exit 1.
Стадия: compile (macro input parsing), до codegen/verification.
Время команды Kani вместе с компиляцией: `44.71 s`; это не время доказательства.
Диагностика (менее 20 строк, формулировки дословные):

```text
error: expected `fn`
  --> /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:84:5
84 |     default fn small_sort<F>(v: &mut [T], is_less: &mut F)
   |     ^^^^^^^
error[E0046]: not all trait items implemented, missing: `small_sort`
  --> /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:75:1
error[E0520]: `small_sort` specializes an item from a parent `impl`, but that item is not marked `default`
   --> /workspace/src/library/core/src/slice/sort/shared/smallsort.rs:101:5
error: could not compile `core` (lib) due to 3 previous errors; 1 warning emitted
```

`k1g.sh check-tooling BUILD 0f5ad96dd907ba06a30deb19e35fb746ea0bc72a`
подтвердил пул, равенство всех lane-файлов базе и пять SHA-256 в summary.

### B — минимальный пример

Build: `38574122-3924-440a-ab45-c4d835aa9393`.
Полный source SHA: `be51ea0261f5fbed7932dfb2b63ce588412da8db`.
Файл [k5-repro.rs](k5-repro.rs), 38 строк, подключён через `#[path]` как модуль
`verify::k5::reduced`. Проверялся **тот же файл**, не перепечатанный фрагмент.
`controls: true` задаёт `--cfg kani_smallsort_controls` и выбирает импорт
`crate::kani`; корень core уже включает `min_specialization`. В самостоятельном
crate файл включает этот feature и `extern crate kani` сам.
Самостоятельный CLI-запуск вне std не выполнялся; установлен именно отказ
в GCB при embedding файла в core. Локально он не запускался.

У игрушечного trait нет собственного generic-параметра метода, компаратора,
Freeze-dispatch или помощников std. `u16` выбирает blanket default impl,
а `u8` — специализацию. Отсутствие `Clone`/`old`/пробы исключает эти спецификации
из причин данной первичной ошибки.

Summary: `COMPILE_ERROR`; `default_form` и `free_form` — `NOT_RUN`.
Положительный контроль здесь не запустился из-за общей ошибки компиляции;
его нельзя считать работающим по одному присутствию в запросе.
Время команды Kani с компиляцией `46.02 s`, не время доказательства.
Диагностика (пути нормализованы до файла из research; сообщения дословные):

```text
error: expected `fn`
  --> research/challenge-8/kani-k1/k5-repro.rs:11:5
11 |     default fn small_sort(v: &mut [u8]) { pair(v); }
   |     ^^^^^^^
error[E0046]: not all trait items implemented, missing: `small_sort`
 --> research/challenge-8/kani-k1/k5-repro.rs:8:1
error[E0520]: `small_sort` specializes an item from a parent `impl`, but that item is not marked `default`
  --> research/challenge-8/kani-k1/k5-repro.rs:14:5
error: could not compile `core` (lib) due to 3 previous errors; 1 warning emitted
```

`check-tooling` подтвердил равенство lane-файлов базе и все пять SHA-256.

### C — настоящий non-default impl, два пути

Build: `c25ee87c-ce60-462d-9fef-eeccb5dc883f`.
Полный source SHA: `c90851d517058cb3505fe04092dff5538065b342`.
Атрибуты `ensures(|_| true)` + `modifies(v)` перенесены на
`impl<T: FreezeMarker> UnstableSmallSortTypeImpl for T::small_sort`.
Для `u64` это нужное non-default тело; далее вызывается Freeze/Copy network.
Плановый домен: произвольный `[u64; 4]`, символическая длина `0..=4`,
компаратор `a < b`, unwind 6. Это домен **попытки**, не доказательства.

В исходник и запрос включены обе формы:
`<u64 as UnstableSmallSortTypeImpl>::small_sort` (`specialized_u64`) и
`crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl::small_sort`
(`trait_path_u64`). Вторая форма ошибки разрешения не дала (вероятно,
указывает на объявление метода в trait); проверка контракта по ней не выполнялась.
Это следует из единственной ошибки C и порядка обхода:
[check_crate_items](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/mod.rs#L86-L128)
проверяет атрибуты всех items до `abort_if_errors()`. Ветка
[simple path](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/resolve.rs#L112-L116)
возвращает DefId найденного item, а
[resolve_path](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/resolve.rs#L132-L179)
проходит через `resolve_in_trait_def`; декларация trait без тела не может нести
этот контракт. Отсутствие ошибки разрешения не означает подтверждение
контракта impl-метода. Обе строки summary — `NOT_RUN`.

Summary: `COMPILE_ERROR`, Kani exit 1, время команды `43.53 s`.
Стадия compile, разрешение цели `proof_for_contract`, до CBMC.
Диагностика (менее 20 строк, дословно):

```text
error: failed to resolve `<u64 as UnstableSmallSortTypeImpl>::small_sort`: unable to find implementation of associated function `slice::sort::shared::smallsort::UnstableSmallSortTypeImpl::small_sort` for u64
 --> /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/k5.rs:6:1
6 | #[kani::proof_for_contract(<u64 as UnstableSmallSortTypeImpl>::small_sort)]
  = note: Kani does not currently support stubs or function contracts on generic functions in traits.
           See https://github.com/model-checking/kani/issues/1997#issuecomment-3134614734 for more information.
error: could not compile `core` (lib) due to 1 previous error; 92 warnings emitted
error: Failed to execute cargo (exit status: 101). Found 1 compilation errors.
```

C экспериментально подтверждает отказ qualified-цели на одной реализации.
Механизм общего ограничения установлен по
[resolve_in_trait_impl](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/resolve.rs#L453-L499):
в `Instance::resolve` передаются только `Self` и аргументы trait, без
собственных generic-параметров метода. Все три объявления `small_sort`
имеют собственный `F` (см. раздел об охвате ниже). Поэтому qualified-цель
`<T as Trait>::small_sort` для этих методов на данном pin не разрешается
независимо от выбранного impl. Это механизм
[Kani #4908](https://github.com/model-checking/kani/issues/4908),
изолированный также в pinned
[UI-тесте generic_trait_fn.rs](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/tests/ui/stubbing/generic_trait_fn.rs):
он проверяет stubbing метода с собственным `U: Clone`, не специализацию
и не `proof_for_contract`. Его
[expected output](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/tests/ui/stubbing/generic_trait_fn.expected)
содержит ту же категорию ошибки разрешения; это подтверждающий исходник,
не новый контрактный опыт K-5.

Примечание про
[Kani #1997](https://github.com/model-checking/kani/issues/1997#issuecomment-3134614734)
само по себе причину не доказывает:
[код выдачи примечания](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/attributes.rs#L734-L768)
проверяет наличие own params у метода **или** parent trait; parent params
включают `Self`, поэтому примечание сопровождает любой `MissingTraitImpl`
для trait-метода. Причину в этом случае
показывает код `resolve_in_trait_impl`, а не формулировка общего примечания.
У default-реализаций A/B раньше срабатывает ошибка парсера; исправление
одного парсера не устраняет общий барьер `F`. Перенос этого вывода на
остальные реализации основан на исходниках, не на шести отдельных сборках.
Успешной компиляции целой формы C нет. `check-tooling` подтвердил базу и пять SHA-256.

### D — различающие контроли

Build: `be67e8d7-5a63-4d6a-9c0e-3cef3a62c062`.
Полный source SHA: `ce450c107bd51ef09a541d1a08860579d9755d88`.
У настоящих trait-методов контракты сняты. Сохранены только `#[cfg(kani)]`
cover-точки в unstable default, unstable Freeze и Freeze/Copy network;
они не меняют обычные runtime-тела. `verify::k5` включается только с
`kani_smallsort_controls`, поэтому отрицательный контроль не попадает в
обычную suite.

Запрошены четыре гармоники:

- `reduced_specialized_form`: `proof_for_contract(<u8 as SmallSort>::small_sort)`,
  метод специализирующего игрушечного impl **без собственных generic-параметров**, `true`, `modifies(v)`,
  произвольные `[u8; 2]` и длина `0..=2`, unwind 3.
- `free_wrapper_cell`: контракт `true` + `modifies(v)` на свободной обёртке
  настоящего `Cell<u8>` default-маршрута, длина `0..=2`, unwind 6. Перед этим
  вызывается настоящий uncontracted `u64` Freeze/Copy путь при N=2 с assert-ами
  сортированности и перестановки. Контракт здесь **на обёртке**, не trait-методе.
- `reduced_free_form`: та же свободная функция `control` и `pair`, что в B;
  дополнительно uncontracted default игрушечного trait для `u16` при N=2
  проверяется assert-ами sorted/permutation и cover-ами. Unwind 3.
- `reject_false`: `proof_for_contract(<u8 as FalseSmallSort>::small_sort)`;
  на non-default impl стоит `ensures(|_| false)` + `modifies(v)`, N=2,
  unwind 3. Ожидается `FAILED` с расположенным check, содержащим `false`.

Summary: `COMPLETE`, но `gate: False`, `expectation met: False`,
`measurement ok: False`, Kani exit 1. Это **не PASS сборки**.
Время всей команды с компиляцией `117.16 s`, max RSS `2010416 KiB`.
Все четыре гармоники действительно запущены: строки `Checking harness` и
`Complete - 2 successfully verified harnesses, 2 failures, 4 total.`
получены через `k1g.sh log-lines BUILD 2716 58`.

| Гармоника | Kani status | Время, s | Checks failed/total | Unreachable checks | Covers |
|---|---|---:|---:|---:|---:|
| `reduced_specialized_form` | SUCCESS | 3.8525066 | 0/146 | 4 | 3/4 (1 unreachable) |
| `reduced_free_form` | SUCCESS | 1.5669434 | 0/158 | 4 | 7/7 |
| `reject_false` | FAILED, ожидаемый postcondition | 1.1699107 | 1/130 | 4 | 2/4 (2 unreachable) |
| `free_wrapper_cell` | FAILED, unwinding | 4.3691077 | 1/512, остальные 511 **undetermined** | Не определено | 3/7, остальные 4 **undetermined** |

Наблюдаемые причины двух отказов (менее 20 строк):

```text
Failed Checks: |_| false
 File: "/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/k5.rs", line 84, in <u8 as slice::sort::shared::smallsort::verify::k5::FalseSmallSort>::small_sort::{closure#2}
Failed Checks: unwinding assertion loop 0
 File: "<builtin-library-memcmp>", line 25, in memcmp
```

Отрицательный контроль сработал именно на `ensures(false)`, не на panic,
memory safety или unwinding. Положительные SUCCESS — отдельные результаты
Kani, а не утверждение о принятии measurement всего запуска лейном.
В `reduced_free_form` удовлетворены **все 7** cover-свойств, включая вход
и возврат uncontracted default (`u16`, N=2), тело специализации `u8` и вызов/
возврат свободного контроля. Это работающий контроль специализации без
контракта на default и свободного контракта той же простой формы.

Для отдельных `reduced_specialized_form` / `reject_false` terse-интерфейс
даёт агрегаты covers, но не сопоставляет их меткам. Нельзя объявить все covers
достижимыми по одному SUCCESS; их неполные количества сохранены в таблице.
У negative N фиксирован как 2, а отказ постусловия подтверждает исполнение
проверки на возврате специализирующего метода при этом N.

`free_wrapper_cell` — отказ нашей границы unwind, **не** новый контрпример
trait-контракту. Возможный источник `memcmp` — 16-байтные сравнения массивов
`[u64; 2]` в предварительном permutation-assert при unwind 6; точная привязка
builtin к source-выражению этим интерфейсом не установлена. Нужен отдельный
опыт с большим unwind или покомпонентным сравнением. Он не запускался:
четыре сборки исчерпаны. Неподтверждённые 511 checks и четыре covers не
объявляются успешными; контракт Cell-обёртки и достижимость её default-тела
не установлены. Это исход «отказ из-за границы нашей гармоники / недостаточно
данных для обёртки».
`check-tooling` подтвердил базу и пять SHA-256 для D.


## Бюджет и команды

Использовано четыре GCB-сборки, все `k1-network`, `measurement`,
`gcb-e2-standard-4`, 10 минут на гармонику, без изменения pin или лейна.
Резервы A/B/C: каждый `(30 + 10*2)*0.0135 = $0.675`;
D: `(30 + 10*4)*0.0135 = $0.945`.
Перед A ledger показывал used `$36.6495`, reserved `$0`; перед D после
окончания A/B/C used `$36.9870`. Прирост `$0.3375` — верхняя граница цены
трёх наших законченных сборок (ledger общий, чужие завершения могли бы
только увеличить её). Вместе с **полным** резервом D верхняя граница K-5
`$0.3375 + $0.945 = $1.2825 < $2.5`. Таким образом, каждый следующий запуск
помещался в остаток; число сборок ограничено четырьмя независимо от остатка денег.
После D общий ledger: used `$37.4730`, reserved `$0.9450` чужих незаконченных
сборок; все четыре K-5 уже закончились. Итоговая верхняя граница цены K-5
по приросту общего used: `$37.4730 - $36.6495 = $0.8235`. Это консервативная
граница, не точная индивидуальная стоимость: в прирост могут входить чужие
законченные сборки. Исторические ledger/evidence записи не менялись.

Для каждого опыта: validate запроса → commit `[skip ci]` → push основной
и служебной веток на один SHA →
`research/challenge-8/kani-k1/tools/k1g.sh dispatch experiment/kani-k1-kfivecontracts-20261028`
→ `k1g.sh watch BUILD` → `k1g.sh summary BUILD`, ограниченные `log-grep` /
`log-lines`, `check-tooling BUILD 0f5ad96dd907ba06a30deb19e35fb746ea0bc72a`.
Запросы каждого опыта сохранены в соответствующем source SHA.

Команда лейна: `scripts/run-kani.sh --path "$PWD" --kani-args` с
`--harness <полное имя>` для каждой запрошенной гармоники, `--exact`,
`--harness-timeout 10m`. Скрипт вызывает pinned `kani verify-std` с
`-Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts
-Z quantifiers -Z stubbing`, `--no-assert-contracts`, `--cbmc-args --object-bits 12`.
B/C/D добавляют `RUSTFLAGS="--cfg kani_smallsort_controls"`; A — нет.
Локальные проверки ограничены Python validate, git/diff и чтением источников;
rustc/cargo/Kani/CBMC локально не запускались. Полные verifier logs не читались.


## Охват шести настоящих тел

Экспериментально охвачены две реализации, A и C; это попытки формы,
не два proof. Общий вывод по исходникам относится к qualified-цели всех
шести реализаций: собственный generic `F` есть во всех трёх объявлениях —
[StableSmallSortTypeImpl:23](https://github.com/Tiramisu-Cake/verify-rust-std/blob/80fa9d5ed7fecfa0b6fce71a33871c7ab9079033/library/core/src/slice/sort/shared/smallsort.rs#L23),
[UnstableSmallSortTypeImpl:72](https://github.com/Tiramisu-Cake/verify-rust-std/blob/80fa9d5ed7fecfa0b6fce71a33871c7ab9079033/library/core/src/slice/sort/shared/smallsort.rs#L72),
[UnstableSmallSortFreezeTypeImpl:114](https://github.com/Tiramisu-Cake/verify-rust-std/blob/80fa9d5ed7fecfa0b6fce71a33871c7ab9079033/library/core/src/slice/sort/shared/smallsort.rs#L114).
Резолвер не передаёт этот аргумент метода в `Instance::resolve`.
Следовательно, любая цель `<T as Trait>::small_sort` в этих трёх trait
упирается в общий механизм #4908; у default до него наблюдался отказ парсера.
Таблица ниже отражает только экспериментальный охват и достижимость,
не подменяя ими этот отдельный вывод по исходникам.

| Тело | Тип, выбирающий тело | Контракт на самом методе | Достижимость тела |
|---|---|---|---|
| Stable default `impl<T>` | !Freeze, например `Cell<u8>` | Не проверялся | Не проверялась |
| Stable `impl<T: FreezeMarker>` | Freeze, например `u64` | Не проверялся | Не проверялась |
| Unstable default `impl<T>` | `Cell<u8>` | A: compile failure до доказательства | D: не установлена — wrapper-контроль оборвался на unwind |
| Unstable `impl<T: FreezeMarker>` | `u64` | C: compile failure при разрешении цели | D: 3/7 covers суммарно, точная body-метка не установлена |
| Unstable Freeze default | Freeze + !Copy, например структура с Drop | Не проверялся | Не проверялась |
| Unstable Freeze `impl<T: FreezeMarker + CopyMarker>` | `u64`, network route | Собственный контракт не проверялся | D: 3/7 covers суммарно, точная body-метка не установлена |

Ни для A, ни для C не было успешной проверки контракта настоящего метода.
Их `NOT_RUN` не устанавливает достижимость и не доказывает выбранное тело.
Типы указывают ожидаемую специализацию по исходнику; только body-cover может
подтвердить исполненный маршрут. У реального пути D агрегат 3/7 без
меток и с unwinding failure не даёт отдельного доказательства body-cover. Игрушечный trait D не входит в эти шесть тел.

Использованные реальные компараторы — stateless строгий `<` на `u64` или
`Cell<u8>::get()`. Домены явно ограничены длинами A/C `u64: 0..=4`, A Cell N=2,
D Cell `0..=2`, D plain u64 N=2; это ограничения гармоник, не универсальные
предусловия контракта. Для минимального `pair` безопасны любые длины,
но действие swap производится только при N=2.

Сортированность + сохранение счётчика пробы в `ensures` **не проверялись**:
форма/цель настоящих методов не прошла стадию compile. Существующие внутренние
контракты и assert-ы не переименовываются в контракты этих трёх методов.
Для будущего содержательного опыта нужно явно задать строгий порядок и
допустимые длины, initialized/no-padding представление пробы,
`size_of::<T>() <= 128` и `len <= 32` для unrolled-помощников. Для stable
маршрута нужен пригодный scratch (на general-пути `scratch.len() >= len + 16`)
и его запись в `modifies` вместе с `v`. Эти условия не проверялись в K-5.

Декларация настоящего trait-метода без тела с атрибутом не проверялась в GCB:
после A/B (воспроизведение и минимизация) и C (generic target resolution)
четвёртая сборка отдана работающим различающим контролям. Для декларации
есть только явно отвергающая ветка исходников макроса, см. выше;
исход именно этого GCB-варианта — **недостаточно данных**. Вторая path-форма C
ошибки разрешения не дала (вероятно, указывает на объявление в trait);
проверка контракта по ней не выполнялась.
Пятого запуска не было, даже при остатке денежного бюджета.

## Классификация результата

1. **Форма работает в проверенном варианте:** игрушечный non-default impl
   для `u8`, метод без собственных generic-параметров, N=0..2, true + modifies;
   свободная функция `control` при N=2. Это bounded evidence формы, не
   sorting-correctness contract настоящего SmallSort и не B2/full proof.
2. **Воспроизводимый отказ инструмента на compile:** default impl настоящего
   метода (A) и независимого от SmallSort минимального примера (B), при
   отдельно работающих простых контролях D. Первая ошибка — `expected fn` на `default`;
   E0046/E0520 — последующие диагностики. C подтверждает отказ generic
   trait-method target на одной реализации. По общему коду резолвера
   ограничение собственного `F` действует на все шесть реализаций;
   у default оно остаётся и после устранения ошибки парсера. Это вывод
   по исходникам и механизму #4908, не дополнительные успешные/неуспешные сборки.
3. **Ошибка границы нашей проверки:** `free_wrapper_cell` в D, unwind memcmp.
   Этот отказ не переносится на компиляцию формы A/B/C.
4. **Недостаточно экспериментальных данных:** отдельные proof и проверки
   достижимости настоящих stable вариантов, Freeze-default и собственного
   Freeze/Copy-метода; опыт с атрибутом на декларации trait без тела;
   proof контракта по второму пути C и proof/достижимость реальной Cell-обёртки.
   Общий вывод по исходникам о барьере `F` для qualified-целей всех шести
   реализаций от этого перечня незапущенных proof не меняется.

Два содержательных постусловия (sorted + сохранение пробы) не добавлялись,
потому что стадия формы/цели на настоящих методах не пройдена. Нельзя свести
наблюдаемое только к старой формуле «E0520/E0599»: E0599 здесь не воспроизведён,
а E0520 оказался вторичным. Можно утверждать конкретные два compile-отказа
на этом pin и показать работающую более узкую форму. Опыт охватил две
из шести настоящих реализаций; общий вывод о qualified-целях остальных
следует из их сигнатур и кода резолвера.

## Подготовка отдельного публичного опыта (R1, без запуска)

В [k5-standalone/README.md](k5-standalone/README.md) подготовлены три
независимых crate, у каждого одна гармоника и не более 30 строк Rust:
`default_fn` (контракт на `default fn`), `generic_method` (non-default метод
с собственным `F`) и `control` (тот же контракт без собственного generic).
Ожидаемые исходы — соответственно `expected fn`, ошибка разрешения цели,
`SUCCESS`; **на Kani 0.68.0 они ещё не проверялись**.

Инструкция предназначена для возможного отдельного запуска координатором
на выпущенном `kani-verifier 0.68.0`. В
[rust-toolchain.toml тега kani-0.68.0](https://github.com/model-checking/kani/blob/kani-0.68.0/rust-toolchain.toml)
указан `nightly-2026-08-21`; этот channel записан только в новый каталог
примера. Pin K-5 `9461e07a`, toolchain исходного лейна и историческая
GCB-метадата не менялись. В R1 не запускались локальный Rust/Kani, GCB,
GitHub Actions или CircleCI. Исправлена только устаревшая строка cover
`uncontracted specialized` в `verify/k5.rs`; прежние результаты D относятся
к прежнему source SHA, а не к изменённой метке.

## Known limitations — текст для PR (English)

On Kani `9461e07a`, the tested specialized trait-method contract fails during compilation; the reduced reproducer and control results are linked below.
Experiments covered 2/6 SmallSort implementations; the bare trait path gave no resolution error, but no contract was checked through it.
Source analysis shows a shared method-owned `F` resolution barrier ([Kani #4908](https://github.com/model-checking/kani/issues/4908), [UI test](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/tests/ui/stubbing/generic_trait_fn.rs)); default impls encounter parsing first and would retain that barrier after a parser fix.
The reproducer was tested only embedded in core; reduced non-generic/free-function controls verified, and a false trait postcondition failed as intended.
The real-wrapper control hit a `memcmp` unwind bound; the [#1997 note](https://github.com/model-checking/kani/issues/1997#issuecomment-3134614734) alone does not establish the cause, no direct parser-issue match was found, and no “3/3” result is claimed.
See [K5 evidence](https://github.com/Tiramisu-Cake/verify-rust-std/blob/experiment/kani-k1-k5contracts-20261028/research/challenge-8/kani-k1/RESULT-K5.md), including reproducer build `38574122-3924-440a-ab45-c4d835aa9393` and control build `be67e8d7-5a63-4d6a-9c0e-3cef3a62c062`.
