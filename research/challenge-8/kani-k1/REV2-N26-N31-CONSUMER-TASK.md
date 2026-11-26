# REV2 · сквозные N26–N31 с контролями

Задание для **w15**. Подготовь офлайн один Ubuntu-пакет из 12 exact singleton: по одному фактическому битовому Proof и post-return контролю на каждую N26–N31. Первая пара — **N31**, затем N26, N27, N28, N29, N30. Валидность идёт в отдельном пакете. Место в fork lane определит координатор после независимого ревью и отдельного GO. Item 2, `proof_credit=NONE`. [Допуск половин](REV2-N26-N31-HALVES-ADMISSION.md) · [Допуск merge-шагов](REV2-N26-N31-MERGE-ADMISSION.md)

| Локальная база | Commit | Tree |
| --- | --- | --- |
| Std merge | `71953c45a9a38cff3538c8a5e413890efc896d70` | `f59ea89d61b25e34f06f9b14d61ad48694b86950` |
| Control merge | `108c45668b1c8aa41a6f0ae228697a639ad54933` | `e4997c4c94ba6b0ce426f4e2fdbbb86c38de05d7` |

Отдельные worktrees. Runtime Std, контракты, существующие опоры и старый cfg-off инвентарь сохраняются побайтно. Добавь verification-only `rev2_n26_n31_consumer` под `kani_smallsort_rev2_n26_n31_consumer` с унаследованными cfg. [Пины merge](REV2-N26-N31-MERGE-HANDOFF.md#пины-и-входы)

## Составные рёбра

Общий домен — actual `small_sort_network::<u8, KeyLess<u8>>` на живом инициализированном V34, точный активный `v[1..1+N]`, произвольные полные байты, числовое `<`, независимый `q: u8`. Для каждого ребра зафиксируй исходник и координату actual вызова, мономорфизацию, геометрию, предпосылки и пост, нативные ID и SHA-256 receipt/projection в индексе. [Правило композиции](REV2-COMPOSITION-RULE.md)

| N | S13 и вставки | Merge | Последний copy-back |
| ---: | --- | --- | --- |
| 31 | `v[1..16]` B01 L17→L15, `v[16..32]` exact B16/L16. Rel13–14 / 13–15. | `M31-PAIR-FIXED` (`45785063793`) и `N31-ODD-CENTER`, D[15] | 31 байт |
| 26 | `v[1..14]` exact B01/L13, `v[14..27]` B14 L14→L13. Вставка пуста с обеих сторон. | `N26-PAIR-FIXED`, 13 пар | 26 байтов |
| 27 | `v[1..14]` exact B01/L13, `v[14..28]` exact B14/L14. ∅ / rel13. | `N27-PAIR-FIXED` и `N27-ODD-CENTER`, D[13] | 27 байтов |
| 28 | `v[1..15]` B01 L17→L14, `v[15..29]` B15 L15→L14. Rel13 / 13. | `N28-PAIR-FIXED`, 14 пар | 28 байтов |
| 29 | `v[1..15]` B01 L17→L14, `v[15..30]` exact B15/L15. Rel13 / 13–14. | `N29-PAIR-FIXED` и `N29-ODD-CENTER`, D[14] | 29 байтов |
| 30 | `v[1..16]` B01 L17→L15, `v[16..31]` B16 L16→L15. Rel13–14 / 13–14. | `N30-PAIR-FIXED`, 15 пар | 30 байтов |

- Каждую B14/B15/B16 свяжи с exact нативным S13 bits и своим swap Check из `45846512615`. Внешние шаги — перенос по длине и пороговый подъём по 45 парам. Для B01 сверь прежний лист и битовые опоры. Левая вставка использует префикс исторического B01/L16, правая — внешний перенос B17→B14/15/16 вместе с индукцией по actual циклу. В handoff укажи rel и собственный end каждого короткого пути. Нативный cover исторических вставок относится к rel13. Сдвиги поздних rel, write bounds и полные кратности при переносе обосновываются по исходнику. [Составной допуск половин](REV2-N26-N31-HALVES-ADMISSION.md#привязка-полного-байтового-домена)
- Stock Check каждой пары и нечётного центра привяжи к `smallsort.rs:424` и `:1014–1042`. Ранговый вывод по `(byte, индекс после вставок)` заполняет D[0..N] в числовом порядке и сохраняет полные кратности. Для N27/N29/N31 отдельно сверь обе позиции остатка и sentinel `left_rev=S−1`, который используется только в `wrapping_add(1)` и приводит к чтению `S+N−1`. Полнота записи scratch перед чтением — внешний вывод при uninit OFF. [Ранговый аргумент и нативные опоры](REV2-N26-N31-MERGE-ADMISSION.md#привязка-нативных-опор-к-actual-циклу)
- Actual `ptr::copy_nonoverlapping(scratch_base,v_base,N)` на `smallsort.rs:425:9`. Scratch32 и V34 раздельны, байтовый size/alignment 1, назначение writable, первые N байтов scratch записаны по рангам. На каждом positive и контроле требуй reached `AFTER_COPY_BACK` и grouped `.safety_check.1/.2`, `.arithmetic_overflow.1`, `.precondition_instance.1/.2/.3` для `ptr::copy_nonoverlapping::<u8>` на `ptr/mod.rs:587:14`. В frozen roster всех 12 `copy_back=true`. Привяжи grouped свойства к последнему actual вызову с exact N и тем же расположением областей на полном байтовом домене. Конечный пост — числовой порядок, исходное полное мультимножество, прежние `q`, `v[0]` и `v[1+N..34]`. [Прецедент copy-back](REV2-N22-N25-ADMISSION.md#привязка-к-полным-байтам) · [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

## Двенадцать корней и witness masks

Plain Proof, по одному общему helper для двух специализаций каждой N. Имена по образцу `n31_actual_bits` и `n31_witness_corrupt`, слоты `N31-ACTUAL-BITS` и `N31-WITNESS-CORRUPT`. Positive задаёт N независимых битов. Внешние байты V34 и q произвольны у обоих корней. Actual вызов выполняет весь маршрут без stubs, Replace и loop contracts. Контроль задаёт конкретную входную маску, выполняет тот же actual вызов и меняет `v[1] ^= 1` после возврата и covers. Оба используют один канонический sorted-popcount oracle и отдельные q/frame assertions.

| N | Маска контроля | Ожидаемый пост → после порчи | Positive: левый остаток / правый sentinel |
| ---: | --- | --- | --- |
| 31 | `0x0000_8001` | `0x6000_0000` → `0x6000_0001` | `0x4000_7fff` / `0x0000_7fff` |
| 26 | `0x0000_2001` | `0x0300_0000` → `0x0300_0001` | ∅ |
| 27 | `0x0000_2001` | `0x0600_0000` → `0x0600_0001` | `0x0400_1fff` / `0x0000_1fff` |
| 28 | `0x0000_4001` | `0x0c00_0000` → `0x0c00_0001` | ∅ |
| 29 | `0x0000_4001` | `0x1800_0000` → `0x1800_0001` | `0x1000_3fff` / `0x0000_3fff` |
| 30 | `0x0000_8001` | `0x3000_0000` → `0x3000_0001` | ∅ |

В каждой паре сначала positive `VERIFIED`, exit 0, затем контроль `FAILED`, exit 1, с единственным отказом `REV2_Nxx_ACTUAL_CANONICAL_SORTED_POPCOUNT`. Сверь ID, класс, метку, файл/строку и столбец regular и согласование stock. Остальные обязательные проверки, включая q/frame, copy и unwind, успешны. Нативный `AFTER_COPY_BACK` подтверждает actual возврат. Покрытие входных предикатов привязывай к path только офлайн, как в N22–N25. [Прецедент контроля](REV2-N22-N25-ADMISSION.md#сверка-сквозного-пакета)

Пять covers у каждого корня — actual comparator, `AFTER_COPY_BACK`, mixed input и по одному `one at rel0 / rest zero` для каждой половины. Каждый такой префикс S13 содержит инверсию. После S13 единственная единица находится на rel12. Каждый нулевой хвост, если он есть, сдвигает её на одну позицию. В N26 обе вставки пусты. У odd positive ещё два covers: левый остаток на левой маске и правый с `c=m` на sentinel-маске из таблицы. Левый свидетель даёт `(0,m,m−1,1)` и источник S. Sentinel даёт `(0,m,m,0)` и источник S+N−1. Odd control имеет один дополнительный cover правого остатка на своей маске, счётчики `(m−1,1,1,m−1)` и источник S+m+1. Итого 5/5 обязательных covers для чётной пары и 7/6 для нечётной. Проверь маски, порядок actual 45 пар, сдвиги, счётчики, группу copy и координаты до заморозки. [Форма конкретного контроля N32](REV2-N32-ADMISSION.md#привязка-строки)

## Три замечания ревью merge

1. **Discovery.** В `ch8-cal1/run.py::check_overlay_roster` верни проверку `not targets` для новых standard harnesses вне карт `*_CHECKS`. Сохрани исторические Check-объекты, включая `MERGE_CHECKS`, при расширении карт модулей и cfg-off/on baseline. Синтетика должна отклонить добавленный contract target при правильных selector/kind/file и принять прежние exact Check. [Код](/root/kani-rev2-n26-n31-merge-control-w15/ch8-cal1/run.py:269)
2. **Комментарий о нативной привязке.** У `results.py:227` укажи, что function из ID проверяет согласованность двух полей regular. Независимые якоря — frozen `_checked_property` regex по `target_instance`, stock target/symbol, строка `modifies` и столбец 1. Сохрани эти проверки при переносе исторических bindings в consumer. [Код](/root/kani-rev2-n26-n31-merge-control-w15/ch8-cal1/results.py:219)
3. **Odd q-frame.** В таблице рёбер укажи, что `less` из odd fixture не передаётся в wrapper, поэтому его локальный `Q_FRAME` не служит свидетельством изменения или сохранения q в actual сети. Нечётная транскрипция привязана к `smallsort.rs:1027–1036`, два равенства actual guard на `:1042` проверяются в harness отдельно. Из отсутствия компаратора в odd ветке следует внешний q-frame, а whole-network `less.q()==q` проверяется нативно до допуска каждой строки. Исторические опоры и receipts остаются со своими пинами. [Ревью трёх замечаний](REV2-N26-N31-MERGE-REVIEW.md#неблокирующее)

## CI-профиль, проверки и сдача

- Один `ubuntu-24.04` job до 120 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, safety/overflow/unwind/undefined-function/assertion-reach ON, uninit/validity OFF. 180 с cold wall + 10 с reap + 5 с receipt + 10 с launch headroom. Лимиты ≤120 с VT, 4 GiB группы, резерв 2 GiB. Сохрани cold CWD/targets/tmp/export, checkpoint исхода и reap до проекции, bounded retry, caps 4/96 MiB и sampled RSS caveat.
- Setup до **54:00** от epoch с ранним compile preflight и первыми ошибками rustc, внешнее окно prepare 56 мин. Входной gate до 55:00. Latest starts: 55:00, 58:25, 61:50, 65:15, 68:40, 72:05, 75:30, 78:55, 82:20, 85:45, 89:10, 92:35. Конец слотов 96:00 и аттестации 98:00. Внутренний measure 44:05, внешний 46 мин. Общий cutoff finish/upload-gate 102:55, абсолютный конец upload 110:00. Finish до 5 мин от входа, внешние таймауты finish/upload 6/7 мин. План 119:00 с резервом 9 мин. Не сокращай абсолютные окна последующих корней ретраем или задержкой receipt.
- Независимый `CH8_REV2_N26_N31_CONSUMER_TRIGGER_TREE` в `pins/sources/finish`, fork `Tiramisu-Cake/kani`, push `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, exact payload SHA, clean detached checkout, tree равный control и sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Дельта discovery строго 12 plain Proof. `CONSUMER_PAIRS_WITHIN_PROFILE` требует 12 `MATCHED`, подтверждённые sampler/reap, полные своевременные anchors и attestation `COMPLETE`. Если N31 positive упирается в лимит, сохрани native исход и phase/CNF, group/CBMC RSS и PSS. После подтверждённого reap запусти предусмотренный отдельный N31 контроль и остальные слоты в своих окнах. Без reap последующие слоты останавливаются. Внепрофильный результат остаётся в receipts. Составной маршрут с отдельным exact copy-back/frame корнем рассматривается после анализа, как для N32. [Оценка N31](REV2-N22-N25-ADMISSION.md#запас-памяти-для-n26n31) · [Лимиты](OWNER-DECISION-LIMITS-20261125.md)
- Проверь Rust-видимость, cfg и runtime diff, rustfmt, YAML, `bash -n`, `git diff --check`, bundle на чистой shallow базе. Сохрани `test_supervisor.py` blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Suite последовательно на обычной и свежих шкалах 1/5/60 с. Синтетика охватывает три замечания там, где меняются гейты, а также tree/payload, координаты, лишний failure, потерю copy/odd cover, late receipt, cutoff finish/upload и неподтверждённый reap. Локально без cargo, rustc, Kani, CBMC, CI, push и изменений Actions variables.
- Сдай `REV2-N26-N31-CONSUMER-HANDOFF.md` с `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Включи exact roster, masks и covers, source blobs/координаты, таблицу рёбер и gaps, worktrees, commit/tree/parent Std, control и локального review-trigger, Actions variable, SHA-256 request/roster/bundle/bindings, часы и проверки. Затем независимое ревью и отдельный GO.

Для каждого нового коммита в Std, control, локальном review-trigger и g0 явно передавай `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com` перед `commit` или `commit-tree`. Перед заморозкой SHA и в handoff проверь author и committer через `git show -s --format='%an <%ae> | %cn <%ce>'`. Локальные коммиты с `[skip ci]`. Во всех commit messages, включая research, ledger, control и trigger, запрещён знак решётки непосредственно перед цифрой. Используй `pr752`, `kani5196`, `issue56`.
