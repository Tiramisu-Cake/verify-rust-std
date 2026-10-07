# Синхронизация с закреплённым upstream cd371e03

2026-10-08. Разрешённая фаза: Git, анализ исходников и документация. **CI budget = 0**:
сборок, verifier, тестов, research runners и workflow_dispatch в этой фазе нет.
Продолжение исследований отложено; подготовленные ниже задания пока не выполнять.
Git-синхронизация не является миграцией профиля или повторной приёмкой доказательств.

## Исходные точки и отдельные слияния

Первичная сверка: локальные и удалённые HEAD совпали с заданными; все шесть
исходных worktree чистые. Upstream/main на момент сверки равен закреплённому
`cd371e035c7e573760c43bf934d53e8118ee3e7d`; цель не менялась. Активных/queued
исследовательских запусков нет. Read-only fetch не понадобился: закреплённые
Git objects уже доступны. Origin — Tiramisu-Cake/verify-rust-std.

| Новая ветка | Исходный HEAD / первый merge parent | Полученный merge SHA | Merge tree |
| --- | --- | --- | --- |
| [sync/upstream-cd371-main](https://github.com/Tiramisu-Cake/verify-rust-std/tree/sync/upstream-cd371-main) | `196121c11fee754327692a6aae7c97670d809c74` | `8aeec5503ee10dcd2ef494705e0b8b7f69e61d4d` | `f2f264b117cb67c9cda71dfb5a5473deb08d9538` |
| [sync/upstream-cd371-research](https://github.com/Tiramisu-Cake/verify-rust-std/tree/sync/upstream-cd371-research) | `f6c3b3cf561a75e1f5f433087c975fd1690b7e38` | `262951a9496a2df208866fe6dedf85f13d78bf3f` | `c1ea4c3a4f37de52e6612d49e2dee332b9aee99b` |
| [sync/upstream-cd371-merge](https://github.com/Tiramisu-Cake/verify-rust-std/tree/sync/upstream-cd371-merge) | `8444589f486e82f23c910bcc918cee1e4681b7ee` | `343d9111be5533a23db52ed3a37f4a1fa7a58976` | `6118b18dd153d7015b94541530b75445e8e66c27` |

Второй parent каждого merge: `cd371e035c7e573760c43bf934d53e8118ee3e7d`.
Таблица закрепляет чистые merge-коммиты до документационного closeout; последние
HEAD новых веток включают отдельные итоговые documentation commits и приводятся
в итоговом отчёте. Их можно получить через branch ref; они не являются proof SHA.

Worktree: `/dev/shm/c8-sync-main`, `/dev/shm/c8-sync-research`,
`/dev/shm/c8-sync-merge`. Из-за заполненного системного диска они sparse;
полные деревья сохранены в Git. Чистый старый detached worktree
`/tmp/sort4-night-workflow` перенесён с сохранением в
`/dev/shm/c8-preserved-sort4-night-workflow`, Git link восстановлен.
Первую попытку merge Git отверг до изменения истории из-за пустых индексов
`--no-checkout`; после заполнения индексов HEAD все три слияния выполнены штатно.

**Конфликтов нет**; содержательные ours/theirs-разрешения не потребовались.
Каждое слияние: 1520 files, +518755/-135898 строк. Rebase/force-push отсутствуют.
`main`, `challenge-8/research`, `challenge-8/merge` не передвинуты. Networks
`challenge-8/networks` остаётся `a9c8913317cbc6d17a8100a8237d50f2356cb5f3`.
Исследовательские ветки не сливались между собой; наш main не вливался в них.

Отдельный разбор main: относительно std base dd2bbad51eb50fdf9730e14802dcaf8a9290092a
его локальные изменения занимают девять путей: AGENTS, custom research workflow,
runbook/README и пять insertion/smoke файлов. 24 exclusive main-коммита с ручными
workflow selections не входят в историю старых веток агентов. Их история и
собственная версия workflow сохранены только в sync/main; consolidation не делалась.

## Сохранённые доказательства и бюджеты

| Направление | Старое доказательное состояние | Бюджет, без изменения |
| --- | --- | --- |
| Первый агент | S6v4 accepted при своих pins; S7c UNACCEPTED, автономное тело VF0 только на экспериментальном старом профиле | 5306/5400 job seconds, остаток94 |
| Второй агент | G2/A/B и девять условных Rust projections accepted на своих старых SHA/stock26.09; wrapping/composition OPEN | 512/1800, остаток1288 |
| Эта Git-фаза | Никакой новой проверки доказательств | 0 разрешено; фактический расход фиксируется после push |

Старый VF source `809de4596839b739dd999f9e462242c835e3af46`, stock26.09,
nightly-2026-02-05. Все старые источники, профили, patch bytes, annotations,
ожидаемые диагностики и контрольные матрицы сохранены. Ни один proof SHA не
переобозначается как результат нового compiler/std/VF.

Первый агент: S6v4 proof `75681fbc57bda633f59096cdc28f0c1aa61daef8`,
profile `experimental-source-linked-select-pointer-drop-v4`, patchSHA256
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
S7c diagnosis `32d909a7b1015a9417b882676d349bab5c80481f`;
partial acceptance `7185d8bae4a25fa2be278424fa9f5c6a80b93956`;
focused controls `6b63670c21bfa57d2531c4be57ac098df6111c5f`;
classifier processor `7eea51399d570b0eba895605c5d05d0de9cf3ed1` (не proof run).
S7c profile `experimental-manuallydrop-new-cfg-v1`, overlaySHA256
`89b0d80bd1e6382a9bf5be2f1ed208bae6aac5e907a21dd782c4c22307578da7`.
**UNACCEPTED сохраняется:** `mir_cfg_unwind` (partial), `mir_extra_operation`,
`mir_contract`, `method_source_pin`, `glue_source_pin` не завершены.
Actual helper/forget linkage и redirect остаются OPEN/NOT RUN.

Второй агент: G2 `b1ed0c22dafec350a64e83675d55350806d77208`,
A `fc4d03d31f92c6d3f3566b0baa506d0a6dec6805`,
B `4e546ec150cf655681516be727aa1a79f525fc56`;
девять Rust projections `1c318453efa4e3a774b2edd791a5298d76132eb0`;
wrapping support diagnostic `1f2eaaa832a7183180675389979ec15c62a78b5d`.
G2 допускает произвольные нормальные Boolean choices; A добавляет scalar final
guard; B — фиксированный конечный SWO, неизменные keys, sorted halves и faithful
normal answers. Rust projections условны на nonzero stride, pointer/index
associations и stock limits. Это не whole-source refinement, caller resource,
FnMut effects, initialization/ownership/copy или unwind theorem. Wrapping -1,
re-entry, terminal associations и общий actual merge остаются OPEN. ZST
applicability не закрывается nonzero components. Git merge не доказывает actual
helper, merge safety/functionality или Challenge целиком.

## Изменения, влияющие на Challenge 8

Все merged `library` и `verifast-proofs` subtrees побайтно совпадают с upstream
(tree object equality), а исследовательский subtree в каждом чистом merge
побайтно совпадает со своим первым parent. Последующий closeout меняет только
документацию. Новых proof/spec/runtime/tool patch правил здесь нет.

| Область | Полученное изменение и требуемый новый audit |
| --- | --- |
| SmallSort targets/callers | `shared/smallsort.rs`: CopyMarker attribute сменён; raw-parts+deref заменены на `slice::from_raw_parts{,_mut}` в general scratch, network и `sort8_stable`. Тела merge_up/down/bidirectional_merge и расписание compare/copy/cursor сохранены, строки сместились. `sort8_stable` изменил caller expression: его полные bytes не прежние. Full-file certificate старого SmallSort больше не соответствует новым bytes. |
| Stable/unstable routes | stable/mod, drift, stable/quicksort и unstable/mod blobs сохранены относительно8444589f; unstable/quicksort поменял cfg_select formatting. ZST/length guards в stable/mod и unstable/mod сохранены статически. alloc/slice и core/slice получили другие API/body/contracts changes; `slice::swap` теперь делает indexing checks и `swap_unchecked`. Caller audit не является доказательством premises actual helper. |
| ManuallyDrop | `core/src/mem/manually_drop.rs`: MaybeDangling<T> field -> T, новые derives, field initialization/move вместо прежних операций new/into_inner; изменены take/drop и attrs. Старое доверенное correspondence/source certificate не переносится автоматически. |
| MaybeUninit/mem | `assume_init` вместо raw ptr read использует новый `transmute_neo`; новые write_default/array APIs; `mem/mod.rs` содержит transmute_neo/transmute_prefix. Layout/validity, exporter и refiner paths требуют отдельного review; assume_init остаётся вне принятых результатов. |
| Pointer operations | const/mut offset/add/sub получают `byte_offset_does_not_wrap` в source contracts. wrapping_add/sub bodies сохранены, но поддержка stock-VF не доказана. `ptr/mod.rs`: lang item drop_in_place -> drop_glue, read/write_unaligned используют packed helper/transmute; изменились const/size выражения. Typed drop/source admission старого профиля нельзя переpin автоматически. |
| Intrinsics | Декларации/const/clauses/fallback metadata изменились; copy contracts используют const size. Сверить select_unpredictable declaration/body/types и его source/MIR gates отдельно. |
| Rust/tool setup | Root nightly2026-02-05 -> nightly2026-09-25; standard VF scripts26.09 ->26.10. setup-verifast-home добавляет26.09.20 и26.10, Linux26.10 archiveSHA256 `5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd`. Source26.10 `f76012fb518703b1d98e243ac4f487f16877cfcb`. |
| Exporter/translator/spec/refinement | VF не vendored в std Git tree: обновлён standard setup; исследовательские runner pins по-прежнему старые и не мигрированы. Кандидат26.10 меняет schema/clauses/const/assert/alias/closure lowering и specs; assert refinement имеет unwind TODO. У MD::new статически остаётся старое successor mismatch. Нужны согласованные exporter/schema/decoder/translator/refiner binaries и полный effective spec hash. |
| Workflows | Upstream меняет book tools на cargo+stable, Flux pin, Kani orchestration/includes. Standard VF proof flags остались прежними; их allow_assume/ignore_unwind_paths не являются нашей research acceptance. Custom research workflows в каждой ветке сохранены со своими controls/selections и прежними branch routing guards; новые sync ветки не означают готовый новый experiment runner. Никакие настройки/проверки вручную не ослаблялись. |


Observed SmallSort full-file SHA256: old844 `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`;
newcd `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`. Это audit hashes, не обновлённые
admission pins: старый certificate/expected hashes остаются неизменными.

[Исходниковая оценка26.10](https://github.com/Tiramisu-Cake/verify-rust-std/blob/f6c3b3cf561a75e1f5f433087c975fd1690b7e38/research/challenge-8/VERIFAST-26.10-MIGRATION.md)
покрывает exporter/translator/spec/refiner diff по точным VF SHA. Архивная
projection-name canonicalization уже upstream; точные S6v4 rules и S7c CFG
repair upstream не покрыты. Архивные patches не добавляются к active chain.

## Исправление source audit второго агента

Все восемь путей исторической SOURCE-MAP существуют в Git trees8444589f иcd371e03.
Отсутствие в прежнем локальном checkout не означало отсутствия в репозитории.
В sync/merge исправлены POINTER-DESIGN и SOURCE-MAP: прежние external Rust
b6f0945e reference hashes сохранены с верной атрибуцией; добавлены настоящие
844/cd blob hashes и repo-line anchors. Пять из восьми external reference hashes
не совпадают с844, это предшествующее синхронизации расхождение. Не обновлялись
certificates, classifier coordinates или intended predicates ради admission.
Свежая source сверка не превращает старые projection proofs в caller proofs.

## Статические проверки и публикация

- Три merge имеют точные два parents, unresolved index entries отсутствуют;
  merge-conflict markers не внесены. Полные runtime/standard VF tree IDs равны upstream.
- В каждом чистом merge research tree/AGENTS/custom research workflow равны
  исходному parent. Новые docs проверяются отдельно; все patch/proof/runner/
  classifier/source certificate bytes сохраняются.
- YAML всех workflows прочитан как данные. Только manual research triggers.
  Book, Kani, Rust tests, GOTO и VeriFast имеют path-filtered push без ограничения
  sync branches; Flux/RAPx/KMIR push ограничены main. Schedule workflows относятся
  к default branch и этой фазой не меняются. PR/merge_group/review events не
  порождаются: PR и обращения upstream не создаются.
- Full merge diff --check отмечает шесть upstream trailing-whitespace sites:
  stdarch intrinsic-test common/values.rs228/298, x86/mod.rs194 и
  stdarch-gen-arm/spec/sve/aarch64.spec.yml3637/4212/4245. Эти три blobs равны
  upstream; замечания унаследованы и runtime/source bytes не правились.
  diff --check для документационного closeout обязан быть чистым.
- Каждый новый merge и итоговый commit этой фазы имеет `[skip ci]`; публикуются
  только готовые tips. После push сверить remote SHA и связанные Actions runs.
  При неожиданном push CI отменить только runs этих sync веток/SHAs, сохранить
  реальное время jobs. Исходные ветки/budgets не передвигать/сбрасывать.

## Подготовленное задание первому агенту — НЕ ВЫПОЛНЯТЬ в этой фазе

Работать от sync/upstream-cd371-research; сначала оформить отдельную BEFORE card
с новым std/source snapshot, stock VF26.10f76012fb/nightly2026-09-25, archive/
binaries/schema/spec hashes и нормальными/unwind обязательствами. Учитывать
старый остаток94s: не считать эту фазу новым бюджетом; до исполнения нужен
проверенный bound подготовки+проверок+артефактов или отдельное решение о бюджете.

1. Stock baseline на новых зависимостях без экспериментальных rules: независимые
   u32/readonly pointer bodies и минимальный exact generic forget adapter с прежним
   контрактом. Не примешивать отсутствующие S6 custom predicates к stock baseline.
   Разделить setup/export/decode/refinement/full VF outcomes; проверить source
   identity, тело/returns/leak/dead-code и достижимый unwind. Повторять только по
   новой гипотезе; unsupported/setup не является intended negative.
2. По фактическим stock failures и source/MIR audit решить, какие четыре S6
   families действительно необходимы/применимы. Новый источник MD/layout/drop_glue
   требует обоснования; не обновлять source pins механически. Если нужен S7c CFG,
   сначала physical-loc диагноз именно этого остатка; при другой причине объяснить
   её, не применять patch ради PASS. Сохранять exported MIR/common cleanup.
3. Любая адаптация — отдельный named profile/card/review, не расширение semantics
   автоматически. Нужна собственная constructor/as_mut_ptr/intrinsics/drop и
   baseline matrix, обычный/shared unwind, false normal/unwind posts и false-pre
   dead-code controls, включая все пять незавершённых старых admission gates.
   Приёмка требует full VF0 и всех предназначенных negative obligations.

Actual-call linkage/redirect, guard/Drop/assume_init/memory/exporter/refiner/kernel
расширения не разрешены этим подготовленным заданием. Старый S7c UNACCEPTED
сохраняется независимо от нового stock baseline.

## Подготовленное задание второму агенту — НЕ ВЫПОЛНЯТЬ в этой фазе

Работать от sync/upstream-cd371-merge, stock VF26.10/new nightly, с отдельной
BEFORE card и сохранением своего512/1800used1288remaining. Исполнение требует
отдельного возобновления; CI budget нынешней фазы остаётся0.

1. Повторно проверить G2/A/B и девять Rust projections на согласованном новом
   stock наборе. Сохранить их domains/premises/full posts; новая строгая matrix
   проверяет тела, normal/unwind scope, return/leak/dead-code, source integrity,
   export/decode/refinement и предназначенные assertion negatives. Старые numbers/
   SHA/принятие не переименовывать как новые результаты.
2. До расширения модели — два отдельных минимальных generic probes точных
   const-pointer wrapping_sub/add; затем только при поддержке исследовать -1/
   re-entry/end association и intended read-from--1 control. Сверить support stage,
   provenance, modulo-address, limits/specs и реальный intended obligation. Два
   исправленных excluded drafts остаются NOT RUN; ранний setup failure не
   калибрует read detector. Ordinary sub не заменяет wrapping.
3. Если stock support отсутствует или недостаточен, сохранить reproducer и STOP
   с обоснованием отдельного model decision. Новый axiom/spec/tool patch, whole
   merge refinement, копии/ownership/FnMut effects/unwind, ZST bridge не входят
   в автоматическое продолжение. G2/A/B и conditional projections не доказывают
   actual Rust merge/Challenge без оставшихся transfer obligations.
