# U8N9 — COMPLETE, готов к итоговому review

Ветка `experiment/kani-k1-ueightnine-20261031`.
Library commit `2c65b6cdd94ad22ac71be1bb301d9f4109d9035c`.
Frozen G1/G2/current library tree `95a25d9241f071a8c22b6c6f5edebb3a31e45100`.
Итог: `../RESULT-U8N9.md`, source audit `SOURCE-AUDIT.md` / `source-audit.json`.

G1 UUID `62f745bc-2db0-496c-812e-88107d76a4cb`,
source/GO `3acc3c19973525034e26d057bba17d19022fc89c`,
request `u8n9-g1-measurement-20261031`, measurement/jobs1/controls:true.
Combined TIMEOUT600; три fixed-route entry SUCCESS/covers1/1; расход$0.4185.
Summary COMPLETE, Cloud FAILURE/gate false; решение по строкам позволило G2.
`g1.review.json` связывает source/request/rows/direct CBMC identities.

G2 UUID `9a33a513-9346-44c0-9d05-dedfcc0c6e63`,
source `8a7c7f22b2d154eaa81c362ea9902d60cc0fef79`,
request `u8n9-g2-diagnostic-jobs3-20261031`, diagnostic/jobs3/controls:true.
General N9, stable nonconst N9, combined N8, A scratch48 N9 SUCCESS/covers6/6.
Реальные три CBMC перекрываются72..293с; sampled simultaneous CBMC1.914GiB,
общий sampled RSS2.961GiB; OOM none_seen, G2 missing rows/process0.
Direct metadata attribution и полные страницы проверены: `g2.review.json`.
Stable выбран по G1 VT221.65с против const300.79с при RSS0.422 против0.311GiB;
выбор для диагностики, не оптимум CI. Check-tooling G1/G2 PASS относительно GO.

Итого собственных UUID: $0.6075, reserved$0, builds2/2. Больше не запускать.
T0 UTC2026-10-31T10:10:25; deadline14:07:39; closure30min.
Перед каждым dispatch budget PASS и envelope70min+closure помещались в окно.
Обе сборки ожидались k1g.sh watch с завершением хода; чтение через k1g.sh.
Pin/toolchain/flags/lanes/CAP73.96 прежние; соседние library-патчи не переносились.

Предложена пара general + nonconst stable вместо conditional caller u8 N9;
A u8 N9 автоматически не ретирить. Перенос только нового opt-in library-блока.
Fixture48 не любой backing; macOS UNKNOWN; требуется CI организаторов.
Все старые library bytes/dependencies сохранены; ordinary cfg статически прежняя,
controls compile без новых targeted diagnostics; fresh ordinary compile не выполнялся.
Итоговый research commit/push и маркеры REVIEW REQUEST / U8N9 ЗАВЕРШЁН — закрытие.
