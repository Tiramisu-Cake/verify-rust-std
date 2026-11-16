# TASK — worker13: S1-04 workflow не прошёл валидацию GitHub (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Факт: владелец дал GO на S1-04. Координатор опубликовал std 5be85699b8 (ветка experiment/ch8-s1-04-pprime-20261116)
и control 5fd5387308 на uninit-ci/ch8-s1k-d. Run 43827636574: conclusion failure, 0 jobs, run name = путь файла —
GitHub отверг сам workflow (схема), ни одна задача не стартовала.

Вероятная причина: .github/workflows/ch8-s1.yml в 5fd5387308 пересериализован с типами-строками —
cancel-in-progress: 'false', timeout-minutes: '1' и т.п., persist-credentials: 'false', submodules: 'true'.
В рабочем 40b5d9cf4 этого нет. Проверь и другие поля.

1. Исправить workflow: нативные boolean/number, без изменения семантики (jobs/needs/matrix/caps те же).
   Обновить payload hashes/CI-REQUEST/check_package assertions, если они зависят от файла.
2. Добавить в preflight проверку типов по схеме GitHub Actions для всех полей, где ожидаются boolean/number
   (или actionlint, если он уже есть на сервере; не скачивать).
3. Новый control commit: тот же parent 40b5d9cf4 (single-parent), сообщение без [skip ci]; тот же std 5be85699b8.
   Короткий review (diff только в workflow/preflight/hashes). g0 kani3300/ch8-s1/s1-04/yaml-fix/: HANDOFF.
   Коммиты g0 [skip ci], author Tiramisu-Cake <igkharin@gmail.com>. Последней строкой READY <control> <g0> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
