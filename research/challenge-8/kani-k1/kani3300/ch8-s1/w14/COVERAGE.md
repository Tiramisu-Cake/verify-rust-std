# Old235 → future S3/S4: предварительная replace-map

Source: exact #752 head `872d5a43380752786415bc00d2a12ce0e930cb37`.
[replace-map.tsv](replace-map.tsv) содержит ровно235 уникальных старых ordinary roots,
class, T/F, fixture/domain token, pinned source+line, timings, panic-stub flag, proposed theorem,
обязательства перехода и пустые новые root/SHA/version. Это **план миграции**, не proof/удаление.
Все235 имеют `ordinary_keep_now=True`, `replacement_approved=False`.
Списки с других source heads сюда не подмешивались.

| Published class | Всего | Условные кандидаты S3/S4 | Сохранять без primary-S замены | Основная причина сохранения |
|---|---:|---:|---:|---|
| General/stable order+count | 25 | 0 | 25 | u8/u64 и `x>>1`, не ordinary `<` |
| Fallback order+count | 7 | 0 | 7 | каждый root включает u8 **и** u64, `x>>1` |
| Network order, count ниже9 | 16 | 10 | 6 | u64 не поглощён u8 |
| Insertion-phase count | 5 | 0 | 5 | arbitrary input/answer, offset9/13, без sorted-prefix premise |
| Safety/dispatch/reachability | 92 | 0 | 92 | arbitrary/mutating F, все offsets/types/ZST/size/scratch |
| Drop/tag | 19 | 0 | 19 | drop counts, mutating-key tag counts, source-route/tag theorem |
| Logical trait entries | 6 | 4 | 2 | оставшиеся `types::DropKey` не равны новым non-Copy wrappers |
| Helpers/fixed witnesses | 9 | 3 | 6 | pointer advancement/arbitrary answers/size predicate/equal positions |
| Profile PFC | 36 | 4 | 32 | other T, tied-key order, canonical guard, exact allocation |
| Real-helper PFC+consumers | 20 | 0 | 20 | arbitrary-answer F, actual PFC and matched verified-stub usage |
| **Всего** | **235** | **21** | **214** | **утверждённых замен0** |

**Цена21 кандидата** в историческом autoharness: Ubuntu542.482283710s,
macOS696.790303310s. Остальные214 стоят7259.397374337s /9837.669368604s.
Это максимум VT удаляемых старых строк в этом предварительном варианте, **не прогноз экономии**:
новые leaves/consumers/controls тоже стоят время, их новых замеров нет. На новом pin всё может измениться.
Таблица по классам с VT: `coverage-classes.tsv`.

## Конкретные возможные замены

| Old family (точные строки в TSV) | Count | Future theorem ID (логический placeholder) | Что нужно сохранить/доказать |
|---|---:|---|---|
| `network::network_correctness_u8_*` | 10 | S4/unstable-u8/network-classes | N{0,1,2},{3,4},5,6,7,9,10,11,12,13; actual unstable entry; ordinary byte `<`; sortedness, count при N<9, normal return, movement и length-edge covers |
| `types::sorted_permutation_traits_*cell_u8*` | 4 | S4/Cell-u8/stable+unstable-default/fallback0..16 | именно Cell<u8>, logical_less equivalent KeyLess, stable и unstable branches, N0/1/2/7/8, count и meaningful input/return covers |
| `network::swap_contract_u8_{n2,n9,n13,indices_n17}` | 4 | S3/swap/u8/full-order/offset-domain | backing2/9/13/17, обе ориентации и все заявленные distinct indices, outside-pair frame; старые PFC относятся к профилю+canonical guard, поэтому нужен явный migration review, а не PASS leaf с похожим именем |
| `fixed_inputs::sorted_permutation_swap_u8_n2` | 1 | S3/swap/u8/full-order/backing2 | exact two-value disjunction, actual body, both comparison outcomes; связанный mutant negative остаётся |
| `fixed_inputs::sorted_permutation_insert_tail_u8_n2` | 1 | S3/insert_tail/u8/full-order/relative16 | relative tail1, backing2, singleton-prefix precondition, exact permutation, return witness |
| `fixed_inputs::sorted_network_prefix_u8_n10` | 1 | S4/unstable-u8/network9..12 | old concrete endpoint assertion выводится из full count+order; достижимость этого входа и actual entry binding |

