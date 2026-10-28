# K-5: отдельные примеры для Kani 0.68.0

Подготовлены по R1 для возможного запуска координатором на отдельном GitHub
Actions runner. **Не запускались:** ни локально, ни в GCB, ни в Actions.
Ожидаемые исходы ниже — гипотезы для проверки на выпущенном Kani 0.68.0,
а не результаты исходных GCB-опытов на `9461e07a`.
[Исходный отчёт K-5](../RESULT-K5.md) содержит проверенные результаты;
старый `k5-repro.rs` проверялся только встроенным в core.

Все три crate независимы: собственный `Cargo.toml` с `[workspace]`,
`src/lib.rs` с `#![feature(min_specialization)]` и ровно одной гармоникой.
В каждом crate не более 30 строк суммарно в manifest и Rust-исходнике.
Kani сам добавляет `kani` и `cfg(kani)` при `cargo kani`
([usage на теге](https://github.com/model-checking/kani/blob/kani-0.68.0/docs/src/usage.md));
зависимость от `kani` в manifest не нужна. Модуль
`#[cfg(kani)] mod check` исключается из обычной сборки.

## Версия и установка (команды для будущего runner)

Nightly из
[rust-toolchain.toml тега kani-0.68.0](https://github.com/model-checking/kani/blob/kani-0.68.0/rust-toolchain.toml):
**`nightly-2026-08-21`**. Он закреплён в локальном для этого каталога
`rust-toolchain.toml`. Это не toolchain исходного лейна K-5.

На Linux runner с Rust/rustup выполнить установку один раз; инструкции
[релизного install guide](https://github.com/model-checking/kani/blob/kani-0.68.0/docs/src/install-guide.md):

```sh
cargo install --locked kani-verifier --version 0.68.0
cargo kani setup
```

Дальнейшие команды выполнять из `research/challenge-8/kani-k1/k5-standalone/`.
Они используют выделенный channel `nightly-2026-08-21`. Сохранить SHA этих
примеров, вывод `cargo kani --version`, выбранный channel, полный вывод
каждой команды и её exit code. Workflow не создаётся и не запускается
этим изменением.

## Три независимых запуска

Первые два запуска ожидаемо завершаются ненулевым кодом. Выполнять их как
независимые шаги; не связывать команды через `&&` и не считать ожидаемую
ошибку компиляции успешной формальной проверкой.

### default_fn

Контракт `ensures(|_| true)` + `modifies(v)` стоит на blanket `default fn`;
`u16` выбирает именно его, `u8` специализирует метод без контракта.
Ожидается отказ compile/macro parsing: `error: expected fn` на `default`,
возможны последующие E0046/E0520. Проверка контракта не ожидается.

```sh
cargo kani --manifest-path default_fn/Cargo.toml -Z function-contracts --harness check::check_default --exact
```

### generic_method

Тот же контракт стоит на non-default impl для `u8`. У метода есть собственный
`F: FnMut(&u8, &u8) -> bool`; компаратор намеренно не используется телом
или спецификацией, чтобы изолировать наличие generic-параметра. Default-метод
не аннотирован. Ожидается отказ разрешения qualified-цели
`<u8 as SmallSort>::small_sort`, механизм
[Kani #4908](https://github.com/model-checking/kani/issues/4908), до verification.
Ориентир по исходникам —
[UI-тест на исходном pin](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/tests/ui/stubbing/generic_trait_fn.rs),
который изолирует generic метода при stubbing; это не результат нового примера.

```sh
cargo kani --manifest-path generic_method/Cargo.toml -Z function-contracts --harness check::check_generic --exact
```

### control

Тот же specializing impl и контракт, но у метода нет собственного generic.
Ожидается `SUCCESS` для произвольного `[u8; 2]` при N=2 и unwind 3;
cover отмечает вызов и возврат при N=2. Это контроль формы true + modifies,
а не контракт сортированности, пробы или «3/3» для SmallSort.

```sh
cargo kani --manifest-path control/Cargo.toml -Z function-contracts --harness check::check_control --exact
```

| Crate | Строк Rust | Гармоника | Ожидаемая стадия / исход |
|---|---:|---|---|
| `default_fn` | 24 | `check::check_default` | compile / `expected fn` |
| `generic_method` | 23 | `check::check_generic` | compile / target resolution error |
| `control` | 24 | `check::check_control` | verification / SUCCESS |

Если наблюдаемый исход отличается, сохранить его как новый результат
Kani 0.68.0; не переносить автоматически выводы исходного pin на релиз
и не заменять ими исторические результаты GCB. Пакет не содержит
экспериментальных изменений библиотеки std или инфраструктуры лейна.
