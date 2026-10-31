# INTEG2 — PARTIAL, кандидат P1-max подготовлен к PRE-BUILD REVIEW

2026-10-31; ветка `experiment/kani-k1-integtwo-20261031`, база ASSEMBLY `e6a8ad05c9`.
Library commit `20aa864ad04e8d81b46d41024b75dc7aa1103dcf`.
Library tree `c522edd42ae67c385e1ee42a1c4d1bffb611c90b`.
GO ещё не получен. Builds0/3, собственные spent/reserved $0/$0; лимит $2,90.
Это кандидат P1-max, новый зелёный P1 не заявлен.

Точные статические списки: `integ2/scope/p1-ordinary.txt` (197),
`integ2/scope/p2-ordinary.txt` (343), `integ2/scope/cfg-on.txt` (479).
Manifest/class/provenance: `integ2/scope/manifest.tsv`, `scope.tsv`, `metrics.json`.
Static P2 patch применён к временной копии внутри worktree: exact343 PASS,
`integ2/scope/p2-static-check.json`; это не native P2 inventory/proof.
Исторические результаты пилотов не являются measurements этого tree.

| Diff к ASSEMBLY | P1 | Расширенный P2 |
|---|---:|---:|
| network correctness u8 N10/N11/N12, insertion permutation u8 N11 | +4 | 0 |
| merge route_safety_all_routes N3..7 | +5 | 0 |
| u8 N9 general + stable nonconst вместо C u8 N9 | +1 | +1 |
| u64 N9 general + stable const вместо P2 C u64 N9 | +2 | +1 |
| три START1 группы вместо P2 baseline | +3 | +2 |
| Итого | 182 → 197 | 339 → 343 |

Stable u64 N6..9 использует один const-repeat helper; general guard расширен до 6..=9.
B u64 N2..5 вызывает отдельный const-u64 helper с function item lt_u64,
тем же oracle, symbolic stable bool и обоими covers; generic helper сохранён.
Stable-ветвь direct corruption control переведена на тот же const initializer.
U8N9 перенесён только в nonconst форме; A u8 N9 и A u8 N5..8 сохранены.
START1 три PFC совместно покрывают tails2..16 с прежними actual requires.
Baseline START1 — timeout-diagnostic; C u64 N9 retired, C u8 N9 provisional retired/fallback.
Оба C N9 остаются opt-in вне P2.
CORR14, R16, P9, прежние u8 тела и aggregate controls не изменены.

Cfg-fallback карта и восемь готовых cfg-only patches: `integ2/cfg-fallbacks.json`, `fallbacks/`.
Stable aggregate N6..8: gate const wrappers, ungate aggregate helper + три wrappers.
B u64 N2..5: по N gate const wrapper, ungate nonconst-wrapper к прежнему generic helper.
U8 недопуск: gate оба новых N9, ungate C u8 N9 в P1; P2 сохраняет C и новую пару.
M9 недопуск: обе новые u64 N9 в P2, C u64 N9 не возвращается.
START1 недопуск: все три группы в P2, baseline не возвращается ordinary.
Тела fallback не редактируются; после выбора надо регенерировать selected P2 patch/manifest.
При r=0: P1=191+u+2m+3s, P2=344−u. Все patches сейчас NOT_APPLIED.

Source audit: `integ2/source-audit.json` содержит точный список изменённых items,
584 сохранённых items и карту прежних local symbol bindings.
Выбранные тела сверены с library-diff M9 `b2930031d8`, CONSTWAVE `a9daab85b0`,
U8N9 `2c65b6cdd9`, START1 `b98ee415fd`; whole-file cherry-pick не применялся.
Изменены только verify/merge.rs и verify/network.rs; production/tool/lane не менялись.
Лексический dependency audit не заменяет Rust resolution/expansion.
Rustfmt заданным wrapper/config --check PASS; строки ≤100; diff-check source/non-patch PASS.
Локально выполнялись только Python, rustfmt и операции Git/чтения; Rust/Kani/CBMC не запускались.

План проверок: G1 inventory ordinary197; G2 отдельный inventory controls479;
G3 measurement jobs1/timeout10min/controls:true, ровно три expected FAILED.
Запросы `integ2/*.request.json` приняты штатным Python validator, всего три entries G3.
Request IDs: `integ2-inventory-ordinary-20261031`, `integ2-inventory-controls-20261031`,
`integ2-measurement-controls-20261031`. G1 request опубликован review-коммитом; UUID отсутствуют.
G2/G3 получат отдельные published request SHA после GO, при том же library tree.
Все native inventories, предупреждения компилятора и proof measurements: NOT_RUN.

| G3 control (сокращённо) | Ожидаемая location frozen source | Результат |
|---|---|---|
| merge::general_stable_direct_value_corruption_control_u64_n2 | merge.rs:841..845 count | NOT_RUN |
| network::insert_tail_contract_u64_start1_prefix_frame_control | network.rs:1257 prefix | NOT_RUN |
| network::insert_tail_contract_u64_start1_suffix_frame_control | network.rs:1260 suffix | NOT_RUN |

Sortedness assert merge.rs:839 не должен отказать; каждый control должен иметь ровно один
intended FAILED, достижимые covers и отсутствие иных отказов/OOB. План: `integ2/controls-plan.json`.
Known expect_check — `This is a placeholder message`; фактические location/class сверяются вручную.
Matcher mismatch не переименовывать в gate=true. Controls пока не приняты.

Полные envelopes G1/G2/G3:60/90/60min; максимальные резервы $0,810/$1,215/$0,810=$2,835.
Перед каждым dispatch обязательны свежий k1g budget, own UUID ledger и full-envelope check.
G3 только при own spent+reserved+$0,810≤$2,90 и достаточном окне, иначе NOT_RUN/PARTIAL.
T0 UTC11:58, deadline UTC16:58 (MSK19:58), резерв закрытия30min; `integ2/window.json`.
Только k1-standard4; CAP_USD73.96, Kani pin, toolchain, flags и lane прежние.
Четвёртой сборки нет; semantic delta требует нового review/GO.
Native P2, macOS, положительные integration proofs и полный CI: NOT_RUN.
macOS/полный CI и итоговый inventory после cfg-отбора принадлежат координатору.
Следующий шаг: PRE-BUILD REVIEW опубликованного SHA и остановка до GO Claude Code.
