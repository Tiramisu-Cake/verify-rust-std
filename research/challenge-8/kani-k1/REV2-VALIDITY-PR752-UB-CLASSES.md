# pr752 · обновление UB classes после Kani 5205

Предлагаемый текст для действующего профиля CI. Он учитывает слияние Kani 5205 и различает возможность нового инструмента и фактический пин pr752. Обновляется bullet в Limitations. Строка `UB classes` в краткой таблице по-прежнему описывает классы, которые штатный прогон проверяет. [Описание pr752](https://github.com/model-checking/verify-rust-std/pull/752) · [Слитое изменение Kani](https://github.com/model-checking/kani/commit/8c6dba5935e8b37a905145c57572d1b67489bae2)

> **UB classes.** This PR uses the repository's Kani pin (`9834c96ce9`) with `-Z uninit-checks` and `-Z valid-value-checks` disabled. On that pin, initialization checking encounters unsupported operations on these routes, and value-validity checking rejects `copy_nonoverlapping`, which SmallSort uses. Kani main at `8c6dba5935` can check supported typed reads after raw copies, including `copy_nonoverlapping`. Writes to immutable bytes and aliasing beyond Kani's pointer checks remain outside the checked scope. [Initialization limitation](https://github.com/model-checking/kani/issues/3300) · [Code at the CI pin](https://github.com/model-checking/kani/blob/9834c96ce90ff57d8495416530b080dc3d52ce25/kani-compiler/src/kani_middle/transform/check_values.rs#L491-L497) · [Value-validity change](https://github.com/model-checking/kani/pull/5205)

Если диагностика SmallSort на новом пине даст завершённые результаты и нативную привязку, можно добавить отдельное предложение после абзаца. Подставить только принятые конфигурации и ссылку на свидетельство.

> In a separate diagnostic on Kani `8c6dba5935`, `-Z valid-value-checks` verified [routes, types, and lengths] and reported the injected invalid value at the expected typed read. [Diagnostic results]
