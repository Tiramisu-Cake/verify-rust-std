# REV2 · валидность на Kani main · независимое ревью R1

Ревьюер: субагент Claude `smallsort-reviewer` (read-only). Codex-ревью не использовалось: задачи этой ветки трижды останавливал фильтр содержимого Codex. [Handoff](REV2-VALIDITY-MAIN-HANDOFF.md) · [Задание](REV2-VALIDITY-MAIN-IMPL-TASK.md) · [Уточнение](REV2-VALIDITY-MAIN-COORD-NOTE.md)

**GO_WITH_NITS на один диагностический Ubuntu-прогон**: control `caaa716bc3856d1e6ec460a74cb22fd36e9200d6`, tree `00220e7ead711ba57bf64f4e07b97d360f047d49`, Std overlay `75ab1822ac0cf10d905ecb8975c2bf0eda35c3a2`, CI-REQUEST SHA-256 `7ccf98c4…c53474`. Блокеров нет. Компиляция, discovery и исходы свойств остаются UNKNOWN до фазы 0.

## Исправить до запуска (координатор)

1. Таймаут шага фазы B в `.github/workflows/ch8-q-pilot.yml:91` — 75 мин. Внутренние дедлайны допускают до ~107 мин: `kani list` в `b_setup` (`run.py:638`, `run.py:660`) ограничен epoch+79:30, слоты B — epoch+119:30, финальная аттестация — 121:30. При долгом setup последние слоты и аттестация теряются. Нужно ограничить B setup как `min(deadline, start + 30 min)` или поднять таймаут шага примерно до 110 мин внутри job 140 мин.

## Замечания

- Review-trigger `24e1a7715c` содержит `[skip ci]`. Для запуска нужен пересозданный коммит с тем же tree и единственным parent `467af9cb8d`, как в FIX3.
- `FAILURE_CLASS["TOOLCHAIN_COMPONENTS"]` (`run.py:34`) относит любой сбой `rustup component list`, включая таймаут, к `LOCAL_COMPONENT_MISSING`. Это неточная классификация, на исход не влияет.
- ON-positive MATCH не требует `read_binding=OBSERVED`. Перед утверждением о проверке на конкретном чтении смотреть `read_binding`. Чувствительность дают только четыре отрицательных случая.
- `trigger_admitted=true` записывается до `spec.load()` (`run.py:810`), как в принятом FIX3.

## Проверено

- **Идентичности.** Совпали все commit/tree/parent, четыре SHA-256 и bundle. У bundle единственный prereq `dab03cf510`, единственный HEAD `75ab1822ac`, refs не создаются. В дереве только два workflow, `ch8-s2.yml` не срабатывает на эту ветку.
- **Фаза 0 только в CI.** Синтетически без фазы 0 все 30 receipts A/B получили `NOT_RUN` / `PHASE_0_NOT_COMPLETED`.
- **Фаза A.** Единственная разница OFF/ON — `-Z valid-value-checks`. ON-negative требует ровно одного validity FAILURE на месте чтения и SATISFIED cover сырой записи. OFF-negative требует SUCCESS без validity-свойств.
- **Фаза B.** Std diff затрагивает три пути (cfg-lint, хвостовой `mod validity_main` под cfg, новый модуль). Runtime побайтно прежний. Нет `assume` и stubs, используется `--no-assert-contracts`, координаты и covers сверены `check_overlay_layout` и `check_coordinates`.
- **Риск компиляции.** Найден не был: пути к приватным элементам родителя видимы ребёнку, на `validity_main` извне не ссылаются, bounds, imports и unsafe в порядке.
- **Gate.** Пин берётся только из `vars.CH8_REV2_VALIDITY_MAIN_TRIGGER_TREE`. Отклоняются пустой, укороченный, чужой и отсутствующий пин, изменённое дерево с согласованным trailer и неверный parent. Caps 4 GiB на слот, резерв 2 GiB, setup 10 GiB, окна A 45+10+5+5 с и B 180+10+5+5 с. План 133:30 при job 140 мин.
- **Команды.** Suite 99/99 на shared clone trigger, в том числе с `time.monotonic` от 60 с (на копии без `.git` 98/99 из-за среды). Прошли rustfmt `--check`, `git diff --check` на трёх диапазонах, YAML и `bash -n` для 7 шагов. Cargo, rustc, Kani, CBMC, Miri, CI и push не запускались.

## R2 · FIX1

**GO** на control FIX1 `3ca002452456f9fdfe303ad01acd439960833429` и trigger `59477c90275fd5e2db710947a25e4c56cd1d2954` с tree `697dc737fe3bda41f4070ad2d65c123c5c4d615a`. У control единственный parent `caaa716bc3`, у trigger — `467af9cb8d`. Блокеров нет.

- **Фаза B.** Setup ограничен минимумом из прежнего дедлайна и старта шага + 30 мин, слоты — минимумом из дедлайна и конца setup + 40 мин. Худший случай около 72 мин при таймауте шага 80 мин. Фаза A ограничена так же: около 19,5 мин при шаге 21 мин. План 133,5 мин укладывается в job 140 мин. Тест `StepBudgetTests` действительно ловит прежние 75 мин.
- **Проба rustup.** `MissingComponents` даёт `LOCAL_COMPONENT_MISSING`, таймаут — `TOOLCHAIN_PROBE_TIMEOUT`, прочий сбой — `TOOLCHAIN_PROBE_FAILED`. Тесты покрывают все три случая.
- **Неизменное.** CI-REQUEST, bundle, fixture, `request.py`, `verdict.py`, `native_properties.py` и `supervisor.py` совпадают с R1. Gate принимает новый pin и отклоняет старый `00220e…`.
- **Проверки.** Suite 102/102 с обычными часами и с часами от 60 с. Прошли YAML, `bash -n` для 7 шагов и `git diff --check`.
- **Trigger.** Review-trigger содержит `[skip ci]`. Для запуска нужен пересозданный коммит с тем же tree и parent `467af9cb8d`.
