# REV2 · шаги merge и нечётные центры N26–N31

Задание для **w15**. Подготовь офлайн один Ubuntu-пакет из пяти exact FIX3 pair Check N26–N30 и трёх odd-center Check N27/N29/N31. Для N31 pair уже есть `M31-PAIR-FIXED` из `45785063793`. Запуск после независимого ревью и отдельного GO, Item 2, `proof_credit=NONE`. Место в очереди определит координатор с учётом пакета валидности. [Допуск опор половин](REV2-N26-N31-HALVES-ADMISSION.md) · [План](REV2-N22-N25-PROVIDERS-RESULTS-ANALYSIS.md#после-consumers-n22n25-n26n31)

## Базы и область

Работай в отдельных worktrees от принятых N26–N31 halves FIX1. [Пины и артефакты](REV2-N26-N31-HALVES-HANDOFF.md#fix1)

| Репозиторий | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Std | `ea34c58ab95b4cbccd9acaa3080597b8b2517a87` | `75c4a374a0c906c989e2770a26990c7cdc6cdf83` | `8fe1b01f0a85ee60118d1813d6b74645e4594213` |
| Control FIX1 | `302604ce810495c342282fba17cbdaea9aaf8cc5` | `b235397dd83b5ee85a53d56ebe40e01f547e8403` | `fd941d949379ac437b9071cf9a1e636ae72aee5b` |

Инициализированный произвольный V34, `S=&v[1]`, переданный source `v[1..1+N]`, `u8/KeyLess<u8>` с числовым `<` и независимым `q: u8`. `D` — отдельная writable `MaybeUninit<[u8;32]>`, читать только гарантированно записанные ячейки. Runtime Std, контракты, старые опоры и тесты supervisor остаются побайтно прежними. Добавь verification-only модуль `rev2_n26_n31_merge` под `kani_smallsort_rev2_n26_n31_merge`. Используй actual вызовы, без stubs, Replace и loop contracts.

| № | Слот | Exact source, область и цели |
| ---: | --- | --- |
| 1 | `N26-PAIR-FIXED` | `v[1..27]`, `m=13`, `k=0..12`, D[k] и D[25−k] |
| 2 | `N27-PAIR-FIXED` | `v[1..28]`, `m=13`, `k=0..12`, D[k] и D[26−k] |
| 3 | `N28-PAIR-FIXED` | `v[1..29]`, `m=14`, `k=0..13`, D[k] и D[27−k] |
| 4 | `N29-PAIR-FIXED` | `v[1..30]`, `m=14`, `k=0..13`, D[k] и D[28−k] |
| 5 | `N30-PAIR-FIXED` | `v[1..31]`, `m=15`, `k=0..14`, D[k] и D[29−k] |
| 6 | `N27-ODD-CENTER` | `v[1..28]`, `m=13`, D[13], sentinel source S+26 |
| 7 | `N29-ODD-CENTER` | `v[1..30]`, `m=14`, D[14], sentinel source S+28 |
| 8 | `N31-ODD-CENTER` | `v[1..32]`, `m=15`, D[15], sentinel source S+30 |

## Что проверяет каждый Check

- **Pair FIX3.** Отдельный `actual_pair_step_nN` для каждого N с постоянными N и m. При `a+b=c+d=k` вызовы получают `(S+a,S+m+b,D+k)` и `(S+m−1−c,S+N−1−d,D+N−1−k)`. Сохрани constraints на счётчики, readable source, writable D, disjoint и `modifies` ровно двух новых целей. Предположение числового порядка половин помещай только в harness. В `requires` обёртки его не добавляй. У каждого Check пост включает обе тройки курсоров, min/max, tie-left у up и tie-right у down, q и source frame, exact read/write bounds. Сохрани десять covers из FIX1 N22–N25, включая exact actual comparator, `k=0,m−1`, normal return, выбор обеих сторон каждым вызовом и ties. [Ревью FIX1 формы](REV2-N22-N25-PROVIDERS-REVIEW.md#r2--fix1) · [Пример exact pair](REV2-MERGE-PAIR-FIXED-RESULTS-ANALYSIS.md)
- **Odd center.** Отдельная source-bound транскрипция actual ветки для каждого N. После m пар `a+b=c+d=m`, остатки `(m−a−c,m+1−b−d)` из `{(1,0),(0,1)}`. Привяжи `wrapping_add(1)`, `left<left_end`, выбранный pointer и значение, однобайтовый copy в D[m], продвижение выбранного курсора и оба равенства end guard. Write set только D[m], q/source frame. Четыре covers — оба положения остатка, post-copy и `c=m` с правым остатком. В последнем случае `left_rev=S−1` используется только для `left_end=S`, читается `S+N−1`. Подставь счётчики из ранговой индукции и сверь обе ветки и точный call site `smallsort.rs:1027–1042`. Вывод о заполнении scratch перед чтением отмечай как внешний при uninit OFF. [Прецедент N23/N25](REV2-N22-N25-ADMISSION.md#нечётные-центры)
- **Нативная привязка.** Зафиксируй exact selector/kind/Check target/file, контрактный символ stock, regular ID/Location/Status и covers каждой специализации. Для пар нужны выбранные cursor anchors и `memcpy.assigns.1/.2`. Для всех копий сверяй применимые grouped `ptr::copy_nonoverlapping::<u8>` на `ptr/mod.rs:587:14`: две проверки выравнивания, переполнение длины в байтах и disjoint/readable/writable. Свяжи их с actual вызовами, scope записей и успешными unwind checks. `copy_back=false` у всех восьми merge roots. Для `M31-PAIR-FIXED` переиспользуй exact `45785063793` после сверки profile, index, receipt/projection SHA-256, actual runtime, компаратора, ptr и Check-модуля. [Grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md) · [N31 pair](REV2-MERGE-PAIR-FIXED-RESULTS-ANALYSIS.md#приёмка-run-45785063793)

В handoff свяжи посты принятых половин с sorted fixture domain. Ранговая индукция по `(byte, индекс в S после вставок)` должна связывать пять новых exact pair и прежний N31 pair с полным диапазоном k actual цикла. Отдельно покажи, что крайние кандидаты из уже исчерпанной половины проигрывают выбор, а цели D[k] и D[N−1−k] различны. У чётных длин после m шагов обе границы сходятся. У нечётных в ранг m подставляется отдельный odd Check. Это обоснование всего merge на составном графе. Для сквозного пакета остаются exact copy-back/frame и различающий контроль каждой длины.

## Профиль и часы

Одна `ubuntu-24.04` job до 120 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, safety/overflow/unwind/undefined-function/assertion-reach ON, uninit/validity OFF. На слот 180 с cold wall, 10 с reap, 5 с receipt и 10 с launch headroom. Отбор VT ≤120 с, cap группы 4 GiB, резерв 2 GiB. Сохрани отдельные холодные targets/CWD/tmp/export, атомарный checkpoint результата и reap до проекции, ограниченный retry, caps 4 MiB/96 MiB и оговорку о sampled RSS Linux. [Лимиты](OWNER-DECISION-LIMITS-20261125.md)

Setup расширен на 5 мин: в halves run до прежней границы prepare оставалось 49,4 с. Все границы от одного monotonic job epoch. Latest starts восьми слотов: 55:00, 58:25, 61:50, 65:15, 68:40, 72:05, 75:30, 78:55. [Замер setup](REV2-N26-N31-HALVES-ADMISSION.md#run-45846512615)

| Стадия | Абсолютная граница | Внешний timeout шага |
| --- | ---: | ---: |
| `prepare` с compile preflight и discovery | 54:00 | 56 мин |
| Входной gate / первый latest start | 55:00 | внутри `measure` |
| Конец слотов / аттестации | 82:20 / 84:20 | `measure` 32 мин |
| Общий cutoff `finish` / `upload-gate` | 89:15 | finish 6 мин |
| Конец upload | 96:20 | upload 7 мин |
| План с резервом и предел job | 105:20 / 120:00 | job 120 мин |

Внутренний `measure` — 30:25 от входа, 8×205 с, 120 с аттестации, 60 с gate, 5 с журнал. Finish до 5 мин от входа и до общего cutoff, затем 5 с на переход к upload. При неподтверждённом reap останови последующие слоты. Поздний receipt сохраняет наблюдение без допуска. `PROVIDERS_WITHIN_PROFILE` требует восемь `VERIFIED` exit 0 и `MATCHED` со всеми нативными anchors, covers, своевременными полными receipts, подтверждённым sampler/reap и финальной аттестацией `COMPLETE`.

## Проверки, сдача и следующий пакет

- Новый независимый pin `CH8_REV2_N26_N31_MERGE_TRIGGER_TREE` для `pins/sources/finish`. Сохрани fork `Tiramisu-Cake/kani`, push `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, точный payload SHA, clean detached checkout, tree равный control, sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Ранний compile preflight сохраняет первые ошибки rustc и предшествует долгому discovery. Cfg-off/on дельта — ровно восемь Check с заданными целями, старый инвентарь сохранён. Upload следует после пройденных gates и finish.
- Сверь Rust-видимость, cfg и runtime diff, `rustfmt --check`, YAML, `bash -n`, `git diff --check`, bundle на чистом shallow base. Сохрани `test_supervisor.py` blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Suite запускай последовательно на обычной и свежих шкалах 1/5/60 с. Синтетика проверяет guards, точный N и Check target/kind, wrong tree/payload, неверный столбец, потерю группового якоря или sentinel cover, `copy_back=true`, поздний receipt, общий cutoff и потерю reap. Локально без cargo, rustc, Kani, CBMC, CI, push и изменений Actions variables.
- Сдай `REV2-N26-N31-MERGE-HANDOFF.md` с `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Включи frozen roster, исходные blobs/координаты и рёбра N26–N31, проверку `M31-PAIR-FIXED`, worktrees, commit/tree/parent Std, control и локального review-trigger, Actions variable, SHA-256 request/roster/bundle/bindings, часы и результаты проверок. Следом независимое ревью и GO.
- После merge отдельный сквозной пакет с actual network, exact copy-back/frame и post-return контролем на каждой N. **Первый positive и контроль — N31**, затем N26 без вставок и N27 с нечётным центром, затем N28–N30. Сохрани измерения первой CNF, phase, group/CBMC RSS и PSS. Если широкий positive выйдет за 120 с VT или 4 GiB, сохраняем наблюдение и отдельный контроль. Для составного допуска закрываем открытые exact native copy-back/frame рёбра коротким корнем по прецеденту N32. На 12 сквозных слотов при новом setup 55 мин расчётный план 119 мин с 9-минутным резервом. [Ресурсный ориентир](REV2-N22-N25-ADMISSION.md#запас-памяти-для-n26n31) · [Прецедент N32](REV2-N32-ADMISSION.md)

Для каждого нового коммита в Std, control, локальном review-trigger и g0 явно передавай `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com` перед `commit` или `commit-tree`. Проверь author и committer через `git show -s --format='%an <%ae> | %cn <%ce>'` до заморозки SHA и в handoff. Локальные коммиты с `[skip ci]`. Во всех commit messages, включая research, ledger, control и trigger, запрещён знак решётки непосредственно перед цифрой. Используй `pr752`, `kani5196`, `issue56`.
