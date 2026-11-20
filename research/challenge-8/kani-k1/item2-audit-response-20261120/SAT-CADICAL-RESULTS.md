# Повтор SAT-модели аудитора на CaDiCaL (координатор, 2026-11-21)

Разрешение владельца на локальные SAT-эксперименты — 2026-11-21. Решатель: `cadical` 1.7.3 из Ubuntu noble (apt), тот же семейный решатель, что в CBMC. Скрипты — `experiment/` без изменений (копия в scratch). Лимиты: `ulimit -v` 1,5 ГБ, `nice -n 19`, по одному, таймаут 300 с (gen4 — 120 с). Машина: 2 ядра, ~1,5 ГБ свободно. Самопроверки аудитора (`gen.py selftest`, `gen3.py selftest`, `check_lemmas.py`) — чисто.

Это модель на уровне значений, не Kani и не proof credit. UNSATISFIABLE = свойство верно на всех входах модели.

| Генератор | Модель | Оракул / вариант | Результат | Время |
| --- | --- | --- | --- | ---: |
| gen.py | ins5 | harness | UNSATISFIABLE | 3.05s |
| gen.py | ins5 | harness_q | UNSATISFIABLE | 0.80s |
| gen.py | ins6 | harness | UNSATISFIABLE | 16.58s |
| gen.py | ins6 | harness_q | UNSATISFIABLE | 4.50s |
| gen.py | ins7 | harness | UNSATISFIABLE | 112.10s |
| gen.py | ins7 | harness_q | UNSATISFIABLE | 26.42s |
| gen.py | net9 | harness | TIMEOUT | 300.02s |
| gen.py | net9 | harness_q | TIMEOUT | 300.03s |
| gen.py | net9 | qform_lemma | UNSATISFIABLE | 0.06s |
| gen.py | net13 | harness | TIMEOUT | 300.02s |
| gen.py | net13 | harness_q | TIMEOUT | 300.01s |
| gen.py | net13 | qform_lemma | UNSATISFIABLE | 0.45s |
| gen.py | net13 | sorted | UNSATISFIABLE | 136.77s |
| gen2.py | net17_qform_lemma | 17 | UNSATISFIABLE | 0.69s |
| gen2.py | ins_leaf_qform | 16 | UNSATISFIABLE | 0.34s |
| gen2.py | ins_leaf_std | 16 | TIMEOUT | 300.02s |
| gen2.py | network_ind_ostat | 32 | UNSATISFIABLE | 1.63s |
| gen2.py | general_ind_ostat | 32 | UNSATISFIABLE | 2.31s |
| gen4.py | ins_stub_count | 4 | UNSATISFIABLE | 2.65s |
| gen4.py | ins_stub_count | 5 | UNSATISFIABLE | 21.00s |
| gen4.py | ins_stub_thr | 8 | UNSATISFIABLE | 0.02s |
| gen4.py | ins_stub_thr | 16 | UNSATISFIABLE | 0.16s |
| gen5.py | merge_plain | 16 | UNSATISFIABLE | 2.46s |
| gen5.py | merge_step | 16 | UNSATISFIABLE | 0.37s |
| gen5.py | merge_inv | 16 | UNSATISFIABLE | 0.10s |
| gen5.py | merge_plain | 32 | UNSATISFIABLE | 28.52s |
| gen5.py | merge_step | 32 | UNSATISFIABLE | 1.71s |
| gen5.py | merge_inv | 32 | UNSATISFIABLE | 0.99s |

## Выводы

1. **Главный тезис аудита подтверждается на CaDiCaL.** Нынешний счётный оракул (`harness`) и один `q` (`harness_q`) не решают сеть N9 и N13 за 300 с; пороговая форма с леммами вызываемых функций — N9 0,06 с, N13 0,45 с, N17 0,69 с, маршруты N32 из сводок 1,6–2,3 с.
2. **Расхождение с аудитом по одному `q`.** На вставке N5–N7 один свободный `q` в 3–4 раза быстрее нынешнего оракула (0,8/4,5/26 с против 3,1/16,6/112 с), а не в 2–10 раз хуже, как на CDCL аудитора. На сетях N9/N13 оба не проходят. Вывод: `count_q` дешевле, но стену не снимает; пороговая композиция — да.
3. **Листья:** `insert_tail` 16 в пороговой форме 0,34 с против таймаута у счётной формы.
4. **Счётные сводки (S2) действительно хуже тела:** потребитель на счётных сводках вставки N5 — 21 с, на пороговых N16 — 0,16 с.
5. **Merge:** 32 без подсказок 28,5 с, с фактами шага 1,7 с, с инвариантом 1,0 с — на CaDiCaL монолитная пороговая форма merge 32 решается (у аудитора не решалась).
6. Только отсортированность N13 — 137 с: порядок на sort13 монолитно дорог и в модели.
