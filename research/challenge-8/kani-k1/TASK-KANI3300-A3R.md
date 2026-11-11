# KANI3300 A3R — регрессия A3 по узкому fork CI (ремонт, круг 1 из 2)

**Выдано координатором 2026-11-12 (ночь).** `TASK-KANI3300-A3.md` в силе. Runtime **Codex**, одна стадия, **Cloud $0**.
Kani: `/root/kani-fix-3300-a1`, ветка `fix/kani-3300-a1`, HEAD = A2R2 `585c93b2ff` (поверх A3 `0b1d68ac69`).

## Факт: `Uninit Quick`, ветка `uninit-ci/a3-protocol` (A3 `0b1d68ac69`), run 43115476304

Format/build/clippy PASS; kani 22/22; ui/script PASS; **expected: 64 passed, 30 failed** (до A3 на A1 — всё зелёное).
Причины (частоты по логу):
- **65×** `Failed Checks: Kani does not support reasoning about memory initialization of intrinsic
  Unimplemented { name: "integer_max", … }` — A3 направил вызовы интринсиков (по крайней мере `integer_max`; проверь
  остальные) в путь «нет парного протокола → Unsupported» или изменил классификацию интринсиков. Интринсики должны идти
  прежним путём (`Intrinsic::from_instance` / `can_skip_intrinsic` / явные модели), предикат парности — только для
  `InstanceKind::Item`/shim с телом.
- **1× ICE** `rustc_mir_transform/src/validate.rs:261:26: broken MIR in Item(DefId(0:9 ~ mai…` — один из новых custom-MIR
  тестов A3 строит невалидный MIR. Найти и исправить тест (сверить формы `core::intrinsics::mir` с исходником пина).
- Остальные: лишние uninit-чтения (`u8`×9, `u16`×4, `u64`×3, `u32`×2, `*const [u8; 12]`×2, `u128`, `[u8; 4]`, `[u8; 2]`) —
  после исправления интринсиков проверить, не осталось ли регрессий от in-place `Call(Move)`-деинициализации (она должна
  срабатывать **только** при `Call` с `Operand::Move(place)` того же tracked места; temp-moves, assignment — без reset).
Падающие существующие тесты включают: maybe-uninit-transfers, -argument-return, -argument-buffer, -transmute, -initialized,
-overlap-copy, -overwrite-copy, -partial-copy, -repeat-local, -reset-alias, -reset-zst, -contract-clause, -contract-frame,
unions.rs и др. Все они должны вернуться к своим golden **без правок golden**.

## Что сделать

Исправить production (не ослабляя проверки A3), исправить невалидный тест; rustfmt `--config-path rustfmt.toml`,
diff --check, clippy source audit, независимое ревью. Коммиты поверх текущего HEAD, не пушить.

## Результат

`kani3300/a3r/RESULT-KANI3300-A3R.md` (≤ 15 строк), research `[skip ci]`, push без force. Последней строкой
`A3R READY <sha Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
