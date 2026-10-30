# OPT — кандидат до первой proof-сборки

База: `c52627e090e059ae8000af23fded3d614a89a2e3`.
Library SHA: `f052d6b7ec826e4f45f7bc1522dde38d5ba16a91`.
Delta: только 91 новая строка в конце `verify/merge.rs`; прежний файл — точный префикс.
Весь блок `opt_split` закрыт `cfg(kani_smallsort_controls)`.
Чужие области INTEG/UNSTABLE8, существующие символы и lane-файлы не менялись.

## Эквивалентность доменов по исходному коду

Для каждого N из {6,8}, T=u64, прежний B `general_route_properties` выбирает
независимый symbolic bool stable. Его false-ветвь ровно `small_sort_general`,
true-ветвь — `StableSmallSortTypeImpl::small_sort` с `[MaybeUninit<u64>;48]`.
Новый `general_direct_body` содержит только false-ветвь, `stable_direct_body` — true.
General создаёт `MaybeUninit<[u64;48]>` внутри настоящего `small_sort_general`;
stable создаёт только свой scratch. Старый helper с selector не вызывается.
В каждой ветви сохранены any `[u64;N]`, orig, один `set_value_probe::<u64>()`,
тот же stateless `lt_u64` (ключ x>>1) и `assert_sorted_and_probe_preserved`.
Ни insertion, ни sort4, ни merge не подменяются; stub-атрибутов в блоке нет.
Поэтому объединение B-split покрывает все прежние пары (stable,input,probe).

Прежний A `merge_scratch48_length_body` выбирает тем же bool одну из двух
backing-аллокаций. Новые general/stable contract bodies сохраняют соответственно
`MaybeUninit<[u64;48]>` / `[MaybeUninit<u64>;48]`, но убирают невыбранную аллокацию.
Удаление мёртвой аллокации — проекция домена по наблюдаемым значениям и геометрии,
а не утверждение о равенстве формул или численных адресов/идентификаторов объектов.
В обеих формах src указывает на offset 0; только префикс N скопирован из any input,
хвост остаётся uninit. Отдельный dst `[u64;N]` полностью инициализирован через any.
Независимые any покрывают и совпадающие/коррелированные input,dst значения.
Поэтому объединение A-split покрывает прежние (stable,input,dst,probe), с точностью
до ненаблюдаемой невыбранной аллокации. u64 не содержит ссылок; lt_u64 не читает адреса.
Оба src/dst по-прежнему раздельны; длины половин N/2 и N-N/2 не меняются.

A сохраняет `proof_for_contract(bidirectional_merge)`: requires sorted halves,
valid destination и N2..32, modifies только dst[..N], оба ensures — прежние.
Новых assume нет: ограничение sorted halves вносит прежний контракт.
Oracle, full-value probe, frame и домены значений не менялись; новые контроли не нужны.
Обе группы сохраняют unwind(34). В каждой гармонике один cover после проверки:
у B — после oracle; у A — после возврата merge под proof_for_contract.
Прежние два covers разложены по маршрутам; SATISFIED пока НЕ установлено.

## Gate и продолжение после GO

`gate.request.json` совпадает с RUN-REQUEST.json: 4 явных N6, measurement,
k1-network, k1-standard4, controls=true, kani_jobs=1, timeout=10 минут на гармонику.
Envelope: 4*10+30=70 минут; максимум резерва 70*$0.0135=$0.9450.
Ограничения OPT: не более 3 builds и $4 собственных spent+reserved; CAP_USD=73.96.
Бюджет до review: общий used $56.5350, reserved $0; cap $73.96.
Перед dispatch снова budget и проверка полного envelope плюс резерва времени;
общий agent label k1-network не определяет собственные расходы OPT.
Список собственных request_id/build UUID: отправленных нет; spent=reserved=$0.
Подготовленный request_id: `opt-split-n6-gate-20261030`, build UUID отсутствует.
Не начинать build без GO координатора на опубликованный кандидат.
После dispatch только `k1g.sh watch BUILD` и завершение хода; без status polling.

Приёмка B и A раздельная: обе ветви SUCCESS, каждый cover SATISFIED, измеримый
спад индивидуального RSS относительно исторических B N6 6.034 / A N6 6.583 GiB.
Рядом указать VT обеих ветвей, сумму VT и стоимость; matched rerun не выполнен,
поэтому причинный speedup не заявлять. При отсутствии выигрыша группы — STOP.
N8 только по принятым группам и при помещающемся полном envelope; N7 не обязателен.
Резервный jobs=3 diagnostic — только при оставшихся окне, бюджете и числе builds.

Исторический источник: RESULT-DIRECT.md (source-reported, не новая проверка).
Уточнение координатора: Evidence Brief к K-1 задаче не применяется (TASK, Ограничения).
Штатный интерфейс: k1g.sh summary/peaks/log-grep/log-lines/check-tooling, включая fetch.
Прежний Brief HTTP 404 не является блокировкой; разрешение явно дано пользователем.
Индивидуальный CBMC/driver пик и метод измерения указать отдельно от одновременного;
сумма RSS не равна физической RAM. Linux 16 GiB не сертифицирует macOS 7 GiB.
macOS UNKNOWN; пригодность определяет только CI организаторов; safe-gate не назначен.

Письменные следующие варианты, без реализации: typed u64 probe как эквивалентная
специализация oracle либо локальная декомпозиция merge с отдельными обязательствами.
Оба потребуют самостоятельного обоснования/review; oracle в этом кандидате прежний.
