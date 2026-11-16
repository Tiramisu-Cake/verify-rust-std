# S1-05 intake — run 43864841077

Вход g0 `43c470084c`; executed control `8860d38558651f7cf2e292d57b06b378c6ad3b94`, std `5be85699b8826e3286c0bf89efb9affefac0acb5`, stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`.

**14/14 artifacts получены; 35/35 stock harness завершены: 27 SUCCESS, 8 FAILURE. Это source-reported observations, не независимый proof credit.** Полный rich inventory есть только у 4 групп / 9 строк; у 10 групп / 26 строк metadata неполны. `collected.json` сохраняет raw verdict каждой строки отдельно от исходного runner UNKNOWN.

| Группа | Строк | child exit | elapsed s | group RSS KiB | rich |
|---|---:|---:|---:|---:|---|
| activation-default-u34 | 1 | 1 | 40.822 | 1933824 | COMPLETE |
| activation-override-u34 | 1 | 1 | 60.169 | 1932928 | INCOMPLETE |
| cell-u34 | 2 | 0 | 774.137 | 8131836 | COMPLETE |
| freeze_copy_u8-n01-u34 | 2 | 0 | 68.400 | 2660016 | INCOMPLETE |
| freeze_copy_u8-n23-u34 | 2 | 0 | 112.974 | 2613052 | INCOMPLETE |
| freeze_default_noncopy-n01-u34 | 2 | 0 | 64.435 | 2680520 | INCOMPLETE |
| freeze_default_noncopy-n23-u34 | 2 | 0 | 245.328 | 2601360 | INCOMPLETE |
| light-controls-u34 | 9 | 1 | 116.651 | 2376692 | INCOMPLETE |
| light-corruption-u4 | 3 | 1 | 41.632 | 1935308 | COMPLETE |
| light-model-u5 | 3 | 0 | 38.116 | 2626032 | COMPLETE |
| stable_freeze_u8-n01-u34 | 2 | 0 | 45.519 | 2653952 | INCOMPLETE |
| stable_freeze_u8-n23-u34 | 2 | 0 | 281.126 | 2635136 | INCOMPLETE |
| unstable_freeze_u8-n01-u34 | 2 | 0 | 66.578 | 2681084 | INCOMPLETE |
| unstable_freeze_u8-n23-u34 | 2 | 0 | 91.177 | 2676652 | INCOMPLETE |

Общий driver elapsed 2047.064 s (включает compile); отдельно compile upper bounds 518.626 s, их нельзя прибавлять повторно. Per-harness verification_time_s записан stock; отдельные per-root process exit/wall/RSS не измерялись и оставлены UNKNOWN. RSS — sampled process-group peak. У всех групп завершён compile marker, нет timeout/signal/output cap, source_before/after совпадают с request. У 10 failed decoder-групп послеобходной fingerprint binaries не достигнут; это отдельный незакрытый gate.

Причина heavy: все 8 child exits = 0, но `RegularEvidence` выбросил `file/line missing`; `_run_group` сохранил FAILED и UNKNOWN, runner exit1. Аналогично повреждены light-controls и activation-override: их child exit1 совпадает со stock FAILURE, однако CI failure вызван также потерей rich metadata, а не корректно принятой негативной проверкой. Activation-default и light-corruption имеют child exit1, но runner/job success: сборщик только записывает observations.

9986 stock properties против 2976 сохранённых rich records. Все 10 декодеров остановились после `.assertion.5` функции `small_sort_general_with_scratch` (source line291), затем отвергли очередную location. Это координата последнего сохранённого свойства, **не** координата дефекта или доказательство причинности. Rejected block удаляется до исключения и не попал в head/tail previews. Точный rejected display, тип отсутствующего поля и binding следующего свойства UNKNOWN; предположение «line0» или «Unknown file» не установлено. Полные raw logs не читались. `BOUNDED-EXCERPTS.json` фиксирует только bounded job boundary и совпавший payload SHA.

Локальный fix `b25dd39a46ba90b167500997d546a5f2f5bd8f3b`: декодер сохраняет валидные stock records с отсутствующими координатами как nullable, original location display и diagnostics; продолжает suffix и следующие harness; затем проверяет точный inventory и по-прежнему отказывает completeness при любом missing site, включая collector replay. Runner печатает terminal blocker. Это исправление потери evidence; оно не восстанавливает утраченное evidence текущего run и не устраняет отсутствующие source locations в stock output. Rich acceptance остаётся fail-closed. Единственный parent40b5d9, прежние depth3/YAML/attempt1/paths/pins/checks/oracles/budgets сохранены; изменены только decoder, reporting, synthetic test и payload hashes.

47 Python synthetic/service/Git/YAML регрессий PASS (26.850 s), локальный package preflight PASS; независимый Luna HIGH review — `fix/REVIEW.md`, actionable findings нет. Actual compiler/proof/CI/rerun NOT_RUN. Bundle требует Kani parent40b5d9; проверен в Kani worktree.

Офлайн-приёмка завершена: **0 qualified; 3 exact negative observations**. Все41 required covers exact-bound SAT;4/35 required-success messages связаны с unique SUCCESS property, остальные31 PENDING. 25 unreachable roles UNKNOWN,20 postcondition sites с negative-scenario applicability PENDING;3 PFC wrapper chains и rich companion activation-default также не закрыты. Это не установленные mandatory blockers по одному имени функции. См. `accept/ACCEPTANCE.md` и `accept/ACCEPT.json`. Независимый proof credit NONE; исторические verdicts/receipts/ledgers не изменены.
