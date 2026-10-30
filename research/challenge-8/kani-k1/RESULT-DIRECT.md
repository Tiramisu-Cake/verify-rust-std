# DIRECT — COMPLETE (B + A)

Домен Copy+Freeze: u64 N2..8, u8 N2..9, general и stable — 30 маршрутных случаев.
B без stubs: 13/15 T/N; u64 N8 и u8 N9 закрыты A + повторно проверенным caller.
macOS — UNKNOWN. Это bounded Kani evidence; пилот ≠ зелёный CI организаторов.
Base SHA: `63fc45e7b2b3e23c6129428425df602ef427156e`.
Library SHA: `b3b68a0ae8f37f1692d8b8ad6d513309532e3bc0`.
Library tree: `e16a8ee5a36c4572a72a0560fb8402ad1b2b5ea5`.
Проверенный source G3: `0335a90e393b566617ec9be870682517dc3d7c62`.
Kani pin: `9461e07af7ec929f050aa4192f29363c9be07779`; unwind(34).
Все builds: measurement, k1-network, k1-standard4, jobs=1, swap off.
Прежние solver/flags: --no-assert-contracts, --object-bits 12; uninit checks off.

G1: `f00d0543-ba0b-4e4c-9622-59531f85cba3`, SHA 5265f374dd, $0.4455, gate false.
G2: `a72ff727-f085-46cd-96a6-dff28f421d6b`, SHA 258208d0e5, $0.5805, gate true.
G3: `7bda9e5a-266a-41c2-89d5-c0606da6befe`, SHA 0335a90e39, $0.3780, gate true.
Ledger: 3/3 builds, $1.4040/$4 spent, reserved $0; CAP_USD 63.96 не менялся.
Budget проверен перед каждым dispatch; полные envelopes: 120/140/140 минут.
В каждом envelope 30 минут setup + 10 минут на гармонику; timeout не урезался.
Свой spent+reserved на старте G1/G2/G3: $1.6200/$2.3355/$2.9160.
Gate N2..4 раздельный: точные времена/RSS, без сцепления формул разных N.

Код: library/core/src/slice/sort/shared/smallsort/verify/merge.rs.
G — small_sort_general; S — StableSmallSortTypeImpl со scratch48.
Граф: оба → small_sort_general_with_scratch → bidirectional_merge (N>=2).
N2..7: копирование + insert_tail по необходимости; N8/9: sort4_stable + merge.
Опора: smallsort.rs:49,205,220,254,286; cover(N>=2) как свидетель не используется.

Таблица: общий VT для G+S, не отдельное измерение каждого маршрута; RSS — CBMC VmHWM.
B — реальный caller без stubs; A — proof_for_contract; C — прежний stubbed caller.
У B/C covers 2/2 проверяют G и S; у A — обе формы backing-аллокации.
RSS в GiB, процессная память, не суммарная физическая RAM; VT — GCB Verification Time.

