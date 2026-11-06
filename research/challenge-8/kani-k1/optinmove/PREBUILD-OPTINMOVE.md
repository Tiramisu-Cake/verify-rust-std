# OPTINMOVE — пакет PRE-BUILD review

Ветка `experiment/kani-k1-optinmove-20261106`, owner `k1-merge`.
Исходное дерево `01c090dc1d`; задание `6a17919511`.
Library `461dac0c43902c7a929e7164492ad4a5f84a4a3b`, tree
`f1d36898b962cb654e66f8b05c9fde7ef512a560`.
Подготовка не разрешает dispatch и не запускает окно стадии.

Из подачи удалены ровно 22 корня: realcontracts 8, permtags 10, scratchgeom 4.
[MOVED-OPTIN.md](MOVED-OPTIN.md) содержит все полные имена, публичные permalinks,
последние найденные source-reported статусы и способ воспроизведения на `44b972435a`.
[moved-statuses.json](moved-statuses.json) сохраняет точные excerpts наших RESULT.
Статус новых ordinary-вариантов с отключёнными covers не присвоен старым вариантам.
N32/default NOT_RUN; TIMEOUT другого N32/kissat не перенесён.

Удалены шесть исключительно исследовательских helpers, три исключительно их импорта
и permutation_case. Хелпер abort_on_order_violation в permtags оставлен для контроля.
Файлы не перемещены. scratchgeom сохраняет один proof и нужные helpers/макрос;
файлов с одним-двумя оставшимися элементами нет.

Все пять кандидатов из задания приняты с точным равенством раскрытых items:

- define_general_direct_harness заменён идентичным define_general_sortedness_harness;
- четыре general_stable_direct_u64_n2..n5 используют define_direct_u64_route_harness;
- два swap_contract_*_indices_n17 используют swap_contract_arbitrary_indices_case;
- dispatch_pair_route_safety_case заменён явной dispatch_safety_stable_bytes16_n32;
- define_merge_scratch48_contract_harness заменён явной merge_scratch48_contract_u8_n9.

Статика: `python3 -B research/challenge-8/kani-k1/optinmove/check_optinmove.py`.
Lexer/expander импортируются из существующих TIDYDOCS/TRIMPART без правки tooling.
Сравнение токенов строгое: сообщения, литералы, атрибуты и тела не нормализуются.
Проверяются 233 ordinary и 13 контролей, их консервативные closure и позиции covers,
все оставшиеся раскрытые items, имена обеих cfg и точный removed-set.
Унаследованный resolver связывает одноимённые private helpers разных модулей.
Его единственное удалённое ложное ребро — permtags::arbitrary_u64_order из merge.
Отдельная проверка доказывает отсутствие пути от сохранённых локальных корней
и отсутствие внешних путей/импортов этого модуля; merge::arbitrary_u64_order сохранён.
Это ограниченная проверка исходников, не compiler name resolution или новый proof.
smallsort.rs побайтно неизменён; нет новых строк >100 или запрещённой лексики в verify.

План компиляции — две сборки kind=inventory, без proof rows. G1 controls=false,
233 имени; G2 controls=true, 246 имён. Одна сборка не даёт оба compiler inventory:
diagnostic+inventory выполняет list до controls RUSTFLAGS. kind=inventory выставляет
нужный RUSTFLAGS до list. Обе стадии компилируют standard- и contract-harnesses.
Тела 246 сохранённых корней идентичны; дополнительных proof rows не требуется.

G1: [RUN-REQUEST.json](RUN-REQUEST.json), byte-identical верхнему RUN-REQUEST.json.
G2: [G2-RUN-REQUEST.json](G2-RUN-REQUEST.json), только подготовленный следующий пакет.
Оба request прошли существующий validate; runner standard4, harnesses=[], inventory=true.
44 мин whole-job work budget + 24 мин runner slack = cutoff 68 мин от validate;
платный timeout 44+30=74 мин. Известный inventory ~47 мин плюс setup/build ~6–8 мин
помещается с запасом ~13 мин до cutoff. Сама list-команда ограничена min(remaining,60 мин).
Это не короткий rows×t+30. Резерв на сборку 74×$0.0135=$0.999; две максимум $1.998≤$2.
Текущий project ledger: used $106.2825, reserve0, cap $118.96; обновить перед dispatch.
Окно после GO: main300 + closeout30 мин; timestamps в RUN-LEDGER перед запуском.
G2 запускать только после разбора G1, публикации отдельного exact-пакета и GO координатора.
Retry0; repair только в пределах задания, GO и собственного spent+reserve≤$2.

После GO G1: dispatch этой опубликованной ветки через k1g.sh, записать UUID,
`k1g.sh watch BUILD` и завершить ход. Не опрашивать status в цикле.
После уведомления: bounded summary, check-tooling против
`59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, inventory страницы по next_offset,
log-grep warnings/unused/verify и budget только своего UUID.
Сверить source/request/build/Kani/pool identities, COMPLETE и inventory gate.
Сравнить полный набор compiler names с ordinary-expected.txt / cfg-on-expected.txt.
Inventory сохраняет порядок list (standard затем contract), поэтому его native names SHA256
может отличаться от SHA256 статически отсортированного списка: записать native hash отдельно,
и вычислить SHA256 полного sorted списка для exact-set сравнения. Сравнивать также количество
и отсутствие дубликатов; raw cache/log/inventory файлы не читать, только bounded helper pages.
Нужны успешные обе cfg и отсутствие новых verify warnings; до этого RESULT остаётся PENDING.
Финальный RESULT≤40 строк, REVIEW REQUEST <sha> / OPTINMOVE ЗАВЕРШЁН и стоп.

## Решение координатора после review

Пакет `3b12f9cc0d2a11ab0a1a7df00e5aa93624c212cf` принят. GO только G1,
inventory controls=false, 233 имени, с указанного exact SHA. G2 в OPTINMOVE не запускать.
Cfg-on compiler inventory, компиляция и все 13 контролей отложены в единый
интеграционный пакет после этапа 3. При успешном G1 и принятой статике этап получает PASS;
отложенные проверки не объявляются выполненными. Подготовленный G2 request — исторический
артефакт review, а не активный план или разрешение dispatch. Это решение заменяет
требование двух inventory builds выше. Ожидание G1: k1g.sh watch BUILD, затем конец хода.

## Итог G1

G1 `242b83e1-d9bc-46d9-a504-1cd3e929fcf0`: SUCCESS, COMPLETE, gate=true, Kani exit0.
Compiler inventory ровно 233 ожидаемых ordinary-имени, дубликатов нет.
Source/request/Kani/pool/tooling привязки PASS; sorted names SHA256 совпал с ожидаемым.
Целевой verify/unused scan — no match; общий warning sample ограничен 200 совпадениями
и не является полной описью предупреждений. Расход $0.5805, reserve0, одна сборка.
Cfg-on inventory/компиляция/13 контролей — DEFERRED_TO_INTEGRATION_AFTER_STAGE_3.
Статус этапа PASS по решению координатора; новых proof rows/credit нет.
Evidence: [verification-report.json](evidence/verification-report.json).
