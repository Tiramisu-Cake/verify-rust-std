# Десять removed cases G1R5

Источник: Kani `5b2265c41..8639a651f`, `tests/expected/uninit/g1-union-pointee-negative/main.rs`.
Имена сохранены в `probes/src/bin/`; чтение заменено на четыре volatile byte reads через заранее взятый raw pointer.
`ожидали` ниже — историческое намерение negative fixture, **не установленный результат Rust/Miri**.

| Имя | Исходная форма | Что ожидали |
| --- | --- | --- |
| whole_move_source_uninit_c | `let _dst = src` для non-Copy `MoveC`; затем `(*p).wide` | uninit FAILURE источника |
| whole_move_source_uninit_rust | то же, `MoveR` | uninit FAILURE источника |
| argument_move_source_uninit_c | `consume_move_c(src)`, inline(never), затем `(*p).wide` | uninit FAILURE источника |
| argument_move_source_uninit_rust | то же, `consume_move_rust(src)` | uninit FAILURE источника |
| field_move_constructor_source_uninit_c | `ManuallyDrop<NonCopyWord>` → `NonCopyFieldC { value: source }`; intrinsic forget union; `*source_word` | uninit FAILURE source |
| field_move_constructor_source_uninit_rust | то же, `NonCopyFieldR` | uninit FAILURE source |
| field_move_projection_source_uninit_c | `(*union_ptr).value = source`; intrinsic forget union; `*source_word` | uninit FAILURE source |
| field_move_projection_source_uninit_rust | то же, `NonCopyFieldR` | uninit FAILURE source |
| intrinsic_forget_move_source_uninit_c | `intrinsics::forget(src)` для `MoveC`; затем `(*p).wide` | uninit FAILURE источника |
| intrinsic_forget_move_source_uninit_rust | то же, `MoveR` | uninit FAILURE источника |

Все четыре исторических union (`MoveC/MoveR/NonCopyFieldC/NonCopyFieldR`) имеют default repr, несмотря на имена.
Только `NonCopyWord` имеет `repr(C)`. Probes сохраняют эти определения и отсутствие Copy/Drop.
Constructor/projection probes дополнительно наблюдают инициализированный destination до forget, чтобы сохранить transfer.
Это восстановленный диагностический материал; старые golden verdicts не переносятся и Kani не изменяется.
