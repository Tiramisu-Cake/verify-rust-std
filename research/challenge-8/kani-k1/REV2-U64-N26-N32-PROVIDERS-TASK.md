# REV2 · опоры сети `u64` N26–N32

Задание для **w13** до `READY_FOR_REVIEW`. Подготовь один Ubuntu-пакет из восьми опор sort13 и десяти локальных проверок merge. Item 2, `proof_credit=NONE`. Подготовка идёт параллельно с consumer N22–N25 в отдельных worktrees. Локально без CI, push или изменения Actions variables. Независимое ревью, отдельный GO и очередь координатора предшествуют запуску. [Правило композиции](REV2-COMPOSITION-RULE.md)

Основа выбора — `45967622962/1`, 13/13 `VERIFIED/MATCHED`, аттестация `COMPLETE`. Четыре pair Check заняли 55,189–61,381 с VT и 91,246–97,855 с cold, CBMC до 923 888 KiB. Первая CNF пары около 379 тыс. переменных и 2,46 млн дизъюнктов. B13 S13 bits прошёл за 47,782 с VT при 2 576 460 KiB группы. Для m13–16 сохраняем ту же форму exact пары. Стоимость при этих m проверит прогон. Обе группы опор помещаются в один job на 140 мин с общим setup. У каждой правой базы будет собственная нативная опора S13, что оставляет для ревью переносы по длине и отдельные переносы вставок. [Индекс и 47 сверенных членов](/root/ch8-artifacts/run-45967622962/ch8-rev2-u64-n22-n25-providers-Linux-X64-45967622962-1/index.json) · [Сводка](/root/ch8-artifacts/run-45967622962/ch8-rev2-u64-n22-n25-providers-Linux-X64-45967622962-1/SUMMARY.md)

| Локальная база | Commit | Tree |
| --- | --- | --- |
| Std N22–N25 providers | `a1335f8e11960150afda1d00d60c72b4362e3cec` | `a04025df1dddb1668c12219307c943a23ee9382a` |
| Control N22–N25 providers | `9e95965f30f40a4dea9532bd04330b0d68537769` | `6b9a8245426143527186a7095e8fbf5623578527` |

