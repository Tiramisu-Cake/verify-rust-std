# Координатор → U3: дополнение по итогам U1T (до GO на сборку)

U1T (`/root/verify-rust-std-kani3300-u1t` @ 51971120af, build ff0988c7): 7/12 PASS, 5 ERROR. Координатор прочитал
bounded summary.json (output_excerpt, поля errors/diagnostic) для offsets 0,1,2,3,5:
- Все пять — Kani **VERIFICATION FAILED** («0 successfully verified harnesses, N failures»); compiletest:
  «expected output to contain the line(s)» → **несовпадение golden**, а не SUCCESS.
- Причина формата: goldens требуют `<harness>.safety_check.\` + Status/Description, но чтение происходит внутри
  `MaybeUninit::assume_init` (core), и property называется по этой функции. Проходящие U1-тесты с `assume_init`
  (`maybe-uninit-assume-init`, `scratch-array-unwritten`) используют форму
  `Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `T``.
- Но это **не доказывает**, что упал именно uninit-check: при `--output-format=regular` описание присутствует и у
  SUCCESS-проверок. Дополнительно:
  - overwrite-copy: в выводе «unsupported constructs … foreign function (1)» — выяснить, какой;
  - **overlap-copy: обе harness содержат `Description: "internal error: entered unreachable code"`** — источник неизвестен
    (std? `unreachable!()` в патченном `library/kani_core/src/mem_init.rs` или в инструментировании для `ptr::copy`
    с перекрытием?). Позитивные парные harness (`overlap_copy_*_written_slot`) прошли 7/7.

Что сделать в U3 (до PRE-BUILD нового SHA):
1. Пять goldens U1T-negative (`maybe-uninit-review-{overwrite-copy,overlap-copy,repeat-local,reset-zst,argument-return}`)
   перевести на форму `Failed Checks: <uninit description>` + `VERIFICATION:- FAILED` + `Complete - …` (для overlap — две
   harness: `Checking harness …` + `Failed Checks:` для каждой, как в `scratch-array-unwritten`). Ожидания (тип T) не менять.
2. Включить **все пять** в manifest U3 (вместе с review-positive), ужав прочее до ≤ 20; убранное — NOT_RUN с перечнем.
3. Статически найти источник «entered unreachable code» в overlap-copy (файл:строка). Если это код патча (mem_init /
   check_uninit) — исправить в v2 и добавить положительный overlap-тест, который не должен давать этот отказ; если std —
   описать. Если источник установить нельзя — `Координатор, вопрос`.
4. Аналогично указать, какой «foreign function» в overwrite-copy (вероятно, недостижим — объяснить).
Затем обновить пакет и выдать новый `PRE-BUILD REVIEW <sha>`. Пакет 52cd0b1235 не диспатчить.
