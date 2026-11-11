# KANI3300 G1R6 — CBMC abort от ZST-array arm, семантика padding-фикстур, forget-фикстура

**Выдано координатором 2026-11-11.** Runtime **Codex**, одна стадия, **Cloud $0** (проверка — fork CI координатором).
`TASK-KANI3300-G1.md`, правки планера, G1R…G1R5 в силе.

## Факт: CI-бисекция (fork run 43080841548, CI-only тест `g1-ci-padding-bisect`, только в ветке `kani-3300-g1-ci`)

Harness: `#[repr(C)] union U_x { z: (), padded: ManuallyDrop<Padded>, <один доп. arm> }`; `write_bytes(src, 0x5a)`;
`ptr::write(&mut dst, ptr::read(&src))`; чтение байта перед `word` (padding Padded, offset 1..3) через `*const U_x`.

| доп. arm | итог |
|---|---|
| — (base), `narrow: u8`, `tuple: ManuallyDrop<(u8,u32)>`, `padded_pair: [ManuallyDrop<Padded>;2]` | FAILURE uninit (ожидаемо) |
| `wide: u32`, `pair: [u16;2]`, `ptr: *mut u32`, `fat: *const [u8]` | SUCCESS |
| **`zst_array: [(); 2]`** | **CBMC failed with status 134** |
| все arms negative-фикстуры | CBMC 134 |

На каждом FAILURE две проверки в одной точке (`*padding`): «pointer of type `*const u8`» и «… of type `u8`» — ок.

## Что сделать

1. **CBMC 134 (production):** найти, как G1 обрабатывает arm `[(); 2]` (ZST-элемент, массив нулевого размера) в
   transfer mask / layout / shadow copy — вероятно goto-выражение с нулевым размером/делением на размер элемента/
   byte_extract нулевой ширины. Исправить в production; добавить фокусный regression-харнесс (union с `[(); N]` arm +
   typed transfer) в подходящую фикстуру (negative, если читается padding вне покрытия; иначе positive).
2. **Семантика padding-фикстур:** SUCCESS при `wide/pair/ptr/fat` корректен — байты, покрытые данными любого поля union,
   сохраняются при typed copy (как в Miri; проверь и сошлись в NOTES на реализацию transfer mask). Значит negative-харнессы
   `padded_typed_transfer_padding_*` и `padded_argument_return_padding_*` на полном `CU/RU` ожидают неверное. Перевести их
   на отдельный union без arms, покрывающих padding (напр. `{z, narrow, padded, tuple, padded_pair}`), ожидание FAILURE
   сохранить; добавить в positive по одному харнессу «padding покрыт `wide` → SUCCESS» (c и rust). Проверить, нет ли других
   negative-харнессов на полном CU с той же ошибкой ожидания.
3. **`reject_forget_union_array`** (`std::intrinsics::forget([U { wide: 1 }; 1])` → SUCCESS, guard не срабатывает):
   операции над storage нет, SUCCESS корректен. Переделать фикстуру так, чтобы by-value контейнер с union реально
   инструментировался (напр. чтение/передача массива через raw pointer или typed copy), и guard `UnionAsField` срабатывал с
   прежним reason; если такого пути нет — удалить фикстуру и обосновать в NOTES.
4. Статика: rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`
   `--config-path rustfmt.toml` (все .rs), `git diff --check`, `-D warnings`, сигнатуры stable_mir. Независимое ревью.
5. Сообщения новых Kani-коммитов — нейтральные, как для upstream (без «coordinator», «per decision» и т.п.).

## Результат

`kani3300/g1r6/NOTES.md` (≤ 30 строк) + `RESULT-KANI3300-G1R6.md` (≤ 20 строк). Коммиты в `/root/kani-fix-3300-g1`
(автор Tiramisu-Cake через `-c`, не пушить; production и тесты отдельно). Research-коммит `[skip ci]`, push без force.
Последней строкой `G1R6 READY <sha последнего коммита Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
