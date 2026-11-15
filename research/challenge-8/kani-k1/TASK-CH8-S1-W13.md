# CH8 S1 — worker13: реальные trait contracts и smoke шести тел

2026-11-16. Одна интеграционная сессия после handoff11; до него допустим static design без чужих edits.
P0 принят: domain16/32, std#752, clean upstream Kani, единый budget≤32. Это задание готовит пакет,
не запускает CI. Это верификация корректности, не security-работа.

## 1. Входы, рабочие пути и запреты

Прочитать root/project AGENTS, `PLAN-CH8-ITEM2-SORTING-v2.md` §§2–4,
`ROADMAP-CH8-ITEMS1-2-FOUR-WORKERS.md`, `TASK-CH8-S1-W11.md`, `CH8-DISPATCH-LEDGER.md`.
Точные входы:

- std **`872d5a43380752786415bc00d2a12ce0e930cb37`**, tree **`384023c2f80a04d0618aa7ce971b1419494b062b`**;
- Kani **`0aac16ef62da9e9d5645782d458593e5d78143ba`**, tree **`9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`**.
  Source ancestry содержит `063204a177272585352b6942ae2b04709fe58b48` и
  `f046b70644e113be0df9c22c2e6ea44a65a57566`; это stock upstream, **без C2/SEL1**.

Создать только worktrees, используя уже существующие object stores:

```sh
git -C /root/verify-rust-std worktree add -b work/ch8-s1-integrate-w13 /root/verify-rust-std-ch8-s1-w13 872d5a43380752786415bc00d2a12ce0e930cb37
git -C /root/kani-fix-3300-c2-s6 worktree add --detach /root/kani-upstream-ch8-s1 0aac16ef62da9e9d5645782d458593e5d78143ba
```

Worker13 единственный создаёт общий read-only Kani worktree; worker11 его не меняет. До создания проверить
object/tree, `worktree list`, disk, отсутствие destination/branch. При занятом пути сверить владельца,
exact identity и чистоту, иначе STOP; не reset/clean/stash/prune чужие области. Не удалять чужие файлы
ради места. Полные clones/копии target/.git запрещены. Отдельные CI/build output dirs появляются только
на runner, не в shared source trees. Не переключать существующий std/Kani clone ради проверки.

Локальные cargo/rustc/Kani/CBMC/Miri/build/rustfmt/setup запрещены. Только source/Git/небольшие synthetic
проверки runner/manifest без verifier. Push/remote branches/non-skip trigger/dispatch — координатор;
публикации — владелец. Только fork CI, Cloud $0. Никакого нового compiler/runtime patch.

## 2. Владение и интерфейс с11/14

Worker13 — **единственный** писатель `library/core/src/slice/sort/shared/smallsort.rs` во всём S.
Разрешены его verification attrs/plumbing; `smallsort/verify.rs` registration/doc актуального S;
минимальные cfg feature gates в `library/core/src/lib.rs` и check-cfg в `library/core/Cargo.toml`;
точный pin в `tool_config/kani-version.toml`; два новых файла в `smallsort/verify/`:
**`sorting_entry_smoke.rs`**, **`sorting_entry_controls.rs`**.
Не менять runtime алгоритм, trait signatures/bounds, thresholds, существующие helper contracts/profiles/roots.

Worker11 владеет только новыми `sorting_model.rs` и `sorting_model_controls.rs`.
Получить его committed SHA/patch+hash и `kani3300/ch8-s1/w11/INTERFACE.md`; проверить только разрешённый
diff, интегрировать commit в свою ветку последовательно. При исправлениях model API вернуть11 конкретное
замечание; не переписывать его файлы самому. Зафиксировать принятое API в
`kani3300/ch8-s1/integration/INTERFACE-ACCEPTED.md`, не менять его молча после freeze.

Контракт фасада: generic read-free inactive fallback для любых T/F; точные три пары KeyLess с u8,
Cell<u8>, transparent Freeze NonCopyByte; `enabled`, immutable `Snapshot` CAP32, `snapshot`, `post`.
Для active=true post требует len+sortedness+полные кратности, invalid snapshot → false. Default
modeled=false раскрывается как граница, не generic theorem. Copy нужен key/snapshot, не T.
Если макросам не подходит shared-slice capture, согласовать raw adapter с теми же условиями.

Research scope13: **`research/challenge-8/kani-k1/kani3300/ch8-s1/integration/`**.
Worker14 позже ведёт независимый CI/cost inventory и review receipts; в его W0-U/pr-texts не писать.
CI-only patch/scripts/manifest хранить внутри integration/ci/; удалять обычные workflows только в
CI-only overlay, никогда в std export или чистом Kani source. Один production/model export SHA и
отдельный CI-control SHA, без вложенного Cargo workspace.

## 3. Actual contracts на шести implementation bodies

