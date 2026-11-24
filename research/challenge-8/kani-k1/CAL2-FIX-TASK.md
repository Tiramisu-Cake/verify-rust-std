# CAL2 · исправления по Round 1 (independent)

Источник: CAL2-REVIEW.md, раздел Round 1 (g0 ca549f76ef), вердикт CHANGES_REQUIRED. Исправить ровно три пункта, ничего больше в пакете не менять (roster, окна, капы, overlay std, workflow остаются как в 7393c84144 / 043a1f19f9).

1. Отказ запуска PSS-потока не должен останавливать Linux measure. Инициализация PSS — внутри обработки ошибок диагностики; при отказе PSS = null с причиной во всех receipts, RSS-телеметрия, guard и слоты продолжаются. Регрессия: инъекция отказа старта потока на уровне measure, все шесть слотов вызываются.
2. Layout guard сравнивает manifest побайтно (без strip). Регрессии: лишняя пустая строка в конце library/core/Cargo.toml и удалённый последний LF — обе отклоняются; зафиксированный overlay 043a1f19f9 по-прежнему принимается.
3. При TIMEOUT или RSS_LIMIT receipt сохраняет наблюдаемый unwind из однозначно связанной строки запуска CBMC (с указанием источника), если stock export отсутствует или неполон; без наблюдения — неизвестно. Регрессии на оба вида отсечки.

После правок: пересобрать request/bundle только если меняются их входы; новый control commit (parent 7393c84144), новый trigger tree с sole parent 467af9cb8d, хэши. Полный suite, нативные rss-stop, pid-race, churn, git diff --check. Локально без cargo, rustc, Kani, CBMC; CI и push не запускать.
Итог: раздел FIX1 в начале CAL2-HANDOFF.md (commits, trees, хэши, тесты, краткий diff), статус READY_FOR_REVIEW, коммит в g0 [skip ci]. Следующее ревью будет только по diff этих трёх пунктов.
