# Независимая сверка отчёта Item 2 — 2026-11-20

**Вердикт: MINOR FIXES.** Проверенные численные значения, статусы и границы admissions подтверждаются. Вывод «пункт 2 не закрыт» корректен. Найдены пропущенная существенная оговорка опубликованного baseline и неполный путь в приложении; исправления приведены ниже. Оснований считать bounded admissions общим sorting/UB theorem нет, и отчёт этого не утверждает.

Проверен `REPORT-CH8-ITEM2-STATUS-RU.md` из planner commit `1e27f92344d844a7668d520065f21645b2d59572`, без изменений в исходном отчёте. Входной HEAD g0: `cba9ec66caea8aff0fa9cc12ccdc36a0f36a53ac`. SHA256 отчёта: `66aae9d577527bbddf527d2a0dd538c7fc786a5716bbf9c7d5fb1ed9bf9f8186`.

Источники читались непосредственно через `git show COMMIT:PATH`; `AUTHOR-CHECK.json` не использовался. `SOURCE-SNAPSHOT.json` использован как указатель на источники и как самостоятельный объект только для проверки утверждений о самом snapshot. Для всех 47 source records заново проверены существование commit/blob, Git blob ID, SHA256 и размер исходных committed bytes. Это проверка происхождения, а не новое native доказательство. Дополнительно через `gh` прочитаны только metadata/body #752 и metadata 27 runs; logs/jobs logs/artifacts не запрашивались. CI, compiler, Cargo, rustc, Kani, CBMC, acquisition/replay/Validate scripts не запускались. Работали две ограниченные независимые read-only сверки: домены/criteria и числа/ресурсы.

Обозначения N1…DEP ниже имеют **точные repository/commit/path из приложения проверяемого отчёта**, сверенные с Git. Для `kani3300/...` полный префикс — `research/challenge-8/kani-k1/`. Для L правильный путь указан в F02. `P0` — body #752, прочитанный заново через `gh api repos/model-checking/verify-rust-std/pulls/752`; совпадение с зафиксированным body проверено по содержанию. PASS исторического author-reported числа означает точную передачу claim источника, а не независимое подтверждение исторического native verdict. Номера строк относятся к pinned source; `/rows/N` — JSON pointer, индекс с нуля.

## Проверенные утверждения

В таблицах 120 групп проверенных утверждений: 118 PASS и два FAIL, включая все 13 строк сводки §3.2 и все числовые значения §5–6. Внутри группы несколько связанных значений проверены каждое; группы не являются числом теорем или proof credit. GitHub metadata перечислены отдельно.

