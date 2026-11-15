# C-сейчас: shared spans и frames

Статическая стадия worker14; вход g0 `ea3cec4078a2b1598d4d4f5d3bd62db9c1a13dde`.
Новых proof results нет. `STOP C` для полного immutable-byte/alias claim сработал;
это не мешает передать законченный статический пакет.

## Identities и чтение таблиц

- **P**: production std `872d5a43380752786415bc00d2a12ce0e930cb37`, tree
  `384023c2f80a04d0618aa7ce971b1419494b062b`, Kani
  `cd355b0bccd32300713bc2ce4f765dafa1510607` из `tool_config/kani-version.toml`.
- **S**: S1 std `75a4d1ea6eb60c63c27c1b18e662740d93bafb08`, tree
  `6d1b90bc11440762c9b65889fc538ba3071b0d9d`, Kani **U**
  `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree
  `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.
- `body:L` означает P:`library/core/src/slice/sort/shared/smallsort.rs:L`;
  `verify/x:L` — P:`library/core/src/slice/sort/shared/smallsort/verify/x:L`.
  Координаты S указаны явно. Чтение через pinned `git show`, без изменения source worktrees.
- Все harness suffix ниже имеют полный prefix
  `core::slice::sort::shared::smallsort::verify::`.
  CLI readable name stock U может опускать `core::`; source name и CLI selector не смешивать.
- **R**: [baseline-roots.tsv](../ch8-s1/w14/baseline-roots.tsv), исторические
  source-reported `SUCCESSFUL` Ubuntu/macOS, run **42363378063**; источник
  [published-timings-source.json](../ch8-s1/w14/published-timings-source.json):
  curated TSV blob `f1c1ed840ca9090284d42d57c082731b015a8865` при research
  `e63e7fadfdc8a9e4871f872fdf022092cbb7387e`.
  Это переданные результаты, не новый независимый B1/B2 credit, не raw logs.

Research/checkpoint статусы здесь зафиксированы на входном g0 ea3cec4078; live S1/B-01
intake не выполнялся. Последующие coordinator dispatch records не являются proof results этой стадии.

Frame ограничивает записи в существующую память вызывающего; локальные allocations callee
не нужно перечислять как внешние write targets. После-call equality сама по себе не исключает
write-then-restore. `modifies` становится проверенным frame в соответствующем PFC,
а в `stub_verified` — границей havoc; одна исходная аннотация или обычный `proof` не доказывает frame.
Disjointness исключает пересечение spans, но не устанавливает lifetime/provenance/tag permissions.

## Inventory: все лексические shared-span edges production SmallSort

`real` ниже означает реальное тело в source; overrides конкретных harness отдельно перечислены далее.
Динамическая полнота всех borrows произвольных T/F этим census не доказана.

