# REV2 · опоры N20/N21 · ревью R1

Ревьюер: субагент Claude `smallsort-reviewer` (read-only). Задание g0 `78e47d827a`, handoff g0 `4a9fe60bf1`.

**GO_WITH_NITS на один Ubuntu-прогон.** Std `87ef4442de…` (tree `832289728d…`), control `414f0060c5…` (tree `bc097e25cf…`, parent `6a599af764`), review-trigger `e69b5ed39f…`. Request `d0228c3a…8ad1`, roster `ff3cf539…c017`, bundle `f93c1a45…8367`. Блокеров нет.

## Исправить до запуска (решение координатора)

1. **Тест координат удалён без замены.** `test_source_coordinate_gate_reads_call_indentation` удалён, у нового `check_native_coordinates` (`request.py:365`) нет юнит-теста. Гате в `sources` работает: ревьюер проверил, что он отклоняет все 276 сдвигов координат на единицу. Нужно вернуть синтетический тест.
2. **Нестабильные тесты supervisor.** На шкале 5 с `test_deadline_terminates_and_reaps_descendant_group` и `test_escaped_descendant_is_killed_by_its_owned_pid` вернули `REAP_UNVERIFIED`. Перед запуском нужно влить test-only исправление w15, если оно пройдёт ревью.

## Замечания

- Blob `rev2_provider_cost.rs` в handoff указан неверно. Правильный — `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de`. Request этот blob не закрепляет.
- В индексе артефактов больше нет идентичностей прошлых overlay. Их можно восстановить через `request.json`.

## Проверено

- **Геометрия.** При `len_div_2=10` обе половины проходят sort9 и затем вставку от смещения 9. Пары merge, центр для нечётной длины и sentinel c=10 сверены с `smallsort.rs`.
- **Координаты.** 92 координаты сверены независимо, line:column = отступ + 1. Нужные нативные anchors подтверждены по прецеденту.
- **Runtime и риск компиляции.** Runtime побайтно прежний, риск компиляции не найден.
- **Control.** Отдельная переменная Actions для tree. Caps 4 GiB. План 5610 с при job 6000 с. Все бюджеты шагов меньше таймаутов.

## Оценка

Шаг из 10 пар займёт 95–115 с VT. Шанс превысить 120 с — около 25–35%. В этом случае слот будет OPEN, а метрики сохранятся.

## R2 · FIX1

**GO на один Ubuntu-прогон**, риск нестабильного self-test supervisor принят. Control `2954a195a5997631fe21169493637531bcc21765` (parent `414f0060c5`), trigger `df7c2f16105e2897f3b4fd60ef1bb251512bdae1`, tree `f56b8ec3d5a8564a4076f3867e35ecb0b8e813c3`. Переменная `CH8_REV2_N20_N21_PROVIDERS_TRIGGER_TREE` равна этому tree.

- **Восстановленный тест `check_native_coordinates`** (`test_run.py:156`) ловит мутации гейта. Он падает, если колонка игнорируется, зафиксирована на 5, сдвинута на единицу или пропущена проверка компаратора.
- **Diff** ограничен `test_run.py` (+46) и handoff. Request, bundle, Std, gate и workflow не менялись. Blob `rev2_provider_cost.rs` в handoff исправлен.
- **Suite.** Обычная шкала OK, 110/110 на шкалах 5 с и 1 с, 109/110 на шкале 60 с. Единственный провал — известный тест supervisor (`REAP_UNVERIFIED`), его стабилизация на доработке.
