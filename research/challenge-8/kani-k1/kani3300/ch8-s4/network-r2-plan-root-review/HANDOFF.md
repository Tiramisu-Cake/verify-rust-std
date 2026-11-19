# План network-r2 проверен root

План `cdedf547df37aec4c442727a902a784f4d1b5155` ([HANDOFF](../network-r2-offline-plan/HANDOFF.md)) проверен: 10 файлов/9 manifest hashes, 16 зависимостей, 9 исходных файлов/26 диапазонов, три Git identity и восемь argv pointers. Он привязан к фактическому intake `00efb1f5440627362af5c470ad434b89c5e27cca` и заданию `fba20047718b69ad279feffdf7bf44d37d0abcae`.

Root согласен с рекомендуемым дизайном как основой отдельной офлайн-реализации:

- Восемь roots с прежними четырьмя негативными контролями первыми. Для N2/N3/N4 — постоянные длины и literal slices в вызове исходного small_sort_network. Для N01 — независимый bool и две взаимоисключающие ветви с literal длинами 0 и 1; один фактический helper call на каждом source-пути.
- Сохраняются все34 независимых полных u8, V34/base1, исходные snapshot/post и full sorted/count, весь frame/canary, четыре positive assertion roles и covers6/6/6/3. Это source-level соответствие доменов; native binding/полнота ещё не установлены.
- Unwind36 и все safety/unwinding checks остаются. Frame loop имеет34 source-итерации при любом N; оснований для глобального N+1 нет без отдельного lowering/эквивалентности. Число source-итераций не равно автоматически CBMC bound.
- Другой network/insertion helper меняет цель. Для зачёта исходного entry theorem нужен действительный caller/equivalence bridge; bounded source-reported leaves не становятся универсальными verified summaries.

Fit600, эффект на символьный обход и причина исходного N01 insertion-progress остаются UNKNOWN. У нас четыре цензурированных wall600 результата, а не измеренная N-независимая стоимость. Новая native-проверка не проводилась. Рекомендация изолирует представление длины и сохраняет цель/оракулы; измеренного ускорения она не обещает.

Оперативные границы будущего задания: использовать существующие офлайн source/control preflights и final Validate текущего GitHub-пакета; общее упоминание Cloud preflight/phase не разрешает Cloud Build/новую lane. Строгий producer остаётся U-REJECT_ALL/proposal DISABLED; каждый guard/status/U сохраняется. Отдельная существующая S1 SOURCE_REPORTED оценка требует per-site/source аргументов и решения root/координатора; это не новая waiver-политика и не автоматический admission.

**Реализация не назначена, executable package не подготовлен, GO на запуск не дан.** Для продолжения нужны отдельная ограниченная реализация с полными source/control/parent/request/workflow/profile pins, независимое exact-package review и отдельные root/координатор GO/dispatch/ledger. Эта проверка не меняет исходники, caps, flags, runtime/policy, старые admission/history или accounting. FullN16/N32, init/provider/caller/general/MIR/B1B2 остаются OPEN.

Точный root receipt — ROOT-REVIEW.json. MANIFEST.json запечатывает эти два файла; содержащий g0 commit указан внешне, без циклической self-pin.
