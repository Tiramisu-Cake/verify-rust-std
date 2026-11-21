# План покрытия network N20–N32

Цель — exact plain proof реального `small_sort_network` для каждой длины N20–N32 на `u8/KeyLess<u8>`, V34/base1, с произвольными байтами и независимым q. Провайдеры — Check реальных sort9, sort13, insert и целого merge. В consumer исполняются выбор половин, insertion loop и copy-back через disjoint scratch32. Runtime std сохраняется. Кампания 16 проверяет сквозные N20/N25 и отдельно actual merge N32. [Задание 16](PILOT16-IMPL-TASK.md) · [Схема N18/N19](MERGE-PLAN.md)

## Матрица вызовов

Активный срез — `v[1..1+N]`, base слева 1, справа `1+floor(N/2)`. Tails отсчитываются от base своей половины. Область каждой вставки включает оба конца. Presort изменяет первые 9 или 13 байтов половины. [Исходник network](/root/verify-rust-std-ch8-q-pilot-v1/library/core/src/slice/sort/shared/smallsort.rs:332)

| N | Длины L/R | Base R | Presort L/R | Tails L | Tails R |
| ---: | --- | ---: | --- | --- | --- |
| 20 | 10/10 | 11 | 9/9 | 9 | 9 |
| 21 | 10/11 | 11 | 9/9 | 9 | 9–10 |
| 22 | 11/11 | 12 | 9/9 | 9–10 | 9–10 |
| 23 | 11/12 | 12 | 9/9 | 9–10 | 9–11 |
| 24 | 12/12 | 13 | 9/9 | 9–11 | 9–11 |
| 25 | 12/13 | 13 | 9/13 | 9–11 | ∅ |
| 26 | 13/13 | 14 | 13/13 | ∅ | ∅ |
| 27 | 13/14 | 14 | 13/13 | ∅ | 13 |
| 28 | 14/14 | 15 | 13/13 | 13 | 13 |
| 29 | 14/15 | 15 | 13/13 | 13 | 13–14 |
| 30 | 15/15 | 16 | 13/13 | 13–14 | 13–14 |
| 31 | 15/16 | 16 | 13/13 | 13–14 | 13–15 |
| 32 | 16/16 | 17 | 13/13 | 13–15 | 13–15 |

Merge выполняет m = floor(N/2) пар up/down. Пишутся scratch `[0..m]` и `[N-m..N]`. Для нечётного N actual odd copy записывает слот m. При равных байтах up берёт левый, down — правый. Cursor equalities, normal return и полная запись активного диапазона относятся к actual Check. В consumer числовой порядок входит через presort и условный numeric post каждой вставки. Native Pre merge проверяется на том же состоянии.

## Порядок расширения

1. **Кампания 16.** N20 проверяет вставку на каждой стороне и первый новый even merge. N25 проверяет границу двух сетей, три левые вставки и actual odd copy в своём merge-провайдере. Длинный Check sort13 на правой геометрии N25 даёт полезный provider при SUCCESS. Check merge N32 измеряет максимальный actual цикл и край маски. N32 consumer требует следующих провайдеров.
2. **N21–N24.** Добавить sort9 Check для `(base,len)=(1,11),(11,11),(12,11),(12,12),(13,12)`, а также Check insert на base11/tails9–10, base12 и base13/tails9–11. Base1/tails9–11 покрывает успешный провайдер 16. Для каждой длины нужен exact Check merge и exact consumer. Приоритет N21 как первому меньшему odd и N24 как верхней границе двух sort9.
3. **N26–N32.** Нужны sort13 Check на left `(1,13..=16)` и right `(14,13),(14,14),(15,14),(15,15),(16,15),(16,16),(17,16)`. Insert сгруппировать по base и перечисленным tails. Сначала N26 как чистый случай двух sort13, затем odd с правой вставкой и N32 с максимальными tails. Check merge каждой длины и каждый consumer учитываются отдельно. Перенос между геометриями требует доказательства применимости к соответствующим allocation/offset/len. Успех base13/len13 относится к правому вызову N25.
4. **Бюджет.** При ожидаемых исходах 16 остаётся около 45 exact и grouped roots, из них 11 Check sort13, 10 merge Check и 11 consumers. По 1 800 с для sort13 и 600 с для остальных дают около 40 тыс. с child-бюджета. Ориентир — 5–7 последовательных пакетов после 16. Уточнить по замерам. При запасе можно измерить один provider на конечном наборе явно перечисленных пар с coverage каждой пары.

## Согласование object bits

Для расширения предложен единый **11-bit OFF** на всех рёбрах Check → Replace и в контролях. В 15 sort9 и потребители N18/N19 прошли на 11, а provider правой вставки base10/tail9 и оба whole merge Check прошли на 12. Для matched N18/N19 нужны эти три Check на 11 битах, сверка sort9 и обоих consumers на согласованном кандидате, и native numeric-Pre/q-post controls на 11. Если весь no-merge граф переводится на 11, согласовать и повторить его P‑1/P‑3, consumers и controls. У actual-swap Check sort9/sort13 отдельного ребра Replace swap нет. При выборе Replace swap нужен отдельный matched Check байтовой сводки.

На каждом ребре сверять std/tool pins, active clauses и cfg, solver/argv, object bits, checks, unwind, точные type/allocation/offset/len и native inventory. При 11 битах отдельно проверить object-ID capacity и pointer/allocation obligations. Разные widths сохраняют самостоятельные исследовательские результаты до matched повторов либо принятого обоснования переноса. Для CI подтвердить у владельца и организаторов tool pin, bits, режим checks, память, таймаут и concurrency. Сверять самый тяжёлый корень всей цепочки с целевым профилем. Прежние 6 GiB — внутренний ориентир. [Сводка 15](run-44884852864/SUMMARY.md) · [Qualification](QUALIFICATION-CHECKLIST.md) · [Ресурсный профиль](PILOT-SUMMARY-AND-NEXT.md)
