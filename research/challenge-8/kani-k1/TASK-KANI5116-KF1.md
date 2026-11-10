# KANI5116 KF1 — исправление kani#5116 (contracts на specialization `default fn`) и regression-тесты Kani

**Выдано координатором 2026-11-11, в рамках GO владельца на работу по kani#5116.** Research-ветка; цель — патч Kani
(production fix макросов + тесты), пригодный для последующего upstream PR в model-checking/kani. Публикации в этом
этапе нет. Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani5116**, ветка **experiment/kani-k1-kani5116-20261110**. **Tooling base:
  `383fd7089550aeabac3ad92366cd7c71e2f237ee`** (KT1, принят координатором); tooling, workflows, пин Kani
  `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain nightly-2026-10-23 не менять.
- Редактировать Kani — в отдельном локальном рабочем клоне **/root/kani-fix-5116** ровно на `f046b70644` (локальная
  ветка, без push, без remote кроме официального для fetch). `/root/kani-src-f046b70644` остаётся read-only эталоном.
  Патч для сборки: `research/challenge-8/kani-k1/kani5116/kf1/kani-fix.patch` = diff клона от полного `f046b70644`
  (production + тесты одним файлом, **включая новые .rs и .expected** — после commit в локальной ветке клона либо
  `add -N`; обычный unstaged diff теряет untracked), SHA-256 в request (`kani_patch`). В PRE-BUILD сверить
  применённое дерево, наличие всех manifest fixtures и golden-файлов.
- Slug **kani5116**, stage `kani5116-kf1`, stable owner **k1-merge**, request `kani5116-kf1-*`.
- Свой cap **$1.50**: одна основная сборка `kani-tests` + не более одного repair (компиляция/тест-фикс по
  результатам), если фактический ledger + резерв ≤ cap. Лимиты KT1: ≤ 29 work-минут + 30 overhead (макс. резерв
  $0.7965); резерв repair добавляется к фактическому расходу, не к резерву Build 1. Окно: main 360 + closeout 30 мин; T0 — при GO.
- Параллельно в /root/verify-rust-std-kani-traitpfc идёт другой этап — не трогать.

## Диагноз (из статической оценки, проверь по исходникам)

- `contract_main` (`library/kani_macros/src/sysroot/contracts/mod.rs`) после проверки trait declaration безусловно
  разбирает элемент как `syn::ItemFn`, у которого нет defaultness; `ImplItemFn` её содержит. `ContractConditionsHandler`
  хранит `ItemFn`, `initialize` принимает `&mut ItemFn`, `bootstrap::handle_untouched` печатает `#vis #sig {body}`;
  повторные атрибуты идут через `handle_expanded`.
- Check/replace/assert/recursion/modifies-wrapper — локальные closures внутри метода; им `default` не нужен.
- KT1-калибровка: в compiletest Kani тесты по умолчанию edition 2015; parse-ошибка макроса выдаётся через
  `::core::compile_error!`, который там не резолвится (E0433), плюс knock-on E0046/E0520. Новые fixtures — с
  `// compile-flags: --edition 2021`, как `tests/kani/FunctionContracts/receiver_contracts.rs`.

## Исправление (production)

1. Пронести defaultness через первое расширение и через `handle_expanded` (stacked attributes): адаптер
   представления функции (ItemFn + сохранённый `default`, либо общий enum), keyword восстанавливается **только на
   внешнем методе**. Сигнатуру/тело/атрибуты/where/qualifiers/spans/`inline` не переписывать; не превращать default
   method в окончательную специализацию; contract inheritance не вводить (override без своего контракта не получает
   summary родителя).
2. Узкий патч: ориентир 2–4 файла макросов, 40–120 строк. Если для работы нужен выход за `kani_macros` (resolver,
   kani-compiler) — **стоп и `Координатор, вопрос`**, не расширять scope молча. Никаких изменений dependencies,
   toolchain, CI Kani.
3. Стиль и заголовки — как в Kani (SPDX/copyright в новых файлах), `rustfmt` на изменённых Rust-файлах через обёртку
   `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh` с конфигом Kani (`rustfmt.toml`
   клона), edition по `Cargo.toml` крейта.

## Тесты (в патче; весь manifest ≤ 20 selectors — лимит `validate_native_manifest` KT1, tooling не менять)

