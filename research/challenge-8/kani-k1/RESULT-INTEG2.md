# INTEG2 — PARTIAL: G2 inventory/G3 controls приняты, G1 ordinary compile blocker

2026-10-31; ветка `experiment/kani-k1-integtwo-20261031`; база ASSEMBLY `e6a8ad05c9`.
Library commit `20aa864ad04e8d81b46d41024b75dc7aa1103dcf`.
Frozen library tree всех трёх builds `c522edd42ae67c385e1ee42a1c4d1bffb611c90b`.
GO Claude Code для `e0ff82577dc58950621dadc9c141d88a5821987f`: `integ2/go.json`.
Это кандидат P1-max с ordinary compile blocker, не новый зелёный P1.

| Build / request source | UUID | Результат | USD |
|---|---|---|---:|
| G1 / e0ff82577d | cda795d5-1cd1-4c32-a87e-778302647151 | FAILURE/TOOL_ERROR, inventory отсутствует | 0.1080 |
| G2 / 580296b8f5 | 7a0cbca0-dda5-4cb2-a0ea-ad6f9112ad71 | SUCCESS/COMPLETE, exact479 | 0.6075 |
| G3 / 00c7a1e00a | fb2ec8a5-9870-4301-a892-ad5d48b74560 | SUCCESS/COMPLETE, controls PASS | 0.1215 |

Request IDs: `integ2-inventory-ordinary-20261031`, `integ2-inventory-controls-20261031`,
`integ2-measurement-controls-20261031`; SHA/request hash/UUID bindings: `integ2/builds.json`.
Builds3/3; own spent **$0.8370≤$2.90**, reserved$0; `integ2/budget-final.txt`, `g*.cost.txt`.
Общий agent label не использовался для отнесения затрат. Дополнительных build slots нет.

Точные статические списки: `integ2/scope/p1-ordinary.txt`197, `p2-ordinary.txt`343,
`cfg-on.txt`479; manifest/provenance — `manifest.tsv`, `scope.tsv`, `metrics.json`.
Exact diff к ASSEMBLY: `p1-diff-from-baseline.txt` +16/−1, `p2-diff-from-baseline.txt` +7/−3.

| Diff к ASSEMBLY | P1 | Расширенный P2 |
|---|---:|---:|
| network correctness u8 N10/N11/N12, insertion permutation u8 N11 | +4 | 0 |
| merge route_safety_all_routes N3..7 | +5 | 0 |
| u8 N9 general + stable nonconst вместо C u8 N9 | +1 | +1 |
| u64 N9 general + stable const вместо P2 C u64 N9 | +2 | +1 |
| три START1 группы вместо P2 baseline | +3 | +2 |
| Итого | 182 → 197 | 339 → 343 |

Stable u64 N6..9: один const-repeat helper с guard6..=9, один ordinary N8 wrapper.
B u64 N2..5: отдельный const-u64 helper, function item lt_u64, прежние oracle/оба covers;
generic helper сохранён. Stable-ветвь direct corruption control согласованно const.
U8N9 перенесён только nonconst-парой; A u8 N9 и A u8 N5..8 сохранены.
START1 три PFC покрывают tails2..16; baseline timeout-diagnostic остаётся opt-in вне P2.
C u64 N9 retired; C u8 N9 provisional retired/fallback; оба opt-in вне P2.
CORR14, R16, P9, прежние u8 тела, correct.rs и aggregate controls не изменены.

G1: Kani exit1, E0425 network.rs:1268 — ordinary insert_tail_group_value вызывает
set_value_probe, импорт которого всё ещё controls-gated (network.rs:6..7).
Также зарегистрированы E0034 checked_sub/MAX; их причинное разрешение не установлено.
Native ordinary inventory (expected197) не создан; G1 tooling PASS; `integ2/g1.failure-review.json`.
Изначальный source audit пропустил cfg-availability; исторические отчёты не переписаны.
Предложен `integ2/g1-proposed-import-cfg-fix.patch`: снять cfg только с импорта.
Patch **NOT_APPLIED**, bodies/names прежние; `g1-import-availability-review.json`.
Frozen source сохранён; library delta требует committed review/GO, нового build здесь нет.

