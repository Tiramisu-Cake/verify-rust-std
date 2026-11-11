# KANI5072 Z1 — исправление kani#5072 (ложный dereference failure у `read_volatile` на ZST) и тесты Kani

**Выдано координатором 2026-11-11, в рамках ночного GO владельца (общий бюджет проекта ≤ $6.40), план согласован с
планером.** Research-ветка; цель — узкий патч Kani (production + тесты), пригодный для upstream PR в
model-checking/kani. Публикаций нет. Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime
**Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani5072**, ветка **experiment/kani-k1-kani5072-20261111** от tooling base
  `c98d7cee0d` (KT1: `kani_patch` + kind `kani-tests`, ≤ 20 selectors). Tooling, пин Kani
  `f046b70644e113be0df9c22c2e6ea44a65a57566`, toolchain nightly-2026-10-23 не менять.
- Код Kani — в новом локальном рабочем клоне **/root/kani-fix-5072** ровно на `f046b70644` (локальная ветка, без
  push; remote только официальный для fetch). `/root/kani-src-f046b70644` — read-only эталон. Патч для сборки:
  `research/challenge-8/kani-k1/kani5072/z1/kani-fix.patch` = diff клона от полного `f046b70644`, **включая новые
  файлы** (commit в локальной ветке или `add -N`), SHA-256 в request (`kani_patch`).
- Slug **kani5072**, stage `kani5072-z1`, stable owner **k1-merge**, request `kani5072-z1-*`.
- Свой cap **$0.50**: одна сборка `kind: kani-tests` (work budget ≈ 5 мин + 30 overhead ⇒ резерв ≈ $0.4725; минимум
  K-1 $0.4185). Повтор — только если факт + новый резерв ≤ cap, с новым GO. Окно: main 300 + closeout 30 мин.
- Параллельно идут другие этапы (`/root/verify-rust-std-kani3300*`, `/root/kani-fix-3300`) — не трогать.

## Диагноз (статический, планер; проверь по исходникам)

- `codegen_volatile_load` (`kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs` ≈ :1906) всегда строит
  `src.dereference()`, а соседний volatile store уже обходит dereference для ZST. Для ZST это создаёт реальный доступ
  к памяти → четыре CBMC pointer checks без локации. `ptr::read` для того же ZST проходит.
- Причина выглядит локальной для lowering Kani. Если для фикса понадобится менять CBMC, его версию или общий pointer
  model — **стоп, `Координатор, вопрос`** с причиной и переоценкой scope.

## Семантика — сначала статический gate

1. Сверить контракт `read_volatile` **точного nightly** (`library/core/src/ptr/mod.rs` в этом worktree ≈ :2131) и
   официальные docs: для ZST указатель не обязан быть валидным для доступа, **alignment обязателен**, значение T должно
   быть корректным. Текст issue говорит «non-null»; по текущей документации null для обитаемого aligned ZST допустим —
   **не добавлять** non-null assertion по аналогии с `ptr::read` без подтверждения в этом контракте. Записать
   вывод в PRE-BUILD.
2. Для ZST: не выполнять load; результат — значение ZST (как в store-пути / `ptr::read`). **Alignment-check
   сохранить.** Для необитаемого ZST сохранить диагностику (обход load не должен давать ложный SUCCESS).
3. Non-ZST путь не менять: проверки реальных чтений (bounds, alignment, uninit) должны остаться.
4. Узкий патч: ориентир 1–2 production-файла, 10–60 строк. Стиль Kani, SPDX-заголовки в новых файлах, rustfmt через
   обёртку `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh` с `rustfmt.toml` клона.

## Тесты (manifest ≤ 20 selectors)

Новые (2–4 файла, `--edition 2021`):
- positive (один fixture можно на несколько harness): исходный repro (`read_volatile(&())`), aligned dangling pointer к
  ZST (`NonNull::dangling()`), over-aligned ZST (`#[repr(align(8))] struct Z;`); null ZST — по сверенному контракту
  (positive или negative, с обоснованием); positive — `require_success: true`;
- negative: misaligned over-aligned ZST → конкретная alignment-диагностика в `.expected`; при возможности —
  необитаемый ZST/never-путь, если Kani его диагностирует сейчас.
Регрессия существующих: `Intrinsics/Volatile/load.rs`, `store.rs`, `unaligned.rs` (или как называются в дереве) и
отрицательный unaligned non-ZST load. Negative — `expect: pass`, `require_success: false` + конкретная `diagnostic`.
Golden существующих тестов не переписывать. `fixme_*` — NOT_RUN.

## Приёмка

- PASS: патч применяется к свежему пину (identity дерева = локальный preflight); новые positive — native PASS;
  negative — ожидаемая диагностика из собственного вывода; существующие — штатный результат; нет TIMEOUT/ignored.
  Неожиданный SUCCESS отрицательного теста — блокер корректности.
- Статика: `git apply --check` на свежем пине, rustfmt — ноль diff, diffstat production/tests раздельно, изменений
  вне `kani-compiler/src/codegen_cprover_gotoc/` и `tests/` нет.
- В PRE-BUILD: diff production, полный manifest, вывод по null/alignment, расчёт резерва.

## RESULT

**RESULT-KANI5072-Z1.md**, ≤ 35 строк: identities; причина и фикс (3–5 строк); семантика null/alignment; diffstat;
таблица тестов; расход; различать code-ready патч, проверенный native subset и причину остановки при backend blocker.
Черновик описания upstream PR — `kani5072/z1/UPSTREAM-PR-DRAFT.md`, ≤ 15 строк, по шаблону Kani
(`.github/PULL_REQUEST_TEMPLATE.md`), с «Resolves #5072».

## Коммиты, ожидание, запреты

- Коммиты `[skip ci]`, push без force, глобальный git config не менять, без `git stash`.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO. Ожидание: `k1g.sh watch BUILD`, затем конец хода.
- Evidence — bounded `k1g.sh summary/native`; raw logs, archives, credentials не читать; прямых GCS/storage/download/
  logging нет.
- Никаких локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно. Никаких Actions/PR/issue/комментариев;
  push в model-checking/kani или Tiramisu-Cake/kani запрещён.
- Только наш код и исходники/тесты/документация Kani. Чужие PR verify-rust-std не открывать.

Маркеры `REVIEW REQUEST <sha>` / **KANI5072 Z1 ЗАВЕРШЁН**, одна стадия, затем стоп.