| Edge и source | Body / заявленный frame и disjointness | Callback/captures/globals и использование после вызова |
|---|---|---|
| Три trait families и шесть impl bodies, `body:20–173` → fallback/general/network | P: real, без trait contracts. Safe fixtures дают exclusive v и отдельный scratch. S: frames разобраны ниже | Все передают тот же `&mut F`; его достижимое состояние generic frame не описывает. После helper return используются v, а у Stable — caller scratch |
| `small_sort_general`, `body:207–220`: local MU `[T;48]` → mutable scratch | Real; отдельного outer frame нет. Stack allocation отличается от caller v | Далее general-with-scratch пишет scratch, читает его через shared source при merge; после return локальный MU не читает/не drop-ит T |
| `general_with_scratch`, `body:222–295`: v → sort4/sort8; scratch halves, scratch `[len..len+16]`; insertion в scratch | Real; отдельного frame нет. Safe slice fixtures отделяют v/scratch; длина scratch ≥len+16 проверяется. sort4/merge имеют свои требует/disjoint frames | Callback видит v, затем scratch, включая временные копии. После сравнений выбранные source values копируются, scratch дополняется/перемещается. Это не глобальная readonly область на весь SmallSort |
| `general_with_scratch`, `body:280–293`: guard.src scratch `[0..len]` → `&[T]` merge, guard.dst v | Real merge; `modifies(dst[..len])`, `merge_contract_regions_disjoint`, len≥2, readable src/writable dst. Local guard хранит raw aliases | При normal return guard забывается. На unwind его Drop читает весь scratch и копирует в v; unwinding не доказан. Shared source жив в merge, guard raw src остаётся нужен на panic path |
| `CopyOnDrop::drop`, `body:297–311`: raw src → raw dst | Real `copy_nonoverlapping`; собственного contract/frame нет; initialized src, writable disjoint dst — условия call sites/comments | Для general src=scratch; для insertion src=local tmp. После копирования tmp/scratch перестают быть необходимы для восстановления. Нет самостоятельного generic Drop/frame proof |
| `small_sort_network`, `body:329–371`: MU `[T;32]`, две successive mutable regions v, затем v → shared merge source → scratch | Real; собственного frame нет. len≤32; no_merge при len<18; region меняется после предыдущего использования; merge disjoint require | Сначала callbacks на v в sort9/13/insertion; затем на v как shared merge source. После merge scratch копируется обратно в v. Запись в v после окончания shared span законна при соблюдении borrow rules |
| `sort9_optimal`/`sort13_optimal`, `body:454–564` → swap callbacks | Real сети; своего frame нет, leaf swap frame — только выбранная пара | Ref inputs создаются внутри swap; после return следующие swaps законно пишут/читают те же slots. Никакой escape references source не возвращает |
| `swap_if_less`, `body:413–445`: `is_less(&*v_b,&*v_a)` | Real; `modifies(v_base+a,v_base+b)`; same allocation, readable+writable обе позиции, checked offsets. a=b допускается, pair-disjointness не требуется | Callback generic может иметь captures/globals. После него выбранные значения читаются/перемещаются. Local MD `v_b_swap_tmp` читается через `&*tmp` в copy; это не callback input; после copy tmp не используется |
| `insert_tail`, `body:588–641`: первый callback `&*tail,&*sift` | Real; frame inclusive `[begin..tail]`, checked contract len, readable/writable single-allocation span, begin<tail | Сразу после callback tail может быть прочитан в MD tmp; sift/другие slots впоследствии сдвигаются. Outer writable span не разрешает запись во время live shared callback borrow |
| `insert_tail`, `body:621–640`: local MD tmp → guard.src и callback `&tmp,&*sift` | Real; тот же inclusive frame. tmp отдельный local, guard.dst передвигается внутри span; local src/dst disjoint по allocation | Callback временно видит tmp и текущий sift. Затем guard читает tmp и заполняет gap при обычном выходе/Drop; tmp нельзя считать мёртвым сразу после callback. Lifetime/tag и unwind guarantees отдельно не установлены |
| `insertion_sort_shift_left`, `body:646–675` → successive insert_tail | Real; `modifies(v)`, requires 0<offset≤len. Внутренние inclusive spans — prefixes v | Повторно использует v после каждого callback/insert; callbacks возможны с локальным tmp вне v. Внешний `modifies(v)` не проверяет разрешённость каждой записи относительно текущего `&T` |
| `sort4_stable`, `body:678–742`: пять callback calls на source/выбранных source pointers | Real; `modifies(dst[..4])`, readable src4, writable dst4, `sort4_contract_regions_disjoint` | Callback calls на строках 711,712,726,727,734. Source pointers сохраняются через последующие callbacks и читаются для четырёх копирований; frame + disjointness защищает src только в квалифицированных F domains |
| `sort8_stable`, `body:745–764`: source8 → scratch8 → `&[T]` merge → dst8 | Real; своего contract/frame нет. Две real sort4 с disjoint requires, затем merge с disjoint requires; геометрия задаётся caller | Временный scratch остаётся shared source в merge. Callback видит сначала исходные 4-spans, потом scratch; после merge scratch может повторно использоваться caller. Source algorithm требует Freeze для наблюдения копий |
| `merge_up`/`merge_down`, `body:767–831`: `&*right_src,&*left_src` → selected source copy | Real leaf bodies без собственных contracts; требования nonalias/read/write — comments и outer merge contract | После callback source читается для copy, указатели используются в следующих итерациях. Нельзя превращать комментарий nonalias в независимое proof всех caller geometries |
| `bidirectional_merge`, `body:833–941`: `v:&[T]`, forward/reverse/odd-last source spans, dst | Real; `modifies(dst[..v.len()])`; readable src, writable dst, len≥2, full-span disjointness. Arithmetic helper: checked byte count; different allocation либо distance≥bytes; для ZST bytes=0 | Все source subspans принадлежат v; callback внешние эффекты не включены. После каждой пары сравнений source pointers остаются живы, odd tail читается на 930; dst на order violation не читается. Returned values не содержат references |

## Proof/stub и effects boundary

Пять real helper contracts — swap, insert_tail, insertion, sort4, merge —
ограничивают только element/destination memory (`verify.rs:22–40`, `body:382–386`).
`is_less:&mut F` не входит в их write sets. Pure function items читают аргументы,
возвращают nondet bool либо фиксированный lawful key order; это не arbitrary effectful FnMut theorem.
`modifies(is_less)` разрешал бы bytes объекта closure, а не автоматически все pointees его captures/globals.

