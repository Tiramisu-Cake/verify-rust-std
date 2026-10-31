# CONSTWAVE — PARTIAL (G2 ожидается)

2026-10-31; ветка `experiment/kani-k1-constwave-20261031`.
Library commit `a9daab85b05e5e18c7b06dd657bb384def842eaa`.
Frozen library tree G1/G2 `3b06bd6d60eec19d3c7ff1a0133f8c8191f20980`.
G1 source `b87fa448770e07e51f498e4fe2320fbaab292ea1`.
G1 build `3b1d1233-bff3-42fc-87af-21d1e083cfb0`, request `constwave-g1-measurement-pairs-20261031`.
G1 request SHA256 `73088722be1ba8eb220fa975baa3f3a1f902905da9d5d6160dfd3b6e344b0af4`.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`; tooling относительно `0d0e585912`: PASS.
G1 COMPLETE, jobs1, controls:true, timeout600, 12/12 SUCCESS, все covers, 0 failed checks.
G1 стоимость $0.3915; G2 резерв $1.0800; общий предел $3.30/2 builds.
Результаты прочитаны только через k1g.sh summary/peaks/check-tooling/log-grep.

S6/S7/S8: `stable_direct_u64_n6/n7/n8` → `stable_direct_const_u64_n6/n7/n8`.
G5: `general_stable_direct_u64_n5` → `general_stable_direct_const_u64_n5`.
R16: `route_safety_all_routes_n16` → `route_safety_all_routes_const_n16`.
M9: `merge_scratch48_contract_u8_n9` → `merge_scratch48_contract_const_u8_n9`.
M9 здесь — обозначение пары PFC N9; отдельный пилот M9 обсуждается ниже.
VT — Verification Time, с; CBMC RSS — kernel VmHWM, KiB, direct attribution.
Checks — failed/total. Aggregate = `MaybeUninit<[u64;48]>` + scratch_view.
Repeat/const = `[MaybeUninit<T>;48]` с обычным/const-repeat initializer.

| Гармоника | Форма | Статус | VT, с | CBMC RSS, KiB | Covers | Checks |
|---|---|---|---:|---:|---|---|
| S6 old | aggregate | SUCCESS | 43.307020 | 873252 | 1/1 | 0/407 |
| S6 const | const | SUCCESS | 31.181812 | 366672 | 1/1 | 0/405 |
| S7 old | aggregate | SUCCESS | 80.345360 | 983592 | 1/1 | 0/407 |
| S7 const | const | SUCCESS | 65.378990 | 410520 | 1/1 | 0/405 |
| S8 old | aggregate | SUCCESS | 202.350880 | 1581664 | 1/1 | 0/407 |
| S8 const | const | SUCCESS | 135.131290 | 770392 | 1/1 | 0/405 |
| G5 old | repeat | SUCCESS | 105.804320 | 4713196 | 2/2 | 0/407 |
| G5 const | const | SUCCESS | 37.682630 | 737488 | 2/2 | 0/407 |
| R16 old | repeat | SUCCESS | 77.376434 | 1610096 | 4/4 | 0/637 |
| R16 const | const | SUCCESS | 73.865230 | 1570976 | 4/4 | 0/637 |
| M9 old | repeat | SUCCESS | 185.722870 | 1342312 | 2/2 | 0/440 |
| M9 const | const | SUCCESS | 202.587140 | 1328556 | 2/2 | 0/440 |

Δconst относительно собственного baseline (VT/RSS): S6 −28.00%/−58.01%;
S7 −18.63%/−58.26%; S8 −33.22%/−51.29%; G5 −64.38%/−84.35%;
R16 −4.54%/−2.43%; M9 +9.08%/−1.02%. R16 и RSS M9 — малые одиночные различия,
устойчивый эффект не установлен. S6/S7/S8 имеют 405 checks вместо 407; это новая геометрия.
Unreachable old/const одинаковы: S6 66, S7 65, S8 62, G5 67, R16 9, M9 95.
TIMEOUT/MISSING нет; у всех 12 CBMC процессов direct attribution, metadata_match_count=1.
G1 sampled sum RSS 5.10 GiB, simultaneous CBMC 4.41 GiB, OOM none_seen.
Linux: MemTotal 16785850368 bytes, swap off; macOS UNKNOWN.

G2 diagnostic/jobs3/controls:true: допущены только S6/S7/S8/G5/R16 const.
M9 const в G2 NOT_RUN: VT хуже baseline на 9.08%; пара не проходит no-regression.
G2 source `d87156a7e33e753885d910614a17f855879643c9`.
G2 build `3a4f6f14-d7b1-41ad-9dd9-f17be6b8de92`.
G2 request `constwave-g2-diagnostic-jobs3-20261031`, envelope 80 мин; запущен.
Результаты и реальные перекрытия CBMC будут внесены после завершения.
Итог PARTIAL из-за M9, успех остальных пяти пар сохраняется.

Source audit: `python3 -B research/challenge-8/kani-k1/CONSTWAVE-SOURCE-AUDIT.py`: PASS.
112 insertion-only строк; старые fn/macro items побайтово прежние; прочая library неизменна.
Имена уникальны, cfg opt-in; старые resolved helpers/macros/imports не затронуты.
Три non-const копии отличаются только initializer; stable_direct меняет aggregate на const
с прежними размером/alignment/mutable slice interface; dispatcher меняет только helper target.
Donor helper M9 `7fd3d250a1` точен, кроме guard 6/7/8. PFC/lt_u8/оба backing/covers прежние.
Rustfmt по TASK exit 0, Rust строки ≤100, diff --check PASS; локальных компиляций нет.
Cfg on: log-grep не обнаружил merge.rs/unused/dead/unexpected/unnecessary/error диагностики;
фоновые unstable-feature/manifest warnings есть. Cfg off: новая часть полностью исключена,
source projection прежняя; отдельная компиляция cfg off в пилоте не измерена.

Предварительно для интеграции, окончательно после G2:
1. `stable_direct_u64_properties` N6..8 — перевести на const; заметно ниже VT/RSS.
2. `general_route_properties` — перевести на const; обе ветви/covers сохранены, ниже VT/RSS.
3. `stable_general_u64_safety_body` — const допустим для единой формы, ресурсный эффект не доказан.
4. `merge_scratch48_length_body` — оставить: VT хуже; controls/positive менять лишь согласованно.

Карта с пилотом M9: совпадают `stable_direct_const_u64_properties` и N8 wrapper.
Нужны один helper с guard 6..=9 при переносе G9/S9const M9 в P2 и один N8 wrapper без дублей.
Whole-file cherry-pick не делать; переносить согласованные items. Опытные baseline/копии
остаются opt-in и не разгейчиваются старым P2-патчем. Ordinary stable_direct N6..8 при замене
aggregate на const сохраняют домен T/F/N/input/probe, но меняют fixture-геометрию:
старый PASS не переносится; нужна проверка нового ordinary tree в CI организаторов.
scratch_view оставить для BACKING controls; correct.rs и соседний U8N9 не переносились.
fixture48 ≠ любой backing; механизм не установлен; пригодность — только CI организаторов.
