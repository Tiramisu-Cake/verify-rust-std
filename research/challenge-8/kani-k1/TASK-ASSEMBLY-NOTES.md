# ASSEMBLY — уточнения координатора и планировщика (обязательны, дополняют TASK-ASSEMBLY.md)

1. **SHA источников.** stable N8: BACKING `a3e0dc4cda`, library `bff6e4863e`, measurement source `740d22674c`.
   BACKING2 (general N7, stable N6/N7): ждать сообщения координатора с exact source/library SHA и подтверждением
   SUCCESS/covers; не подменять их OPT stable со старым backing. Cell N8 — финальный UNSTABLE8 G3 (covers 4/4).
2. **Уникальные имена по маршруту.** `general_stable_direct_u64_n6/n7/n8` уже заняты прежними combined B — новые
   имена general-only/stable-only, карта source-name → new-name. Без скрытого `any stable` в helpers; снять cfg с
   fixed-route helper/macro types; ordinary adapter вынести из cfg-модуля. Не копировать целиком opt_split/backing.
3. **182 — условный прогноз** (176+3+6−3). C данного N ретирить только при успехе обеих ветвей с прежними T/F/N/oracle;
   при PARTIAL пересчитать и пометить оставшийся C conditional. Явно описать: новый stable direct — другая fixture
   (aggregate backing), не измерение старой array-backed.
4. **P2-патч пересобрать.** Combined B u64 N6/N7 (positive DIRECT) теперь дублируют новые пары — не поднимать их в P2
   автоматически, классифицировать как дубли; статус исторических A u64 решить и записать. Пересчитать ordinary P2 и
   controls, static apply; 339 не сохраняется автоматически. TIMEOUT types, retired/negative/unsupported — gated.
5. **Пять controls по именам:** `merge::general_stable_direct_value_corruption_control_u64_n2`,
   `merge::merge_scratch48_unsorted_halves_control_u64_n4`, из BACKING — `stable_value_corruption_control_u64_n2`,
   `unsorted_halves_control_u64_n4`, `allocation_bounds_control_u64` (пути после переноса; они должны использовать
   перенесённый ordinary adapter/oracle, а не старую копию). Measurement jobs=1, controls:true, timeout 600. Gate:
   ожидаемый FAILED, covers, никаких иных отказов; compile/unsupported/TIMEOUT — не ожидаемый результат.
6. **Ручная сверка по итоговому SHA:** у count-controls единственный FAILED — count-assert общего oracle (отсутствие
   строки SUCCESS для sortedness в terse summary не выдавать за явный PASS); unsorted-halves — requires
   `merge_inputs_are_sorted`; bounds — raw write за всей allocation 48. Старые номера строк не использовать.
7. **Бюджет поднят до $3,5** (3 сборки, не больше). До dispatch: T0, work-timeout inventory по известным list timings
   (10 мин уже давали timeout — брать с запасом, как G2/G3 INTEG), резерв закрытия; inventories можно отправить
   подряд/параллельно. Каждый следующий полный envelope — по фактическим spent+reserved; proof timeout не урезать. Если
   не помещается — PARTIAL с точным остатком.
8. **Один замороженный library tree после GO** для всех трёх запросов (у каждого свой RUN-REQUEST/request SHA/UUID);
   exact name sets обеих cfg сверить. Положительные перенесённые entry этим build не перепроверяются — это полный CI
   координатора. Library-правка после GO — delta-review.