`verify/merge/profiles.rs:211–325`: checked wrappers `swap_profile`, `sort4_profile`,
`insert_tail_profile`, `merge_profile` вызывают real helpers; frames соответственно pair,
dst4, inclusive tail span, dstN. Requires добавляют canonical `P::CMP`, geometry,
sorted prefix/halves там, где нужны. Profile CMP — fn pointer; summaries не разрешены для нового F/geometry.
`PROFILE_PROBE_*`, `merge::VALUE_PROBE_BYTES`, Cell/Drop probe globals устанавливаются
fixtures до вызова и читаются моделями; comparator их не пишет. Drop-count counters и mutating
Cell fixtures не превращаются в разрешённые глобальные эффекты всех helper contracts.

Реальные algorithm/callback bodies в `merge`, `network`, `scratch_geometry`, `types`,
`fixed_inputs`, `tag_permutation` не заменены verified summaries. Отдельные roots
в merge/network/scratch/fixed_inputs заменяют **только** `panic_on_ord_violation` на
cover + assume(false): normal/abort boundary, не unwinding proof.

Verified summary edges production fixtures:

| Consumer root | Summary; соответствующая real-body PFC/domain |
|---|---|
| `helper_contracts::unstable_network_safety_u8_n9_stubbed`, `helper_contracts::unstable_network_safety_u8_n13_stubbed` | swap; `helper_contracts::swap_safety_u8_backing9`, `helper_contracts::swap_safety_u8_backing13`. `comparison_covers` дополнительно заменён пустым hook, так как callback bypassed |
| `helper_contracts_wide::unstable_network_safety_u8_n32_stubbed` | swap; `helper_contracts_wide::swap_safety_u8_backing32` с interior bases; insertion/merge real, order-panic cut |
| `helper_contracts_wide::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed` | merge; `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0`, тот же `tail_less_u64`; sort4 real. Safety-only summary не гарантирует initialized dst (`verify/helper_contracts_wide.rs:146`) |
| controls `helper_contracts::rejects_swap_outside_backing_u8`, `helper_contracts::rejects_insert_tail_equal_begin_u64`, `helper_contracts::rejects_merge_overlapping_dst_u64` | Stubbed requires negatives; не real-body temporal-mutation tests и не новые положительные domains |

## Proven / gap: точный уровень утверждения

В строках **R** ниже «следует» означает логическое следствие заявленного проверенного
frame + требует на **названном** domain, при source-reported успехе R. Независимая
переаттестация historical proofs и C-controls здесь не выполнена; общего C PASS нет.

| Claim | Root / pinned source | Что следует; предел |
|---|---|---|
| Merge source вне dst write set | P, R: `helper_contracts::merge_safety_u64_len2`, `helper_contracts::merge_safety_u64_len4`; `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` | dst-only frame + disjoint src запрещает записи в src в этих PFC. N2/4 separate allocations; N8 scratch48 src32/dst0. Transient negative ещё NOT_RUN |
| Ordered merge source confinement | P, R: `merge::merge_contract_u64_n2_to4`, `merge::merge_contract_u64_n5`, `merge::merge_contract_u64_n6`, `merge::merge_contract_u64_n7`, `merge::merge_contract_u64_n8`; `merge::merge_contract_u8_n2_to4`, `merge::merge_contract_u8_n5`, `merge::merge_contract_u8_n6`, `merge::merge_contract_u8_n7`, `merge::merge_contract_u8_n8`, `merge::merge_contract_u8_n9`; `merge::merge_scratch48_contract_u8_n9` | `profiles::merge_profile` frame dstN + disjointness, exact canonical LtU64/LtU8, sorted halves. Не arbitrary lengths/F и не generic source preservation theorem |
| sort4 source confinement | P, R: `helper_contracts::sort4_safety_u64`; `merge::sort4_contract_u64_n4`, `merge::sort4_contract_bytes16_n4` | dst4 frame + disjoint src4; arbitrary read-only comparator первого либо canonical Sort4ReadU64/Sort4ReadB16 двух последних |
| Swap не пишет вне pair | P, R: `helper_contracts::swap_safety_u8_backing4`, `helper_contracts::swap_safety_u64_backing4`, `helper_contracts::swap_safety_bytes17_backing4`, `helper_contracts::swap_safety_u8_backing9`, `helper_contracts::swap_safety_u8_backing13`; `helper_contracts_wide::swap_safety_u8_backing32`, `helper_contracts_wide::swap_safety_u64_backing32` | Pair frame, включая equal positions, wide interior base. Не readonly pair во время callback |
| insert_tail не пишет suffix вне inclusive span | P, R: `helper_contracts::insert_tail_safety_u64_tail1_to4_backing5`; `insert_tail_contracts::insert_tail_safety_u64_backing17_tail1_to7`, `insert_tail_contracts::insert_tail_safety_u64_backing17_tail8_to15` | Inclusive prefix frame; exact read-only arbitrary-answer comparator. Local tmp shared-ref temporal permissions из этого не следуют |
| Insertion ограничен v | P, R: `helper_contracts::insertion_safety_u64_len2`, `helper_contracts::insertion_safety_u64_len3` | `modifies(v)`, любой допустимый offset в N2/3. Не arbitrary length proof, не readonly bytes v при callback |
| Concrete trait forwarding ограничен pair | P, R: `forwarding_contracts::stable_cell_n2`, `forwarding_contracts::unstable_byte_n2`, `forwarding_contracts::freeze_noncopy_n2` | Wrapper frame pair; Stable Cell scratch disjoint и вне write set. Реальные trait bodies, canonical comparators. Это contracts wrappers N2, не contracts самих generic trait methods |
| Legal interior mutation внутри input | P: `network::mutating_route_safety_cell_n0_to4`, `network::mutating_route_safety_cell_n5_to8`, `network::mutating_route_safety_cell_n9_to12`, `network::mutating_route_safety_cell_n13_to16`; `network::mutating_insertion_safety_cell_n1_to5`; `verify/network.rs:539–634` | Real Cell callbacks пишут ключи через UnsafeCell и сохраняют tags. Наличие harness не устанавливает полноту UnsafeCell/alias checks; это также не проверка disjoint external callback state |
| Шесть S1 trait frames | S; [CONTRACT-SCOPE](../ch8-s1/integration/CONTRACT-SCOPE.md), [CHECKPOINT](../ch8-s1/integration/CHECKPOINT.json) | Только source/static-reviewed candidate, ALL_NOT_RUN; нельзя объявить доказанными |
| Generic callbacks/captures/globals; writes за live `&T` в разрешённом outer frame; guard unwind/lifetime/reuse | P/S | **GAP / STOP C**. Frame/disjointness недостаточно; отсутствие returned refs этого не меняет |

