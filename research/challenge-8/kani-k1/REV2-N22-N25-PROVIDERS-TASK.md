# REV2 · опоры N22–N25 в форме FIX3

Задание для **w14 после допуска N20/N21**. Подготовь локально пакет для одного Ubuntu job. В нём 12 последовательных слотов: девять проверок sort9 и merge в нужных геометриях и три проверки фактических вставок на полных байтах. Сквозные корни и контроли N22–N25 запланированы следующим пакетом. Основа — [актуальный разбор FIX3-пар](REV2-MERGE-PAIR-FIXED-RESULTS-ANALYSIS.md), [карта N18–N31](REV2-N18-N31-PLAN.md) и [правило композиции](REV2-COMPOSITION-RULE.md).

## Пины и область

Работай в отдельных локальных worktrees от принятой базы N20/N21 consumer:

| Репозиторий | Commit | Tree | Parent |
| --- | --- | --- | --- |
| Std | `000e6c4bf6ef0436e83e745618c077d988543169` | `c79edb9b6caf4734907f31590b782f2698b7e647` | `f72f4303bacfff4706b20268a87b2a1031a8ee0b` |
| Control | `2404b83ff5adcc969939764f405670c00c0bfcaa` | `510af47eeb2689e8e27a20b44e881f5f624f00cf` | `8e1603eef95407eaf03bb592266d7513540682f8` |

Control наследует принятый стабилизированный `ch8-cal1/test_supervisor.py` с blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Создай новый независимый detached review-trigger от разрешённого sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, закрепи его отдельной переменной Actions вида `CH8_REV2_N22_N25_PROVIDERS_TRIGGER_TREE`; не переиспользуй переменные N20/N21. Сохрани fork `Tiramisu-Cake/kani`, ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1 и exact push payload SHA в gate.

Домен — инициализированный произвольный V34, `u8/KeyLess<u8>` с числовым `<` и независимый `q: u8`. Runtime `std`, actual sort/merge/copy код и существующие контракты сохраняются побайтно. Работай с actual functions и verification-only wrappers, без stubs, Replace и новых loop contracts. Оставь `u8` и `KeyLess<u8>` связанными с реальными source call sites. Scratch — отдельный writable `MaybeUninit<[u8; 32]>`; читай только записанные ячейки. Uninit и validity остаются OFF.

| N | m | Половины | Полный source slice | odd center |
| ---: | ---: | --- | --- | --- |
| 22 | 11 | left `[1..12]`, right `[12..23]` | `v[1..23]` | нет |
| 23 | 11 | left `[1..12]`, right `[12..24]` | `v[1..24]` | `k=11` |
| 24 | 12 | left `[1..13]`, right `[13..25]` | `v[1..25]` | нет |
| 25 | 12 | left `[1..13]`, right `[13..26]` | `v[1..26]` | `k=12` |

Индексы половин в таблице задают Rust-срезы с exclusive end. Для каждой длины сначала сверяй exact source call, compile-time N/m, extent, верхнюю цель и read offsets с pinned `smallsort.rs`. Не объединяй N22/N23 или N24/N25 в symbolic-N Check: даже при одинаковом m каждый FIX3 pair — отдельная specialization и exact N.

## Состав пакета

Добавь отдельный provider-модуль и cfg. Зафиксируй полный roster из 12 слотов до создания bundle и discovery. Слоты 1–9 проверяют sort9 и merge. Слоты 10–12 — отдельные `PLAIN_PROOF` фактических вставок на самых длинных хвостах. Все 12 запускаются последовательно в указанном порядке. Для каждого переноса явно запиши intended N и source edge; само наличие более длинного успешно проверенного driver не доказывает, что shorter actual путь выполнил те же записи.