| ID | Место / проверенное утверждение | Итог | Прямой источник / координата |
| --- | --- | --- | --- |
| C01 | §1: семь UB-целей — три trait entries и четыре перечисленных helper | PASS | N1, строки 19–27 |
| C02 | §1: sorting contracts требуются для трёх trait entries | PASS | N1, строки 29–36 |
| C03 | §1: цитата `for all possible slices with arbitrary valid length` | PASS | N1, строки 35–39 |
| C04 | §1: SAFETY и dangling/misaligned, uninitialized reads, immutable writes, invalid values | PASS | N1, строки 41–53 |
| C05 | §1: automation, принятый integrated tool, passing PR checks, запрет runtime-изменений | PASS | N2, Solution Requirements, строки 32–49 |
| C06 | §1: fallback≤16, general/network≤32 — рабочая редукция, не замена arbitrary length | PASS | CLOSE, строки 17–24 |
| C07 | §1: arbitrary helper length/offset не следует из фиксированных длин | PASS | CLOSE, строки 91–102 |
| C08 | §1: u8/Cell/NonCopyByte и чистый KeyLess не покрывают generic T/F, panic/ownership/layout | PASS | MODEL, Project/key_less!/active_model!; CLOSE, строки 61–110 |
| C09 | §1: sortedness плюс полный multiset; tie stability отдельно; OFF не доказывает все UB-классы | PASS | MODEL, active_post; P0, Limitations; CLOSE, строки 112–125 |
| B01 | §2: #752 open, head872d5a…/submission/ch8-smallsort, base25b2b2… | PASS | Свежие PR metadata, таблица ниже |
| B02 | §2: 235 ordinary harness +13 opt-in controls, cfg обычным CI не включён | PASS | P0, What is checked / Negative controls; source-reported scope сохранён |
| B03 | §2: general/stable u8/u64 N0..9, fallback N0..6 | PASS | P0, Highlights / coverage table |
| B04 | §2: network sortedness до13, count ниже9, distinct-tag N9/N13 | PASS | P0, coverage table / full-value oracle explanation |
| B05 | §2: safety matrix до32, размеры1/8/16/17/85/86, массивы16/17/85/86, Drop/Cell/ZST | PASS | P0, Highlights / Safety row / Limitations |
| B06 | §2: insertion offsets u64 N1..20; это не sorting correctness для всех T/N | PASS | P0, Safety row / Contracts |
| B07 | §2: 16 actual-helper PFC +4 verified consumers; три N2 wrappers не равны trait-method contracts | PASS | P0, Contracts / Challenge criteria; CLOSE |
| B08 | §2: run42363378063, historical235/OS,978/978 covers,7802/10534с, maxima246/340с | PASS | P0, CI; run metadata подтверждают success/head, численные native итоги остаются author-reported |
| B09 | §2: 71 assume(false) panic stubs; comparator panic/unwind не доказаны | PASS | P0, Limitations / Panics |
| B10 | §2: pins cd355b0bccd32300713bc2ce4f765dafa1510607 / c5e65fdfc3e15ec32293f2a4c07509aebec033c9 / 0aac16ef62da9e9d5645782d458593e5d78143ba | PASS | P1/P2 `[kani].commit`; TOOL и pinned S-line sources |
| B11 | §2: S1–S4P3 ещё не интегрированы в опубликованную голову | PASS | Свежая head #752; UPD, Attribution gate; отдельные source pins admissions |
| D01 | §3.1/3.2 entry smoke:35/35, шесть bodies, N0..3,22 PFC chains, восемь негативов, два origin runs | PASS | S1A, строки 17–28/54–67/95–104; S1R; L, S1 admission |
| D02 | §3.1: S2 — cost probe; compile/registration failures, general32 RSS, merge32/sort13_assumed child600, без provider credit | PASS | L, S2 r0…r5; строки с runs44336681406/44375519132 |
| D03 | §3.2 swap: C, u8/KeyLess, V34, base0..20, indices0..12, включая равные | PASS | S3Q, строки 8–14 |
| D04 | §3.2 sort4 separate: C, два backing6, active[1,5), полный u8 | PASS | S3Q, строки 8–14 |
| D05 | §3.2 sort4 same: C, backing48, disjoint ranges4, starts0..44, exact metadata exception | PASS | S3Q, строки 8–14/22–28; S3L |
| D06 | §3.2 merge separate: C, два backing10, active[1,9), sorted halves4+4 | PASS | S3Q, строки 8–14 |
| D07 | §3.2 MU48: C, src[32,40),dst[0,8),known[8,48),halves4+4; только functional/known-value frame | PASS | S32Q, строки 19–32; init-state/dstinit theorem не дан |
| D08 | §3.2 insert_tail: C, V34/base1/relative-tail1/span2; один case из16, не все геометрии | PASS | BQ, строки 6–9/35–40 |
| D09 | §3.2 sort9: O, actual25 swaps, V34/base1/len9, u8/KeyLess | PASS | BQ, строки 10–12 |
| D10 | §3.2 Cell fallback: O, два блока N0..2/N3..4; union0..4 только этого контекста | PASS | FQ, строки 3–7/16–19; FR |
| D11 | §3.2 network-r2: O, N2/N3/N4/N01 с обеими длинами; четыре Q, union0..4 | PASS | NQ, строки 3–5; NR, строки 9–24 |
| D12 | §3.2 network: O, только exact{8,9}, два Q | PASS | P3Q, строки 3–8; P3R |
| D13 | §3.2 N13/N17: O, тот же полный u8/V34/base1; BLOCKER child600, inventories/roles/covers UNKNOWN | PASS | P3Q, строки 25–32; P3R, строки 15–22 |
| D14 | §3.2 две partial MU геометрии — DIAGNOSTIC_ONLY_INITIALIZATION_OPEN | PASS | S32Q, строки 29–35 |
| D15 | §3.1/3.2 literal calls не заменяют actual network; N8 tails1..7,N9 sort9/empty suffix,N13 sort13,N17 tails13..16 | PASS | NPK, строка14; STD, строки351–389; P3R, строки18–22 |
| D16 | §3.2 no_merge=len<18; N17 не исполнил merge; general/network18..32 — иной путь | PASS | STD, строки351–389; P3R, строка22 |
| D17 | §3: APPROVE N13/N17 — approval классификации blocker, не положительный proof | PASS | P3R, строки1–3/15–16 |
| D18 | §3: leaves не дают caller entailment, provider, generic theorem, panic/Drop/permission или общий entry contract | PASS | S3Q, строки32–36; CLOSE, строки40–59/61–125; P3Q |
| A01 | §4.1: полный logical u8 для трёх T; owned Snapshot; closed comparator; inactive enabled=false | PASS | MODEL, строки11–66/68–92/125–166 |
| A02 | §4.1: post проверяет length/order и count каждого входного value; полный multiset и duplicates, O(N²) | PASS | MODEL, active_post, строки94–123; равные длины исключают novel-value остаток |
| A03 | §4.1: full backing frame + arbitrary outside canary | PASS | HARNESS, каждый positive: loop0..34 и canary assume/assert |
| A04 | §4.1: tool source declarations nightly-2026-10-23, CBMC6.11.0,Kissat4.0.1 | PASS | TOOL `[toolchain].channel`; DEP CBMC_VERSION/KISSAT_VERSION; это не solver-binary audit |
| A05 | §4.1: network-r2/S4P3 positives Original без stubs/verified/provider/summary | PASS | NR, строка9; P3R, строка9; NI, строка43 |
| A06 | §4.2: order/count corruption, weak descending13 seam, Cell[0,1]→[0,0]; designated failure и Cell activation | PASS | NI, строки43–50; P3R, строка43; FQ/P3PK |
| A07 | §4.2: четыре positive roles, feasible six covers; N01 только3 SAT, включая обе длины | PASS | NR, строки13–18/38; NI, строки25–28; HARNESS |
| A08 | §4.3: strict0/8,expected_match=false,SELECTED_PARTIAL,workflowFAILURE не переписаны admission | PASS | NQ/P3Q, concluding status paragraphs; NI/P3I inventories |
| A09 | §4.3: U только per-instance/source-local; mandatory role не U; guards/failures/covers/incomplete сохраняются | PASS | NR, строки28–42; P3R, строки24–53 |
| A10 | §4.3: network-r2 67 U, включая16 merge U;13 model/builtin metadata records | PASS | NI, строки5/25–28; NR, строки28–42 |
| A11 | §4.3: S4P3 subtotal655 относится к шести complete inventories; два timeout inventories UNKNOWN | PASS | P3I, строки3–5; P3Q, строки25–32 |
| A12 | §4.3: Q bounded/source-reported, без independent AST/MIR/emitter и B1/B2 credit | PASS | S3Q/NQ/P3Q, scope/open-credit paragraphs |
| A13 | §4.4: SUCCESS system class unreachable с null file/line отличается от status UNREACHABLE | PASS | S3L/S32Q/FQ, exact metadata record descriptions |
| A14 | §4.4: metadata cases1 sort4same +3 merge +2 fallback=6; qualified positives1+1+2=4 | PASS | S3L/S3Q/S32Q/FQ; самостоятельный пересчёт этих множеств |
| A15 | §4.4: общий emitter study — пять3merge+2fallback; sort4 reference отдельно | PASS | ZERO, строки5–9; S3L |
| A16 | §4.4: MIR template — кандидат, actual emitter/site/span UNKNOWN; wildcard не применён | PASS | ZERO, строки5–11 |
| A17 | §4.4: bridge/network-r2/S4P3 без нового missing-location exception | PASS | BQ; NR, строки40–42; P3Q, строки21–23 |
| A18 | §4.5: review→root finalValidate→GO→source publication→same-parent sibling→ch8-s2→compact intake→review→admission | PASS | NPK/NI/P3I; NG/P3G и GO-REQUEST.md в тех же GO commits |
| A19 | §4.5: snapshot/PID/reap/cleanup/prefix gates; upload не делает incomplete proof COMPLETE | PASS | NI, Resource/timing/containment; P3I, lifecycle/inventory distinctions; это обвязка |
| A20 | §4.5: exact,jobs1,no-assert-contracts,600s,object-bits12 и восемь unstable flags; uninit/value OFF | PASS | RES `/flags`; NPK/NR; producer cfg s2_assumed не означает positive stub |
| A21 | §4.5: базовые unstable flags/no-assert-contracts совпадают с organiser, exact-singleton workflow отличается | PASS | P3 `unstable_args`/verify-std commands; RES/NPK |
| A22 | §4.5: positives36, controls34/34/34/36; frame loop34 требует собственного unwind | PASS | HARNESS; P3PK, строки76–78; NP/RES; larger-domain sufficiency не заявлена |
| L01 | §5.1: pinned ledger26db9b6306…,item2 used18, tracking-only, не cap | PASS | L, Item2 used и owner2026-11-19 policy |
| L02 | §5.1: первые три S1 IDs43775527125/43777127361/43784240498 и compile/list/partial outcomes | PASS | L, строки119–156; свежие run metadata |
| L03 | §5.1: следующие четыре43830757263/43864841077/43889560779/43923266772 и decoder/location/finalization limits | PASS | L, строки166–182; свежие metadata; workflow success43923266772 не означает Q |
| L04 | §5.1: composite origins44095954742/44128268928 и35/35 | PASS | L, строки183–184/225–261; S1R; metadata |
| L05 | §5.1: S2 IDs44336681406/44375519132 — RSS затем timeout/GLOBAL_STOP | PASS | L, соответствующие S2 r4-r2/r5 rows; metadata |
| L06 | §5.1: S3 IDs44416629057/44439462279; bridge44460583125;fallback44481580554 | PASS | L/S3Q/S32Q/BQ/FQ; metadata |
| L07 | §5.1: S4 IDs44505531344/44548842328/44577116178 и4timeout→4success→N8/N9+2timeouts | PASS | NI1/NQ/P3Q; metadata; workflow FAILURE отделён от native success |
| L08 | §5.1: неучтённые43827636574/43829165289/44264952389/44284869572/44302170220/44310254730/44328364855/44405927807 | PASS | L, explicit charge0 decisions; все восемь ID сверены metadata, positive proof им не приписан |
| T01 | §5.2: единицыVT/child; GiB=KiB/1048576; headroom600−child только completed | PASS | COST source metric fields; пересчёт округлений и разностей |
| T02 | Swap: VT27.297,child62.995,RSS1.843,headroom537.005 | PASS | S3I `/rows/2` |
| T03 | Sort4 separate:78.983/120.782/2.447/479.218 | PASS | S3I `/rows/3` |
| T04 | Sort4 same:212.238/254.769/2.192/345.231 | PASS | S3I `/rows/4` |
| T05 | Merge8 separate:150.964/191.767/2.453/408.233 | PASS | S3I `/rows/6` |
| T06 | Merge MU48:197.389/236.409/2.691/363.591,init OPEN | PASS | S32I `/rows/4`; S32Q |
| T07 | Insert-tail:51.863/94.058/2.073/505.942 | PASS | BI `/rows/3` |
| T08 | Sort9:223.202/260.338/2.468/339.662 | PASS | BI `/rows/4` |
| T09 | Cell N0..2:140.742/189.050/2.866/410.950 | PASS | FI `/rows/4` |
| T10 | Cell N3..4:144.622/193.600/2.668/406.400 | PASS | FI `/rows/5` |
| T11 | Network-r2 N2:3.061/41.716/2.491/558.284 | PASS | NC `/rows/4` |
| T12 | Network-r2 N3:3.846/43.751/2.428/556.249 | PASS | NC `/rows/5` |
| T13 | Network-r2 N4:4.692/44.183/2.109/555.817 | PASS | NC `/rows/6` |
| T14 | Network-r2 N01:33.428/72.998/2.163/527.002 | PASS | NC `/rows/7` |
| T15 | Network N8:109.308/143.320/2.509/456.680 | PASS | P3C `/rows/4` |
| T16 | Network N9:207.138/242.435/2.470/357.565 | PASS | P3C `/rows/5` |
| T17 | N13/N17: VT UNKNOWN,child600.071/600.152,RSS2.447/2.521;child wall,не RSS/compile cutoff | PASS | P3C `/rows/6`, `/rows/7`, `/censored_cases` |
| T18 | Старый rel16:112.349с/6.034GiB RSS cutoff | PASS | S3I `/rows/5/execution`; S3Q |
| T19 | Старые variable tails:131.465/126.130с,RSS6.067/6.037GiB | PASS | S32I `/rows/3`, `/rows/5` |
| T20 | Broad bridge fallback/network,S4P1 network,4symbolic network — wall600,память нижеlocal6GiB | PASS | BI `/rows/5`, `/rows/6`; FI `/rows/6`, `/rows/7`; NI1 network rows |
| T21 | Campaigns1454.136/1068.751/1672.393/1779.707/2535.875/359.381/1722.953с | PASS | S3I/S32I/BI/FI/NI1/NC/P3C `/campaign_elapsed_seconds`, в указанном порядке |
| T22 | Network-r2 setup531.185с,job898с отличаются отcampaign359.381с | PASS | NI, Resource/timing/containment; S5T, строки106–124 |
| T23 | S1 Cell stable617.990,unstable485.290с,cap1200; не uniform600 | PASS | L, строки258–261; S5T |
| T24 | Child600/compile180/slot720/controller180/cleanup240/campaign6900/outer7500/step7560/phase8100/setup1800/job180min | PASS | RES `/caps`,`/budgets`; S5T, строки42–56 |
| T25 | Local6/outer12/reserve2GiB,Ceff=min(6,12,A−2) | PASS | RES KiB caps; NI, effective local caps; S5T |
| T26 | stdout16/stderr1/export8/artifact256MiB; полный peak и exclusive solver UNKNOWN | PASS | RES `/caps`; NI, metric limitations; S5T |
| R01 | §6.1: N13/N17 compile-marker upper33.869/32.884с,whole-child600,нет complete results/resource export | PASS | P3C `/rows/6`, `/rows/7`, `/censored_cases`; P3R, строки63–68 |
| R02 | §6.1: из600−marker нельзя получить solver time или нулиU/FAIL/covers | PASS | P3C/P3R, censored-cost interpretation |
| R03 | §6.1: N17 ещё доmerge; sort13/oracle hotspot и phase times не локализованы | PASS | STD/P3R, строка22; P3C, censored_cases |
| R04 | §6.1: independent q:u8 —256values; один count O(N) против nestedO(N²), лишь гипотеза дизайна | PASS | MODEL, active_post; математическая сверка, native equivalence/fit не объявлены |
| R05 | §6.2: OFF is_initialized не init theorem; ON plan BLOCKED/CONDITIONAL,copy0/downward/AddressOf/mask/capture открыты | PASS | ON, feasibility plan и risk/control requirements |
| R06 | §6.2: MU48 known[8,48) и sorted dst не устанавливают initialized reads/сохранение holes | PASS | S32Q, строки19–35; ON |
| R07 | §6.2: validity и immutable-write/permission самостоятельны; value frame не исключает write-restore | PASS | N1; CLOSE, строки112–125; ON |
| R08 | §6.3: toolchain/list/schema/shallow/contracts и потерянный compile diagnostic | PASS | L, S1/S2 rows; потеря diagnostic в run44284869572 явно UNKNOWN |
| R09 | §6.3: selected_roots=8 при7rows,неверные types/counts local/upload | PASS | RCOUNT, строки7–15/24–26 |
| R10 | §6.3: неполная powerset cfg matrix и missing terminal-schema gate | PASS | RGATE, findings; это gate-completeness defect,не native counterexample |
| R11 | §6.3: snapshot-path false positive S3; interrupted compile S2 GLOBAL_STOP | PASS | L, runs44405927807 и44375519132 |
| R12 | §6.3: четыре censored symbolic600 не устанавливают N-independent cost/compiler cause | PASS | NI1/N01/NP/NC; native verification UNKNOWN у старых timeout |
| R13 | §6.3: final synthetic366tests/685.015с,389/701.366с;не native proof | PASS | NG/P3G `/internal_result/test_counts` sums366/389; `/outer_elapsed_seconds` rounds685.015/701.366 |
| R14 | §6.3: новый u8/KeyLess не subsume u64/tied-key/Drop/ZST/mutating-F/consumers;source trust seam открыт | PASS | P0/S5 legacy map; ZERO/NR/P3R |
| R15 | §6: general0..32,fallback5..16,network gaps{0..4,8,9},type/threshold/geometry/entry closure не закрыты | PASS | CLOSE/P3Q; планы не считаются execution; новые tool fixes не являются organizer adoption |
| P01 | §7: планы PLAN ONLY,не reservation/GO;1–2дня/0CI/1pilot/дни–недели — estimates,не evidence | PASS | S5/UPD scope; SNAP `/planning_estimates`, явная авторская оценка |
| P02 | §7: gaps5..7/10..12/14..16/18..32,merge/copyback иsameT/F требуют новых результатов | PASS | CLOSE/STD/P3Q; current accepted set не интерполируется |
| P03 | §7: шесть implementation bodies,entryPFC/caller/init/threshold и independent ON lane | PASS | CLOSE, строки61–125; UPD future sequence; ON |
| P04 | §7:23positives/43invocations/5hypothetical campaigns,retained/provider lanes сверхcore | PASS | S5, строки108–138; S5T; это арифметика плана,не пять выданных запусков |
| P05 | §7: matched totalVT/critical shard/concurrency/setup/build/compile/job,историческиKANI_JOBS=2;600 не whole-CI budget | PASS | S5T, строки137–149 и timing-scope discussion |
| P06 | §8: все12 audit questions относятся к реально открытым scope/type/MIR/U/emitter/oracle/cost/ON/retention/infrastructure seams | PASS | N1/P0/S1R/NR/P3R/ZERO/MODEL/CLOSE/ON/S5/RCOUNT/RGATE/S5T; ответы не выдаются за proof |
| X01 | §9: snapshot commit2a0becc18c7580c6d39f5d20a02c0cea37dbf924,47Git-source records,56cost rows | PASS | Commit:path snapshot даёт тот же blob `fcfb04984623d0e3bc9a0d548bba072279292093`; длины массивов47/56; все47 source hashes сверены отдельно |
| X02 | §9: все47 source commits существуют; source paths разрешаются,разные std/Kani repositories различены | PASS | Независимый git blob/hash/size check всех47 records; TOOL/DEP в Kani repo; оговорка о печатном L в F02 |
| X03 | Весь отчёт: нет чужих challenge PR/solutions и external research links | PASS | Полное чтение; единственное `#number` — #752; нет HTTP(S) URLs/внешних markdown links; локальные research-пути не внешние ссылки |
| F01 | §2/§4: полнота раскрытия известных model limitations baseline | FAIL | P0, Limitations / Model trust; четыре array-valued fixtures caveat не перенесены в отчёт |
| F02 | §9: самодостаточность указанного пути L для `git show COMMIT:PATH` | FAIL | В приложении напечатано `CH8-DISPATCH-LEDGER.md`; реальный pinned path содержит research/challenge-8/kani-k1/ |

