# REV2 N26–N31 half providers · FIX1 после ревью R1

Задание для **w15**, та же стадия. Ревью R1 — GO с неблокирующими замечаниями; пакет в очереди CI последним, поэтому закрываем их до запуска. [Ревью](REV2-N26-N31-HALVES-REVIEW.md) · [Handoff](REV2-N26-N31-HALVES-HANDOFF.md)

1. **Валидатор (замечание 2).** В `ch8-cal1/results.py:109` верни строгую проверку `copy_back`: привяжи её к виду слота или ожидаемому исходу, чтобы произвольный bool не проходил. Верни отрицательный тест со сдвигом якоря `ptr/mod.rs:587:14` → `588:14` для строки проверки; убедись мутацией, что тест различает.
2. **Handoff (замечания 1, 3, 4).** Пометь выводы об инициализации правых вставок как внешние при uninit OFF; укажи, что нативно показан только сдвиг на первой вставке (rel13), а rel14/rel15 — офлайн; сформулируй шаг как «external base translation + loop induction». Обнови статус run `45829863637` (success, 8/8 MATCHED). Исправь диапазон источников копий на `[begin, tail−1]`.

Std не меняется. Пересоздай Control-коммит поверх `fd941d9493` и detached review-trigger с тем же tree и sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`; обнови хэши request/bundle, если изменятся. Повтори suite на четырёх шкалах, YAML, `bash -n`, `git diff --check`. Добавь в handoff раздел FIX1 с новыми пинами, дельтой и результатами. Статус `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. CI, push, Actions variables, cargo/rustc/Kani/CBMC — не запускать. Все коммиты через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, с `[skip ci]`, без знака решётки перед цифрой.
