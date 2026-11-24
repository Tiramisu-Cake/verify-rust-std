# CAL2 Darwin · FIX6: тесты Linux на runner macOS

Run 45326209217 (macos-26-arm64, python 3.15): самопроверка control упала до discovery, 103/104. Тест test_supervisor.SupervisorTests.test_linux_live_pressure_requires_consecutive_samples_over_two_seconds (test_supervisor.py около строки 570) подделывает монотонные часы и сдвигает их с 0,25 до 2,25 с; на Darwin это попадает в новое правило 2,0 с без валидного RSS и даёт SAMPLER_ERROR (Darwin census deadline exhausted). Боевая политика верна, дефект в тесте: Linux PSI-тест исполняется на Darwin. Поверх control 3b8ef79474.

1. Этот тест выполнять только на Linux (skip на других платформах с причиной) либо явно фиксировать в нём Linux-путь sampler, не меняя боевой код.
2. Просмотреть весь suite: найти все тесты, которые подделывают часы или память и при этом на Darwin пойдут по реальному Darwin census (и потому зависят от правила 2,0 с или от ps). Каждый такой тест либо привязать к платформе, либо сделать независимым от Darwin census. Перечислить их в handoff с решением по каждому.
3. Боевой код (supervisor.py, run.py, telemetry.py, workflow, request, bundle) не менять. Изменения только в test_*.py.

Проверка: полный suite на Linux; дополнительно прогнать suite с подменой платформы на Darwin там, где это возможно синтетически, и перечислить, какие тесты на Darwin будут пропущены. Новый control (parent 3b8ef79474), trigger с тем же tree и sole parent 467af9cb8d. Раздел FIX6 в начале CAL2-MAC-FIX-HANDOFF.md, READY_FOR_REVIEW, коммит g0 [skip ci]. Ревью — только diff тестов: блокируют только изменение боевого кода, ослабление проверки на Linux или оставшийся тест, который на Darwin зависит от скорости ps или от правила 2,0 с. Локально без cargo, rustc, Kani, CBMC; CI и push не запускать.