Включать S1 attrs/modules под **`cfg(all(kani, kani_smallsort_sorting))`**; добавить новый cfg в check-cfg.
Negatives дополнительно требуют existing `kani_smallsort_controls`; ordinary #752 roots и их guards
не заменять S controls. Модель должна быть доступна attrs в core. `unboxed_closures` уже есть в baseline;
добавлять, например, `fn_traits` только если source inspection показал необходимость, под kani gate.
Не вводить новый runtime bound ради именованного Fn type.

На каждом методе — `requires` с **полностью квалифицированным порогом именно его trait**:

| Body | Trait в requires | PFC instance S1 |
|---|---|---|
| Stable default `impl<T>` | `<T as StableSmallSortTypeImpl>::small_sort_threshold()` | Cell<u8> |
| Stable Freeze override | тот же Stable trait | u8 |
| Unstable default `impl<T>` | `<T as UnstableSmallSortTypeImpl>::small_sort_threshold()` | Cell<u8> |
| Unstable Freeze forwarding | тот же Unstable trait | u8 |
| UnstableFreeze default | `<T as UnstableSmallSortFreezeTypeImpl>::small_sort_threshold()` | NonCopyByte |
| UnstableFreeze Copy override | тот же UnstableFreeze trait | u8 |

`requires(v.len() <= ...threshold())` единообразен; не заменить на<=3 и не оставить лишь на wrapper/trait
declaration. Для stable scratch определить реальный минимальный clause: general при len>=2 требует
scratch.len()>=len+16; fallback игнорирует scratch, general при len0/1 возвращается до чтения scratch.
Допустим общий консервативный clause, если точное ограничение и исключённая геометрия явно записаны,
но не требовать initialized T в MU scratch. Не объявлять доказанными arbitrary scratch lengths/offsets
после фиксированного backing smoke. Все ссылочные args корректны/exclusive по fixtures, raw adapters
добавляют явно обоснованные geometry predicates, не предположения о результате.

На каждом из шести **реальных** methods — semantic ensures: при modeled=true output отсортирован
по pure key, имеет ту же длину и full-value multiset относительно **value snapshot до вызова**.
Snapshot сохранять через корректное `old(snapshot(...))`, не `old(&v)`; checker не вызывает FnMut.
Inactive F/T не превращать в runtime requires(enabled) для всех пользователей метода. Формулировать
условный model claim и явно ограничивать его известными парами в документации/инвентаре.

Если для PFC требуются modifies, писать только обоснованные frames конкретного KeyLess-домена
(active v, допустимый stable scratch, comparator ZST). Не заявлять полный frame произвольного FnMut
с внешними записями. S1 **не** использует новые контракты как `stub_verified` и не квалифицирует Replace;
потребители появятся после полной проверки domain/frames, не по одному smoke.
`panic_on_ord_violation`, entry/helper bodies и comparator **не stub**: lawful order должен дойти до
нормального возврата сам. No assume(false), trusted summaries, pre-sorted input или отключения checks.

## 4. Smoke и доказательство активации

Подготовить **шесть отдельных `proof_for_contract` roots**, каждый с actual target из таблицы.
Внутри одного root symbolic initialized backing3 и arbitrary N под0<=N<=3; covers для каждого N0/1/2/3.
Если macro/tool target требует splitting N, обосновать и обновить inventory без расширения домена/caps.
Stable scratch — отдельная flat MU allocation с достаточным активным prefix, не initialized snapshot scratch.
Для default Cell показать empty scratch; для Freeze len0/1 тоже проверить допустимый empty scratch,
len2/3 — достаточный prefix. Отдельные fixtures либо symbolic legal length с явными covers.
Input байты независимы; Cell/NonCopy конструировать поэлементно, не добавляя ненужный unsupported constructor.

Каждый root перед вызовом assert model enabled=true; actual PFC означает проверку его требует/ensures,
не только caller assertions. После возврата — независимый snapshot/checker assertion, useful return,
N0/1 unchanged-value checks, N2/3 reversed/duplicate/ascending return covers. Сохранить canaries вокруг
active span и не читать unused MU. Проверить source predicates выбора типа/ветви: Cell !Freeze,
NonCopyByte Freeze !Copy size1, u8 Freeze+Copy efficient swap; threshold фактически16/32.
N0..3 проходят шесть impl, **не все внутренние branches**: network merge N>=18 и general sort4/8 позже.

В CONTROL-MAP отдельно:

- worker11 model/activation/order/count/invalid-snapshot controls и их legal companions;
- **два диагностических activation variants** (default method и specialized override): условный
  postcondition в test-only overlay заведомо false при enabled=true; соответствующий PFC должен
  получить именно contract postcondition failure. Это проверяет attachment real method и выбор тела,
  а не только дополнительный caller assert. Сначала design/static review, затем в том же bounded CI.
  Variants изолированы от export и друг от друга, не меняют алгоритм и не публикуются;
- positive/negative oracle на каждый exact selector: failed properties, useful successes/covers, phase,
  original exit/signal, no incomplete inventory. Нельзя заранее выдумать property IDs/counts до CI.

`--no-assert-contracts` сохраняется у положительного organizer-profile PFC; не убрать его, чтобы
выглядеть успешным. Проверить, что PFC реально активирует ensures и при нём. При необходимости
диагностические macro/activation modes отдельно назвать; они не заменяют positive profile.
False guard/ранний abort/недостигнутый postcondition — STOP, не VACUOUS PASS.

