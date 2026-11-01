# DOMFIVE — реестр доменов контрактов на Part 1 v5

Ветка `experiment/kani-k1-domfive-20261102`; источник кода `5a3009b065` (library tree `cbe69760c8`, = HEAD).
Основа — DOMAINS-v4 и `domains/` ревизии `790458b54e`. Сборок, Kani, CI не было; только Python/Git.

Перенесено: паспорта 10 tags, сводки 4 profile-контрактов, все 22 записи target × tag × domain
(swap 11, sort4 2, insertion 2, merge 4, wrappers 3), раздел requires vs executed domain, opt-in harnesses,
«Not established» = v4 «Нельзя» 6–12 и раздел совместимости (Sort4ReadU64 ≠ LtU64, нет ordinary verified stubs,
model-trust open для трёх array PFC со ссылкой на Kani #5104).
Результат: `SMALLSORT-CONTRACT-DOMAINS.md` (англ., 208 строк, 155 ссылок на `5a3009b065`), `domains/pfc-inventory.tsv`
(37 строк), `domains/check_domains.py`, `domains/README.md`. Внутренние коды S01/Q01/M01… заменены на ключи вида
`merge_profile × LtU8 × exact→exact`. Статус только «SUCCESS in the organizer CI run of 5a3009b065: `<V5-KANI-RUN>`».

Отличия от v4 (верен источник v5):
1. Все ссылки пересчитаны. `specfix.rs` строки 1–333, `wrap.rs`, `smallsort.rs` не сдвинулись; `specfix.rs` после
   333 −2; `network.rs`/`merge.rs` сдвинуты удалениями (напр. PFC-атрибуты swap macro 1144→1133, sort4 279→218,
   merge 684/712→542/570, scratch48 1088→899, insert_tail macro 1390→1339, `contract_insert_tail_u8_prefix` 1424→1373).
2. Лексических PFC sites 37→18, inventory 109→37: 72 `cfg(any())` PFC удалены (нет ни в исходниках, ни в G2 382);
   `correct.rs` и PFC `specdiag` удалены. Строки v4 о retired/`cfg(any())`/NOT_RUN/исторических TIMEOUT не переносились.
3. v4: «остальные `stub_verified` — у отключённых raw consumers». В v5 других нет: только 4 под controls (specfix 501/511/524/536).
4. Ряд ссылок v4 указывал на doc-комментарий; теперь на строку item (`sort4_read_lt_*` 73/79→74/80,
   `merge_length_body` 157→148, wrap `Model` 18→19, `sorted` 83→84, `DropValue` 414→405, frame-хелпер →1306).
5. Семантических расхождений между записями v4 и кодом v5 для 35 PFC не найдено (fixtures, N, offsets, probe,
   unwind/solver, frame-assert, routes перепроверены вручную).

Вывод `python3 research/challenge-8/kani-k1/domains/check_domains.py`:
`OK: 5a3009b065 library cbe69760c8; 37 PFC entries / 18 lexical sites; 35 ordinary + 2 controls + 0 cfg(any()); 72 v4-retired absent; G1 200 / G2 382 membership; 22 domains; 155 source links (44 harness-name links)`
Негативные пробы скрипта (подмена номера строки/ссылки на соседний harness) дают AssertionError.

Не проверено мной: сам v5 Kani run (плейсхолдер); описание Kani #5104 взято из черновика PR.