Новые (все `--edition 2021`, `-Zfunction-contracts`, при stub — `-Zstubbing`), на `#![feature(min_specialization)]`
blanket `impl<T>` с `default fn` и specializing impl:
- исходный repro #5116 (ensures + modifies на `default fn`) — PFC через неспециализированный `Self` выбирает default:
  PASS; по отдельности `requires`, `ensures`, `modifies` на `default fn`; stacked clauses в двух порядках;
  метод с собственным generic `F: FnMut` (как в kani#4908/#5135); `stub_verified` default-метода в caller;
- override без контракта и default с контрактом: PFC на override не должен получить контракт default (проверить
  ожидаемым поведением/диагностикой, без contract inheritance); плюс положительный specializing override **со своим**
  контрактом и отличимым postcondition;
- метод с собственным `F: FnMut`: и PFC, и `stub_verified`;
- `old`: положительный eager-снимок изменяемого скаляра + отрицательный контроль неверного postcondition;
- отрицательные (`tests/expected/function-contract/…` с `.expected`): ложный `ensures` на `default fn`; нарушение
  `requires` у вызывающего через stub; запись вне `modifies` — для каждого указать ожидаемое свойство/диагностику
  (не общую строку FAILED). Для expected/ui: native PASS, `expect: pass`, `require_success: false` и конкретная
  диагностическая подстрока. `expect: fail` в KF1 не используется: repro #5116 после фикса — обычный kani PASS.
- Положительные случаи можно объединять в одном fixture, чтобы уложиться в лимит selectors.
- Существующие (регрессия, точный обязательный subset в PRE-BUILD, вместе с новыми ≤ 20): kani#5135-регрессия
  `kani/FunctionContracts/generic_trait_specialization.rs`, четыре соседних из KT1, и выбранные fixtures для обычных
  free fn / impl method / trait / `modifies` / `old` / `stub_verified` (назвать какие). Штатно ignored/`fixme_*` и
  файлы без golden (например `expected/modifies/{refcell_fixme,unsafe_rc_fixme}.rs`) в PASS-набор не включать —
  перечислить как NOT_RUN заранее (известное исключение, не удаление упавшего теста). Расширенная матрица — отдельный
  этап.
- Каждый selector — с ожиданием в typed manifest (`expect`, `require_success`, `diagnostic`); положительные expected-
  тесты — `--require-success`. Golden-файлы существующих тестов не переписывать.

## Строки сборки и приёмка

- Build 1: `kind: kani-tests`, `kani_patch` = `kani-fix.patch`, manifest выше. Резерв по формуле runner'а (KT1
  сборки шли ≈ 8–9 мин; Kani ≈ 4.5 мин, compiletest ≈ 16 с) с запасом на число тестов; расчёт — в PRE-BUILD.
- PASS: патч применяется к свежему checkout пина (identity дерева = локальный preflight); все новые положительные —
  native PASS (repro #5116 теперь проходит); все отрицательные — ожидаемые отказы с нужной диагностикой из
  собственного вывода; все существующие regression-тесты — их штатный результат; ни одного TIMEOUT/ignored.
- Любой неожиданный отказ существующего теста — регрессия: классифицировать по excerpt; repair только в рамках
  макро-патча/фикстур, с новым GO. Не ослаблять ожидания и не удалять тесты ради PASS.
- Статика до Build: `git apply --check` на свежем checkout пина, rustfmt — ноль diff на изменённых файлах, diffstat
  патча (production vs tests раздельно), отсутствие изменений вне `library/kani_macros/` и `tests/`.

## RESULT

**RESULT-KANI5116-KF1.md**, ≤ 45 строк: identities (pin, patch SHA-256, дерево после apply, tooling base); diffstat
production/tests; суть исправления (3–5 строк); таблица тестов (новые — все; существующие — сводка pass/fail по
группам с перечислением отказов); время/расход; что не проверено (полный upstream CI, `safety::` атрибуты core,
core-default smoke — KF2); черновик описания для будущего upstream PR Kani (≤ 10 строк, отдельным файлом
`kf1/UPSTREAM-PR-DRAFT.md`, без публикации).

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]`, push без force, глобальный git config не менять, `git stash` не использовать.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native` (как в KT1). Raw logs, archives, credentials не читать; прямых
  GCS/storage/download/logging-команд нет.
- Никаких локальных cargo/rustc/Kani/CBMC; Python-скрипты и rustfmt-обёртка — можно. Никаких Actions/PR/issue/
  комментариев на GitHub, никакого fork Kani, push в model-checking/kani запрещён.
- Только наш код и исходники/тесты/документация Kani на `f046b70644`. Чужие PR verify-rust-std, их ветки и код не
  открывать.

Маркеры `REVIEW REQUEST <sha>` / **KANI5116 KF1 ЗАВЕРШЁН**, одна стадия, затем стоп.
