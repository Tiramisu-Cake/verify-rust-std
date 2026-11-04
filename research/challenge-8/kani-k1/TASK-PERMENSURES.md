# PERMENSURES — перестановка в контракте `swap_if_less` и композиция на длинной сети

**Выдано координатором 2026-11-05 (ночь).** Dispatch только после exact-packet PRE-BUILD review/GO координатора.
Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-permensures**, ветка **experiment/kani-k1-permensures-20261105** от
  **588c002998** (REALCONTRACTSTWO: `requires`/`modifies` на пяти настоящих хелперах).
- Slug **permensures**; stable owner — свободный на момент dispatch. Request_id `permensures-*`.
- Project cap **$118.96**, свой cap **$3.00**. **До двух сборок** (G2 с новым GO). Один compile-error repair на
  сборку. Tooling base: **59893bff1f**.
- Окно: main 240 + closeout 30 мин.

## Контекст

- PERMTAGS (`6542b3c4ba`, ветка `experiment/kani-k1-permtags-20261105`): перестановка через различные теги и
  компаратор с произвольным ответом доказана для network u8 до N17 (335 с) прямым раскрытием тел. N32 даёт TIMEOUT
  даже с kissat.
- Контракт `swap_if_less` сейчас без `ensures`, поэтому `stub_verified` теряет значения в позициях `a`, `b`.

## Что сделать

1. **`ensures` перестановки пары на `swap_if_less`**, верный при **любом** `F`, без модели компаратора: после
   возврата мультимножество {значения в `a_pos`, `b_pos`} равно прежнему. При `a_pos == b_pos` значение не
   меняется. Сравнение по полным значениям через байтовое или `PartialEq`-независимое представление. Если общий
   `T` не позволяет, сформулировать через `old(ptr::read)` и побайтовое равенство под `cfg(kani)`. Тела не менять.
2. **PFC** этого `ensures` на u8 для backing 4, 9, 13, 18 и 32, позиции `kani::any()`, компаратор с произвольным
   ответом. Это отдельные корни; существующие safety-PFC сохранить.
3. **Consumer:** перестановка через теги (как в `permtags.rs`: различные теги, компаратор с произвольным
   ответом, маска) на Unstable network u8 с `#[kani::stub_verified(swap_if_less)]` на длинах N17 (сравнение с
   335 с без подмены), N18, N24, N32. Домен consumer (u8, backing N, тот же компаратор) должен совпадать с
   доказанным PFC.
4. **Негативный контроль:** consumer, который портит один элемент после сортировки, должен упасть на маске.

## Сборки

- **G1:** kind diagnostic, `controls: true`, jobs 1, лимит 10 мин. Строки: PFC backing 13 и 32, consumers N17 и
  N32, контроль. Не больше 6 строк.
- **G2** (с GO): остальные длины и backing по итогам G1.

## Коммиты, ожидание, RESULT

- Library- и research-коммиты отдельно, `[skip ci]`, push без force. Последней строкой
  `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.
- **RESULT-PERMENSURES.md**, ≤ 35 строк:
  - точный текст `ensures`;
  - таблица строк;
  - совпадение доменов;
  - сравнение времени с PERMTAGS;
  - вывод: можно ли довести перестановку network до N32 композицией.

## Запреты

- Только bounded evidence; raw logs и credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код и документация Kani; чужие PR не открывать.
- Тела runtime, workflows и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **PERMENSURES ЗАВЕРШЁН**, затем стоп.