| № | Slot / назначение | Точный результат и связь |
| ---: | --- | --- |
| 1 | `S9-B12-L12-BITS` | Actual `sort9_optimal` на `v[12..24]`: base 12, битовый префикс rel0–8 и произвольный хвост rel9–11. Проверить каноничность, отсортированную mask с тем же popcount, q и внешний frame; covers mixed input, inversion, actual comparator и достигнутый post. Привязать `S9-B12-L12` к правой половине N23. Для N22 same-base перенос L12→L11 обосновать внешним префиксным рассуждением: тот же guard, 25 пар rel0–8, никакого доступа к rel11. |
| 2 | `S9-B12-SWAP` | Check actual `swap_if_less` с прежним FIX3 контрактом на base 12, полном V34 и `0 ≤ a < b < 9`. Проверить min/max двух байтов, modifies ровно двух адресов, q и внешний frame, swap/no-swap, равные значения на разных позициях и normal return. Привязать к actual S9 specialization и 25 пар на B12. |
| 3 | `S9-B13-L12-BITS` | Actual `sort9_optimal` на `v[13..25]`: base 13, битовый префикс rel0–8 и произвольный хвост rel9–11. Те же каноничность/oracle/q/frame/covers, что в slot 1. Привязать exact L12 к правой половине N24. Для N25 точная правая геометрия закрывается имеющимся `S13-B13-L13-BITS`: сверить его pinned source и отсутствие хвоста после sort13; не считать L12 proof доказательством L13. |
| 4 | `N22-PAIR-FIXED` | Отдельный Check actual `merge_up`/`merge_down`, compile-time `N=22,m=11`, полный `0 ≤ k < 11`, численно упорядоченные половины и writable-only scratch. Используй постоянную FIX3 shape с точными N/m; при `a+b=c+d=k` up получает `(S+a, S+m+b, D+k)`, down — `(S+m−1−c, S+N−1−d, D+N−1−k)`. Проверить обе тройки курсоров, min/max, tie side, source/q frame и exact writes только в новых целях, точные read/write/disjoint границы и applicable grouped DFCC/safety properties обеих однобайтовых копий. Отдельные covers для `k=0,10`, полезного возврата, двух выбора каждой стороны и ties обоих направлений. |
| 5 | `N23-PAIR-FIXED` | Тот же набор obligations, но отдельная FIX3 specialization `N=23,m=11`; при `a+b=c+d=k` используй up `(S+a, S+m+b, D+k)`, down `(S+m−1−c, S+N−1−d, D+N−1−k)` и цели `D[k]`/`D[22-k]`. Не переносить N22 Check как substitute. Covers отдельно идентифицируют N23. |
| 6 | `N23-ODD-CENTER` | Check actual odd branch локальной source-bound транскрипцией при `N=23,k=m=11`. Предпосылки счётчиков и ровно одного остатка. Привязать source pointers, `wrapping_add(1)` sentinel и end guard к actual ветке; проверить выбранный байт, продвижение курсора, оба конечных равенства, source/q frame и modifies только `D[11]`. Covers обоих остатков, post-copy и исчерпания левой половины (`c=11`, sentinel `S−1`, остаток справа); sentinel не разыменовывать. |
| 7 | `N24-PAIR-FIXED` | Отдельный Check `N=24,m=12` в постоянной FIX3 shape; при `a+b=c+d=k` up получает `(S+a,S+m+b,D+k)`, down — `(S+m−1−c,S+N−1−d,D+N−1−k)`. Проверки pair, exact offsets/write set, grouped DFCC anchors и covers для `k=0,11`, возврата, выбора сторон и tie-направлений — раздельно для N24. |
| 8 | `N25-PAIR-FIXED` | Отдельный Check `N=25,m=12` в той же постоянной форме, с его собственными exact N25 offsets: up `(S+a,S+m+b,D+k)`, down `(S+m−1−c,S+N−1−d,D+N−1−k)` при `a+b=c+d=k`, и целью `D[24-k]`; все pair/DFCC/frame/covers obligations сохраняются отдельно от N24. |
| 9 | `N25-ODD-CENTER` | Отдельный odd Check `N=25,k=m=12`; те же source/sentinel/end-guard obligations, но точные границы N25. Проверить выбранный источник и `D[12]`, продвижение выбранного курсора, оба terminal equalities, source/q frame и modifies только `D[12]`. Covers обоих остатков, post-copy и исчерпания левой половины (`c=12`, sentinel `S−1`, остаток справа). Sentinel не разыменовывать. |
| 10 | `INSERT-B01-L12-BYTES` | Actual byte driver на base 1, максимальная левая геометрия L12 с offset 9. Доказать порядок полного среза, сохранение `count(<q)` и q/V34 frame. Покрыть нормальный возврат, отсутствие сдвига и сдвиги на всех rel9–11. Intended exact N24/N25; отдельно вывести L12→L11 перенос с префиксной отсечкой к левой половине N22/N23. Значит, B01/L12 покрывает left N24 и N25; не переносить его на правую половину. |
| 11 | `INSERT-B12-L12-BYTES` | Actual byte driver на B12/L12, offset 9. Intended exact N23; отдельно вывести L12→L11 префиксный перенос к N22 и exact фактическую запись. Проверить order, `count(<q)`, q/V34 frame, normal return и no-shift/full-shift covers. |
| 12 | `INSERT-B13-L12-BYTES` | Actual byte driver на B13/L12, offset 9, intended exact N24. Не назначать его N25: N25 right имеет L13 и закрывается парой `S13-B13-L13-BITS` и `S13-B13-L13-SWAP`. Проверить полный post/frame и no-shift/full-shift covers. |