## GitHub metadata: IDs, attempts и головы

Прочитано 2026-11-20 UTC. Команды были read-only: `gh api repos/model-checking/verify-rust-std/pulls/752`, `gh api repos/Tiramisu-Cake/kani/actions/runs/ID` с проекцией `id,run_attempt,status,conclusion,head_sha,path,created_at` и `gh run view 42363378063 --repo Tiramisu-Cake/verify-rust-std --json ...`. Логи не читались. Все runs ниже `completed`, `attempt=1`; все проверки ID/attempt PASS. Conclusion workflow не подменяет native verdict/admission.

#752: `state=open`, head `872d5a43380752786415bc00d2a12ce0e930cb37`, head ref `submission/ch8-smallsort`, head repository `Tiramisu-Cake/verify-rust-std`; base `main`, SHA `25b2b24c82a960734a2bab082784747b9b785177`; `updated_at=2026-11-16T13:10:52Z`. Все соответствующие поля отчёта PASS.

| Run ID | Repository | Head prefix | Workflow conclusion | Сопоставление |
| --- | --- | --- | --- | --- |
| 42363378063 | Tiramisu-Cake/verify-rust-std | 872d5a4338 | success | P0,baseline,Kani workflow |
| 43775527125 | Tiramisu-Cake/kani | 83f88a9075 | failure | L,S1 |
| 43777127361 | Tiramisu-Cake/kani | 79542c7733 | failure | L,S1 |
| 43784240498 | Tiramisu-Cake/kani | 8233b98c15 | failure | L,S1 |
| 43830757263 | Tiramisu-Cake/kani | 205b0e98c7 | failure | L,S1 |
| 43864841077 | Tiramisu-Cake/kani | 8860d38558 | failure | L,S1 |
| 43889560779 | Tiramisu-Cake/kani | a14a513eb7 | failure | L,S1 |
| 43923266772 | Tiramisu-Cake/kani | b37f6f75c5 | success | L,S1;не proof qualification |
| 44095954742 | Tiramisu-Cake/kani | 21592884db | failure | L,S1 original |
| 44128268928 | Tiramisu-Cake/kani | 4336dfed5a | success | L,S1 Cell retry |
| 44336681406 | Tiramisu-Cake/kani | 6157554df8 | failure | L,S2 |
| 44375519132 | Tiramisu-Cake/kani | 33c687e43d | failure | L,S2 |
| 44416629057 | Tiramisu-Cake/kani | 7497ecdb39 | failure | L,S3Q |
| 44439462279 | Tiramisu-Cake/kani | 474a9d1617 | failure | L,S32Q |
| 44460583125 | Tiramisu-Cake/kani | c2bbdb972c | failure | L,BQ |
| 44481580554 | Tiramisu-Cake/kani | 563a899dce | failure | L,FQ |
| 44505531344 | Tiramisu-Cake/kani | 9c63491609 | failure | L,NI1 |
| 44548842328 | Tiramisu-Cake/kani | d88fac48cf | failure | L,NQ/NI |
| 44577116178 | Tiramisu-Cake/kani | 960cc68609 | failure | L,P3Q/P3I |
| 43827636574 | Tiramisu-Cake/kani | 5fd5387308 | failure | L,charge0 schema |
| 43829165289 | Tiramisu-Cake/kani | 2a532e5913 | cancelled | L,charge0 shallow Validate |
| 44264952389 | Tiramisu-Cake/kani | 056c7d2ae4 | failure | L,charge0 compile |
| 44284869572 | Tiramisu-Cake/kani | bdedeae662 | failure | L,charge0 compile |
| 44302170220 | Tiramisu-Cake/kani | 59ff2f1d98 | failure | L,charge0 compile |
| 44310254730 | Tiramisu-Cake/kani | 6d7f3c4b5b | failure | L,charge0 compile |
| 44328364855 | Tiramisu-Cake/kani | 173ed30be4 | failure | L,charge0 Validate timeout |
| 44405927807 | Tiramisu-Cake/kani | d92581141b | failure | L,charge0 controller BEFORE |

