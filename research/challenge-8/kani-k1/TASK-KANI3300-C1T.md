# KANI3300 C1-T — шесть promoted expected-тестов, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна test-only стадия, **Cloud $0**, без запусков.
M0 принят. Отдельный compile-only CI/runner C1-L **отменён координатором**; результаты a8f6b7196a сохранить исторически,
его adapter/runner не реализовывать. Проверка — существующий Uninit Quick координатора сначала на baseline tests, затем M1.
Это верификация корректности, не security-работа.

## Вход и изоляция

Прочитать `kani3300/c1p/HANDOFF-M0.md`, шесть `promoted_*.rs` @ **d8d3e6d4ca**, контракт M0 @ **742c77fa03** и
`TASK-KANI3300-M1.md`. Source `/root/kani-fix-3300-p1b1` @ **6134e42dd1c65dc980336e7d9455aba02d423edf** — read-only.
Создать отдельный clone **/root/kani-fix-3300-c1t**, ветку **tests/kani-3300-promoted-controls** от этого exact base.
Если destination/ветка уже существуют в другом состоянии — STOP без reset/stash. Production/pins не менять.

## Что сделать

1. Оформить ровно 6 drafts как обычные per-selector expected inputs в
   **tests/expected/uninit/promoted-allocations/**: `direct-legal.rs`, `direct-left-hole.rs`, `direct-right-hole.rs`,
   `helper-legal.rs`, `helper-left-hole.rs`, `helper-right-hole.rs` и соответствующие `.expected`.
   Один harness на input; сохранить исходную задачу/идентичность operands и helper boundary, не добавлять tests D0/flat-copy сюда.
   Нейтральные названия/комментарии/license header; compile-flags edition2021/-D warnings, kani-flags uninit-checks/regular
   по существующему raw-eq-uninit. Удалить misleading draft/proposed flag comments при активации.
2. **Goldens по семантике исправленной модели**, одинаковые для baseline/M1:
   legal — SUCCESS + equality true, оба raw_eq byte checks законны; left/right hole — uninit-read нужного operand,
   не ранний UB/layout Unsupported. Expected text взять из existing raw-eq-uninit conventions; per-operand property IDs
   и actual lowering не выдумывать. В source/manifest записать требуемый binding, в golden только обоснованный semantic
   verdict/diagnostic и впоследствии наблюдённые детали. Не принимать baseline false failure как новый желаемый legal golden.
3. On baseline legal могут ложно упасть; holes уже могут иметь FAILURE. **Ни общий FAIL, ни substring golden не доказывает
   intended side**: другой fully initialized promoted operand на старой модели тоже может ложно падать.
   CI request должен отдельно запросить binding обоих checks и extra failures. Не обещать, что все negative selectors
   baseline пройдут goldens; наблюдённый результат сохранить, goldens corrected-model не ослаблять под лишние failures.
4. References к `[MaybeUninit<u8>;3]` должны быть валидны до raw_eq; hole — actual uninitialized byte, без writes в immutable
   constant storage и без manufactured prior UB. Retained raw_eq, promoted GlobalAlloc/Some-None mask и helper argument
   пока NOT_RUN; source spelling не доказывает их. Some(0)/None/coalescing не выводить из GOTO zero initializer.
5. Минимальные compile/format правки допустимы, source semantics не менять ради ожидаемого вывода. `DRAFT-PORT-MAP.json`:
   original draft/hash → active source/harness/hash/golden и каждое изменение с причиной. Если source не даёт требуемое
   promotion/retained read, записать mismatch и proposed repair отдельно; не объявлять незапущенный контроль bound.
6. `CI-REQUEST.md`: 6 новых selectors на baseline+C1-T и затем **тех же files** на M1, без нового framework/workflow.
   При необходимости coordinator добавляет --emit=mir в существующий Quick и targeted property inspection; field/IDs
   в goldens уточняются только по фактическим наблюдениям. Setup/compiler/solver/harness/golden status различать.
   Baseline known failures — repro, не whole-Quick PASS; M1 требует legal SUCCESS и корректного reached hole failure,
   без лишних новых safety/Unsupported failures. Не запускать CI и не ждать его в этой сессии.

## Проверки, коммит и handoff M1

Статика: git diff --check, imports/unused/-D warnings source audit, разрешённая rustfmt-обёртка
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --config-path rustfmt.toml`.
Один bounded Luna High review test contracts/false-positive masking/manifest, без повторного production review и вложенной делегации.
Компиляция, MIR/runtime binding и результаты новых inputs — NOT_RUN; CI не выполнялся этой стадией.

**Один локальный test-only commit** поверх base, author/committer **Tiramisu-Cake <igkharin@gmail.com>**, нейтральное сообщение
без [skip ci]. Diff ограничен 6 source/6 expected в указанном новом path; не менять production/существующие controls.
Kani **не пушить**. Передать exact commit/hash/path inventory для неизменённого переноса в M1; model owner не редактирует
эти fixtures параллельно. Review/CI findings по ним возвращаются этому владельцу через координатора.

В g0 `research/challenge-8/kani-k1/kani3300/c1t/`: `NOTES.md` (≤25 строк), `DRAFT-PORT-MAP.json`,
`TEST-MANIFEST.json`, `CI-REQUEST.md`, `REVIEW.md`, `RESULT-KANI3300-C1T.md` (≤15 строк). Записать full base/test SHA/tree,
semantic expected отдельно от NOT_RUN observed, ограничения operand binding и handoff воркеру 14.
Research commit [skip ci], тот же author/committer, stage только kani3300/c1t/, push g0 без force;
concurrent/non-fast-forward — handoff без reset/stash/force/чужих m1/c1l файлов.
Никаких локальных cargo/rustc/Kani/CBMC/Miri/сборок, Actions/Cloud dispatch, runner/workflow/adapter edits,
raw logs/archives/credentials, PR/issue/комментариев и сторонних PR links. D0/C1-L historical inputs не переписывать.
После пакета STOP. Последняя строка: `READY <sha локального test-only Kani-коммита>`.