Для N22–N25 правые S9 bases — только B12 и B13. Check `swap_if_less` нужен только на B12. Для B13 используй `S13-B13-L13-SWAP` из run `45688753097`. Сверь pin, исходник и call site B13 на rel0–8. Оба корня S13 для B13 описаны в [разборе геометрий](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md). N24 и N25 используют B01/L12 на левой половине; N25 справа использует prior-run exact S13 B13/L13 и не имеет хвоста после sort13. Левые S9 основы — B01 с переносом длины 11/12 по общему guard и неизменным префиксом из 25 сравнительных пар.

У трёх проверок вставок единственная предпосылка о данных — числовой порядок первых девяти байтов. Остальные байты и q независимы. Для переноса с L12 на L11 свяжи первые две вставки с фактическими rel9/10 через инвариант prefix-order, сохранение полных кратностей и границы записи каждой итерации. Третья вставка rel11 входит только в L12. Геометрия и проверки `copy_nonoverlapping` для короткого пути должны следовать из этого инварианта и фактических смещений. Зафиксируй exact intended N для каждого ребра: base1/L12 — N24/N25, с переносом на N22/N23; B12/L12 — N23, с переносом на N22; B13/L12 — N24. На N25 справа длина 13 и S13 leaf. Эти три проверки закрывают только рёбра вставок. Merge, copy-back и сквозной пост квалифицируются отдельно.

## Профиль, сроки и приёмка