G2: controls:true, inventory:true, work60min; точное множество479 равно static manifest.
Шесть bounded pages80/80/80/80/80/79, continuations до done, duplicates/missing/unexpected0.
Request/source/pin/artifact/names hashes и coverage PASS: `integ2/g2.inventory-check.json`.
Это native cfg-on enumeration, не positive proof; inventory memory/time MISSING.
Static P2 patch temporary apply/name check343 PASS: `integ2/scope/p2-static-check.json`.
Native P2 NOT_RUN; static names не подтверждают cfg-availability/компиляцию P2.

G3: jobs1/controls:true/timeout10min, gate true, Kani exit1 ожидаем; covers3/3.
Ровно один intended FAILED каждого, иных отказов/OOB нет; actual locations сверены вручную.

| Control (полное имя после verify::) | FAILED/checks | Covers | Actual frozen source |
|---|---|---|---|
| merge::general_stable_direct_value_corruption_control_u64_n2 | 1/409 | 1/1 | merge.rs:841 count |
| network::insert_tail_contract_u64_start1_prefix_frame_control | 1/424 | 1/1 | network.rs:1257 prefix |
| network::insert_tail_contract_u64_start1_suffix_frame_control | 1/426 | 1/1 | network.rs:1260 suffix |

Shared count/frame checker locations, не OOB; sortedness assert839 не FAILED.
Terse output не даёт отдельной явной sortedness SUCCESS строки. Known placeholder matcher
совпал; mismatch не переименовывался в gate=true. `integ2/g3.controls-review.json`.
Sampled CBMC≤0.79GiB, OOM none_seen; это не универсальная memory/proof гарантия.
Tooling G1/G2/G3 PASS к GO source; G2/G3 targeted helper warnings no match.
Прежние manifest/force-warn unstable warnings сохраняются; G1 compile errors явно выше.

Cfg-fallback карта/восемь неприменённых cfg-only patches: `integ2/cfg-fallbacks.json`, `fallbacks/`.
Aggregate stable N6..8: gate const wrappers, ungate aggregate helper + три wrappers.
B u64 N2..5: по N gate const wrapper, ungate nonconst-wrapper к прежнему generic helper.
U8 недопуск: gate новую пару, ungate C u8 N9 в P1; P2 включает C и новую пару.
M9 недопуск: обе новые u64 N9 в P2, C u64 N9 остаётся retired.
START1 недопуск: три группы в P2; baseline не возвращается ordinary.
Тела не менять; после cfg-отбора регенерировать selected P2 patch/manifest.
При r=0: P1=191+u+2m+3s, P2=344−u; const/fallback замены cardinality не меняют.

Source audit `integ2/source-audit.json`: точные изменённые items,584 сохранённых items/local bindings;
ограничение cfg-audit задокументировано выше. Donors M9 b2930031d8/CONSTWAVE a9daab85b0,
U8N9 2c65b6cdd9/START1 b98ee415fd: item-level transfer, без whole-file cherry-pick.
Изменены только verify/merge.rs/network.rs; production/tool/lane не затронуты.
Rustfmt заданным wrapper/config --check PASS; .rs≤100; source/non-patch diff-check PASS.
Kani pin9461e07a/toolchain/flags/CAP_USD73.96 прежние; uninit checks off, только k1-standard4.
Перед dispatch — свежие global/own budgets и full envelopes60/90/60min + closing30min;
max reserves$2.835≤$2.90. T0 UTC11:58/deadline16:58; закрыто внутри исходного окна.
Все ожидания через k1g.sh watch с завершением хода; все notifications/results reviewed.
Локально Rust/cargo/Kani/CBMC не запускались; Actions/CircleCI/submission ветки не затронуты.
Positive integration proofs, native P2, macOS и полный CI NOT_RUN; historical pilot credit не перенесён.
Координатору: import-fix review/GO и дальнейший ordinary inventory перед macOS/cfg-отбором/полным CI.