Для первых девяти учтённых S1 runs и двух charge0 S1 workflow path `.github/workflows/ch8-s1.yml`; для остальных перечисленных Kani runs — `.github/workflows/ch8-s2.yml`. 18 учтённых и восемь charge0 ID подтверждены как существующие metadata; accounting остаётся решением pinned ledger, не нашим пересчётом бюджетов.

## Исправления FAIL и пропуски для аудитора

**F01 — добавить baseline array-model caveat.** §2 перечисляет массивы и safety matrix, §4.1 говорит о доверии модели, но пропускает конкретный известный defect/caveat из опубликованного baseline. Источник: body [нашего #752](https://github.com/model-checking/verify-rust-std/pull/752), `Limitations` → `Model trust`, также pinned `2a0becc18c7580c6d39f5d20a02c0cea37dbf924:research/challenge-8/kani-k1/item2-status-report-20261120/SOURCE-SNAPSHOT.json`, JSON pointer `/pr752/body`. Прочитан сам актуальный body; snapshot не использован вместо него. Исторический status defect не перепроверялся и не должен подаваться как новый результат.

Предлагаемая вставка после перечисления baseline types:

> В опубликованном #752 отдельно сохранена оговорка о доверии модели массивов на organizer pin cd355b0b: автор сообщает о failing array-select reproducer. Она относится к `network::swap_contract_bytes16_n2`, `network::swap_contract_bytes17_n2`, `merge::sort4_contract_bytes16_n4` и `merge::sort4_arbitrary_comparator_bytes16_n4`. Это ограничение четырёх исторических array-valued fixtures, не новый counterexample сортировки и не автоматически перенесённый verdict для новой u8-линии.

Эта вставка не требует ссылки на чужой challenge PR/solution или external research: достаточно P0 и имён собственных fixtures. Сейчас общий вывод отчёта не завышен, но внешний аудитор должен видеть конкретную оговорку, а не только общее «доверяем модели».

**F02 — дописать путь L.** В приложении §9 указать `research/challenge-8/kani-k1/CH8-DISPATCH-LEDGER.md` вместо голого `CH8-DISPATCH-LEDGER.md`, сохранив commit `26db9b630682cfae8670392ea9236d701f45b481`. Вводная фраза сейчас раскрывает префикс именно для `kani3300/`, а L так не начинается. `git show 26db9b630682cfae8670392ea9236d701f45b481:CH8-DISPATCH-LEDGER.md` не разрешается; полный путь разрешается и содержит заявленные решения. Commit и содержимое L верны; это дефект навигации/воспроизводимости, а не учёта.

**Дополнительное уточнение, не factual FAIL.** В §4.5 полезно ограничить формулировку о supervisor наблюдаемой полнотой lifecycle evidence. NI прямо сохраняет bounded lifecycle diagnostics с omitted events UNKNOWN, одновременно отдельно подтверждая completion/shutdown/protected observations. Источник: `7c66fb85b99f77801ff10e99ccc5d37761ba5442:research/challenge-8/kani-k1/kani3300/ch8-s4/run-44548842328/HANDOFF.md`, абзац `Each row retains64 lifecycle diagnostics…` в Resource/timing/containment. Предлагаемое предложение: «Часть lifecycle diagnostics ограничена preview; пропущенные события остаются UNKNOWN. Проверенные completion/shutdown/protected observations не означают полный trace всех событий». Это не отменяет source-reported admission и не требует читать raw logs.

Проверенные ограничения «что это НЕ значит» согласованы с admissions: normal-return bounded cases не повышены до generic/all-length theorem; реальные helper bodies отделены от proof-owned models/wrappers; выбранные u8/Cell/NonCopyByte не объявлены всеми T/F; exact lengths не интерполируются; initialized backing и known-value MU frame не названы init-mask theorem; SUCCESS system metadata не смешаны с UNREACHABLE; incomplete inventories остаются UNKNOWN; fork workflow и отдельное admission не названы passing organizer PR checks. Существенных overclaims среди этих утверждений не найдено.

Это завершённая одна read-only стадия fact-check. Новых admissions, proof credit, запусков, исключений, accounting или изменений исходного отчёта этот документ не создаёт.