- Одна `ubuntu-24.04` job, максимум 120 минут. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`; safety/overflow/unwind/undefined-function/assertion-reach ON, uninit/validity OFF. Лимиты каждого root: VT ≤120 с, cold wall ≤180 с, cap группы 4 GiB и Ubuntu reserve 2 GiB. Для каждого cold slot создай отдельные CWD, Cargo/Kani targets, TMPDIR и export; заложи 10 с reap, 5 с receipt и 10 с launch headroom. Сохрани atomic outcome/reap checkpoint до проекции, bounded receipt/retry и caps 4 MiB projection / 96 MiB artifact.
- Бюджет от общего epoch: setup/preflight/discovery 50:00; 12 слотов по 3:25 = 41:00; итоговая аттестация 2:00; finish 5:00; upload 7:00; резерв 9:00. Плановый итог — **114:00**, job limit — 120:00.

| Событие | Latest start / граница от epoch |
| --- | ---: |
| Готовность к запуску слотов после discovery и входного gate | 50:00 |
| Slot 1–12 latest start | 50:00, 53:25, 56:50, 60:15, 63:40, 67:05, 70:30, 73:55, 77:20, 80:45, 84:10, 87:35 |
| Все 12 slot windows завершены | 91:00 |
| Аттестация завершена | 93:00 |
| Finish завершён | 98:00 |
| Upload завершён | 105:00 |
| Резервный deadline плана | 114:00 |
| Жёсткая граница job | 120:00 |

Сохрани абсолютные границы от job epoch. После раннего завершения setup можно запустить первый слот раньше, сохранив все полные окна по 205 с. После неподтверждённого reap следующие слоты получают явную причину пропуска. Внутренний бюджет `measure` равен 44:05 с учётом 12×205 с на слоты, 120 с на аттестацию, 60 с на входной gate и 5 с на журнал. Внешний таймаут шага — 46 мин. Для входного gate оставь 60 с до latest start первого слота. Абсолютные границы слотов, аттестации и публикации из таблицы действуют и при более позднем входе в шаг. В handoff запиши внутренние и внешние границы `prepare`, `measure`, `finish` и `upload`.

- В `pins`, `sources`, `finish` сверяй независимый tree через новую переменную, clean detached checkout, sole parent, fork/ref/attempt, exact payload SHA и все pinned source blobs/координаты, включая столбцы. В предусмотренном runner workflow выполни overlay compile preflight до exact discovery и сохрани первые rustc diagnostics как данные. Discovery должен показать точную cfg-off/on delta всех 12 roots с exact selector/kind/file и объектом каждого Check. В итоговых receipts сохраняй native ID/Location/Status, phase/CNF, VT/wall, group и CBMC RSS, sampler/reap, обязательные covers, anchors и финальную аттестацию.
- Для всех четырёх pair Check сверяй выбранный `actual_pair_step_nN` и grouped native DFCC anchors `memcpy.assigns.1/.2` плюс применимые grouped `ptr::copy_nonoverlapping::<u8>` свойства на pinned `ptr/mod.rs:587:14`: alignment, byte-length overflow, disjoint/readable/writable. Actual вызовы связывай по pinned source coordinate и достигнутым cursor/post covers. Сохраняй оговорку о возможном недоучёте Linux group RSS при смене worker TID.
- `PROVIDERS_WITHIN_PROFILE` допускается только при всех 12 exact roots `VERIFIED`, exit 0, `MATCHED`, полном наборе covers, timely complete receipts, подтверждённом sampler/reap и завершённой аттестации. Успешный provider-run — диагностическое свидетельство, `proof_credit=NONE`.
- Эта задача остаётся локальной подготовкой. Не отправляй CI, не делай push, не меняй Actions variables, не запускай локально cargo/rustc/Kani/CBMC. Сделай статические сверки источника, cfg/видимости, runtime diff, coordinate gates, request/roster/windows, `git diff --check`, YAML/`bash -n` и синтетические проверки gate/roster/selector/kind/Check/covers/late receipt/reap; тестовые наборы, если нужны в локальной подготовке, запускай последовательно на обычной и свежих шкалах 1/5/60 с. Для исторических опор используй опубликованные структурированные receipts, projections и индексы.
- Сдай `REV2-N22-N25-PROVIDERS-HANDOFF.md`: exact source blobs/coordinates, геометрии и рёбра по N, worktree/commit/tree/parent Std/control/trigger, независимую переменную tree, SHA-256 request/roster/bundle, roster, все step windows, preflight/discovery и статические/синтетические результаты. Статус — `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`; затем требуется отдельное ревью и GO. Любые локальные commit messages не должны содержать `#` непосредственно перед цифрой; употребляй `pr752`, `kani5196`, `issue56`.