| build | метод | T | N | маршрут | статус | VT GCB, с | RSS GiB | covers |
|---|---|---|---|---|---|---|---|---|
| G1 | B | u64 | 2 | G+S | SUCCESS | 21.032 | 1.159 | 2/2 |
| G1 | B | u64 | 3 | G+S | SUCCESS | 31.138 | 1.691 | 2/2 |
| G1 | B | u64 | 4 | G+S | SUCCESS | 99.822 | 3.917 | 2/2 |
| G3 | B | u64 | 5 | G+S | SUCCESS | 89.789 | 4.492 | 2/2 |
| G3 | B | u64 | 6 | G+S | SUCCESS | 235.455 | 6.034 | 2/2 |
| G3 | B | u64 | 7 | G+S | SUCCESS | 382.716 | 6.280 | 2/2 |
| G1 | B | u64 | 8 | G+S | TIMEOUT | — | 9.016 | — |
| G1 | B | u8 | 2 | G+S | SUCCESS | 4.376 | 0.110 | 2/2 |
| G1 | B | u8 | 3 | G+S | SUCCESS | 7.266 | 0.174 | 2/2 |
| G1 | B | u8 | 4 | G+S | SUCCESS | 26.390 | 0.201 | 2/2 |
| G3 | B | u8 | 5 | G+S | SUCCESS | 27.549 | 0.243 | 2/2 |
| G3 | B | u8 | 6 | G+S | SUCCESS | 22.382 | 0.304 | 2/2 |
| G3 | B | u8 | 7 | G+S | SUCCESS | 48.826 | 0.352 | 2/2 |
| G3 | B | u8 | 8 | G+S | SUCCESS | 142.442 | 0.556 | 2/2 |
| G1 | B | u8 | 9 | G+S | TIMEOUT | — | 0.600 | — |
| G2 | A | u64 | 5 | G+S | SUCCESS | 208.692 | 4.659 | 2/2 |
| G2 | A | u64 | 6 | G+S | SUCCESS | 310.391 | 6.583 | 2/2 |
| G2 | A | u64 | 7 | G+S | SUCCESS | 338.996 | 7.020 | 2/2 |
| G2 | A | u64 | 8 | G+S | SUCCESS | 417.825 | 8.813 | 2/2 |
| G2 | A | u8 | 5 | G+S | SUCCESS | 84.005 | 0.722 | 2/2 |
| G2 | A | u8 | 6 | G+S | SUCCESS | 124.352 | 0.936 | 2/2 |
| G2 | A | u8 | 7 | G+S | SUCCESS | 131.917 | 1.015 | 2/2 |
| G2 | A | u8 | 8 | G+S | SUCCESS | 193.207 | 1.207 | 2/2 |
| G2 | A | u8 | 9 | G+S | SUCCESS | 187.810 | 1.279 | 2/2 |
| G3 | C | u64 | 6 | G+S | SUCCESS | 38.438 | 0.455 | 2/2 |
| G3 | C | u64 | 7 | G+S | SUCCESS | 49.329 | 0.513 | 2/2 |
| G3 | C | u64 | 8 | G+S | SUCCESS | 93.255 | 0.972 | 2/2 |
| G3 | C | u8 | 9 | G+S | SUCCESS | 53.550 | 0.610 | 2/2 |

Приёмка A: T=u64/u8, F=тот же stateless lt_u64/lt_u8 (ключ x>>1), полные значения any.
Один set_value_probe на вызов; произвольный probe считает полные значения, не ключи.
Обе реальные формы: [MaybeUninit<T>;48] и MaybeUninit<[T;48]>, cover каждой SATISFIED.
src — offset 0, срез длины N; инициализирован только префикс N, хвост uninit.
Половины floor(N/2) и N-floor(N/2); те же sorted-halves requires.
dst — отдельный инициализированный [T;N], any покрывает и коррелированные с input значения.
No-alias: разные локальные аллокации. Frame прежний modifies(dst[..N]); scratch не добавлен.
Произвольные отсортированные половины покрывают состояния caller после insertion/sort4.
G3 повторно проверил C для u64 N6..8/u8 N9; G2 доказал A на обеих геометриях.

Контроль B (cfg kani_smallsort_controls): после real sort v[0]^=1 сохраняет ключ,
но проверка full-value counts FAILED: merge.rs:952, 1/407, VT 27.591 с, RSS 1.170 GiB.
Check: direct output preserves full-value counts; проверка sortedness не отказала.
Контроль A: реальный verified stub, корректная память, несортированная левая половина.
Check: CopyOnDrop::<T>::merge_inputs_are_sorted(v, &is_less), smallsort.rs:842.
FAILED 1/470, VT 0.510 с, RSS 0.032 GiB, cover 1/1, штатный --no-assert-contracts.
G1 B-контроль отказал на counts (merge.rs:846), но placeholder не совпал с expect_check;
G2 тот же count-assert записан через kani::assert: точное сообщение подтверждено.

Scratch-transfer больше не посылка: B — u64 N2..7/u8 N2..8; A+C — u64 N8/u8 N9.
Непроверенных обязательных T/N/маршрутов нет. B u64 N8/u8 N9: TIMEOUT (лимит 600 с), VT неизвестен.
Продолжение именно B: оптимизировать формулу этих двух гармоник при прежних доменах/flags.
За пределами: uninit, aliasing, generic T, unwind, stable !Freeze, unstable Freeze !Copy,
unstable trait u8/u64 (network). N0/1 не дублировались: merge не вызывается.
Чистая delta Part 1: +121 строк в одном файле, 15 B + 9 A + 2 controls; только добавления.
Прежние stub-гармоники, контракты, домены и covers сохранены; замены/удаления нет.
Два медленных B остаются в патче: COMPLETE по цели B+A не означает зелёный ordinary CI.
Rustfmt --check (указанный edition 2024/config) exit 0; код и этот отчёт ≤100 символов/строку.
Tooling G1/G2/G3 совпадает с base; [summary, peaks, requests и audit](direct/).