Даже эти21 остаются в ordinary, пока нет qualified new root/contract/source pin, matching
T/F/domain/property/geometry и review caller preconditions. F pointers/KeyLess имеют разные types:
эквивалентность comparison semantics и миграция контракта не подразумеваются.
При более узком backing/offset/frame/N нового листа кандидат возвращается в RETAIN.
Старые покрытые N перечислены явно; будущие symbolic classes должны включать все эти N,
но ещё доказать весь собственный claimed range, включая отсутствующий в old suite N8/другие края.

## Что сохраняется и почему

- **32 tied-key entry roots** (25+7), три N2 forwarding profiles и старые LtU8/LtU64/LtI32
  profile instances: `x>>1` допускает разные full values с равными ключами. Сортировка полным
  `<` не доказывает прежний tie/payload oracle. Нужны P-specific static adapters/qualification
  или отдельное решение владельца о scope, не молчаливый opt-in.
- **92 safety roots**: в частности u64 N1..20 все offsets, `Cell<TaggedKey>` с записью keys,
  массивы16/17/85/86, network::DropValue, WrappedU64, ZST(), minimal u64 scratch18 при N2,
  noncopy bytes86 fallback и threshold/reachability witnesses. Lawful KeyLess и u8 theorem
  этих domains не покрывают. Relative16 не поглощает insertionN17..20; offset0/separate-array
  proof не поглощает interior-base/same-allocation proof.
- **19 drop/tag roots**:13 merge drop-count/tag,3 mutating-route tag-count,
  2 arbitrary-comparator network tag permutations и1 type/source-route predicate.
  Count/order полного byte не теорема о destructors, IDs или callback writes.
- **20 actual-helper roots** =16 PFC+4 verified-stub consumers. Сохраняются arbitrary-answer
  comparator и пары одинаковых T/F/allocation на backing4/9/13/32, u64 insertion backing5/17,
  insertion len2/3, separate sort4/merge2/4 и scratch48 merge8 src32→dst0.
  Single successful PFC не квалифицирует иной consumer/domain.
- **Profile36** включает swap14,sort4×2,insert_tail×5,merge×12,forward×3.
  Четыре strict-u8 swap candidates выше оставляют32 профильных roots.
  `[u8;16/17]` с byte0 order, `Cell<i32>`, DropValue, u64/i32, LtU8 и scratch48
  остаются со своими model/canonical guard/geometry, независимо от нового u8 proof.
- **Остальные6 helper roots**: merge_up pointer advancement, arbitrary-answer merge4 count,
  sort4 arbitrary-comparator u64/bytes16, same-position swap и efficient-swap type matrix.
  Новый merge sorted/count не подразумевает exact merge_up frontier advancement;
  leaf с requires distinct indices не покрывает equal-position case.
- Четыре array fixtures из #752 сохраняют **#5104 caveat**: swap bytes16/17,
  sort4_contract_bytes16 и sort4_arbitrary_comparator_bytes16. Эти строки не превращены в
  бесспорный theorem и не поглощены scalar proof.

## Служебные ворота inventory

13 cfg-only negative controls находятся **вне235** и не удаляются ради бюджета.
[Source controls report](https://github.com/Tiramisu-Cake/verify-rust-std/blob/fc72b711781e2c0effb3fc1d33dfad55785bd5b2/research/challenge-8/kani-k1/en/negative-controls.md)
остаётся историческим claim; этот пакет controls не запускал. Новые S controls учитываются отдельно.
71 ordinary root содержит panic stub (поле `panic_stub`); остальные164 не заменяют его.
Это не общий no-panic theorem: будущий S sorting path обязан работать без panic stub.

В TSV `domain_fixture` — идентификатор точной fixture, **не самодостаточная формула requires**.
`source`/`source_url` указывают её единственное определение/макровызов на exact old SHA;
geometry authority включает вызываемые helper/macro и profiles, не только имя root.
Перед утверждением любой строки replacement нужно развернуть эти requires, initialized ranges,
active slice/backing/offset/topology, frame, snapshot/probe и callback effects, вписать exact
new root/body/domain/contract version, control receipts и reviewer identity.
Числа235/183/52 — inventory source claims; они не устанавливают AST/MIR/PFC binding новых proofs.
