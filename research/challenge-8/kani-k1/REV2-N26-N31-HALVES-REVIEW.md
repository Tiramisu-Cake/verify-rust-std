# REV2 N26–N31 half providers · независимое ревью R1

**GO** с неблокирующими замечаниями · ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26 · Std `ea34c58ab95b4cbccd9acaa3080597b8b2517a87` (tree `75c4a374a0`, parent `8fe1b01f0a`), Control `b22438e7bec284757a84e4da85bf959f6eec4617` (tree `22b10aa374`, parent `fd941d9493`), review-trigger `6161972f92` (тот же tree, parent `467af9cb8d`), handoff g0 `5b7d879436`.

## Неблокирующее

1. **Правые вставки на базах 14–16 держатся только на офлайн-аргументе** (handoff 86–101). Ревьюер перепроверил по `smallsort.rs` (`:725` проверка `sift == begin` до `sub(1)` на `:730`; сдвиг `sift→sift+1`; отдельный `tmp` и `CopyOnDrop` `:357–364`; `tail` читается только при `tail != end` `:761`; доступы в `[begin, tail]` и `tmp`) — пробела нет. Пробелы в свидетельствах и маркировке: (а) исторический драйвер B17 нативно показывает сдвиг только на первой вставке (rel13, cover `REV2_N32_INSERT_SHIFT`); достижимость сдвигов rel14/rel15 нативно не показана; (б) выводы об инициализации при uninit OFF не помечены как внешние (handoff 88–90); (в) перенос доказательства на другую базу буквально не входит в список внешних шагов правила композиции. В admission: «composite: external base translation + loop induction, init external under uninit OFF»; координатор принимает этот шаг явно.
2. **Ослаблен валидатор результатов** (`ch8-cal1/results.py:109`): прежде `copy_back` был привязан к ожидаемому исходу, теперь допускается любой bool. Удалён отрицательный тест сдвига якоря копии `587:14 → 588:14`; среди swap-check только первая локация проверяется мутацией (`test_results.py:482–488`). Для этого пакета безопасно (roster заморожен, у всех шести строк `false`).
3. Handoff, строка 9: предшествующий run `45829863637` указан как `running`; он завершён success 8/8 MATCHED.
4. Handoff, строка 89: источники копий лежат в `[begin, tail−1]`, а не `[begin, tail]`.
5. Различающего контроля в пакете нет — по заданию отложено; форма `check_bits` покрыта историческим `S13-B17-L16-CORRUPT-MASK`.

## Проверено

- Std: три пути (check-cfg, cfg-gate в `verify.rs`, новый модуль на 142 строки); `smallsort.rs` `0b77c3db`, `cal1_model` `236394dc`, `ptr/mod.rs` `9220ac5a`, исторические S13-модули и блок N32 неизменны.
- Три bit-sort корня — plain Proof, actual `sort13` на `v[14..28]`, `v[15..30]`, `v[16..32]` (правые половины N27/N29/N31); три swap Check на базах 14/15/16 с `a<b<13`. Таблица половин и 45 пар (`:612–656`) совпадают; перебор всех 8192 масок сортирует.
- 100 координат source bindings; хэши request `62aba996…`, bundle `2033e104…`, roster `e097e28d…`, bindings `05b42ed7…`; `test_supervisor.py` `df63a457…`; bundle проверен на shallow `dab03cf510`.
- Control: своя переменная `CH8_REV2_N26_N31_HALVES_TRIGGER_TREE`; 6 слотов; таймауты шагов ≥ внутренних бюджетов; cutoff 77:25, план 93:30; остановка слотов при неподтверждённом reap. Исторические S13 — 2,0–2,2 GiB, риска уровня N25 нет.
- 118/118 на шкалах default/1/5/60 с; rustfmt, `git diff --check`, YAML, `bash -n`; авторство Tiramisu-Cake, `[skip ci]`.

Не запускалось: cargo, rustc, Kani, CBMC, CI, `pins` с payload.