## 5. Bounded CI-REQUEST: 1 обязательный +1 условный dispatch S1

Reuse working sibling control/export recipe SEL1-C2 replay, но **все binding/setup/argv/manifest заново**
для std872d+S1 и stock0aac. Старые receipts не свидетельство S. Tool setup из exact0aac, неизменный
backend/toolchain/dependencies; std tool pin изменить ровно на0aac. Не запускать compiletest всего Kani,
full Gate A или новые S2 length32 probes в S1.

- Первый dispatch: ubuntu-24.04, jobs1, max-parallel1; build/list once, шесть positive PFC и компактный
  manifest positives/negatives/activation variants. Включить 1 smoke старого ordinary root как bridge
  нового чистого pin, не весь #752 suite. Зафиксировать полный row inventory до запуска.
- Профиль S: organizer unstable flags из exact scripts, в том числе function-contracts/stubbing,
  `--no-assert-contracts`, object-bits12; **uninit/value checks OFF**, default solver/slicing/checks.
  Записать exact CLI ordering (Kani -Z до backend --cbmc-args), cfg и per-row unwind; проверить loops
  snapshot/count CAP32 и N3, не отключать unwinding assertions.
- **600s/invocation** driver+codegen+backend после setup; RSS aggregate≤6GiB/root, не сумма разновременных
  process peaks. Whole dispatch envelope≤120 runner-min: setup≤30, verifier phase≤75, receipt/upload
  reserve≥15. Fixed row batch/phase cap; превышение → STOP/UNKNOWN для оставшихся строк, не silent skip.
  Если manifest не вмещается, сократить дублирующие diagnostics до dispatch с review, а не caps.
- Capture source/tree/changed-file hashes до/после, actual tool/backend hashes/argv/selected root/mode,
  named failure lists, useful successes, raw RSS KiB (+GiB /1048576), wall/phase, exits/signals/caps.
  Timeout/watchdog убивает process group TERM→KILL; ограниченные outputs с explicit truncation;
  `always()` bounded artifacts/fallback receipt. Setup-only или отсутствующий post/cover → не proof.
- **Второй dispatch** только координатор после review первого: одна адресная fixture/integration/CI
  поправка или минимальный tool-blocker repro. Не второй budget для worker11, не solver sweep,
  новый compiler patch или увеличение cap. Infra failure и rerun также списываются в S1 cap2.

В CI-REQUEST перечислить planned row costs, workflow timeout/matrix и outputs caps из working recipe,
ledger reservation S1-01/(S1-02), literal source/control SHAs и fork-only trigger guard.
Synthetic checks wrapper без toolchain: success/negative, wrong SHA/root/mode/guard, timeout/signal,
missing/oversized output и export drift. Подготовка offline; worker14 review инвентаря не новый dispatch.

## 6. Приёмка, STOP и выход

Приёмка подготовки: разрешённый diff, API принят11/13, шесть real targets+fully-qualified threshold attrs,
pure immutable model, прочитанные types/conversions/borrow lifetimes, frozen input/row manifests,
bounded CI-only пакет, все future outcomes NOT_RUN. Общий research пакет не объявляет P1 пройденным.

P1 после CI координатора: шесть PFC legal SUCCESS со всеми asserted postconditions/useful covers;
enabled=true во всех claimed instances/N; activation variants и semantic negatives DETECTED нужной
проверкой, legal companions SUCCESS, no unexpected failures/Unsupported/caps и bridge не регрессировал.
Это механизм на N0..3, не full threshold proof/∀T/extra-UB evidence/организаторское принятие.

STOP: любой Fn ABI/default-specialization/old snapshot/closure lowering blocker; неверный trait body;
нельзя выразить model без новых runtime bounds; fake enabled/defaultfalse; источник/ref/manifest drift;
unqualified frame/summary; необходимость compiler/runtime/алгоритмической правки; caps/неполный receipt.
Записать узкий repro и решение P1 владельцу. Не переходить к S2/листьям самовольно.

Deliverables в integration/: INPUTS; INTERFACE-ACCEPTED; SIX-BODY-MAP с target/mode/type/N/threshold;
CONTRACT-SCOPE; CONTROL-MAP; TYPE-REVIEW; export source SHA/tree/diff/patch hashes; ci/CI-REQUEST.md/json,
CI-only patch+identities, synthetic VALIDATION; RESULT template NOT_RUN; handoff13→14/координатор.
В общем g0 research worktree commit-окно согласовать с координатором/14/11; stage только integration/,
проверить index и не захватить чужие staged files. При занятом index STOP, без reset чужого.
Source/model commit(s) и research только своих путей `[skip ci]`, author/committer
`Tiramisu-Cake <igkharin@gmail.com>` через per-command `git -c`, без Co-Authored-By. Не push.
Завершить `READY <research-sha> <integrated-std-sha> <ci-package-sha-or-patch-hash>`.