Добавь verification-only модуль `rev2_u64_n26_n32_providers` с opt-in `kani_smallsort_rev2_u64_n26_n32_providers` внутри `cfg(kani)`, check-cfg и зависимостью от cfg модуля с `u64_less`. Runtime Std, контракты и существующие модули сохраняются побайтно. CI-base bundle `dab03cf510df5c35141cde49f1368b1242f5035e`. [Пины и blobs N22–N25](REV2-U64-N22-N25-PROVIDERS-HANDOFF.md#worktrees-и-замороженные-входы)

## Геометрии и опоры половин

Домен — живая инициализированная `V: [u64;34]`, активный срез `v[1..1+N]`, `S=&v[1]`, полный числовой `<` через тот же `u64_less`. Все указанные диапазоны Rust с исключённым концом. В каждой половине actual caller выбирает sort13 и передаёт offset 13 в `insertion_sort_shift_left`. Размер и выравнивание слова 8 байтов. Scratch — отдельная живая `MaybeUninit<[u64;32]>`, 256 байтов, база D. [Прецедент геометрий `u8`](REV2-N26-N31-HALVES-ADMISSION.md)

| N, m | Левая половина B01 | Правая половина | Вставки слева / справа, rel | Merge |
| --- | --- | --- | --- | --- |
| 26, 13 | `v[1..14]`, L13 | `v[14..27]`, B14 L13 | ∅ / ∅ | 13 пар |
| 27, 13 | `v[1..14]`, L13 | `v[14..28]`, B14 L14 | ∅ / 13 | 13 пар, `D[13]` |
| 28, 14 | `v[1..15]`, L14 | `v[15..29]`, B15 L14 | 13 / 13 | 14 пар |
| 29, 14 | `v[1..15]`, L14 | `v[15..30]`, B15 L15 | 13 / 13–14 | 14 пар, `D[14]` |
| 30, 15 | `v[1..16]`, L15 | `v[16..31]`, B16 L15 | 13–14 / 13–14 | 15 пар |
| 31, 15 | `v[1..16]`, L15 | `v[16..32]`, B16 L16 | 13–14 / 13–15 | 15 пар, `D[15]` |
| 32, 16 | `v[1..17]`, L16 | `v[17..33]`, B17 L16 | 13–15 / 13–15 | 16 пар |

- **Левый sort13.** Переиспользуй `U64-N13-S13-BITS` и `U64-N13-SWAP` из `45919454859/1`. Для L14–L16 перенеси пост по длине: тот же B01, guard `len>=13`, неизменное расписание 45 пар rel0–12, произвольный хвост остаётся во frame. В правых геометриях новый S13 bits на максимальной длине каждой базы и отдельный полноширинный swap. Сужения B14 L14 → L13, B15 L15 → L14 и B16 L16 → L15 используют те же адреса и guard. Для B17 нужна своя опора. B13 из N25 задаёт форму и исходную оценку стоимости. [Пороговый перенос N13](REV2-U64-N13-ADMISSION.md#перенос-на-полные-u64-и-фактический-маршрут)
- **Нативные посты S13.** Plain Proof bits вызывает actual sort13 на точном срезе. Во входном префиксе все `2^13` комбинаций `0u64/1u64`, остальные 21 слово произвольны. Посты — каноничность, отсортированная маска с тем же popcount и скалярный frame всех остальных слов, включая хвост среза. Covers — mixed, inversion, actual comparator и normal return. Plain Proof swap на том же base проверяет actual `swap_if_less` для `0≤a<b<13` и произвольных полных слов: min/max, frame остальных 32 слов, covers `>`, `<`, `==`, comparator и return. Проверь все 45 пар в фактическом порядке, обе группы typed `ptr::copy::<u64>` на `ptr/mod.rs:682:9` и `ptr::copy_nonoverlapping::<u64>` на `:587:14`. Для полного порядка и кратностей нужен внешний пороговый перенос через scalar min/max и сохранение каждой пары. [Пример правого B13](REV2-U64-N22-N25-PROVIDERS-HANDOFF.md)
- **Вставки.** Для B01 используй уже проверенные литеральные `REL13/14/15` из `45933888115/1` на тех же полных `u64`. Для правых B14 rel13, B15 rel13–14, B16/B17 rel13–15 оформи внешний адресный перенос каждого нужного шага. Для фиксированного R исходный `1+j` переходит в `B+j` при `0≤j≤R` в той же живой V34, сдвиги в байтах 104/112/120/128 для B14/15/16/17. Сохраняются выравнивание, полный comparator, `sift==begin`, все соседние непересекающиеся копии, отдельный tmp `CopyOnDrop` и frame за tail. В каждой половине exact driver на `smallsort.rs:742–769` получает отсортированный префикс и останавливается у собственного end. Пост отображения после R даёт предусловие следующего R и сохраняет его tail. При L13 `tail==end` сразу. Сопоставь с адресным аргументом w15 для N22–N25, сохрани отдельный список внешних рёбер и результат их независимого ревью. Если конкретный перенос не принят, оставь зависимую длину открытой и укажи точный B/R для отдельного малого пакета. Символьный R в одном корне не нужен. [Литералы FIX1](REV2-U64-N14-N17-ADMISSION.md#сверка-обоих-прогонов) · [Прецедент адресной сверки](REV2-U64-N22-N25-PROVIDERS-HANDOFF.md#половины-presort-и-вставки)

## Десять exact Check для merge

- **Семь пар.** Отдельная ProofForContract на verification-only обёртку для каждой N. Литералы N/m, символьные `0≤k<m`, `0≤a,c≤k`, `b=k−a`, `d=k−c`. Actual up читает `S+a` и `S+m+b` и пишет `D[k]`, actual down читает `S+m−1−c` и `S+N−1−d` и пишет `D[N−1−k]`. Полные слова источника произвольны. Предпосылку числового порядка половин применяет внешняя индукция. Сохрани обе тройки курсоров, scoped write set ровно двух назначений, read/write/disjoint, min/max, tie-left/tie-right и source frame. Десять covers как у N25, включая обе стороны каждого направления, равные значения, k=0 и k=m−1, компаратор и возврат. Сверь 819/1015/1240/1496 состояний `(k,a,c)` для m13/14/15/16 и начальные/следующие адреса. [Форма N22–N25](REV2-U64-N22-N25-PROVIDERS-HANDOFF.md#пары-центр-и-индукция)
- **Три центра.** Для N27/29/31 точный курсорный домен после m пар. `a+b=c+d=m`, остатки `(m−a−c,m+1−b−d)` равны `(1,0)` или `(0,1)`. Левый случай выбирает `S+a` при `(b,c,d)=(m−a,m−1−a,1+a)`, правый — `S+2m−a` при `(b,c,d)=(m−a,m−a,a)`. Сверь все 27/29/31 состояний. Транскрибируй actual `smallsort.rs:1027–1036` с wrapping и тем же сравнением курсоров. При `c=m` sentinel `S−1` продвигается до S без чтения. Проверить выбранный адрес, полное слово и write set одной ячейки `D[m]`, оба равенства на `:1042` и source frame. Четыре covers — левый и правый остаток, sentinel и возврат.
- **Нативная привязка и внешний вывод.** Для каждого Check закрепи exact `target_fn`, `single_top_level_call`, `no_recursive_call`, scoped `memcpy.assigns.1/.2`, шесть grouped typed-copy свойств `u64` на `ptr/mod.rs:587:14` и все выведенные unwind. В pair свяжи курсоры с closure собственной цели и копиями `smallsort.rs:885:9`, `:918:9`, в odd — с собственным call site, соответствующим `:1034:13`. Покажи, как для каждой длины ранг `(значение, индекс после вставок)` определяет непересекающиеся записи, обе проверки концов и заполнение `D[0..N]` перед чтением при uninit OFF. При превышении профиля exact пары разбери фактическую фазу и CNF. Первая альтернатива — отдельные up/down с общим неизменным источником и раздельными назначениями после независимого ревью. [Правило общих ID](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md) · [Урок N22–N25 R1](REV2-U64-N22-N25-PROVIDERS-REVIEW.md)

## Замороженный roster

Префикс exact selector `slice::sort::shared::smallsort::verify::rev2_u64_n26_n32_providers::`. Во всех слотах `copy_back=false`, ожидаются `VERIFIED`, exit 0 и полный набор covers. Сначала измеряются наибольшие пары m16/m15, затем наибольшая половина.

| Слот / суффикс selector | Режим | Latest start |
| --- | --- | --- |
| `U64-N32-PAIR-STEP` / `u64_n32_pair_step` | Check | 55:00 |
| `U64-N31-PAIR-STEP` / `u64_n31_pair_step` | Check | 58:25 |
| `U64-N30-PAIR-STEP` / `u64_n30_pair_step` | Check | 61:50 |
| `U64-S13-B17-L16-BITS` / `u64_s13_b17_l16_bits` | Plain Proof | 65:15 |
| `U64-S13-B17-SWAP` / `u64_s13_b17_swap` | Plain Proof | 68:40 |
| `U64-N29-PAIR-STEP` / `u64_n29_pair_step` | Check | 72:05 |
| `U64-N28-PAIR-STEP` / `u64_n28_pair_step` | Check | 75:30 |
| `U64-N27-PAIR-STEP` / `u64_n27_pair_step` | Check | 78:55 |
| `U64-N26-PAIR-STEP` / `u64_n26_pair_step` | Check | 82:20 |
| `U64-N31-ODD-CENTER` / `u64_n31_odd_center` | Check | 85:45 |
| `U64-N29-ODD-CENTER` / `u64_n29_odd_center` | Check | 89:10 |
| `U64-N27-ODD-CENTER` / `u64_n27_odd_center` | Check | 92:35 |
| `U64-S13-B16-L16-BITS` / `u64_s13_b16_l16_bits` | Plain Proof | 96:00 |
| `U64-S13-B16-SWAP` / `u64_s13_b16_swap` | Plain Proof | 99:25 |
| `U64-S13-B15-L15-BITS` / `u64_s13_b15_l15_bits` | Plain Proof | 102:50 |
| `U64-S13-B15-SWAP` / `u64_s13_b15_swap` | Plain Proof | 106:15 |
| `U64-S13-B14-L14-BITS` / `u64_s13_b14_l14_bits` | Plain Proof | 109:40 |
| `U64-S13-B14-SWAP` / `u64_s13_b14_swap` | Plain Proof | 113:05 |

## Control и сдача

- Одна `ubuntu-24.04` X64 job до 140 мин. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, CBMC 6.11.0/CaDiCaL, OB12, unwind36. Сохрани `--exact --jobs=1 --no-assert-contracts`, прежние `-Z`, `KANI_JOBS=1`. Actual тела в Original. Safety, overflow, unwind, undefined-function, assertion-reach ON, uninit/validity OFF. Без stubs, Replace и loop contracts. **120 с VT, 4 GiB группового RSS, 180 с cold wall** на корень, 2 GiB резерва ОС. Собственные холодные CWD, Cargo/Kani targets, tmp и export. Сохрани оговорку о Linux RSS при смене TID. [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)
- Prepare до 54:00, внешний timeout 56 мин, ранний compile preflight с первыми ошибками rustc до cfg-on/off list. Identity gate до 55:00. Восемнадцать окон по 205 с, включая 10 с reap, 5 с receipt и 10 с запаса на запуск. Конец слотов 116:30, аттестации 118:30. Внутренний measure 64:35, внешний 66 мин. Finish/upload-gate до 123:25, upload до 130:30, с 6 мин резерва план 136:30. Сохрани checkpoint исхода и reap до проекции, bounded retry, caps 4/96 MiB и блокировку следующих слотов при неподтверждённом reap.
- Exact discovery проверяет 131 историческую запись и дельту 18. Восемь plain Proof с пустыми targets, десять ProofForContract с одной точной целью. Новый индекс и диагноз `U64_N26_N32_PROVIDERS_WITHIN_PROFILE`. Для диагноза нужны 18 `VERIFIED/MATCHED`, полные проекции, своевременные receipts, ожидаемые covers, подтверждённые sampler/reap и аттестация `COMPLETE`. Публикуй фазу, первую CNF, VT, cold wall, group/CBMC RSS и доступную PSS. Результаты вне профиля и непринятые внешние рёбра указывай по зависимым длинам.
- Независимый tree pin `CH8_REV2_U64_N26_N32_PROVIDERS_TRIGGER_TREE` для `pins/sources/finish/upload-gate`. Fork `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, чистый detached HEAD равен `GITHUB_SHA` и payload SHA. Tree локального review-trigger совпадает с Control, sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Перед upload сверяются admission receipt, индекс и хэши.
- Офлайн сверь исходники, фактические 45 пар, геометрии, proof attributes, видимость Rust-имён, cfg и побайтный runtime diff. Для каждого цикла проверь границу по unwind36. Сравнения полных слов и frame скалярные. Исключи скрытый `memcmp`; символические k,a,c задают адреса одной пары. Rustfmt `nightly-2026-11-19` с `use_small_heuristics=Max` до фиксации координат. Проверь TOML/YAML, `bash -n`, `git diff --check`, shallow bundle и trigger. Синтетика отклоняет ложную цель или селектор, потерю typed/scoped/return anchor, неверный tree/payload, late receipt, потерю reap/attestation и публикацию после cutoff. Сохрани `test_supervisor.py` blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Suite последовательно на штатной и свежих шкалах 1/5/60 с. Локально без cargo, rustc, Kani и CBMC.
- Сдай `REV2-U64-N26-N32-PROVIDERS-HANDOFF.md` с `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Приложи exact selectors/targets, source blobs и координаты, нативные и внешние рёбра по длинам, хэши переиспользуемых receipts/projections, полные commit/tree/parent, tree variable, четыре SHA-256 входов, argv, часы и проверки.

План на закрытие N26–N32 после текущей работы N22–N25 — этот пакет опор, затем отдельный пакет из семи локальных copy-back/frame и семи контролей фактической сети по модели N20–N25. Начальный ориентир 1–2 рабочих дня на подготовку и ревью опор, затем ещё 1–2 дня на consumer и составной допуск, без учёта очереди или исправлений. Для `stub_verified` и заявлений pr752 действуют отдельные условия. [Прецедент consumer](REV2-U64-N22-N25-CONSUMER-TASK.md)

Все локальные коммиты, включая Std, Control, review-trigger и g0, с `[skip ci]`. Для `commit` и `commit-tree` используй `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com` и сверь author/committer. В сообщениях любых коммитов запрещён знак решётки непосредственно перед цифрой, чтобы GitHub не создавал публичные перекрёстные ссылки. Используй `pr752`, `kani5196`, `issue56`.
