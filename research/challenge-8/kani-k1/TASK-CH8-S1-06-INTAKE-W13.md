# TASK — worker13: intake S1-06 run 43889560779 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Run 43889560779 (control `b25dd39a46` → sibling `a14a513eb7`, std `5be85699b8`, tool 0aac; твой фикс декодера после S1-05).
Итог jobs — как в S1-05: success — light-model, light-corruption, activation-default, cell; failure — light-controls,
activation-override и все 8 heavy. В heavy (пример freeze_copy_u8-n01) runner завершился
`ValueError: rich metadata incomplete: file/line missing` — completeness fail-closed сработал.

1. Скачать artifacts всех 14 групп в свой каталог, собрать per-row evidence: verdict, rich inventory, exits/elapsed/RSS.
2. Для heavy: какие именно properties без file/line (class/description/ID, сколько), обязательны ли они для приёмки по
   ACCEPTANCE-POLICY-BATCH (post/frame/relation/covers) или это служебные stock-проверки. Сохранились ли verdicts и
   остальной inventory несмотря на отказ.
3. Передать в офлайн-приёмку (классификатор w11): что принимается уже сейчас; что блокируется только отсутствием
   location у не-обязательных проверок (вопрос политики — сформулировать вариант для координатора, не решать самому).
4. g0 `kani3300/ch8-s1/s1-06/run-43889560779/`: RESULT.md, collected.json, HANDOFF.md (+ fix/ при дефекте пакета). Коммит
   [skip ci], author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <g0> [<fix control SHA>] или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать.
