# B3 D0′ — пиковая память из уже выполненных прогонов (замечание аудитора R2)

2026-11-15, координатор. Новых CI нет; источник — job logs (bounded grep) двух прогонов workflow
«Perf s2n-quic-core memory profile» (одинаковый blob `78097b0ce8`; CBMC peak RSS по goto-файлу — опрос раз в 3 s,
это максимум замеров, не точный пик; сторож убивает `cbmc` при MemAvailable < 1200 MiB).

- v4: [43624196686](https://github.com/Tiramisu-Cake/kani/actions/runs/43624196686), head `a5eaaf2937` (parent `3d9a180938`)
- main: [43624201005](https://github.com/Tiramisu-Cake/kani/actions/runs/43624201005), head `fb1e8aff89` (parent `0aac16ef62`)

## CBMC peak RSS (KB), топ s2n-quic-core

| harness (goto) | v4 | main |
|---|---:|---:|
| `sync::spsc::tests::alloc_test` | 7 521 144 | 7 521 972 |
| `inet::checksum::tests::differential` | 5 360 024 | 5 320 712 |
| `slice::tests::vectored_copy_fuzz_test` | 2 023 760 | 2 024 844 |
| `packet::number::sliding_window::tests::insert_test` | 1 432 620 | 1 433 288 |
| `sync::cursor::tests::oracle_test` | 1 421 992 | 1 422 536 |
| `inet::checksum::tests::u32_u16_differential` | 756 776 | 758 928 |
| `inet::ipv6::tests::header_getter_setter_test` | 558 888 | 559 488 |
| `varint::tests::eight_byte_sequence_test` | 552 872 | 551 740 |
| `varint::tests::round_trip_values_test` | 495 864 | 495 792 |
| `crypto::tls::tests::parse_hello_test` | 276 316 | 413 724 |

Остальные строки топ-15 совпадают в пределах ±3 %. Пики CBMC обоих плеч совпадают в пределах шума опроса
(alloc_test: разница 0.01 %); единственное заметное отличие (parse_hello_test) — малый harness, артефакт 3-секундного опроса.

## alloc_test: внешний kissat и вмешательство сторожа

| | v4 | main |
|---|---|---|
| KISSAT rss до kill CBMC | 3.5 → 6.8 ГБ (9 замеров) | 2.7 → 4.8 ГБ (3 замера) |
| kill CBMC (MemAvailable) | 840 MiB, 18:19:27 | 857 MiB, 18:22:50 |
| KISSAT после kill CBMC | рос до 8.2 ГБ ещё ~18 s (сирота) | не наблюдался |

alloc_test (`kani::solver(kissat)`) одновременно держит CBMC ≈7.5 ГБ и внешний kissat в несколько ГБ: в **обоих**
плечах сумма упирается в 16 ГБ и сторож сработал. Kissat-ряды несопоставимы (сторож прервал плечи в разные моменты),
поэтому оба результата — INCOMPLETE для сравнения пика solver. Подтверждает замечание аудитора: сторож, убивающий
только `cbmc`, оставляет `kissat` сиротой.

Вывод D0′: на стороне CBMC пиковая память v4 и main по s2n-quic-core не различается; о kissat данных для сравнения нет.
Это не заменяет T1 и не устанавливает причину потерь раннера.