## Три trait entries и pin

P: `StableSmallSortTypeImpl::small_sort`, `UnstableSmallSortTypeImpl::small_sort`,
`UnstableSmallSortFreezeTypeImpl::small_sort` не имеют прямых contracts. Всего шесть
реализаций: Stable default/Freeze, Unstable default/Freeze forwarder, Freeze default/Copy.
P `verify.rs:55–58` сообщает blockers #4908/#5116 на cd355; wrapper proofs N2 их не снимают.

S: прямые `cfg(all(kani,kani_smallsort_sorting))` contracts на всех шести bodies:

| Entry family, S source lines | Frames | Подготовленные PFC roots (suffix после общего prefix) |
|---|---|---|
| Stable default 40, Freeze 62 | default `v`; Freeze `v,scratch` | `sorting_entry_smoke::stable_default_cell`, `sorting_entry_smoke::stable_freeze_u8` |
| Unstable default 91, Freeze forwarder 109 | `v` | `sorting_entry_smoke::unstable_default_cell`, `sorting_entry_smoke::unstable_freeze_u8` |
| UnstableFreeze default 139, Copy override 175 | `v` | `sorting_entry_smoke::freeze_default_noncopy`, `sorting_entry_smoke::freeze_copy_u8` |

Точные root spellings сверяются с S:`verify/sorting_entry_smoke.rs`; статус всех — NOT_RUN.
Frame scope: named ZST `sorting_model::KeyLess` для u8, Cell<u8>, NonCopyByte;
enabled/post snapshot facade не доказывает arbitrary-F frame, даже когда ensures inactive.
Scratch frame шире временного shared source: temporal mutation внутри него не исключена.
Requires ограничивают v.len() threshold соответствующего trait; Stable Freeze также требует
`v.len()<2 || scratch.len()>=v.len()+16`. Отдельного generic captured-state require нет.

U содержит исправления generic method contracts (#4908, PR #5135) и specialization defaults
(#5116, PR #5153), в отличие от P tool pin. Это позволяет ставить S1 PFC, но не является
SmallSort proof result. Наличие fixes не добавляет aliasing/lifetime instrumentation,
transitive captured-state footprint, generic FnMut theorem либо Replace qualification.
Точные upstream commit/test anchors дополнены в HANDOFF после статической сверки.

## STOP C

Сработали две установленные границы §9: arbitrary callback/captures не покрыты frames;
запись внутри outer v/scratch frame при живом shared borrow требует отсутствующей
temporal/lifetime/tag модели. Полнота generic borrow inventory не доказана.
`legal UnsafeCell rejected` **не наблюдалось**: новые controls не запускались.
Остановить расширение C-claim/собственную alias-модель; сохранить конкретные frame claims,
передать [дизайн controls](CONTROLS-DESIGN.md) для отдельного GO. B-01 intake не входит в стадию.
