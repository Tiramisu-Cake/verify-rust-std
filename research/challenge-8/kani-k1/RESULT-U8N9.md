# U8N9 — COMPLETE: прямые general и stable u8 N9

Дата: 2026-10-31; ветка `experiment/kani-k1-ueightnine-20261031`.
Library commit `2c65b6cdd94ad22ac71be1bb301d9f4109d9035c`.
Frozen library tree G1/G2 `95a25d9241f071a8c22b6c6f5edebb3a31e45100`.
G1 source/GO `3acc3c19973525034e26d057bba17d19022fc89c`;
G2 source `8a7c7f22b2d154eaa81c362ea9902d60cc0fef79`.
G1 `62f745bc-2db0-496c-812e-88107d76a4cb`, measurement/jobs1, $0.4185.
G2 `9a33a513-9346-44c0-9d05-dedfcc0c6e63`, diagnostic/jobs3, $0.1890.
Итого по k1g budget собственных UUID: **$0.6075**, reserved$0, сборок2/2, лимит$1.9.
Обе сборки controls:true, timeout600; Kani `9461e07a`, uninit checks off.
Pool k1-standard4, Ubuntu24.04.5, 4CPU, RAM15.63GiB, swap0; Linux, не macOS.

Имена ниже относительно `slice::sort::shared::smallsort::verify::merge`.
CBMC RSS — KiB, per-process VmHWM с direct metadata attribution; checks=failed/total.
G2 VT/RSS относятся к общему jobs3 запуску, не изолированным measurement.

| Run | Гармоника | Маршрут | Scratch | Статус | VT, с | CBMC RSS, KiB | Covers | Checks |
|---|---|---|---|---|---:|---:|---|---|
| G1 | general_stable_direct_u8_n9 | combined | general aggregate48 / stable nonconst48 | TIMEOUT600 | MISSING | 627024 | MISSING | MISSING |
| G1 | general_direct_u8_n9 | general | внутренний aggregate48 | SUCCESS | 193.24382 | 335140 | 1/1 | 0/400 |
| G1 | stable_direct_nonconst_u8_n9 | stable | nonconst48 | SUCCESS | 221.64731 | 442276 | 1/1 | 0/398 |
| G1 | stable_direct_const_u8_n9 | stable | const48 | SUCCESS | 300.79068 | 325988 | 1/1 | 0/398 |
| G2 | general_direct_u8_n9 | general | внутренний aggregate48 | SUCCESS | 230.09187 | 336032 | 1/1 | 0/400 |
| G2 | stable_direct_nonconst_u8_n9 | stable | nonconst48 | SUCCESS | 227.56679 | 444808 | 1/1 | 0/398 |
| G2 | general_stable_direct_u8_n8 | combined | aggregate48 / nonconst48 | SUCCESS | 148.75179 | 583952 | 2/2 | 0/400 |
| G2 | merge_scratch48_contract_u8_n9 | merge contract | aggregate48 / nonconst48 | SUCCESS | 295.33417 | 1342456 | 2/2 | 0/440 |

G1 summary COMPLETE, Cloud FAILURE/gate false из-за прежнего combined TIMEOUT;
решение принято по строкам: все три новые гармоники SUCCESS, covers3/3.
G2 summary COMPLETE, Cloud SUCCESS/gate true, covers6/6; missing rows/process0.
Unreachable checks G1 split:63 в каждой; G2 general/stable/N8/A:63/63/64/95.
Достижимость нормального возврата подтверждают covers после oracle; TIMEOUT не proof.

Split: general193.24с + nonconst stable221.65с закрыли обе ветви при том же initializer,
тогда как unchanged combined TIMEOUT600. Значит const не требуется для этого закрытия.
Это наблюдение данного T/N и запуска, не гарантия универсального ускорения.
Initializer отдельно: const тоже SUCCESS, но VT300.79с против221.65с nonconst;
RSS0.311 против0.422GiB. Здесь const экономит память и увеличивает VT.
В G2 выбран nonconst по меньшему VT при умеренном дополнительном RSS;
не заявляется оптимум CI. Обе fixed-route ветви повторно SUCCESS в jobs3.

Реальное перекрытие CBMC: PID9279 stable N9 (68..293с), PID9284 general N9
(68..295с), PID9304 A N9 (72..363с): общая наблюдаемая жизнь72..293с.
Затем PID9331 combined N8 (297..444с) перекрывается с A до363с.
Отсчёт — sampler verify; direct metadata различает процессы при нескольких active threads.
Измеренный simultaneous CBMC RSS2007308KiB (1.914GiB) в293с;
общий sampled RSS3105008KiB (2.961GiB) в363с, time-v max single1939628KiB.
G2 sampling2s/223samples; G1 OOM и G2 OOM=`none_seen`, не абсолютная гарантия.

Предложение для интеграции: conditional caller u8 N9 заменить парой
`general_direct_u8_n9` + `stable_direct_nonconst_u8_n9`, поскольку обе прошли
на frozen tree в jobs1 и jobs3. Переносить только library-diff нового блока;
разгейтирование — отдельная интеграция. **A u8 N9 автоматически не ретирить.**
Const entry оставить как диагностическую альтернативу, baseline combined — как TIMEOUT.

Source audit: единственная library-правка — один opt-in блок57 строк в конце merge.rs;
61353 исходных байта сохранены побайтно, остальные library-файлы прежние.
Семь новых имён уникальны; импорты/модули не добавлены, старые macro invocations
предшествуют новому macro: resolved helper/macro dependencies сохранены в обеих cfg.
General + nonconst stable = два исчерпывающих значения старого symbolic stable bool;
arbitrary u8[9]/probe, snapshot, общий oracle, исходный lt_u8 function item,
unwind34 и post-assert covers совпадают. Stubs/selector отсутствуют.
Тела stable helper-ов отличаются только initializer; const имеет тот же функциональный домен.
`u8n9/SOURCE-AUDIT.md`, `source-audit.json`, `g1.review.json`, `g2.review.json`.

Rustfmt заданным wrapper/config exit0; Rust строки<=100, diff-check PASS.
Controls compile G1/G2 успешен; targeted merge/unused/dead_code/error diagnostics нет.
Прежние manifest/force-warn unstable warnings сохраняются. В ordinary cfg все новые
items исключены и исходный код/dependencies прежние; fresh ordinary compile не выполнялся.
Lane/pin/toolchain/flags прежние; check-tooling G1/G2 PASS относительно GO3acc3c1997.
Локально Rust/cargo/Kani/CBMC не запускались; Evidence Brief не использовался.

Оговорки: fixture48 не любой backing; macOS UNKNOWN; этот пилот вне CI.
Пригодность интегрированного набора устанавливает только CI организаторов.
T0 UTC10:10:25, deadline14:07:39, closure30min; оба envelope70min прошли preflight.
UUID/request/source identities, стоимость и резерв: `u8n9/builds.json`, `g*.preflight.json`.
